#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Mensagem mais clara quando settings_local.py não existe.
    try:
        __import__(os.environ['DJANGO_SETTINGS_MODULE'])
    except ModuleNotFoundError as exc:
        if str(exc).endswith("settings_local'") or "settings_local" in str(exc):
            raise ModuleNotFoundError(
                "Configuração local ausente. Crie 'sreadmin/settings_local.py' (copie de "
                "'sreadmin/settings_local.py.template')."
            ) from exc
        raise
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
