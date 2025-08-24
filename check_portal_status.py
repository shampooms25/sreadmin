#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.models import EldPortalSemVideo

print("=== Verificação de Portais sem Vídeo ===")
portais = EldPortalSemVideo.objects.all()
print(f"Total de portais sem vídeo: {portais.count()}")

ativos = EldPortalSemVideo.objects.filter(ativo=True)
print(f"Portais sem vídeo ativos: {ativos.count()}")

for p in ativos:
    print(f"  ID: {p.id}")
    print(f"  Nome: {p.nome}")
    print(f"  Arquivo ZIP: {p.arquivo_zip}")
    if p.arquivo_zip:
        print(f"  Caminho: {p.arquivo_zip.path}")
        print(f"  Existe: {os.path.exists(p.arquivo_zip.path) if p.arquivo_zip.path else 'N/A'}")
    print("  ---")

# Verificar também portais com vídeo
from painel.models import EldGerenciarPortal
portais_video = EldGerenciarPortal.objects.filter(ativo=True)
print(f"\nPortais com vídeo ativos: {portais_video.count()}")
for p in portais_video:
    print(f"  ID: {p.id}")
    print(f"  Nome: {getattr(p, 'nome', 'N/A')}")
    print(f"  Arquivo ZIP: {p.captive_portal_zip}")
    print("  ---")
