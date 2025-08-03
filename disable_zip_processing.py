"""
Script para desabilitar temporariamente o processamento de ZIP
e isolar o problema de upload
"""

import os
import sys

def main():
    print("🔧 DESABILITANDO PROCESSAMENTO DE ZIP TEMPORARIAMENTE")
    print("=" * 55)
    
    # Caminho para o arquivo models.py
    models_path = "/var/www/sreadmin/painel/models.py"
    
    if not os.path.exists(models_path):
        print(f"❌ Arquivo não encontrado: {models_path}")
        return
    
    # Ler o arquivo
    with open(models_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fazer backup
    backup_path = f"{models_path}.backup"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup criado: {backup_path}")
    
    # Comentar a linha problemática
    lines = content.split('\n')
    modified = False
    
    for i, line in enumerate(lines):
        # Procurar pela linha que chama o ZipManagerService
        if 'ZipManagerService.update_zip_with_video' in line and not line.strip().startswith('#'):
            lines[i] = f"                            # TEMPORARIAMENTE DESABILITADO: {line.strip()}"
            modified = True
            print(f"✅ Linha {i+1} comentada: {line.strip()}")
    
    if modified:
        # Salvar arquivo modificado
        new_content = '\n'.join(lines)
        with open(models_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Arquivo modificado salvo")
        
        print(f"\n🧪 TESTE AGORA:")
        print(f"   1. Reiniciar Apache: sudo systemctl restart apache2")
        print(f"   2. Testar upload em: https://paineleld.poppnet.com.br/admin/")
        print(f"   3. Se funcionar, o problema está no processamento do ZIP")
        
        print(f"\n🔄 PARA REVERTER:")
        print(f"   cp {backup_path} {models_path}")
        print(f"   sudo systemctl restart apache2")
        
    else:
        print("❌ Linha não encontrada para comentar")

if __name__ == "__main__":
    main()
