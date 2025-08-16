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
import tempfile
from datetime import datetime


class Config:
    # Ajuste para seu ambiente de produção
    API_BASE_URL = "https://paineleld.poppnet.com.br"
    API_TOKEN = "TROQUE_PELO_TOKEN"  # defina o token válido

    PORTAL_HTDOCS_PATH = "/var/captiveportal/zone0/htdocs"
    STATE_FILE = "/var/db/poppfire_portal_state.json"
    BACKUP_DIR = "/var/db/poppfire_portal_backups"
    LOG_FILE = "/var/log/poppfire_portal_updater.log"

    TIMEOUT = 30
    RETRY_ATTEMPTS = 3
    MIN_UPDATE_INTERVAL = 300  # 5 minutos
    MAX_BACKUPS = 5


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
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
        self.htdocs = Config.PORTAL_HTDOCS_PATH
        self.backups = Config.BACKUP_DIR
        os.makedirs(self.backups, exist_ok=True)

    def current_hash(self):
        if not os.path.exists(self.htdocs):
            return None
        h = hashlib.sha256()
        for root, dirs, files in os.walk(self.htdocs):
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
        if not os.path.exists(self.htdocs):
            return None
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(self.backups, f"portal_backup_{ts}.zip")
        try:
            with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
                for root, _, files in os.walk(self.htdocs):
                    for f in files:
                        p = os.path.join(root, f)
                        arc = os.path.relpath(p, self.htdocs)
                        z.write(p, arc)
            self._cleanup_old_backups()
            return path
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            return None

    def install_zip_bytes(self, zip_bytes: bytes):
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
                if os.path.exists(self.htdocs):
                    shutil.rmtree(self.htdocs)
                os.makedirs(self.htdocs, exist_ok=True)
                for root, _, files in os.walk(extract):
                    for f in files:
                        src = os.path.join(root, f)
                        rel = os.path.relpath(src, extract)
                        dst = os.path.join(self.htdocs, rel)
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        shutil.copy2(src, dst)
                self._fix_permissions()
                return True
        except Exception as e:
            logger.error(f"Erro ao instalar: {e}")
            if backup_path and os.path.exists(backup_path):
                self._restore(backup_path)
            return False

    def _fix_permissions(self):
        try:
            for root, dirs, files in os.walk(self.htdocs):
                for d in dirs:
                    os.chmod(os.path.join(root, d), 0o755)
                for f in files:
                    p = os.path.join(root, f)
                    os.chmod(p, 0o755 if f.endswith(('.php', '.py', '.sh')) else 0o644)
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
            if os.path.exists(self.htdocs):
                shutil.rmtree(self.htdocs)
            os.makedirs(self.htdocs, exist_ok=True)
            with zipfile.ZipFile(backup_zip, 'r') as z:
                z.extractall(self.htdocs)
            self._fix_permissions()
        except Exception as e:
            logger.error(f"Erro ao restaurar: {e}")


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
            if self.installer.install_zip_bytes(zip_bytes):
                new_hash = self.installer.current_hash()
                self.state.data.update({
                    'current_portal_type': portal_type,
                    'current_hash': new_hash,
                    'last_update': datetime.now().isoformat(),
                    'update_count': self.state.data.get('update_count', 0) + 1
                })
                self.api.report('success', new_hash, portal_type)
                self._restart_services()
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

    def _restart_services(self):
        try:
            cmds = [
                "/usr/local/etc/rc.d/lighttpd restart",
                "configctl captiveportal restart"
            ]
            for c in cmds:
                try:
                    os.system(c)
                    logger.info(f"Executado: {c}")
                except Exception as e:
                    logger.warning(f"Erro ao executar {c}: {e}")
        except Exception as e:
            logger.warning(f"Erro no restart de serviços: {e}")


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
