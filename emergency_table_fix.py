#!/usr/bin/env python
"""
Script EMERGENCIAL para corrigir caminhos duplicados nos arquivos de portal sem vídeo
ESPECIAL: Contorna validação para corrigir espaços extras
Execute no servidor de produção
"""
import os
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.models import EldPortalSemVideo
from django.core.exceptions import ValidationError

def emergency_fix_portal_paths():
    """EMERGENCIAL: Corrige caminhos duplicados e espaços extras - contornando validação"""
    print("=== CORREÇÃO EMERGENCIAL - Portal sem Vídeo ===")
    
    portais = EldPortalSemVideo.objects.all()
    print(f"Total de portais encontrados: {portais.count()}")
    
    fixed_count = 0
    
    for portal in portais:
        if not portal.arquivo_zip:
            print(f"Portal '{portal.nome}' sem arquivo ZIP - pulando")
            continue
            
        current_name = portal.arquivo_zip.name
        print(f"\nPortal: {portal.nome}")
        print(f"Caminho atual: '{current_name}' (len={len(current_name)})")
        
        # Detectar problemas
        has_duplication = 'portal_sem_video/portal_sem_video/' in current_name
        has_extra_spaces = current_name != current_name.strip()
        needs_fix = has_duplication or has_extra_spaces
        
        if needs_fix:
            # Corrigir o nome
            new_name = current_name
            
            # 1. Remover duplicação se existir
            if has_duplication:
                new_name = new_name.replace('portal_sem_video/portal_sem_video/', 'portal_sem_video/')
                print(f"✂️  Removendo duplicação")
            
            # 2. Fazer trim de espaços
            new_name = new_name.strip()
            print(f"🧹 Removendo espaços extras")
            
            print(f"Novo caminho: '{new_name}' (len={len(new_name)})")
            
            # 3. Salvar SEM chamar clean() para contornar validação
            try:
                # Atualizar diretamente no banco usando update() - não chama clean()
                EldPortalSemVideo.objects.filter(pk=portal.pk).update(
                    arquivo_zip=new_name
                )
                print("✅ Corrigido via UPDATE direto!")
                fixed_count += 1
                
                # Recarregar objeto para verificar
                portal.refresh_from_db()
                print(f"Verificação: '{portal.arquivo_zip.name}'")
                
            except Exception as e:
                print(f"❌ Erro na correção via UPDATE: {e}")
                
                # Fallback: tentar via propriedade direta
                try:
                    portal.arquivo_zip.name = new_name
                    # Usar super() para evitar clean() customizado
                    super(EldPortalSemVideo, portal).save(update_fields=['arquivo_zip'])
                    print("✅ Corrigido via super().save()!")
                    fixed_count += 1
                except Exception as e2:
                    print(f"❌ Erro no fallback: {e2}")
        else:
            print("✅ Caminho já está correto")
            
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
    
    # Verificar portal ativo final
    print(f"\n=== Verificação Final ===")
    portal_ativo = EldPortalSemVideo.objects.filter(ativo=True).first()
    if portal_ativo:
        print(f"Portal ativo: {portal_ativo.nome}")
        final_name = portal_ativo.arquivo_zip.name
        print(f"Caminho final: '{final_name}' (len={len(final_name)})")
        print(f"Path completo: {portal_ativo.arquivo_zip.path}")
        try:
            exists = os.path.exists(portal_ativo.arquivo_zip.path)
            print(f"Arquivo existe: {exists}")
            if exists:
                print("🎉 SUCESSO! Portal sem vídeo corrigido e arquivo existe!")
            else:
                print("⚠️  Arquivo não encontrado no sistema de arquivos")
        except Exception as e:
            print(f"Erro ao verificar: {e}")
    else:
        print("\n⚠️  Nenhum portal ativo encontrado!")

if __name__ == "__main__":
    emergency_fix_portal_paths()
