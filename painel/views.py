from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse
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
    get_telemetry_data,
    get_availability_report_data,
    get_service_line_location,
    get_service_lines_with_auto_recharge_status_parallel,
    get_usage_report_data,
    disable_auto_recharge,
    get_telemetry_data,
    get_availability_report_data,
    get_service_line_location,
    determine_service_line_status,
    get_enhanced_service_line_status,
    DEFAULT_ACCOUNT
)
from .models import StarlinkAdminProxy
import json

# Importações para geração de PDF
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.units import inch
    from io import BytesIO
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

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
                'account_id': result.get("account_id", "N/A")
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
        'current_time': datetime.now(),
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
                'account_id': result.get("account_id", "N/A")
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
                'account_id': result.get("account_id", selected_account)
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

@staff_member_required
def starlink_service_lines_report(request):
    """
    Relatório detalhado das Service Lines com consumo desde janeiro e exportação PDF
    """
    # Verificar se reportlab está disponível para PDF
    if not REPORTLAB_AVAILABLE:
        messages.error(request, 'A biblioteca reportlab não está instalada. Instale com: pip install reportlab')
        return redirect('/admin/starlink/')
    
    import calendar
    
    # Lista das service lines disponíveis
    available_service_lines = [
        "ACC-2744134-64041-5",
        "SL-584834-27677-38",  # Água Boa
        "SL-1699740-82130-75", # Andradina
        "SL-392724-73066-26",  # Barra do Garças
        "SL-587704-51577-33",  # Campo Grande II
        "SL-394617-13437-25",  # Colíder II
        "SL-530469-90180-22",  # Diamantino
        "SL-491513-87949-37",  # Ituiutaba
        "SL-395043-99178-35",  # Iturama 16
        "SL-2637054-65540-72", # Iturama 129
        "SL-545676-85363-35",  # Juara
        "SL-395214-97826-33",  # Mozarlandia
        "SL-394623-22091-1",   # Nova Andradina
        "SL-394389-82386-40",  # Nova Andradina
        "SL-557504-39478-34",  # Pedra Preta
        "SL-2649008-40458-75", # Pedra Preta MT Novembro
        "SL-395008-69755-34",  # Pimenta Bueno
        "SL-493552-30739-27",  # Pontes e Lacerda
        "SL-553068-10955-24",  # Santana do Araguaia
        "SL-395124-53530-17",  # Senador Canedo
        "SL-405115-90755-19",  # Vilhena 132
        "SL-573409-21924-23",  # Vilhena 062
        "SL-395102-14680-16",  # Lins Couros
        "SL-390500-47941-19",  # Lins Lin
        "SL-395083-96744-35",  # Lins
        "SL-395221-96279-32",  # Lins
    ]
    
    # Mapeamento de service lines para localidades
    service_line_locations = {
        "ACC-2744134-64041-5": "Conta Principal",
        "SL-584834-27677-38": "Água Boa",
        "SL-1699740-82130-75": "Andradina",
        "SL-392724-73066-26": "Barra do Garças",
        "SL-587704-51577-33": "Campo Grande II",
        "SL-394617-13437-25": "Colíder II",
        "SL-530469-90180-22": "Diamantino",
        "SL-491513-87949-37": "Ituiutaba",
        "SL-395043-99178-35": "Iturama 16",
        "SL-2637054-65540-72": "Iturama 129",
        "SL-545676-85363-35": "Juara",
        "SL-395214-97826-33": "Mozarlandia",
        "SL-394623-22091-1": "Nova Andradina",
        "SL-394389-82386-40": "Nova Andradina",
        "SL-557504-39478-34": "Pedra Preta",
        "SL-2649008-40458-75": "Pedra Preta MT Novembro",
        "SL-395008-69755-34": "Pimenta Bueno",
        "SL-493552-30739-27": "Pontes e Lacerda",
        "SL-553068-10955-24": "Santana do Araguaia",
        "SL-395124-53530-17": "Senador Canedo",
        "SL-405115-90755-19": "Vilhena 132",
        "SL-573409-21924-23": "Vilhena 062",
        "SL-395102-14680-16": "Lins Couros",
        "SL-390500-47941-19": "Lins Lin",
        "SL-395083-96744-35": "Lins",
        "SL-395221-96279-32": "Lins",
    }
    
    # Função para buscar dados de consumo de cada service line
    def get_service_line_consumption_data(service_lines):
        consumption_data = {}
        
        # Gerar lista de ciclos de faturamento (dia 03 até dia 02 do próximo mês)
        current_date = datetime.now()
        cycles = []
        
        # Começar de janeiro 2025
        start_year = 2025
        start_month = 1
        
        # Gerar ciclos até o mês atual
        for month in range(start_month, current_date.month + 1):
            cycle_start = datetime(start_year, month, 3)  # Dia 03 do mês
            
            # Calcular o fim do ciclo (dia 02 do próximo mês)
            if month == 12:
                cycle_end = datetime(start_year + 1, 1, 2)
            else:
                cycle_end = datetime(start_year, month + 1, 2)
            
            cycle_name = f"{calendar.month_name[month]} {start_year}"
            cycles.append({
                'name': cycle_name,
                'start_date': cycle_start,
                'end_date': cycle_end,
                'month': month,
                'year': start_year
            })
        
        for sl in service_lines:
            try:
                # Buscar dados de consumo da API Starlink para cada ciclo
                monthly_consumption = []
                total_consumption_gb = 0
                
                for cycle in cycles:
                    try:
                        # Aqui seria a chamada real para a API Starlink
                        # cycle_start_str = cycle['start_date'].strftime("%d/%m/%Y")
                        # cycle_end_str = cycle['end_date'].strftime("%d/%m/%Y")
                        # usage_data = get_usage_report_data(account_id="ACC-2744134-64041-5", 
                        #                                   cycle_start=cycle_start_str, 
                        #                                   cycle_end=cycle_end_str)
                        
                        # Por enquanto, simular dados até a integração estar completa
                        import random
                        
                        # Simular valores priority e standard (em GB)
                        priority_gb = round(random.uniform(20, 80), 2)
                        standard_gb = round(random.uniform(30, 100), 2)
                        
                        # Consumo total = priority + standard
                        total_cycle_gb = priority_gb + standard_gb
                        total_consumption_gb += total_cycle_gb
                        
                        monthly_consumption.append({
                            'cycle_name': cycle['name'],
                            'cycle_start': cycle['start_date'].strftime("%d/%m/%Y"),
                            'cycle_end': cycle['end_date'].strftime("%d/%m/%Y"),
                            'priority_gb': priority_gb,
                            'standard_gb': standard_gb,
                            'total_gb': total_cycle_gb,
                            'total_mb': total_cycle_gb * 1024
                        })
                        
                    except Exception as e:
                        print(f"Erro ao buscar dados do ciclo {cycle['name']} para {sl}: {e}")
                        monthly_consumption.append({
                            'cycle_name': cycle['name'],
                            'cycle_start': cycle['start_date'].strftime("%d/%m/%Y"),
                            'cycle_end': cycle['end_date'].strftime("%d/%m/%Y"),
                            'priority_gb': 0,
                            'standard_gb': 0,
                            'total_gb': 0,
                            'total_mb': 0,
                            'error': str(e)
                        })
                
                consumption_data[sl] = {
                    'location': service_line_locations.get(sl, "N/A"),
                    'monthly_data': monthly_consumption,
                    'total_consumption_gb': round(total_consumption_gb, 2),
                    'average_monthly_gb': round(total_consumption_gb / len(cycles), 2) if cycles else 0,
                    'total_cycles': len(cycles),
                    'status': 'Ativo'
                }
                
            except Exception as e:
                print(f"Erro ao buscar dados de {sl}: {e}")
                consumption_data[sl] = {
                    'location': service_line_locations.get(sl, "N/A"),
                    'monthly_data': [],
                    'total_consumption_gb': 0,
                    'average_monthly_gb': 0,
                    'total_cycles': 0,
                    'status': 'Erro',
                    'error': str(e)
                }
        
        return consumption_data, cycles
    
    # Obter contexto do admin
    context = get_admin_context(request)
    
    # Verificar se é uma requisição de exportação PDF
    if request.GET.get('export') == 'pdf':
        # Filtros aplicados
        selected_service_lines = request.GET.getlist('service_lines')
        if not selected_service_lines:
            selected_service_lines = available_service_lines
        
        # Buscar dados de consumo
        consumption_data, cycles = get_service_line_consumption_data(selected_service_lines)
        
        # Criar PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.darkblue
        )
        
        # Conteúdo do PDF
        story = []
        
        # Título
        title = Paragraph("Relatório de Consumo Starlink - Ciclos de Faturamento 2025", title_style)
        story.append(title)
        story.append(Spacer(1, 15))
        
        # Data do relatório
        date_text = f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}"
        story.append(Paragraph(date_text, styles['Normal']))
        story.append(Spacer(1, 10))
        
        # Informações sobre ciclos
        cycle_info = f"<b>Período de Faturamento:</b> Dia 03 até dia 02 do mês seguinte | <b>Ciclos:</b> {len(cycles)}"
        story.append(Paragraph(cycle_info, styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Resumo
        total_consumption_all = sum([data['total_consumption_gb'] for data in consumption_data.values()])
        summary_text = f"<b>Resumo:</b> {len(selected_service_lines)} Service Lines | Consumo Total: {total_consumption_all:.2f} GB | Consumo = Priority + Standard"
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Tabela de consumo por service line
        for sl in selected_service_lines:
            try:
                data = consumption_data.get(sl, {})
                location = str(data.get('location', 'N/A')).replace('<', '&lt;').replace('>', '&gt;')
                total_gb = float(data.get('total_consumption_gb', 0))
                avg_gb = float(data.get('average_monthly_gb', 0))
                
                # Cabeçalho da service line (sanitizado)
                sl_clean = str(sl).replace('<', '&lt;').replace('>', '&gt;')
                sl_title = Paragraph(f"<b>{sl_clean} - {location}</b>", styles['Heading3'])
                story.append(sl_title)
                
                # Tabela de consumo por ciclo
                table_data = [['Ciclo', 'Período', 'Priority (GB)', 'Standard (GB)', 'Total (GB)']]
                
                for cycle_data in data.get('monthly_data', []):
                    # Sanitizar e validar dados da tabela
                    cycle_name = str(cycle_data.get('cycle_name', 'N/A')).replace('<', '&lt;').replace('>', '&gt;')
                    cycle_start = str(cycle_data.get('cycle_start', '')).replace('<', '&lt;').replace('>', '&gt;')
                    cycle_end = str(cycle_data.get('cycle_end', '')).replace('<', '&lt;').replace('>', '&gt;')
                    
                    priority_gb = float(cycle_data.get('priority_gb', 0))
                    standard_gb = float(cycle_data.get('standard_gb', 0))
                    total_cycle_gb = float(cycle_data.get('total_gb', 0))
                    
                    table_data.append([
                        cycle_name,
                        f"{cycle_start} - {cycle_end}",
                        f"{priority_gb:.2f}",
                        f"{standard_gb:.2f}",
                        f"{total_cycle_gb:.2f}"
                    ])
                
                # Linha de total
                table_data.append(['TOTAL', f'{len(cycles)} ciclos', '-', '-', f"{total_gb:.2f} GB"])
                table_data.append(['MÉDIA POR CICLO', '-', '-', '-', f"{avg_gb:.2f} GB"])
                
                # Criar tabela
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                    ('BACKGROUND', (0, -2), (-1, -1), colors.lightgrey),
                    ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
                story.append(Spacer(1, 20))
                
            except Exception as table_error:
                # Se houver erro em uma service line específica, pular ela
                error_msg = f"Erro ao processar dados da service line {sl}: {str(table_error)}"
                story.append(Paragraph(f"<b>ERRO:</b> {error_msg}", styles['Normal']))
                story.append(Spacer(1, 20))
        
        # Gerar PDF
        try:
            doc.build(story)
            buffer.seek(0)
            
            # Obter dados do PDF
            pdf_data = buffer.getvalue()
            buffer.close()
            
            # Verificar se PDF foi gerado corretamente
            if not pdf_data or len(pdf_data) < 100:
                return HttpResponse("Erro: PDF vazio ou muito pequeno", status=500)
            
            if not pdf_data.startswith(b'%PDF-'):
                return HttpResponse("Erro: Formato PDF inválido", status=500)
            
            # Criar resposta HTTP com PDF
            response = HttpResponse(
                pdf_data, 
                content_type='application/pdf'
            )
            
            # Headers otimizados para download
            filename = f"relatorio_consumo_starlink_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response['Content-Length'] = str(len(pdf_data))
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
            return response
            
        except Exception as pdf_error:
            return HttpResponse(f"Erro na geração do PDF: {str(pdf_error)}", status=500)
    
    # Para requisições normais (não PDF), renderizar a página
    selected_service_lines = request.GET.getlist('service_lines')
    if not selected_service_lines:
        selected_service_lines = available_service_lines
    
    # Buscar dados de consumo
    consumption_data, cycles = get_service_line_consumption_data(selected_service_lines)
    
    # Preparar dados para a tabela
    filtered_data = []
    total_consumption_all = 0
    
    for sl in selected_service_lines:
        data = consumption_data.get(sl, {})
        total_consumption_all += data.get('total_consumption_gb', 0)
        filtered_data.append({
            'service_line': sl,
            'location': data.get('location', 'N/A'),
            'total_consumption_gb': data.get('total_consumption_gb', 0),
            'average_monthly_gb': data.get('average_monthly_gb', 0),
            'total_cycles': data.get('total_cycles', 0),
            'status': data.get('status', 'N/A'),
            'monthly_data': data.get('monthly_data', [])
        })
    
    # Criar breadcrumbs
    base_breadcrumbs = [
        {'name': 'Início', 'url': '/admin/'},
        {'name': 'Starlink Admin', 'url': '/admin/starlink/'},
        {'name': 'Relatório Consumo', 'url': None}
    ]
    
    # Adicionar contexto específico da view
    context.update({
        'title': 'Relatório de Consumo Starlink - Ciclos de Faturamento 2025',
        'breadcrumbs': base_breadcrumbs,
        'available_service_lines': available_service_lines,
        'service_line_locations': service_line_locations,
        'selected_service_lines': selected_service_lines,
        'filtered_data': filtered_data,
        'consumption_data': consumption_data,
        'cycles': cycles,
        'total_service_lines': len(filtered_data),
        'total_consumption_all': round(total_consumption_all, 2),
        'average_consumption_all': round(total_consumption_all / len(filtered_data), 2) if filtered_data else 0,
        'total_cycles': len(cycles),
    })
    
    return render(request, 'admin/painel/starlink/service_lines_report.html', context)


@staff_member_required
def starlink_service_lines_selection(request):
    """
    Página de seleção de Service Lines para relatório de consumo
    Redireciona para o relatório completo
    """
    # Redirecionar diretamente para o relatório de consumo
    from django.shortcuts import redirect
    return redirect('painel:starlink_service_lines_report')


def generate_billing_cycles():
    """
    Gera uma lista de ciclos de faturamento com formato amigável
    Os ciclos da Starlink vão do dia 03 de um mês até o dia 02 do mês seguinte
    """
    from datetime import datetime, date
    from dateutil.relativedelta import relativedelta
    
    cycles = []
    current_date = datetime.now().date()
    
    # Começar a partir do ciclo atual (ou anterior se estivermos antes do dia 03)
    if current_date.day < 3:
        # Se estivermos antes do dia 03, o ciclo atual ainda é do mês passado
        cycle_start = date(current_date.year, current_date.month - 1, 3) if current_date.month > 1 else date(current_date.year - 1, 12, 3)
    else:
        # Se estivermos no dia 03 ou depois, o ciclo atual é do mês atual
        cycle_start = date(current_date.year, current_date.month, 3)
    
    # Gerar os últimos 12 ciclos (incluindo o atual)
    for i in range(12):
        start_date = cycle_start - relativedelta(months=i)
        end_date = (start_date + relativedelta(months=1)) - relativedelta(days=1)  # Dia 02 do mês seguinte
        
        # Definir o mês de referência (mês do início do ciclo)
        month_names = [
            'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
            'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
        ]
        
        month_names_full = [
            'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
            'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
        ]
        
        month_name = month_names[start_date.month - 1]
        month_name_full = month_names_full[start_date.month - 1]
        end_month_name_full = month_names_full[end_date.month - 1]
        year = start_date.year
        
        # Formatar as datas para exibição
        start_str = f"{start_date.day:02d} de {month_name_full}"
        end_str = f"{end_date.day:02d} de {end_month_name_full}"
        
        cycles.append({
            'value': f"{start_date.isoformat()}|{end_date.isoformat()}",  # Valor para o formulário
            'label': f"{month_name}/{year}",  # Label principal
            'description': f"ciclo de {start_str} à {end_str}",  # Descrição detalhada
            'start_date': start_date,
            'end_date': end_date,
            'is_current': i == 0  # O primeiro ciclo é o atual
        })
    
    return cycles


@staff_member_required
def starlink_availability_selection(request):
    """
    Página de seleção de Service Lines para relatório de disponibilidade
    """
    # Obter a conta selecionada da URL
    selected_account = request.GET.get('account_id', DEFAULT_ACCOUNT)
    
    # Verificar se a conta é válida
    available_accounts = get_available_accounts()
    if selected_account not in available_accounts:
        selected_account = DEFAULT_ACCOUNT

    # Obter contexto do admin
    context = get_admin_context(request)
    
    # Adicionar contexto das contas
    context.update(get_account_context(request))
    
    # Criar breadcrumbs
    base_breadcrumbs = [
        {'name': 'Início', 'url': '/admin/'},
        {'name': 'Starlink Admin', 'url': '/admin/starlink/'},
        {'name': 'Relatório Disponibilidade', 'url': None}
    ]
    
    # Inicializar variáveis
    available_service_lines = []
    service_line_locations = {}
    total_service_lines = 0
    error_message = None
    
    try:
        # Obter todas as service lines da conta selecionada usando a API
        print(f"🔍 Obtendo service lines para conta: {selected_account}")
        result = get_service_lines_with_location(selected_account)
        
        if "error" in result:
            error_message = result["error"]
            messages.error(request, f'Erro ao consultar Service Lines: {result["error"]}')
        else:
            service_lines_data = result.get("service_lines", [])
            
            # Processar os dados para o formato esperado pelo template
            for service_line in service_lines_data:
                service_line_number = service_line.get("serviceLineNumber")
                if service_line_number:
                    available_service_lines.append(service_line_number)
                    service_line_locations[service_line_number] = service_line.get("serviceLocation", "Localização não informada")
            
            total_service_lines = len(available_service_lines)
            
            # Adicionar mensagem de sucesso
            messages.success(request, f'{total_service_lines} Service Lines encontradas para a conta {available_accounts[selected_account]["name"]}!')
            
            print(f"✅ {total_service_lines} service lines processadas com sucesso")
    
    except Exception as e:
        error_message = str(e)
        messages.error(request, f'Erro ao consultar Service Lines: {str(e)}')
        print(f"❌ Erro ao obter service lines: {str(e)}")
    
    # Adicionar contexto específico da view
    context.update({
        'title': 'Relatório de Disponibilidade - Seleção de Service Lines',
        'breadcrumbs': get_breadcrumbs_with_account(base_breadcrumbs, selected_account),
        'available_service_lines': available_service_lines,
        'service_line_locations': service_line_locations,
        'total_service_lines': total_service_lines,
        'selected_account': selected_account,
        'error_message': error_message,
        'billing_cycles': generate_billing_cycles(),  # Adicionar os ciclos de faturamento
    })
    
    return render(request, 'admin/painel/starlink/availability_selection.html', context)


# @staff_member_required  # Temporarily disabled for debugging
def starlink_availability_report(request):
    """
    Relatório de disponibilidade das Service Lines com tráfego e telemetria
    """
    # from django.http import HttpResponse
    # from reportlab.pdfgen import canvas
    # from reportlab.lib.pagesizes import letter, A4
    # from reportlab.lib import colors
    # from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    # from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    # from reportlab.lib.units import inch
    # from io import BytesIO
    # import calendar

    # Obter parâmetros da requisição
    selected_service_lines = request.GET.getlist('service_lines')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    if not selected_service_lines:
        # Redirecionar para seleção se não há service lines
        messages.error(request, 'Selecione pelo menos uma Service Line para gerar o relatório.')
        return redirect('painel:starlink_availability_selection')
    
    # Função para gerar dados de ciclo baseados nas datas
    def generate_cycle_data(start_date_str, end_date_str):
        if not start_date_str or not end_date_str:
            # Se não há datas, usar ciclo atual
            current_date = datetime.now()
            cycle_start = datetime(current_date.year, current_date.month, 3)
            if current_date.day < 3:
                # Se estamos antes do dia 3, usar mês anterior
                if current_date.month == 1:
                    cycle_start = datetime(current_date.year - 1, 12, 3)
                else:
                    cycle_start = datetime(current_date.year, current_date.month - 1, 3)
            
            start_date_str = cycle_start.strftime("%d/%m/%Y")
            if cycle_start.month == 12:
                cycle_end = datetime(cycle_start.year + 1, 1, 2)
            else:
                cycle_end = datetime(cycle_start.year, cycle_start.month + 1, 2)
            end_date_str = cycle_end.strftime("%d/%m/%Y")
        
        # Buscar dados de disponibilidade (telemetria)
        availability_data = get_availability_report_data(selected_service_lines, start_date_str, end_date_str)
        
        # Buscar dados de consumo (billing)
        consumption_data = get_usage_report_data(account_id="ACC-2744134-64041-5", 
                                                cycle_start=start_date_str, 
                                                cycle_end=end_date_str)
        
        # Combinar dados de disponibilidade e consumo
        combined_data = {}
        for sl in selected_service_lines:
            # Dados de disponibilidade
            avail_info = availability_data.get(sl, {})
            
            # Dados de consumo - procurar no array usage_data
            consumption_info = {}
            if consumption_data.get('success') and 'usage_data' in consumption_data:
                for usage_line in consumption_data['usage_data']:
                    if usage_line.get('serviceLineNumber') == sl:
                        consumption_info = {
                            'priority_gb': usage_line.get('priorityGB', 0),  # Já em GB
                            'standard_gb': usage_line.get('standardGB', 0),  # Já em GB
                            'total_gb': usage_line.get('totalGB', 0),  # Já em GB
                        }
                        break
            
            # Combinar
            combined_data[sl] = {
                **avail_info,  # availability data
                **consumption_info  # consumption data
            }

        return combined_data, start_date_str, end_date_str    # Verificar se é requisição para PDF
    if request.GET.get('pdf') == '1':
        # Gerar PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Center
        )
        
        # Função para gerar dados de ciclo baseados nas datas
        if not start_date or not end_date:
            # Se não há datas, usar ciclo atual
            current_date = datetime.now()
            cycle_start = datetime(current_date.year, current_date.month, 3)
            if current_date.day < 3:
                # Se estamos antes do dia 3, usar mês anterior
                if current_date.month == 1:
                    cycle_start = datetime(current_date.year - 1, 12, 3)
                else:
                    cycle_start = datetime(current_date.year, current_date.month - 1, 3)
            
            start_date_str = cycle_start.strftime("%d/%m/%Y")
            if cycle_start.month == 12:
                cycle_end = datetime(cycle_start.year + 1, 1, 2)
            else:
                cycle_end = datetime(cycle_start.year, cycle_start.month + 1, 2)
            end_date_str = cycle_end.strftime("%d/%m/%Y")
        
        # Buscar dados de disponibilidade (telemetria)
        availability_data = get_availability_report_data(selected_service_lines, start_date_str, end_date_str)
        
        # Buscar dados de consumo (billing)
        consumption_data = get_usage_report_data(account_id="ACC-2744134-64041-5", 
                                                cycle_start=start_date_str, 
                                                cycle_end=end_date_str)
        
        # Combinar dados de disponibilidade e consumo
        combined_data = {}
        for sl in selected_service_lines:
            # Dados de disponibilidade
            avail_info = availability_data.get(sl, {})
            
            # Dados de consumo - procurar no array usage_data
            consumption_info = {}
            if consumption_data.get('success') and 'usage_data' in consumption_data:
                for usage_line in consumption_data['usage_data']:
                    if usage_line.get('serviceLineNumber') == sl:
                        consumption_info = {
                            'priority_gb': usage_line.get('priorityGB', 0),  # Já em GB
                            'standard_gb': usage_line.get('standardGB', 0),  # Já em GB
                            'total_gb': usage_line.get('totalGB', 0),  # Já em GB
                        }
                        break
            
            # Combinar
            combined_data[sl] = {
                **avail_info,  # availability data
                **consumption_info  # consumption data
            }
        
        # Conteúdo do PDF
        story = []
        
        # Título
        title = Paragraph("Relatório de Disponibilidade Starlink", title_style)
        story.append(title)
        story.append(Spacer(1, 15))
        
        # Data do relatório
        date_text = f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}"
        story.append(Paragraph(date_text, styles['Normal']))
        
        # Período
        period_text = f"<b>Período:</b> {cycle_start} - {cycle_end} (Ciclo Starlink: dia 03 - dia 02)"
        story.append(Paragraph(period_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Tabela principal
        table_data = [['Service Line', 'Localização', 'Uptime %', 'Downtime (h)', 'Obstrução (h)', 'Status']]
        
        for sl in selected_service_lines:
            data = combined_data.get(sl, {})
            table_data.append([
                sl,
                data.get('location', 'N/A'),
                f"{data.get('uptime_percentage', 0):.2f}%",
                f"{data.get('downtime_hours', 0):.2f}",
                f"{data.get('obstruction_hours', 0):.2f}",
                data.get('availability_status', 'N/A')
            ])
        
        # Adicionar linha de totais
        table_data.append(['TOTAL/MÉDIA', '', '', '', '', ''])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 30))
        
        # Observações
        notes = [
            "• Uptime: Percentual de tempo que o serviço esteve disponível",
            "• Downtime: Horas de indisponibilidade do serviço",
            "• Obstrução: Horas de obstrução do sinal satellite",
            "• Dados obtidos via API Starlink Telemetry",
            "• Ciclo de faturamento: 03 do mês até 02 do mês seguinte"
        ]
        
        for note in notes:
            story.append(Paragraph(note, styles['Normal']))
        
        # Gerar PDF
        doc.build(story)
        buffer.seek(0)
        
        # Retornar resposta HTTP com PDF
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="relatorio_disponibilidade_starlink_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        return response
    
    # Para requisições normais (não PDF), renderizar a página
    # Gerar dados
    report_data, cycle_start, cycle_end = generate_cycle_data(start_date, end_date)
    
    # Obter status detalhado para as service lines selecionadas
    try:
        # Extrair apenas os números das service lines (sem SL- prefix)
        sl_numbers = []
        for sl in selected_service_lines:
            if sl.startswith('SL-'):
                # Extrair o número do meio (formato SL-XXXXXX-XXXXX-XX)
                parts = sl.split('-')
                if len(parts) >= 2:
                    sl_numbers.append(parts[1])
            else:
                sl_numbers.append(sl)
        
        status_data = get_enhanced_service_line_status(sl_numbers, include_telemetry=False)
        print(f"📊 Status obtido para {len(status_data)} service lines")
    except Exception as e:
        print(f"⚠️ Erro ao obter status: {e}")
        status_data = {}
    
    # Preparar dados para exibição
    filtered_data = []
    total_uptime = 0
    total_downtime = 0
    total_obstruction = 0
    total_consumption = 0
    total_usage_percentage = 0
    
    for sl in selected_service_lines:
        data = report_data.get(sl, {})
        uptime = data.get('uptime_percentage', 0)
        downtime = data.get('downtime_hours', 0)
        obstruction = data.get('obstruction_hours', 0)
        total_gb = data.get('total_gb', 0)
        usage_percentage = data.get('usage_percentage', 0)
        
        total_uptime += uptime
        total_downtime += downtime
        total_obstruction += obstruction
        total_consumption += total_gb
        total_usage_percentage += usage_percentage
        
        # Obter status para esta service line
        status_info = None
        if sl.startswith('SL-'):
            parts = sl.split('-')
            if len(parts) >= 2:
                sl_number = parts[1]
                status_info = status_data.get(sl_number)
        
        filtered_data.append({
            'service_line': sl,
            'location': data.get('location', 'N/A'),
            'uptime_percentage': uptime,
            'downtime_hours': downtime,
            'obstruction_hours': obstruction,
            'availability_status': data.get('availability_status', 'N/A'),
            'priority_gb': data.get('priority_gb', 0),
            'standard_gb': data.get('standard_gb', 0),
            'total_gb': total_gb,
            'usage_percentage': usage_percentage,
            'usage_threshold': data.get('usage_threshold', 'normal'),
            'status_info': status_info  # Adicionar informação de status
        })
    
    # Calcular médias
    num_lines = len(selected_service_lines) if selected_service_lines else 1
    avg_uptime = total_uptime / num_lines
    avg_downtime = total_downtime / num_lines
    avg_obstruction = total_obstruction / num_lines
    avg_consumption = total_consumption / num_lines
    avg_usage_percentage = total_usage_percentage / num_lines
    
    # Obter contexto do admin
    context = get_admin_context(request)
    
    # Criar breadcrumbs
    base_breadcrumbs = [
        {'name': 'Início', 'url': '/admin/'},
        {'name': 'Starlink Admin', 'url': '/admin/starlink/'},
        {'name': 'Seleção Service Lines', 'url': reverse('painel:starlink_availability_selection')},
        {'name': 'Relatório Disponibilidade', 'url': None}
    ]
    
    # Adicionar contexto específico da view
    context.update({
        'title': 'Relatório Completo de Service Lines',
        'breadcrumbs': base_breadcrumbs,
        'selected_service_lines': selected_service_lines,
        'filtered_data': filtered_data,
        'cycle_start': cycle_start,
        'cycle_end': cycle_end,
        'total_service_lines': len(selected_service_lines),
        'avg_uptime': round(avg_uptime, 2),
        'avg_downtime': round(avg_downtime, 2),
        'avg_obstruction': round(avg_obstruction, 2),
        'avg_consumption': round(avg_consumption, 2),
        'avg_usage_percentage': round(avg_usage_percentage, 2),
        'total_uptime': round(total_uptime, 2),
        'total_downtime': round(total_downtime, 2),
        'total_obstruction': round(total_obstruction, 2),
        'total_consumption': round(total_consumption, 2),
    })
    
    return render(request, 'admin/painel/starlink/availability_report.html', context)


