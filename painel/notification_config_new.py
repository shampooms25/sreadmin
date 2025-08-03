"""
Sistema de notificações para uploads de vídeos
Configurações para email e telegram
"""

# Configurações de Email
EMAIL_CONFIG = {
    'SMTP_HOST': 'smtp.gmail.com',  # Ajuste conforme seu provedor
    'SMTP_PORT': 587,
    'EMAIL_USER': '',  # Configure com email do sistema
    'EMAIL_PASSWORD': '',  # Configure com senha/app password
    'FROM_EMAIL': 'sistema@poppnet.com.br',
    'TO_EMAILS': [
        'luiz.fernando@fibernetworks.com.br',
        'h.junior@poppnet.com.br'
    ]
}

# Configurações do Telegram
TELEGRAM_CONFIG = {
    'BOT_TOKEN': '7790828605:AAF8zDTX_6F04T7Xishv5roNdbmaky3WLPI',
    'CHAT_ID': '-4684906685'
}

# Configurações do ZIP
ZIP_CONFIG = {
    'ZIP_FILENAME': 'src.zip',
    'PROJECT_ROOT': 'src',
    'VIDEOS_PATH': 'src/assets/videos',
    'BACKUP_DIR': 'backups/zip_backups'
}
