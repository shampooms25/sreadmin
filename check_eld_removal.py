#!/usr/bin/env python
"""
Teste para verificar se o link 'ELD Admin' foi removido com sucesso
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.contrib import admin

def check_eld_admin_removal():
    """
    Verifica se o link 'ELD Admin' foi removido com sucesso
    """
    print("=== VERIFICAÇÃO DA REMOÇÃO DO 'ELD ADMIN' ===\n")
    
    # Obter todos os modelos registrados no admin
    registered_models = admin.site._registry
    
    captive_portal_models = []
    
    for model, model_admin in registered_models.items():
        if model._meta.app_label == 'captive_portal':
            captive_portal_models.append({
                'model': model.__name__,
                'verbose_name': model._meta.verbose_name,
                'verbose_name_plural': model._meta.verbose_name_plural,
            })
    
    print("ITENS NO MENU 'GERENCIAR CAPTIVE PORTAL':")
    print("-" * 50)
    for model_info in captive_portal_models:
        print(f"• {model_info['verbose_name_plural']} ({model_info['model']})")
    
    # Verificar se 'ELD Admin' ainda existe
    eld_admin_found = any('ELD Admin' in model_info['verbose_name_plural'] for model_info in captive_portal_models)
    
    print(f"\nTotal de itens no menu: {len(captive_portal_models)}")
    
    if eld_admin_found:
        print("\n❌ ERRO: Link 'ELD Admin' ainda está presente!")
        return False
    else:
        print("\n✅ SUCESSO: Link 'ELD Admin' foi removido com sucesso!")
        print("✅ O menu agora contém apenas os itens necessários:")
        for model_info in captive_portal_models:
            print(f"   - {model_info['verbose_name_plural']}")
        return True

if __name__ == "__main__":
    check_eld_admin_removal()
