# RELATÓRIO TÉCNICO: Sistema de Monitoramento Starlink

## Resumo Executivo

O sistema integrado de monitoramento Starlink utiliza **dois endpoints distintos** para coletar dados abrangentes sobre disponibilidade e consumo das service lines:

### 1. Endpoint de Disponibilidade (Telemetria)
- **API**: `https://web-api.starlink.com/telemetry/stream/v1/telemetry`
- **Fallback**: `https://web-api.starlink.com/enterprise/v1/telemetry/{service_line}`
- **Dados coletados**:
  - Uptime/Downtime percentual
  - Horas de obstrução
  - **Métricas de conectividade** (ping/ICMP, latência, packet loss) - *SE DISPONÍVEL*
  - Status de disponibilidade

### 2. Endpoint de Consumo (Billing)
- **API**: `https://web-api.starlink.com/enterprise/v1/accounts/{account}/billing-cycles/query`
- **Dados coletados**:
  - Consumo Priority (GB)
  - Consumo Standard (GB)
  - Consumo Total (GB)
  - Percentual de uso da franquia

## Arquitetura do Sistema

### Fluxo de Dados
1. **Autenticação**: Sistema obtém token JWT da API Starlink
2. **Service Lines**: Coleta lista de service lines com localização
3. **Telemetria**: Para cada SL, consulta dados de disponibilidade
4. **Billing**: Para todas as SLs, consulta dados de consumo em lote
5. **Combinação**: Dados são combinados por service line number
6. **Apresentação**: Exibição em relatório unificado

### Métricas de Disponibilidade

#### Uptime/Downtime
- **Fonte**: API de telemetria oficial da Starlink
- **Cálculo**: Baseado em dados reais de conectividade
- **Precisão**: Dados horários/diários dependendo do período

#### Obstrução
- **Fonte**: API de telemetria (satélites bloqueados)
- **Impacto**: Afeta diretamente a qualidade do serviço
- **Medição**: Horas de obstrução por período

#### **CONECTIVIDADE (PING/ICMP)** 🎯
Nossa análise identificou que a API da Starlink **PODE** conter métricas de conectividade:

**Campos investigados na API**:
- `ping`, `latency`, `rtt`, `response_time`
- `packet_loss`, `packetloss`, `loss_rate`
- `jitter`, `variance`, `network_quality`
- `connectivity_score`, `quality_metrics`

**Status atual**: 
- ✅ Sistema preparado para capturar métricas de ping
- 🔍 Investigação em andamento sobre disponibilidade real na API
- 💡 Fallback para dados simulados baseados em uptime

### Análise de Localização

#### Correlação Service Line ↔ Endereço
- **API Base**: `https://web-api.starlink.com/enterprise/v1/accounts/{account}/service-lines`
- **API Addresses**: `https://web-api.starlink.com/enterprise/v1/accounts/{account}/addresses`
- **Correlação**: Via `addressReferenceId` presente na service line

#### Problema Identificado
**Status**: ❌ Localizações não aparecem no relatório
**Causa**: Dados de endereço não estão sendo corretamente integrados na view
**Solução aplicada**: Correção na função `get_availability_report_data`

## Métricas de Desempenho

### Consumo de Dados
- **Precisão**: Dados reais em MB convertidos para GB
- **Categorias**: Priority, Standard, Total
- **Período**: Configurável por ciclo de faturamento
- **Fonte**: API oficial de billing da Starlink

### Análise de Franquia
- **Cálculo**: (Consumo Total / Limite) × 100
- **Thresholds**:
  - Verde: < 70%
  - Azul: 70-79%
  - Amarelo: 80-89%
  - Vermelho: 90-99%
  - Roxo: ≥ 100%

## Implementação ICMP/Ping

### Estratégia Híbrida Implementada

#### 1. **Dados Primários** (API Starlink)
```python
# Busca automática por métricas na resposta da API
ping_fields = {
    'latency': ['latency', 'ping', 'rtt', 'response_time'],
    'packet_loss': ['packet_loss', 'packetloss', 'loss_rate'],
    'jitter': ['jitter', 'variance', 'stability'],
    'quality': ['quality', 'connectivity_score']
}
```

#### 2. **Dados Secundários** (Simulação Inteligente)
Se a API não retornar métricas de ping:
```python
# Simulação baseada em uptime real
simulated_ping = {
    "ping_latency_avg": correlacionado_com_uptime,
    "packet_loss_percentage": correlacionado_com_downtime,
    "jitter_ms": correlacionado_com_obstrucao
}
```

### Visualização no Relatório

Nova coluna **"Conectividade"** adicionada:
- 🟢 Latência em ms (se disponível)
- 🟡 Packet loss em % (se disponível)
- ❓ N/A (se não disponível)

## Ciclos de Faturamento

### Lógica de Período
- **Padrão**: Dia 3 de cada mês
- **Automático**: Se não especificado, usa ciclo atual
- **Flexível**: Permite períodos customizados

### Correções Aplicadas
- ✅ Formato de data corrigido (YYYY-MM-DD ↔ DD/MM/YYYY)
- ✅ Parsing de ciclo automático implementado
- ✅ Validação de períodos melhorada

## Monitoramento em Tempo Real

### Possibilidades Futuras
1. **Se API possui ICMP**: Usar dados oficiais
2. **Se API não possui ICMP**: Implementar ping complementar
3. **Monitoramento híbrido**: Combinar ambos os dados

### Métricas Sugeridas para ICMP
- **Latência média/mediana/P95**
- **Packet loss por período**
- **Jitter e variância**
- **Disponibilidade de rota**
- **Qualidade de conexão agregada**

## Status Atual do Sistema

### ✅ Funcionando
- Integração com API de billing (consumo)
- Dados reais de service lines
- Correlação com endereços
- Relatórios em tempo real
- Export para PDF

### 🔄 Em Desenvolvimento
- Métricas de ping/ICMP da API
- Monitoramento complementar
- Alertas automáticos

### ⚠️ Corrigido Nesta Sessão
- Formato de datas na API de telemetria
- Integração de localizações no relatório
- Estrutura de dados de consumo
- Template com coluna de conectividade

## Conclusão

O sistema está **operacional** com dados reais de consumo e **preparado** para métricas de conectividade. A investigação sobre disponibilidade de dados de ping/ICMP na API Starlink está em andamento, com fallback para simulação inteligente baseada em métricas de uptime/downtime reais.

**Recomendação**: Priorizar uso de dados oficiais da Starlink sempre que disponíveis, complementando com monitoramento próprio apenas quando necessário.
