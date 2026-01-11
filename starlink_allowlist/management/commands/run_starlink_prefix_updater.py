from __future__ import annotations

import time
from typing import Any

from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = (
        'Executa update_starlink_prefixes em loop (útil para ambiente local/testes). '
        'Em produção, prefira cron/systemd timer/Celery beat.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval-seconds',
            type=int,
            default=6 * 60 * 60,
            help='Intervalo entre execuções (padrão: 6h).',
        )
        parser.add_argument(
            '--once',
            action='store_true',
            help='Executa apenas uma vez e sai.',
        )

        # Repasse de opções do update_starlink_prefixes
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--no-rdap', action='store_true')
        parser.add_argument('--backfill-missing', action='store_true')
        parser.add_argument('--rdap-timeout', type=float, default=8.0)
        parser.add_argument('--asn', action='append')
        parser.add_argument('--from-file', default='')

    def handle(self, *args: Any, **options: Any):
        interval_seconds: int = int(options['interval_seconds'])
        once: bool = bool(options.get('once'))

        while True:
            start = time.time()
            try:
                call_command(
                    'update_starlink_prefixes',
                    dry_run=bool(options.get('dry_run')),
                    no_rdap=bool(options.get('no_rdap')),
                    backfill_missing=bool(options.get('backfill_missing')),
                    rdap_timeout=float(options.get('rdap_timeout')),
                    asn=options.get('asn') or None,
                    from_file=(options.get('from_file') or '').strip() or None,
                )
            except Exception as exc:
                # Não derruba o loop; registra no console
                self.stderr.write(self.style.ERROR(f'update_starlink_prefixes falhou: {exc}'))

            if once:
                return

            elapsed = time.time() - start
            sleep_for = max(1, interval_seconds - int(elapsed))
            self.stdout.write(self.style.NOTICE(f'Aguardando {sleep_for}s para próxima execução...'))
            time.sleep(sleep_for)
