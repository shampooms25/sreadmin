#!/usr/bin/env python3
"""
Script para testar o download de PDF via linha de comando
"""

import requests
import datetime

def test_pdf_download():
    """Testa o download do PDF do relatório de disponibilidade"""
    
    # URL do relatório com parâmetros
    base_url = "http://localhost:8000/starlink/starlink/availability-report/"
    params = {
        'service_lines': ['SL-5242096-78596-88', 'SL-3771955-54471-83', 'SL-3481747-13739-82'],
        'start_date': '2025-01-03',
        'end_date': '2025-02-02',
        'export': 'pdf'
    }
    
    try:
        print("🔄 Iniciando teste de download do PDF...")
        print(f"📊 URL: {base_url}")
        print(f"📋 Parâmetros: {params}")
        
        # Fazer requisição
        response = requests.get(base_url, params=params)
        
        print(f"📈 Status HTTP: {response.status_code}")
        print(f"📄 Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"📁 Content-Length: {len(response.content)} bytes")
        print(f"💾 Content-Disposition: {response.headers.get('Content-Disposition', 'N/A')}")
        
        if response.status_code == 200:
            # Salvar arquivo
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"teste_relatorio_disponibilidade_{timestamp}.pdf"
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ PDF salvo com sucesso: {filename}")
            print(f"📊 Arquivo tem {len(response.content)} bytes")
            
            # Verificar se é realmente um PDF
            if response.content.startswith(b'%PDF-'):
                print("✅ Arquivo é um PDF válido")
            else:
                print("❌ Arquivo não parece ser um PDF válido")
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"📄 Resposta: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")

def test_consumption_pdf():
    """Testa o download do PDF do relatório de consumo"""
    
    base_url = "http://localhost:8000/starlink/starlink/service-lines/"
    params = {
        'service_lines': ['SL-5242096-78596-88', 'SL-3771955-54471-83'],
        'export': 'pdf'
    }
    
    try:
        print("\n🔄 Testando relatório de consumo...")
        response = requests.get(base_url, params=params)
        
        print(f"📈 Status HTTP: {response.status_code}")
        print(f"📄 Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"📁 Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200 and response.content.startswith(b'%PDF-'):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"teste_relatorio_consumo_{timestamp}.pdf"
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ PDF de consumo salvo: {filename}")
        else:
            print("❌ Erro no relatório de consumo")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🔬 Testador de Download de PDF - SRAdmin")
    print("="*50)
    
    test_pdf_download()
    test_consumption_pdf()
    
    print("\n" + "="*50)
    print("📋 Instruções para testar no navegador:")
    print("1. Acesse: http://localhost:8000/starlink/starlink/availability-report/")
    print("2. Selecione algumas Service Lines")
    print("3. Clique no botão 'Baixar PDF'")
    print("4. O download deve iniciar automaticamente")
    print("\n💡 Se não funcionar no Simple Browser do VS Code, teste em:")
    print("   - Chrome, Firefox ou Edge")
    print("   - Funcionalidade JavaScript habilitada")
