# API para Appliances POPPFIRE - Documentação Completa

## 📋 Visão Geral

A API permite que Appliances POPPFIRE se conectem ao servidor central (172.18.25.253) para verificar e baixar atualizações do portal captive automaticamente.

## 🔐 Autenticação

**Tipo**: Bearer Token  
**Header**: `Authorization: Bearer <token>`

### Gerar Token

```bash
# Gerar token para um appliance
python generate_appliance_token.py appliance-001
```

### Tokens de Desenvolvimento
```
Token de teste: 1234567890abcdef1234567890abcdef
Usuário: appliance-001
```

## 🌐 Endpoints da API

**Base URL**: `http://172.18.25.253:8000/api/`

### 1. Informações da API

```http
GET /api/appliances/info/
Authorization: Bearer <token>
```

**Response**:
```json
{
    "api_name": "POPPFIRE Appliance API",
    "version": "1.0",
    "description": "API para integração com Appliances POPPFIRE",
    "endpoints": {
        "portal_status": "/api/appliances/portal/status/",
        "portal_download": "/api/appliances/portal/download/",
        "update_status": "/api/appliances/portal/update-status/",
        "api_info": "/api/appliances/info/"
    },
    "authentication": "Bearer Token",
    "server_time": "2025-08-06T10:30:00Z",
    "server_ip": "172.18.25.253"
}
```

### 2. Status do Portal

```http
GET /api/appliances/portal/status/
Authorization: Bearer <token>
```

**Response (Portal com Vídeo Ativo)**:
```json
{
    "status": "active",
    "portal_type": "with_video",
    "portal_hash": "abc123def456...",
    "last_updated": "2025-08-06T10:30:00Z",
    "download_url": "/api/appliances/portal/download/?type=with_video",
    "video_name": "video_institucional.mp4",
    "video_url": "http://172.18.25.253:8000/media/videos/video_institucional.mp4",
    "video_size_mb": 15.8,
    "using_custom_video": true,
    "timestamp": "2025-08-06T10:35:00Z"
}
```

**Response (Portal sem Vídeo)**:
```json
{
    "status": "active",
    "portal_type": "without_video",
    "portal_hash": "def456abc789...",
    "portal_name": "Portal Corporativo",
    "portal_version": "1.0",
    "last_updated": "2025-08-06T09:15:00Z",
    "download_url": "/api/appliances/portal/download/?type=without_video",
    "file_size_mb": 5.2,
    "timestamp": "2025-08-06T10:35:00Z"
}
```

### 3. Download do Portal

```http
GET /api/appliances/portal/download/?type=<tipo>
Authorization: Bearer <token>
```

**Parâmetros**:
- `type`: `with_video`, `without_video` ou `auto` (padrão)

**Response**: Arquivo ZIP binário

**Headers de Resposta**:
```
Content-Type: application/zip
Content-Disposition: attachment; filename="src.zip"
Content-Length: 1048576
X-Portal-Type: with_video
X-Portal-Hash: abc123def456...
X-Download-Timestamp: 2025-08-06T10:30:00Z
```

### 4. Report de Status de Atualização

```http
POST /api/appliances/portal/update-status/
Authorization: Bearer <token>
Content-Type: application/json
```

**Body**:
```json
{
    "appliance_id": "appliance-001",
    "appliance_ip": "192.168.1.100",
    "update_status": "success",
    "portal_hash": "abc123def456...",
    "portal_type": "with_video",
    "update_timestamp": "2025-08-06T10:30:00Z"
}
```

**Response**:
```json
{
    "status": "success",
    "message": "Status de atualização recebido com sucesso",
    "received_data": {
        "appliance_id": "appliance-001",
        "status": "success",
        "portal_type": "with_video"
    },
    "timestamp": "2025-08-06T10:35:00Z"
}
```

## 🔄 Fluxo de Atualização

### 1. Verificação Periódica
```bash
# O appliance deve verificar o status a cada X minutos
curl -H "Authorization: Bearer <token>" \
     http://172.18.25.253:8000/api/appliances/portal/status/
```

### 2. Comparação de Hash
```bash
# Comparar portal_hash com hash local
# Se diferente, fazer download
```

### 3. Download do Portal
```bash
curl -H "Authorization: Bearer <token>" \
     -O http://172.18.25.253:8000/api/appliances/portal/download/?type=auto
```

