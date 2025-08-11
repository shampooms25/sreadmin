# 🐧 GUIA DEFINITIVO: Correção em Produção Ubuntu

## 🚀 PASSOS RÁPIDOS (Método Automático)

### 1. Conectar no servidor Ubuntu:
```bash
ssh usuario@SEU-IP-SERVIDOR
cd /var/www/sreadmin
```

### 2. Executar script automático:
```bash
# Fazer backup
sudo cp -r /var/www/sreadmin /var/www/sreadmin.backup.$(date +%Y%m%d_%H%M%S)

# Executar deploy
chmod +x production_deploy.sh
sudo ./production_deploy.sh
```

### 3. Verificar se funcionou:
```bash
curl -H "Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0" \
     http://SEU-IP:8000/api/appliances/info/
```

---

## 🔧 PASSOS MANUAIS (Método Detalhado)

### 1. **Backup de Segurança**
```bash
sudo cp -r /var/www/sreadmin /var/www/sreadmin.backup.$(date +%Y%m%d_%H%M%S)
python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json
```

### 2. **Atualizar Código**
```bash
git pull origin main
sudo chown -R www-data:www-data /var/www/sreadmin/
```

### 3. **Configurar Ambiente Virtual**
```bash
sudo -u www-data python3 -m venv venv
sudo -u www-data source venv/bin/activate
sudo -u www-data pip install -r requirements.txt
sudo -u www-data pip install Pillow requests
```

### 4. **Migrações do Banco**
```bash
sudo -u www-data python manage.py migrate --fake-initial
sudo -u www-data python manage.py collectstatic --noinput
```

### 5. **Criar Tokens de Autenticação**
```bash
sudo -u www-data python manage.py shell << 'EOF'
from captive_portal.models import ApplianceToken

# Token para Postman (seu teste)
obj, created = ApplianceToken.objects.get_or_create(
    token='c8c786467d4a8d2825eaf549534d1ab0',
    defaults={
        'appliance_id': 'POSTMAN-TEST',
        'appliance_name': 'Appliance Teste Postman',
        'description': 'Token para testes via Postman - Ubuntu',
        'is_active': True,
    }
)
print(f'✅ Token Postman: {obj.token} - Ativo: {obj.is_active}')

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
print(f'✅ Token Produção: {obj2.token} - Ativo: {obj2.is_active}')
EOF
```

### 6. **Configurar Permissões**
```bash
sudo chown -R www-data:www-data /var/www/sreadmin/
sudo chmod -R 755 /var/www/sreadmin/
sudo chmod -R 775 /var/www/sreadmin/media/
```

### 7. **Configurar Systemd Service**
```bash
sudo tee /etc/systemd/system/poppfire-django.service << 'EOF'
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

sudo systemctl daemon-reload
sudo systemctl enable poppfire-django
sudo systemctl start poppfire-django
```

### 8. **Verificar Status do Serviço**
```bash
sudo systemctl status poppfire-django
sudo journalctl -u poppfire-django -f
```

### 9. **Configurar Nginx (Opcional, mas Recomendado)**
```bash
sudo tee /etc/nginx/sites-available/poppfire << 'EOF'
server {
    listen 80;
    server_name SEU-IP-SERVIDOR;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Authorization $http_authorization;
    }

    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
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
EOF

sudo ln -sf /etc/nginx/sites-available/poppfire /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🧪 TESTES FINAIS

### 1. **Testar API Info**
```bash
curl -H "Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0" \
     http://SEU-IP:8000/api/appliances/info/
```

### 2. **Testar Portal Status**
```bash
curl -H "Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0" \
     http://SEU-IP:8000/api/appliances/portal/status/
```

### 3. **Testar Download**
```bash
curl -H "Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0" \
     http://SEU-IP:8000/api/appliances/portal/download/?type=with_video \
     --output portal_test.zip
```

### 4. **Testar no Postman**
- **URL**: `http://SEU-IP:8000/api/appliances/info/`
- **Header**: `Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0`
- **⚠️ Use HTTP, não HTTPS!**

---

## 🔍 TROUBLESHOOTING

### Se não funcionar:

1. **Verificar logs:**
```bash
sudo journalctl -u poppfire-django -f
sudo tail -f /var/log/nginx/error.log
```

2. **Verificar se o processo está rodando:**
```bash
ps aux | grep python
netstat -tlnp | grep :8000
```

3. **Verificar firewall:**
```bash
sudo ufw status
sudo ufw allow 8000
```

4. **Testar diretamente:**
```bash
cd /var/www/sreadmin
sudo -u www-data python manage.py runserver 0.0.0.0:8000
```

---

## 📋 URLS FINAIS

**Substitua `SEU-IP` pelo IP real do servidor Ubuntu:**

- **Admin**: `http://SEU-IP:8000/admin/`
- **API Info**: `http://SEU-IP:8000/api/appliances/info/`
- **Portal Status**: `http://SEU-IP:8000/api/appliances/portal/status/`
- **Download**: `http://SEU-IP:8000/api/appliances/portal/download/?type=with_video`

## 🔑 TOKENS CONFIGURADOS

- **Teste**: `c8c786467d4a8d2825eaf549534d1ab0`
- **Produção**: `f8e7d6c5b4a3928170695e4c3d2b1a0f`

## ✅ CHECKLIST FINAL

- [ ] Backup realizado
- [ ] Código atualizado
- [ ] Migrações aplicadas
- [ ] Tokens criados
- [ ] Permissões configuradas
- [ ] Serviço systemd funcionando
- [ ] Nginx configurado (opcional)
- [ ] API testada e funcionando
- [ ] Postman testado com HTTP (não HTTPS)

---

## 🎯 RESUMO EXECUTIVO

1. **Conecte no servidor Ubuntu**
2. **Execute**: `sudo ./production_deploy.sh`
3. **Teste**: `curl -H "Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0" http://SEU-IP:8000/api/appliances/info/`
4. **Use HTTP no Postman**: `http://SEU-IP:8000/api/appliances/info/`
