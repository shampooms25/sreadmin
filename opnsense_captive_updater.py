#!/usr/bin/env python3
"""
Script de Atualização do Portal Captive para OpenSense
===============================================

Este script deve ser executado no OpenSense para verificar e baixar
atualizações do portal captive do servidor Django.

Servidor: 172.18.25.253
APIs disponíveis:
- /api/captive-portal/status/ - Status do servidor
- /api/captive-portal/config/ - Configuração ativa
- /api/captive-portal/download/video/<id>/ - Download de vídeo
- /api/captive-portal/download/zip/<id>/ - Download de ZIP

Autor: Sistema ELD - Portal Captive
Data: 2025-07-27
"""

import requests
import json
import hashlib
import os
import sys
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
import time

# Configurações
SERVER_IP = "172.18.25.253"
SERVER_PORT = "8000"
BASE_URL = f"http://{SERVER_IP}:{SERVER_PORT}"

# Diretórios no OpenSense (ajustar conforme necessário)
CAPTIVE_PORTAL_DIR = "/usr/local/captiveportal"
VIDEOS_DIR = "/usr/local/captiveportal/videos"
BACKUP_DIR = "/usr/local/captiveportal/backup"
LOG_FILE = "/var/log/captive_portal_updater.log"
STATE_FILE = "/usr/local/captiveportal/update_state.json"

# Timeout para requests
REQUEST_TIMEOUT = 30

