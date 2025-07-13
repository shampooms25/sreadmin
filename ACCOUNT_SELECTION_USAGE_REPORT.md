# Seleção de Conta no Relatório de Uso - Starlink Admin

## Funcionalidade Implementada

Foi adicionada uma **caixa de seleção de conta (ACC)** no relatório de uso da Starlink que permite:

1. **Seleção de conta diretamente na página** - o usuário pode trocar de conta sem precisar alterar a URL
2. **Cálculo automático do ciclo atual** - sempre exibe o período do último dia 03 até hoje
3. **Seleção automática** - quando a página é aberta com um `account_id` na URL, a conta é automaticamente selecionada
4. **Interface responsiva** - funciona bem em desktop e dispositivos móveis

## Como Usar

### 1. Acesso Geral
- **URL**: `http://localhost:8000/admin/starlink/usage-report/`
- **Função**: Mostra todas as contas disponíveis na caixa de seleção

### 2. Acesso com Conta Específica
- **URL**: `http://localhost:8000/admin/starlink/usage-report/?account_id=ACC-2744134-64041-5`
- **Função**: Abre a página já com a conta selecionada

### 3. Trocar de Conta
- Use a caixa de seleção no topo da página
- Ao selecionar uma conta, o relatório é atualizado automaticamente
- A opção "Todas as Contas" remove a seleção específica

## Contas Disponíveis

O sistema possui 5 contas configuradas:

1. **Conta Primária** (ACC-3697602-31930-14) - 53 service lines
2. **Conta Secundária** (ACC-3697620-11506-11) - 15 service lines  
3. **Conta Principal** (ACC-2744134-64041-5) - 70 service lines
4. **Conta Norte** (ACC-3697622-49133-20) - 1 service line
5. **Conta Sul** (ACC-3697611-48655-26) - 3 service lines

## Ciclo de Faturamento

O sistema calcula automaticamente o **ciclo atual** seguindo a regra:
- **Início**: Último dia 03 do mês
- **Fim**: Data atual (hoje)

### Exemplos de Cálculo:
- Se hoje é 07/07/2025 → Ciclo: 03/07/2025 até 07/07/2025 (5 dias)
- Se hoje é 01/07/2025 → Ciclo: 03/06/2025 até 01/07/2025 (29 dias)

## Implementação Técnica

### Arquivos Modificados:

1. **`painel/templates/admin/painel/starlink/usage_report.html`**
   - Adicionado formulário de seleção de conta
   - Adicionado CSS responsivo
   - Adicionadas informações da conta selecionada no cabeçalho

2. **`painel/views.py`**
   - Função `starlink_usage_report` já estava preparada
   - Função `get_account_context` fornece contexto das contas
   - Função `get_selected_account` processa a seleção

3. **`painel/starlink_api.py`**
   - Função `get_usage_report_data` gera dados simulados
   - Função `get_available_accounts` lista contas disponíveis

### Features Implementadas:

- ✅ **Caixa de seleção de conta** com submissão automática
- ✅ **Seleção via URL** (`?account_id=ACC-XXXX`)
- ✅ **Ciclo atual automático** (do último dia 03 até hoje)
- ✅ **Interface responsiva** com CSS moderno
- ✅ **Dados simulados** para todas as contas
- ✅ **Estatísticas completas** por threshold de consumo
- ✅ **Informações da conta** no cabeçalho
- ✅ **Compatibilidade com impressão** (oculta elementos de interface)

## Testes

### Testes Automatizados:
- `test_account_selection_simple.py` - Testa funcionalidade core
- `test_usage_report_final.py` - Teste completo da funcionalidade

### Testes Manuais:
1. Acesse `http://localhost:8000/admin/starlink/usage-report/`
2. Teste a caixa de seleção de conta
3. Verifique se o ciclo atual é calculado corretamente
4. Teste com URLs específicas de conta

## Logs de Teste

```
=== TESTE FINAL: Relatório de Uso com Seleção de Conta ===
✓ Total de contas: 5
✓ Conta encontrada: Conta Principal
✓ Dados obtidos com sucesso
✓ Total de service lines: 70
✓ Ciclo atual: 03/07/2025 até 07/07/2025
✓ Dias no ciclo: 5
✓ Todas as contas testadas com sucesso
```

## Próximos Passos (Opcionais)

1. **Seleção de outros ciclos** - Permitir escolher ciclos anteriores
2. **Filtros adicionais** - Por status, localização, etc.
3. **Exportação** - CSV, PDF, etc.
4. **Gráficos** - Visualizações adicionais
5. **Alertas** - Notificações por email/SMS

---

**Status**: ✅ **IMPLEMENTADO E FUNCIONANDO**
**Data**: 07/07/2025
**Versão**: 1.0
