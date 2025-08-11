# Diferenças Críticas: Windows vs Linux - POPPFIRE API

## 🚨 PROBLEMA PRINCIPAL

Você está desenvolvendo no **Windows** mas o ambiente de **produção é Linux**. Existem várias diferenças que podem causar o erro 401:

## 🔧 DIFERENÇAS PRINCIPAIS

### 1. **Caminhos de Arquivo**
- **Windows**: `C:\Projetos\Poppnet\sreadmin`
- **Linux**: `/var/www/sreadmin`

### 2. **Permissões de Arquivo**
- **Windows**: Não há conceito Unix de permissões
- **Linux**: Precisa `www-data:www-data` e `chmod 755`

### 3. **Servidor Web**
- **Windows**: Desenvolvimento com `python manage.py runserver`
- **Linux**: Produção com nginx/apache + gunicorn/uwsgi

### 4. **Banco de Dados**
- **Windows**: SQLite ou PostgreSQL local
- **Linux**: PostgreSQL em produção com configurações diferentes

### 5. **Arquivo `appliance_tokens.json`**
- **Windows**: Pode não existir, usa apenas banco
- **Linux**: Se existir, precisa permissões corretas

## 🛠️ SOLUÇÕES PARA CADA AMBIENTE

### Para Windows (Desenvolvimento)

```bash
# 1. Criar token no banco
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()
from captive_portal.models import ApplianceToken
obj, created = ApplianceToken.objects.get_or_create(
    token='c8c786467d4a8d2825eaf549534d1ab0',
    defaults={
        'appliance_id': 'POSTMAN-TEST',
        'appliance_name': 'Appliance Teste Postman',
        'description': 'Token para testes via Postman',
        'is_active': True,
    }
)
print(f'Token: {obj.token}')
print(f'Ativo: {obj.is_active}')
"

# 2. Iniciar servidor
python manage.py runserver 127.0.0.1:8000

# 3. Testar no Postman
# URL: http://127.0.0.1:8000/api/appliances/info/
# Header: Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0
```

### Para Linux (Produção)

```bash
# 1. Usar o script de deploy
./production_deploy.sh

# 2. Ou executar manualmente:
python linux_production_setup.py
./setup_linux_production.sh

# 3. Verificar permissões
sudo chown -R www-data:www-data /var/www/sreadmin/
sudo chmod -R 755 /var/www/sreadmin/

# 4. Iniciar serviços
sudo systemctl start poppfire-django
sudo systemctl start nginx
```

## 🧪 TESTE ESPECÍFICO PARA SEU CASO

### No Windows (onde você está agora):

1. **Execute este comando para criar o token:**
```python
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()
from captive_portal.models import ApplianceToken

# Criar token específico do Postman
token = 'c8c786467d4a8d2825eaf549534d1ab0'
obj, created = ApplianceToken.objects.get_or_create(
    token=token,
    defaults={
        'appliance_id': 'POSTMAN-TEST',
        'appliance_name': 'Appliance Teste Postman',
        'description': 'Token para testes via Postman - Windows',
        'is_active': True,
    }
)

print('=' * 50)
print(f'Token: {token}')
print(f'Nome: {obj.appliance_name}')
print(f'Ativo: {obj.is_active}')
print(f'Criado agora: {created}')

# Testar autenticação
from captive_portal.api_views import ApplianceAPIAuthentication
from unittest.mock import Mock

mock_request = Mock()
mock_request.META = {
    'HTTP_AUTHORIZATION': f'Bearer {token}',
    'REMOTE_ADDR': '127.0.0.1'
}

is_valid, result = ApplianceAPIAuthentication.verify_token(mock_request)
print(f'Autenticação: {\"✅ OK\" if is_valid else \"❌ ERRO\"} - {result.appliance_name if is_valid else result}')
print('=' * 50)
"
```

2. **Inicie o servidor Django:**
```bash
python manage.py runserver 127.0.0.1:8000
```

3. **Teste no Postman:**
- **URL**: `http://127.0.0.1:8000/api/appliances/info/`
- **Method**: `GET`
- **Header**: `Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0`

### No Linux (produção):

1. **Execute o script de produção que criamos:**
```bash
# Transferir arquivos para o servidor
scp production_deploy.sh user@servidor:/var/www/sreadmin/
scp linux_production_setup.py user@servidor:/var/www/sreadmin/

# No servidor Linux
cd /var/www/sreadmin
chmod +x production_deploy.sh
./production_deploy.sh
```

## 🔍 DIAGNÓSTICO DO ERRO 401

O erro "Token não fornecido ou formato inválido" geralmente significa:

1. **Header mal formatado** - deve ser exatamente: `Authorization: Bearer TOKEN`
2. **Token não existe no banco** - verificar com query SQL
3. **Token inativo** - verificar campo `is_active`
4. **Servidor não está rodando** - verificar porta 8000
5. **URL incorreta** - verificar endpoint `/api/appliances/info/`

## 🎯 AÇÃO IMEDIATA

Execute este comando no Windows para resolver agora:

```bash
# Criar token e testar
python quick_test_windows.py

# Iniciar servidor
python manage.py runserver 127.0.0.1:8000
```

Depois teste no Postman com:
- URL: `http://127.0.0.1:8000/api/appliances/info/`
- Header: `Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0`

## 📞 PRÓXIMOS PASSOS

1. ✅ Resolver no Windows primeiro
2. 🐧 Depois aplicar no Linux com os scripts criados
3. 🔧 Configurar nginx/systemd para produção
4. 🧪 Testar OpnSense integration
