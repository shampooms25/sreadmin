# -*- coding: utf-8 -*-
"""
Traduções personalizadas para o Django Admin em Português do Brasil
"""

from django.utils.translation import gettext_lazy as _

# Dicionário de traduções customizadas
CUSTOM_TRANSLATIONS = {
    # Login e Autenticação
    'Username:': 'Nome de usuário:',
    'Username': 'Nome de usuário',
    'Password:': 'Senha:',
    'Password': 'Senha',
    'Log in': 'Entrar',
    'Log out': 'Sair',
    'Sign in to start your session': 'Faça login para iniciar sua sessão',
    
    # Navegação Principal
    'Administration': 'Administração',
    'Site administration': 'Administração do site',
    'Welcome,': 'Bem-vindo,',
    'View site': 'Ver site',
    'Documentation': 'Documentação',
    'Change password': 'Alterar senha',
    'Recent actions': 'Ações recentes',
    'My actions': 'Minhas ações',
    'Home': 'Início',
    'Dashboard': 'Painel',
    
    # CRUD Operations
    'Add': 'Adicionar',
    'Change': 'Alterar',
    'Delete': 'Excluir',
    'View': 'Visualizar',
    'Edit': 'Editar',
    'Save': 'Salvar',
    'Save and continue editing': 'Salvar e continuar editando',
    'Save and add another': 'Salvar e adicionar outro',
    'Save as new': 'Salvar como novo',
    'Cancel': 'Cancelar',
      # Filtros e Busca
    'Search': 'Buscar',
    'Filter': 'Filtro',
    'Show all': 'Mostrar todos',
    'Any date': 'Qualquer data',
    'Today': 'Hoje',
    'Past 7 days': 'Últimos 7 dias',
    'This month': 'Este mês',
    'This year': 'Este ano',
    'No date': 'Sem data',
    'Has date': 'Tem data',
    'Empty': 'Vazio',
    'Not empty': 'Não vazio',
    'Yes': 'Sim',
    'No': 'Não',
    'Unknown': 'Desconhecido',
    
    # Paginação
    'Go': 'Ir',
    'Clear all filters': 'Limpar todos os filtros',
    'First': 'Primeiro',
    'Previous': 'Anterior',
    'Next': 'Próximo',
    'Last': 'Último',
    'Show': 'Mostrar',
    
    # Ações em Lote
    'Action:': 'Ação:',
    'Select an action': 'Selecione uma ação',
    "Yes, I'm sure": 'Sim, tenho certeza',
    'No, take me back': 'Não, me leve de volta',
    
    # Campos e Formulários
    'Currently:': 'Atualmente:',
    'Change:': 'Alterar:',
    'Clear': 'Limpar',
    'Remove': 'Remover',
    'Add another': 'Adicionar outro',
    'Chosen': 'Escolhidos',
    'Available': 'Disponíveis',
    'Choose': 'Escolher',
    'Choose all': 'Escolher todos',
    'Remove all': 'Remover todos',
    
    # Data e Hora
    'Calendar': 'Calendário',
    'Clock': 'Relógio',
    'Now': 'Agora',
    'Midnight': 'Meia-noite',
    '6 a.m.': '6h',
    'Noon': 'Meio-dia',
    '6 p.m.': '18h',
    
    # Usuários e Permissões
    'Users': 'Usuários',
    'Groups': 'Grupos',
    'User': 'Usuário',
    'Group': 'Grupo',
    'Permissions': 'Permissões',
    'Personal info': 'Informações pessoais',
    'Important dates': 'Datas importantes',
    'First name': 'Primeiro nome',
    'Last name': 'Último nome',
    'Email address': 'Endereço de email',
    'Active': 'Ativo',
    'Staff status': 'Status da equipe',
    'Superuser status': 'Status de superusuário',
    'Last login': 'Último login',
    'Date joined': 'Data de cadastro',
    
    # Mensagens de Status
    'None available': 'Nenhuma disponível',
    'Unknown content': 'Conteúdo desconhecido',
    'Page not found': 'Página não encontrada',
    'Server Error (500)': 'Erro do Servidor (500)',
    'Database error': 'Erro de banco de dados',
    
    # Validação
    'This field is required.': 'Este campo é obrigatório.',
    'Enter a valid value.': 'Insira um valor válido.',
    'Enter a valid email address.': 'Insira um endereço de email válido.',
    'Enter a valid URL.': 'Insira uma URL válida.',
    'Enter a valid date.': 'Insira uma data válida.',
    'Enter a valid time.': 'Insira um horário válido.',
    'Enter a valid date/time.': 'Insira uma data/horário válidos.',
    'Enter a whole number.': 'Insira um número inteiro.',
    'Enter a valid number.': 'Insira um número válido.',
}

def get_translation(text):
    """
    Retorna a tradução personalizada para o texto fornecido.
    Se não encontrar tradução, retorna o texto original.
    """
    return CUSTOM_TRANSLATIONS.get(text, text)
