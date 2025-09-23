"""
Serviços de notificação para uploads de vídeos
"""
import smtplib
try:
    import requests
except ImportError:
    requests = None
import os
import zipfile
import shutil
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from django.core.mail import send_mail
from .notification_config import EMAIL_CONFIG, TELEGRAM_CONFIG, ZIP_CONFIG
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """Serviço para envio de notificações de upload de vídeos"""
    
    @staticmethod
    def send_email_notification(video_file, user=None):
        """Envia notificação por email sobre upload de vídeo"""
        try:
            subject = "🎥 Novo vídeo enviado para o Portal Captive"
            
            # Informações do arquivo
            file_size_mb = round(video_file.size / (1024 * 1024), 2)
            upload_time = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
            user_info = user.username if user else "Sistema"
            
            # Corpo do email
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">
                        🎥 Novo Vídeo Enviado - Portal Captive
                    </h2>
                    
                    <div style="background: #f8fafc; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #4a5568;">📋 Detalhes do Upload:</h3>
                        <ul style="list-style: none; padding: 0;">
                            <li style="margin: 8px 0;"><strong>📁 Nome do arquivo:</strong> {video_file.name}</li>
                            <li style="margin: 8px 0;"><strong>📊 Tamanho:</strong> {file_size_mb} MB</li>
                            <li style="margin: 8px 0;"><strong>👤 Enviado por:</strong> {user_info}</li>
                            <li style="margin: 8px 0;"><strong>🕒 Data/Hora:</strong> {upload_time}</li>
                        </ul>
                    </div>
                    
                    <div style="background: #e6fffa; padding: 15px; border-radius: 8px; border-left: 4px solid #38b2ac;">
                        <p style="margin: 0;"><strong>ℹ️ Informação:</strong></p>
                        <p style="margin: 5px 0 0 0;">O vídeo foi enviado com sucesso e está disponível para configuração no sistema de gerenciamento do portal captive.</p>
                    </div>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; font-size: 12px; color: #718096; text-align: center;">
                        <p>📧 Notificação automática do sistema POPPFIRE ADMIN</p>
                        <p>🕒 Gerado em {upload_time}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Enviar email usando Django
            from django.core.mail import EmailMultiAlternatives
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=f"Novo vídeo enviado: {video_file.name} ({file_size_mb} MB)",
                from_email=EMAIL_CONFIG['FROM_EMAIL'],
                to=EMAIL_CONFIG['TO_EMAILS']
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            logger.info(f"Email enviado com sucesso para {', '.join(EMAIL_CONFIG['TO_EMAILS'])}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {str(e)}")
            return False
    
    @staticmethod
    def send_telegram_notification(video_file, user=None):
        """Envia notificação pelo Telegram sobre upload de vídeo"""
        try:
            # Informações do arquivo
            file_size_mb = round(video_file.size / (1024 * 1024), 2)
            upload_time = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
            user_info = user.username if user else "Sistema"
            
            # Mensagem formatada
            message = f"""🎥 Novo Vídeo - Portal Captive

📋 Detalhes do Upload:
• 📁 Arquivo: {video_file.name}
• 📊 Tamanho: {file_size_mb} MB
• 👤 Enviado por: {user_info}
• 🕒 Data/Hora: {upload_time}

✅ Status: Vídeo enviado com sucesso!
🔧 Sistema: POPPFIRE ADMIN

Notificação automática 🤖"""
            
            # Enviar via API do Telegram
            url = f"https://api.telegram.org/bot{TELEGRAM_CONFIG['BOT_TOKEN']}/sendMessage"
            params = {
                "chat_id": TELEGRAM_CONFIG['CHAT_ID'],
                "text": message
            }
            
            response = requests.post(url, params=params, timeout=10)
            
            if response.status_code == 200:
                logger.info("Notificação Telegram enviada com sucesso")
                return True
            else:
                logger.error(f"Erro ao enviar Telegram: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar notificação Telegram: {str(e)}")
            return False

