from django.urls import path

from .api_views import prefixes, health

app_name = 'starlink_allowlist'

urlpatterns = [
    path('health/', health, name='health'),
    path('prefixes/', prefixes, name='prefixes'),
]
