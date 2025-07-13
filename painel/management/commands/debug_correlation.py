from django.core.management.base import BaseCommand
from painel.starlink_api import get_detailed_service_lines, get_starlink_addresses
import json

class Command(BaseCommand):
    help = 'Debug correlation between Service Lines and Addresses'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Iniciando debug da correlação Service Lines x Addresses...\n')
        
        # Buscar dados
        self.stdout.write('📡 Buscando Service Lines...')
        service_lines_result = get_detailed_service_lines()
        
        self.stdout.write('📍 Buscando Addresses...')
        addresses_result = get_starlink_addresses()
        
        if not service_lines_result or service_lines_result.get('error'):
            self.stdout.write(f'❌ Erro ao buscar Service Lines: {service_lines_result.get("error", "Erro desconhecido")}')
            return
            
        if not addresses_result or addresses_result.get('error'):
            self.stdout.write(f'❌ Erro ao buscar addresses: {addresses_result.get("error", "Erro desconhecido")}')
            return
            
        service_lines = service_lines_result.get('service_lines', [])
        addresses = addresses_result.get('addresses', {})
        
        self.stdout.write(f'✅ {len(service_lines)} Service Lines encontrados')
        self.stdout.write(f'✅ {len(addresses)} Addresses encontrados\n')
        
        # Analisar primeiros dados
        self.stdout.write('📊 ANÁLISE DE DADOS:\n')
        
        # Mostrar estrutura dos addresses
        self.stdout.write('🏠 Estrutura dos Addresses:')
        if addresses:
            first_addr_id = list(addresses.keys())[0]
            first_addr = addresses[first_addr_id]
            self.stdout.write(f'   Campos disponíveis: {list(first_addr.keys())}')
            self.stdout.write(f'   Exemplo: {json.dumps(first_addr, indent=2)}\n')
        
        # Analisar service lines
        self.stdout.write('📋 Análise dos Service Lines:')
        found_locations = 0
        not_found = 0
        
        for i, sl in enumerate(service_lines[:5]):  # Primeiros 5 para debug
            self.stdout.write(f'\n--- Service Line {i+1} ---')
            self.stdout.write(f'   ID: {sl.get("id", "N/A")}')
            self.stdout.write(f'   Nickname: {sl.get("nickname", "N/A")}')
            self.stdout.write(f'   Location: {sl.get("serviceLocation", "N/A")}')
            
            # Verificar se tem addressReferenceId
            if "addressReferenceId" in sl:
                self.stdout.write(f'   ✅ addressReferenceId: {sl["addressReferenceId"]}')
            else:
                self.stdout.write('   ❌ addressReferenceId não encontrado')
            
            # Mostrar dados brutos para debug
            raw_data = sl.get("rawData", {})
            if raw_data:
                self.stdout.write('   📄 Dados brutos - campos principais:')
                important_fields = ['serviceLineNumber', 'nickname', 'serviceLocation', 'serviceAddress', 'latitude', 'longitude', 'addressReferenceId']
                for field in important_fields:
                    if field in raw_data:
                        self.stdout.write(f'      - {field}: {raw_data[field]}')
                
                # Mostrar todos os campos disponíveis
                self.stdout.write(f'   📋 Todos os campos disponíveis: {list(raw_data.keys())}')
                
                # Buscar recursivamente por addressReferenceId
                self.stdout.write('   🔍 Busca recursiva por campos relacionados a endereço:')
                self.search_address_reference_id(raw_data, "   ")
            else:
                self.stdout.write('   ❌ Nenhum dado bruto disponível')
            
            if sl["serviceLocation"] != "Localização não informada":
                found_locations += 1
            else:
                not_found += 1
        
        self.stdout.write(f'\n📈 ESTATÍSTICAS:')
        self.stdout.write(f'   ✅ Com localização: {found_locations}')
        self.stdout.write(f'   ❌ Sem localização: {not_found}')
        
        # Tentar correlacionar com addresses
        self.stdout.write('\n🔗 TENTATIVA DE CORRELAÇÃO:')
        self.try_correlation(service_lines, addresses)
    
    def search_address_reference_id(self, data, indent=""):
        """Busca recursivamente por addressReferenceId nos dados"""
        if isinstance(data, dict):
            for key, value in data.items():
                if "address" in key.lower() or "location" in key.lower():
                    self.stdout.write(f'{indent}🎯 Campo relacionado a endereço: {key} = {value}')
                if isinstance(value, (dict, list)):
                    self.search_address_reference_id(value, indent + "  ")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    self.search_address_reference_id(item, indent + "  ")
    
    def try_correlation(self, service_lines, addresses):
        """Tenta correlacionar service lines com addresses"""
        
        # Os addresses já estão indexados por ID (addressReferenceId)
        self.stdout.write(f'   📇 Addresses disponíveis: {len(addresses)}')
        
        # Mostrar alguns IDs para debug
        address_ids = list(addresses.keys())[:5]
        self.stdout.write(f'   🔑 Primeiros IDs de addresses: {address_ids}')
        
        correlations_found = 0
        
        for i, sl in enumerate(service_lines[:10]):  # Primeiros 10 para teste
            self.stdout.write(f'\n   --- Correlação Service Line {i+1} ---')
            
            # Tentar vários campos possíveis
            possible_fields = [
                'addressReferenceId',
                'serviceAddressId', 
                'locationId',
                'addressId',
                'serviceLocationId'
            ]
            
            found_correlation = False
            
            for field in possible_fields:
                if field in sl:
                    ref_id = sl[field]
                    self.stdout.write(f'     Tentando campo {field}: {ref_id}')
                    
                    # Verificar se existe nos addresses
                    if ref_id in addresses:
                        addr = addresses[ref_id]
                        self.stdout.write(f'     ✅ CORRELAÇÃO ENCONTRADA!')
                        self.stdout.write(f'        Endereço: {addr.get("formatted", "N/A")}')
                        self.stdout.write(f'        Localidade: {addr.get("locality", "N/A")}, {addr.get("state", "N/A")}, {addr.get("country", "N/A")}')
                        correlations_found += 1
                        found_correlation = True
                        break
                    else:
                        self.stdout.write(f'     ❌ {ref_id} não encontrado nos addresses')
            
            if not found_correlation:
                self.stdout.write('     ❌ Nenhuma correlação encontrada')
                
                # Tentar buscar nos dados brutos
                raw_data = sl.get("raw_data", {})
                if raw_data:
                    self.stdout.write('     🔍 Buscando nos dados brutos...')
                    self.search_correlation_in_raw_data(raw_data, addresses)
        
        self.stdout.write(f'\n📊 RESULTADO DA CORRELAÇÃO:')
        self.stdout.write(f'   ✅ Correlações encontradas: {correlations_found}')
        self.stdout.write(f'   ❌ Sem correlação: {min(10, len(service_lines)) - correlations_found}')
    
    def search_correlation_in_raw_data(self, data, addresses):
        """Busca correlação nos dados brutos"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and value in addresses:
                    addr = addresses[value]
                    self.stdout.write(f'       ✅ Correlação encontrada no campo {key}: {value}')
                    self.stdout.write(f'          Endereço: {addr.get("formatted", "N/A")}')
                    return True
                elif isinstance(value, (dict, list)):
                    if self.search_correlation_in_raw_data(value, addresses):
                        return True
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    if self.search_correlation_in_raw_data(item, addresses):
                        return True
        return False
