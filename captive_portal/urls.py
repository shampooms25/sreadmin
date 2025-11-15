"""
URLs para API do portal captive
Rotas para integração com Appliances POPPFIRE
"""
from django.urls import path
from .api_views import (
    portal_status,
    portal_download, 
    portal_update_status,
    api_info,
    captive_portal_success
)
from .setup_views import setup_appliance_tokens, check_appliance_tokens

app_name = 'captive_portal_api'

urlpatterns = [
    # Informações da API
    path('appliances/info/', api_info, name='api_info'),
    
    # Status do portal
    path('appliances/portal/status/', portal_status, name='portal_status'),
    
    # Download do portal
    path('appliances/portal/download/', portal_download, name='portal_download'),
    
    # Status de atualização dos appliances
    path('appliances/portal/update-status/', portal_update_status, name='update_status'),
    
    # Registro de visualizações de vídeos (público, sem autenticação)
    path('captive-portal/success/', captive_portal_success, name='captive_portal_success'),
    
    # URLs de setup (temporárias)
    path('setup/tokens/', setup_appliance_tokens, name='setup_tokens'),
    path('setup/check/', check_appliance_tokens, name='check_tokens'),
]
