#!/usr/bin/env python
"""
Script para verificar e sincronizar os tokens do ApplianceToken
"""

import os
import sys
import django

# Setup do Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from captive_portal.models import ApplianceToken
import json
from django.utils import timezone
from datetime import datetime

def verify_and_sync_tokens():
    """Verificar tabela e sincronizar tokens"""
    
    print("🔍 Verificando tabela ApplianceToken...")
    
    try:
        # Testar se a tabela existe
        total_tokens = ApplianceToken.objects.count()
        print(f"✅ Tabela existe! Total de tokens no banco: {total_tokens}")
        
        # Carregar tokens do JSON
        json_file = 'appliance_tokens.json'
        if os.path.exists(json_file):
            print(f"📄 Carregando tokens do arquivo {json_file}...")
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            tokens_data = data.get('tokens', {})
            print(f"📊 Encontrados {len(tokens_data)} tokens no JSON")
            
            synced_count = 0
            updated_count = 0
            
            for token, info in tokens_data.items():
                try:
                    # Verificar se o token já existe
                    obj, created = ApplianceToken.objects.get_or_create(
                        token=token,
                        defaults={
                            'appliance_id': info['appliance_id'],
                            'appliance_name': info['appliance_name'],
                            'description': info['description'],
                            'is_active': True,
                            'created_at': timezone.now(),
                        }
                    )
                    
                    if created:
                        print(f"  ✅ Token criado: {token[:16]}...")
                        synced_count += 1
                    else:
                        # Atualizar informações se necessário
                        updated = False
                        if obj.appliance_name != info['appliance_name']:
                            obj.appliance_name = info['appliance_name']
                            updated = True
                        if obj.description != info['description']:
                            obj.description = info['description']
                            updated = True
                        
                        if updated:
                            obj.save()
                            print(f"  🔄 Token atualizado: {token[:16]}...")
                            updated_count += 1
                        else:
                            print(f"  ℹ️ Token já existe: {token[:16]}...")
                    
                    # Atualizar last_used se disponível
                    if info.get('last_used'):
                        try:
                            last_used_str = info['last_used']
                            # Tentar vários formatos de data
                            for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%SZ']:
                                try:
                                    last_used = datetime.strptime(last_used_str, fmt)
                                    obj.last_used = timezone.make_aware(last_used)
                                    obj.save()
                                    break
                                except ValueError:
                                    continue
                        except Exception as e:
                            print(f"    ⚠️ Erro ao processar last_used: {e}")
                    
                except Exception as e:
                    print(f"  ❌ Erro ao processar token {token[:16]}...: {e}")
            
            print(f"\n📈 Sincronização concluída:")
            print(f"   - Tokens criados: {synced_count}")
            print(f"   - Tokens atualizados: {updated_count}")
            print(f"   - Total no banco após sync: {ApplianceToken.objects.count()}")
            
        else:
            print(f"⚠️ Arquivo {json_file} não encontrado")
        
        # Listar todos os tokens
        print("\n📋 Tokens ativos no sistema:")
        for token in ApplianceToken.objects.filter(is_active=True):
            status = "🟢 Ativo" if token.is_active else "🔴 Inativo"
            last_used = token.last_used.strftime("%d/%m/%Y %H:%M") if token.last_used else "Nunca usado"
            print(f"  {status} {token.appliance_name} ({token.appliance_id})")
            print(f"    Token: {token.token[:16]}...")
            print(f"    Último uso: {last_used}")
            print(f"    Descrição: {token.description}")
            print()
        
        print("✅ Verificação concluída com sucesso!")
        print(f"🌐 Acesse: http://localhost:8000/admin/captive_portal/appliancetoken/")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar tabela: {e}")
        print(f"💡 Tente executar: python manage.py migrate captive_portal")
        return False

if __name__ == '__main__':
    verify_and_sync_tokens()
