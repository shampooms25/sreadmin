#!/usr/bin/env python
"""
Script MAIS SIMPLES para correção - usando ORM Django com update()
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.models import EldPortalSemVideo

print("=== CORREÇÃO SIMPLES VIA ORM ===")

# Buscar portal ativo
portal = EldPortalSemVideo.objects.filter(ativo=True).first()

if not portal:
    print("❌ Nenhum portal ativo encontrado")
    exit(1)

print(f"Portal encontrado: {portal.nome}")
current_name = portal.arquivo_zip.name
print(f"Caminho atual: '{current_name}' (len={len(current_name)})")

# Verificar se precisa corrigir
needs_fix = ('portal_sem_video/portal_sem_video/' in current_name or 
             current_name != current_name.strip())

if needs_fix:
    # Corrigir o nome
    new_name = current_name.replace('portal_sem_video/portal_sem_video/', 'portal_sem_video/').strip()
    print(f"Novo caminho: '{new_name}' (len={len(new_name)})")
    
    # Usar update() que não chama clean() nem save()
    affected = EldPortalSemVideo.objects.filter(pk=portal.pk).update(arquivo_zip=new_name)
    print(f"Registros atualizados: {affected}")
    
    # Verificar resultado
    portal.refresh_from_db()
    final_name = portal.arquivo_zip.name
    print(f"Resultado final: '{final_name}' (len={len(final_name)})")
    
    # Verificar se arquivo existe
    try:
        path = portal.arquivo_zip.path
        exists = os.path.exists(path)
        print(f"Path: {path}")
        print(f"Arquivo existe: {exists}")
        
        if exists:
            print("🎉 SUCESSO! Arquivo corrigido e existe!")
        else:
            print("⚠️  Caminho corrigido mas arquivo não encontrado")
            
            # Tentar encontrar o arquivo
            import glob
            media_dir = os.path.dirname(path)
            pattern = os.path.join(media_dir, "*.zip")
            files = glob.glob(pattern)
            print(f"Arquivos ZIP encontrados em {media_dir}:")
            for f in files:
                print(f"  {f}")
                
    except Exception as e:
        print(f"Erro ao verificar path: {e}")
        
else:
    print("✅ Caminho já está correto")
    
    # Mesmo assim, verificar se arquivo existe
    try:
        path = portal.arquivo_zip.path
        exists = os.path.exists(path)
        print(f"Path: {path}")
        print(f"Arquivo existe: {exists}")
        
        if not exists:
            print("❌ Arquivo não existe no sistema!")
    except Exception as e:
        print(f"Erro: {e}")

print("\n=== TESTANDO API ===")
try:
    from captive_portal.api_views import portal_download
    from django.test import RequestFactory
    
    factory = RequestFactory()
    request = factory.get('/api/appliances/portal/download/?type=without_video')
    request.appliance_user = type('Mock', (), {'username': 'test-appliance'})()
    
    response = portal_download(request)
    print(f"API Status: {response.status_code}")
    
    if response.status_code == 200:
        print("🎉 API FUNCIONANDO!")
        if hasattr(response, 'content'):
            print(f"Content Length: {len(response.content)} bytes")
    else:
        print("❌ API ainda com problema")
        if hasattr(response, 'content'):
            try:
                import json
                error = json.loads(response.content.decode())
                print(f"Erro: {error}")
            except:
                print(f"Response: {response.content.decode()[:200]}...")
                
except Exception as e:
    print(f"Erro no teste API: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Script concluído!")
