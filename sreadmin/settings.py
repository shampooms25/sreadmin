"""Settings entrypoint.

Este arquivo existe para padronizar o DJANGO_SETTINGS_MODULE em todos os ambientes.

- Em produção/dev, o esperado é ter `sreadmin/settings_local.py` (não versionado) com
  SECRET_KEY, DATABASES, ALLOWED_HOSTS etc.
- O template fica em `sreadmin/settings_local.py.template`.

Motivo: evitar conflitos de `git pull` e erros como "No module named 'sreadmin.settings'".
"""

try:
    from .settings_local import *  # noqa: F401,F403
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "Arquivo de configuração ausente: crie 'sreadmin/settings_local.py' (copie de "
        "'sreadmin/settings_local.py.template')"
    ) from exc

# Alguns ambientes antigos podem ter um settings_local.py incompleto.
# Como estes apps são parte do projeto, garantimos que existam em INSTALLED_APPS.
_required_apps = [
    'painel',
    'captive_portal',
    'boxes',
    'starlink_allowlist',
]

if 'INSTALLED_APPS' in globals():
    for _app in _required_apps:
        if _app not in INSTALLED_APPS:
            INSTALLED_APPS.append(_app)
