#!/usr/bin/env python
"""
Teste específico para verificar o admin do GerenciarPortalProxy
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.contrib import admin
from painel.admin import GerenciarPortalProxy, EldGerenciarPortalAdmin
from painel.models import EldGerenciarPortal

def test_proxy_admin():
    """
    Testa o proxy admin para detectar problemas
    """
    print("=== TESTE DO PROXY ADMIN ===\n")
    
    # Verificar se o proxy está registrado
    registered_models = admin.site._registry
    
    if GerenciarPortalProxy in registered_models:
        print("✅ GerenciarPortalProxy está registrado no admin")
        admin_class = registered_models[GerenciarPortalProxy]
        print(f"   Admin class: {admin_class.__class__.__name__}")
    else:
        print("❌ GerenciarPortalProxy NÃO está registrado")
        return False
    
    # Verificar os campos do modelo proxy
    print(f"\n📋 CAMPOS DO MODELO PROXY:")
    print(f"   Modelo base: {GerenciarPortalProxy.__bases__}")
    print(f"   Meta app_label: {GerenciarPortalProxy._meta.app_label}")
    print(f"   Tabela DB: {GerenciarPortalProxy._meta.db_table}")
    
    # Listar campos disponíveis
    print(f"\n🔍 CAMPOS DISPONÍVEIS:")
    for field in GerenciarPortalProxy._meta.fields:
        print(f"   • {field.name} ({field.__class__.__name__})")
    
    # Verificar admin fields
    admin_instance = admin_class
    print(f"\n⚙️ CONFIGURAÇÃO DO ADMIN:")
    print(f"   fields: {getattr(admin_instance, 'fields', 'Não definido')}")
    print(f"   list_display: {getattr(admin_instance, 'list_display', 'Não definido')}")
    print(f"   readonly_fields: {getattr(admin_instance, 'readonly_fields', 'Não definido')}")
    
    # Testar formfield_for_foreignkey
    try:
        print(f"\n🧪 TESTE DE FORMFIELD:")
        # Simular request e field
        class MockRequest:
            pass
        
        class MockField:
            name = 'nome_video'
        
        request = MockRequest()
        field = MockField()
        result = admin_instance.formfield_for_foreignkey(field, request)
        print(f"   ✅ formfield_for_foreignkey funcionando")
        
    except Exception as e:
        print(f"   ❌ Erro em formfield_for_foreignkey: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_proxy_admin()
    if success:
        print(f"\n🎉 PROXY ADMIN FUNCIONANDO!")
    else:
        print(f"\n💥 PROBLEMAS NO PROXY ADMIN")
