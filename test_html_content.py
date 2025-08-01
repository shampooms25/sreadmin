#!/usr/bin/env python3
"""
Teste específico para verificar o conteúdo HTML do endpoint
"""

import requests
import re

def test_html_content():
    """Testa o conteúdo HTML retornado pelo endpoint"""
    print("🌐 TESTANDO CONTEÚDO HTML DO ENDPOINT...")
    print("=" * 50)
    
    try:
        url = "http://localhost:8000/admin/starlink/usage-report/?account_id=ACC-2744134-64041-5"
        print(f"📋 URL: {url}")
        
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            print(f"✅ Status: {response.status_code}")
            print(f"📏 Tamanho: {len(content)} caracteres")
            
            # Procurar por nossa Service Line específica
            target_sl = "SL-854897-75238-43"
            if target_sl in content:
                print(f"✅ Service Line {target_sl} encontrada!")
                
                # Extrair a linha da tabela que contém nossa SL
                # Usar regex para encontrar a linha completa
                pattern = rf'<tr[^>]*>.*?{re.escape(target_sl)}.*?</tr>'
                match = re.search(pattern, content, re.DOTALL)
                
                if match:
                    table_row = match.group(0)
                    print(f"📋 Linha da tabela encontrada:")
                    print(f"   {table_row[:200]}...")
                    
                    # Procurar por valores de GB
                    gb_values = re.findall(r'(\d+\.?\d*)\s*GB', table_row)
                    print(f"📊 Valores GB encontrados: {gb_values}")
                    
                    # Verificar se há um valor próximo de 90
                    for value_str in gb_values:
                        try:
                            value = float(value_str)
                            if 85 <= value <= 95:  # Tolerância maior
                                print(f"✅ Valor correto encontrado: {value} GB")
                                return True
                        except ValueError:
                            continue
                    
                    print(f"❌ Nenhum valor próximo de 90 GB encontrado")
                    return False
                else:
                    print(f"❌ Linha da tabela não encontrada")
                    return False
            else:
                print(f"❌ Service Line {target_sl} não encontrada")
                
                # Vamos ver se há outras Service Lines
                sl_matches = re.findall(r'SL-\d+-\d+-\d+', content)
                if sl_matches:
                    print(f"📋 Service Lines encontradas no HTML: {sl_matches[:5]}...")
                else:
                    print(f"📋 Nenhuma Service Line encontrada no HTML")
                    
                    # Vamos ver se há mensagem de erro
                    error_pattern = r'<div class="error-message">.*?</div>'
                    error_match = re.search(error_pattern, content, re.DOTALL)
                    if error_match:
                        error_content = error_match.group(0)
                        print(f"❌ Erro encontrado: {error_content}")
                    
                    # Vamos ver se há mensagem de empty state
                    empty_pattern = r'<div class="empty-state">.*?</div>'
                    empty_match = re.search(empty_pattern, content, re.DOTALL)
                    if empty_match:
                        empty_content = empty_match.group(0)
                        print(f"📭 Estado vazio: {empty_content}")
                
                return False
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = test_html_content()
    print(f"\n🎯 Resultado: {'✅ SUCESSO' if success else '❌ FALHA'}")
