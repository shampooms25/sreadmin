#!/usr/bin/env python3
"""
Updater de Portal Captive para OpnSense integrado à API POPPFIRE.
- Consulta status do portal
- Compara com instalação local
- Baixa e instala ZIP do portal
- Mantém backups e estado
"""

import os
import sys
import json
import hashlib
import requests
import zipfile
import shutil
import logging
import subprocess
import tempfile
import pwd
import grp
import time
import argparse
import signal
import socket
from datetime import datetime
import re


class Config:
    # Ajuste para seu ambiente de produção
    API_BASE_URL = "https://paineleld.poppnet.com.br"
    API_TOKEN = "884f88da2e8a947500ceb4af1dafa10d"  # token do appliance

    # Caminho padrão (pfSense/OPNsense antigos). Será descoberto dinamicamente abaixo.
    PORTAL_HTDOCS_PATH = "/var/captiveportal/zone0/htdocs"
    STATE_FILE = "/var/db/poppfire_portal_state.json"
    BACKUP_DIR = "/var/db/poppfire_portal_backups"
    LOG_FILE = "/var/log/poppfire_portal_updater.log"

    TIMEOUT = 30
    RETRY_ATTEMPTS = 3
    MIN_UPDATE_INTERVAL = 60  # 1 minuto
    MAX_BACKUPS = 5
    DEBUG = True  # Ativa logs extras de diagnóstico
    SYNC_DEFAULT_TEMPLATE = True  # Ativado por padrão: garante persistência pós-reboot
    ENFORCE_LOCAL_DRIFT = False  # Se true, reinstala quando detectar alterações manuais locais
    DISCONNECT_SESSIONS_ON_UPDATE = True  # Derruba sessões apenas quando uma atualização ocorre

    # Credenciais API Local (OPNsense) para gerenciamento de sessões
    LOCAL_API_KEY = "nyDvq1X0zWd4DC0YCJm43Hrwi1C3640acDDZ0r40ITrf6FvfDqsAEZhpGc40oMWNFo5zwvfTNyfM1GfX"
    LOCAL_API_SECRET = "36SfXGuYDwqhR37LdagJPZ/9K3gowro2dJHVDkSPhe/8+QjdqHojdJh41SqjQBGgd9Nmij0CYwhUAABl"
    LOCAL_API_URL = "https://127.0.0.1:5555/api"


# Evitar linhas duplicadas: log apenas em stdout; o wrapper redireciona para arquivo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("poppfire_updater")


class PortalState:
    def __init__(self):
        self.path = Config.STATE_FILE
        self.data = self._load()

    def _load(self):
        try:
            if os.path.exists(self.path):
                with open(self.path, 'r') as f:
                    data = json.load(f)
                    data.setdefault("current_zip_hash", None)
                    data.setdefault("current_local_hash", None)
                    return data
        except Exception as e:
            logger.warning(f"Erro ao carregar estado: {e}")
        return {
            "current_portal_type": None,
            "current_hash": None,
            "current_zip_hash": None,
            "current_local_hash": None,
            "last_update": None,
            "last_check": None,
            "update_count": 0,
            "errors": []
        }

    def save(self):
        try:
            self.data["last_check"] = datetime.now().isoformat()
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar estado: {e}")

    def should_check(self):
        last = self.data.get("last_check")
        if not last:
            return True
        try:
            from datetime import datetime as dt
            now = dt.now()
            prev = dt.fromisoformat(last)
            return (now - prev).total_seconds() > Config.MIN_UPDATE_INTERVAL
        except Exception:
            return True

    def add_error(self, msg: str):
        self.data.setdefault("errors", []).append({
            "timestamp": datetime.now().isoformat(),
            "message": msg
        })
        self.data["errors"] = self.data["errors"][-10:]


class API:
    def __init__(self):
        self.base = Config.API_BASE_URL.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {Config.API_TOKEN}',
            'User-Agent': 'OpnSense-Portal-Updater/1.0'
        }

    def _req(self, endpoint: str, method='GET', **kwargs):
        url = f"{self.base}/api/appliances{endpoint}"
        for i in range(Config.RETRY_ATTEMPTS):
            try:
                resp = requests.request(method, url, headers=self.headers, timeout=Config.TIMEOUT, allow_redirects=True, **kwargs)
                if resp.status_code == 401:
                    raise Exception("Token de autenticação inválido")
                
                # Casos especiais: 404 pode ser uma resposta válida da API 
                if resp.status_code == 404 and (endpoint == '/portal/status/' or endpoint.startswith('/portal/download/')):
                    # Verificar se há conteúdo JSON válido na resposta 404
                    try:
                        resp.json()  # Se conseguir fazer parse do JSON, é uma resposta válida
                        return resp
                    except ValueError:
                        # Se não for JSON válido, é um 404 real de erro
                        pass
                
                resp.raise_for_status()
                return resp
            except requests.RequestException as e:
                if i == Config.RETRY_ATTEMPTS - 1:
                    raise
                logger.warning(f"Tentativa {i+1} falhou: {e}")
        raise Exception("Falha ao chamar API")

    def portal_status(self):
        resp = self._req('/portal/status/')
        data = resp.json()
        
        # Se a API retornou 404 mas com JSON válido, tratar como resposta normal
        if resp.status_code == 404:
            logger.info(f"API retornou 404 com dados: {data}")
            # Adicionar campos padrão se não existirem
            if 'portal_type' not in data:
                data['portal_type'] = None
            if 'portal_hash' not in data:
                data['portal_hash'] = None
                
        return data

    def download_zip(self, portal_type: str):
        resp = self._req(f"/portal/download/?type={portal_type}")
        
        # Verificar se a resposta é um erro em JSON
        if resp.headers.get('content-type', '').startswith('application/json'):
            try:
                error_data = resp.json()
                if 'error' in error_data:
                    raise Exception(f"Portal não disponível: {error_data.get('error')} - {error_data.get('message', '')}")
            except ValueError:
                # Se não conseguiu fazer parse do JSON, continuar normalmente
                pass
        
        return resp.content

    def report(self, status: str, portal_hash: str, portal_type: str, error: str | None = None):
        try:
            payload = {
                "appliance_id": "OPNSENSE-001",
                "appliance_ip": self._ip() or "unknown",
                "update_status": status,
                "portal_hash": portal_hash,
                "portal_type": portal_type,
                "update_timestamp": datetime.now().isoformat(),
            }
            if error:
                payload["error_message"] = error
            self._req('/portal/update-status/', method='POST', json=payload)
        except Exception as e:
            logger.warning(f"Erro ao reportar status: {e}")

    def _ip(self):
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return None


