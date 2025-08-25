#!/usr/bin/env python3
"""
CORREÇÃO FINAL - Remove espaços em branco do nome do arquivo
Execute este script no servidor de produção
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, '/var/www/sreadmin')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.models import EldPortalSemVideo

def main():
    print("=== CORREÇÃO FINAL - REMOVENDO ESPAÇOS ===")
    
    portal = EldPortalSemVideo.objects.filter(ativo=True).first()
    if not portal:
        print("❌ Nenhum portal ativo encontrado!")
        return
    
    print(f"Portal: {portal.nome}")
    
    # Mostrar problema
    old_name = portal.arquivo_zip.name
    old_path = portal.arquivo_zip.path
    
    print(f"Nome antigo (len={len(old_name)}): \"{old_name}\"")
    print(f"Path antigo (len={len(old_path)}): \"{old_path}\"")
    print(f"Arquivo existe (antigo): {os.path.exists(old_path)}")
    
    # Limpar espaços
    clean_name = old_name.strip()
    
    print(f"\nNome limpo (len={len(clean_name)}): \"{clean_name}\"")
    
    # Atualizar banco
    EldPortalSemVideo.objects.filter(ativo=True).update(arquivo_zip=clean_name)
    print("✅ Banco de dados atualizado!")
    
    # Verificar correção
    portal.refresh_from_db()
    new_name = portal.arquivo_zip.name
    new_path = portal.arquivo_zip.path
    
    print(f"\nNome novo (len={len(new_name)}): \"{new_name}\"")
    print(f"Path novo (len={len(new_path)}): \"{new_path}\"")
    print(f"Arquivo existe (novo): {os.path.exists(new_path)}")
    
    if os.path.exists(new_path):
        print(f"✅ SUCESSO! Arquivo acessível: {os.path.getsize(new_path)} bytes")
        return True
    else:
        print("❌ ERRO: Arquivo ainda não acessível!")
        return False

if __name__ == '__main__':
    success = main()
    
    if success:
        print("\n🎉 CORREÇÃO CONCLUÍDA! Teste a API agora.")
    else:
        print("\n❌ Correção falhou. Verifique os arquivos manualmente.")
