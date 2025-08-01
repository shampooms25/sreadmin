#!/usr/bin/env python3
"""
Teste das correções do ELD
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from painel.views import eld_main

def test_eld_main():
    """Testa a view eld_main"""
    print("🧪 TESTANDO ELD MAIN VIEW...")
    print("=" * 50)
    
    try:
        # Criar um request factory
        factory = RequestFactory()
        
        # Criar um usuário staff
        user = User.objects.filter(is_staff=True).first()
        if not user:
            user = User.objects.create_user(
                username='testuser',
                password='testpass',
                is_staff=True,
                is_superuser=True
            )
        
        # Criar request simulado
        request = factory.get('/admin/eld/')
        request.user = user
        
        # Adicionar sistema de mensagens
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        print(f"👤 Usuário: {user.username}")
        
        # Chamar a view
        response = eld_main(request)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ View ELD funcionando corretamente!")
            
            # Verificar se o conteúdo está sendo renderizado
            content = response.content.decode('utf-8')
            if 'ELD Admin' in content:
                print("✅ Conteúdo ELD encontrado!")
            else:
                print("⚠️ Conteúdo ELD não encontrado")
                
            return True
        else:
            print(f"❌ Status inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_query():
    """Testa query no banco de dados"""
    print("\n🧪 TESTANDO QUERY NO BANCO...")
    print("=" * 50)
    
    try:
        from painel.models import EldUploadVideo
        from django.db.models import Sum, Count
        
        # Testar agregações
        total_size = EldUploadVideo.objects.aggregate(total=Sum('tamanho'))['total'] or 0
        total_count = EldUploadVideo.objects.count()
        
        print(f"📊 Total de vídeos: {total_count}")
        print(f"📊 Tamanho total: {total_size} MB")
        print("✅ Queries funcionando corretamente!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na query: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test1 = test_eld_main()
    test2 = test_database_query()
    
    print(f"\n🎯 Resultado: {'✅ TODOS OS TESTES PASSARAM' if (test1 and test2) else '❌ ALGUM TESTE FALHOU'}")
