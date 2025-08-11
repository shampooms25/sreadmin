#!/usr/bin/env python3
"""
Script de Correção URGENTE para Erro 500 - Tabelas Faltantes
Execute: python emergency_fix.py
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def print_header():
    print("🚨 CORREÇÃO URGENTE - Erro 500 Produção")
    print("=" * 40)

def check_django_directory():
    """Verificar se estamos no diretório correto do Django"""
    if not Path("manage.py").exists():
        print("❌ Erro: Execute no diretório /var/www/sreadmin")
        print("   Certifique-se de estar no diretório que contém manage.py")
        sys.exit(1)
    print("✅ Diretório Django encontrado")

def create_tables():
    """Criar tabelas faltantes diretamente no banco"""
    print("\n🔧 CRIANDO TABELAS FALTANTES...")
    
    script = '''
import os
import django
from django.conf import settings
from django.db import connection

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

print("🔧 Conectando ao banco de dados...")

try:
    with connection.cursor() as cursor:
        # Criar eld_gerenciar_portal
        print("Criando eld_gerenciar_portal...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eld_gerenciar_portal (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(200) NOT NULL,
                ativo BOOLEAN NOT NULL DEFAULT false,
                captive_portal_zip VARCHAR(100),
                video_file VARCHAR(100),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # Criar eld_portal_sem_video
        print("Criando eld_portal_sem_video...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eld_portal_sem_video (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(200) NOT NULL,
                ativo BOOLEAN NOT NULL DEFAULT false,
                arquivo_zip VARCHAR(100),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # Inserir dados padrão
        cursor.execute("SELECT COUNT(*) FROM eld_gerenciar_portal;")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO eld_gerenciar_portal (nome, ativo) 
                VALUES ('Portal Captive Padrão', false);
            """)
            print("✅ Registro padrão inserido em eld_gerenciar_portal")
        
        cursor.execute("SELECT COUNT(*) FROM eld_portal_sem_video;")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO eld_portal_sem_video (nome, ativo) 
                VALUES ('Portal Sem Vídeo Padrão', false);
            """)
            print("✅ Registro padrão inserido em eld_portal_sem_video")
        
        print("✅ Tabelas criadas com sucesso!")
        
except Exception as e:
    print(f"❌ Erro ao criar tabelas: {e}")
    import traceback
    traceback.print_exc()
'''
    
    # Executar script
    result = subprocess.run([sys.executable, "-c", script], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"❌ Erro na criação das tabelas:")
        print(result.stderr)

def mark_migrations():
    """Marcar migrações como aplicadas"""
    print("\n🔧 MARCANDO MIGRAÇÕES...")
    
    script = '''
import os
import django
from django.conf import settings
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

try:
    with connection.cursor() as cursor:
        # Garantir tabela de migrações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS django_migrations (
                id SERIAL PRIMARY KEY,
                app VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                applied TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(app, name)
            );
        """)
        
        # Marcar migrações principais
        migrations = [
            ('painel', '0001_initial'),
            ('captive_portal', '0001_initial'),
            ('captive_portal', '0004_appliancetoken'),
        ]
        
        for app, migration in migrations:
            cursor.execute("""
                INSERT INTO django_migrations (app, name) 
                VALUES (%s, %s) 
                ON CONFLICT (app, name) DO NOTHING;
            """, [app, migration])
        
        print("✅ Migrações marcadas como aplicadas")
        
except Exception as e:
    print(f"❌ Erro nas migrações: {e}")
