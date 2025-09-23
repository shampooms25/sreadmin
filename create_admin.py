#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append('c:\\Projetos\\Poppnet\\sreadmin')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.contrib.auth.models import User

try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
        print("✅ Usuário admin criado com sucesso!")
        print("Username: admin")
        print("Password: admin123")
    else:
        print("✅ Usuário admin já existe!")
        print("Username: admin")
        print("Password: admin123")
except Exception as e:
    print(f"❌ Erro ao criar usuário: {str(e)}")
