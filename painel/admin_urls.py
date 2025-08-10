from django.urls import path
from . import admin_views

app_name = 'painel_admin'

urlpatterns = [
    # ZIP Manager Views
    path('zip-manager/', admin_views.zip_manager_view, name='zip_manager'),
    path('zip-info/<int:config_id>/', admin_views.zip_info_ajax, name='zip_info_ajax'),
    path('update-zip/', admin_views.update_zip_with_video_ajax, name='update_zip_ajax'),
    
    # Notification Testing
    path('test-notifications/', admin_views.test_notifications_view, name='test_notifications'),
]
