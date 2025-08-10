"""
Comando personalizado para configurar tokens do Appliance POPPFIRE
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import json
import os


class Command(BaseCommand):
    help = 'Configura o sistema de tokens do Appliance POPPFIRE'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a recriação da tabela se ela já existir',
        )

    def handle(self, *args, **options):
        self.stdout.write("🚀 CONFIGURAÇÃO DO SISTEMA DE TOKENS APPLIANCE POPPFIRE")
        self.stdout.write("=" * 60)

        # 1. Verificar se a tabela já existe
        if self.check_table_exists() and not options['force']:
            self.stdout.write(
                self.style.WARNING("⚠️ Tabela ApplianceToken já existe!")
            )
            self.stdout.write("Use --force para recriar a tabela.")
            return

        # 2. Executar migrações
        try:
            self.stdout.write("🔄 Executando migrações...")
            call_command('migrate', verbosity=0)
            self.stdout.write(
                self.style.SUCCESS("✅ Migrações executadas com sucesso!")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erro nas migrações: {e}")
            )
            return

        # 3. Verificar se a tabela foi criada
        if self.check_table_exists():
            self.stdout.write(
                self.style.SUCCESS("✅ Tabela ApplianceToken criada com sucesso!")
            )
        else:
            self.stdout.write(
                self.style.ERROR("❌ Tabela ApplianceToken não foi criada!")
            )
            return

        # 4. Sincronizar tokens do JSON
        self.sync_tokens_from_json()

        # 5. Exibir instruções finais
        self.stdout.write("\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
        self.stdout.write("=" * 60)
        self.stdout.write("✅ Sistema de tokens configurado com sucesso!")
        self.stdout.write("✅ Acesse /admin/captive_portal/appliancetoken/ para gerenciar")
        self.stdout.write("✅ Use a API em /api/appliances/ para testar")

    def check_table_exists(self):
        """
        Verifica se a tabela ApplianceToken existe
        """
        try:
            from captive_portal.models import ApplianceToken
            ApplianceToken.objects.count()
            return True
        except Exception:
            return False

    def sync_tokens_from_json(self):
        """
        Sincroniza tokens do arquivo JSON para o banco de dados
        """
        self.stdout.write("🔄 Sincronizando tokens do JSON...")

        json_file = 'appliance_tokens.json'
        if not os.path.exists(json_file):
            self.stdout.write(
                self.style.WARNING(f"⚠️ Arquivo {json_file} não encontrado.")
            )
            return

        try:
            from captive_portal.models import ApplianceToken

            with open(json_file, 'r', encoding='utf-8') as f:
                tokens_data = json.load(f)

            tokens = tokens_data.get('tokens', {})
            synced = 0

            for token, info in tokens.items():
                # Verificar se já existe
                if not ApplianceToken.objects.filter(token=token).exists():
                    ApplianceToken.objects.create(
                        token=token,
                        appliance_id=info['appliance_id'],
                        appliance_name=info['appliance_name'],
                        description=info.get('description', ''),
                        is_active=True
                    )
                    synced += 1
                    self.stdout.write(f"  ✅ {info['appliance_name']}")

            self.stdout.write(
                self.style.SUCCESS(f"✅ {synced} tokens sincronizados!")
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erro ao sincronizar tokens: {e}")
            )

    def get_table_info(self):
        """
        Obtém informações sobre as tabelas existentes
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%appliance%'
            """)
            return cursor.fetchall()
