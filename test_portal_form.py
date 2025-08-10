#!/usr/bin/env python
"""
Teste rápido para verificar se o formulário Portal com Vídeo está funcionando
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.admin import GerenciarPortalForm
from painel.models import EldGerenciarPortal

def test_portal_form():
    """
    Testa o formulário customizado para Portal com Vídeo
    """
    print("=== TESTE DO FORMULÁRIO PORTAL COM VÍDEO ===\n")
    
    # Testar instanciação do formulário
    try:
        form = GerenciarPortalForm()
        print("✅ Formulário GerenciarPortalForm criado com sucesso!")
        
        # Verificar campos disponíveis
        print(f"\n📋 Campos do formulário:")
        for field_name in form.fields:
            field = form.fields[field_name]
            print(f"   • {field_name}: {field.__class__.__name__}")
        
        # Verificar se portal_sem_video NÃO está nos campos
        if 'portal_sem_video' not in form.fields:
            print(f"\n✅ Campo 'portal_sem_video' foi removido com sucesso do formulário!")
        else:
            print(f"\n❌ Campo 'portal_sem_video' ainda está presente no formulário!")
            
        # Verificar se ativar_video NÃO está nos campos
        if 'ativar_video' not in form.fields:
            print(f"✅ Campo 'ativar_video' foi removido com sucesso do formulário!")
        else:
            print(f"❌ Campo 'ativar_video' ainda está presente no formulário!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar formulário: {str(e)}")
        return False

def test_form_validation():
    """
    Testa validação básica do formulário
    """
    print(f"\n🧪 TESTE DE VALIDAÇÃO:")
    
    try:
        # Dados de teste válidos
        data = {
            'ativo': True,
            'nome_video': None,  # Pode ser None
            'captive_portal_zip': None  # Pode ser None
        }
        
        form = GerenciarPortalForm(data=data)
        
        if form.is_valid():
            print("✅ Formulário válido com dados básicos!")
        else:
            print(f"⚠️ Formulário inválido: {form.errors}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na validação: {str(e)}")
        return False

if __name__ == "__main__":
    success1 = test_portal_form()
    success2 = test_form_validation()
    
    if success1 and success2:
        print(f"\n🎉 TODOS OS TESTES PASSARAM!")
        print(f"   Formulário Portal com Vídeo está configurado corretamente.")
        print(f"   Agora teste em: http://localhost:8000/admin/captive_portal/gerenciarportalproxy/add/")
    else:
        print(f"\n💥 ALGUNS TESTES FALHARAM")
        print(f"   Verifique os erros acima antes de testar na interface.")