def test_pdf_simple(request):
    """View de teste para geração de PDF simples"""
    try:
        # Criar buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Conteúdo simples
        story = []
        story.append(Paragraph("TESTE - Relatório PDF", styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Este é um teste de geração de PDF.", styles['Normal']))
        story.append(Paragraph("Se você conseguir visualizar este arquivo, o sistema está funcionando.", styles['Normal']))
        
        # Gerar PDF
        doc.build(story)
        buffer.seek(0)
        
        # Obter dados do PDF
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # Verificar se PDF foi gerado corretamente
        if not pdf_data or len(pdf_data) < 100:
            return HttpResponse("Erro: PDF vazio ou muito pequeno", status=500)
        
        if not pdf_data.startswith(b'%PDF-'):
            return HttpResponse("Erro: Formato PDF inválido", status=500)
        
        # Criar resposta HTTP com PDF
        response = HttpResponse(pdf_data, content_type='application/pdf')
        
        # Headers para forçar download
        filename = f"teste_pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = str(len(pdf_data))
        
        return response
        
    except Exception as e:
        return HttpResponse(f"Erro na geração do PDF: {str(e)}", status=500)


def debug_availability_report(request):
    """
    View simples para debug dos dados de billing
    """
    from django.http import HttpResponse
    import json
    
    account_id = request.GET.get('account_id', 'ACC-2744134-64041-5')
    
    # Testar apenas a função que está com problema
    try:
        result = get_usage_report_data(account_id)
        
        # Retornar JSON para debug
        return HttpResponse(
            json.dumps(result, indent=2, default=str),
            content_type='application/json'
        )
    except Exception as e:
        import traceback
        error_info = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return HttpResponse(
            json.dumps(error_info, indent=2),
            content_type='application/json',
            status=500
        )
    
    # Obter parâmetros da requisição
    selected_service_lines = request.GET.getlist('service_lines')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    if not selected_service_lines:
        # Redirecionar para seleção se não há service lines
        messages.error(request, 'Selecione pelo menos uma Service Line para gerar o relatório.')
        return redirect('painel:starlink_availability_selection')
    
    # Função para gerar dados de ciclo baseados nas datas
    def generate_cycle_data(start_date_str, end_date_str):
        if not start_date_str or not end_date_str:
            # Se não há datas, usar ciclo atual
            current_date = datetime.now()
            cycle_start = datetime(current_date.year, current_date.month, 3)
            if current_date.day < 3:
                # Se estamos antes do dia 3, usar mês anterior
                if current_date.month == 1:
                    cycle_start = datetime(current_date.year - 1, 12, 3)
                else:
                    cycle_start = datetime(current_date.year, current_date.month - 1, 3)
            
            start_date_str = cycle_start.strftime("%d/%m/%Y")
            if cycle_start.month == 12:
                cycle_end = datetime(cycle_start.year + 1, 1, 2)
            else:
                cycle_end = datetime(cycle_start.year, cycle_start.month + 1, 2)
            end_date_str = cycle_end.strftime("%d/%m/%Y")
        
        # Buscar dados de disponibilidade (telemetria)
        availability_data = get_availability_report_data(selected_service_lines, start_date_str, end_date_str)
        
        # Buscar dados de consumo (billing)
        consumption_data = get_usage_report_data(account_id="ACC-2744134-64041-5", 
                                                cycle_start=start_date_str, 
                                                cycle_end=end_date_str)
        
        # Combinar dados de disponibilidade e consumo
        combined_data = {}
        for sl in selected_service_lines:
            # Dados de disponibilidade
            avail_data = availability_data.get(sl, {})
            
            # Dados de consumo - encontrar na lista de usage_data
            consumption_info = None
            if consumption_data.get("success") and consumption_data.get("usage_data"):
                for usage_item in consumption_data["usage_data"]:
                    if usage_item.get("serviceLineNumber") == sl:
                        consumption_info = usage_item
                        break
            
            combined_data[sl] = {
                "service_line": sl,
                "location": avail_data.get("location", get_service_line_location(sl)),
                # Dados de disponibilidade
                "uptime_percentage": avail_data.get("uptime_percentage", 0),
                "downtime_hours": avail_data.get("downtime_hours", 0),
                "obstruction_hours": avail_data.get("obstruction_hours", 0),
                "availability_status": avail_data.get("availability_status", "N/A"),
                # Dados de consumo
                "priority_gb": consumption_info.get("priorityGB", 0) if consumption_info else 0,
                "standard_gb": consumption_info.get("standardGB", 0) if consumption_info else 0,
                "total_gb": consumption_info.get("totalGB", 0) if consumption_info else 0,
                "usage_percentage": consumption_info.get("usagePercentage", 0) if consumption_info else 0,
                "usage_threshold": consumption_info.get("threshold", "normal") if consumption_info else "normal"
            }
        
        return combined_data, start_date_str, end_date_str
    
    # Verificar se é uma requisição de exportação PDF
    if request.GET.get('export') == 'pdf':
        # Verificar se reportlab está disponível para PDF
        if not REPORTLAB_AVAILABLE:
            messages.error(request, 'A biblioteca reportlab não está instalada. Instale com: pip install reportlab')
            return redirect('painel:starlink_availability_selection')
            
        # Gerar dados
        report_data, cycle_start, cycle_end = generate_cycle_data(start_date, end_date)
        
        # Criar PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.darkblue
        )
        
        # Conteúdo do PDF
        story = []
        
        # Título
        title = Paragraph("Relatório de Disponibilidade Starlink", title_style)
        story.append(title)
        story.append(Spacer(1, 15))
        
        # Data do relatório
        date_text = f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}"
        story.append(Paragraph(date_text, styles['Normal']))
        
        # Período
        period_text = f"<b>Período:</b> {cycle_start} - {cycle_end} (Ciclo Starlink: dia 03 - dia 02)"
        story.append(Paragraph(period_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Tabela principal
        table_data = [['Service Line', 'Localização', 'Uptime %', 'Downtime (h)', 'Obstrução (h)', 'Status']]
        
        total_uptime = 0
        total_downtime = 0
        total_obstruction = 0
        
        for sl in selected_service_lines:
            data = report_data.get(sl, {})
            uptime = data.get('uptime_percentage', 0)
            downtime = data.get('downtime_hours', 0)
            obstruction = data.get('obstruction_hours', 0)
            
            total_uptime += uptime
            total_downtime += downtime
            total_obstruction += obstruction
            
            table_data.append([
                sl,
                data.get('location', 'N/A'),
                f"{uptime}%",
                f"{downtime}h",
                f"{obstruction}h",
                data.get('availability_status', 'N/A')
            ])
        
        # Adicionar totais
        avg_uptime = total_uptime / len(selected_service_lines) if selected_service_lines else 0
        table_data.append([
            'MÉDIAS', 
            f'{len(selected_service_lines)} Service Lines',
            f"{avg_uptime:.2f}%",
            f"{total_downtime:.2f}h",
            f"{total_obstruction:.2f}h",
            "Consolidado"
        ])
        
        # Criar tabela
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 30))
        
        # Observações
        notes = [
            "• Uptime: Percentual de tempo que o serviço esteve disponível",
            "• Downtime: Horas de indisponibilidade do serviço",
            "• Obstrução: Horas de obstrução do sinal satellite",
            "• Dados obtidos via API Starlink Telemetry",
            "• Ciclo de faturamento: 03 do mês até 02 do mês seguinte"
        ]
        
        for note in notes:
            story.append(Paragraph(note, styles['Normal']))
        
        # Gerar PDF
        doc.build(story)
        buffer.seek(0)
        
        # Retornar resposta HTTP com PDF
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="relatorio_disponibilidade_starlink_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        return response
    
    # Para requisições normais (não PDF), renderizar a página
    # Gerar dados
    report_data, cycle_start, cycle_end = generate_cycle_data(start_date, end_date)
    
    # Preparar dados para exibição
    filtered_data = []
    total_uptime = 0
    total_downtime = 0
    total_obstruction = 0
    total_consumption = 0
    total_usage_percentage = 0
    
    for sl in selected_service_lines:
        data = report_data.get(sl, {})
        uptime = data.get('uptime_percentage', 0)
        downtime = data.get('downtime_hours', 0)
        obstruction = data.get('obstruction_hours', 0)
        total_gb = data.get('total_gb', 0)
        usage_percentage = data.get('usage_percentage', 0)
        
        total_uptime += uptime
        total_downtime += downtime
        total_obstruction += obstruction
        total_consumption += total_gb
        total_usage_percentage += usage_percentage
        
        filtered_data.append({
            'service_line': sl,
            'location': data.get('location', 'N/A'),
            'uptime_percentage': uptime,
            'downtime_hours': downtime,
            'obstruction_hours': obstruction,
            'availability_status': data.get('availability_status', 'N/A'),
            'priority_gb': data.get('priority_gb', 0),
            'standard_gb': data.get('standard_gb', 0),
            'total_gb': total_gb,
            'usage_percentage': usage_percentage,
            'usage_threshold': data.get('usage_threshold', 'normal')
        })
    
    # Calcular médias
    num_lines = len(selected_service_lines) if selected_service_lines else 1
    avg_uptime = total_uptime / num_lines
    avg_downtime = total_downtime / num_lines
    avg_obstruction = total_obstruction / num_lines
    avg_consumption = total_consumption / num_lines
    avg_usage_percentage = total_usage_percentage / num_lines
    
    # Obter contexto do admin
    context = get_admin_context(request)
    
    # Criar breadcrumbs
    base_breadcrumbs = [
        {'name': 'Início', 'url': '/admin/'},
        {'name': 'Starlink Admin', 'url': '/admin/starlink/'},
        {'name': 'Seleção Service Lines', 'url': reverse('painel:starlink_availability_selection')},
        {'name': 'Relatório Disponibilidade', 'url': None}
    ]
    
    # Adicionar contexto específico da view
    context.update({
        'title': 'Relatório Completo de Service Lines',
        'breadcrumbs': base_breadcrumbs,
        'selected_service_lines': selected_service_lines,
        'filtered_data': filtered_data,
        'cycle_start': cycle_start,
        'cycle_end': cycle_end,
        'total_service_lines': len(selected_service_lines),
        'avg_uptime': round(avg_uptime, 2),
        'avg_downtime': round(avg_downtime, 2),
        'avg_obstruction': round(avg_obstruction, 2),
        'avg_consumption': round(avg_consumption, 2),
        'avg_usage_percentage': round(avg_usage_percentage, 2),
        'total_uptime': round(total_uptime, 2),
        'total_downtime': round(total_downtime, 2),
        'total_obstruction': round(total_obstruction, 2),
        'total_consumption': round(total_consumption, 2),
    })
    
    return render(request, 'admin/painel/starlink/availability_report.html', context)
