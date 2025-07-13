# Funcionalidade de Botões Dinâmicos - Dashboard Starlink

## 🎯 Objetivo
Implementar funcionalidade para desativar/ativar botões do dashboard conforme a seleção de conta, evitando erros e melhorando a experiência do usuário.

## 🔧 Funcionalidades Implementadas

### 1. Estado dos Botões Baseado na Seleção de Conta

#### Cenário 1: Nenhuma Conta Selecionada
- **Comportamento**: Botões desativados
- **Visual**: Cor cinza, cursor "not-allowed", opacidade reduzida
- **Funcionalidade**: Links não funcionam (`onclick="return false;"`)
- **Mensagem**: Aviso informativo sobre a necessidade de selecionar uma conta

#### Cenário 2: Conta Específica Selecionada
- **Comportamento**: Botões ativados
- **Visual**: Cores originais, cursor normal
- **Funcionalidade**: Links funcionam normalmente
- **Parâmetros**: URLs incluem `?account_id=valor`

### 2. Controle JavaScript Dinâmico

#### Função `updateButtonStates()`
```javascript
function updateButtonStates() {
    const select = document.getElementById('account-select');
    const accountId = select.value;
    const buttons = document.querySelectorAll('.card-button');
    
    buttons.forEach(button => {
        if (accountId) {
            // Ativar botões
            button.classList.remove('disabled');
            button.style.pointerEvents = 'auto';
            button.onclick = null;
            
            // Atualizar href
            const baseUrl = button.href.split('?')[0];
            button.href = `${baseUrl}?account_id=${accountId}`;
        } else {
            // Desativar botões
            button.classList.add('disabled');
            button.style.pointerEvents = 'none';
            button.onclick = function() { return false; };
            
            // Remover parâmetros
            const baseUrl = button.href.split('?')[0];
            button.href = baseUrl;
        }
    });
}
```

#### Função `changeAccount()` Aprimorada
```javascript
function changeAccount() {
    const select = document.getElementById('account-select');
    const accountId = select.value;
    
    if (accountId) {
        window.location.href = `?account_id=${accountId}`;
    } else {
        window.location.href = window.location.pathname;
    }
}
```

### 3. Estilos CSS para Botões Desativados

```css
.card-button:disabled,
.card-button.disabled {
    background: #6c757d !important;
    color: #fff !important;
    cursor: not-allowed !important;
    opacity: 0.6;
    transform: none !important;
    pointer-events: none;
}

.card-button.disabled:hover {
    background: #6c757d !important;
    transform: none !important;
}
```

### 4. Mensagem de Aviso

#### HTML da Mensagem
```html
{% if not selected_account %}
<div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin-bottom: 20px;">
    <div style="color: #856404; font-weight: 500;">
        <i class="fas fa-exclamation-triangle"></i> Informação
    </div>
    <div style="color: #856404; font-size: 0.9rem; margin-top: 5px;">
        Os botões de ação estão desativados. Selecione uma conta específica para acessar os relatórios e funcionalidades.
    </div>
</div>
{% endif %}
```

## 🎨 Estrutura dos Botões

### Template dos Botões
```html
<a href="{% url 'painel:starlink_detailed_report' %}{% if selected_account %}?account_id={{ selected_account }}{% endif %}" 
   class="card-button {% if not selected_account %}disabled{% endif %}" 
   style="background: #fd7e14;"
   {% if not selected_account %}onclick="return false;"{% endif %}>
    <i class="fas fa-print"></i> Relatório Completo
</a>
```

#### Características:
- **Classe condicional**: `{% if not selected_account %}disabled{% endif %}`
- **Link condicional**: `{% if selected_account %}?account_id={{ selected_account }}{% endif %}`
- **Onclick condicional**: `{% if not selected_account %}onclick="return false;"{% endif %}`

## 📋 Botões Afetados

1. **Relatório Detalhado** (`starlink_detailed_report`)
2. **Consumo de Franquia** (`starlink_usage_report`)
3. **Status da API** (`starlink_api_status`)
4. **Debug da API** (`starlink_debug_api`)

## 🔄 Fluxo de Funcionamento

### Entrada na Página
1. Dashboard carrega sem conta selecionada
2. Botões aparecem desativados
3. Mensagem de aviso é exibida
4. Estatísticas mostram resumo de todas as contas

### Seleção de Conta
1. Usuário seleciona uma conta no dropdown
2. JavaScript atualiza estado dos botões
3. Página recarrega com account_id
4. Botões ficam ativados
5. Mensagem de aviso desaparece

### Volta para "Selecione uma conta"
1. Usuário seleciona "Selecione uma conta"
2. JavaScript atualiza estado dos botões
3. Página recarrega sem account_id
4. Botões ficam desativados novamente
5. Mensagem de aviso reaparece

## 🧪 Testes Implementados

### Arquivo: `test_buttons_functionality.py`

#### Testes Cobertos:
1. **test_dashboard_buttons_disabled_no_account**
   - Verifica se botões estão desativados sem conta selecionada
   
2. **test_dashboard_buttons_enabled_with_account**
   - Verifica se botões estão ativados com conta selecionada
   
3. **test_dashboard_css_disabled_buttons**
   - Verifica se CSS de botões desativados está presente
   
4. **test_dashboard_javascript_functions**
   - Verifica se funções JavaScript estão presentes
   
5. **test_dashboard_warning_message**
   - Verifica se mensagem de aviso aparece corretamente

## ✅ Benefícios

### 1. Experiência do Usuário
- ✅ Interface mais intuitiva
- ✅ Feedback visual claro sobre o estado
- ✅ Prevenção de erros de navegação

### 2. Robustez do Sistema
- ✅ Evita requisições com parâmetros inválidos
- ✅ Previne erros 404 ou 500
- ✅ Melhora a estabilidade da aplicação

### 3. Usabilidade
- ✅ Guia o usuário para a ação correta
- ✅ Mensagens informativas claras
- ✅ Navegação consistente

## 🚀 Implementação Técnica

### Arquivos Modificados:
- `painel/templates/admin/painel/starlink/dashboard.html`
- `test_buttons_functionality.py` (novo)

### Tecnologias Utilizadas:
- **Django Templates**: Lógica condicional
- **CSS**: Estilos para estados desativados
- **JavaScript**: Controle dinâmico de estados
- **HTML5**: Estrutura semântica

## 📊 Resultado Final

### Estado Inicial (Sem Conta)
```
┌─────────────────────────────────────┐
│ Selecione uma conta: [            ] │
│ ⚠️  Os botões estão desativados     │
│                                     │
│ [🔒 Relatório]  [🔒 Consumo]       │
│ [🔒 Status]     [🔒 Debug]         │
└─────────────────────────────────────┘
```

### Estado Ativo (Com Conta)
```
┌─────────────────────────────────────┐
│ Selecione uma conta: [Conta 1    ] │
│ ℹ️  Conta: Conta Principal         │
│                                     │
│ [📊 Relatório]  [📈 Consumo]       │
│ [❤️  Status]     [🐛 Debug]         │
└─────────────────────────────────────┘
```

---

**Status**: ✅ Implementado e Testado
**Data**: 05/07/2025
**Versão**: 1.1 - Botões Dinâmicos
