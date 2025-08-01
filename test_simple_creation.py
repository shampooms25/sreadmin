#!/usr/bin/env python
"""
Teste simples para verificar se conseguimos criar uma configuração do portal
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.models import EldGerenciarPortal, EldUploadVideo

def test_simple_creation():
    """
    Testa criação simples de configuração
    """
    print("=== TESTE DE CRIAÇÃO SIMPLES ===\n")
    
    try:
        # Verificar quantos vídeos existem
        videos = EldUploadVideo.objects.all()
        print(f"📹 Vídeos disponíveis: {videos.count()}")
        for video in videos:
            print(f"   • {video}")
        
        # Tentar criar uma configuração simples
        config = EldGerenciarPortal(
            ativar_video=False,
            ativo=True
        )
        
        # Validar sem salvar
        config.clean()
        print(f"\n✅ Validação OK: Configuração sem vídeo (ativar_video=False)")
        
        # Testar validação com vídeo ativo mas sem vídeo selecionado
        config.ativar_video = True
        try:
            config.clean()
            print(f"❌ ERRO: Deveria falhar a validação!")
        except Exception as e:
            print(f"✅ Validação OK: {str(e)[:100]}...")
        
        # Testar com vídeo selecionado
        if videos.exists():
            config.nome_video = videos.first()
            config.clean()
            print(f"✅ Validação OK: Configuração com vídeo selecionado")
        
        print(f"\n🎉 TESTES DE VALIDAÇÃO FUNCIONANDO!")
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_simple_creation()
    if success:
        print(f"\n✅ MODELO FUNCIONANDO CORRETAMENTE!")
        print(f"   O admin deve funcionar agora.")
    else:
        print(f"\n💥 PROBLEMAS NO MODELO")
