import os, sys, django
sys.path.insert(0, '/var/www/sreadmin')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()
from painel.models import EldPortalSemVideo

print('=== DEBUG COMPLETO DA API ===')

portal = EldPortalSemVideo.objects.filter(ativo=True).first()
if portal:
    print(f'Portal: {portal.nome}')
    print(f'arquivo_zip.name: "{portal.arquivo_zip.name}"')
    
    file_path = portal.arquivo_zip.path
    print(f'file_path: "{file_path}"')
    print(f'file_path length: {len(file_path)}')
    print(f'file_path repr: {repr(file_path)}')
    
    exists = os.path.exists(file_path)
    print(f'os.path.exists: {exists}')
    
    # Testar paths limpos
    clean_path = file_path.strip()
    clean_exists = os.path.exists(clean_path)
    print(f'clean_path exists: {clean_exists}')
    print(f'clean_path: "{clean_path}"')
    
    if clean_exists:
        print('✅ PATH LIMPO FUNCIONA!')
        # Simular o que aconteceria na API
        try:
            with open(clean_path, 'rb') as f:
                data = f.read(100)
                print(f'Arquivo legível: {len(data)} bytes lidos')
                print('✅ ARQUIVO TOTALMENTE ACESSÍVEL!')
        except Exception as e:
            print(f'Erro ao ler: {e}')
else:
    print('Nenhum portal encontrado')
