# Implementação Completa - API para Appliances POPPFIRE

## ✅ Status da Implementação

**🎉 IMPLEMENTAÇÃO 100% CONCLUÍDA!**

### 🔄 Mudanças Realizadas

#### 1. Substituição de Terminologia
- ✅ Todas as menções a "OPNSENSE" → "APPLIANCE POPPFIRE"
- ✅ Todas as menções a "OpenSense" → "Appliance POPPFIRE"
- ✅ Documentação atualizada
- ✅ Comentários no código atualizados

#### 2. API Completa Implementada
- ✅ Sistema de autenticação com Bearer Token
- ✅ Endpoint de informações da API
- ✅ Endpoint de status do portal
- ✅ Endpoint de download do portal
- ✅ Endpoint de report de status
- ✅ Validações e tratamento de erros
- ✅ Logs detalhados

#### 3. Lógica de Negócio
- ✅ **Portal Ativo**: Retorna portal com vídeo (src.zip)
- ✅ **Portal Inativo**: Retorna portal sem vídeo (scripts_poppnet_sre.zip)
- ✅ Cálculo de hash SHA256 para verificação de mudanças
- ✅ Detecção automática do tipo de portal
- ✅ Substituição automática de vídeo no ZIP

## 🌐 Endpoints da API

**Base URL**: `http://172.18.25.253:8000/api/`

### 1. Informações da API
```
GET /api/appliances/info/
Authorization: Bearer <token>
```

### 2. Status do Portal
```
GET /api/appliances/portal/status/
Authorization: Bearer <token>
```

### 3. Download do Portal
```
GET /api/appliances/portal/download/?type=auto
Authorization: Bearer <token>
```

### 4. Report de Status
```
POST /api/appliances/portal/update-status/
Authorization: Bearer <token>
Content-Type: application/json
```

## 🔑 Tokens de Autenticação

### Token de Desenvolvimento
```
Token: 1234567890abcdef1234567890abcdef
Usuário: appliance-001
```

### Token Gerado
```
Token: eda8f1807d260fe4a8214ed496e23b72
Usuário: appliance-appliance-001
```

### Gerar Novos Tokens
```bash
python generate_appliance_token.py <nome-do-appliance>
```

## 🧪 Teste no Postman

### Collection Completa

#### 1. Test API Info
```http
GET http://172.18.25.253:8000/api/appliances/info/
Headers:
  Authorization: Bearer eda8f1807d260fe4a8214ed496e23b72
```

**Response Esperado**:
```json
{
    "api_name": "POPPFIRE Appliance API",
    "version": "1.0",
    "description": "API para integração com Appliances POPPFIRE",
    "endpoints": {...},
    "server_time": "2025-08-06T...",
    "server_ip": "172.18.25.253"
}
```

#### 2. Test Portal Status
```http
GET http://172.18.25.253:8000/api/appliances/portal/status/
Headers:
  Authorization: Bearer eda8f1807d260fe4a8214ed496e23b72
```

**Response Esperado (Portal Ativo)**:
```json
{
    "status": "active",
    "portal_type": "with_video",
    "portal_hash": "abc123...",
    "last_updated": "2025-08-06T...",
    "download_url": "/api/appliances/portal/download/?type=with_video",
    "video_name": "Eld02.mp4",
    "video_url": "http://172.18.25.253:8000/media/videos/eld/Eld02.mp4",
    "using_custom_video": true
}
```

#### 3. Test Portal Download
```http
GET http://172.18.25.253:8000/api/appliances/portal/download/?type=auto
Headers:
  Authorization: Bearer eda8f1807d260fe4a8214ed496e23b72
```

**Response**: Arquivo ZIP binário (src.zip ou scripts_poppnet_sre.zip)

#### 4. Test Update Status
```http
POST http://172.18.25.253:8000/api/appliances/portal/update-status/
Headers:
  Authorization: Bearer eda8f1807d260fe4a8214ed496e23b72
  Content-Type: application/json

Body:
{
    "appliance_id": "test-appliance-001",
    "appliance_ip": "192.168.1.100",
    "update_status": "success",
    "portal_hash": "abc123def456",
    "portal_type": "with_video",
    "update_timestamp": "2025-08-06T12:00:00Z"
}
```

## 🔄 Fluxo de Funcionamento

### 1. Verificação de Status
O appliance consulta o endpoint `/status/` para verificar:
- Se há portal ativo
- Qual tipo de portal (com ou sem vídeo)
- Hash do portal atual
- Informações do vídeo (se aplicável)

### 2. Tomada de Decisão
```python
# Pseudocódigo do appliance
current_hash = get_local_portal_hash()
server_status = api.get_portal_status()

if current_hash != server_status['portal_hash']:
    # Baixar novo portal
    portal_zip = api.download_portal()
    install_portal(portal_zip)
    reload_portal_service()
    
    # Reportar sucesso
    api.report_status("success", server_status['portal_hash'])
```

### 3. Download e Instalação
- Download do ZIP apropriado
- Extração no diretório do portal
- Recarregamento do serviço
- Report de status de volta para o servidor

### 4. Tipos de Portal

#### Portal Ativo (com vídeo)
- **Arquivo**: `src.zip`
- **Conteúdo**: Portal completo com vídeo substituído
- **Estrutura**: `src/assets/videos/video.mp4`

#### Portal Inativo (sem vídeo)
- **Arquivo**: `scripts_poppnet_sre.zip`
- **Conteúdo**: Portal básico sem vídeo
- **Estrutura**: Portal estático

## 📁 Arquivos Criados/Modificados

### Novos Arquivos
```
captive_portal/api_views.py          - API completa
generate_appliance_token.py         - Gerador de tokens
test_appliance_api.py               - Testes da API
API_APPLIANCES_POPPFIRE_DOCUMENTACAO.md - Documentação
```

### Arquivos Modificados
```
painel/admin.py                     - Substituição de terminologia
painel/models.py                    - Substituição de terminologia
captive_portal/urls.py              - URLs da API
sreadmin/urls.py                    - Roteamento principal
```

## 🚀 Próximos Passos

### 1. Teste Inicial
```bash
# Executar testes locais
python test_appliance_api.py

# Gerar token de produção
python generate_appliance_token.py appliance-producao-001
```

### 2. Configuração no Appliance
- Implementar cliente HTTP
- Configurar token de autenticação
- Implementar lógica de verificação periódica
- Implementar lógica de download e instalação

### 3. Monitoramento
- Implementar logs de API
- Dashboard de status dos appliances
- Alertas de falhas de sincronização

### 4. Melhorias Futuras
- Rate limiting
- Tokens com expiração
- Compressão de resposta
- Cache de portais
- Webhook notifications

## ✅ Validação Final

### Testes Realizados
- ✅ Autenticação funcionando
- ✅ URLs configuradas corretamente
- ✅ Modelos de dados acessíveis
- ✅ Cálculo de hash funcional
- ✅ Portal ativo detectado
- ✅ Endpoints acessíveis

### Cenários Testados
- ✅ Token válido aceito
- ✅ Token inválido rejeitado
- ✅ Portal com vídeo ativo
- ✅ Portal sem vídeo disponível
- ✅ Cálculo de hash de arquivos

## 🎯 Informações para Teste

**Server IP**: `172.18.25.253:8000`  
**Token de Teste**: `eda8f1807d260fe4a8214ed496e23b72`  
**Token de Dev**: `1234567890abcdef1234567890abcdef`

**Status**: ✅ **COMPLETO E FUNCIONAL**  
**Data**: 06/08/2025  
**Versão**: 1.0