class ZipManagerService:
    """Serviço para gerenciar atualizações do arquivo ZIP do portal"""
    
    @staticmethod
    def backup_current_zip(zip_path):
        """Faz backup do ZIP atual antes de modificar"""
        try:
            if not os.path.exists(zip_path):
                return None
                
            # Criar diretório de backup se não existir
            backup_dir = ZIP_CONFIG['BACKUP_DIR']
            os.makedirs(backup_dir, exist_ok=True)
            
            # Nome do backup com timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"src_backup_{timestamp}.zip"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Copiar arquivo
            shutil.copy2(zip_path, backup_path)
            logger.info(f"Backup criado: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Erro ao criar backup do ZIP: {str(e)}")
            return None
    
    @staticmethod
    def update_zip_with_video(zip_path, video_file):
        """Atualiza o ZIP substituindo o vídeo na pasta assets/videos"""
        try:
            if not os.path.exists(zip_path):
                logger.warning(f"Arquivo ZIP não encontrado: {zip_path}")
                return False
            
            # Fazer backup primeiro
            backup_path = ZipManagerService.backup_current_zip(zip_path)
            
            # Diretório temporário para extração
            temp_dir = f"temp_zip_extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            try:
                # Extrair ZIP atual
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Caminho para a pasta de vídeos
                videos_dir = os.path.join(temp_dir, ZIP_CONFIG['VIDEOS_PATH'])
                os.makedirs(videos_dir, exist_ok=True)
                
                # Remover vídeos existentes na pasta
                for file in os.listdir(videos_dir):
                    if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                        os.remove(os.path.join(videos_dir, file))
                        logger.info(f"Vídeo antigo removido: {file}")
                
                # Copiar novo vídeo
                video_destination = os.path.join(videos_dir, video_file.name)
                with open(video_destination, 'wb') as dest_file:
                    for chunk in video_file.chunks():
                        dest_file.write(chunk)
                
                logger.info(f"Novo vídeo adicionado: {video_file.name}")
                
                # Criar selected_video.txt para override automático
                try:
                    selected_txt_path = os.path.join(videos_dir, 'selected_video.txt')
                    with open(selected_txt_path, 'w', encoding='utf-8') as f:
                        f.write(video_file.name)
                    logger.info(f"selected_video.txt criado com: {video_file.name}")
                except Exception as e:
                    logger.warning(f"Falha ao criar selected_video.txt: {e}")
                
                # Atualizar HTMLs com nome do vídeo correto
                ZipManagerService._patch_html_video_references(temp_dir, video_file.name)
                
                # Recriar ZIP
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            archive_name = os.path.relpath(file_path, temp_dir)
                            zip_ref.write(file_path, archive_name)
                
                logger.info(f"ZIP atualizado com sucesso: {zip_path}")
                return True
                
            finally:
                # Limpar diretório temporário
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    
        except Exception as e:
            logger.error(f"Erro ao atualizar ZIP: {str(e)}")
            return False
    
    @staticmethod
    def get_zip_info(zip_path):
        """Retorna informações sobre o conteúdo do ZIP"""
        try:
            if not os.path.exists(zip_path):
                return None
            
            info = {
                'file_size': os.path.getsize(zip_path),
                'files': [],
                'videos': []
            }
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.filelist:
                    info['files'].append({
                        'name': file_info.filename,
                        'size': file_info.file_size,
                        'date': datetime(*file_info.date_time).strftime('%d/%m/%Y %H:%M:%S')
                    })
                    
                    # Identificar vídeos
                    if (file_info.filename.startswith(ZIP_CONFIG['VIDEOS_PATH']) and 
                        file_info.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm'))):
                        info['videos'].append(file_info.filename)
            
            return info
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do ZIP: {str(e)}")
            return None
    
    @staticmethod
    def _patch_html_video_references(temp_dir, video_filename):
        """
        Atualiza referências de vídeo em arquivos HTML dentro do diretório extraído
        """
        import re
        
        # HTMLs que precisam ser atualizados (assumindo estrutura src/)
        html_files = ['src/index.html', 'src/login.html', 'src/login2.html']
        
        for html_file in html_files:
            file_path = os.path.join(temp_dir, html_file)
            if not os.path.exists(file_path):
                continue
                
            try:
                # Ler conteúdo atual
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                original_content = content
                
                # Atualizar tag <source src="assets/videos/...">
                pattern = r'(<source\b[^>]*\bsrc=["\']assets/videos/)([^"\']+)(["\'][^>]*>)'
                content, n = re.subn(pattern, r'\1' + video_filename + r'\3', content, count=1)
                
                # Fallback: substituir referências diretas de eldNN.mp4
                if n == 0:
                    content = re.sub(r'assets/videos/eld\d+\.mp4', f'assets/videos/{video_filename}', content, count=1)
                    if content != original_content:
                        n = 1
                
                # Atualizar poster se existir (tentativa de mesma base)
                base_no_ext = os.path.splitext(video_filename)[0]
                for ext in ['.jpg', '.png']:
                    poster_file = f'assets/videos/{base_no_ext}{ext}'
                    poster_path = os.path.join(temp_dir, 'src', 'assets', 'videos', f'{base_no_ext}{ext}')
                    
                    # Se o poster existir, atualizar referência
                    if os.path.exists(poster_path):
                        content, n_poster = re.subn(
                            r'(poster=["\']assets/videos/)([^"\']+)(["\'])', 
                            r'\1' + base_no_ext + ext + r'\3', 
                            content, count=1
                        )
                        if n_poster == 0:
                            # Fallback para eldNN.jpg/png
                            content = re.sub(
                                r'poster=["\']assets/videos/eld\d+\.(jpg|png)["\']', 
                                f'poster="assets/videos/{base_no_ext}{ext}"', 
                                content, count=1
                            )
                        break
                
                # Gravar se houve mudanças
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"{html_file} atualizado para usar vídeo {video_filename}")
                
            except Exception as e:
                logger.warning(f"Falha ao atualizar {html_file}: {e}")