from django.core.management.base import BaseCommand
from painel.starlink_api import get_detailed_service_lines
import json


class Command(BaseCommand):
    help = 'Analisa os dados existentes do billing-cycles para extrair informações de localização'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Analisando dados do billing-cycles para localização...'))
        
        try:
            # Usar a função existente que já funciona
            result = get_detailed_service_lines()
            
            if "error" in result:
                self.stdout.write(self.style.ERROR(f'❌ Erro: {result["error"]}'))
                return
            
            self.stdout.write(self.style.SUCCESS('✅ Dados obtidos com sucesso!'))
            
            service_lines = result.get("service_lines", [])
            
            if not service_lines:
                self.stdout.write(self.style.WARNING('⚠️  Nenhum service line encontrado'))
                return
            
            # Analisar cada service line
            print(f"\n{'='*80}")
            print(f"📋 ANÁLISE DETALHADA DE {len(service_lines)} SERVICE LINES")
            print(f"{'='*80}")
            
            for i, service_line in enumerate(service_lines, 1):
                print(f"\n🔍 SERVICE LINE {i}: {service_line.get('serviceLineNumber', 'N/A')}")
                print(f"{'─'*60}")
                
                raw_data = service_line.get('rawData', {})
                
                if raw_data:
                    print(f"📄 DADOS BRUTOS COMPLETOS:")
                    print(json.dumps(raw_data, indent=2, ensure_ascii=False))
                    print(f"{'─'*60}")
                    
                    # Procurar por campos relacionados a localização
                    location_fields = []
                    
                    def find_location_fields(data, prefix=""):
                        if isinstance(data, dict):
                            for key, value in data.items():
                                full_key = f"{prefix}.{key}" if prefix else key
                                
                                # Verificar se o campo pode conter informação de localização
                                location_keywords = ['address', 'location', 'site', 'place', 'city', 'country', 'state', 'region', 'lat', 'lon', 'coordinate', 'geo', 'nickname', 'name']
                                
                                if any(keyword in key.lower() for keyword in location_keywords):
                                    location_fields.append({
                                        'field': full_key,
                                        'value': value,
                                        'type': type(value).__name__
                                    })
                                
                                # Recursivamente procurar em objetos aninhados
                                if isinstance(value, dict):
                                    find_location_fields(value, full_key)
                                elif isinstance(value, list) and value and isinstance(value[0], dict):
                                    find_location_fields(value[0], f"{full_key}[0]")
                    
                    find_location_fields(raw_data)
                    
                    if location_fields:
                        print(f"📍 CAMPOS RELACIONADOS À LOCALIZAÇÃO ENCONTRADOS:")
                        for field in location_fields:
                            print(f"   🔹 {field['field']}: {field['value']} ({field['type']})")
                    else:
                        print(f"❌ Nenhum campo relacionado à localização encontrado")
                
                else:
                    print(f"❌ Nenhum dado bruto disponível")
                
                print(f"{'─'*60}")
            
            print(f"\n{'='*80}")
            print(f"✅ Análise concluída!")
            print(f"{'='*80}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro inesperado: {e}'))
