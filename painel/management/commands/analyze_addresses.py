from django.core.management.base import BaseCommand
from painel.starlink_api import get_starlink_addresses, get_valid_token
import requests
import json

class Command(BaseCommand):
    help = 'Analisa dados de endereços para encontrar correlação'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Analisando dados de endereços...'))
        
        try:
            # Primeiro, obter todos os endereços
            addresses_result = get_starlink_addresses()
            
            if not addresses_result.get("success"):
                self.stdout.write(self.style.ERROR(f'❌ Erro ao obter endereços: {addresses_result.get("error")}'))
                return
            
            # Obter dados brutos completos dos endereços
            token = get_valid_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            addresses_url = "https://web-api.starlink.com/enterprise/v1/account/ACC-2744134-64041-5/addresses"
            response = requests.get(addresses_url, headers=headers)
            raw_addresses = response.json()
            
            if "content" in raw_addresses and "results" in raw_addresses["content"]:
                addresses = raw_addresses["content"]["results"]
                
                self.stdout.write(f'📍 Total de endereços: {len(addresses)}')
                self.stdout.write('\n🔍 ANÁLISE DETALHADA DOS PRIMEIROS 3 ENDEREÇOS:')
                
                for i, addr in enumerate(addresses[:3]):
                    self.stdout.write(f'\n📍 ENDEREÇO {i+1}:')
                    self.stdout.write(f'   ID: {addr.get("addressReferenceId")}')
                    self.stdout.write(f'   Localidade: {addr.get("locality")}')
                    self.stdout.write(f'   Estado: {addr.get("administrativeArea")} ({addr.get("administrativeAreaCode")})')
                    self.stdout.write(f'   País: {addr.get("region")} ({addr.get("regionCode")})')
                    self.stdout.write(f'   Endereço formatado: {addr.get("formattedAddress")}')
                    self.stdout.write(f'   Coordenadas: {addr.get("latitude")}, {addr.get("longitude")}')
                    self.stdout.write(f'   CEP: {addr.get("postalCode")}')
                    self.stdout.write(f'   Metadata: {addr.get("metadata")}')
                    self.stdout.write(f'   Todos os campos: {list(addr.keys())}')
                
                # Vamos tentar outros endpoints que podem ter correlação
                self.stdout.write('\n🔍 TESTANDO OUTROS ENDPOINTS...')
                
                endpoints_to_test = [
                    "/account/ACC-2744134-64041-5",
                    "/accounts/ACC-2744134-64041-5/service-lines", 
                    "/accounts/ACC-2744134-64041-5/usage",
                    "/accounts/ACC-2744134-64041-5/sites",
                    "/accounts/ACC-2744134-64041-5/locations"
                ]
                
                base_url = "https://web-api.starlink.com/enterprise/v1"
                
                for endpoint in endpoints_to_test:
                    url = base_url + endpoint
                    self.stdout.write(f'\n🔍 Testando: {endpoint}')
                    
                    try:
                        response = requests.get(url, headers=headers)
                        
                        if response.status_code == 200:
                            self.stdout.write(f'✅ SUCESSO!')
                            data = response.json()
                            
                            if isinstance(data, dict) and "content" in data:
                                if "results" in data["content"]:
                                    results = data["content"]["results"]
                                    self.stdout.write(f'   📊 {len(results)} resultados')
                                    if results:
                                        first = results[0]
                                        self.stdout.write(f'   🔑 Campos: {list(first.keys())}')
                                        
                                        # Procurar campos relevantes
                                        relevant_fields = []
                                        for key in first.keys():
                                            if any(term in key.lower() for term in ['service', 'line', 'address', 'location', 'id', 'ref']):
                                                relevant_fields.append(key)
                                        
                                        if relevant_fields:
                                            self.stdout.write(f'   🎯 Campos relevantes: {relevant_fields}')
                                            for field in relevant_fields:
                                                value = first.get(field)
                                                if isinstance(value, (str, int, float)):
                                                    self.stdout.write(f'      {field}: {value}')
                                                elif isinstance(value, dict):
                                                    self.stdout.write(f'      {field}: {list(value.keys())}')
                                
                                else:
                                    self.stdout.write(f'   🔑 Campos: {list(data["content"].keys())}')
                            else:
                                self.stdout.write(f'   🔑 Campos raiz: {list(data.keys())}')
                        
                        elif response.status_code == 404:
                            self.stdout.write(f'❌ Não encontrado')
                        elif response.status_code == 403:
                            self.stdout.write(f'⚠️ Sem permissão')
                        else:
                            self.stdout.write(f'❌ Erro {response.status_code}')
                            
                    except Exception as e:
                        self.stdout.write(f'❌ Erro: {e}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro inesperado: {e}'))
