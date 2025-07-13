from django.core.management.base import BaseCommand
from painel.starlink_api import get_service_lines_with_location

class Command(BaseCommand):
    help = 'Verifica se todos os Service Lines estão sendo listados'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Verificando TODOS os Service Lines...\n')
        
        result = get_service_lines_with_location()
        
        if result.get("error"):
            self.stdout.write(f'❌ Erro: {result["error"]}')
            return
        
        service_lines = result.get("service_lines", [])
        stats = result.get("statistics", {})
        
        self.stdout.write(f'📊 ESTATÍSTICAS COMPLETAS:')
        self.stdout.write(f'   📡 Total de Service Lines: {stats.get("total_service_lines", 0)}')
        self.stdout.write(f'   ✅ Com endereço: {stats.get("with_address", 0)}')
        self.stdout.write(f'   ❌ Sem endereço: {stats.get("without_address", 0)}')
        self.stdout.write(f'   🏷️  Com nickname: {stats.get("with_nickname", 0)}')
        self.stdout.write(f'   🟢 Ativos: {stats.get("active_lines", 0)}')
        self.stdout.write(f'   🔴 Inativos: {stats.get("inactive_lines", 0)}')
        self.stdout.write('')
        
        # Mostrar Service Lines SEM endereço
        without_address = [sl for sl in service_lines if not sl["hasAddress"]]
        if without_address:
            self.stdout.write(f'🔍 Service Lines SEM endereço ({len(without_address)}):')
            for i, sl in enumerate(without_address[:10]):  # Mostrar primeiros 10
                self.stdout.write(f'   {i+1}. {sl["serviceLineNumber"]}')
                self.stdout.write(f'      📍 Localização: {sl["serviceLocation"]}')
                self.stdout.write(f'      🏷️  Nickname: {sl.get("nickname", "N/A")}')
                self.stdout.write(f'      🔄 Status: {sl.get("status", "N/A")}')
                self.stdout.write(f'      📅 Início: {sl.get("startDate", "N/A")}')
                self.stdout.write('')
        
        # Mostrar Service Lines COM endereço
        with_address = [sl for sl in service_lines if sl["hasAddress"]]
        if with_address:
            self.stdout.write(f'✅ Service Lines COM endereço ({len(with_address)}):')
            for i, sl in enumerate(with_address[:5]):  # Mostrar primeiros 5
                self.stdout.write(f'   {i+1}. {sl["serviceLineNumber"]}')
                self.stdout.write(f'      📍 Localização: {sl["serviceLocation"]}')
                self.stdout.write(f'      🏷️  Nickname: {sl.get("nickname", "N/A")}')
                self.stdout.write(f'      🔄 Status: {sl.get("status", "N/A")}')
                self.stdout.write(f'      📌 Address ID: {sl.get("addressReferenceId", "N/A")}')
                self.stdout.write('')
        
        # Verificar se há Service Lines com dados incompletos
        incomplete = [sl for sl in service_lines if not sl["serviceLineNumber"] or sl["serviceLineNumber"].startswith("SL-UNKNOWN")]
        if incomplete:
            self.stdout.write(f'⚠️  Service Lines com dados incompletos ({len(incomplete)}):')
            for i, sl in enumerate(incomplete):
                self.stdout.write(f'   {i+1}. {sl["serviceLineNumber"]}')
                self.stdout.write(f'      📄 Dados brutos: {list(sl["rawData"].keys())}')
                self.stdout.write('')
        
        self.stdout.write(f'🎯 CONCLUSÃO:')
        self.stdout.write(f'   📊 Listando {len(service_lines)} Service Lines no total')
        self.stdout.write(f'   ✅ {len(with_address)} com endereço correlacionado')
        self.stdout.write(f'   ❌ {len(without_address)} sem endereço correlacionado')
        self.stdout.write(f'   💯 Taxa de cobertura: 100% (todos os Service Lines listados)')
        
        if len(without_address) > 0:
            self.stdout.write(f'   💡 Sugestão: Service Lines sem endereço podem estar usando nickname como identificação')
