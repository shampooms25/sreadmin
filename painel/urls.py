from django.urls import path
from . import views

app_name = 'painel'

urlpatterns = [
    # URLs da Starlink - Nova estrutura
    path('starlink/', views.starlink_main, name='starlink_main'),  # Página principal com 2 cards
    path('starlink/dashboard/', views.starlink_dashboard, name='starlink_dashboard'),  # Dashboard atual
    path('starlink/admin/', views.starlink_admin, name='starlink_admin'),  # Administração das contas
    path('starlink/auto-recharge/', views.starlink_auto_recharge_management, name='starlink_auto_recharge_management'),  # Gerenciar recarga automática
    path('starlink/disable-auto-recharge/', views.starlink_disable_auto_recharge, name='starlink_disable_auto_recharge'),  # Desativar recarga automática
    path('starlink/toggle-auto-recharge/', views.starlink_toggle_auto_recharge, name='starlink_toggle_auto_recharge'),  # Ativar/desativar recarga
    path('starlink/service-lines/', views.starlink_service_lines, name='starlink_service_lines'),
    path('starlink/billing-report/', views.starlink_billing_report, name='starlink_billing_report'),
    path('starlink/detailed-report/', views.starlink_detailed_report, name='starlink_detailed_report'),
    path('starlink/usage-report/', views.starlink_usage_report, name='starlink_usage_report'),
    path('starlink/api-status/', views.starlink_api_status, name='starlink_api_status'),
    path('starlink/debug-api/', views.starlink_debug_api, name='starlink_debug_api'),  # Debug temporário
]
