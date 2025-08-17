from django.urls import path
from . import admin_views
from .portal_views import portal_sem_video_download

app_name = 'painel_admin'

urlpatterns = [
    # ZIP Manager Views
    path('zip-manager/', admin_views.zip_manager_view, name='zip_manager'),
    path('zip-info/<int:config_id>/', admin_views.zip_info_ajax, name='zip_info_ajax'),
    path('update-zip/', admin_views.update_zip_with_video_ajax, name='update_zip_ajax'),
    # Portal sem Vídeo - Download (espelhado sob /admin para evitar 404 no proxy)
    path('portal-sem-video/<int:portal_id>/download/', portal_sem_video_download, name='portal_sem_video_download_admin'),
    
    # Notification Testing
    path('test-notifications/', admin_views.test_notifications_view, name='test_notifications'),
]
