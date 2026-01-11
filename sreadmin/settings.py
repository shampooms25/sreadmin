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
