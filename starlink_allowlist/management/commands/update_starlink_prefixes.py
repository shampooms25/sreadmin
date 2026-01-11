from __future__ import annotations

import ipaddress
import json
from pathlib import Path
from datetime import timedelta

import requests
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.db import transaction
from django.utils import timezone

from starlink_allowlist.models import StarlinkASN, StarlinkPrefix, StarlinkUpdateRun
from starlink_allowlist.services import classify_is_americas, classify_region, rdap_lookup_any


class Command(BaseCommand):
    help = 'Atualiza prefixes Starlink a partir de ASNs habilitados (BGPView/RIPEstat) e classifica Américas via RDAP.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Não grava alterações no banco')
        parser.add_argument('--no-rdap', action='store_true', help='Não faz lookup RDAP (não atualiza country/rir/is_americas)')
        parser.add_argument(
            '--backfill-missing',
            action='store_true',
            help='Preenche metadados faltantes (country/rir/region/is_americas) em prefixes existentes (requer RDAP).',
        )
        parser.add_argument(
            '--from-file',
            default='',
            help=(
                'Modo offline: carrega prefixes de um arquivo .txt ou .json e aplica o mesmo algoritmo de add/remove. '
                'TXT: um CIDR por linha (ignora linhas vazias e comentários iniciando com #). '
                'JSON: pode ser {"asns": [{"number":14593, "ipv4": [..], "ipv6": [..]}]} '
                'ou um payload estilo BGPView {"data": {"ipv4_prefixes": [{"prefix": "..."}], ...}} '
                '(nesse caso é necessário informar --asn).'
            ),
        )
        parser.add_argument('--rdap-timeout', type=float, default=8.0)
        parser.add_argument('--asn', action='append', help='Limitar a ASNs específicos (ex: --asn 14593 --asn 45700)')

    def _parse_prefixes_text(self, path: Path) -> list[str]:
        lines = path.read_text(encoding='utf-8').splitlines()
        out: list[str] = []
        for line in lines:
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            out.append(s)
        return out

    def _extract_prefixes_from_bgpview_like(self, data: dict) -> tuple[list[str], list[str]]:
        data = (data or {}).get('data') or {}
        v4 = [p.get('prefix') for p in (data.get('ipv4_prefixes') or []) if p.get('prefix')]
        v6 = [p.get('prefix') for p in (data.get('ipv6_prefixes') or []) if p.get('prefix')]
        return v4, v6

    def _parse_prefixes_json_for_asns(self, path: Path) -> dict[int, list[tuple[str, int]]]:
        raw = json.loads(path.read_text(encoding='utf-8'))

        # Case 1: our explicit schema: {"asns": [{"number":14593, "ipv4":[], "ipv6":[]}, ...]}
        if isinstance(raw, dict) and isinstance(raw.get('asns'), list):
            out: dict[int, list[tuple[str, int]]] = {}
            for item in raw.get('asns') or []:
                if not isinstance(item, dict):
                    continue
                num_raw = item.get('number')
                try:
                    num = int(num_raw)
                except Exception:
                    continue

                v4 = item.get('ipv4') or item.get('ipv4_prefixes') or []
                v6 = item.get('ipv6') or item.get('ipv6_prefixes') or []

                fetched: list[tuple[str, int]] = []
                for cidr in v4:
                    if cidr:
                        fetched.append((str(cidr), 4))
                for cidr in v6:
                    if cidr:
                        fetched.append((str(cidr), 6))
                out[num] = fetched
            return out

        # Case 2: BGPView-like payload: {"data": {"ipv4_prefixes": [{"prefix": "..."}], ...}}
        if isinstance(raw, dict) and 'data' in raw:
            v4, v6 = self._extract_prefixes_from_bgpview_like(raw)
            fetched: list[tuple[str, int]] = []
            fetched += [(cidr, 4) for cidr in v4]
            fetched += [(cidr, 6) for cidr in v6]
            return {-1: fetched}  # placeholder key; must be mapped by caller via --asn

        # Case 3: list of CIDRs
        if isinstance(raw, list):
            fetched: list[tuple[str, int]] = []
            for cidr in raw:
                if not cidr:
                    continue
                fetched.append((str(cidr), 0))
            return {-1: fetched}

        raise ValueError('Formato JSON não reconhecido para import offline.')

    def _normalize_fetched(self, fetched: list[tuple[str, int]]) -> tuple[list[tuple[str, int, str]], list[str]]:
        normalized: list[tuple[str, int, str]] = []
        invalid: list[str] = []
        for cidr, version in fetched:
            try:
                net = ipaddress.ip_network(cidr, strict=False)
                normalized.append((str(net), net.version, str(net.network_address)))
            except Exception:
                invalid.append(str(cidr))
        return normalized, invalid

    def _fetch_from_bgpview(self, asn_number: int) -> list[tuple[str, int]]:
        url = f'https://api.bgpview.io/asn/{asn_number}/prefixes'
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        data = resp.json() or {}
        v4, v6 = self._extract_prefixes_from_bgpview_like(data)
        fetched: list[tuple[str, int]] = []
        fetched += [(cidr, 4) for cidr in v4]
        fetched += [(cidr, 6) for cidr in v6]
        return fetched

    def _fetch_from_ripestat(self, asn_number: int) -> list[tuple[str, int]]:
        # https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS14593
        url = f'https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS{asn_number}'
        resp = requests.get(url, timeout=20, headers={'User-Agent': 'sreadmin-starlink-allowlist/1.0'})
        resp.raise_for_status()
        raw = resp.json() or {}
        data = (raw.get('data') or {}) if isinstance(raw, dict) else {}
        prefixes = data.get('prefixes') or []

        fetched: list[tuple[str, int]] = []
        for item in prefixes:
            if isinstance(item, dict):
                cidr = item.get('prefix')
            else:
                cidr = item
            if not cidr:
                continue
            # versão será normalizada em _normalize_fetched; aqui setamos 0 para "desconhecida"
            fetched.append((str(cidr), 0))
        return fetched

    def _fetch_prefixes_auto(self, asn_number: int) -> list[tuple[str, int]]:
        try:
            return self._fetch_from_bgpview(asn_number)
        except Exception as e:
            self.stdout.write(self.style.WARNING(
                f'BGPView indisponível para AS{asn_number} ({e}). Tentando RIPEstat...'
            ))
            return self._fetch_from_ripestat(asn_number)

    def handle(self, *args, **options):
        dry_run: bool = options['dry_run']
        no_rdap: bool = options['no_rdap']
        backfill_missing: bool = options.get('backfill_missing', False)
        from_file: str = (options.get('from_file') or '').strip()
        rdap_timeout: float = options['rdap_timeout']
        asn_filter = options.get('asn') or []

        qs = StarlinkASN.objects.filter(enabled=True)
        if asn_filter:
            numbers = [int(x) for x in asn_filter]
            qs = qs.filter(number__in=numbers)

        asns = list(qs)
        if not asns:
            self.stdout.write(self.style.WARNING('Nenhum ASN habilitado para atualizar.'))
            return

        offline_map: dict[int, list[tuple[str, int]]] = {}
        if from_file:
            path = Path(from_file)
            if not path.exists():
                raise FileNotFoundError(str(path))

            if path.suffix.lower() == '.json':
                offline_map = self._parse_prefixes_json_for_asns(path)
            else:
                cidrs = self._parse_prefixes_text(path)
                offline_map = {-1: [(c, 0) for c in cidrs]}

            if -1 in offline_map:
                # placeholder import: requires single target ASN
                if len(asns) != 1:
                    raise ValueError('Import offline (lista simples) requer exatamente 1 ASN selecionado via --asn.')
                only = asns[0]
                offline_map[only.number] = offline_map.pop(-1)

            # validate that all keys exist in selected ASN list
            selected_numbers = {a.number for a in asns}
            missing = sorted(set(offline_map.keys()) - selected_numbers)
            if missing:
                raise ValueError(f'Import offline contém ASNs não selecionados/habilitados: {missing}')

        run = StarlinkUpdateRun.objects.create(
            started_at=timezone.now(),
            status=StarlinkUpdateRun.STATUS_SUCCESS,
            source='file' if from_file else 'bgpview',
            asns=[a.number for a in asns],
            details={},
        )

        try:
            details = {}
            total_added = 0
            total_removed = 0
            total_active = 0
            total_backfilled = 0

            for asn in asns:
                if from_file:
                    self.stdout.write(f'Carregando prefixes (offline) do AS{asn.number}...')
                    fetched = offline_map.get(asn.number) or []
                else:
                    self.stdout.write(f'Buscando prefixes do AS{asn.number}...')
                    fetched = self._fetch_prefixes_auto(asn.number)

                normalized, invalid = self._normalize_fetched(fetched)

                fetched_set = {(cidr, version) for cidr, version, _ip in normalized}

                existing = StarlinkPrefix.objects.filter(asn=asn)
                existing_active = set(existing.filter(active=True).values_list('cidr', 'ip_version'))

                to_add = sorted(fetched_set - existing_active)
                to_remove = sorted(existing_active - fetched_set)

                details[str(asn.number)] = {
                    'fetched_total': len(fetched_set),
                    'invalid': invalid,
                    'to_add': len(to_add),
                    'to_remove': len(to_remove),
                }

                if dry_run:
                    total_added += len(to_add)
                    total_removed += len(to_remove)
                    total_active += len(fetched_set)
                    continue

                with transaction.atomic():
                    now = timezone.now()

                    # Marcar removidos como inativos (não deletar)
                    if to_remove:
                        StarlinkPrefix.objects.filter(asn=asn, active=True, cidr__in=[c for c, _v in to_remove]).update(
                            active=False,
                            last_seen_at=now,
                        )

                    # Atualizar last_seen dos que continuam
                    StarlinkPrefix.objects.filter(asn=asn, active=True).update(last_seen_at=now)

                    # Inserir novos
                    for cidr, version in to_add:
                        country = ''
                        rir = ''
                        is_americas = True
                        region = 'unknown'

                        if not no_rdap:
                            try:
                                ip = str(ipaddress.ip_network(cidr, strict=False).network_address)
                            except Exception:
                                ip = ''

                            if ip:
                                info = rdap_lookup_any(ip, timeout_seconds=rdap_timeout)
                                if info:
                                    country = info.country
                                    rir = info.rir
                                    is_americas = classify_is_americas(rir=rir, country=country)
                                    region = classify_region(rir=rir, country=country)

                        StarlinkPrefix.objects.create(
                            cidr=cidr,
                            ip_version=version,
                            asn=asn,
                            country=country,
                            rir=rir,
                            region=region,
                            is_americas=is_americas,
                            first_seen_at=now,
                            last_seen_at=now,
                            active=True,
                        )

                # Backfill opcional fora da transação principal (evita segurar lock por muito tempo)
                if (not dry_run) and (not no_rdap) and backfill_missing:
                    now = timezone.now()
                    missing_qs = StarlinkPrefix.objects.filter(asn=asn, active=True).filter(
                        Q(country='') | Q(rir='') | Q(region='')
                    )

                    backfilled = 0
                    for p in missing_qs.only('id', 'cidr', 'country', 'rir', 'region', 'is_americas'):
                        try:
                            ip = str(ipaddress.ip_network(p.cidr, strict=False).network_address)
                        except Exception:
                            continue

                        info = rdap_lookup_any(ip, timeout_seconds=rdap_timeout)
                        if not info:
                            continue

                        country = info.country
                        rir = info.rir
                        is_americas = classify_is_americas(rir=rir, country=country)
                        region = classify_region(rir=rir, country=country)

                        StarlinkPrefix.objects.filter(pk=p.pk).update(
                            country=country,
                            rir=rir,
                            region=region,
                            is_americas=is_americas,
                            last_seen_at=now,
                        )
                        backfilled += 1

                    if backfilled:
                        details[str(asn.number)]['backfilled'] = backfilled
                        total_backfilled += backfilled

                total_added += len(to_add)
                total_removed += len(to_remove)
                total_active += len(fetched_set)

            if not dry_run:
                run.finished_at = timezone.now()
                run.total_prefixes = total_active
                run.added_prefixes = total_added
                run.removed_prefixes = total_removed
                if total_backfilled:
                    run.details = {**details, '_backfilled_total': total_backfilled}
                else:
                    run.details = details
                run.status = StarlinkUpdateRun.STATUS_SUCCESS
                run.save(update_fields=['finished_at', 'total_prefixes', 'added_prefixes', 'removed_prefixes', 'details', 'status'])

            self.stdout.write(self.style.SUCCESS(
                f'OK. total={total_active} added={total_added} removed={total_removed}' + (' (dry-run)' if dry_run else '')
            ))

        except Exception as e:
            if not dry_run:
                run.finished_at = timezone.now()
                run.status = StarlinkUpdateRun.STATUS_ERROR
                run.error = str(e)
                run.save(update_fields=['finished_at', 'status', 'error'])
            raise
