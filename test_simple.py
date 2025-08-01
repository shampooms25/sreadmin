import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.template.loader import get_template

try:
    template = get_template('admin/painel/starlink/dashboard.html')
    print("✅ Template carregado com sucesso")
    
    context = {
        'title': 'Dashboard Starlink',
        'breadcrumbs': [
            {'name': 'Admin', 'url': '/admin/'},
            {'name': 'Starlink', 'url': '/admin/starlink/'},
            {'name': 'Dashboard', 'url': None}
        ],
        'available_accounts': {
            'ACC-2744134-64041-5': {
                'name': 'Conta Principal',
                'description': 'Conta principal consolidada'
            }
        },
        'selected_account': 'ACC-2744134-64041-5',
        'account_info': {
            'name': 'Conta Principal',
            'description': 'Conta principal consolidada'
        },
        'has_statistics': True,
        'total_service_lines': 42,
        'statistics': {
            'active_lines': 35,
            'offline_lines': 5,
            'no_data_lines': 2
        }
    }
    
    rendered = template.render(context)
    print("✅ Template renderizado com sucesso")
    print(f"📊 Template renderizado com {len(rendered)} caracteres")
    print("🎉 TEMPLATE DASHBOARD.HTML FUNCIONANDO CORRETAMENTE!")
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
