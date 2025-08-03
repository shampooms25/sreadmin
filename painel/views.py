from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.contrib import messages, admin
from django.urls import reverse
from django.db.models import Sum
from datetime import datetime
from django.contrib.admin import site
from django.template.response import TemplateResponse
from django.contrib.admin.sites import AdminSite
from .starlink_api import (
    query_service_lines, 
    get_billing_summary, 
    get_service_line_details,
    test_api_connection,
    get_service_lines_with_location,
    debug_api_response,
    get_available_accounts,
    get_account_info,
    get_service_lines_with_auto_recharge_status,
    get_service_lines_with_auto_recharge_status_parallel,
    get_usage_report_data,
    disable_auto_recharge,
    DEFAULT_ACCOUNT
)
from .models import StarlinkAdminProxy
import json

def get_admin_context(request):
    """
    Retorna o contexto necessário para templates do admin
    """
    admin_site = site
    context = admin_site.each_context(request)
    return context

def get_selected_account(request):
    """
    Obtém a conta selecionada pelo usuário ou None para mostrar todas
    """
    # Aceitar tanto 'account' quanto 'account_id' para compatibilidade
    selected_account = (request.GET.get('account_id') or 
                       request.GET.get('account') or 
                       request.POST.get('account_id') or 
                       request.POST.get('account'))
    
    # Se uma conta específica foi selecionada e é válida, retorna ela
    if selected_account and selected_account in get_available_accounts():
        return selected_account
    
    # Se não foi selecionada conta ou é inválida, retorna None para mostrar todas
    return None


def get_breadcrumbs_with_account(base_breadcrumbs, selected_account):
    """
    Adiciona o parâmetro de conta aos breadcrumbs
    """
    breadcrumbs = []
    for crumb in base_breadcrumbs:
        if crumb.get('url') and selected_account:
            # Adicionar o parâmetro de conta se necessário
            separator = '&' if '?' in crumb['url'] else '?'
            crumb['url'] = f"{crumb['url']}{separator}account_id={selected_account}"
        breadcrumbs.append(crumb)
    return breadcrumbs


def get_account_context(request):
    """
    Retorna contexto relacionado às contas Starlink
    """
    selected_account = get_selected_account(request)
    
    return {
        'available_accounts': get_available_accounts(),
        'selected_account': selected_account,
        'account_info': get_account_info(selected_account) if selected_account else None,
        'show_all_accounts': selected_account is None
    }


@staff_member_required
def starlink_dashboard(request):
    """
    Dashboard principal da Starlink com botões de acesso
    """
    # Obter contexto do admin
    context = get_admin_context(request)
    
    # Adicionar contexto das contas
    context.update(get_account_context(request))
    selected_account = get_selected_account(request)
    
    # Criar breadcrumbs
    base_breadcrumbs = [
        {'name': 'Início', 'url': '/admin/'},
        {'name': 'Starlink Admin', 'url': '/admin/starlink/'},
        {'name': 'Dashboard', 'url': None}
    ]
    
    # Adicionar contexto específico da view
    context.update({
        'title': 'Starlink - Dashboard',
        'breadcrumbs': get_breadcrumbs_with_account(base_breadcrumbs, selected_account)
    })
    
    # Tentar obter estatísticas rápidas dos service lines
    try:
        if selected_account:
            # Conta específica selecionada
            result = get_service_lines_with_location(selected_account)
            if "error" not in result:
                context.update({
                    'has_statistics': True,
                    'statistics': result.get("statistics", {}),
                    'total_service_lines': result.get("total", 0),
                    'account_mode': 'single'
                })
        else:
            # Mostrar resumo de todas as contas
            # all_accounts_result = get_all_accounts_summary()
            # if all_accounts_result.get("success"):
            #     total_summary = all_accounts_result.get("total_summary", {})
            #     context.update({
            #         'has_statistics': True,
            #         'statistics': {
            #             'total_service_lines': total_summary.get("total_service_lines", 0),
            #             'active_lines': total_summary.get("active_lines", 0),
            #             'offline_lines': total_summary.get("offline_lines", 0),
            #             'no_data_lines': total_summary.get("no_data_lines", 0),
            #             'pending_lines': total_summary.get("pending_lines", 0),
            #             'suspended_lines': total_summary.get("suspended_lines", 0),
            #             'indeterminate_lines': total_summary.get("indeterminate_lines", 0),
            #             'total_counted': total_summary.get("total_counted", 0),
            #             'count_discrepancy': total_summary.get("count_discrepancy", 0)
            #         }
            #     })
            pass
    except Exception as e:
        # Se não conseguir obter estatísticas, não quebra a página
        context.update({
            'has_statistics': False,
            'statistics': {},
            'total_service_lines': 0,
            'account_mode': 'single' if selected_account else 'all'
        })
    
    return render(request, 'admin/painel/starlink/dashboard.html', context)


