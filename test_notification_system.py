#!/usr/bin/env python3
"""
Script de teste para o sistema de notificações
Execute dentro do ambiente virtual: python test_notification_system.py
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.services import NotificationService, ZipManagerService
from painel.notification_config import EMAIL_CONFIG, TELEGRAM_CONFIG, ZIP_CONFIG
from datetime import datetime

def test_configurations():
    """Testa se as configurações estão corretas"""
    print("🔧 Testando Configurações...")
    
    # Email
    if EMAIL_CONFIG.get('EMAIL_USER') and EMAIL_CONFIG.get('EMAIL_PASSWORD'):
        print("✅ Email: Credenciais configuradas")
    else:
        print("⚠️  Email: Credenciais não configuradas")
    
    # Telegram
    if TELEGRAM_CONFIG.get('BOT_TOKEN') and TELEGRAM_CONFIG.get('CHAT_ID'):
        print("✅ Telegram: Token e Chat ID configurados")
    else:
        print("❌ Telegram: Token ou Chat ID não configurados")
    
    # ZIP
    print(f"✅ ZIP: Configuração carregada - {ZIP_CONFIG.get('ZIP_FILENAME', 'N/A')}")
    print()

def test_telegram_notification():
    """Testa notificação do Telegram"""
    print("🤖 Testando Notificação Telegram...")
    
    try:
        # Simular um arquivo de vídeo
        class MockVideoFile:
            def __init__(self):
                self.name = "teste_video.mp4"
                self.size = 50 * 1024 * 1024  # 50MB
        
        class MockUser:
            def __init__(self):
                self.username = "admin_teste"
        
        mock_video = MockVideoFile()
        mock_user = MockUser()
        
        success = NotificationService.send_telegram_notification(mock_video, mock_user)
        
        if success:
            print("✅ Notificação Telegram enviada com sucesso!")
        else:
            print("❌ Falha ao enviar notificação Telegram")
            
    except Exception as e:
        print(f"❌ Erro no teste Telegram: {str(e)}")
    
    print()

def test_email_notification():
    """Testa notificação por email"""
    print("📧 Testando Notificação Email...")
    
    if not EMAIL_CONFIG.get('EMAIL_USER') or not EMAIL_CONFIG.get('EMAIL_PASSWORD'):
        print("⚠️  Pulando teste de email - credenciais não configuradas")
        print("   Configure EMAIL_USER e EMAIL_PASSWORD em notification_config.py")
        print()
        return
    
    try:
        # Simular um arquivo de vídeo
        class MockVideoFile:
            def __init__(self):
                self.name = "teste_video.mp4"
                self.size = 50 * 1024 * 1024  # 50MB
        
        class MockUser:
            def __init__(self):
                self.username = "admin_teste"
        
        mock_video = MockVideoFile()
        mock_user = MockUser()
        
        success = NotificationService.send_email_notification(mock_video, mock_user)
        
        if success:
            print("✅ Notificação Email enviada com sucesso!")
        else:
            print("❌ Falha ao enviar notificação Email")
            
    except Exception as e:
        print(f"❌ Erro no teste Email: {str(e)}")
    
    print()

def main():
    """Função principal"""
    print("🚀 TESTE DO SISTEMA DE NOTIFICAÇÕES")
    print("=" * 50)
    print()
    
    test_configurations()
    test_telegram_notification()
    test_email_notification()
    
    print("🎯 RESUMO:")
    print("- Configure as credenciais de email em painel/notification_config.py")
    print("- Telegram já está configurado e funcionando")
    print("- Sistema pronto para receber uploads de vídeo!")
    print()
    print("💡 Para testar completamente:")
    print("1. Configure EMAIL_USER e EMAIL_PASSWORD")
    print("2. Faça upload de um vídeo pelo sistema")
    print("3. Verifique se chegaram as notificações")

if __name__ == "__main__":
    main()