class Installer:
    def __init__(self):
        self.backups = Config.BACKUP_DIR
        os.makedirs(self.backups, exist_ok=True)
        self.htdocs_paths = self._discover_htdocs_paths()
        # Caminho primário usado para hashing/backup (primeiro válido)
        self.primary_htdocs = self.htdocs_paths[0] if self.htdocs_paths else Config.PORTAL_HTDOCS_PATH
        if not self.htdocs_paths:
            # Garante ao menos o caminho padrão
            os.makedirs(self.primary_htdocs, exist_ok=True)
            self.htdocs_paths = [self.primary_htdocs]
        logger.info(f"HTDOCS detectados: {', '.join(self.htdocs_paths)}")
        # Snapshot em memória de arquivos críticos para reaplicação pós-start
        self._critical_snapshot = None  # dict nome->bytes
        
        # AUTO-FIX: Na inicialização, verificar e corrigir persistência automaticamente
        self._auto_fix_persistence_on_init()

    def _auto_fix_persistence_on_init(self):
        """Verifica e corrige automaticamente a persistência do template na inicialização.
        
        Esta função é executada uma vez por execução do script e:
        1. Detecta se o template default está desatualizado ou com conteúdo padrão
        2. Se o htdocs principal tiver nosso template customizado, copia para o default
        3. Registra a correção para evitar processamento desnecessário
        """
        try:
            # Só executa se tivermos conteúdo no htdocs principal
            src_dir = self.primary_htdocs
            src_index = os.path.join(src_dir, "index.html")
            
            if not os.path.exists(src_index):
                logger.debug("Auto-fix: Sem index.html na fonte, pulando verificação")
                return
            
            # Verificar se a fonte tem nosso template customizado
            try:
                with open(src_index, 'r', encoding='utf-8', errors='ignore') as f:
                    src_content = f.read(2000)
                
                # Marcadores que indicam nosso template POPPFIRE
                our_markers = ['Portal de Acesso', 'poppfire', 'POPPFIRE', 'videoPlayer', 'checkVideo']
                has_our_template = any(m in src_content for m in our_markers)
                
                if not has_our_template:
                    logger.debug("Auto-fix: Fonte não contém template POPPFIRE, pulando")
                    return
                    
            except Exception as e:
                logger.debug(f"Auto-fix: Erro ao ler fonte: {e}")
                return
            
            # Descobrir caminho do fetch_template.py
            primary_default = self._discover_fetch_template_path()
            if not primary_default:
                # Fallback para caminho conhecido
                primary_default = "/usr/local/opnsense/scripts/captiveportal/htdocs_default"
            
            # Verificar se o default precisa de atualização
            default_index = os.path.join(primary_default, "index.html")
            needs_update = False
            
            if not os.path.exists(default_index):
                logger.info(f"Auto-fix: Template default não existe em {primary_default}")
                needs_update = True
            else:
                try:
                    with open(default_index, 'r', encoding='utf-8', errors='ignore') as f:
                        default_content = f.read(2000)
                    
                    # Verificar se é o template padrão do OPNsense (não o nosso)
                    default_opnsense_markers = ['Captive Portal login', 'opnlogo.png', 'Orange theme']
                    is_default_opnsense = any(m in default_content for m in default_opnsense_markers)
                    
                    # Verificar se NÃO tem nossos marcadores
                    has_our_markers = any(m in default_content for m in our_markers)
                    
                    if is_default_opnsense and not has_our_markers:
                        logger.info("Auto-fix: Template default contém layout OPNsense padrão, precisa atualizar")
                        needs_update = True
                    elif not has_our_markers:
                        # Comparar tamanhos como heurística adicional
                        src_size = os.path.getsize(src_index)
                        default_size = os.path.getsize(default_index)
                        if abs(src_size - default_size) > 1000:  # Diferença significativa
                            logger.info(f"Auto-fix: Tamanhos diferentes (src={src_size}, default={default_size})")
                            needs_update = True
                            
                except Exception as e:
                    logger.warning(f"Auto-fix: Erro ao verificar default: {e}")
                    needs_update = True
            
            if needs_update:
                logger.info("=" * 50)
                logger.info("AUTO-FIX: Aplicando correção de persistência...")
                logger.info("=" * 50)
                self.copy_to_default_template()
                logger.info("AUTO-FIX: Correção aplicada com sucesso!")
            else:
                logger.debug("Auto-fix: Template default já está atualizado")
                
        except Exception as e:
            logger.warning(f"Auto-fix persistence check falhou: {e}")

    def _discover_htdocs_paths(self):
        """Descobre htdocs ativos no OPNsense (zoneX/htdocs). Se não houver zonas, tenta caminhos legados."""
        zone_paths = []
        base = "/var/captiveportal"
        if os.path.isdir(base):
            try:
                for name in sorted(os.listdir(base)):
                    if name.startswith("zone"):
                        p = os.path.join(base, name, "htdocs")
                        if os.path.isdir(p):
                            zone_paths.append(p)
            except Exception as e:
                logger.warning(f"Falha ao listar zonas em {base}: {e}")
        if zone_paths:
            return zone_paths
        # Fallback: caminhos alternativos/legados (usados apenas se não houver zonas)
        legacy = []
        for alt in [
            "/usr/local/captiveportal/htdocs",
            "/usr/local/captiveportal",
        ]:
            if os.path.isdir(alt):
                legacy.append(alt)
        return legacy

    def current_hash(self):
        htdocs = self.primary_htdocs
        if not os.path.exists(htdocs):
            return None
        h = hashlib.sha256()
        for root, dirs, files in os.walk(htdocs):
            dirs.sort(); files.sort()
            for f in files:
                p = os.path.join(root, f)
                try:
                    with open(p, 'rb') as fp:
                        for chunk in iter(lambda: fp.read(4096), b""):
                            h.update(chunk)
                except Exception as e:
                    logger.warning(f"Erro ao ler {p}: {e}")
        return h.hexdigest()

    def backup(self):
        htdocs = self.primary_htdocs
        if not os.path.exists(htdocs):
            return None
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(self.backups, f"portal_backup_{ts}.zip")
        try:
            with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
                for root, _, files in os.walk(htdocs):
                    for f in files:
                        p = os.path.join(root, f)
                        arc = os.path.relpath(p, htdocs)
                        z.write(p, arc)
            self._cleanup_old_backups()
            return path
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            return None

    def install_zip_bytes(self, zip_bytes: bytes, force_login_sync: bool = False):
        backup_path = None
        try:
            backup_path = self.backup()
            with tempfile.TemporaryDirectory() as td:
                zp = os.path.join(td, 'portal.zip')
                with open(zp, 'wb') as f:
                    f.write(zip_bytes)
                extract = os.path.join(td, 'extracted')
                with zipfile.ZipFile(zp, 'r') as z:
                    z.extractall(extract)
                # Se o ZIP tiver uma única pasta na raiz, achatar para a raiz do htdocs
                entries = [e for e in os.listdir(extract) if not e.startswith('__MACOSX')]
                base_dir = extract
                if len(entries) == 1 and os.path.isdir(os.path.join(extract, entries[0])):
                    base_dir = os.path.join(extract, entries[0])
                if Config.DEBUG:
                    try:
                        all_files = []
                        for root, _, files in os.walk(base_dir):
                            for f in files:
                                rel = os.path.relpath(os.path.join(root, f), base_dir)
                                all_files.append(rel)
                        logger.info(f"Arquivos no ZIP (total {len(all_files)}): " + ", ".join(sorted(all_files)[:40]) + (" ..." if len(all_files) > 40 else ""))
                    except Exception as e:
                        logger.warning(f"Diag ZIP listing falhou: {e}")

                # Limpa e instala em TODAS as zonas/paths detectados
                for htdocs in self.htdocs_paths:
                    try:
                        # Limpar conteúdo (rm -rf htdocs/*), preservando o diretório
                        if os.path.exists(htdocs):
                            for entry in os.listdir(htdocs):
                                target = os.path.join(htdocs, entry)
                                try:
                                    if os.path.isdir(target) and not os.path.islink(target):
                                        shutil.rmtree(target)
                                    else:
                                        os.remove(target)
                                except FileNotFoundError:
                                    pass
                                except Exception as e:
                                    logger.warning(f"Falha ao remover {target}: {e}")
                        else:
                            os.makedirs(htdocs, exist_ok=True)
                        files_written = 0
                        for root, _, files in os.walk(base_dir):
                            for f in files:
                                src = os.path.join(root, f)
                                rel = os.path.relpath(src, base_dir)
                                dst = os.path.join(htdocs, rel)
                                os.makedirs(os.path.dirname(dst), exist_ok=True)
                                shutil.copy2(src, dst)
                                files_written += 1
                        self._fix_permissions(htdocs)
                        # Ajustar nome do vídeo principal (se necessário) antes de sincronizar logins
                        try:
                            self._auto_update_video_source(htdocs)
                        except Exception as e:
                            logger.warning(f"Ajuste automático de vídeo falhou: {e}")
                        # Sincronizar entrypoints para OPNsense (login.html/login2.html)
                        self._sync_login_entrypoints(htdocs, force=force_login_sync)
                        # Se contiver player de vídeo, marcar caminho principal para proteção posterior
                        if htdocs == self.primary_htdocs:
                            try:
                                idx = os.path.join(htdocs, 'index.html')
                                if os.path.exists(idx):
                                    with open(idx,'r',encoding='utf-8',errors='ignore') as fh:
                                        c = fh.read()
                                    # Heurísticas ampliadas para detectar portal com vídeo
                                    video_markers = [
                                        'assets/videos/', 'assets/video/',  # diretórios comuns
                                        'videoPlayer.js', 'checkVideo.js',
                                        '<video', '.mp4', '.webm'
                                    ]
                                    self.video_portal_active = any(m in c for m in video_markers)
                                    if Config.DEBUG:
                                        present = [m for m in video_markers if m in c]
                                        logger.info(f"Detecção vídeo index.html: markers encontrados={present} -> ativo={self.video_portal_active}")
                                        # Logar primeiras linhas para inspeção
                                        preview = '\n'.join(c.splitlines()[:8])
                                        logger.info("Preview index.html (8 linhas):\n" + preview)
                            except Exception:
                                self.video_portal_active = False
                        logger.info(f"Instalação aplicada em: {htdocs} (arquivos escritos: {files_written})")
                    except Exception as e:
                        logger.error(f"Falha ao instalar em {htdocs}: {e}")
                return True
        except Exception as e:
            logger.error(f"Erro ao instalar: {e}")
            if backup_path and os.path.exists(backup_path):
                self._restore(backup_path)
            return False

    def check_video_assets(self) -> dict:
        """Verifica se existem arquivos de vídeo em assets/videos em cada htdocs e retorna estatísticas."""
        stats = {}
        try:
            for htdocs in self.htdocs_paths:
                videos_dir = os.path.join(htdocs, "assets", "videos")
                count = 0
                total_size = 0
                if os.path.isdir(videos_dir):
                    for name in os.listdir(videos_dir):
                        if name.lower().endswith((".mp4", ".webm", ".mov", ".mkv", ".avi")):
                            count += 1
                            try:
                                total_size += os.path.getsize(os.path.join(videos_dir, name))
                            except Exception:
                                pass
                stats[htdocs] = {"count": count, "total_size": total_size}
        except Exception as e:
            logger.warning(f"Falha ao verificar vídeos: {e}")
        return stats

    def _auto_update_video_source(self, htdocs: str):
        """Atualiza a tag <source src="assets/videos/..."> em index.html (e depois login/login2) para
        apontar para o arquivo de vídeo principal presente no diretório. Critério: maior arquivo .mp4/.webm/.mov/.mkv/.avi.
        Apenas altera se o index ainda não referencia o escolhido.
        """
        videos_dir = os.path.join(htdocs, "assets", "videos")
        index_path = os.path.join(htdocs, "index.html")
        if not (os.path.isdir(videos_dir) and os.path.isfile(index_path)):
            return
        # Coletar candidatos
        videos: list[tuple[str,int,float,int]] = []  # (nome, size, mtime, versao_detectada|-1)
        version_regex = re.compile(r'(?i)^(eld)(\d+)\.(mp4|webm|mov|mkv|avi)$')
        try:
            for name in os.listdir(videos_dir):
                if name.lower().endswith((".mp4", ".webm", ".mov", ".mkv", ".avi")):
                    p = os.path.join(videos_dir, name)
                    try:
                        sz = os.path.getsize(p)
                    except Exception:
                        sz = 0
                    try:
                        mt = os.path.getmtime(p)
                    except Exception:
                        mt = 0.0
                    m = version_regex.match(name)
                    ver = int(m.group(2)) if m else -1
                    videos.append((name, sz, mt, ver))
        except Exception as e:
            logger.warning(f"Falha ao listar vídeos em {videos_dir}: {e}")
            return
        if not videos:
            return
        # ---- Overrides explícitos (prioridade mais alta) ----
        # 1. Variável de ambiente POPPFIRE_VIDEO_NAME
        # 2. Arquivo assets/videos/selected_video.txt contendo exatamente o nome do arquivo
        override_name = None
        env_name = os.environ.get("POPPFIRE_VIDEO_NAME")
        if env_name:
            override_name = env_name.strip()
        else:
            sel_file = os.path.join(videos_dir, "selected_video.txt")
            if os.path.isfile(sel_file):
                try:
                    with open(sel_file, 'r', encoding='utf-8', errors='ignore') as sf:
                        line = sf.readline().strip()
                        if line:
                            override_name = line
                except Exception as e:
                    logger.warning(f"Falha ao ler selected_video.txt: {e}")
        chosen = None
        chosen_reason = None
        if override_name:
            # Normalizar: se não tiver extensão, tentar .mp4
            base_override = override_name
            if '.' not in os.path.basename(base_override):
                base_override_mp4 = base_override + '.mp4'
            else:
                base_override_mp4 = base_override
            # Procurar case-insensitive dentro da lista
            names_available = {v[0].lower(): v[0] for v in videos}
            for candidate in [base_override, base_override_mp4]:
                low = candidate.lower()
                if low in names_available:
                    chosen = names_available[low]
                    chosen_reason = f"override explícito ({candidate})"
                    break
            if not chosen and Config.DEBUG:
                logger.warning(f"Override de vídeo '{override_name}' não corresponde a nenhum arquivo existente. Prosseguindo com heurística.")
        # Estratégia de seleção:
        # 1. Se existir qualquer vídeo com padrão eldNN (case-insensitive), escolhe o de maior NN.
        # 2. Caso contrário, escolhe o de maior tamanho.
        if not chosen:
            eld_videos = [v for v in videos if v[3] >= 0]
            if eld_videos:
                eld_videos.sort(key=lambda x: (-x[3], -x[1], -x[2], x[0]))
                chosen = eld_videos[0][0]
                chosen_reason = f"maior versão eldNN (v{eld_videos[0][3]})"
            else:
                videos.sort(key=lambda x: (-x[1], -x[2], x[0]))
                chosen = videos[0][0]
                chosen_reason = "maior tamanho"
        try:
            with open(index_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"Não foi possível ler index.html para ajuste de vídeo: {e}")
            return
        if f"assets/videos/{chosen}" in content:
            # Já aponta corretamente
            if Config.DEBUG:
                logger.info(f"index.html já usa vídeo {chosen} ({chosen_reason})")
            return
        # Regex para primeira tag <source ... src="assets/videos/...">
        pattern = r'(<source\b[^>]*\bsrc=["\']assets/videos/)([^"\']+)(["\'][^>]*>)'
        try:
            new_content, n = re.subn(pattern, r'\1' + chosen + r'\3', content, count=1)
            if n == 0:
                # fallback: substituir eld01.mp4 se existir
                if "eld01.mp4" in content:
                    new_content = content.replace("eld01.mp4", chosen, 1)
                    n = 1
            if n > 0:
                try:
                    with open(index_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    logger.info(f"index.html atualizado para usar vídeo {chosen} ({chosen_reason})")
                    # Ajustar poster se existir arquivo correspondente (mesma base .jpg/.png)
                    base_no_ext = os.path.splitext(chosen)[0]
                    poster_candidates = [f"{base_no_ext}.jpg", f"{base_no_ext}.png"]
                    try:
                        with open(index_path, 'r', encoding='utf-8', errors='ignore') as f2:
                            idx2 = f2.read()
                        for pc in poster_candidates:
                            poster_path = f"assets/videos/{pc}"
                            full_poster = os.path.join(videos_dir, pc)
                            if os.path.exists(full_poster) and poster_path not in idx2:
                                # Trocar primeiro poster="assets/videos/algumacoisa.jpg"
                                new_idx2, pn = re.subn(r'(poster=["\']assets/videos/)([^"\']+)(["\'])', r'\1' + pc + r'\3', idx2, count=1)
                                if pn == 0 and "eld01.jpg" in idx2:
                                    new_idx2 = idx2.replace("eld01.jpg", pc, 1)
                                    pn = 1
                                if pn > 0:
                                    with open(index_path, 'w', encoding='utf-8') as f3:
                                        f3.write(new_idx2)
                                    logger.info(f"Poster atualizado para {pc}")
                                break
                    except Exception as e:
                        logger.warning(f"Ajuste de poster falhou: {e}")
                except Exception as e:
                    logger.warning(f"Falha ao gravar index.html ajustado: {e}")
            # Replicar para login/login2 se existirem (após ajuste do index)
            for ln in ["login.html", "login2.html"]:
                lp = os.path.join(htdocs, ln)
                if not os.path.isfile(lp):
                    continue
                try:
                    with open(lp, 'r', encoding='utf-8', errors='ignore') as f:
                        lc = f.read()
                    if f"assets/videos/{chosen}" in lc:
                        continue
                    lc2, n2 = re.subn(pattern, r'\1' + chosen + r'\3', lc, count=1)
                    if n2 == 0 and "eld01.mp4" in lc:
                        lc2 = lc.replace("eld01.mp4", chosen, 1)
                        n2 = 1
                    if n2 > 0 and lc2 != lc:
                        with open(lp, 'w', encoding='utf-8') as f:
                            f.write(lc2)
                        logger.info(f"{ln} atualizado para usar vídeo {chosen} ({chosen_reason})")
                except Exception as e:
                    logger.warning(f"Falha ao ajustar {ln}: {e}")
        except Exception as e:
            logger.warning(f"Regex de ajuste de vídeo falhou: {e}")

    def _fix_permissions(self, htdocs_path: str):
        try:
            # Tenta usar www:www se existir
            uid = gid = None
            try:
                uid = pwd.getpwnam('www').pw_uid
                gid = grp.getgrnam('www').gr_gid
            except Exception:
                uid = gid = None
            for root, dirs, files in os.walk(htdocs_path):
                for d in dirs:
                    os.chmod(os.path.join(root, d), 0o755)
                    if uid is not None and gid is not None:
                        try:
                            os.chown(os.path.join(root, d), uid, gid)
                        except Exception:
                            pass
                for f in files:
                    p = os.path.join(root, f)
                    os.chmod(p, 0o755 if f.endswith(('.php', '.py', '.sh')) else 0o644)
                    if uid is not None and gid is not None:
                        try:
                            os.chown(p, uid, gid)
                        except Exception:
                            pass
        except Exception as e:
            logger.warning(f"Permissões: {e}")

    def _cleanup_old_backups(self):
        try:
            entries = []
            for f in os.listdir(self.backups):
                if f.startswith('portal_backup_') and f.endswith('.zip'):
                    p = os.path.join(self.backups, f)
                    entries.append((p, os.path.getmtime(p)))
            entries.sort(key=lambda x: x[1])
            while len(entries) > Config.MAX_BACKUPS:
                old = entries.pop(0)
                os.remove(old[0])
                logger.info(f"Backup removido: {old[0]}")
        except Exception as e:
            logger.warning(f"Limpeza de backups: {e}")

    def _restore(self, backup_zip: str):
        try:
            htdocs = self.primary_htdocs
            if os.path.exists(htdocs):
                shutil.rmtree(htdocs)
            os.makedirs(htdocs, exist_ok=True)
            with zipfile.ZipFile(backup_zip, 'r') as z:
                z.extractall(htdocs)
            self._fix_permissions(htdocs)
        except Exception as e:
            logger.error(f"Erro ao restaurar: {e}")

    def _sync_login_entrypoints(self, htdocs: str, force: bool = False):
        """Algumas versões do captive portal usam login.html como entrada. Se o index contém player de vídeo,
        replicamos esse conteúdo para login.html e login2.html, preservando backups .bak.
        """
        try:
            index_path = os.path.join(htdocs, 'index.html')
            if not os.path.exists(index_path):
                return
            with open(index_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            # Heurística: detectar portal com vídeo pelos scripts ou forçar quando solicitado
            if force or ('checkVideo.js' in content) or ('videoPlayer.js' in content) or ('assets/videos/' in content):
                for name in ['login.html', 'login2.html']:
                    target = os.path.join(htdocs, name)
                    try:
                        if os.path.exists(target):
                            # Backup simples
                            bak = target + '.bak'
                            try:
                                shutil.copy2(target, bak)
                            except Exception:
                                pass
                        shutil.copy2(index_path, target)
                    except Exception as e:
                        logger.warning(f"Falha ao sincronizar {name}: {e}")
        except Exception as e:
            logger.warning(f"Sync entrypoints: {e}")

    def _clear_volt_cache(self):
        """Limpa o cache de templates compilados do Volt."""
        cache_dirs = [
            "/usr/local/opnsense/mvc/app/cache",
            "/var/cache/opnsense/mvc" # Algumas versões podem usar este
        ]
        for cache_dir in cache_dirs:
            if os.path.isdir(cache_dir):
                try:
                    count = 0
                    for f in os.listdir(cache_dir):
                        if f.endswith(".php") or "volt" in f:
                            try:
                                os.remove(os.path.join(cache_dir, f))
                                count += 1
                            except Exception:
                                pass
                    if count > 0:
                        logger.info(f"Cache Volt limpo em {cache_dir} ({count} arquivos removidos)")
                except Exception as e:
                    logger.warning(f"Erro ao limpar cache Volt em {cache_dir}: {e}")

    def _run_cmd(self, cmd: str) -> int:
        try:
            rc = os.system(cmd)
            logger.info(f"Executado: {cmd} (rc={rc})")
            return rc
        except Exception as e:
            logger.warning(f"Erro ao executar {cmd}: {e}")
            return 1

    def _discover_fetch_template_path(self) -> str | None:
        """Descobre dinamicamente o caminho usado pelo fetch_template.py do OPNsense.
        
        O fetch_template.py usa: source_directory = '%s/htdocs_default' % os.path.realpath(os.path.dirname(__file__))
        Então precisamos encontrar onde está o fetch_template.py e calcular o htdocs_default relativo a ele.
        """
        # Locais conhecidos onde o fetch_template.py pode estar
        fetch_template_locations = [
            "/usr/local/opnsense/scripts/captiveportal/fetch_template.py",  # OPNsense 25.x
            "/usr/local/opnsense/scripts/OPNsense/CaptivePortal/fetch_template.py",  # Versões antigas
        ]
        
        for fetch_path in fetch_template_locations:
            if os.path.exists(fetch_path):
                # Calcular htdocs_default relativo ao diretório do fetch_template.py
                script_dir = os.path.dirname(os.path.realpath(fetch_path))
                htdocs_default = os.path.join(script_dir, "htdocs_default")
                logger.info(f"fetch_template.py encontrado em: {fetch_path}")
                logger.info(f"htdocs_default calculado: {htdocs_default}")
                return htdocs_default
        
        # Fallback: buscar via grep se disponível
        try:
            cmd = "find /usr/local/opnsense -name 'fetch_template.py' -type f 2>/dev/null | head -1"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                fetch_path = result.stdout.strip()
                script_dir = os.path.dirname(os.path.realpath(fetch_path))
                htdocs_default = os.path.join(script_dir, "htdocs_default")
                logger.info(f"fetch_template.py descoberto via find: {fetch_path}")
                logger.info(f"htdocs_default calculado: {htdocs_default}")
                return htdocs_default
        except Exception as e:
            logger.warning(f"Busca via find falhou: {e}")
        
        return None

    def _get_all_template_paths(self) -> list:
        """Retorna lista de todos os caminhos de template que devem ser atualizados.
        
        Prioridade:
        1. Caminho descoberto dinamicamente via fetch_template.py (PRINCIPAL)
        2. Caminhos conhecidos hardcoded (fallback/compatibilidade)
        """
        paths = []
        
        # 1. Descoberta dinâmica (mais confiável)
        dynamic_path = self._discover_fetch_template_path()
        if dynamic_path:
            paths.append(dynamic_path)
        
        # 2. Caminhos conhecidos (para compatibilidade com diferentes versões)
        known_paths = [
            "/usr/local/opnsense/scripts/captiveportal/htdocs_default",  # OPNsense 25.x
            "/usr/local/opnsense/scripts/OPNsense/CaptivePortal/htdocs_default",  # Versões antigas
        ]
        
        for p in known_paths:
            if p not in paths:  # Evitar duplicatas
                paths.append(p)
        
        return paths

    def copy_to_default_template(self):
        """Copia TODO o conteúdo do portal atual para htdocs_default para garantir persistência.
        
        VERSÃO 3.1 - Auto-Discovery:
        - Descobre automaticamente o caminho correto usado pelo fetch_template.py
        - Copia para todos os caminhos conhecidos para máxima compatibilidade
        - Cria diretórios se não existirem
        - Faz backup do original na primeira execução
        """
        try:
            logger.info("=" * 60)
            logger.info("Iniciando sincronização de persistência (v3.1 - Auto-Discovery)")
            logger.info("=" * 60)
            
            src_dir = self.primary_htdocs
            if not os.path.isdir(src_dir):
                logger.error(f"Diretório fonte não existe: {src_dir}")
                return
            
            # Verificar se temos conteúdo para copiar
            src_files = os.listdir(src_dir) if os.path.isdir(src_dir) else []
            if not src_files:
                logger.warning(f"Diretório fonte vazio: {src_dir}")
                return
            
            logger.info(f"Fonte: {src_dir} ({len(src_files)} itens)")
            
            # Obter todos os caminhos de destino
            template_paths = self._get_all_template_paths()
            logger.info(f"Destinos identificados: {template_paths}")
            
            primary_path = template_paths[0] if template_paths else None
            success_count = 0
            
            for target_dir in template_paths:
                try:
                    is_primary = (target_dir == primary_path)
                    label = "[PRINCIPAL]" if is_primary else "[SECUNDÁRIO]"
                    
                    logger.info(f"{label} Processando: {target_dir}")
                    
                    # Criar diretório se não existir
                    if not os.path.isdir(target_dir):
                        logger.info(f"  Criando diretório: {target_dir}")
                        os.makedirs(target_dir, exist_ok=True)
                    
                    # Fazer backup do original na primeira execução (apenas para o principal)
                    backup_marker = os.path.join(target_dir, ".poppfire_backup_done")
                    if is_primary and not os.path.exists(backup_marker):
                        backup_dir = target_dir + ".original_backup"
                        if not os.path.exists(backup_dir) and os.path.isdir(target_dir) and os.listdir(target_dir):
                            try:
                                shutil.copytree(target_dir, backup_dir)
                                logger.info(f"  Backup original criado: {backup_dir}")
                            except Exception as e:
                                logger.warning(f"  Falha ao criar backup: {e}")
                        # Criar marker
                        try:
                            with open(backup_marker, 'w') as f:
                                f.write(f"Backup criado em: {datetime.now().isoformat()}\n")
                                f.write(f"Fonte: {src_dir}\n")
                        except Exception:
                            pass
                    
                    # Copiar arquivos (cp -Rf para preservar estrutura)
                    cmd = f"cp -Rf {src_dir}/* {target_dir}/"
                    rc = self._run_cmd(cmd)
                    
                    if rc == 0:
                        # Corrigir permissões
                        self._fix_permissions(target_dir)
                        
                        # Verificar se a cópia foi bem sucedida
                        test_file = os.path.join(target_dir, "index.html")
                        if os.path.exists(test_file):
                            try:
                                with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read(1000)
                                # Verificar marcadores do nosso template
                                markers = ['video', 'Portal de Acesso', 'poppfire', 'POPPFIRE']
                                found = [m for m in markers if m.lower() in content.lower()]
                                if found:
                                    logger.info(f"  ✓ Template customizado confirmado (markers: {found})")
                                    success_count += 1
                                else:
                                    logger.warning(f"  ⚠ Cópia OK mas markers não encontrados")
                                    success_count += 1  # Ainda conta como sucesso
                            except Exception as e:
                                logger.warning(f"  Verificação falhou: {e}")
                        else:
                            logger.warning(f"  ⚠ index.html não encontrado após cópia")
                    else:
                        logger.error(f"  ✗ Comando cp falhou (rc={rc})")
                        
                except Exception as e:
                    logger.error(f"  Erro ao processar {target_dir}: {e}")
            
            # Resumo final
            logger.info("-" * 40)
            if success_count > 0:
                logger.info(f"✓ Persistência aplicada em {success_count}/{len(template_paths)} destino(s)")
            else:
                logger.error("✗ Nenhum destino foi atualizado com sucesso!")
            
            # Diagnóstico extra: verificar o que o fetch_template.py vai usar
            if primary_path and os.path.isdir(primary_path):
                try:
                    files = os.listdir(primary_path)
                    idx = os.path.join(primary_path, "index.html")
                    if os.path.exists(idx):
                        size = os.path.getsize(idx)
                        logger.info(f"Diagnóstico: {primary_path}/index.html = {size} bytes")
                except Exception:
                    pass
            
            logger.info("Sincronização de persistência concluída (v3.1)")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Sync template default (v3.1): {e}")

    # ---- NOVO: Snapshot & Restore críticos ----
    def snapshot_critical_files(self):
        """Captura conteúdo bruto de arquivos críticos antes do start para possível reaplicação."""
        critical = {}
        base = self.primary_htdocs
        for name in ["index.html", "login.html", "login2.html"]:
            p = os.path.join(base, name)
            if os.path.exists(p):
                try:
                    with open(p, 'rb') as f:
                        critical[name] = f.read()
                except Exception as e:
                    logger.warning(f"Snapshot falhou {name}: {e}")
        self._critical_snapshot = critical
        if Config.DEBUG:
            logger.info(f"Snapshot crítico criado: {list(critical.keys())}")
        return critical

    def restore_critical_files(self):
        """Reaplica arquivos críticos a partir do snapshot em memória se existir."""
        if not self._critical_snapshot:
            logger.warning("Sem snapshot crítico para restaurar")
            return False
        base = self.primary_htdocs
        restored = []
        for name, data in self._critical_snapshot.items():
            try:
                p = os.path.join(base, name)
                with open(p, 'wb') as f:
                    f.write(data)
                restored.append(name)
            except Exception as e:
                logger.warning(f"Falha ao restaurar {name}: {e}")
        if restored:
            try:
                self._fix_permissions(base)
            except Exception:
                pass
            logger.info(f"Arquivos críticos reaplicados pós-start: {restored}")
            # Atualiza também template default apenas se estiver habilitado
            if Config.SYNC_DEFAULT_TEMPLATE:
                try:
                    self.copy_to_default_template()
                except Exception:
                    pass
            return True
        return False


class LocalAPI:
    """Interface mínima com a API local do OPNsense para encerrar sessões do captive portal."""

    def __init__(self):
        self.base = Config.LOCAL_API_URL.rstrip('/')
        self.auth = (Config.LOCAL_API_KEY, Config.LOCAL_API_SECRET)
        try:
            import urllib3  # type: ignore

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        except Exception:
            pass

    def disconnect_all_sessions(self) -> int:
        disconnected = 0
        try:
            list_url = f"{self.base}/captiveportal/session/list"
            logger.info(f"Consultando sessões ativas em {list_url}...")
            resp = requests.get(list_url, auth=self.auth, verify=False, timeout=10)
            if resp.status_code != 200:
                logger.warning(f"Falha ao listar sessões: {resp.status_code} - {resp.text}")
                return 0
            sessions = resp.json()
            if not sessions:
                logger.info("Nenhuma sessão ativa encontrada.")
                return 0
            disconnect_url = f"{self.base}/captiveportal/session/disconnect"
            logger.info(f"Desconectando {len(sessions)} sessão(ões) ativas...")
            for session in sessions:
                zone_id = session.get('zoneid')
                session_id = session.get('sessionId')
                user = session.get('userName', 'unknown')
                if zone_id is None or not session_id:
                    continue
                payload = {"zoneid": zone_id, "sessionId": session_id}
                try:
                    resp_disc = requests.post(disconnect_url, json=payload, auth=self.auth, verify=False, timeout=5)
                    if resp_disc.status_code == 200:
                        try:
                            logger.info(f"Sessão desconectada: user={user}, resp={resp_disc.json()}")
                        except ValueError:
                            logger.info(f"Sessão desconectada: user={user}")
                        disconnected += 1
                    else:
                        logger.warning(f"Falha ao desconectar {user}: {resp_disc.status_code}")
                except Exception as e:
                    logger.warning(f"Erro ao desconectar sessão {session_id}: {e}")
        except Exception as e:
            logger.error(f"Erro na API local: {e}")
        return disconnected


class Updater:
    def __init__(self, *, force_check: bool = False):
        self.state = PortalState()
        self.api = API()
        self.installer = Installer()
        self.force_check = force_check
        self.local_api = LocalAPI() if Config.DISCONNECT_SESSIONS_ON_UPDATE else None

    def run(self):
        try:
            logger.info("=== Verificação de atualização do portal ===")
            if not self.force_check and not self.state.should_check():
                logger.info("Verificação pulada (intervalo mínimo)")
                return True
            if self.force_check:
                logger.info("Verificação forçada: ignorando intervalo mínimo")
            st = self.api.portal_status()
            portal_type = st.get('portal_type')
            server_hash = st.get('portal_hash')
            local_hash = self.installer.current_hash()
            stored_zip_hash = self.state.data.get('current_zip_hash')
            stored_local_hash = self.state.data.get('current_local_hash')
            logger.info(
                "Tipo: %s | Hash servidor: %s | Hash local: %s | Zip salvo: %s | Local salvo: %s",
                portal_type,
                server_hash,
                local_hash,
                stored_zip_hash,
                stored_local_hash,
            )
            
            # Verificar se há portal disponível
            if portal_type is None:
                logger.info("Nenhum portal disponível no servidor - aguardando ativação")
                # Atualizar estado indicando que não há portal
                self.state.data.update({
                    'current_portal_type': None,
                    'current_hash': None,
                    'current_zip_hash': None,
                    'current_local_hash': None,
                    'last_check': datetime.now().isoformat()
                })
                self.state.save()
                return True
            
            needs_zip_change = bool(server_hash) and (server_hash != stored_zip_hash)
            local_missing = local_hash is None
            type_changed = self.state.data.get('current_portal_type') != portal_type
            if Config.ENFORCE_LOCAL_DRIFT:
                local_drift = bool(local_hash and stored_local_hash and local_hash != stored_local_hash)
            else:
                local_drift = False
            
            needs = needs_zip_change or local_missing or type_changed or local_drift
            
            # Watchdog: Se o serviço não estiver rodando, força atualização/restart
            if not self._check_zone0_running():
                logger.warning("Watchdog: Serviço Captive Portal não detectado na porta 8000. Forçando reinicialização.")
                needs = True

            if self.force_check:
                logger.info("Modo FORCE ativado: Forçando reinstalação independente de hashes.")
                needs = True

            if not needs:
                # Atualiza estado com hashes atuais para evitar comparações futuras inconsistentes
                self.state.data['current_zip_hash'] = stored_zip_hash or server_hash
                self.state.data['current_local_hash'] = local_hash
                self.state.data['current_hash'] = local_hash
                self.state.save()
                logger.info("Sem alterações")
                return True
            logger.info(f"Atualizando portal: {portal_type}")
            zip_bytes = self.api.download_zip(portal_type)
            # Parar captive portal antes de alterar arquivos para evitar trava/substituições
            self._stop_captive_portal()
            install_ok = self.installer.install_zip_bytes(zip_bytes, force_login_sync=(portal_type == 'with_video'))
            # Opcionalmente sincroniza template default (agora ativado por padrão)
            try:
                if install_ok and Config.SYNC_DEFAULT_TEMPLATE:
                    self.installer.copy_to_default_template()
            except Exception:
                pass
            # Hash antes de subir
            before_hash = self.installer.current_hash()
            # Snapshot crítico antes de subir
            critical_snapshot = self.installer.snapshot_critical_files()
            self._start_captive_portal()
            if install_ok and self.local_api:
                time.sleep(5)
                try:
                    disconnected = self.local_api.disconnect_all_sessions()
                    logger.info(f"Sessões derrubadas após atualização: {disconnected}")
                except Exception as e:
                    logger.warning(f"Falha ao desconectar sessões: {e}")
            # Pequeno atraso para possível sobrescrita
            time.sleep(1)
            after_hash = self.installer.current_hash()
            if install_ok and before_hash and after_hash and before_hash != after_hash:
                logger.warning("Conteúdo do portal foi modificado após start (possível sobrescrita pelo template). Iniciando reaplicação de arquivos críticos.")
                # Diagnóstico: comparar tamanho/assinatura dos críticos
                try:
                    diffs = []
                    for name in ["index.html", "login.html", "login2.html"]:
                        orig = critical_snapshot.get(name)
                        path = os.path.join(self.installer.primary_htdocs, name)
                        if orig and os.path.exists(path):
                            with open(path, 'rb') as f:
                                cur = f.read()
                            if hashlib.sha256(orig).hexdigest() != hashlib.sha256(cur).hexdigest():
                                diffs.append(name)
                    if diffs:
                        logger.info(f"Arquivos alterados pelo start detectados: {diffs}")
                except Exception as e:
                    logger.warning(f"Diff crítico falhou: {e}")
                # Reaplicar snapshot
                reapplied = self.installer.restore_critical_files()
                if reapplied:
                    # Recalcular hash global após reaplicação
                    after_hash2 = self.installer.current_hash()
                    logger.info(f"Hash após reaplicação: {after_hash2}")
                else:
                    logger.warning("Reaplicação de arquivos críticos não ocorreu (snapshot vazio ou falha)")
            if install_ok:
                new_hash = self.installer.current_hash()
                self.state.data.update({
                    'current_portal_type': portal_type,
                    'current_hash': new_hash,
                    'current_zip_hash': server_hash,
                    'current_local_hash': new_hash,
                    'last_update': datetime.now().isoformat(),
                    'update_count': self.state.data.get('update_count', 0) + 1
                })
                logger.info(f"Portal atualizado com sucesso! Novo hash: {new_hash}")
                # Sanidade: verificar presença de vídeos em 'with_video'
                if portal_type == 'with_video':
                    stats = self.installer.check_video_assets()
                    for path, s in stats.items():
                        logger.info(f"Verificação de vídeos em {path}: {s['count']} arquivo(s), {s['total_size']} bytes")
                    if not any(s.get('count', 0) > 0 for s in stats.values()):
                        logger.warning("Portal 'with_video' sem vídeos em assets/videos — verifique a geração do ZIP no servidor")
                self.api.report('success', new_hash, portal_type)
                # Reinício adicional não é necessário quando paramos/iniciamos explicitamente
            else:
                raise Exception("Falha na instalação do portal")
            self.state.save()
            return True
        except Exception as e:
            msg = f"Erro durante atualização: {e}"
            logger.error(msg)
            self.state.add_error(msg)
            self.state.save()
            try:
                current_hash = self.installer.current_hash() or 'unknown'
                portal_type = self.state.data.get('current_portal_type') or 'unknown'
                self.api.report('failed', current_hash, portal_type, msg)
            except Exception:
                pass
            return False

    def _run_cmd(self, cmd: str) -> int:
        try:
            rc = os.system(cmd)
            logger.info(f"Executado: {cmd} (rc={rc})")
            return rc
        except Exception as e:
            logger.warning(f"Erro ao executar {cmd}: {e}")
            return 1

    def _cleanup_pid_and_processes(self):
        """Limpa processos travados e arquivos PID órfãos da Zona 0 de forma agressiva."""
        pid_file = "/var/run/lighttpd-cp-zone-0.pid"
        
        logger.info("Iniciando limpeza profunda de processos e PIDs da Zona 0...")

        # 1. Tentar parar via sistema (best effort)
        self._run_cmd("configctl captiveportal stop")
        time.sleep(1)

        # 2. Kill forçado (SIGKILL) em qualquer processo lighttpd da zona 0
        try:
            # pgrep -f busca na linha de comando completa
            cmd = "pgrep -f 'lighttpd-cp-zone-0.conf'"
            try:
                out = subprocess.check_output(cmd, shell=True).decode().strip()
                if out:
                    pids = out.split()
                    for p in pids:
                        logger.info(f"Matando processo lighttpd zona 0 (PID {p})...")
                        try:
                            os.kill(int(p), signal.SIGKILL)
                        except ProcessLookupError:
                            pass # Já morreu
                        except Exception as e:
                            logger.warning(f"Falha ao matar PID {p}: {e}")
            except subprocess.CalledProcessError:
                pass # Nenhum processo encontrado
        except Exception as e:
            logger.warning(f"Erro na busca de processos: {e}")

        # 3. Remoção incondicional do arquivo PID
        # Se matamos os processos acima, qualquer PID file restante é inválido.
        if os.path.exists(pid_file):
            try:
                logger.info(f"Removendo arquivo PID residual: {pid_file}")
                os.remove(pid_file)
            except Exception as e:
                logger.warning(f"Erro ao remover PID file: {e}")

    def _stop_captive_portal(self):
        self._cleanup_pid_and_processes()

    def _start_captive_portal(self):
        # Limpeza prévia agressiva
        self._cleanup_pid_and_processes()
        
        logger.info("Tentando iniciar Captive Portal (Método Padrão)...")
        self._run_cmd("configctl captiveportal start")
        
        # Aguardar e verificar (loop de 5s)
        for _ in range(5):
            time.sleep(1)
            if self._check_zone0_running():
                logger.info("Captive Portal iniciado com sucesso (Método Padrão).")
                return

        logger.warning("Método padrão falhou (timeout ou erro). Tentando Método Direto...")
        
        # Limpeza novamente para garantir que não ficou lixo da tentativa anterior
        self._cleanup_pid_and_processes()
        
        # Workaround: Iniciar direto o binário apontando para a config
        cmd_direct = "/usr/local/sbin/lighttpd -f /var/etc/lighttpd-cp-zone-0.conf"
        self._run_cmd(cmd_direct)
        
        for _ in range(5):
            time.sleep(1)
            if self._check_zone0_running():
                logger.info("Captive Portal iniciado com sucesso (Método Direto).")
                return
                
        logger.error("FALHA CRÍTICA: Captive Portal não iniciou com nenhum método.")

    def _check_zone0_running(self) -> bool:
        """Verifica se a porta 8000 (padrão zona 0) está ouvindo ou se o processo existe."""
        try:
            # Check porta 8000
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', 8000))
            sock.close()
            if result == 0:
                return True
        except Exception:
            pass
            
        # Fallback: check processo
        try:
            cmd = "pgrep -f 'lighttpd-cp-zone-0.conf'"
            return subprocess.call(cmd, shell=True) == 0
        except Exception:
            return False

    def _lighttpd_enabled_or_running(self) -> bool:
        try:
            # Verifica processo
            try:
                out = subprocess.run(["pgrep", "-x", "lighttpd"], capture_output=True)
                if out.returncode == 0:
                    return True
            except Exception:
                pass
            # Verifica rc.conf
            try:
                if os.path.exists("/etc/rc.conf"):
                    with open("/etc/rc.conf", "r") as f:
                        content = f.read()
                        if "lighttpd_enable=\"YES\"" in content:
                            return True
            except Exception:
                pass
        except Exception:
            pass
        return False


def main():
    parser = argparse.ArgumentParser(description="Atualizador do portal captive POPPFIRE")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignora o intervalo mínimo e força a verificação agora",
    )
    parser.add_argument(
        "--sync-default-template",
        action="store_true",
        help="Copia arquivos do portal atual para o template default do OPNsense",
    )
    parser.add_argument(
        "--enforce-local-drift",
        action="store_true",
        help="Força reinstalação quando arquivos locais foram alterados manualmente",
    )
    parser.add_argument(
        "--skip-session-disconnect",
        action="store_true",
        help="Não derruba sessões após atualizar o portal",
    )
    args = parser.parse_args()

    if args.sync_default_template:
        Config.SYNC_DEFAULT_TEMPLATE = True
    if args.enforce_local_drift:
        Config.ENFORCE_LOCAL_DRIFT = True
    if args.skip_session_disconnect:
        Config.DISCONNECT_SESSIONS_ON_UPDATE = False

    try:
        ok = Updater(force_check=args.force).run()
        sys.exit(0 if ok else 1)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

