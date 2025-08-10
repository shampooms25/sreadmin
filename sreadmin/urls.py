from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=False), name='home'),
    path('admin/painel/', include('painel.admin_urls', namespace='painel_admin')),  # URLs administrativas do painel
    path('admin/', admin.site.urls),  # Django admin depois das customizadas
    path('starlink/', include('painel.urls')),  # URLs do painel Starlink
    # API para integração com Appliances POPPFIRE
    path('api/', include('captive_portal.urls')),
    # path('adminlte/', include('adminlte4.urls')), # REMOVA ou COMENTE esta linha
]

# Servir arquivos estáticos e de mídia durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)