@staff_member_required
def starlink_service_lines(request):
    """
    Lista todos os Service Line Numbers
    """
    # Obter contexto do admin
    context = get_admin_context(request)
    
    # Adicionar contexto das contas
    context.update(get_account_context(request))
    selected_account = get_selected_account(request)
    
    # Criar breadcrumbs
    base_breadcrumbs = [
        {'name': 'Início', 'url': '/admin/'},
        {'name': 'Starlink Admin', 'url': '/admin/starlink/'},
        {'name': 'Service Lines', 'url': None}
    ]
    
    # Adicionar contexto específico da view
    context.update({
        'title': 'Service Lines - Starlink',
        'breadcrumbs': get_breadcrumbs_with_account(base_breadcrumbs, selected_account)
    })
    # Adicionar contexto das contas
    context.update(get_account_context(request))
    selected_account = get_selected_account(request)
    
    # Adicionar contexto específico da view
    context.update({
        'title': 'Service Lines - Starlink',
        'breadcrumbs': [
            {'name': 'Início', 'url': '/admin/'},
            {'name': 'Starlink Admin', 'url': '/admin/starlink/'},
            {'name': 'Service Lines', 'url': None}
        ]
    })
    
    try:
        result = get_service_lines_with_location(selected_account)
        if "error" in result:
            context.update({
                'service_lines': [],
                'total_count': 0,
                'success': False,
                'error': result["error"]
            })
            messages.error(request, f'Erro ao consultar Service Lines: {result["error"]}')
        else:
            service_lines = result.get("service_lines", [])
            context.update({
                'service_lines': service_lines,
                'total_count': result.get("total", 0),
                'statistics': result.get("statistics", {}),
                'success': True,
                'account_id': result.get("account_id", "N/A"),
                'last_update': result.get("last_update", "N/A")
            })
            messages.success(request, f'{len(service_lines)} Service Lines encontrados com sucesso!')
    except Exception as e:
        context.update({
            'service_lines': [],
            'total_count': 0,
            'success': False,
            'error': str(e)
        })
        messages.error(request, f'Erro ao consultar Service Lines: {str(e)}')
    
    return render(request, 'admin/painel/starlink/service_lines.html', context)


@staff_member_required
def starlink_billing_report(request):
    """
    Relatório de faturamento
    """
    # Obter contexto do admin
    context = get_admin_context(request)
    
    # Adicionar contexto das contas
    context.update(get_account_context(request))
    selected_account = get_selected_account(request)
    
    # Adicionar contexto específico da view
    context.update({
        'title': 'Relatório de Faturamento - Starlink',
        'breadcrumbs': [
            {'name': 'Início', 'url': '/admin/'},
            {'name': 'Starlink Admin', 'url': '/admin/starlink/'},
            {'name': 'Relatório de Faturamento', 'url': None}
        ]
    })
    
    try:
        billing_data = get_billing_summary(selected_account)
        context.update({
            'billing_data': billing_data,
            'success': True
        })
        if 'error' not in billing_data:
            messages.success(request, 'Relatório de faturamento gerado com sucesso!')
        else:
            messages.error(request, f'Erro: {billing_data["error"]}')
    except Exception as e:
        context.update({
            'billing_data': {'error': str(e)},
            'success': False
        })
        messages.error(request, f'Erro ao gerar relatório: {str(e)}')
    
    return render(request, 'admin/painel/starlink/billing_report.html', context)