### 4. Report de Status
```bash
curl -X POST \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"appliance_id":"appliance-001","update_status":"success",...}' \
     http://172.18.25.253:8000/api/appliances/portal/update-status/
```

## 🧪 Testes no Postman

### Collection de Testes

**1. Test API Info**
```
GET http://172.18.25.253:8000/api/appliances/info/
Headers:
  Authorization: Bearer 1234567890abcdef1234567890abcdef
```

**2. Test Portal Status**
```
GET http://172.18.25.253:8000/api/appliances/portal/status/
Headers:
  Authorization: Bearer 1234567890abcdef1234567890abcdef
```

**3. Test Portal Download**
```
GET http://172.18.25.253:8000/api/appliances/portal/download/?type=auto
Headers:
  Authorization: Bearer 1234567890abcdef1234567890abcdef
```

**4. Test Update Status**
```
POST http://172.18.25.253:8000/api/appliances/portal/update-status/
Headers:
  Authorization: Bearer 1234567890abcdef1234567890abcdef
  Content-Type: application/json
Body:
{
    "appliance_id": "test-appliance",
    "appliance_ip": "192.168.1.100",
    "update_status": "success",
    "portal_hash": "test123",
    "portal_type": "with_video",
    "update_timestamp": "2025-08-06T10:30:00Z"
}
```

## ⚠️ Códigos de Erro

### 401 - Não Autorizado
```json
{
    "error": "Não autorizado",
    "message": "Token não fornecido ou formato inválido",
    "timestamp": "2025-08-06T10:30:00Z"
}
```

### 404 - Portal Não Encontrado
```json
{
    "error": "Nenhum portal disponível",
    "message": "Não há portal com vídeo ativo nem portal sem vídeo disponível",
    "timestamp": "2025-08-06T10:30:00Z"
}
```

### 400 - Parâmetro Inválido
```json
{
    "error": "Tipo de portal inválido",
    "message": "Tipo deve ser \"with_video\", \"without_video\" ou \"auto\"",
    "timestamp": "2025-08-06T10:30:00Z"
}
```

### 500 - Erro do Servidor
```json
{
    "error": "Erro interno do servidor",
    "message": "Detalhes do erro...",
    "timestamp": "2025-08-06T10:30:00Z"
}
```

## 🏗️ Implementação no Appliance

### Script Básico de Atualização

```python
#!/usr/bin/env python3
import requests
import hashlib
import os
import time

class PoppfirePortalUpdater:
    def __init__(self, token, server_url="http://172.18.25.253:8000"):
        self.token = token
        self.server_url = server_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def check_portal_status(self):
        """Verifica status do portal"""
        url = f"{self.server_url}/api/appliances/portal/status/"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def download_portal(self, portal_type="auto"):
        """Baixa o portal ZIP"""
        url = f"{self.server_url}/api/appliances/portal/download/?type={portal_type}"
        response = requests.get(url, headers=self.headers)
        return response.content
    
    def report_status(self, appliance_id, status, portal_hash, portal_type):
        """Reporta status de atualização"""
        url = f"{self.server_url}/api/appliances/portal/update-status/"
        data = {
            "appliance_id": appliance_id,
            "update_status": status,
            "portal_hash": portal_hash,
            "portal_type": portal_type,
            "update_timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()

# Uso
updater = PoppfirePortalUpdater("1234567890abcdef1234567890abcdef")
status = updater.check_portal_status()
print(f"Portal Status: {status}")
```

## 📊 Monitoramento

### Logs da API
- Logs de autenticação
- Logs de download
- Logs de status de appliances
- Métricas de uso

### Dashboard (Futuro)
- Status de todos os appliances
- Histórico de atualizações
- Alertas de falhas
- Estatísticas de uso

## 🔒 Segurança

### Recomendações
1. **Tokens únicos** para cada appliance
2. **Rotação periódica** de tokens
3. **Logs de auditoria** de todas as operações
4. **Rate limiting** para prevenir abuso
5. **HTTPS** em produção

### Implementações Futuras
- Rate limiting
- IP whitelisting
- Tokens com expiração
- Refresh tokens
- Audit logs detalhados

---

**Status**: ✅ Implementado e funcional  
**Versão**: 1.0  
**Data**: 06/08/2025
