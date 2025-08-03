#!/usr/bin/env python3
"""
Script para aplicar correção definitiva no upload
Remove temporariamente o processamento de notificações e ZIP
"""

import os
import sys

def main():
    print("🔧 APLICANDO CORREÇÃO DEFINITIVA - UPLOAD SIMPLIFICADO")
    print("=" * 55)
    
    project_path = "/var/www/sreadmin"
    models_path = f"{project_path}/painel/models.py"
    
    if not os.path.exists(models_path):
        print(f"❌ Arquivo não encontrado: {models_path}")
        return
    
    # Ler arquivo atual
    with open(models_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fazer backup
    backup_path = f"{models_path}.before_fix"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup criado: {backup_path}")
    
    # Novo método save simplificado
    new_save_method = '''    def save(self, *args, **kwargs):
        # Verificar se é um novo registro
        is_new = self.pk is None
        
        # Calcular tamanho do arquivo em MB
        if self.video:
            self.tamanho = round(self.video.size / (1024 * 1024), 2)
        
        # Salvar o modelo SEM processamento adicional (temporário)
        super().save(*args, **kwargs)
        
        # TEMPORARIAMENTE REMOVIDO: processamento de notificações e ZIP
        # para resolver problema de permissão em '/videos'
        
        if is_new and self.video:
            print(f"✅ Upload realizado: {self.video.name} ({self.tamanho}MB)")'''
    
    # Encontrar e substituir o método save
    lines = content.split('\n')
    new_lines = []
    inside_save_method = False
    save_indent = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Detectar início do método save
        if 'def save(self, *args, **kwargs):' in line:
            inside_save_method = True
            save_indent = len(line) - len(line.lstrip())
            
            # Adicionar o novo método save
            new_lines.append(new_save_method)
            
            # Pular todas as linhas do método save atual
            i += 1
            while i < len(lines):
                current_line = lines[i]
                current_indent = len(current_line) - len(current_line.lstrip()) if current_line.strip() else 0
                
                # Se chegou a uma linha com mesmo indentação ou menor, saiu do método
                if current_line.strip() and current_indent <= save_indent:
                    inside_save_method = False
                    break
                i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    # Salvar arquivo modificado
    new_content = '\n'.join(new_lines)
    with open(models_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Método save() simplificado aplicado")
    
    print(f"\n🧪 TESTE AGORA:")
    print(f"   1. sudo systemctl restart apache2")
    print(f"   2. Testar upload: https://paineleld.poppnet.com.br/admin/")
    print(f"   3. Se funcionar, o problema estava no processamento adicional")
    
    print(f"\n🔄 PARA REVERTER (quando quiser):")
    print(f"   cp {backup_path} {models_path}")
    print(f"   sudo systemctl restart apache2")
    
    print(f"\n💡 SE FUNCIONOU:")
    print(f"   - Upload básico está OK")
    print(f"   - Problema estava no processamento de ZIP/notificações")
    print(f"   - Podemos reativar gradualmente as funcionalidades")

if __name__ == "__main__":
    main()
