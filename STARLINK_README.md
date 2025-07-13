# Sistema de Integração Starlink API

Este documento descreve o sistema de integração com a API da Starlink implementado no painel administrativo do Django.

## Estrutura do Sistema

### Arquivos Principais

1. **`painel/starlink_api.py`** - Módulo principal para integração com a API
2. **`painel/views.py`** - Views para as páginas da Starlink
3. **`painel/urls.py`** - Roteamento das URLs
4. **Templates** - Interface visual em `painel/templates/admin/painel/starlink/`

### Funcionalidades Implementadas

#### 1. Dashboard Principal
- **URL**: `/admin/starlink/`
- **Funcionalidade**: Página principal com botões de acesso rápido
- **Botões disponíveis**:
  - Service Lines
  - Relatório de Faturamento
  - Relatório Detalhado
  - Status da API

#### 2. Service Lines
- **URL**: `/admin/starlink/service-lines/`
- **Funcionalidade**: Lista todos os Service Line Numbers da conta
- **Recursos**:
  - Exibição em tabela com informações detalhadas
  - Contador de ciclos de faturamento
  - Status de cada service line
  - Função de atualização

#### 3. Relatório de Faturamento
- **URL**: `/admin/starlink/billing-report/`
- **Funcionalidade**: Gera relatório financeiro resumido
- **Recursos**:
  - Resumo geral da conta
  - Total de cobranças
  - Informações de ciclos de faturamento
  - Lista dos primeiros 10 Service Lines

#### 4. Relatório Detalhado
- **URL**: `/admin/starlink/detailed-report/`
- **Funcionalidade**: Relatório completo para impressão
- **Recursos**:
  - Lista completa de todos os Service Lines
  - Layout otimizado para impressão
  - Seção específica formatada para relatórios
  - Função de impressão integrada

#### 5. Status da API
- **URL**: `/admin/starlink/api-status/`
- **Funcionalidade**: Verifica conectividade com a API
- **Recursos**:
  - Teste de autenticação
  - Verificação de funcionamento
  - Status visual (sucesso/erro)
  - Detalhes do token de acesso

### Menu Lateral Customizado

O sistema inclui um menu lateral flutuante acessível em todas as páginas do admin:

- **Botão de acesso**: Ícone de satélite no canto superior direito
- **Conteúdo**: Links diretos para todas as funcionalidades Starlink
- **Responsivo**: Adaptado para desktop e mobile

## Configuração da API

### Credenciais
```python
CLIENT_ID = "498ca080-3eb2-4a4d-a5d9-3828dbef0194"
CLIENT_SECRET = "fibernetworks_api@2025"
```

### Endpoints
- **Autenticação**: `https://api.starlink.com/auth/connect/token`
- **Consulta**: `https://web-api.starlink.com/enterprise/v1/accounts/ACC-2744134-64041-5/billing-cycles/query`

### Parâmetros de Consulta
- **Ciclos de faturamento**: 12 (últimos 12 meses)
- **Página**: 0 (primeira página)
- **Limite**: 100 (máximo de results por página)

## Funções Principais da API

### 1. Autenticação
```python
def get_token(client_id, client_secret)
def get_valid_token()
```

### 2. Consulta de Dados
```python
def query_service_lines()
def get_detailed_service_lines()
def get_billing_summary()
```

### 3. Teste de Conectividade
```python
def test_api_connection()
```

## Como Usar

### 1. Acesso via Menu Principal
1. Faça login no admin Django
2. Clique no ícone de satélite no menu lateral
3. Escolha a funcionalidade desejada

### 2. Acesso Direto via URL
- Dashboard: `/admin/starlink/`
- Service Lines: `/admin/starlink/service-lines/`
- Relatórios: `/admin/starlink/billing-report/` ou `/admin/starlink/detailed-report/`
- Status: `/admin/starlink/api-status/`

### 3. Relatório para Impressão
1. Acesse o "Relatório Detalhado"
2. Clique em "Imprimir Relatório"
3. Use a função de impressão do navegador

## Tratamento de Erros

O sistema inclui tratamento robusto de erros:

- **Falha de autenticação**: Mensagem clara sobre problemas de token
- **Erro de rede**: Informações sobre conectividade
- **Dados indisponíveis**: Mensagens informativas para o usuário
- **Timeout**: Tratamento de requisições que demoram muito

## Dependências

```
Django>=5.2.3
requests
psycopg2-binary
django-adminlte4
```

## Instalação

1. Instalar dependências:
```bash
pip install -r requirements.txt
```

2. Aplicar migrações:
```bash
python manage.py migrate
```

3. Executar servidor:
```bash
python manage.py runserver
```

## Personalização

### Alterando Credenciais
Edite as constantes no arquivo `starlink_api.py`:
```python
CLIENT_ID = "seu_client_id"
CLIENT_SECRET = "seu_client_secret"
```

### Modificando Parâmetros de Consulta
Ajuste os valores no payload das funções de consulta:
```python
payload = {
    "serviceLinesFilter": [],
    "previousBillingCycles": 12,  # Altere aqui
    "pageIndex": 0,
    "pageLimit": 100  # Altere aqui
}
```

### Customizando Interface
- Templates estão em `painel/templates/admin/painel/starlink/`
- CSS customizado incluso em cada template
- Menu lateral editável em `base_site.html`

## Logs e Debug

Para habilitar logs detalhados:
1. Adicione prints nas funções da API conforme necessário
2. Use o Django Debug Toolbar para monitorar requisições
3. Verifique os logs do servidor para erros de conectividade

## Suporte

Este sistema foi desenvolvido baseado no modelo de código fornecido e implementa as funcionalidades solicitadas para integração com a API Starlink Enterprise.

Para questões específicas ou personalização adicional, consulte:
- Documentação da API Starlink
- Documentação do Django
- Código fonte nos arquivos mencionados
