"""
Script para criar tabela EldPortalSemVideo e adicionar coluna portal_sem_video_id
"""
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.db import connection

def create_portal_sem_video_table():
    """Criar tabela eld_portal_sem_video"""
    
    print("🚀 CRIANDO ESTRUTURA PARA PORTAL SEM VÍDEO")
    print("=" * 50)
    
    cursor = connection.cursor()
    
    try:
        # 1. Criar tabela eld_portal_sem_video
        print("📋 Criando tabela eld_portal_sem_video...")
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS eld_portal_sem_video (
            id BIGSERIAL PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            versao VARCHAR(50) NOT NULL,
            descricao TEXT,
            arquivo_zip VARCHAR(100) NOT NULL,
            ativo BOOLEAN DEFAULT FALSE,
            tamanho_mb DECIMAL(10,2),
            data_criacao TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            data_atualizacao TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        cursor.execute(create_table_sql)
        print("✅ Tabela eld_portal_sem_video criada com sucesso!")
        
        # 2. Verificar se coluna portal_sem_video_id já existe
        print("🔍 Verificando coluna portal_sem_video_id...")
        
        check_column_sql = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'eld_gerenciar_portal' 
        AND column_name = 'portal_sem_video_id';
        """
        
        cursor.execute(check_column_sql)
        column_exists = cursor.fetchone()
        
        if not column_exists:
            # 3. Adicionar coluna portal_sem_video_id
            print("📋 Adicionando coluna portal_sem_video_id...")
            
            add_column_sql = """
            ALTER TABLE eld_gerenciar_portal 
            ADD COLUMN portal_sem_video_id BIGINT;
            """
            
            cursor.execute(add_column_sql)
            
            # 4. Adicionar foreign key
            print("🔗 Criando foreign key...")
            
            add_fk_sql = """
            ALTER TABLE eld_gerenciar_portal 
            ADD CONSTRAINT fk_portal_sem_video 
            FOREIGN KEY (portal_sem_video_id) 
            REFERENCES eld_portal_sem_video(id) 
            ON DELETE SET NULL;
            """
            
            cursor.execute(add_fk_sql)
            print("✅ Coluna portal_sem_video_id adicionada com sucesso!")
        else:
            print("ℹ️  Coluna portal_sem_video_id já existe!")
        
        # 5. Verificar estruturas criadas
        print("\n📊 VERIFICANDO ESTRUTURAS CRIADAS:")
        
        # Verificar tabela eld_portal_sem_video
        cursor.execute("SELECT COUNT(*) FROM eld_portal_sem_video;")
        count = cursor.fetchone()[0]
        print(f"✅ Tabela eld_portal_sem_video: {count} registros")
        
        # Verificar coluna adicionada
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'eld_gerenciar_portal' 
            AND column_name = 'portal_sem_video_id';
        """)
        column_info = cursor.fetchone()
        if column_info:
            print(f"✅ Coluna portal_sem_video_id: {column_info[1]} ({column_info[2]})")
        
        print("\n🎉 ESTRUTURA CRIADA COM SUCESSO!")
        print("Agora você pode:")
        print("1. Acessar o admin: /admin/")
        print("2. Ir em Captive Portal > Portal sem Vídeo")
        print("3. Fazer upload de scripts_poppnet_sre.zip")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    finally:
        cursor.close()
    
    return True

if __name__ == "__main__":
    create_portal_sem_video_table()
