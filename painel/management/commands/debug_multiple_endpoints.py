from django.core.management.base import BaseCommand
from painel.starlink_api import get_valid_token
import requests
import json

class Command(BaseCommand):
    help = 'Analisa múltiplos endpoints para encontrar correlação'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Analisando múltiplos endpoints para correlação...\n')
        
        token = get_valid_token()
        if not token:
            self.stdout.write('❌ Erro ao obter token')
            return
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        base_url = "https://web-api.starlink.com/enterprise/v1/account/ACC-2744134-64041-5"
        
        endpoints_to_test = [
            "/service-lines",
            "/subscriptions",
            "/services",
            "/locations",
            "/service-locations",
            "/billing-cycles",
            "/equipment",
            "/installations"
        ]
        
        self.stdout.write('📡 Testando endpoints disponíveis...\n')
        
        for endpoint in endpoints_to_test:
            url = f"{base_url}{endpoint}"
            self.stdout.write(f'🔍 Testando: {endpoint}')
            
            try:
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    self.stdout.write(f'   ✅ Sucesso! Status: {response.status_code}')
                    
                    # Analisar estrutura dos dados
                    if isinstance(data, dict):
                        if 'content' in data:
                            content = data['content']
                            if isinstance(content, dict):
                                self.stdout.write(f'   📄 Estrutura: {list(content.keys())}')
                                
                                # Verificar se há results
                                if 'results' in content:
                                    results = content['results']
                                    if isinstance(results, list) and len(results) > 0:
                                        self.stdout.write(f'   📊 {len(results)} resultados encontrados')
                                        first_result = results[0]
                                        if isinstance(first_result, dict):
                                            self.stdout.write(f'   🔑 Campos do primeiro resultado: {list(first_result.keys())}')
                                            
                                            # Verificar se há campos relacionados a endereço
                                            address_fields = [k for k in first_result.keys() if 'address' in k.lower() or 'location' in k.lower()]
                                            if address_fields:
                                                self.stdout.write(f'   🎯 Campos relacionados a endereço: {address_fields}')
                                                for field in address_fields:
                                                    self.stdout.write(f'      - {field}: {first_result[field]}')
                            else:
                                self.stdout.write(f'   📄 Content é lista com {len(content)} itens')
                        else:
                            self.stdout.write(f'   📄 Estrutura raiz: {list(data.keys())}')
                    else:
                        self.stdout.write(f'   � Dados são lista com {len(data)} itens')
                        
                elif response.status_code == 404:
                    self.stdout.write(f'   ❌ Endpoint não encontrado (404)')
                elif response.status_code == 403:
                    self.stdout.write(f'   ❌ Sem permissão (403)')
                else:
                    self.stdout.write(f'   ❌ Erro HTTP {response.status_code}')
                    
            except Exception as e:
                self.stdout.write(f'   ❌ Erro na requisição: {e}')
            
            self.stdout.write('')  # linha em branco
        
        # Agora vamos testar o endpoint que já sabemos que funciona com mais detalhes
        self.stdout.write('📊 Analisando endpoint billing-cycles com mais detalhes...\n')
        
        payload = {
            "serviceLinesFilter": [],
            "previousBillingCycles": 1,  # Reduzir para análise
            "pageIndex": 0,
            "pageLimit": 5  # Apenas 5 para análise
        }
        
        url = f"{base_url}/billing-cycles/query"
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.stdout.write('✅ Dados de billing-cycles obtidos')
                
                if 'content' in data and 'results' in data['content']:
                    results = data['content']['results']
                    self.stdout.write(f'📊 {len(results)} Service Lines encontrados')
                    
                    for i, result in enumerate(results[:2]):  # Analisar primeiros 2
                        self.stdout.write(f'\n🔍 Service Line {i+1}:')
                        self.stdout.write(f'   📡 Número: {result.get("serviceLineNumber", "N/A")}')
                        self.stdout.write(f'   📄 Todos os campos: {list(result.keys())}')
                        
                        # Procurar por campos relacionados a endereço/localização
                        for key, value in result.items():
                            if 'address' in key.lower() or 'location' in key.lower():
                                self.stdout.write(f'   🎯 Campo relacionado: {key} = {value}')
                            elif isinstance(value, dict):
                                # Verificar se há campos de endereço dentro de objetos
                                for subkey, subvalue in value.items():
                                    if 'address' in subkey.lower() or 'location' in subkey.lower():
                                        self.stdout.write(f'   🎯 Campo relacionado em {key}: {subkey} = {subvalue}')
                        
                        # Verificar billing cycles
                        if 'billingCycles' in result:
                            cycles = result['billingCycles']
                            if isinstance(cycles, list) and len(cycles) > 0:
                                self.stdout.write(f'   📊 {len(cycles)} billing cycles encontrados')
                                first_cycle = cycles[0]
                                if isinstance(first_cycle, dict):
                                    self.stdout.write(f'   🔑 Campos do billing cycle: {list(first_cycle.keys())}')
                                    
                                    # Verificar se há campos de endereço nos billing cycles
                                    for key, value in first_cycle.items():
                                        if 'address' in key.lower() or 'location' in key.lower():
                                            self.stdout.write(f'   🎯 Campo relacionado no billing cycle: {key} = {value}')
                                            
        except Exception as e:
            self.stdout.write(f'❌ Erro ao analisar billing-cycles: {e}')
        
        self.stdout.write('\n🎯 CONCLUSÃO:')
        self.stdout.write('   A correlação entre Service Lines e Addresses pode estar:')
        self.stdout.write('   1. Em um endpoint específico não testado')
        self.stdout.write('   2. Nos metadados dos billing cycles')
        self.stdout.write('   3. Requer uma abordagem diferente de correlação')