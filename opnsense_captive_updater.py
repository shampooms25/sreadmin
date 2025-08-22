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
                        # Sincronizar entrypoints para OPNsense (login.html/login2.html)
                        self._sync_login_entrypoints(htdocs, force=force_login_sync)
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
            # Sempre tentar subir novamente o captive portal, mesmo em caso de falha
            self._start_captive_portal()
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
