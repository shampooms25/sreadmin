from django.core.management.base import BaseCommand
from painel.starlink_api import debug_api_response

class Command(BaseCommand):
    help = 'Debug completo da API Starlink - mostra todos os campos disponíveis'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando debug da API Starlink...')
        )
        
        try:
            debug_api_response()
            self.stdout.write(
                self.style.SUCCESS('✅ Debug concluído com sucesso!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro no debug: {e}')
            )
