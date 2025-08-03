"""
Script para adicionar logs detalhados ao processo de upload
e identificar exatamente onde ocorre o erro /videos
"""

import os
import sys

def main():
    print("🕵️  ADICIONANDO LOGS DETALHADOS PARA DIAGNÓSTICO")
    print("=" * 50)
    
    # Caminho para o arquivo models.py
    models_path = "/var/www/sreadmin/painel/models.py"
    
    if not os.path.exists(models_path):
        print(f"❌ Arquivo não encontrado: {models_path}")
        return
    
    # Ler o arquivo
    with open(models_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fazer backup
    backup_path = f"{models_path}.debug_backup"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup criado: {backup_path}")
    
    # Código de logging para adicionar
    logging_code = '''
                # LOGS DE DEBUG - INÍCIO
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"DEBUG: Iniciando save() - is_new: {is_new}")
                if self.video:
                    logger.error(f"DEBUG: Video file: {self.video}")
                    logger.error(f"DEBUG: Video name: {self.video.name}")
                    try:
                        logger.error(f"DEBUG: Video path: {self.video.path}")
                    except Exception as e:
                        logger.error(f"DEBUG: Erro ao acessar video.path: {e}")
                # LOGS DE DEBUG - FIM'''
    
    # Encontrar onde inserir o logging
    lines = content.split('\n')
    modified = False
    
    for i, line in enumerate(lines):
        # Procurar pela linha "super().save(*args, **kwargs)"
        if 'super().save(*args, **kwargs)' in line:
            # Inserir logging antes do super().save()
            indent = len(line) - len(line.lstrip())
            logging_lines = logging_code.strip().split('\n')
            for j, log_line in enumerate(logging_lines):
                lines.insert(i + j, ' ' * indent + log_line)
            modified = True
            print(f"✅ Logs adicionados antes da linha {i+1}")
            break
    
    if modified:
        # Salvar arquivo modificado
        new_content = '\n'.join(lines)
        with open(models_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Arquivo com logs salvo")
        
        print(f"\n🧪 PRÓXIMOS PASSOS:")
        print(f"   1. Reiniciar Apache: sudo systemctl restart apache2")
        print(f"   2. Tentar upload de vídeo")
        print(f"   3. Verificar logs: sudo tail -f /var/log/apache2/error.log")
        print(f"   4. Procurar por linhas 'DEBUG:' nos logs")
        
        print(f"\n🔄 PARA REVERTER:")
        print(f"   cp {backup_path} {models_path}")
        print(f"   sudo systemctl restart apache2")
        
    else:
        print("❌ Linha super().save() não encontrada")

if __name__ == "__main__":
    main()
