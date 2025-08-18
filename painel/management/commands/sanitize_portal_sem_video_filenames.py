from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
import os
import re

from painel.models import EldPortalSemVideo

class Command(BaseCommand):
    help = "Sanitiza nomes de arquivos ZIP de Portais sem Vídeo (remove espaços e caracteres problemáticos)."

    def handle(self, *args, **options):
        changed = 0
        errors = 0
        with transaction.atomic():
            for portal in EldPortalSemVideo.objects.all():
                f = portal.arquivo_zip
                if not f:
                    continue
                current = getattr(f, 'name', '') or ''
                if not current:
                    continue

                dir_name = os.path.dirname(current) or 'portal_sem_video'
                base = os.path.basename(current)
                name, ext = os.path.splitext(base)
                cleaned_name = re.sub(r'\s+', '_', name.strip())
                cleaned_name = re.sub(r'[^A-Za-z0-9_\-\.]+', '', cleaned_name) or 'portal_sem_video'
                cleaned_ext = ext if ext else '.zip'
                safe_base = f"{cleaned_name}{cleaned_ext}"
                safe_name = os.path.join(dir_name, safe_base)

                if safe_name != current:
                    # Renomear no storage fisicamente e atualizar no model
                    try:
                        storage = f.storage
                        if storage.exists(current):
                            # destino não deve colidir
                            if storage.exists(safe_name):
                                base_no_ext = os.path.splitext(safe_base)[0]
                                safe_base = f"{base_no_ext}_{portal.pk}{cleaned_ext}"
                                safe_name = os.path.join(dir_name, safe_base)
                            storage.save(safe_name, storage.open(current, 'rb'))
                            storage.delete(current)
                        portal.arquivo_zip.name = safe_name
                        portal.save(update_fields=['arquivo_zip'])
                        changed += 1
                        self.stdout.write(self.style.SUCCESS(f"Atualizado: {current} -> {safe_name}"))
                    except Exception as e:
                        errors += 1
                        self.stderr.write(self.style.ERROR(f"Erro ao renomear {current}: {e}"))
        self.stdout.write(self.style.NOTICE(f"Concluído. Alterados: {changed}, Erros: {errors}"))
