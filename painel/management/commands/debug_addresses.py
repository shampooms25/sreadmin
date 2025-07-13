from django.core.management.base import BaseCommand
from painel.starlink_api import (
    debug_addresses_endpoint, 
    debug_multiple_endpoints
)

class Command(BaseCommand):
    help = 'Debug do endpoint de endereços da API Starlink'

    def add_arguments(self, parser):
        parser.add_argument(
            '--multiple',
            action='store_true',
            help='Testa múltiplos endpoints',
        )

    def handle(self, *args, **options):
        if options['multiple']:
            self.stdout.write(self.style.SUCCESS('🚀 Iniciando debug de múltiplos endpoints...'))
            
            try:
                results = debug_multiple_endpoints()
                
                self.stdout.write('\n📊 RESUMO DOS RESULTADOS:')
                for endpoint, result in results.items():
                    if result['success']:
                        self.stdout.write(self.style.SUCCESS(f'✅ {endpoint}: SUCESSO'))
                    else:
                        self.stdout.write(self.style.ERROR(f'❌ {endpoint}: ERRO'))
                        
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Erro inesperado: {e}'))
        else:
            self.stdout.write(self.style.SUCCESS('🚀 Iniciando debug do endpoint de endereços...'))
            
            try:
                result = debug_addresses_endpoint()
                
                if result.get('success'):
                    self.stdout.write(self.style.SUCCESS('✅ Endpoint de addresses funcionou!'))
                    self.stdout.write('📊 Dados de addresses encontrados.')
                else:
                    self.stdout.write(self.style.ERROR(f'❌ Erro: {result.get("error", "Erro desconhecido")}'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Erro inesperado: {e}'))
