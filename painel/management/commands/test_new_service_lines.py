from django.core.management.base import BaseCommand
from painel.starlink_api import get_service_lines_with_location

class Command(BaseCommand):
    help = 'Testa a nova função com endpoint /service-lines'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Testando nova função get_service_lines_with_location...\n')
        
        result = get_service_lines_with_location()
        
        if result.get("error"):
            self.stdout.write(f'❌ Erro: {result["error"]}')
            return
        
        service_lines = result.get("service_lines", [])
        correlations_found = result.get("correlations_found", 0)
        
        self.stdout.write(f'✅ {len(service_lines)} Service Lines encontrados')
        self.stdout.write(f'🎯 {correlations_found} correlações de endereço encontradas')
        self.stdout.write(f'📊 Taxa de sucesso: {(correlations_found/len(service_lines)*100):.1f}%\n')
        
        # Mostrar alguns exemplos
        self.stdout.write('📋 Primeiros 5 Service Lines:')
        for i, sl in enumerate(service_lines[:5]):
            self.stdout.write(f'\n{i+1}. {sl["serviceLineNumber"]}')
            self.stdout.write(f'   📍 Localização: {sl["serviceLocation"]}')
            self.stdout.write(f'   🏷️  Nickname: {sl.get("nickname", "N/A")}')
            self.stdout.write(f'   📌 Address ID: {sl.get("addressReferenceId", "N/A")}')
            self.stdout.write(f'   🔄 Status: {sl.get("status", "N/A")}')
        
        # Estatísticas
        with_location = len([sl for sl in service_lines if sl["serviceLocation"] != "Localização não informada"])
        without_location = len(service_lines) - with_location
        
        self.stdout.write(f'\n📈 ESTATÍSTICAS FINAIS:')
        self.stdout.write(f'   ✅ Com localização: {with_location}')
        self.stdout.write(f'   ❌ Sem localização: {without_location}')
        self.stdout.write(f'   🎯 Taxa de sucesso: {(with_location/len(service_lines)*100):.1f}%')
        
        if with_location > 0:
            self.stdout.write(f'\n🎉 SUCESSO! Conseguimos correlacionar Service Lines com endereços!')
        else:
            self.stdout.write(f'\n❌ Ainda não conseguimos correlacionar os endereços...')