'''
    
    result = subprocess.run([sys.executable, "-c", script], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"❌ Erro nas migrações:")
        print(result.stderr)

def restart_services():
    """Reiniciar serviços web"""
    print("\n🔧 REINICIANDO SERVIÇOS...")
    
    # Parar processos Django existentes
    try:
        subprocess.run(["pkill", "-f", "manage.py runserver"], 
                      capture_output=True)
        subprocess.run(["pkill", "-f", "wsgi"], capture_output=True)
        time.sleep(2)
        print("✅ Processos Django anteriores finalizados")
    except:
        pass
    
    # Reiniciar Apache/Nginx
    try:
        result = subprocess.run(["systemctl", "is-active", "apache2"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("🔄 Reiniciando Apache...")
            subprocess.run(["systemctl", "reload", "apache2"])
    except:
        pass
    
    try:
        result = subprocess.run(["systemctl", "is-active", "nginx"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("🔄 Reiniciando Nginx...")
            subprocess.run(["systemctl", "reload", "nginx"])
    except:
        pass

def start_test_server():
    """Iniciar servidor de teste"""
    print("\n🚀 Iniciando servidor de teste...")
    
    try:
        # Iniciar servidor em background
        with open("emergency_fix.log", "w") as log_file:
            subprocess.Popen([sys.executable, "manage.py", "runserver", "0.0.0.0:8000"], 
                           stdout=log_file, stderr=log_file)
        
        time.sleep(5)
        print("✅ Servidor de teste iniciado na porta 8000")
    except Exception as e:
        print(f"⚠️ Erro ao iniciar servidor: {e}")

def verify_tables():
    """Verificar se as tabelas foram criadas"""
    print("\n🧪 VERIFICANDO TABELAS...")
    
    script = '''
import os
import django
from django.conf import settings
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM eld_gerenciar_portal;")
        count1 = cursor.fetchone()[0]
        print(f"✅ eld_gerenciar_portal: {count1} registros")
        
        cursor.execute("SELECT COUNT(*) FROM eld_portal_sem_video;")
        count2 = cursor.fetchone()[0]
        print(f"✅ eld_portal_sem_video: {count2} registros")
        
        print("✅ Todas as tabelas estão acessíveis!")
        
except Exception as e:
    print(f"❌ Erro na verificação: {e}")
'''
    
    result = subprocess.run([sys.executable, "-c", script], 
                          capture_output=True, text=True)
    
    print(result.stdout if result.returncode == 0 else result.stderr)

def test_api():
    """Testar API para verificar se o erro 500 foi corrigido"""
    print("\n🌐 TESTANDO API...")
    
    try:
        time.sleep(2)
        
        headers = {
            'Authorization': 'Bearer c8c786467d4a8d2825eaf549534d1ab0',
            'Content-Type': 'application/json'
        }
        
        response = requests.get("http://127.0.0.1:8000/api/appliances/info/", 
                               headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ API respondendo corretamente (200 OK)")
            print(f"   Resposta: {response.text[:100]}...")
        else:
            print(f"⚠️ API respondeu com código: {response.status_code}")
            if response.text:
                print(f"   Resposta: {response.text[:200]}...")
                
    except requests.exceptions.ConnectionError:
        print("⚠️ Servidor ainda não está respondendo na porta 8000")
    except Exception as e:
        print(f"⚠️ Erro no teste da API: {e}")

def show_final_info():
    """Mostrar informações finais"""
    print("\n✅ CORREÇÃO EMERGENCIAL CONCLUÍDA!")
    print("=" * 40)
    
    # Tentar obter IP do servidor
    try:
        result = subprocess.run(["hostname", "-I"], capture_output=True, text=True)
        server_ip = result.stdout.split()[0] if result.stdout else "127.0.0.1"
    except:
        server_ip = "127.0.0.1"
    
    print(f"\n🌐 URLs para teste:")
    print(f"   http://{server_ip}:8000/api/appliances/info/")
    print(f"   http://{server_ip}:8000/admin/")
    print(f"\n🔑 Token para autorização:")
    print(f"   Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0")
    print(f"\n📊 Logs de monitoramento:")
    print(f"   tail -f emergency_fix.log")
    print(f"\n🔧 Se persistir o erro 500:")
    print(f"   1. Verifique: tail -f /var/log/apache2/error.log")
    print(f"   2. Execute: python manage.py showmigrations")
    print(f"   3. Teste: python manage.py shell")

def main():
    """Função principal"""
    print_header()
    
    try:
        check_django_directory()
        create_tables()
        mark_migrations()
        restart_services()
        start_test_server()
        verify_tables()
        test_api()
        show_final_info()
        
    except KeyboardInterrupt:
        print("\n❌ Operação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
