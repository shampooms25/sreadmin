from __future__ import annotations

import ipaddress
from datetime import timedelta

import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from starlink_allowlist.models import StarlinkASN, StarlinkPrefix, StarlinkUpdateRun
from starlink_allowlist.services import classify_is_americas, rdap_lookup_any


class Command(BaseCommand):
    help = 'Atualiza prefixes Starlink a partir de ASNs habilitados (BGPView) e classifica Américas via RDAP.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Não grava alterações no banco')
        parser.add_argument('--no-rdap', action='store_true', help='Não faz lookup RDAP (não atualiza country/rir/is_americas)')
        parser.add_argument('--rdap-timeout', type=float, default=8.0)
        parser.add_argument('--asn', action='append', help='Limitar a ASNs específicos (ex: --asn 14593 --asn 45700)')

    def handle(self, *args, **options):
        dry_run: bool = options['dry_run']
        no_rdap: bool = options['no_rdap']
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

        run = StarlinkUpdateRun.objects.create(
            started_at=timezone.now(),
            status=StarlinkUpdateRun.STATUS_SUCCESS,
            source='bgpview',
            asns=[a.number for a in asns],
            details={},
        )

        try:
            details = {}
            total_added = 0
            total_removed = 0
            total_active = 0

            for asn in asns:
                self.stdout.write(f'Buscando prefixes do AS{asn.number}...')
                url = f'https://api.bgpview.io/asn/{asn.number}/prefixes'
                resp = requests.get(url, timeout=20)
                resp.raise_for_status()
                data = resp.json().get('data') or {}

                v4 = [p.get('prefix') for p in (data.get('ipv4_prefixes') or []) if p.get('prefix')]
                v6 = [p.get('prefix') for p in (data.get('ipv6_prefixes') or []) if p.get('prefix')]

                fetched = []
                fetched += [(cidr, 4) for cidr in v4]
                fetched += [(cidr, 6) for cidr in v6]

                # Normalizar/validar CIDR
                normalized: list[tuple[str, int, str]] = []
                invalid: list[str] = []
                for cidr, version in fetched:
                    try:
                        net = ipaddress.ip_network(cidr, strict=False)
                        normalized.append((str(net), net.version, str(net.network_address)))
                    except Exception:
                        invalid.append(cidr)

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

                        StarlinkPrefix.objects.create(
                            cidr=cidr,
                            ip_version=version,
                            asn=asn,
                            country=country,
                            rir=rir,
                            is_americas=is_americas,
                            first_seen_at=now,
                            last_seen_at=now,
                            active=True,
                        )

                total_added += len(to_add)
                total_removed += len(to_remove)
                total_active += len(fetched_set)

            if not dry_run:
                run.finished_at = timezone.now()
                run.total_prefixes = total_active
                run.added_prefixes = total_added
                run.removed_prefixes = total_removed
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
