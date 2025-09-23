#!/usr/bin/env python3
"""
Script para corrigir o erro 422 substituindo apenas a seção problemática
"""

import os

# Ler o arquivo
with open('painel/starlink_api.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituir a seção problemática
old_section = '''        # Tentar com diferentes formatos de payload para resolver erro 422
        print(f"🔍 Consultando billing cycles para {len(service_line_numbers)} service lines...")
        
        # Primeiro, tentar sem filtro de service lines (se a API mudou)
        payload_simple = {
            "previousBillingCycles": 2,
            "pageIndex": 0,
            "pageLimit": 100
        }
        
        print(f"📋 Tentando payload simples (sem filtros): {json.dumps(payload_simple, indent=2)}")
        print(f"🌐 URL: {url}")
        
        response = requests.post(url, json=payload_simple, headers=headers)
        print(f"📊 Status da resposta (sem filtros): {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Payload sem filtros funcionou!")
            billing_data = response.json()
        else:
            print(f"❌ Payload sem filtros falhou: {response.text}")
            
            # Tentar com serviceLinesFilter como strings
            payload_with_strings = {
                "serviceLinesFilter": [str(num) for num in service_line_numbers],
                "previousBillingCycles": 2,
                "pageIndex": 0,
                "pageLimit": 100
            }
            
            print(f"📋 Tentando com service lines como strings: {json.dumps(payload_with_strings, indent=2)}")
            response = requests.post(url, json=payload_with_strings, headers=headers)
            print(f"📊 Status da resposta (com strings): {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Payload com strings funcionou!")
                billing_data = response.json()
            else:
                print(f"❌ Payload com strings falhou: {response.text}")
                
                # Tentar com apenas um service line para teste
                payload_single = {
                    "serviceLinesFilter": [str(service_line_numbers[0])],
                    "previousBillingCycles": 1,
                    "pageIndex": 0,
                    "pageLimit": 10
                }
                
                print(f"📋 Tentando com apenas um service line: {json.dumps(payload_single, indent=2)}")
                response = requests.post(url, json=payload_single, headers=headers)
                print(f"📊 Status da resposta (single SL): {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ Payload com single SL funcionou!")
                    billing_data = response.json()
                else:
                    print(f"❌ Todos os payloads falharam. Última resposta: {response.text}")
                    print(f"📋 Headers da resposta: {dict(response.headers)}")
                    
                    return {
                        "error": f"Erro na consulta de billing: {response.status_code} - {response.text}",
                        "usage_data": [],
                        "statistics": {},
                        "total_lines": 0,
                        "debug_info": {
                            "service_lines_count": len(service_line_numbers),
                            "first_service_line": service_line_numbers[0] if service_line_numbers else None,
                            "response_text": response.text,
                            "headers": dict(response.headers)
                        }
                    }
        
        billing_data = response.json()'''

new_section = '''        print(f"🔍 Consultando billing cycles...")
        
        # Usar APENAS payload simples sem filtros (que sabemos que funciona)
        payload_simple = {
            "previousBillingCycles": 2,
            "pageIndex": 0,
            "pageLimit": 100
        }
        
        print(f"📋 Usando payload simples: {json.dumps(payload_simple, indent=2)}")
        
        response = requests.post(url, json=payload_simple, headers=headers)
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Falha na API: {response.text}")
            return {
                "error": f"Erro na consulta de billing: {response.status_code}",
                "usage_data": [],
                "statistics": {},
                "total_lines": 0
            }
        
        print("✅ Sucesso na consulta!")
        billing_data = response.json()'''

if old_section in content:
    content = content.replace(old_section, new_section)
    print("✅ Substituição realizada com sucesso!")
    
    # Salvar o arquivo
    with open('painel/starlink_api.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Arquivo salvo!")
else:
    print("❌ Seção não encontrada - tentando busca mais específica...")
    
    # Tentar encontrar apenas uma parte menor
    marker = "Tentar com diferentes formatos de payload para resolver erro 422"
    if marker in content:
        print(f"✅ Marcador encontrado!")
    else:
        print(f"❌ Marcador não encontrado")
