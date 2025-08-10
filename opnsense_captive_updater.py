#!/usr/bin/env python3
"""
Script de Sincronização de Portal Captive para OpnSense
Integração com POPPFIRE Appliance API

Este script:
1. Verifica o status do portal via API
2. Compara com a versão local instalada
3. Baixa e aplica atualizações automaticamente
4. Mantém histórico de versões

Localização no OpnSense: /usr/local/bin/poppfire_portal_updater.py
Portal htdocs: /var/captiveportal/zone0/htdocs/

Execução recomendada: A cada 5 minutos via cron
"""

import os
import sys
import json
import hashlib
import requests
import zipfile
import shutil
import logging
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

# Configurações
class Config:
    # API do POPPFIRE
    API_BASE_URL = "http://172.18.25.253:8000"  # IP do servidor POPPFIRE
    API_TOKEN = "f8e7d6c5b4a3928170695e4c3d2b1a0f"  # Token do appliance
    
    # Caminhos no OpnSense
    PORTAL_HTDOCS_PATH = "/var/captiveportal/zone0/htdocs"
    STATE_FILE = "/var/db/poppfire_portal_state.json"
    BACKUP_DIR = "/var/db/poppfire_portal_backups"
    LOG_FILE = "/var/log/poppfire_portal_updater.log"
    
    # Configurações de operação
    MAX_BACKUPS = 5
    TIMEOUT = 30
    RETRY_ATTEMPTS = 3
    MIN_UPDATE_INTERVAL = 300  # 5 minutos em segundos


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class PortalState:
    """Gerencia o estado atual do portal no OpnSense"""
    
    def __init__(self):
        self.state_file = Config.STATE_FILE
        self.state = self._load_state()
    
    def _load_state(self):
        """Carrega o estado atual do arquivo"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Erro ao carregar estado: {e}")
        
        # Estado padrão
        return {
            "current_portal_type": None,
            "current_hash": None,
            "last_update": None,
            "last_check": None,
            "update_count": 0,
            "errors": []
        }
    
    def save_state(self):
        """Salva o estado atual no arquivo"""
        try:
            self.state["last_check"] = datetime.now().isoformat()
            
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar estado: {e}")
    
    def should_check_update(self):
        """Verifica se deve checar atualizações (evita spam)"""
        if not self.state.get("last_check"):
            return True
        
        try:
            last_check = datetime.fromisoformat(self.state["last_check"])
            return (datetime.now() - last_check).total_seconds() > Config.MIN_UPDATE_INTERVAL
        except:
            return True
    
    def add_error(self, error_msg):
        """Adiciona erro ao histórico"""
        self.state.setdefault("errors", []).append({
            "timestamp": datetime.now().isoformat(),
            "message": error_msg
        })
        
        # Manter apenas os últimos 10 erros
        self.state["errors"] = self.state["errors"][-10:]


class PoppfireAPI:
    """Cliente para a API do POPPFIRE"""
    
    def __init__(self):
        self.base_url = Config.API_BASE_URL
        self.token = Config.API_TOKEN
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'User-Agent': 'OpnSense-Portal-Updater/1.0'
        }
    
    def _make_request(self, endpoint, method='GET', **kwargs):
        """Faz requisição à API com retry"""
        url = f"{self.base_url}/api/appliances{endpoint}"
        
        for attempt in range(Config.RETRY_ATTEMPTS):
            try:
                response = requests.request(
                    method, url, 
                    headers=self.headers,
                    timeout=Config.TIMEOUT,
                    **kwargs
                )
                
                if response.status_code == 401:
                    raise Exception("Token de autenticação inválido")
                
                response.raise_for_status()
                return response
                
            except requests.RequestException as e:
                logger.warning(f"Tentativa {attempt + 1} falhou: {e}")
                if attempt == Config.RETRY_ATTEMPTS - 1:
                    raise
        
        raise Exception("Máximo de tentativas excedido")
    
    def get_portal_status(self):
        """Obtém status atual do portal"""
        try:
            response = self._make_request('/portal/status/')
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter status do portal: {e}")
            raise
    
    def download_portal(self, portal_type):
        """Baixa o arquivo ZIP do portal"""
        try:
            response = self._make_request(f'/portal/download/?type={portal_type}')
            return response.content
        except Exception as e:
            logger.error(f"Erro ao baixar portal {portal_type}: {e}")
            raise
    
    def report_update_status(self, status, portal_hash, portal_type, error_msg=None):
        """Reporta status de atualização para o servidor"""
        try:
            data = {
                "appliance_id": "OPNSENSE-001",
                "appliance_ip": self._get_local_ip(),
                "update_status": status,
                "portal_hash": portal_hash,
                "portal_type": portal_type,
                "update_timestamp": datetime.now().isoformat()
            }
            
            if error_msg:
                data["error_message"] = error_msg
            
            response = self._make_request('/portal/update-status/', method='POST', json=data)
            logger.info(f"Status de atualização reportado: {status}")
            
        except Exception as e:
            logger.warning(f"Erro ao reportar status de atualização: {e}")
    
    def _get_local_ip(self):
        """Obtém IP local do OpnSense"""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "unknown"


class PortalManager:
    """Gerencia instalação e atualização do portal no OpnSense"""
    
    def __init__(self):
        self.htdocs_path = Config.PORTAL_HTDOCS_PATH
        self.backup_dir = Config.BACKUP_DIR
        
        # Criar diretórios necessários
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def calculate_current_hash(self):
        """Calcula hash SHA256 do portal atual instalado"""
        try:
            if not os.path.exists(self.htdocs_path):
                return None
            
            # Criar um hash baseado em todos os arquivos do portal
            hash_sha256 = hashlib.sha256()
            
            for root, dirs, files in os.walk(self.htdocs_path):
                # Ordenar para garantir consistência
                dirs.sort()
                files.sort()
                
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'rb') as f:
                            for chunk in iter(lambda: f.read(4096), b""):
                                hash_sha256.update(chunk)
                    except Exception as e:
                        logger.warning(f"Erro ao ler arquivo {file_path}: {e}")
            
            return hash_sha256.hexdigest()
            
        except Exception as e:
            logger.error(f"Erro ao calcular hash atual: {e}")
            return None
    
    def backup_current_portal(self):
        """Cria backup do portal atual"""
        try:
            if not os.path.exists(self.htdocs_path):
                logger.info("Nenhum portal para backup")
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"portal_backup_{timestamp}.zip"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
                for root, dirs, files in os.walk(self.htdocs_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, self.htdocs_path)
                        backup_zip.write(file_path, arc_path)
            
            logger.info(f"Backup criado: {backup_path}")
            
            # Limpar backups antigos
            self._cleanup_old_backups()
            
            return backup_path
            
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            return None
    
    def install_portal(self, zip_content, portal_type):
        """Instala o novo portal a partir do ZIP"""
        try:
            # Criar backup antes da instalação
            backup_path = self.backup_current_portal()
            
            # Criar diretório temporário
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, "portal.zip")
                
                # Salvar ZIP temporário
                with open(zip_path, 'wb') as f:
                    f.write(zip_content)
                
                # Extrair ZIP
                extract_dir = os.path.join(temp_dir, "extracted")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # Remover portal atual
                if os.path.exists(self.htdocs_path):
                    shutil.rmtree(self.htdocs_path)
                
                # Criar diretório htdocs
                os.makedirs(self.htdocs_path, exist_ok=True)
                
                # Copiar arquivos extraídos
                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        src_file = os.path.join(root, file)
                        rel_path = os.path.relpath(src_file, extract_dir)
                        dst_file = os.path.join(self.htdocs_path, rel_path)
                        
                        # Criar diretório de destino se necessário
                        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                        shutil.copy2(src_file, dst_file)
                
                # Ajustar permissões
                self._fix_permissions()
                
                logger.info(f"Portal {portal_type} instalado com sucesso")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao instalar portal: {e}")
            
            # Tentar restaurar backup
            if backup_path and os.path.exists(backup_path):
                logger.info("Tentando restaurar backup...")
                self._restore_backup(backup_path)
            
            return False
    
    def _fix_permissions(self):
        """Ajusta permissões dos arquivos do portal"""
        try:
            # Definir permissões apropriadas para o OpnSense
            for root, dirs, files in os.walk(self.htdocs_path):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    os.chmod(dir_path, 0o755)
                
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    if file_name.endswith(('.php', '.py', '.sh')):
                        os.chmod(file_path, 0o755)
                    else:
                        os.chmod(file_path, 0o644)
        except Exception as e:
            logger.warning(f"Erro ao ajustar permissões: {e}")
    
    def _cleanup_old_backups(self):
        """Remove backups antigos"""
        try:
            backups = []
            for file in os.listdir(self.backup_dir):
                if file.startswith("portal_backup_") and file.endswith(".zip"):
                    file_path = os.path.join(self.backup_dir, file)
                    backups.append((file_path, os.path.getmtime(file_path)))
            
            # Ordenar por data (mais antigo primeiro)
            backups.sort(key=lambda x: x[1])
            
            # Remover backups excedentes
            while len(backups) > Config.MAX_BACKUPS:
                old_backup = backups.pop(0)
                os.remove(old_backup[0])
                logger.info(f"Backup antigo removido: {old_backup[0]}")
                
        except Exception as e:
            logger.warning(f"Erro ao limpar backups antigos: {e}")
    
    def _restore_backup(self, backup_path):
        """Restaura backup em caso de erro"""
        try:
            if os.path.exists(self.htdocs_path):
                shutil.rmtree(self.htdocs_path)
            
            os.makedirs(self.htdocs_path, exist_ok=True)
            
            with zipfile.ZipFile(backup_path, 'r') as backup_zip:
                backup_zip.extractall(self.htdocs_path)
            
            self._fix_permissions()
            logger.info("Backup restaurado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {e}")


class PortalUpdater:
    """Classe principal para atualização do portal"""
    
    def __init__(self):
        self.state = PortalState()
        self.api = PoppfireAPI()
        self.manager = PortalManager()
    
    def run(self):
        """Executa o processo de atualização"""
        try:
            logger.info("=== Iniciando verificação de atualização do portal ===")
            
            # Verificar se deve executar verificação
            if not self.state.should_check_update():
                logger.info("Verificação pulada (intervalo mínimo não atingido)")
                return True
            
            # Obter status atual do portal no servidor
            portal_status = self.api.get_portal_status()
            logger.info(f"Status do servidor: {portal_status.get('status')} - Tipo: {portal_status.get('portal_type')}")
            
            # Calcular hash atual do portal instalado
            current_hash = self.manager.calculate_current_hash()
            server_hash = portal_status.get('portal_hash')
            portal_type = portal_status.get('portal_type')
            
            logger.info(f"Hash atual: {current_hash}")
            logger.info(f"Hash servidor: {server_hash}")
            
            # Verificar se precisa atualizar
            needs_update = (
                current_hash != server_hash or
                self.state.state.get('current_portal_type') != portal_type or
                current_hash is None  # Nenhum portal instalado
            )
            
            if not needs_update:
                logger.info("Portal já está atualizado")
                self.state.save_state()
                return True
            
            # Baixar e instalar nova versão
            logger.info(f"Atualizando portal: {portal_type}")
            
            zip_content = self.api.download_portal(portal_type)
            
            if self.manager.install_portal(zip_content, portal_type):
                # Atualização bem-sucedida
                new_hash = self.manager.calculate_current_hash()
                
                self.state.state.update({
                    'current_portal_type': portal_type,
                    'current_hash': new_hash,
                    'last_update': datetime.now().isoformat(),
                    'update_count': self.state.state.get('update_count', 0) + 1
                })
                
                logger.info(f"Portal atualizado com sucesso! Novo hash: {new_hash}")
                
                # Reportar sucesso para o servidor
                self.api.report_update_status('success', new_hash, portal_type)
                
                # Reiniciar serviços do portal captive se necessário
                self._restart_captive_portal()
                
            else:
                raise Exception("Falha na instalação do portal")
            
            self.state.save_state()
            return True
            
        except Exception as e:
            error_msg = f"Erro durante atualização: {str(e)}"
            logger.error(error_msg)
            
            self.state.add_error(error_msg)
            self.state.save_state()
            
            # Reportar erro para o servidor
            try:
                self.api.report_update_status('failed', current_hash or 'unknown', 
                                            portal_type or 'unknown', error_msg)
            except:
                pass
            
            return False
    
    def _restart_captive_portal(self):
        """Reinicia o serviço do portal captive no OpnSense"""
        try:
            # Comandos específicos do OpnSense para reiniciar o portal captive
            restart_commands = [
                "/usr/local/etc/rc.d/lighttpd restart",
                "configctl captiveportal restart"
            ]
            
            for cmd in restart_commands:
                try:
                    os.system(cmd)
                    logger.info(f"Comando executado: {cmd}")
                except Exception as e:
                    logger.warning(f"Erro ao executar {cmd}: {e}")
            
        except Exception as e:
            logger.warning(f"Erro ao reiniciar portal captive: {e}")


def main():
    """Função principal"""
    try:
        updater = PortalUpdater()
        success = updater.run()
        
        if success:
            logger.info("=== Atualização concluída com sucesso ===")
            sys.exit(0)
        else:
            logger.error("=== Atualização falhou ===")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
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
