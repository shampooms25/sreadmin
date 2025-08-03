"""
Configurações específicas para produção - Ubuntu 24
Adicione estas configurações ao seu settings.py ou crie um settings_production.py
"""

import os
from pathlib import Path

# Diretório base do projeto em produção
BASE_DIR = '/var/www/sreadmin'

# Debug deve ser False em produção
DEBUG = False

# Hosts permitidos
ALLOWED_HOSTS = [
    'paineleld.poppnet.com.br',
    '200.115.107.79',
    'localhost',
    '127.0.0.1'
]

# Configurações de media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configurações de arquivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configurações de logging para debug
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/www/sreadmin/django_errors.log',
        },
        'upload_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/www/sreadmin/upload_debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'painel.models': {
            'handlers': ['upload_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Configurações de segurança para produção
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Configuração do banco de dados para produção
# (ajuste conforme sua configuração)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sreadmin_db',
        'USER': 'sreadmin_user',
        'PASSWORD': 'sua_senha_aqui',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Configurações de email para notificações em produção
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # ou seu servidor SMTP
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu_email@dominio.com'
EMAIL_HOST_PASSWORD = 'sua_senha_email'
DEFAULT_FROM_EMAIL = 'noreply@paineleld.poppnet.com.br'

# Configurações de cache para produção
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Configurações de sessão
SESSION_COOKIE_SECURE = True  # Apenas HTTPS
CSRF_COOKIE_SECURE = True     # Apenas HTTPS

print(f"🔧 Configurações de produção carregadas:")
print(f"   BASE_DIR: {BASE_DIR}")
print(f"   MEDIA_ROOT: {MEDIA_ROOT}")
print(f"   DEBUG: {DEBUG}")
