from django.core.management.base import BaseCommand
from painel.starlink_api import get_service_lines_with_location

class Command(BaseCommand):
    help = 'Analisa os dados de status dos Service Lines'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Analisando dados de status dos Service Lines...\n')
        
        result = get_service_lines_with_location()
        
        if result.get("error"):
            self.stdout.write(f'❌ Erro: {result["error"]}')
            return
        
        service_lines = result.get("service_lines", [])
        
        # Analisar os primeiros Service Lines para entender os dados de status
        self.stdout.write(f'📊 Analisando estrutura de dados de status...\n')
        
        for i, sl in enumerate(service_lines[:5]):
            self.stdout.write(f'📡 Service Line {i+1}: {sl["serviceLineNumber"]}')
            self.stdout.write(f'   Status atual: {sl.get("status", "N/A")}')
            self.stdout.write(f'   Active: {sl["rawData"].get("active", "N/A")}')
            
            # Verificar todos os campos que podem indicar status
            raw_data = sl["rawData"]
            status_fields = []
            
            for key, value in raw_data.items():
                if any(word in key.lower() for word in ['status', 'state', 'active', 'online', 'offline', 'health', 'connection']):
                    status_fields.append(f'{key}: {value}')
            
            if status_fields:
                self.stdout.write(f'   🔍 Campos relacionados a status:')
                for field in status_fields:
                    self.stdout.write(f'      - {field}')
            
            # Verificar se há dados de data usage recente
            if 'dataBlocks' in raw_data:
                data_blocks = raw_data['dataBlocks']
                self.stdout.write(f'   📊 Data blocks: {len(data_blocks) if isinstance(data_blocks, list) else data_blocks}')
            
            self.stdout.write('')
        
        # Análise estatística de status
        self.stdout.write(f'📈 ANÁLISE ESTATÍSTICA DE STATUS:')
        
        # Contar por status atual
        status_count = {}
        for sl in service_lines:
            status = sl.get("status", "Desconhecido")
            status_count[status] = status_count.get(status, 0) + 1
        
        for status, count in status_count.items():
            self.stdout.write(f'   {status}: {count}')
        
        # Analisar campo 'active'
        active_count = 0
        inactive_count = 0
        unknown_count = 0
        
        for sl in service_lines:
            active = sl["rawData"].get("active")
            if active is True:
                active_count += 1
            elif active is False:
                inactive_count += 1
            else:
                unknown_count += 1
        
        self.stdout.write(f'\n📊 Campo "active":')
        self.stdout.write(f'   True: {active_count}')
        self.stdout.write(f'   False: {inactive_count}')
        self.stdout.write(f'   Desconhecido: {unknown_count}')
        
        # Verificar se há outros indicadores de status
        self.stdout.write(f'\n🔍 Investigando outros indicadores de status...')
        
        # Verificar datas para identificar "sem dados recentes"
        from datetime import datetime, timedelta
        import dateutil.parser
        
        recent_threshold = datetime.now() - timedelta(days=7)  # 7 dias atrás
        
        with_recent_data = 0
        without_recent_data = 0
        no_date_info = 0
        
        for sl in service_lines:
            raw_data = sl["rawData"]
            
            # Procurar por campos de data que podem indicar atividade recente
            last_activity = None
            
            # Verificar vários campos de data possíveis
            date_fields = ['lastUpdated', 'lastActivity', 'lastDataTime', 'endDate']
            
            for field in date_fields:
                if field in raw_data and raw_data[field]:
                    try:
                        last_activity = dateutil.parser.parse(raw_data[field])
                        break
                    except:
                        continue
            
            if last_activity:
                if last_activity > recent_threshold:
                    with_recent_data += 1
                else:
                    without_recent_data += 1
            else:
                no_date_info += 1
        
        self.stdout.write(f'   📅 Com dados recentes (últimos 7 dias): {with_recent_data}')
        self.stdout.write(f'   📅 Sem dados recentes: {without_recent_data}')
        self.stdout.write(f'   📅 Sem informação de data: {no_date_info}')
        
        self.stdout.write(f'\n💡 RECOMENDAÇÕES PARA IMPLEMENTAÇÃO:')
        self.stdout.write(f'   1. Usar campo "active" como base para status')
        self.stdout.write(f'   2. Implementar lógica para detectar "sem dados recentes"')
        self.stdout.write(f'   3. Criar categorias: Ativo, Offline, Sem Dados')
        self.stdout.write(f'   4. Cores: Verde (ativo), Vermelho (offline), Amarelo (sem dados)')
