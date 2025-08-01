from django.core.management.base import BaseCommand
from painel.starlink_api import get_service_lines_with_location

class Command(BaseCommand):
    help = 'Testa o template com dados simulados de status'

    def handle(self, *args, **options):
        self.stdout.write('🎨 Testando template com status diferentes...\n')
        
        result = get_service_lines_with_location()
        
        if result.get("error"):
            self.stdout.write(f'❌ Erro: {result["error"]}')
            return
        
        service_lines = result.get("service_lines", [])
        stats = result.get("statistics", {})
        
        # Simular alguns status diferentes para teste visual
        if len(service_lines) >= 3:
            # Forçar alguns status para teste
            service_lines[0]["status"] = "Offline"
            service_lines[0]["statusClass"] = "offline"
            
            service_lines[1]["status"] = "Sem Dados"
            service_lines[1]["statusClass"] = "no_data"
            
            service_lines[2]["status"] = "Ativo"
            service_lines[2]["statusClass"] = "active"
        
        self.stdout.write(f'✅ Template pode ser testado com:')
        self.stdout.write(f'   🔴 1 Offline: {service_lines[0]["serviceLineNumber"]}')
        self.stdout.write(f'   🟡 1 Sem Dados: {service_lines[1]["serviceLineNumber"]}')
        self.stdout.write(f'   🟢 1 Ativo: {service_lines[2]["serviceLineNumber"]}')
        self.stdout.write('')
        self.stdout.write(f'📊 Estatísticas atuais:')
        self.stdout.write(f'   🟢 Ativos: {stats.get("active_lines", 0)}')
        self.stdout.write(f'   🔴 Offline: {stats.get("offline_lines", 0)}')
        self.stdout.write(f'   🟡 Sem Dados: {stats.get("no_data_lines", 0)}')
        self.stdout.write('')
        self.stdout.write(f'🌐 Acesse o dashboard em: http://localhost:8000/admin/painel/starlink/service-lines/')
        self.stdout.write(f'   Para ver os cards coloridos e as linhas da tabela com background colorido!')
        
        # Mostrar preview do HTML que será gerado
        self.stdout.write(f'\n🎨 PREVIEW DOS CARDS:')
        self.stdout.write(f'   Card Verde (Ativos): {stats.get("active_lines", 0)}')
        self.stdout.write(f'   Card Vermelho (Offline): {stats.get("offline_lines", 0)}')
        self.stdout.write(f'   Card Amarelo (Sem Dados): {stats.get("no_data_lines", 0)}')
        
        self.stdout.write(f'\n🎨 PREVIEW DAS LINHAS DA TABELA:')
        for i, sl in enumerate(service_lines[:3]):
            color_emoji = "🟢" if sl.get("statusClass") == "active" else ("🔴" if sl.get("statusClass") == "offline" else "🟡")
            self.stdout.write(f'   {color_emoji} {sl["serviceLineNumber"]} - {sl["status"]} - Background: {sl.get("statusClass", "active")}')
        
        self.stdout.write(f'\n💡 As cores no navegador serão:')
        self.stdout.write(f'   🟢 Verde claro para Ativos')
        self.stdout.write(f'   🔴 Vermelho claro para Offline')
        self.stdout.write(f'   🟡 Amarelo claro para Sem Dados')
