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
    MIN_UPDATE_INTERVAL = 300  # 5 minutos
    MAX_BACKUPS = 5
    DEBUG = True  # Ativa logs extras de diagnóstico


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
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Erro ao carregar estado: {e}")
        return {
            "current_portal_type": None,
            "current_hash": None,
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
                resp = requests.request(method, url, headers=self.headers, timeout=Config.TIMEOUT, **kwargs)
                if resp.status_code == 401:
                    raise Exception("Token de autenticação inválido")
                resp.raise_for_status()
                return resp
            except requests.RequestException as e:
                if i == Config.RETRY_ATTEMPTS - 1:
                    raise
                logger.warning(f"Tentativa {i+1} falhou: {e}")
        raise Exception("Falha ao chamar API")

    def portal_status(self):
        return self._req('/portal/status/').json()

    def download_zip(self, portal_type: str):
        return self._req(f"/portal/download/?type={portal_type}").content

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

    def copy_to_default_template(self):
        """Copia index/login/login2 para htdocs_default para evitar que OPNsense reponha template antigo."""
        try:
            default_dir = "/usr/local/opnsense/scripts/OPNsense/CaptivePortal/htdocs_default"
            if not os.path.isdir(default_dir):
                return
            src_dir = self.primary_htdocs
            for name in ["index.html","login.html","login2.html"]:
                s = os.path.join(src_dir, name)
                if os.path.exists(s):
                    d = os.path.join(default_dir, name)
                    try:
                        shutil.copy2(s, d)
                    except Exception as e:
                        logger.warning(f"Falha ao copiar {name} para template default: {e}")
            logger.info("Templates default sincronizados")
        except Exception as e:
            logger.warning(f"Sync template default: {e}")

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
            # Atualiza também template default para evitar próxima sobrescrita
            try:
                self.copy_to_default_template()
            except Exception:
                pass
            return True
        return False


class Updater:
    def __init__(self):
        self.state = PortalState()
        self.api = API()
        self.installer = Installer()

    def run(self):
        try:
            logger.info("=== Verificação de atualização do portal ===")
            if not self.state.should_check():
                logger.info("Verificação pulada (intervalo mínimo)")
                return True
            st = self.api.portal_status()
            portal_type = st.get('portal_type')
            server_hash = st.get('portal_hash')
            local_hash = self.installer.current_hash()
            logger.info(f"Tipo: {portal_type} | Hash servidor: {server_hash} | Hash local: {local_hash}")
            needs = (local_hash != server_hash) or (self.state.data.get('current_portal_type') != portal_type) or (local_hash is None)
            if not needs:
                self.state.save()
                logger.info("Sem alterações")
                return True
            logger.info(f"Atualizando portal: {portal_type}")
            zip_bytes = self.api.download_zip(portal_type)
            # Parar captive portal antes de alterar arquivos para evitar trava/substituições
            self._stop_captive_portal()
            install_ok = self.installer.install_zip_bytes(zip_bytes, force_login_sync=(portal_type == 'with_video'))
            # Proteger index copiando também para htdocs_default antes de subir
            try:
                if install_ok and getattr(self.installer, 'video_portal_active', False):
                    self.installer.copy_to_default_template()
            except Exception:
                pass
            # Hash antes de subir
            before_hash = self.installer.current_hash()
            # Snapshot crítico antes de subir
            critical_snapshot = self.installer.snapshot_critical_files()
            self._start_captive_portal()
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

    def _stop_captive_portal(self):
        # Para o captive portal antes da atualização
        rc = self._run_cmd("configctl captiveportal stop")
        if rc != 0:
            self._run_cmd("service captiveportal stop")
        time.sleep(1)

    def _start_captive_portal(self):
        # Inicia o captive portal após a atualização
        rc = self._run_cmd("configctl captiveportal start")
        if rc != 0:
            self._run_cmd("service captiveportal start")
        time.sleep(1)

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
    try:
        ok = Updater().run()
        sys.exit(0 if ok else 1)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
