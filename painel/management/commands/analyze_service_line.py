from django.core.management.base import BaseCommand
from painel.starlink_api import get_valid_token
import requests
import json

class Command(BaseCommand):
    help = 'Analisa um Service Line específico para encontrar dados de localização'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Analisando Service Line específico...'))
        
        # Service Line de exemplo
        service_line = "SL-395008-69755-34"
        base_url = "https://web-api.starlink.com/enterprise/v1"
        
        # Endpoints para testar
        endpoints_to_test = [
            f"/accounts/ACC-2744134-64041-5/service-lines/{service_line}",
            f"/accounts/ACC-2744134-64041-5/service-lines/{service_line}/details",
            f"/accounts/ACC-2744134-64041-5/service-lines/{service_line}/location",
            f"/service-lines/{service_line}",
            f"/service-lines/{service_line}/details",
            f"/service-lines/{service_line}/location",
            f"/accounts/ACC-2744134-64041-5/terminals",
            f"/accounts/ACC-2744134-64041-5/devices",
            f"/accounts/ACC-2744134-64041-5/subscriptions"
        ]
        
        try:
            token = get_valid_token()
            if not token:
                self.stdout.write(self.style.ERROR('❌ Não foi possível obter token'))
                return

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            successful_endpoints = []
            
            for endpoint in endpoints_to_test:
                url = base_url + endpoint
                self.stdout.write(f'\n🔍 Testando: {endpoint}')
                
                try:
                    response = requests.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        self.stdout.write(f'✅ SUCESSO! {response.status_code}')
                        data = response.json()
                        successful_endpoints.append(endpoint)
                        
                        # Analisar a estrutura dos dados
                        if isinstance(data, dict):
                            if "content" in data and "results" in data["content"]:
                                results = data["content"]["results"]
                                self.stdout.write(f'   📊 {len(results)} resultados encontrados')
                                if results:
                                    first_result = results[0]
                                    self.stdout.write(f'   🔑 Campos: {list(first_result.keys())}')
                                    
                                    # Procurar por campos relacionados a localização
                                    location_fields = []
                                    for key in first_result.keys():
                                        if any(term in key.lower() for term in ['address', 'location', 'lat', 'lng', 'coordinates', 'site', 'terminal']):
                                            location_fields.append(key)
                                    
                                    if location_fields:
                                        self.stdout.write(f'   📍 Campos de localização: {location_fields}')
                                        for field in location_fields:
                                            self.stdout.write(f'      {field}: {first_result.get(field)}')
                            else:
                                self.stdout.write(f'   🔑 Campos raiz: {list(data.keys())}')
                        else:
                            self.stdout.write(f'   📋 Tipo de dados: {type(data)}')
                            
                    elif response.status_code == 404:
                        self.stdout.write(f'❌ Não encontrado (404)')
                    elif response.status_code == 403:
                        self.stdout.write(f'⚠️ Sem permissão (403)')
                    else:
                        self.stdout.write(f'❌ Erro {response.status_code}: {response.text[:100]}')
                        
                except Exception as e:
                    self.stdout.write(f'❌ Erro na requisição: {e}')
            
            if successful_endpoints:
                self.stdout.write(f'\n✅ Endpoints que funcionaram: {successful_endpoints}')
            else:
                self.stdout.write(f'\n❌ Nenhum endpoint funcionou')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro inesperado: {e}'))
