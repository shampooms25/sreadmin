#!/usr/bin/env python3
"""
Script para criar novo modelo para gerenciar Portal sem Vídeo
Adiciona funcionalidade para dois tipos de ZIP: com e sem vídeo
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, '/var/www/sreadmin')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

def create_migration():
    """Criar nova migração para o modelo PortalSemVideo"""
    
    migration_content = '''# Generated migration for Portal sem Video
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('painel', '0006_elduploadvideo'),  # Ajustar conforme última migração
    ]

    operations = [
        migrations.CreateModel(
            name='EldPortalSemVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(help_text='Nome descritivo para este portal', max_length=255, verbose_name='Nome do Portal')),
                ('arquivo_zip', models.FileField(help_text='Arquivo ZIP do portal sem vídeo (scripts_poppnet_sre.zip)', upload_to='portal_sem_video/', verbose_name='Arquivo ZIP')),
                ('descricao', models.TextField(blank=True, help_text='Descrição do portal e suas características', verbose_name='Descrição')),
                ('versao', models.CharField(help_text='Versão do portal (ex: 1.0, 2.1)', max_length=50, verbose_name='Versão')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Última Atualização')),
                ('ativo', models.BooleanField(default=False, help_text='Marcar como portal padrão para uso sem vídeo', verbose_name='Portal Ativo')),
                ('tamanho_mb', models.DecimalField(decimal_places=2, help_text='Tamanho do arquivo ZIP em MB', max_digits=10, verbose_name='Tamanho (MB)')),
            ],
            options={
                'verbose_name': 'Portal sem Vídeo',
                'verbose_name_plural': 'Portais sem Vídeo',
                'db_table': 'eld_portal_sem_video',
                'ordering': ['-data_atualizacao'],
            },
        ),
        
        # Adicionar campo para link ao portal sem vídeo no modelo existente
        migrations.AddField(
            model_name='eldgerenciarportal',
            name='portal_sem_video',
            field=models.ForeignKey(blank=True, help_text='Portal usado quando vídeo estiver desativado', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='configuracoes_portal', to='painel.eldportalsemvideo', verbose_name='Portal sem Vídeo'),
        ),
    ]
'''
    
    # Criar arquivo de migração
    migration_dir = '/var/www/sreadmin/painel/migrations'
    migration_file = f'{migration_dir}/0007_eldportalsemvideo.py'
    
    with open(migration_file, 'w', encoding='utf-8') as f:
        f.write(migration_content)
    
    print(f"✅ Migração criada: {migration_file}")
    return migration_file

def main():
    print("🚀 CRIANDO ESTRUTURA PARA PORTAL SEM VÍDEO")
    print("=" * 50)
    
    try:
        # 1. Criar migração
        migration_file = create_migration()
        
        # 2. Executar migração
        print("\n📦 Executando migração...")
        os.system("cd /var/www/sreadmin && python manage.py migrate")
        
        # 3. Criar diretório para uploads
        upload_dir = '/var/www/sreadmin/media/portal_sem_video'
        os.makedirs(upload_dir, exist_ok=True)
        print(f"✅ Diretório criado: {upload_dir}")
        
        # 4. Configurar permissões
        os.system(f"sudo chown -R www-data:www-data {upload_dir}")
        os.system(f"sudo chmod -R 775 {upload_dir}")
        print(f"✅ Permissões configuradas")
        
        print(f"\n✅ ESTRUTURA CRIADA COM SUCESSO!")
        print(f"\n📋 PRÓXIMOS PASSOS:")
        print(f"   1. Adicionar modelo ao models.py")
        print(f"   2. Adicionar admin ao admin.py")  
        print(f"   3. Criar views e templates")
        print(f"   4. Adicionar validação de preview de vídeo")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
