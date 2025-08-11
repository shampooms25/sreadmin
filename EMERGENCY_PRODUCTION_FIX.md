# 🚨 CORREÇÃO URGENTE - Produção Ubuntu

## ❌ PROBLEMA: Ainda recebendo 401 em produção

Você está recebendo "Token não fornecido ou formato inválido" mesmo após as correções. Vamos diagnosticar e corrigir:

## 🔧 SOLUÇÃO PASSO A PASSO

### 1. **Conectar no servidor Ubuntu:**
```bash
ssh usuario@SEU-IP-SERVIDOR
cd /var/www/sreadmin
```

### 2. **Executar diagnóstico completo:**
```bash
chmod +x diagnose_production.sh
sudo ./diagnose_production.sh
```

### 3. **OU executar correção emergencial:**
```bash
chmod +x fix_production_emergency.sh
sudo ./fix_production_emergency.sh
```

## 🔍 DIAGNÓSTICO MANUAL

Se os scripts não funcionarem, execute manualmente:

### 1. **Verificar se o token existe:**
```bash
python manage.py shell -c "
from captive_portal.models import ApplianceToken
tokens = ApplianceToken.objects.all()
print(f'Total tokens: {tokens.count()}')
for t in tokens: print(f'{t.token[:20]}... - {t.appliance_name} - Ativo: {t.is_active}')

# Verificar token específico
try:
    token = ApplianceToken.objects.get(token='c8c786467d4a8d2825eaf549534d1ab0')
    print(f'Token encontrado: {token.appliance_name} - Ativo: {token.is_active}')
except:
    print('Token NÃO encontrado!')
"
```

### 2. **Criar token forçadamente:**
```bash
python manage.py shell -c "
from captive_portal.models import ApplianceToken

# Deletar se existir
ApplianceToken.objects.filter(token='c8c786467d4a8d2825eaf549534d1ab0').delete()

# Criar novo
token = ApplianceToken.objects.create(
    token='c8c786467d4a8d2825eaf549534d1ab0',
    appliance_id='POSTMAN-TEST',
    appliance_name='Appliance Teste Postman',
    description='Token para testes - Produção',
    is_active=True
)
print(f'Token criado: {token.token} - Ativo: {token.is_active}')
"
```

### 3. **Verificar se o servidor está rodando:**
```bash
ps aux | grep "manage.py runserver"
netstat -tlnp | grep :8000
```

### 4. **Iniciar servidor se necessário:**
```bash
# Parar qualquer processo existente
pkill -f "manage.py runserver"

# Iniciar servidor
nohup python manage.py runserver 0.0.0.0:8000 > django.log 2>&1 &

# Verificar se iniciou
sleep 3
ps aux | grep "manage.py runserver"
```

### 5. **Testar localmente no servidor:**
```bash
# Sem autenticação (deve dar 401)
curl -w "Status: %{http_code}\n" http://127.0.0.1:8000/api/appliances/info/

# Com autenticação (deve dar 200)
curl -H "Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0" \
     -w "Status: %{http_code}\n" \
     http://127.0.0.1:8000/api/appliances/info/
```

## 🎯 POSSÍVEIS CAUSAS DO PROBLEMA

### 1. **Token não existe no banco**
```bash
# Verificar
python manage.py dbshell -c "SELECT * FROM captive_portal_appliancetoken WHERE token='c8c786467d4a8d2825eaf549534d1ab0';"
```

### 2. **Problema de migrações**
```bash
python manage.py showmigrations captive_portal
python manage.py migrate captive_portal
```

### 3. **Problemas de permissão**
```bash
sudo chown -R www-data:www-data /var/www/sreadmin/
sudo chmod -R 755 /var/www/sreadmin/
```

### 4. **Servidor não está rodando**
```bash
python manage.py runserver 0.0.0.0:8000
```

### 5. **Firewall bloqueando**
```bash
sudo ufw status
sudo ufw allow 8000
```

## 🌐 TESTE NO POSTMAN

Após a correção, teste no Postman:

**URL**: `http://SEU-IP-REAL:8000/api/appliances/info/`
**Method**: `GET`
**Header**: `Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0`

### ⚠️ PONTOS CRÍTICOS:

1. **Use HTTP (não HTTPS)**
2. **Use o IP real do servidor Ubuntu**
3. **Certifique-se que a porta 8000 está liberada**
4. **O token deve estar exatamente como mostrado**

## 📊 VERIFICAÇÃO FINAL

Se ainda não funcionar, execute este comando no servidor:

```bash
# Obter IP do servidor
SERVER_IP=$(hostname -I | awk '{print $1}')
echo "IP do servidor: $SERVER_IP"

# Testar de dentro do servidor
curl -H "Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0" \
     http://$SERVER_IP:8000/api/appliances/info/

# Se funcionar localmente mas não externamente, é problema de firewall/rede
```

## 🚨 COMANDO DE EMERGÊNCIA

Execute este comando único que faz tudo:

```bash
cd /var/www/sreadmin && \
pkill -f "manage.py runserver" ; \
python manage.py shell -c "
from captive_portal.models import ApplianceToken
ApplianceToken.objects.filter(token='c8c786467d4a8d2825eaf549534d1ab0').delete()
token = ApplianceToken.objects.create(token='c8c786467d4a8d2825eaf549534d1ab0', appliance_id='POSTMAN-TEST', appliance_name='Teste Postman', description='Token teste', is_active=True)
print(f'Token: {token.token} - Ativo: {token.is_active}')
" && \
nohup python manage.py runserver 0.0.0.0:8000 > django.log 2>&1 & \
sleep 3 && \
echo "IP: $(hostname -I | awk '{print $1}')" && \
curl -H "Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0" http://127.0.0.1:8000/api/appliances/info/
```

Este comando único:
1. Para o servidor
2. Deleta e recria o token
3. Inicia o servidor
4. Testa a API
5. Mostra o IP para usar no Postman
