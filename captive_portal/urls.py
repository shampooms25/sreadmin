"""
URLs para API do portal captive
Rotas para integração com OpenSense
"""
from django.urls import path
from .api_views import (
    CaptivePortalAPIView,
    VideoDownloadAPIView, 
    PortalZipDownloadAPIView,
    StatusAPIView
)

app_name = 'captive_portal_api'

urlpatterns = [
    # Status do servidor
    path('status/', StatusAPIView.as_view(), name='status'),
    
    # Configuração do portal captive
    path('config/', CaptivePortalAPIView.as_view(), name='config'),
    
    # Downloads
    path('download/video/<int:video_id>/', VideoDownloadAPIView.as_view(), name='download_video'),
    path('download/zip/<int:config_id>/', PortalZipDownloadAPIView.as_view(), name='download_zip'),
]
