#!/usr/bin/env python
"""
Script simples para verificar e executar migrações
"""

import subprocess
import sys
import os

def run_command(command, description):
    """
    Executa um comando e retorna o resultado
    """
    print(f"🔄 {description}...")
    print(f"💻 Executando: {command}")
    
    try:
        # Executar comando
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=r"c:\Projetos\Poppnet\sreadmin"
        )
        
        print(f"Return code: {result.returncode}")
        
        if result.stdout:
            print("📄 STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️ STDERR:")
            print(result.stderr)
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except Exception as e:
        print(f"❌ Erro ao executar comando: {e}")
        return False, "", str(e)

def main():
    """
    Função principal
    """
    print("🚀 VERIFICAÇÃO E EXECUÇÃO DE MIGRAÇÕES")
    print("=" * 55)
    
    # Comando Python com caminho completo
    python_cmd = r"C:\Projetos\Poppnet\sreadmin\venv\Scripts\python.exe"
    
    # 1. Verificar migrações pendentes
    print("\n1️⃣ Verificando migrações pendentes...")
    success, stdout, stderr = run_command(
        f'"{python_cmd}" manage.py showmigrations captive_portal',
        "Verificando status das migrações"
    )
    
    # 2. Executar migrações
    print("\n2️⃣ Executando migrações...")
    success, stdout, stderr = run_command(
        f'"{python_cmd}" manage.py migrate',
        "Executando todas as migrações"
    )
    
    # 3. Verificar se a tabela foi criada
    print("\n3️⃣ Testando acesso à tabela...")
    test_script = '''
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sreadmin.settings")
django.setup()
from captive_portal.models import ApplianceToken
print(f"Tabela existe! Total de registros: {ApplianceToken.objects.count()}")
'''
    
    success, stdout, stderr = run_command(
        f'"{python_cmd}" -c "{test_script}"',
        "Testando acesso à tabela ApplianceToken"
    )
    
    print("\n🎯 RESUMO:")
    if "Tabela existe!" in stdout:
        print("✅ Migração bem-sucedida! A tabela ApplianceToken foi criada.")
        print("✅ Você pode acessar /admin/captive_portal/appliancetoken/")
    else:
        print("❌ Problema na migração. Verifique os logs acima.")

if __name__ == "__main__":
    main()
