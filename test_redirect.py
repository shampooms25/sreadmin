#!/usr/bin/env python3
"""
Teste do redirecionamento da URL raiz
"""

import requests

def test_redirect():
    """Testa se o redirecionamento da raiz funciona"""
    print("🌐 TESTANDO REDIRECIONAMENTO DA URL RAIZ...")
    print("=" * 50)
    
    try:
        # Testar URL raiz
        url = "http://localhost:8000/"
        print(f"📋 Testando: {url}")
        
        response = requests.get(url, allow_redirects=False, timeout=10)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code in [301, 302]:
            # Redirecionamento encontrado
            redirect_url = response.headers.get('Location', '')
            print(f"🔄 Redirecionando para: {redirect_url}")
            
            if '/admin/' in redirect_url:
                print("✅ SUCESSO: Redirecionamento para admin configurado corretamente!")
                
                # Testar o redirecionamento completo
                print("\n🔍 Testando redirecionamento completo...")
                final_response = requests.get(url, allow_redirects=True, timeout=10)
                print(f"📊 Status final: {final_response.status_code}")
                print(f"🌐 URL final: {final_response.url}")
                
                if 'login' in final_response.url:
                    print("✅ PERFEITO: Redirecionado para página de login!")
                    return True
                else:
                    print("⚠️  Redirecionado para admin, mas não para login")
                    return True
            else:
                print(f"❌ ERRO: Redirecionamento incorreto para: {redirect_url}")
                return False
        elif response.status_code == 200:
            print("⚠️  URL raiz retorna 200 sem redirecionamento")
            print("🔧 Verifique se a configuração foi aplicada corretamente")
            return False
        else:
            print(f"❌ Status inesperado: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar ao servidor")
        print("🔧 Certifique-se de que o servidor está rodando em localhost:8000")
        return False
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

if __name__ == "__main__":
    success = test_redirect()
    print(f"\n🎯 Resultado: {'✅ SUCESSO' if success else '❌ FALHA'}")
