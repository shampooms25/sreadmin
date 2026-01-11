from django.urls import path

from .api_views import prefixes, prefixes_grouped, health

app_name = 'starlink_allowlist'

urlpatterns = [
    path('health/', health, name='health'),
    path('prefixes/', prefixes, name='prefixes'),
    path('prefixes_grouped/', prefixes_grouped, name='prefixes_grouped'),
]