class CaptivePortalUpdater:
    """
    Classe principal para atualização do portal captive
    """
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        self.state = self.load_state()
        
    def setup_logging(self):
        """
        Configura o sistema de logs
        """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def load_state(self) -> Dict:
        """
        Carrega o estado anterior da atualização
        """
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Erro ao carregar estado anterior: {e}")
        
        return {
            'last_update': None,
            'last_config_id': None,
            'last_video_hash': None,
            'last_zip_hash': None
        }
    
    def save_state(self):
        """
        Salva o estado atual da atualização
        """
        try:
            os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
            with open(STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            self.logger.error(f"Erro ao salvar estado: {e}")
    
    def calculate_file_hash(self, file_path: str) -> Optional[str]:
        """
        Calcula hash SHA256 de um arquivo
        """
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"Erro ao calcular hash de {file_path}: {e}")
            return None
    
    def check_server_status(self) -> bool:
        """
        Verifica se o servidor está online
        """
        try:
            self.logger.info(f"Verificando status do servidor {SERVER_IP}...")
            
            response = requests.get(
                f"{BASE_URL}/api/captive-portal/status/",
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                self.logger.info(f"Servidor online - Status: {data.get('status')}")
                self.logger.info(f"Horário do servidor: {data.get('server_time')}")
                return True
            else:
                self.logger.error(f"Servidor retornou status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao conectar com servidor: {e}")
            return False
    
    def get_server_config(self) -> Optional[Dict]:
        """
        Obtém a configuração ativa do servidor
        """
        try:
            self.logger.info("Obtendo configuração do portal captive...")
            
            response = requests.get(
                f"{BASE_URL}/api/captive-portal/config/",
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data['status'] == 'success':
                    self.logger.info(f"Configuração obtida - ID: {data.get('config_id')}")
                    return data
                elif data['status'] == 'no_config':
                    self.logger.info("Nenhuma configuração ativa no servidor")
                    return None
                else:
                    self.logger.error(f"Erro na configuração: {data.get('message')}")
                    return None
            else:
                self.logger.error(f"Erro HTTP {response.status_code} ao obter configuração")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao obter configuração: {e}")
            return None
    
    def download_file(self, url: str, local_path: str) -> bool:
        """
        Baixa um arquivo do servidor
        """
        try:
            self.logger.info(f"Baixando arquivo de {url} para {local_path}...")
            
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            response = requests.get(
                f"{BASE_URL}{url}",
                timeout=REQUEST_TIMEOUT,
                stream=True
            )
            
            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                self.logger.info(f"Arquivo baixado com sucesso: {local_path}")
                return True
            else:
                self.logger.error(f"Erro HTTP {response.status_code} ao baixar arquivo")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao baixar arquivo: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erro geral ao baixar arquivo: {e}")
            return False
    
    def backup_current_files(self):
        """
        Faz backup dos arquivos atuais
        """
        try:
            if not os.path.exists(CAPTIVE_PORTAL_DIR):
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{BACKUP_DIR}/backup_{timestamp}"
            
            self.logger.info(f"Fazendo backup para {backup_path}...")
            
            # Criar diretório de backup
            os.makedirs(backup_path, exist_ok=True)
            
            # Copiar arquivos importantes (implementar conforme necessário)
            import shutil
            if os.path.exists(VIDEOS_DIR):
                shutil.copytree(VIDEOS_DIR, f"{backup_path}/videos", dirs_exist_ok=True)
            
            self.logger.info("Backup concluído")
            
        except Exception as e:
            self.logger.error(f"Erro ao fazer backup: {e}")
    
    def extract_portal_zip(self, zip_path: str) -> bool:
        """
        Extrai o ZIP do portal captive
        """
        try:
            import zipfile
            
            self.logger.info(f"Extraindo ZIP do portal: {zip_path}")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(CAPTIVE_PORTAL_DIR)
            
            self.logger.info("ZIP extraído com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair ZIP: {e}")
            return False
    
    def restart_captive_portal_service(self):
        """
        Reinicia o serviço do portal captive (implementar conforme OpenSense)
        """
        try:
            self.logger.info("Reiniciando serviço do portal captive...")
            
            # Comandos para reiniciar o portal captive no OpenSense
            # Ajustar conforme a configuração específica
            os.system("pfctl -F all")  # Limpar regras de firewall
            os.system("/usr/local/etc/rc.d/lighttpd restart")  # Reiniciar web server
            
            self.logger.info("Serviço reiniciado")
            
        except Exception as e:
            self.logger.error(f"Erro ao reiniciar serviço: {e}")
    
    def needs_update(self, config: Dict) -> Tuple[bool, str]:
        """
        Verifica se precisa de atualização
        """
        reasons = []
        
        # Verificar se é uma nova configuração
        current_config_id = config.get('config_id')
        if current_config_id != self.state.get('last_config_id'):
            reasons.append(f"Nova configuração (ID: {current_config_id})")
        
        # Verificar hash do vídeo
        video_info = config.get('video')
        if video_info:
            current_video_hash = video_info.get('hash')
            if current_video_hash != self.state.get('last_video_hash'):
                reasons.append("Vídeo alterado")
        
        # Verificar hash do ZIP
        zip_info = config.get('portal_zip')
        if zip_info:
            current_zip_hash = zip_info.get('hash')
            if current_zip_hash != self.state.get('last_zip_hash'):
                reasons.append("Portal ZIP alterado")
        
        needs_update = len(reasons) > 0
        reason_text = "; ".join(reasons) if reasons else "Nenhuma alteração"
        
        return needs_update, reason_text
    
    def perform_update(self, config: Dict) -> bool:
        """
        Executa a atualização do portal
        """
        try:
            self.logger.info("=== INICIANDO ATUALIZAÇÃO DO PORTAL CAPTIVE ===")
            
            success = True
            
            # Fazer backup antes da atualização
            self.backup_current_files()
            
            # Baixar vídeo se necessário
            video_info = config.get('video')
            if video_info and config.get('ativar_video'):
                video_url = video_info['url']
                video_filename = video_info['name']
                video_path = os.path.join(VIDEOS_DIR, video_filename)
                
                if self.download_file(video_url, video_path):
                    # Verificar hash do arquivo baixado
                    local_hash = self.calculate_file_hash(video_path)
                    expected_hash = video_info.get('hash')
                    
                    if local_hash == expected_hash:
                        self.logger.info("Hash do vídeo verificado com sucesso")
                        self.state['last_video_hash'] = local_hash
                    else:
                        self.logger.error("Hash do vídeo não confere!")
                        success = False
                else:
                    success = False
            
            # Baixar e extrair ZIP do portal se necessário
            zip_info = config.get('portal_zip')
            if zip_info:
                zip_url = zip_info['url']
                zip_filename = f"portal_{config['config_id']}.zip"
                zip_path = os.path.join(BACKUP_DIR, zip_filename)
                
                if self.download_file(zip_url, zip_path):
                    # Verificar hash do ZIP
                    local_hash = self.calculate_file_hash(zip_path)
                    expected_hash = zip_info.get('hash')
                    
                    if local_hash == expected_hash:
                        self.logger.info("Hash do ZIP verificado com sucesso")
                        
                        # Extrair ZIP
                        if self.extract_portal_zip(zip_path):
                            self.state['last_zip_hash'] = local_hash
                        else:
                            success = False
                    else:
                        self.logger.error("Hash do ZIP não confere!")
                        success = False
                else:
                    success = False
            
            if success:
                # Atualizar estado
                self.state['last_config_id'] = config['config_id']
                self.state['last_update'] = datetime.now().isoformat()
                self.save_state()
                
                # Reiniciar serviço
                self.restart_captive_portal_service()
                
                self.logger.info("=== ATUALIZAÇÃO CONCLUÍDA COM SUCESSO ===")
                return True
            else:
                self.logger.error("=== ATUALIZAÇÃO FALHOU ===")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro durante atualização: {e}")
            return False
    
    def run(self):
        """
        Executa o processo de verificação e atualização
        """
        try:
            self.logger.info("Iniciando verificação de atualizações...")
            
            # Verificar se servidor está online
            if not self.check_server_status():
                self.logger.error("Servidor não está acessível")
                return False
            
            # Obter configuração do servidor
            config = self.get_server_config()
            if not config:
                self.logger.info("Nenhuma configuração ativa - nada para atualizar")
                return True
            
            # Verificar se precisa atualizar
            needs_update, reason = self.needs_update(config)
            
            if needs_update:
                self.logger.info(f"Atualização necessária: {reason}")
                return self.perform_update(config)
            else:
                self.logger.info("Portal captive já está atualizado")
                return True
                
        except Exception as e:
            self.logger.error(f"Erro geral no updater: {e}")
            return False


def main():
    """
    Função principal
    """
    print("Portal Captive Updater para OpenSense")
    print("=====================================")
    print(f"Servidor: {SERVER_IP}:{SERVER_PORT}")
    print(f"Log: {LOG_FILE}")
    print()
    
    updater = CaptivePortalUpdater()
    success = updater.run()
    
    exit_code = 0 if success else 1
    print(f"\nFinalizado com código: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
