# 🚨 PROBLEMA IDENTIFICADO: SSL/HTTPS vs HTTP

## ❌ O QUE ESTÁ ERRADO

Você está usando **HTTPS** no Postman:
```
https://localhost:8000/api/appliances/portal/download/?type=with_video
```

Mas o servidor Django de desenvolvimento roda em **HTTP** (não HTTPS), causando o erro:
```
Error: write EPROTO ... SSL routines ... WRONG_VERSION_NUMBER
```

## ✅ SOLUÇÃO IMEDIATA

### 1. Use HTTP (não HTTPS) no Postman:

**URLs CORRETAS:**
```
http://localhost:8000/api/appliances/info/
http://localhost:8000/api/appliances/portal/status/
http://localhost:8000/api/appliances/portal/download/?type=with_video
http://localhost:8000/api/appliances/portal/download/?type=without_video
http://localhost:8000/admin/
```

### 2. Header de Autenticação:
```
Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0
```

### 3. Iniciar Servidor Django:
```bash
python manage.py runserver 127.0.0.1:8000
```

## 🔧 CONFIGURAÇÃO DO TOKEN

Execute este comando para garantir que o token existe:

```python
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

print(f'✅ Token: {obj.token}')
print(f'✅ Ativo: {obj.is_active}')
print(f'✅ {'Criado' if created else 'Já existia'}')
"
```

## 🧪 TESTE NO POSTMAN

1. **Mude de HTTPS para HTTP**
2. **URL**: `http://localhost:8000/api/appliances/info/`
3. **Method**: `GET`
4. **Header**: `Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0`

## 📁 ARQUIVOS CRIADOS

- `fix_ssl_problem.bat` - Script para Windows corrigir problema
- `test_api_fix.py` - Teste completo da API
- `production_deploy.sh` - Atualizado com seu token
- Este arquivo - Documentação da solução

## 🐧 PARA PRODUÇÃO LINUX

O script `production_deploy.sh` foi atualizado para incluir seu token de teste e resolver as diferenças entre Windows e Linux.

## 💡 RESUMO

**PROBLEMA**: Protocolo HTTPS vs HTTP
**SOLUÇÃO**: Trocar `https://` por `http://` no Postman
**CAUSA**: Django development server não tem SSL por padrão
**STATUS**: Funcionalidade estava correta, apenas problema de protocolo
