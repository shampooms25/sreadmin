"""
Script para limpar imports duplicados no starlink_api.py
"""

import re

def clean_imports():
    with open('painel/starlink_api.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remover imports locais redundantes de datetime
    # Manter apenas o import global no topo
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Pular linhas que são imports locais de datetime (com indentação)
        if re.match(r'^[\s]+from datetime import datetime, timedelta$', line):
            print(f"Removendo linha: {line.strip()}")
            continue
        cleaned_lines.append(line)
    
    # Escrever arquivo limpo
    with open('painel/starlink_api.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))
    
    print("✅ Imports duplicados removidos!")

if __name__ == "__main__":
    clean_imports()
