import subprocess
import sys
import os

def execute_migration():
    """
    Executa a migração usando subprocess e mostra o output
    """
    print("🔄 Executando migração do Django...")
    
    # Caminho para o Python do ambiente virtual
    python_path = r"C:\Projetos\Poppnet\sreadmin\venv\Scripts\python.exe"
    
    # Diretório do projeto
    project_dir = r"C:\Projetos\Poppnet\sreadmin"
    
    # Comando para executar
    cmd = [python_path, "manage.py", "migrate"]
    
    try:
        # Executar o comando
        result = subprocess.run(
            cmd,
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=False  # Não lançar exceção em caso de erro
        )
        
        print(f"Return code: {result.returncode}")
        
        if result.stdout:
            print("📄 OUTPUT:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️ ERRORS:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Migração executada com sucesso!")
            return True
        else:
            print("❌ Erro na migração!")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao executar comando: {e}")
        return False

def test_table():
    """
    Testa se a tabela foi criada
    """
    print("\n🔍 Testando se a tabela foi criada...")
    
    test_code = '''
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sreadmin.settings")
django.setup()

try:
    from captive_portal.models import ApplianceToken
    count = ApplianceToken.objects.count()
    print(f"SUCCESS: Tabela existe! Registros: {count}")
except Exception as e:
    print(f"ERROR: {e}")
'''
    
    # Salvar código em arquivo temporário
    with open("temp_test.py", "w") as f:
        f.write(test_code)
    
    # Executar teste
    python_path = r"C:\Projetos\Poppnet\sreadmin\venv\Scripts\python.exe"
    project_dir = r"C:\Projetos\Poppnet\sreadmin"
    
    try:
        result = subprocess.run(
            [python_path, "temp_test.py"],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        
        print("📄 RESULTADO DO TESTE:")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        # Limpar arquivo temporário
        os.remove("temp_test.py")
        
        return "SUCCESS" in result.stdout
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    print("🚀 EXECUÇÃO FORÇADA DE MIGRAÇÃO")
    print("=" * 40)
    
    # Executar migração
    migration_success = execute_migration()
    
    if migration_success:
        # Testar tabela
        table_success = test_table()
        
        if table_success:
            print("\n🎉 SUCESSO TOTAL!")
            print("✅ Migração executada")
            print("✅ Tabela ApplianceToken criada")
            print("✅ Você pode acessar /admin/captive_portal/appliancetoken/")
        else:
            print("\n⚠️ Migração executada mas tabela não acessível")
    else:
        print("\n❌ Falha na migração")
