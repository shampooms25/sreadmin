#!/usr/bin/env python3
"""
Script para verificar o status do Git no servidor de produção
"""

import subprocess
import os

def run_command(cmd, cwd=None):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def main():
    project_path = "/var/www/sreadmin"
    
    print("🔍 VERIFICANDO STATUS DO GIT NO SERVIDOR")
    print("=" * 45)
    
    # 1. Verificar se é um repositório Git
    if not os.path.exists(f"{project_path}/.git"):
        print("❌ Não é um repositório Git!")
        return
    
    print(f"✅ Repositório Git encontrado em: {project_path}")
    
    # 2. Verificar branch atual
    code, stdout, stderr = run_command("git branch --show-current", cwd=project_path)
    if code == 0:
        current_branch = stdout.strip()
        print(f"📍 Branch atual: {current_branch}")
    
    # 3. Verificar status dos arquivos
    code, stdout, stderr = run_command("git status --porcelain", cwd=project_path)
    if code == 0:
        if stdout.strip():
            print("⚠️  ARQUIVOS MODIFICADOS DETECTADOS:")
            print(stdout)
        else:
            print("✅ Nenhuma modificação local detectada")
    
    # 4. Verificar arquivos específicos que podem ter sido alterados
    files_to_check = [
        "painel/models.py",
        "sreadmin/settings.py", 
        "sreadmin/wsgi.py"
    ]
    
    print("\n🔍 VERIFICANDO ARQUIVOS ESPECÍFICOS:")
    for file_path in files_to_check:
        full_path = f"{project_path}/{file_path}"
        if os.path.exists(full_path):
            # Verificar se o arquivo foi modificado
            code, stdout, stderr = run_command(f"git diff HEAD -- {file_path}", cwd=project_path)
            if code == 0 and stdout.strip():
                print(f"⚠️  {file_path} - MODIFICADO")
                print(f"   Primeiras linhas das modificações:")
                lines = stdout.split('\n')[:10]
                for line in lines:
                    if line.startswith(('+', '-')) and not line.startswith(('+++', '---')):
                        print(f"   {line}")
            else:
                print(f"✅ {file_path} - sem alterações")
        else:
            print(f"❌ {file_path} - não encontrado")
    
    # 5. Verificar commits pendentes
    code, stdout, stderr = run_command("git log --oneline -5", cwd=project_path)
    if code == 0:
        print(f"\n📜 ÚLTIMOS 5 COMMITS:")
        print(stdout)
    
    # 6. Verificar diferença com origin
    code, stdout, stderr = run_command("git fetch", cwd=project_path)
    code, stdout, stderr = run_command("git log HEAD..origin/main --oneline", cwd=project_path)
    if code == 0:
        if stdout.strip():
            print(f"\n🔄 COMMITS DISPONÍVEIS NO REMOTO:")
            print(stdout)
        else:
            print(f"\n✅ Local está sincronizado com o remoto")
    
    print(f"\n📋 PRÓXIMOS PASSOS SUGERIDOS:")
    print(f"   1. Se há modificações locais → Criar commit ou stash")
    print(f"   2. Se há commits remotos → Fazer pull com merge/rebase") 
    print(f"   3. Aplicar correção segura sem conflitos Git")

if __name__ == "__main__":
    main()
