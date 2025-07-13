# Starlink Admin Panel (SRAdmin)

Sistema de administração completo para gerenciamento de contas Starlink Enterprise.

## 🚀 Funcionalidades

- **Dashboard Completo**: Visualização geral de todas as Service Lines
- **Gerenciamento de Recarga Automática**: Ativação/desativação de recarga automática de franquia
- **Relatórios de Uso**: Consumo detalhado com dados reais da API Starlink
- **Interface Moderna**: Design responsivo e intuitivo
- **Multi-conta**: Suporte para múltiplas contas Starlink

## 🛠️ Tecnologias

- **Backend**: Django 5.2.3 + Python 3.13
- **Frontend**: HTML5, CSS3, JavaScript (AdminLTE theme)
- **API**: Integração completa com Starlink Enterprise API
- **Database**: SQLite (desenvolvimento)

## ⚙️ Configuração

1. Clone o repositório
2. Instale as dependências: \pip install -r requirements.txt\
3. Configure as credenciais da API Starlink
4. Execute: \python manage.py runserver\

## 📊 Principais Endpoints

- \/admin/starlink/\ - Dashboard principal
- \/admin/starlink/auto-recharge/\ - Gerenciamento de recarga automática
- \/admin/starlink/usage-report/\ - Relatórios de consumo

## 🔐 Funcionalidades de Segurança

- Autenticação obrigatória
- Cache inteligente para performance
- Validação de dados da API
- Logs detalhados de operações

## 📈 Performance

- Processamento paralelo para consultas múltiplas
- Cache de resultados para evitar chamadas desnecessárias
- Interface otimizada para grandes volumes de dados

---
Desenvolvido para gerenciamento eficiente de infraestrutura Starlink Enterprise.
