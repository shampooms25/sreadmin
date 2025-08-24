#!/usr/bin/env python
"""
Script para corrigir caminhos duplicados nos arquivos de portal sem vídeo
Execute no servidor de produção
"""
import os
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.models import EldPortalSemVideo

def fix_portal_paths():
    """Corrige caminhos duplicados de portais sem vídeo"""
    print("=== Correção de Caminhos - Portal sem Vídeo ===")
    
    portais = EldPortalSemVideo.objects.all()
    print(f"Total de portais encontrados: {portais.count()}")
    
    fixed_count = 0
    
    for portal in portais:
        if not portal.arquivo_zip:
            print(f"Portal '{portal.nome}' sem arquivo ZIP - pulando")
            continue
            
        current_name = portal.arquivo_zip.name
        print(f"\nPortal: {portal.nome}")
        print(f"Caminho atual: '{current_name}'")
        
        # Verificar se há duplicação
        if 'portal_sem_video/portal_sem_video/' in current_name:
            # Remover duplicação
            new_name = current_name.replace('portal_sem_video/portal_sem_video/', 'portal_sem_video/')
            print(f"CORREÇÃO: Removendo duplicação")
            print(f"Novo caminho: '{new_name}'")
            
            portal.arquivo_zip.name = new_name
            portal.save()
            fixed_count += 1
            print("✅ Corrigido!")
            
        elif current_name.startswith('portal_sem_video/'):
            # Caminho correto, mas vamos normalizar para apenas nome do arquivo
            filename = os.path.basename(current_name)
            if filename != current_name:
                print(f"NORMALIZAÇÃO: Simplificando para nome do arquivo")
                print(f"Novo caminho: '{filename}'")
                
                portal.arquivo_zip.name = filename
                portal.save()
                fixed_count += 1
                print("✅ Normalizado!")
            else:
                print("✅ Já está correto")
        else:
            print("✅ Caminho OK")
            
        # Verificar se arquivo existe
        try:
            path = portal.arquivo_zip.path
            exists = os.path.exists(path)
            print(f"Arquivo existe: {exists}")
            if not exists:
                print(f"⚠️  ATENÇÃO: Arquivo não encontrado em: {path}")
        except Exception as e:
            print(f"❌ Erro ao verificar arquivo: {e}")
    
    print(f"\n=== Resumo ===")
    print(f"Portais corrigidos: {fixed_count}")
    print(f"Total de portais: {portais.count()}")
    
    # Verificar portal ativo
    portal_ativo = EldPortalSemVideo.objects.filter(ativo=True).first()
    if portal_ativo:
        print(f"\nPortal ativo: {portal_ativo.nome}")
        print(f"Caminho final: {portal_ativo.arquivo_zip.name}")
        print(f"Path completo: {portal_ativo.arquivo_zip.path}")
        try:
            exists = os.path.exists(portal_ativo.arquivo_zip.path)
            print(f"Arquivo existe: {exists}")
        except Exception as e:
            print(f"Erro ao verificar: {e}")
    else:
        print("\n⚠️  Nenhum portal ativo encontrado!")

if __name__ == "__main__":
    fix_portal_paths()
