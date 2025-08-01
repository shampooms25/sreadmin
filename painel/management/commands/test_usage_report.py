from django.core.management.base import BaseCommand
from painel.starlink_api import get_billing_usage_data

class Command(BaseCommand):
    help = 'Testa a função de consumo de franquia'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Testando função de consumo de franquia...'))
        
        try:
            # Testar a função
            result = get_billing_usage_data()
            
            if result["success"]:
                self.stdout.write(self.style.SUCCESS('✅ Função executada com sucesso!'))
                self.stdout.write(f'📊 Total de Service Lines: {result["total_lines"]}')
                self.stdout.write(f'📅 Período: {result["cycle_start"]} - {result["cycle_end"]}')
                
                # Mostrar estatísticas
                stats = result["statistics"]
                self.stdout.write('\n📈 Estatísticas de threshold:')
                self.stdout.write(f'   🟢 Abaixo de 70%: {stats["lines_under_70"]}')
                self.stdout.write(f'   🟡 70% ou mais: {stats["lines_70_plus"]}')
                self.stdout.write(f'   🟠 80% ou mais: {stats["lines_80_plus"]}')
                self.stdout.write(f'   🔴 90% ou mais: {stats["lines_90_plus"]}')
                self.stdout.write(f'   🟣 100% ou mais: {stats["lines_100_plus"]}')
                
                # Mostrar os 5 maiores consumidores
                self.stdout.write('\n🏆 Top 5 maiores consumidores:')
                for i, line in enumerate(result["usage_data"][:5], 1):
                    self.stdout.write(f'   {i}. {line["serviceLineNumber"]} - {line["totalGB"]:.2f} GB ({line["usagePercentage"]:.1f}%)')
                
            else:
                self.stdout.write(self.style.ERROR(f'❌ Erro: {result["error"]}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro na execução: {str(e)}'))
            
        self.stdout.write(self.style.SUCCESS('\n✅ Teste concluído!'))
