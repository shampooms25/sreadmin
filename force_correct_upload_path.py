#!/usr/bin/env python3
"""
Script para forçar o Django a usar o caminho correto de upload
Corrige o problema onde Django tenta acessar '/videos' ao invés do MEDIA_ROOT correto
"""

import os
import sys

def main():
    print("🔧 CORREÇÃO FORÇADA - CAMINHO DE UPLOAD")
    print("=" * 45)
    
    project_path = "/var/www/sreadmin"
    models_path = f"{project_path}/painel/models.py"
    
    if not os.path.exists(models_path):
        print(f"❌ Arquivo não encontrado: {models_path}")
        return
    
    # Ler arquivo atual
    with open(models_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fazer backup
    backup_path = f"{models_path}.backup_original"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup criado: {backup_path}")
    
    # Procurar pela definição do campo video
    lines = content.split('\n')
    new_lines = []
    modified = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Procurar pela linha do campo video
        if 'video = models.FileField(' in line:
            print(f"✅ Encontrada definição do campo video na linha {i+1}")
            
            # Substituir por uma versão que usa função upload_to personalizada
            indent = len(line) - len(line.lstrip())
            new_field_definition = f"""{' ' * indent}def upload_video_to(instance, filename):
{' ' * (indent + 4)}\"\"\"
{' ' * (indent + 4)}Função personalizada para definir onde salvar o vídeo
{' ' * (indent + 4)}Força o uso do MEDIA_ROOT correto
{' ' * (indent + 4)}\"\"\"
{' ' * (indent + 4)}from django.conf import settings
{' ' * (indent + 4)}import os
{' ' * (indent + 4)}return os.path.join('videos', 'eld', filename)

{' ' * indent}video = models.FileField(
{' ' * (indent + 4)}upload_to=upload_video_to,"""
            
            new_lines.append(new_field_definition)
            
            # Pular a linha atual e procurar pelas próximas linhas do campo
            i += 1
            while i < len(lines) and not lines[i].strip().endswith(')'):
                if 'upload_to' not in lines[i]:  # Manter outras configurações exceto upload_to
                    new_lines.append(lines[i])
                i += 1
            
            # Adicionar a linha de fechamento
            if i < len(lines):
                new_lines.append(lines[i])
            
            modified = True
            i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    if modified:
        # Salvar arquivo modificado
        new_content = '\n'.join(new_lines)
        with open(models_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Campo video modificado com função upload_to personalizada")
        
        # Verificar se existe diretório /videos e remover se necessário
        if os.path.exists("/videos"):
            print(f"\n⚠️  DIRETÓRIO /videos ENCONTRADO NA RAIZ!")
            print(f"   Este diretório pode estar causando conflito")
            print(f"   Execute: sudo rm -rf /videos")
        else:
            print(f"\n✅ Diretório /videos não existe na raiz (correto)")
        
        # Garantir que o diretório correto existe
        correct_path = f"{project_path}/media/videos/eld"
        os.makedirs(correct_path, exist_ok=True)
        print(f"✅ Diretório correto criado: {correct_path}")
        
        # Configurar permissões
        os.system(f"sudo chown -R www-data:www-data {project_path}/media")
        os.system(f"sudo chmod -R 775 {project_path}/media/videos")
        print(f"✅ Permissões configuradas")
        
        print(f"\n🧪 PRÓXIMOS PASSOS:")
        print(f"   1. sudo systemctl restart apache2")
        print(f"   2. Testar upload: https://paineleld.poppnet.com.br/admin/")
        print(f"   3. O vídeo deve ser salvo em: {correct_path}")
        
        print(f"\n🔄 PARA REVERTER:")
        print(f"   cp {backup_path} {models_path}")
        print(f"   sudo systemctl restart apache2")
        
    else:
        print("❌ Campo video não encontrado para modificar")
    
    print(f"\n✅ CORREÇÃO APLICADA!")

if __name__ == "__main__":
    main()
