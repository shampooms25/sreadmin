from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand

from starlink_allowlist.models import CustomPrefix, StarlinkASN, StarlinkPrefix


class Command(BaseCommand):
    help = (
        'Exporta prefixes (StarlinkPrefix) em JSON compatível com o modo offline do update_starlink_prefixes (--from-file).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            default='',
            help='Caminho do arquivo de saída. Se omitido, imprime no stdout.',
        )
        parser.add_argument(
            '--ip-version',
            choices=['4', '6'],
            default='',
            help='Filtra IPv4 ou IPv6 (padrão: ambos).',
        )
        parser.add_argument(
            '--include-non-americas',
            action='store_true',
            help='Inclui prefixes fora das Américas (por padrão exporta apenas is_americas=True).',
        )
        parser.add_argument(
            '--include-inactive',
            action='store_true',
            help='Inclui prefixes inativos (active=False).',
        )
        parser.add_argument(
            '--include-custom',
            action='store_true',
            help='Inclui CustomPrefix (enabled=True) em um campo "custom" no JSON.',
        )
        parser.add_argument(
            '--asn',
            action='append',
            help='Limitar a ASNs específicos (ex: --asn 14593 --asn 45700).',
        )

    def handle(self, *args, **options):
        output_path: str = (options.get('output') or '').strip()
        ip_version_raw: str = (options.get('ip_version') or '').strip()
        include_non_americas: bool = bool(options.get('include_non_americas'))
        include_inactive: bool = bool(options.get('include_inactive'))
        include_custom: bool = bool(options.get('include_custom'))
        asn_filter = options.get('asn') or []

        asns_qs = StarlinkASN.objects.all().order_by('number')
        if asn_filter:
            numbers = [int(x) for x in asn_filter]
            asns_qs = asns_qs.filter(number__in=numbers)

        prefixes_qs = StarlinkPrefix.objects.select_related('asn')
        if not include_inactive:
            prefixes_qs = prefixes_qs.filter(active=True)
        if ip_version_raw in {'4', '6'}:
            prefixes_qs = prefixes_qs.filter(ip_version=int(ip_version_raw))
        if not include_non_americas:
            prefixes_qs = prefixes_qs.filter(is_americas=True)
        if asn_filter:
            prefixes_qs = prefixes_qs.filter(asn__number__in=[int(x) for x in asn_filter])

        # build per-asn lists
        by_asn: dict[int, dict] = {}
        for asn in asns_qs:
            by_asn[asn.number] = {
                'number': asn.number,
                'name': asn.name,
                'enabled': asn.enabled,
                'americas_only': asn.americas_only,
                'ipv4': [],
                'ipv6': [],
            }

        for p in prefixes_qs.order_by('asn__number', 'ip_version', 'cidr'):
            entry = by_asn.get(p.asn.number)
            if not entry:
                # ASN not selected (e.g. if prefixes exist for ASN but asn_filter excluded it)
                continue
            if p.ip_version == 4:
                entry['ipv4'].append(p.cidr)
            elif p.ip_version == 6:
                entry['ipv6'].append(p.cidr)

        asns_out = [by_asn[k] for k in sorted(by_asn.keys())]

        payload: dict = {
            'schema': 'starlink_allowlist_export_v1',
            'filters': {
                'ip_version': ip_version_raw or None,
                'include_non_americas': include_non_americas,
                'include_inactive': include_inactive,
                'asns': [int(x) for x in asn_filter] if asn_filter else None,
            },
            'asns': asns_out,
        }

        if include_custom:
            cqs = CustomPrefix.objects.filter(enabled=True)
            if ip_version_raw in {'4', '6'}:
                cqs = cqs.filter(ip_version=int(ip_version_raw))
            payload['custom'] = [
                {
                    'cidr': c.cidr,
                    'ip_version': c.ip_version,
                    'name': c.name,
                    'region': c.region,
                    'country': c.country,
                }
                for c in cqs.order_by('ip_version', 'cidr')
            ]

        text = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'

        if output_path:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')
            self.stdout.write(self.style.SUCCESS(f'OK: wrote {path}'))
            return

        self.stdout.write(text)
