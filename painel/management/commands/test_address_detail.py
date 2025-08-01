from django.core.management.base import BaseCommand
from painel.starlink_api import get_starlink_addresses, get_valid_token
import requests
import json

class Command(BaseCommand):
    help = 'Testa o endpoint /addresses/{addressReferenceId}'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Testando endpoint /addresses/{addressReferenceId}...\n')
        
        # Primeiro, buscar os addresses
        addresses_result = get_starlink_addresses()
        
        if not addresses_result or addresses_result.get('error'):
            self.stdout.write(f'❌ Erro ao buscar addresses: {addresses_result.get("error", "Erro desconhecido")}')
            return
        
        addresses = addresses_result.get('addresses', {})
        self.stdout.write(f'✅ {len(addresses)} Addresses encontrados')
        
        # Testar o endpoint detalhado com os primeiros 3 addresses
        token = get_valid_token()
        if not token:
            self.stdout.write('❌ Erro ao obter token')
            return
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        tested_count = 0
        max_tests = 3
        
        for address_id, address_info in addresses.items():
            if tested_count >= max_tests:
                break
                
            self.stdout.write(f'\n📍 Testando Address ID: {address_id}')
            self.stdout.write(f'   Localização conhecida: {address_info["locality"]}, {address_info["state"]}, {address_info["country"]}')
            
            # Fazer requisição para o endpoint detalhado
            detail_url = f"https://web-api.starlink.com/enterprise/v1/account/ACC-2744134-64041-5/addresses/{address_id}"
            
            try:
                response = requests.get(detail_url, headers=headers)
                
                if response.status_code == 200:
                    detail_data = response.json()
                    self.stdout.write('   ✅ Endpoint detalhado funcionou!')
                    self.stdout.write(f'   📄 Dados retornados: {json.dumps(detail_data, indent=2)[:500]}...')
                    
                    # Verificar se há informações adicionais
                    if 'serviceLines' in detail_data:
                        self.stdout.write(f'   🎯 ENCONTRADO! Service Lines vinculados: {len(detail_data["serviceLines"])}')
                        for sl in detail_data["serviceLines"][:3]:  # Mostrar primeiros 3
                            self.stdout.write(f'      - {sl.get("serviceLineNumber", "N/A")}')
                    else:
                        self.stdout.write('   ❌ Nenhum Service Line vinculado encontrado neste address')
                        
                elif response.status_code == 404:
                    self.stdout.write('   ❌ Address não encontrado (404)')
                else:
                    self.stdout.write(f'   ❌ Erro HTTP {response.status_code}: {response.text[:200]}...')
                    
            except Exception as e:
                self.stdout.write(f'   ❌ Erro na requisição: {e}')
            
            tested_count += 1
        
        self.stdout.write(f'\n📊 RESUMO:')
        self.stdout.write(f'   🔍 {tested_count} addresses testados')
        self.stdout.write(f'   💡 CONCLUSÃO: O endpoint /addresses/{{addressReferenceId}} pode conter')
        self.stdout.write(f'      informações de Service Lines vinculados a cada endereço!')
