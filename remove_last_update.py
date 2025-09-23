#!/usr/bin/env python3
"""Script para remover todas as referências a 'last_update' do starlink_api.py"""

import re

def remove_last_update_references():
    """Remove todas as referencias a last_update do arquivo"""
    
    with open('painel/starlink_api.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Padrão para remover linhas que contêm last_update
    patterns = [
        # Remove linhas como: "last_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        r',\s*"last_update":\s*datetime\.now\(\)\.strftime\("[^"]+"\)',
        # Remove linhas como: "last_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        r'"last_update":\s*datetime\.now\(\)\.strftime\("[^"]+"\),?',
        # Remove trailing comma antes de }
        r',(\s*})',
    ]
    
    original_content = content
    
    for pattern in patterns:
        content = re.sub(pattern, r'\1' if '\\1' in pattern else '', content)
    
    # Fix any double commas that might have been created
    content = re.sub(r',,', ',', content)
    
    # Write back to file
    with open('painel/starlink_api.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    changes = len(original_content) != len(content)
    if changes:
        print("✅ Referências a 'last_update' removidas do starlink_api.py")
    else:
        print("ℹ️  Nenhuma alteração necessária")
    
    return changes

if __name__ == "__main__":
    remove_last_update_references()
