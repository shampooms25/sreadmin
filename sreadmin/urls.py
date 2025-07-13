from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', include('painel.urls')),  # URLs do painel primeiro
    path('admin/', admin.site.urls),
    # path('adminlte/', include('adminlte4.urls')), # REMOVA ou COMENTE esta linha
]

# Servir arquivos estáticos durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)