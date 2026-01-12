from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from ipaddress import ip_network
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from starlink_allowlist.models import CustomPrefix, StarlinkPrefix


@dataclass(frozen=True)
class ClassifiedPrefix:
    raw: str
    cidr: str
    ip_version: int
    classification: str  # starlink | non_starlink | overlaps_starlink
    reason: str


def _iter_input_lines(text: str) -> list[str]:
    out: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith('#'):
            continue
        # allow inline comments
        s = re.split(r"\s+#", s, maxsplit=1)[0].strip()
        if not s:
            continue
        # first token only (so you can paste "cidr,name" etc if needed)
        token = s.split()[0].strip().strip(',')
        if token:
            out.append(token)
    return out


def _parse_network(raw: str):
    # strict=False allows single IPs (becomes /32 or /128)
    return ip_network(raw, strict=False)


def _load_starlink_networks() -> dict[int, list]:
    nets_v4 = []
    nets_v6 = []
    for cidr in StarlinkPrefix.objects.filter(active=True).values_list('cidr', flat=True):
        try:
            n = ip_network(cidr, strict=True)
        except Exception:
            continue
        if n.version == 4:
            nets_v4.append(n)
        else:
            nets_v6.append(n)
    return {4: nets_v4, 6: nets_v6}


def _classify(net, starlink_nets: list) -> tuple[str, str]:
    # Prefer containment check: user net is inside a starlink net.
    for sn in starlink_nets:
        if net.subnet_of(sn):
            return 'starlink', f'contained_in={sn}'

    # Overlap check (includes supernets and partial overlaps)
    for sn in starlink_nets:
        if net.overlaps(sn):
            if net.supernet_of(sn):
                return 'overlaps_starlink', f'supernet_of={sn}'
            return 'overlaps_starlink', f'overlaps={sn}'

    return 'non_starlink', 'no_overlap'


class Command(BaseCommand):
    help = (
        'Importa uma lista de prefixos/IPs e cria CustomPrefix apenas para os que NÃO forem Starlink. '
        'A detecção é feita comparando com StarlinkPrefix(active=True) por contenção/overlap.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--input',
            default='',
            help='Arquivo de entrada com um CIDR/IP por linha. Se omitido, lê do stdin.',
        )
        parser.add_argument(
            '--ip-version',
            choices=['4', '6', 'both'],
            default='both',
            help='Filtra entradas de entrada por IP version (default: both).',
        )
        parser.add_argument(
            '--name',
            default='',
            help='Nome opcional a ser aplicado aos CustomPrefix criados (mesmo nome para todos).',
        )
        parser.add_argument(
            '--enabled',
            action='store_true',
            help='Cria CustomPrefix como enabled=True (default: True).',
        )
        parser.add_argument(
            '--disabled',
            action='store_true',
            help='Cria CustomPrefix como enabled=False.',
        )
        parser.add_argument(
            '--include-overlaps',
            action='store_true',
            help=(
                'Também cria CustomPrefix para itens que sobrepõem Starlink (supernet/overlap). '
                'Use com cuidado.'
            ),
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Não grava no banco; apenas mostra o resumo.',
        )
        parser.add_argument(
            '--report',
            default='',
            help='Se informado, grava um JSON com o resultado da classificação.',
        )

    def handle(self, *args, **options):
        input_path = (options.get('input') or '').strip()
        ip_version_filter = (options.get('ip_version') or 'both').strip()
        name = (options.get('name') or '').strip()
        include_overlaps = bool(options.get('include_overlaps'))
        dry_run = bool(options.get('dry_run'))
        report_path = (options.get('report') or '').strip()

        if bool(options.get('enabled')) and bool(options.get('disabled')):
            raise SystemExit('Use apenas --enabled OU --disabled (não ambos).')
        enabled = True
        if bool(options.get('disabled')):
            enabled = False

        if input_path:
            text = Path(input_path).read_text(encoding='utf-8')
        else:
            if sys.stdin is None or sys.stdin.closed or sys.stdin.isatty():
                raise SystemExit('Nenhum --input informado e nenhum stdin detectado. Use --input ou pipe (ex: cat arquivo | ...).')
            text = sys.stdin.read()

        raw_items = _iter_input_lines(text)
        if not raw_items:
            self.stdout.write(self.style.WARNING('Nenhuma entrada encontrada.'))
            return

        starlink_by_ver = _load_starlink_networks()

        classified: list[ClassifiedPrefix] = []
        seen_cidr: set[str] = set()

        for raw in raw_items:
            try:
                net = _parse_network(raw)
            except Exception as e:
                classified.append(
                    ClassifiedPrefix(
                        raw=raw,
                        cidr='',
                        ip_version=0,
                        classification='invalid',
                        reason=str(e),
                    )
                )
                continue

            if ip_version_filter in {'4', '6'} and str(net.version) != ip_version_filter:
                continue

            cidr = str(net)
            if cidr in seen_cidr:
                continue
            seen_cidr.add(cidr)

            cls, reason = _classify(net, starlink_by_ver[net.version])
            classified.append(
                ClassifiedPrefix(
                    raw=raw,
                    cidr=cidr,
                    ip_version=net.version,
                    classification=cls,
                    reason=reason,
                )
            )

        to_create = [c for c in classified if c.classification == 'non_starlink']
        overlaps = [c for c in classified if c.classification == 'overlaps_starlink']
        already_custom = set(CustomPrefix.objects.values_list('cidr', flat=True))

        create_candidates = [c for c in to_create if c.cidr and c.cidr not in already_custom]
        if include_overlaps:
            create_candidates.extend([c for c in overlaps if c.cidr and c.cidr not in already_custom])

        skipped_existing = [c for c in to_create if c.cidr in already_custom]

        summary = {
            'input_total': len(raw_items),
            'classified_total': len(classified),
            'starlink': sum(1 for c in classified if c.classification == 'starlink'),
            'non_starlink': len(to_create),
            'overlaps_starlink': len(overlaps),
            'invalid': sum(1 for c in classified if c.classification == 'invalid'),
            'create_new': len(create_candidates),
            'skipped_existing_custom': len(skipped_existing),
            'dry_run': dry_run,
            'ip_version_filter': ip_version_filter,
            'include_overlaps': include_overlaps,
        }

        if report_path:
            Path(report_path).parent.mkdir(parents=True, exist_ok=True)
            Path(report_path).write_text(
                json.dumps(
                    {
                        'summary': summary,
                        'items': [c.__dict__ for c in classified],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + '\n',
                encoding='utf-8',
            )
            self.stdout.write(self.style.SUCCESS(f'OK: wrote report {report_path}'))

        self.stdout.write(json.dumps(summary, ensure_ascii=False))

        if dry_run:
            return

        if not create_candidates:
            self.stdout.write(self.style.WARNING('Nada para criar.'))
            return

        with transaction.atomic():
            for c in create_candidates:
                CustomPrefix.objects.create(
                    cidr=c.cidr,
                    ip_version=c.ip_version,
                    name=name,
                    enabled=enabled,
                )

        self.stdout.write(self.style.SUCCESS(f'OK: created {len(create_candidates)} CustomPrefix'))