@staff_member_required
def starlink_api_status(request):
    """
    Verifica o status da API
    """
    selected_account = get_selected_account(request)
    
    if request.method == 'POST':
        try:
            # Usar a nova função de teste de conexão
            status_result = test_api_connection(selected_account)
            return JsonResponse(status_result)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Erro inesperado: {str(e)}',
                'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            })
    
    # Para GET requests, fazer um teste inicial
    try:
        api_status = test_api_connection(selected_account)
    except Exception as e:
        api_status = {
            'status': 'error',
            'message': f'Erro ao verificar status: {str(e)}',
            'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
    
    # Obter contexto do admin
    context = get_admin_context(request)
    
    # Adicionar contexto das contas
    context.update(get_account_context(request))
    
    # Adicionar contexto específico da view
    context.update({
        'title': 'Status da API - Starlink',
        'breadcrumbs': [
            {'name': 'Início', 'url': '/admin/'},
            {'name': 'Starlink Admin', 'url': '/admin/starlink/'},
            {'name': 'Status da API', 'url': None}
        ],
        'api_status': api_status
    })
    
    return render(request, 'admin/painel/starlink/api_status.html', context)


@staff_member_required
def starlink_detailed_report(request):
    """
    Relatório detalhado da Starlink com lista completa de Service Lines
    """
    # Obter contexto do admin
    context = get_admin_context(request)
    
    # Adicionar contexto das contas
    context.update(get_account_context(request))
    selected_account = get_selected_account(request)
    
    # Adicionar contexto específico da view
    context.update({
        'title': 'Relatório Detalhado - Starlink',
        'breadcrumbs': [
            {'name': 'Início', 'url': '/admin/'},
            {'name': 'Starlink Admin', 'url': '/admin/starlink/'},
            {'name': 'Relatório Detalhado', 'url': None}
        ]
    })
    
    try:
        # Obter dados detalhados dos service lines
        result = get_service_lines_with_location(selected_account)
        
        if "error" in result:
            context.update({
                'success': False,
                'error': result["error"],
                'service_lines': [],
                'total_count': 0
            })
            messages.error(request, f'Erro ao gerar relatório: {result["error"]}')
        else:
            service_lines = result.get("service_lines", [])
            context.update({
                'success': True,
                'service_lines': service_lines,
                'total_count': result.get("total", 0),
                'statistics': result.get("statistics", {}),
                'account_id': result.get("account_id", "N/A"),
                'last_update': result.get("last_update", "N/A")
            })
            messages.success(request, f'Relatório gerado com sucesso! {len(service_lines)} Service Lines encontrados.')
            
    except Exception as e:
        context.update({
            'success': False,
            'error': str(e),
            'service_lines': [],
            'total_count': 0
        })
        messages.error(request, f'Erro ao gerar relatório: {str(e)}')
    
    return render(request, 'admin/painel/starlink/detailed_report.html', context)


@staff_member_required
def starlink_debug_api(request):
    """
    Debug da API - mostra resultado completo no console
    """
    # Obter contexto do admin
    context = get_admin_context(request)
    
    # Adicionar contexto das contas
    context.update(get_account_context(request))
    selected_account = get_selected_account(request)
    
    # Adicionar contexto específico da view
    context.update({
        'title': 'Debug API - Starlink',
        'breadcrumbs': [
            {'name': 'Início', 'url': '/admin/'},
            {'name': 'Starlink Admin', 'url': '/admin/starlink/'},
            {'name': 'Debug API', 'url': None}
        ]
    })
    
    try:
        print(f"\n🚀 INICIANDO DEBUG DA API STARLINK - Conta: {selected_account}...")
        
        # Debug padrão da API
        debug_api_response(selected_account)
        
        # Nota: Recurso de recurring-data foi removido por enquanto
        # # Consultar recurring-data para todas as service lines
        # if selected_account:
        #     print(f"\n🔍 CONSULTANDO RECURRING-DATA para conta: {selected_account}")
        #     recurring_data = get_all_recurring_data(selected_account)
        #     if recurring_data.get("success"):
        #         print(f"✅ Recurring-data consultado para {recurring_data.get('total_service_lines', 0)} service lines")
        #     else:
        #         print(f"❌ Erro ao consultar recurring-data: {recurring_data.get('error', 'Erro desconhecido')}")
        # else:
        #     print("⚠️ Nenhuma conta selecionada - pulando consulta de recurring-data")
        
        print("✅ Debug concluído! Verifique o console do servidor.")
        
        context.update({
            'success': True,
            'message': 'Debug executado com sucesso! Verifique o console do servidor para ver os dados completos da API, incluindo informações de recurring-data.'
        })
        messages.success(request, 'Debug da API executado! Verifique o console do servidor.')
        
    except Exception as e:
        context.update({
            'success': False,
            'error': str(e)
        })
        messages.error(request, f'Erro no debug: {str(e)}')
    
    return render(request, 'admin/painel/starlink/debug_api.html', context)


@staff_member_required
def starlink_usage_report(request):
    """
    Relatório de consumo de franquia dos Service Lines
    """
    # Obter contexto do admin
    context = get_admin_context(request)
    
    # Adicionar contexto das contas
    context.update(get_account_context(request))
    selected_account = get_selected_account(request)
    
    # Calcular o ciclo atual (dia 03 do mês atual até hoje)
    from datetime import date
    today = date.today()
    
    # Se hoje é antes do dia 3, o ciclo atual começou no mês anterior
    if today.day < 3:
        # Ciclo começou no dia 3 do mês anterior
        if today.month == 1:
            cycle_start_month = 12
            cycle_start_year = today.year - 1
        else:
            cycle_start_month = today.month - 1
            cycle_start_year = today.year
        cycle_start = date(cycle_start_year, cycle_start_month, 3)
    else:
        # Ciclo começou no dia 3 do mês atual
        cycle_start = date(today.year, today.month, 3)
    
    cycle_end = today
    
    # Adicionar contexto específico da view
    context.update({
        'title': 'Relatório de Consumo de Franquia - Starlink',
        'breadcrumbs': [
            {'name': 'Início', 'url': '/admin/'},
            {'name': 'Starlink Admin', 'url': '/admin/starlink/'},
            {'name': 'Relatório de Consumo', 'url': None}
        ],
        'cycle_start_calculated': cycle_start.strftime("%d/%m/%Y"),
        'cycle_end_calculated': cycle_end.strftime("%d/%m/%Y")
    })
    
    try:
        # Obter dados de consumo usando a função específica para relatório de uso
        # Passar as datas do ciclo atual para a função
        result = get_usage_report_data(selected_account, 
                                     cycle_start=context['cycle_start_calculated'],
                                     cycle_end=context['cycle_end_calculated'])
        
        if "error" in result:
            context.update({
                'success': False,
                'error': result["error"],
                'usage_data': [],
                'statistics': {}
            })
            messages.error(request, f'Erro ao gerar relatório: {result["error"]}')
        else:
            # As datas já estão corretas no result agora
            context.update({
                'success': True,
                'usage_data': result.get("usage_data", []),
                'statistics': result.get("statistics", {}),
                'total_lines': result.get("total_lines", 0),
                'cycle_start': result.get("cycle_start", "N/A"),
                'cycle_end': result.get("cycle_end", "N/A"),
                'cycle_days': result.get("cycle_days", 0),
                'account_id': result.get("account_id", selected_account),
                'last_update': result.get("last_update", "N/A")
            })
            
            cycle_days = result.get("cycle_days", 0)
            messages.success(request, f'Relatório gerado para o ciclo atual ({cycle_days} dias)! {result.get("total_lines", 0)} Service Lines analisados.')
            
    except Exception as e:
        context.update({
            'success': False,
            'error': str(e),
            'usage_data': [],
            'statistics': {}
        })
        messages.error(request, f'Erro ao gerar relatório: {str(e)}')
    
    return render(request, 'admin/painel/starlink/usage_report.html', context)


@staff_member_required
def starlink_main(request):
    """
    Página principal Starlink com 2 cards: Dashboard e Administração
    """
    # Obter contexto do admin
    context = get_admin_context(request)
    
    # Adicionar contexto específico da view
    context.update({
        'title': 'Starlink Admin',
        'breadcrumbs': [
            {'name': 'Início', 'url': '/admin/'},
            {'name': 'Starlink Admin', 'url': None}
        ]
    })
    
    return render(request, 'admin/painel/starlink/main.html', context)


@staff_member_required
def starlink_admin(request):
    """
    Página de administração Starlink com visão geral de todas as contas
    """
    # Obter contexto do admin
    context = get_admin_context(request)
    
    # Adicionar contexto das contas
    context.update(get_account_context(request))
    
    # Adicionar contexto específico da view
    context.update({
        'title': 'Starlink - Administração',
        'breadcrumbs': [
            {'name': 'Início', 'url': '/admin/'},
            {'name': 'Starlink Admin', 'url': '/admin/starlink/'},
            {'name': 'Administração', 'url': None}
        ]
    })
    
    return render(request, 'admin/painel/starlink/admin.html', context)


@staff_member_required
def starlink_auto_recharge_management(request):
    """View para gerenciar recarga automática de service lines"""
    selected_account = request.GET.get('account_id')
    
    if not selected_account:
        messages.error(request, "Por favor, selecione uma conta para gerenciar a recarga automática.")
        return redirect('painel:starlink_dashboard')
    
    # Verificar se a conta existe
    available_accounts = get_available_accounts()
    if selected_account not in available_accounts:
        messages.error(request, "Conta inválida selecionada.")
        return redirect('painel:starlink_dashboard')
    
    account_info = get_account_info(selected_account)
    
    # Obter service lines com status de recarga automática
    # Usar versão paralela para melhor performance com mais de 20 service lines
    print(f"🚀 Verificando quantas service lines existem para decidir o método...")
    
    # Fazer uma consulta rápida para contar as service lines
    quick_check = get_service_lines_with_location(selected_account)
    service_lines_count = 0
    if 'error' not in quick_check:
        service_lines_count = len(quick_check.get('service_lines', []))
    
    print(f"📊 Encontradas {service_lines_count} service lines")
    
    # Usar versão paralela se houver muitas service lines
    if service_lines_count > 20:
        print(f"🚀 Usando consulta paralela para {service_lines_count} service lines")
        service_lines_data = get_service_lines_with_auto_recharge_status_parallel(selected_account, max_workers=5)
    else:
        print(f"🔄 Usando consulta sequencial para {service_lines_count} service lines")
        service_lines_data = get_service_lines_with_auto_recharge_status(selected_account)
    
    if 'error' in service_lines_data:
        messages.error(request, f"Erro ao obter dados: {service_lines_data['error']}")
        service_lines = []
        total_count = 0
        active_count = 0
    else:
        service_lines = service_lines_data.get('service_lines', [])
        total_count = service_lines_data.get('total_count', 0)
        
        # Contar quantas têm recarga automática ativa
        active_count = sum(1 for sl in service_lines 
                          if sl.get('auto_recharge_status', {}).get('active', False))
    
    # Obter contexto do admin
    admin_context = get_admin_context(request)
    
    context = admin_context.copy()
    context.update({
        'title': 'Gerenciamento de Recarga Automática',
        'selected_account': selected_account,
        'account_info': account_info,
        'available_accounts': available_accounts,
        'service_lines': service_lines,
        'service_lines_data': service_lines_data,  # Adicionar dados completos para métricas
        'performance_stats': service_lines_data.get('performance_stats', {}),  # Estatísticas de performance
        'total_count': total_count,
        'active_count': active_count,
        'inactive_count': total_count - active_count,
    })
    
    return render(request, 'admin/painel/starlink/auto_recharge_management.html', context)


@staff_member_required
def starlink_toggle_auto_recharge(request):
    """View para ativar/desativar recarga automática de uma service line"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    account_id = request.POST.get('account_id')
    service_line_number = request.POST.get('service_line_number')
    action = request.POST.get('action')  # 'disable' ou 'enable'
    
    if not all([account_id, service_line_number, action]):
        return JsonResponse({'error': 'Parâmetros obrigatórios não fornecidos'}, status=400)
    
    try:
        if action == 'disable':
            result = disable_auto_recharge(account_id, service_line_number)
        else:
            return JsonResponse({'error': 'Ação não implementada ainda'}, status=400)
        
        if 'error' in result:
            return JsonResponse({'error': result['error']}, status=400)
        
        return JsonResponse({
            'success': True,
            'message': result.get('message', 'Operação realizada com sucesso'),
            'service_line': service_line_number
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
def starlink_disable_auto_recharge(request):
    """View para confirmar e executar a desativação de recarga automática"""
    account_id = request.GET.get('account_id') or request.POST.get('account_id')
    service_line_number = request.GET.get('service_line') or request.POST.get('service_line_number')
    
    if not account_id or not service_line_number:
        messages.error(request, "Parâmetros obrigatórios não fornecidos.")
        return redirect('painel:starlink_auto_recharge_management')
    
    # Verificar se a conta existe
    available_accounts = get_available_accounts()
    if account_id not in available_accounts:
        messages.error(request, "Conta inválida selecionada.")
        return redirect('painel:starlink_auto_recharge_management')
    
    account_info = get_account_info(account_id)
    
    # Obter contexto do admin
    admin_context = get_admin_context(request)
    
    context = admin_context.copy()
    context.update({
        'title': 'Desativar Recarga Automática',
        'account_id': account_id,
        'account_info': account_info,
        'service_line_number': service_line_number,
        'service_line_info': None
    })
    
    # Se for POST, executar a desativação
    if request.method == 'POST' and request.POST.get('confirm') == 'true':
        try:
            print(f"🚀 DESATIVANDO RECARGA AUTOMÁTICA:")
            print(f"   Conta: {account_id}")
            print(f"   Service Line: {service_line_number}")
            
            result = disable_auto_recharge(account_id, service_line_number)
            
            if result.get('success'):
                messages.success(request, f'✅ Recarga automática desativada com sucesso para a Service Line {service_line_number}!')
                print(f"✅ SUCESSO: Recarga automática desativada para {service_line_number}")
                
                # Limpar cache para forçar atualização
                from .starlink_api import clear_auto_recharge_cache
                clear_auto_recharge_cache()
                
                return redirect(f"{reverse('painel:starlink_auto_recharge_management')}?account_id={account_id}")
            else:
                error_msg = result.get('error', 'Erro desconhecido')
                messages.error(request, f'❌ Erro ao desativar recarga automática: {error_msg}')
                print(f"❌ ERRO: {error_msg}")
                
        except Exception as e:
            messages.error(request, f'❌ Erro inesperado: {str(e)}')
            print(f"❌ ERRO INESPERADO: {str(e)}")
    
    # Obter informações da service line para exibir na confirmação
    try:
        # Buscar a service line específica
        service_lines_result = get_service_lines_with_location(account_id)
        
        if "error" not in service_lines_result:
            service_lines = service_lines_result.get("service_lines", [])
            
            # Encontrar a service line específica
            target_service_line = None
            for sl in service_lines:
                if sl.get("serviceLineNumber") == service_line_number:
                    target_service_line = sl
                    break
            
            if target_service_line:
                # Obter status de recarga automática
                from .starlink_api import check_auto_recharge_status_fast
                auto_recharge_status = check_auto_recharge_status_fast(account_id, service_line_number)
                target_service_line["auto_recharge_status"] = auto_recharge_status
                
                context['service_line_info'] = target_service_line
            else:
                messages.warning(request, f'Service Line {service_line_number} não encontrada na conta {account_id}.')
        else:
            messages.error(request, f'Erro ao obter dados da conta: {service_lines_result["error"]}')
            
    except Exception as e:
        messages.error(request, f'Erro ao obter informações da Service Line: {str(e)}')
    
    return render(request, 'admin/painel/starlink/disable_auto_recharge.html', context)


@staff_member_required
def eld_video_list(request):
    """
    Lista todos os vídeos ELD uploadados
    """
    from .models import EldUploadVideo
    
    # Obter contexto do admin
    context = get_admin_context(request)
    
    # Obter todos os vídeos ordenados por data
    videos = EldUploadVideo.objects.all().order_by('-data', '-id')
    
    # Calcular estatísticas
    total_videos = videos.count()
    total_size = sum(video.tamanho for video in videos)
    
    context.update({
        'title': 'Uploads de Vídeos ELD',
        'breadcrumbs': [
            {'name': 'Início', 'url': '/admin/'},
            {'name': 'ELD Admin', 'url': '/admin/eld/'},
            {'name': 'Uploads de Vídeos', 'url': None}
        ],
        'videos': videos,
        'total_videos': total_videos,
        'total_size': round(total_size, 2),
        'success': True
    })
    
    return render(request, 'admin/painel/eld/video_list.html', context)


@staff_member_required
def eld_video_upload(request):
    """
    Formulário para upload de vídeos ELD
    """
    from .forms import EldVideoUploadForm
    from .models import EldUploadVideo
    
    # Obter contexto do admin
    context = get_admin_context(request)
    
    if request.method == 'POST':
        form = EldVideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Salvar o vídeo
                video = form.save()
                
                messages.success(
                    request, 
                    f'✅ Vídeo enviado com sucesso! '
                    f'Arquivo: {video.video.name} ({video.tamanho}MB)'
                )
                return redirect('painel:eld_video_list')
                
            except Exception as e:
                messages.error(request, f'❌ Erro ao salvar vídeo: {str(e)}')
        else:
            # Mostrar erros de validação
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {error}')
    else:
        form = EldVideoUploadForm()
    
    context.update({
        'title': 'Upload de Vídeo ELD',
        'breadcrumbs': [
            {'name': 'Início', 'url': '/admin/'},
            {'name': 'ELD Admin', 'url': '/admin/eld/'},
            {'name': 'Uploads de Vídeos', 'url': '/admin/eld/videos/'},
            {'name': 'Novo Upload', 'url': None}
        ],
        'form': form
    })
    
    return render(request, 'admin/painel/eld/video_upload.html', context)


@staff_member_required
def eld_video_delete(request, video_id):
    """
    Deletar um vídeo ELD
    """
    from .models import EldUploadVideo
    import os
    
    try:
        video = EldUploadVideo.objects.get(id=video_id)
        
        if request.method == 'POST':
            # Deletar arquivo físico
            if video.video and os.path.exists(video.video.path):
                os.remove(video.video.path)
            
            # Deletar registro do banco
            video_name = video.video.name
            video.delete()
            
            messages.success(request, f'✅ Vídeo {video_name} deletado com sucesso!')
            return redirect('painel:eld_video_list')
        
        # Obter contexto do admin
        context = get_admin_context(request)
        context.update({
            'title': 'Deletar Vídeo ELD',
            'breadcrumbs': [
                {'name': 'Início', 'url': '/admin/'},
                {'name': 'ELD Admin', 'url': '/admin/eld/'},
                {'name': 'Uploads de Vídeos', 'url': '/admin/eld/videos/'},
                {'name': 'Deletar', 'url': None}
            ],
            'video': video
        })
        
        return render(request, 'admin/painel/eld/video_delete.html', context)
        
    except EldUploadVideo.DoesNotExist:
        messages.error(request, '❌ Vídeo não encontrado!')
        return redirect('painel:eld_video_list')


@staff_member_required
def eld_main(request):
    """
    Página principal do ELD Admin
    """
    from .models import EldUploadVideo
    
    # Obter contexto do admin
    context = get_admin_context(request)
    
    # Estatísticas rápidas
    total_videos = EldUploadVideo.objects.count()
    total_size = EldUploadVideo.objects.aggregate(
        total=Sum('tamanho')
    )['total'] or 0
    
    recent_videos = EldUploadVideo.objects.order_by('-data', '-id')[:5]
    
    context.update({
        'title': 'ELD Admin',
        'breadcrumbs': [
            {'name': 'Início', 'url': '/admin/'},
            {'name': 'ELD Admin', 'url': None}
        ],
        'total_videos': total_videos,
        'total_size': round(total_size, 2),
        'recent_videos': recent_videos
    })
    
    return render(request, 'admin/painel/eld/main.html', context)


# ========================================
# VIEWS PARA PORTAL SEM VÍDEO
# ========================================

# Importar views do arquivo portal_views.py
from .portal_views import (
    portal_sem_video_list,
    portal_sem_video_upload, 
    portal_sem_video_detail,
    portal_sem_video_delete,
    portal_sem_video_download,
    video_preview_ajax
)
