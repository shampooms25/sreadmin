#!/usr/bin/env python3
"""
Script para remover todas as referências a 'last_update' do arquivo starlink_api.py
"""

import re

def fix_starlink_api():
    api_file = 'painel/starlink_api.py'
    
    try:
        with open(api_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📝 Arquivo original: {len(content)} caracteres")
        
        # Padrões para remover
        patterns = [
            # Remove linhas completas com last_update
            r'^\s*"last_update":\s*[^,\n]+,?\s*$',
            r'^\s*\'last_update\':\s*[^,\n]+,?\s*$',
            # Remove campos last_update de dicionários
            r'"last_update":\s*[^,}]+,?\s*',
            r'\'last_update\':\s*[^,}]+,?\s*',
            # Remove variáveis last_update
            r'last_update\s*=\s*[^,\n]+',
            r'last_update_recent\s*=\s*[^\n]+',
            # Remove condicionais com last_update (mas mantém outras partes)
            r'if\s+last_update:[^\n]*\n(\s+[^\n]+\n)*',
            # Remove get de last_update
            r'\.get\([\'"]last_update[\'"][^)]*\)',
        ]
        
        modified_content = content
        changes = 0
        
        for pattern in patterns:
            before = modified_content
            modified_content = re.sub(pattern, '', modified_content, flags=re.MULTILINE)
            if before != modified_content:
                changes += 1
                print(f"✅ Aplicado padrão: {pattern[:50]}...")
        
        # Remove linhas vazias extras
        modified_content = re.sub(r'\n\s*\n\s*\n', '\n\n', modified_content)
        
        # Remove vírgulas duplas
        modified_content = re.sub(r',\s*,', ',', modified_content)
        
        # Remove vírgulas antes de }
        modified_content = re.sub(r',\s*}', '}', modified_content)
        
        print(f"📝 Arquivo modificado: {len(modified_content)} caracteres")
        print(f"🔄 {changes} padrões aplicados")
        
        # Backup do arquivo original
        import shutil
        shutil.copy(api_file, f"{api_file}.backup")
        print(f"💾 Backup criado: {api_file}.backup")
        
        # Salva o arquivo modificado
        with open(api_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print(f"✅ Arquivo {api_file} atualizado")
        
        # Verifica se ainda há referências
        remaining = modified_content.count('last_update')
        print(f"📊 Referências restantes a 'last_update': {remaining}")
        
        if remaining > 0:
            # Mostra as linhas que ainda contêm last_update
            lines = modified_content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'last_update' in line:
                    print(f"   Linha {i}: {line.strip()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao processar arquivo: {e}")
        return False

if __name__ == "__main__":
    print("🧹 Iniciando limpeza de referências 'last_update'...")
    if fix_starlink_api():
        print("✅ Limpeza concluída com sucesso!")
    else:
        print("❌ Falha na limpeza!")
