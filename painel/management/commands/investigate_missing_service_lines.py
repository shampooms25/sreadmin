from django.core.management.base import BaseCommand
from painel.starlink_api import get_valid_token
import requests
import json

class Command(BaseCommand):
    help = 'Investiga por que só estamos vendo 50 Service Lines em vez de 70'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Investigando discrepância: 70 unidades no painel vs 50 na API...\n')
        
        token = get_valid_token()
        if not token:
            self.stdout.write('❌ Erro ao obter token')
            return
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        base_url = "https://web-api.starlink.com/enterprise/v1/account/ACC-2744134-64041-5"
        
        # 1. Testar endpoint /service-lines com paginação
        self.stdout.write('📡 1. Testando endpoint /service-lines com paginação...')
        service_lines_url = f"{base_url}/service-lines"
        
        try:
            response = requests.get(service_lines_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            self.stdout.write(f'   📊 Estrutura da resposta: {list(data.keys())}')
            
            if 'content' in data:
                content = data['content']
                self.stdout.write(f'   📄 Content: {list(content.keys())}')
                
                total_count = content.get('totalCount', 0)
                page_index = content.get('pageIndex', 0)
                limit = content.get('limit', 0)
                is_last_page = content.get('isLastPage', False)
                results = content.get('results', [])
                
                self.stdout.write(f'   📈 Total Count: {total_count}')
                self.stdout.write(f'   📄 Page Index: {page_index}')
                self.stdout.write(f'   📏 Limit: {limit}')
                self.stdout.write(f'   📋 Is Last Page: {is_last_page}')
                self.stdout.write(f'   🔢 Results nesta página: {len(results)}')
                
                # Se não é a última página, há mais dados!
                if not is_last_page:
                    self.stdout.write(f'   ⚠️  ATENÇÃO: Não é a última página! Há mais dados disponíveis.')
                    
                    # Tentar buscar próximas páginas
                    all_results = results.copy()
                    current_page = page_index + 1
                    
                    while not is_last_page and current_page < 10:  # Limite de segurança
                        next_url = f"{service_lines_url}?pageIndex={current_page}&limit={limit}"
                        self.stdout.write(f'   📖 Buscando página {current_page}...')
                        
                        next_response = requests.get(next_url, headers=headers)
                        if next_response.status_code == 200:
                            next_data = next_response.json()
                            next_content = next_data.get('content', {})
                            next_results = next_content.get('results', [])
                            is_last_page = next_content.get('isLastPage', True)
                            
                            all_results.extend(next_results)
                            self.stdout.write(f'      ✅ Página {current_page}: {len(next_results)} resultados')
                            current_page += 1
                        else:
                            self.stdout.write(f'      ❌ Erro na página {current_page}: {next_response.status_code}')
                            break
                    
                    self.stdout.write(f'   📊 TOTAL APÓS PAGINAÇÃO: {len(all_results)} Service Lines')
                    
                    # Analisar os resultados extras
                    extra_results = all_results[len(results):]
                    if extra_results:
                        self.stdout.write(f'   🔍 Primeiros 5 Service Lines das páginas extras:')
                        for i, sl in enumerate(extra_results[:5]):
                            self.stdout.write(f'      {i+1}. {sl.get("serviceLineNumber", "N/A")}')
                            self.stdout.write(f'         Status: {sl.get("active", "N/A")}')
                            self.stdout.write(f'         Nickname: {sl.get("nickname", "N/A")}')
                            self.stdout.write(f'         Address ID: {sl.get("addressReferenceId", "N/A")}')
                
        except Exception as e:
            self.stdout.write(f'   ❌ Erro: {e}')
        
        # 2. Testar diferentes filtros
        self.stdout.write('\n📡 2. Testando endpoint /service-lines com filtros diferentes...')
        
        # Testar com limit maior
        try:
            large_limit_url = f"{service_lines_url}?limit=100"
            response = requests.get(large_limit_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('content', {}).get('results', [])
                self.stdout.write(f'   📊 Com limit=100: {len(results)} Service Lines')
                
                # Analisar status
                active_count = len([sl for sl in results if sl.get('active', False)])
                inactive_count = len(results) - active_count
                
                self.stdout.write(f'   🟢 Ativos: {active_count}')
                self.stdout.write(f'   🔴 Inativos: {inactive_count}')
                
        except Exception as e:
            self.stdout.write(f'   ❌ Erro com limit=100: {e}')
        
        # 3. Comparar com billing-cycles
        self.stdout.write('\n📡 3. Comparando com endpoint /billing-cycles/query...')
        
        payload = {
            "serviceLinesFilter": [],
            "previousBillingCycles": 1,
            "pageIndex": 0,
            "pageLimit": 100
        }
        
        try:
            billing_url = f"{base_url}/billing-cycles/query"
            response = requests.post(billing_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('content', {}).get('results', [])
                self.stdout.write(f'   📊 Billing cycles: {len(results)} Service Lines')
                
                # Comparar IDs
                billing_service_lines = [sl.get('serviceLineNumber') for sl in results]
                self.stdout.write(f'   🔍 Primeiros 5 Service Lines do billing: {billing_service_lines[:5]}')
                
        except Exception as e:
            self.stdout.write(f'   ❌ Erro no billing-cycles: {e}')
        
        # 4. Verificar se há filtros implícitos
        self.stdout.write('\n📡 4. Verificando possíveis filtros implícitos...')
        
        # Teorias possíveis:
        theories = [
            "Paginação não implementada corretamente",
            "Filtros implícitos por status (ativo/inativo)",
            "Filtros por tipo de serviço",
            "Filtros por data (service lines antigas não aparecem)",
            "Diferentes endpoints para diferentes tipos de unidades",
            "Limitação de API por permissão"
        ]
        
        for i, theory in enumerate(theories, 1):
            self.stdout.write(f'   {i}. {theory}')
        
        self.stdout.write('\n🎯 PRÓXIMOS PASSOS:')
        self.stdout.write('   1. Implementar paginação correta se necessário')
        self.stdout.write('   2. Verificar filtros de status')
        self.stdout.write('   3. Comparar com dados do painel manualmente')
        self.stdout.write('   4. Testar endpoints alternativos')
