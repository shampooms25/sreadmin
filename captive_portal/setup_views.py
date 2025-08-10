"""
View temporária para executar a migração da tabela ApplianceToken
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, transaction
import json
import os


@csrf_exempt
def setup_appliance_tokens(request):
    """
    View para configurar a tabela ApplianceToken
    """
    results = []
    
    try:
        # 1. Criar tabela diretamente
        results.append("🔄 Criando tabela ApplianceToken...")
        
        sql = '''
        CREATE TABLE IF NOT EXISTS captive_portal_appliancetoken (
            id SERIAL PRIMARY KEY,
            token VARCHAR(64) UNIQUE NOT NULL,
            appliance_id VARCHAR(100) UNIQUE NOT NULL,
            appliance_name VARCHAR(200) NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            last_used TIMESTAMP WITH TIME ZONE,
            ip_address INET
        );
        
        CREATE UNIQUE INDEX IF NOT EXISTS captive_portal_appliancetoken_token_unique 
            ON captive_portal_appliancetoken(token);
        CREATE UNIQUE INDEX IF NOT EXISTS captive_portal_appliancetoken_appliance_id_unique 
            ON captive_portal_appliancetoken(appliance_id);
        '''
        
        with connection.cursor() as cursor:
            cursor.execute(sql)
        
        results.append("✅ Tabela criada com sucesso!")
        
        # 2. Testar acesso via ORM
        results.append("🔍 Testando acesso via Django ORM...")
        
        from captive_portal.models import ApplianceToken
        count = ApplianceToken.objects.count()
        results.append(f"✅ Tabela acessível! Total de registros: {count}")
        
        # 3. Sincronizar tokens do JSON se a tabela estiver vazia
        if count == 0:
            results.append("🔄 Sincronizando tokens do JSON...")
            
            json_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'appliance_tokens.json')
            
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    tokens_data = json.load(f)
                
                tokens = tokens_data.get('tokens', {})
                synced = 0
                
                for token, info in tokens.items():
                    if not ApplianceToken.objects.filter(token=token).exists():
                        ApplianceToken.objects.create(
                            token=token,
                            appliance_id=info['appliance_id'],
                            appliance_name=info['appliance_name'],
                            description=info.get('description', ''),
                            is_active=True
                        )
                        synced += 1
                        results.append(f"  ✅ {info['appliance_name']}")
                
                results.append(f"✅ {synced} tokens sincronizados!")
            else:
                results.append("⚠️ Arquivo appliance_tokens.json não encontrado")
        else:
            results.append(f"ℹ️ Tabela já possui {count} registros")
        
        # 4. Marcar migração como aplicada
        results.append("🔄 Marcando migração como aplicada...")
        
        try:
            from django.db.migrations.recorder import MigrationRecorder
            recorder = MigrationRecorder(connection)
            recorder.record_applied('captive_portal', '0004_appliancetoken')
            results.append("✅ Migração marcada como aplicada!")
        except Exception as e:
            results.append(f"⚠️ Aviso: {e}")
        
        results.append("🎉 CONFIGURAÇÃO CONCLUÍDA!")
        results.append("✅ Sistema de tokens pronto para uso!")
        results.append("✅ Acesse /admin/captive_portal/appliancetoken/")
        
        return JsonResponse({
            'success': True,
            'message': 'Sistema configurado com sucesso!',
            'details': results
        })
        
    except Exception as e:
        results.append(f"❌ Erro: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'details': results
        })


def check_appliance_tokens(request):
    """
    View para verificar o status do sistema de tokens
    """
    try:
        from captive_portal.models import ApplianceToken
        
        # Estatísticas
        total = ApplianceToken.objects.count()
        active = ApplianceToken.objects.filter(is_active=True).count()
        used = ApplianceToken.objects.filter(last_used__isnull=False).count()
        
        # Listar tokens
        tokens = []
        for token in ApplianceToken.objects.all()[:10]:  # Primeiros 10
            tokens.append({
                'id': token.id,
                'appliance_name': token.appliance_name,
                'appliance_id': token.appliance_id,
                'is_active': token.is_active,
                'last_used': token.last_used.isoformat() if token.last_used else None,
                'created_at': token.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'statistics': {
                'total': total,
                'active': active,
                'used': used,
                'unused': active - used
            },
            'tokens': tokens
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
