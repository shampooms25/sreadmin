#!/usr/bin/env python3
"""
Script para limpar o cache de recarga automática
"""

import os
import sys
import django
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import clear_auto_recharge_cache

def clear_cache():
    """Limpa o cache de recarga automática"""
    print("🗑️  Limpando cache de recarga automática...")
    clear_auto_recharge_cache()
    print("✅ Cache limpo com sucesso!")

if __name__ == "__main__":
    clear_cache()
