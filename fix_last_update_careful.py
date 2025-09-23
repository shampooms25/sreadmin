#!/usr/bin/env python3
"""
Script para remover APENAS as referências a "last_update" (não last_updated) do arquivo starlink_api.py
"""

import re

def fix_starlink_api_careful():
    api_file = 'painel/starlink_api.py'
    
    try:
        with open(api_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"📝 Arquivo original: {len(lines)} linhas")
        
        # Procurar por linhas que contêm "last_update": (mas não "last_updated")
        new_lines = []
        removed_count = 0
        
        for i, line in enumerate(lines):
            # Remover linhas que contêm especificamente "last_update": (não "last_updated")
            if '"last_update":' in line or "'last_update':" in line:
                print(f"   Removendo linha {i+1}: {line.strip()}")
                removed_count += 1
                continue
            
            new_lines.append(line)
        
        print(f"📝 Linhas removidas: {removed_count}")
        print(f"📝 Arquivo modificado: {len(new_lines)} linhas")
        
        # Verifica que não removeu nada importante
        content = ''.join(new_lines)
        
        # Garantir que funções importantes estão presentes
        important_funcs = [
            'def get_enhanced_service_line_status',
            'def determine_availability_status',
            'def generate_simulated_telemetry_data'
        ]
        
        for func in important_funcs:
            if func not in content:
                print(f"❌ ERRO: Função importante removida: {func}")
                return False
            else:
                print(f"✅ Função preservada: {func}")
        
        # Salva o arquivo modificado
        with open(api_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print(f"✅ Arquivo {api_file} atualizado")
        
        # Verifica se ainda há referências problemáticas
        remaining_last_update = content.count('"last_update":')
        remaining_last_update += content.count("'last_update':")
        print(f"📊 Referências restantes a 'last_update': {remaining_last_update}")
        
        # Verifica que last_updated ainda está lá (deve ter 1 ou 2 referências)
        remaining_last_updated = content.count('last_updated')
        print(f"📊 Referências a 'last_updated' (devem permanecer): {remaining_last_updated}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao processar arquivo: {e}")
        return False

if __name__ == "__main__":
    print("🧹 Iniciando limpeza cuidadosa de 'last_update'...")
    if fix_starlink_api_careful():
        print("✅ Limpeza concluída com sucesso!")
    else:
        print("❌ Falha na limpeza!")
