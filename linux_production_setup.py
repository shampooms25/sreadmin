#!/usr/bin/env python
"""
Configuração específica para ambiente de produção Linux
Resolve diferenças entre Windows (desenvolvimento) e Linux (produção)
"""

import os
import sys
import platform
import django
import json
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from captive_portal.models import ApplianceToken
from django.conf import settings

def ensure_production_tokens():
    """
    Criar tokens específicos para produção Linux
    """
    print("🔧 Configurando tokens para produção Linux...")
    
    # Token que você está usando no Postman
    postman_token = 'c8c786467d4a8d2825eaf549534d1ab0'
    
    # Tokens de produção
    production_tokens = [
        {
            'token': postman_token,
            'appliance_id': 'POSTMAN-TEST',
            'appliance_name': 'Appliance Teste Postman',
            'description': 'Token para testes via Postman - Ambiente Linux',
            'is_active': True,
        },
        {
            'token': 'f8e7d6c5b4a3928170695e4c3d2b1a0f',
            'appliance_id': 'APPLIANCE-PROD-001',
            'appliance_name': 'Appliance POPPFIRE Produção 001',
            'description': 'Token para appliance de produção principal',
            'is_active': True,
        },
        {
            'token': '1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p',
            'appliance_id': 'APPLIANCE-BACKUP',
            'appliance_name': 'Appliance POPPFIRE Backup',
            'description': 'Token para appliance de backup',
            'is_active': True,
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for token_data in production_tokens:
        obj, created = ApplianceToken.objects.get_or_create(
            token=token_data['token'],
            defaults=token_data
        )
        
        if created:
            created_count += 1
            print(f"✅ Token criado: {obj.appliance_name}")
        else:
            # Atualizar se necessário
            updated = False
            for field in ['appliance_id', 'appliance_name', 'description', 'is_active']:
                if getattr(obj, field) != token_data[field]:
                    setattr(obj, field, token_data[field])
                    updated = True
            
            if updated:
                obj.save()
                updated_count += 1
                print(f"🔄 Token atualizado: {obj.appliance_name}")
            else:
                print(f"ℹ️ Token OK: {obj.appliance_name}")
    
    print(f"\n📊 Resumo: {created_count} criados, {updated_count} atualizados")
    return production_tokens

def create_linux_config():
    """
    Criar configurações específicas para Linux
    """
    print("\n🐧 Criando configurações para Linux...")
    
    # Criar arquivo de configuração para nginx/apache
    nginx_config = """
# Configuração Nginx para POPPFIRE API
server {
    listen 80;
    server_name seu-servidor.com;
    
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Headers para API
        proxy_set_header Authorization $http_authorization;
    }
    
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /var/www/sreadmin/static/;
        expires 30d;
    }
    
    location /media/ {
        alias /var/www/sreadmin/media/;
        expires 7d;
    }
}
"""
    
    with open('nginx_poppfire.conf', 'w') as f:
        f.write(nginx_config)
    print("✅ Configuração nginx criada: nginx_poppfire.conf")
    
    # Criar script de inicialização para systemd
    systemd_service = """[Unit]
Description=POPPFIRE Django Application
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/sreadmin
Environment=DJANGO_SETTINGS_MODULE=sreadmin.settings
ExecStart=/var/www/sreadmin/venv/bin/python manage.py runserver 127.0.0.1:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    with open('poppfire-django.service', 'w') as f:
        f.write(systemd_service)
    print("✅ Service systemd criado: poppfire-django.service")

def fix_linux_permissions():
    """
    Corrigir permissões específicas do Linux
    """
    print("\n🔐 Configurando permissões para Linux...")
    
    # Comandos para executar no Linux
    linux_commands = [
        "sudo chown -R www-data:www-data /var/www/sreadmin/",
        "sudo chmod -R 755 /var/www/sreadmin/",
        "sudo chmod -R 775 /var/www/sreadmin/media/",
        "sudo chmod 644 /var/www/sreadmin/appliance_tokens.json",
        "sudo systemctl daemon-reload",
        "sudo systemctl enable poppfire-django",
        "sudo systemctl start poppfire-django",
        "sudo cp nginx_poppfire.conf /etc/nginx/sites-available/",
        "sudo ln -sf /etc/nginx/sites-available/nginx_poppfire.conf /etc/nginx/sites-enabled/",
        "sudo nginx -t && sudo systemctl reload nginx"
    ]
    
    print("📋 Comandos para executar no servidor Linux:")
    for cmd in linux_commands:
        print(f"   {cmd}")
    
    # Criar script de setup para Linux
    setup_script = "#!/bin/bash\n"
    setup_script += "# Script de setup para produção Linux\n\n"
    setup_script += "echo '🐧 Configurando POPPFIRE para produção Linux...'\n\n"
    
    for cmd in linux_commands:
        setup_script += f"echo 'Executando: {cmd}'\n"
        setup_script += f"{cmd}\n"
        setup_script += "if [ $? -eq 0 ]; then\n"
        setup_script += "    echo '✅ OK'\nelse\n"
        setup_script += "    echo '❌ ERRO'\nfi\n\n"
    
    setup_script += "echo '🎉 Setup concluído!'\n"
    
    with open('setup_linux_production.sh', 'w') as f:
        f.write(setup_script)
    
    print("✅ Script de setup criado: setup_linux_production.sh")

def create_windows_vs_linux_guide():
    """
    Criar guia de diferenças entre Windows e Linux
    """
    guide = """# Guia: Diferenças Windows vs Linux para POPPFIRE API

## Principais Diferenças

### 1. Caminhos de Arquivo
- **Windows**: `C:\\Projetos\\Poppnet\\sreadmin`
- **Linux**: `/var/www/sreadmin`

### 2. Permissões
- **Windows**: Não há conceito de owner/group como no Linux
- **Linux**: Precisa configurar `www-data:www-data` e permissões 755/775

### 3. Servidor Web
- **Windows**: Geralmente desenvolvimento com `python manage.py runserver`
- **Linux**: Produção com nginx/apache + systemd service

### 4. Endereços de Rede
- **Windows**: `127.0.0.1` ou `localhost`
- **Linux**: IP do servidor (ex: `172.18.25.253`)

### 5. Arquivo appliance_tokens.json
- **Windows**: Pode não existir, usa tokens do banco
- **Linux**: Precisa de permissões corretas se existir

## Configuração para Desenvolvimento (Windows)

```bash
# Instalar dependências
pip install -r requirements.txt

# Aplicar migrações
python manage.py migrate

# Criar tokens
python debug_multiplatform.py

# Iniciar servidor
python manage.py runserver 127.0.0.1:8000
```

## Configuração para Produção (Linux)

```bash
# Executar script de produção
./production_deploy.sh

# Ou configuração manual
python linux_production_setup.py
./setup_linux_production.sh
```

## URLs de Teste

### Windows (Desenvolvimento)
- API Info: `http://127.0.0.1:8000/api/appliances/info/`
- Admin: `http://127.0.0.1:8000/admin/`

### Linux (Produção)
- API Info: `http://SEU-IP:8000/api/appliances/info/`
- Admin: `http://SEU-IP:8000/admin/`

## Headers de Autenticação

```
Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0
Content-Type: application/json
```

## Troubleshooting

### Windows
- Verificar se o servidor está rodando
- Confirmar que não há firewall bloqueando
- Usar 127.0.0.1 em vez de 0.0.0.0

### Linux
- Verificar permissões de arquivos
- Confirmar que a porta 8000 está liberada
- Checar logs: `journalctl -u poppfire-django -f`
- Verificar nginx: `sudo nginx -t`

### Ambos
- Confirmar que o token existe no banco
- Verificar logs do Django
- Testar autenticação com script debug
"""
    
    with open('WINDOWS_VS_LINUX_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("✅ Guia criado: WINDOWS_VS_LINUX_GUIDE.md")

def main():
    print("🌐 Configuração Multiplataforma POPPFIRE")
    print("=" * 50)
    
    current_os = platform.system()
    print(f"🖥️ Sistema atual: {current_os}")
    
    # Configurar tokens
    tokens = ensure_production_tokens()
    
    if current_os == "Windows":
        print("\n📝 Executando configuração para desenvolvimento Windows...")
        print("✅ Tokens configurados para desenvolvimento")
        
        print("\n🚀 Para testar no Windows:")
        print("1. python manage.py runserver 127.0.0.1:8000")
        print("2. Teste no Postman: http://127.0.0.1:8000/api/appliances/info/")
        print(f"3. Header: Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0")
        
    else:
        print("\n📝 Executando configuração para produção Linux...")
        create_linux_config()
        fix_linux_permissions()
    
    # Criar guia sempre
    create_windows_vs_linux_guide()
    
    print("\n" + "=" * 50)
    print("✅ Configuração multiplataforma concluída!")
    
    print(f"\n🔑 Token principal: c8c786467d4a8d2825eaf549534d1ab0")
    print("📁 Arquivos criados:")
    print("   - WINDOWS_VS_LINUX_GUIDE.md")
    if current_os != "Windows":
        print("   - nginx_poppfire.conf")
        print("   - poppfire-django.service") 
        print("   - setup_linux_production.sh")

if __name__ == '__main__':
    main()
