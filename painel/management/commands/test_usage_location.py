from django.core.management.base import BaseCommand
from painel.starlink_api import get_billing_usage_data

class Command(BaseCommand):
    help = 'Testa a função de consumo de franquia com localização'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📍 Testando função de consumo com localização...'))
        
        try:
            # Testar a função
            result = get_billing_usage_data()
            
            if result["success"]:
                self.stdout.write(self.style.SUCCESS('✅ Função executada com sucesso!'))
                self.stdout.write(f'📊 Total de Service Lines: {result["total_lines"]}')
                self.stdout.write(f'📅 Período: {result["cycle_start"]} - {result["cycle_end"]}')
                
                # Mostrar os 5 maiores consumidores com localização
                self.stdout.write('\n🏆 Top 5 maiores consumidores com localização:')
                for i, line in enumerate(result["usage_data"][:5], 1):
                    location = line.get("location", "N/A")
                    nickname = line.get("nickname", "N/A")
                    self.stdout.write(f'   {i}. {line["serviceLineNumber"]}')
                    self.stdout.write(f'      📍 Local: {location}')
                    self.stdout.write(f'      🏷️  Nickname: {nickname}')
                    self.stdout.write(f'      📊 Consumo: {line["totalGB"]:.2f} GB ({line["usagePercentage"]:.1f}%)')
                    self.stdout.write('')
                
                # Verificar quantos têm localização
                with_location = len([x for x in result["usage_data"] if x.get("location", "Localização não informada") != "Localização não informada"])
                self.stdout.write(f'📍 Service Lines com localização: {with_location}/{result["total_lines"]}')
                
            else:
                self.stdout.write(self.style.ERROR(f'❌ Erro: {result["error"]}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro na execução: {str(e)}'))
            
        self.stdout.write(self.style.SUCCESS('\n✅ Teste concluído!'))
