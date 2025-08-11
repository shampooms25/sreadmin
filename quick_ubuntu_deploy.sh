#!/bin/bash
# Script simplificado para execução rápida em produção Ubuntu

echo "🐧 Deploy Rápido POPPFIRE - Ubuntu"
echo "=================================="

# Verificar se está no diretório correto
if [ ! -f "manage.py" ]; then
    echo "❌ Execute este script no diretório /var/www/sreadmin"
    exit 1
fi

echo "🔄 1. Fazendo backup..."
sudo cp -r /var/www/sreadmin /var/www/sreadmin.backup.$(date +%Y%m%d_%H%M%S)

echo "🔄 2. Atualizando código..."
git pull origin main

echo "🔄 3. Configurando permissões..."
sudo chown -R www-data:www-data /var/www/sreadmin/

echo "🔄 4. Instalando dependências..."
sudo -u www-data pip install Pillow requests --quiet

echo "🔄 5. Aplicando migrações..."
sudo -u www-data python manage.py migrate --fake-initial

echo "🔄 6. Coletando arquivos estáticos..."
sudo -u www-data python manage.py collectstatic --noinput

echo "🔄 7. Criando tokens de autenticação..."
sudo -u www-data python manage.py shell << 'EOF'
from captive_portal.models import ApplianceToken

# Token para Postman
obj, created = ApplianceToken.objects.get_or_create(
    token='c8c786467d4a8d2825eaf549534d1ab0',
    defaults={
        'appliance_id': 'POSTMAN-TEST',
        'appliance_name': 'Appliance Teste Postman',
        'description': 'Token para testes via Postman - Ubuntu',
        'is_active': True,
    }
)
print(f'✅ Token Postman: {obj.appliance_name} - Ativo: {obj.is_active}')

# Token para produção
obj2, created2 = ApplianceToken.objects.get_or_create(
    token='f8e7d6c5b4a3928170695e4c3d2b1a0f',
    defaults={
        'appliance_id': 'APPLIANCE-PROD-001',
        'appliance_name': 'Appliance POPPFIRE Produção',
        'description': 'Token para appliance de produção',
        'is_active': True,
    }
)
print(f'✅ Token Produção: {obj2.appliance_name} - Ativo: {obj2.is_active}')
EOF

echo "🔄 8. Configurando serviço systemd..."
sudo tee /etc/systemd/system/poppfire-django.service > /dev/null << 'EOF'
[Unit]
Description=POPPFIRE Django Application
After=network.target postgresql.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/sreadmin
Environment=DJANGO_SETTINGS_MODULE=sreadmin.settings
ExecStart=/var/www/sreadmin/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 9. Reiniciando serviços..."
sudo systemctl daemon-reload
sudo systemctl enable poppfire-django
sudo systemctl restart poppfire-django

echo "🔄 10. Verificando status..."
sudo systemctl is-active poppfire-django

echo ""
echo "🧪 Testando API..."
sleep 3

# Obter IP do servidor
SERVER_IP=$(hostname -I | awk '{print $1}')

echo "Testando endpoint de informações..."
curl -s -H "Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0" \
     "http://127.0.0.1:8000/api/appliances/info/" | head -c 100

echo ""
echo ""
echo "✅ Deploy concluído!"
echo ""
echo "🌐 URLs para teste:"
echo "   API Info: http://$SERVER_IP:8000/api/appliances/info/"
echo "   Admin: http://$SERVER_IP:8000/admin/"
echo "   Portal Status: http://$SERVER_IP:8000/api/appliances/portal/status/"
echo "   Download: http://$SERVER_IP:8000/api/appliances/portal/download/?type=with_video"
echo ""
echo "🔑 Tokens configurados:"
echo "   Teste: c8c786467d4a8d2825eaf549534d1ab0"
echo "   Produção: f8e7d6c5b4a3928170695e4c3d2b1a0f"
echo ""
echo "🔧 Para verificar logs:"
echo "   sudo journalctl -u poppfire-django -f"
echo ""
echo "⚠️ Lembre-se: Use HTTP (não HTTPS) no Postman!"
