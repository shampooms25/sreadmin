#!/usr/bin/env python3
"""
Teste direto da view do Django sem autenticação HTTP
"""

import os
import sys
import django

# Configurar Django ANTES de importar qualquer modelo
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from painel.views import starlink_usage_report

def test_view_directly():
    """Testa a view diretamente sem HTTP"""
    print("🎯 TESTANDO VIEW DIRETAMENTE...")
    print("=" * 50)
    
    try:
        # Criar um request factory
        factory = RequestFactory()
        
        # Criar um usuário staff para simular autenticação
        user = User.objects.filter(is_staff=True).first()
        if not user:
            print("❌ Nenhum usuário staff encontrado no banco")
            return False
        
        # Criar request simulado
        request = factory.get('/admin/starlink/usage-report/', {
            'account_id': 'ACC-2744134-64041-5'
        })
        
        # Adicionar usuário ao request
        request.user = user
        
        # Adicionar sistema de mensagens (necessário para a view)
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        print(f"👤 Usuário autenticado: {user.username}")
        print(f"📋 Account ID: ACC-2744134-64041-5")
        
        # Chamar a view
        response = starlink_usage_report(request)
        
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            print(f"📏 Tamanho do conteúdo: {len(content)} caracteres")
            
            # Verificar se nossa Service Line está presente
            target_sl = "SL-854897-75238-43"
            if target_sl in content:
                print(f"✅ Service Line {target_sl} encontrada!")
                
                # Procurar por valores próximos de 90
                import re
                gb_values = re.findall(r'(\d+\.?\d*)\s*GB', content)
                print(f"📊 Valores GB encontrados: {gb_values[:10]}...")  # Primeiros 10
                
                for value_str in gb_values:
                    try:
                        value = float(value_str)
                        if 85 <= value <= 95:
                            print(f"✅ Valor correto encontrado: {value} GB")
                            return True
                    except ValueError:
                        continue
                
                print(f"❌ Valor próximo de 90 GB não encontrado")
                return False
            else:
                print(f"❌ Service Line {target_sl} não encontrada")
                
                # Verificar se há erro
                if "error-message" in content:
                    print("❌ Página contém mensagem de erro")
                elif "empty-state" in content:
                    print("📭 Página mostra estado vazio")
                else:
                    print("⚠️  Conteúdo inesperado")
                
                return False
        else:
            print(f"❌ Status inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_view_directly()
    print(f"\n🎯 Resultado: {'✅ SUCESSO' if success else '❌ FALHA'}")
