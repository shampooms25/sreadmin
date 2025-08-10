"""
Módulo para integração com a API da Starlink
"""

try:
    import requests
except ImportError:
    requests = None
import time
import json
from datetime import datetime, timedelta
import dateutil.parser

# Configurações para API
AUTH_URL = "https://api.starlink.com/auth/connect/token"

# Configuração de múltiplas contas Starlink
STARLINK_ACCOUNTS = {
    "ACC-3697602-31930-14": {
        "name": "Conta Primária",
        "description": "Conta principal de operações"
    },
    "ACC-3697620-11506-11": {
        "name": "Conta Secundária", 
        "description": "Conta secundária regional"
    },
    "ACC-2744134-64041-5": {
        "name": "Conta Principal",
        "description": "Conta principal consolidada"
    },
    "ACC-3697622-49133-20": {
        "name": "Conta Norte",
        "description": "Conta regional norte"
    },
    "ACC-3697611-48655-26": {
        "name": "Conta Sul",
        "description": "Conta regional sul"
    }
}

# Conta padrão (pode ser alterada via interface)
DEFAULT_ACCOUNT = "ACC-2744134-64041-5"


def get_api_url(account_id=None):
    """
    Constrói a URL da API para uma conta específica
    """
    if account_id is None:
        account_id = DEFAULT_ACCOUNT
    
    return f"https://web-api.starlink.com/enterprise/v1/accounts/{account_id}/billing-cycles/query"


def get_account_base_url(account_id=None):
    """
    Constrói a URL base da conta para endpoints específicos
    """
    if account_id is None:
        account_id = DEFAULT_ACCOUNT
    
    return f"https://web-api.starlink.com/enterprise/v1/account/{account_id}"


def get_available_accounts():
    """
    Retorna lista de contas disponíveis
    """
    return STARLINK_ACCOUNTS


def get_account_info(account_id):
    """
    Retorna informações de uma conta específica
    """
    return STARLINK_ACCOUNTS.get(account_id, {
        "name": "Conta Desconhecida",
        "description": "Conta não encontrada"
    })

CLIENT_ID = "498ca080-3eb2-4a4d-a5d9-3828dbef0194"
CLIENT_SECRET = "fibernetworks_api@2025"

token_data = {
    "access_token": None,
    "expires_at": 0
}


def get_token(client_id, client_secret):
    """
    Obtém um novo token de acesso da API Starlink
    """
    if requests is None:
        raise Exception("Módulo requests não disponível")
        
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(AUTH_URL, data=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        expires_in = data.get("expires_in", 0)
        token_data["access_token"] = data.get("access_token")
        token_data["expires_at"] = time.time() + expires_in

        return token_data["access_token"]
    except requests.exceptions.RequestException as e:
        raise Exception(f"Erro ao obter token: {e}")


def get_valid_token():
    """
    Retorna um token válido, renovando se necessário
    """
    if not token_data["access_token"] or time.time() >= token_data["expires_at"]:
        return get_token(CLIENT_ID, CLIENT_SECRET)
    return token_data["access_token"]


def query_service_lines(account_id=None):
    """
    Consulta todos os Service Line Numbers da conta
    """
    payload = {
        "serviceLinesFilter": [],
        "previousBillingCycles": 12,
        "pageIndex": 0,
        "pageLimit": 100
    }

    try:
        token = get_valid_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        api_url = get_api_url(account_id)
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        service_line_numbers = []

        if "content" in data and "results" in data["content"]:
            for result in data["content"]["results"]:
                service_line_number = result.get("serviceLineNumber")
                
                if service_line_number:
                    service_line_numbers.append(service_line_number)
        
        return service_line_numbers

    except requests.exceptions.RequestException as e:
        raise Exception(f"Erro na requisição à API: {e}")
    except Exception as e:
        raise Exception(f"Erro inesperado: {e}")


def get_service_line_details(service_line_number):
    """
    Obtém detalhes específicos de um Service Line
    """
    # Esta função pode ser expandida conforme necessário
    # Por enquanto, retorna informações básicas
    return {
        "service_line_number": service_line_number,
        "status": "Ativo",
        "last_updated": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }


def get_billing_summary(account_id=None):
    """
    Obtém resumo de faturamento com dados detalhados
    """
    if account_id is None:
        account_id = DEFAULT_ACCOUNT
        
    payload = {
        "serviceLinesFilter": [],
        "previousBillingCycles": 12,
        "pageIndex": 0,
        "pageLimit": 100
    }

    try:
        token = get_valid_token()
        if not token:
            return {
                "error": "Não foi possível obter token de acesso",
                "total_service_lines": 0,
                "service_lines": [],
                "last_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "account_id": account_id
            }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        api_url = get_api_url(account_id)
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        service_lines = []
        total_charges = 0
        billing_cycles = []

        if "content" in data and "results" in data["content"]:
            for result in data["content"]["results"]:
                service_line_number = result.get("serviceLineNumber")
                
                if service_line_number:
                    # Extrair dados de faturamento
                    billing_info = {
                        "serviceLineNumber": service_line_number,
                        "billing_cycles": result.get("billingCycles", []),
                        "total_amount": 0,
                        "last_billing_date": None
                    }
                    
                    # Processar ciclos de faturamento
                    for cycle in result.get("billingCycles", []):
                        amount = cycle.get("totalAmount", 0)
                        billing_info["total_amount"] += amount
                        total_charges += amount
                        
                        billing_date = cycle.get("billingDate")
                        if billing_date and (not billing_info["last_billing_date"] or billing_date > billing_info["last_billing_date"]):
                            billing_info["last_billing_date"] = billing_date
                        
                        # Verificar se há dataBlocks no ciclo de faturamento
                        if "dataBlocks" in cycle:
                            print("=" * 80)
                            print(f"📊 DATABLOCKS ENCONTRADOS no billing para Service Line: {service_line_number}")
                            print(f"Account: {account_id}")
                            print("=" * 80)
                            print(json.dumps(cycle["dataBlocks"], indent=2, ensure_ascii=False))
                            print("=" * 80)
                    
                    service_lines.append(billing_info)

        return {
            "success": True,
            "total_service_lines": len(service_lines),
            "service_lines": service_lines,
            "total_charges": total_charges,
            "billing_cycles_analyzed": 12,
            "last_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "account_id": account_id,
            "raw_data": data
        }

    except requests.exceptions.RequestException as e:
        return {
            "error": f"Erro na requisição à API: {e}",
            "total_service_lines": 0,
            "service_lines": [],
            "total_charges": 0,
            "last_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "account_id": account_id
        }
    except Exception as e:
        return {
            "error": f"Erro inesperado: {e}",
            "total_service_lines": 0,
            "service_lines": [],
            "total_charges": 0,
            "last_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "account_id": account_id
        }


def test_api_connection(account_id=None):
    """
    Testa a conexão com a API Starlink
    """
    if account_id is None:
        account_id = DEFAULT_ACCOUNT
        
    try:
        # Primeiro, testa a autenticação
        token = get_valid_token()
        if not token:
            return {
                "status": "error",
                "message": "Falha na autenticação",
                "details": "Não foi possível obter token de acesso",
                "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }

        # Testa uma requisição simples à API
        payload = {
            "serviceLinesFilter": [],
            "previousBillingCycles": 1,
            "pageIndex": 0,
            "pageLimit": 1
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        api_url = get_api_url(account_id)
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        
        # Se chegou até aqui, a conexão está OK
        expires_at = datetime.fromtimestamp(token_data['expires_at']).strftime('%d/%m/%Y %H:%M:%S')
        
        return {
            "status": "success",
            "message": "Conexão com API Starlink estabelecida com sucesso",
            "details": f"Token válido até: {expires_at}",
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "account_id": account_id
        }

    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": "Falha na comunicação com a API",
            "details": str(e),
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Erro inesperado na verificação da API",
            "details": str(e),
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }


def get_detailed_service_lines(account_id=None):
    """
    Obtém lista detalhada de Service Lines com informações completas de localização
    """
    if account_id is None:
        account_id = DEFAULT_ACCOUNT
        
    payload = {
        "serviceLinesFilter": [],
        "previousBillingCycles": 12,
        "pageIndex": 0,
        "pageLimit": 100
    }

    try:
        token = get_valid_token()
        if not token:
            return {"error": "Não foi possível obter token de acesso"}

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Primeiro, obter dados dos endereços
        addresses_result = get_starlink_addresses(account_id)
        addresses_dict = {}
        if addresses_result.get("success"):
            addresses_dict = addresses_result.get("addresses", {})

        api_url = get_api_url(account_id)
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        service_lines = []
        if "content" in data and "results" in data["content"]:
            for i, result in enumerate(data["content"]["results"], 1):
                service_line_number = result.get("serviceLineNumber")
                
                if service_line_number:
                    # Extrair informações de localização dos dados da API
                    location_info = "Localização não informada"
                    
                    # Primeiro tentar usar os dados de endereços se houver addressReferenceId
                    address_ref_id = None
                    if "addressReferenceId" in result:
                        address_ref_id = result["addressReferenceId"]
                    elif "serviceLocation" in result and isinstance(result["serviceLocation"], dict):
                        address_ref_id = result["serviceLocation"].get("addressReferenceId")
                    
                    if address_ref_id and address_ref_id in addresses_dict:
                        addr = addresses_dict[address_ref_id]
                        location_parts = []
                        if addr["locality"]:
                            location_parts.append(addr["locality"])
                        if addr["state"]:
                            location_parts.append(addr["state"])
                        if addr["country"]:
                            location_parts.append(addr["country"])
                        
                        if location_parts:
                            location_info = ", ".join(location_parts)
                        elif addr["formatted"]:
                            # Usar endereço formatado como fallback
                            location_info = addr["formatted"][:50] + "..." if len(addr["formatted"]) > 50 else addr["formatted"]
                    
                    # Fallback: tentar extrair de outros campos se não encontrou nos endereços
                    if location_info == "Localização não informada":
                        if "nickname" in result and result["nickname"]:
                            location_info = result["nickname"]
                        elif "serviceAddress" in result and result["serviceAddress"]:
                            location_info = str(result["serviceAddress"])
                        elif "latitude" in result and "longitude" in result:
                            location_info = f"GPS: {result['latitude']}, {result['longitude']}"
                    
                    service_lines.append({
                        "index": i,
                        "serviceLineNumber": service_line_number,
                        "status": "Ativo",  # Pode ser expandido com dados reais
                        "serviceLocation": location_info,
                        "lastUpdate": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "billingCycles": len(result.get("billingCycles", [])),
                        "addressReferenceId": address_ref_id,
                        "rawData": result  # Para debuging ou relatórios detalhados
                    })

        return {
            "success": True,
            "service_lines": service_lines,
            "total": len(service_lines),
            "addresses_loaded": len(addresses_dict),
            "account_id": account_id,
            "last_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Erro na requisição à API: {e}"}
    except Exception as e:
        return {"error": f"Erro inesperado: {e}"}


def debug_api_response(account_id=None):
    """
    Função para debug - mostra no console o resultado completo da API
    """
    if account_id is None:
        account_id = DEFAULT_ACCOUNT
        
    payload = {
        "serviceLinesFilter": [],
        "previousBillingCycles": 12,
        "pageIndex": 0,
        "pageLimit": 5  # Limitar para debug
    }

    try:
        token = get_valid_token()
        if not token:
            print("❌ Não foi possível obter token de acesso")
            return

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        print(f"🔍 Fazendo requisição à API Starlink - Conta: {account_id}...")
        api_url = get_api_url(account_id)
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        print("\n" + "="*80)
        print("📋 RESULTADO COMPLETO DA API STARLINK")
        print("="*80)
        
        # Mostrar estrutura geral
        print(f"📊 Estrutura principal: {list(data.keys())}")
        
        if "content" in data:
            print(f"📦 Conteúdo disponível: {list(data['content'].keys())}")
            
            if "results" in data["content"]:
                results = data["content"]["results"]
                print(f"📈 Total de resultados: {len(results)}")
                
                # Mostrar detalhes de cada resultado
                for i, result in enumerate(results[:3]):  # Mostrar apenas os 3 primeiros
                    print(f"\n🔸 RESULTADO {i+1}:")
                    print(f"   📋 Campos disponíveis: {list(result.keys())}")
                    
                    # Mostrar campos específicos
                    for key, value in result.items():
                        if isinstance(value, dict):
                            print(f"   📁 {key}: {list(value.keys())} (dict)")
                        elif isinstance(value, list):
                            print(f"   📝 {key}: {len(value)} itens (list)")
                        else:
                            print(f"   ✏️  {key}: {str(value)[:100]}...")
                    
                    # Procurar campos que podem conter localização
                    location_fields = [
                        'serviceLocation', 'location', 'address', 'site', 
                        'serviceAddress', 'installationAddress', 'billingAddress',
                        'coordinates', 'geoLocation', 'region', 'country', 
                        'city', 'state', 'zipCode', 'postalCode'
                    ]
                    
                    print(f"\n   🗺️  CAMPOS DE LOCALIZAÇÃO ENCONTRADOS:")
                    for field in location_fields:
                        if field in result:
                            print(f"   ✅ {field}: {result[field]}")
                    
                    print("-" * 60)
        
        print("\n" + "="*80)
        print("📋 DADOS BRUTOS COMPLETOS (JSON)")
        print("="*80)
        import json
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Erro no debug: {e}")


def debug_addresses_endpoint(account_id=None):
    """
    Testa o endpoint específico de addresses fornecido pelo usuário
    """
    if account_id is None:
        account_id = DEFAULT_ACCOUNT
        
    addresses_url = f"https://web-api.starlink.com/enterprise/v1/account/{account_id}/addresses"
    
    try:
        token = get_valid_token()
        if not token:
            return {"error": "Não foi possível obter token de acesso"}

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        print(f"\n🔍 TESTANDO ENDPOINT ADDRESSES:")
        print(f"URL: {addresses_url}")
        print(f"Headers: {headers}")
        print("-" * 80)

        response = requests.get(addresses_url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCESSO! Dados retornados:")
            print(f"Tipo de resposta: {type(data)}")
            print(f"Conteúdo completo:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return {"success": True, "data": data}
        else:
            print(f"\n❌ ERRO HTTP {response.status_code}")
            print(f"Resposta: {response.text}")
            return {"error": f"HTTP {response.status_code}: {response.text}"}

    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERRO DE REQUISIÇÃO: {e}")
        return {"error": f"Erro na requisição à API: {e}"}
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        return {"error": f"Erro inesperado: {e}"}


def debug_multiple_endpoints(account_id=None):
    """
    Testa múltiplos endpoints baseados no padrão da API
    """
    if account_id is None:
        account_id = DEFAULT_ACCOUNT
        
    base_url = f"https://web-api.starlink.com/enterprise/v1/accounts/{account_id}"
    
    endpoints_to_test = [
        "addresses",
        "service-lines",
        "terminals",
        "locations",
        "sites",
        "subscriptions"
    ]
    
    results = {}
    
    for endpoint in endpoints_to_test:
        url = f"{base_url}/{endpoint}"
        print(f"\n{'='*60}")
        print(f"🔍 Testando endpoint: {endpoint}")
        print(f"📍 URL: {url}")
        print(f"{'='*60}")
        
        try:
            token = get_valid_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sucesso!")
                print(f"📄 Tipo: {type(data)}")
                
                if isinstance(data, dict):
                    print(f"📋 Chaves: {list(data.keys())}")
                elif isinstance(data, list):
                    print(f"📋 Lista com {len(data)} items")
                
                results[endpoint] = {"success": True, "data": data}
                print(f"📄 DADOS:")
                print(data)
                
            else:
                print(f"❌ Erro {response.status_code}: {response.text}")
                results[endpoint] = {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            results[endpoint] = {"success": False, "error": str(e)}
    
    return results


def get_starlink_addresses(account_id=None):
    """
    Obtém todos os endereços cadastrados na conta Starlink
    """
    if account_id is None:
        account_id = DEFAULT_ACCOUNT
        
    addresses_url = f"{get_account_base_url(account_id)}/addresses"
    
    try:
        token = get_valid_token()
        if not token:
            return {"error": "Não foi possível obter token de acesso"}

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.get(addresses_url, headers=headers)
        response.raise_for_status()
        
        if response.status_code == 200:
            data = response.json()
            addresses = data.get("content", {}).get("results", [])
            
            # Processar endereços para facilitar o uso
            processed_addresses = {}
            for addr in addresses:
                addr_id = addr.get("addressReferenceId")
                if addr_id:
                    processed_addresses[addr_id] = {
                        "id": addr_id,
                        "locality": addr.get("locality", ""),
                        "state": addr.get("administrativeAreaCode", ""),
                        "country": addr.get("regionCode", ""),
                        "formatted": addr.get("formattedAddress", ""),
                        "coordinates": f"{addr.get('latitude', '')}, {addr.get('longitude', '')}" if addr.get('latitude') and addr.get('longitude') else "",
                        "postal_code": addr.get("postalCode", "")
                    }
            
            return {
                "success": True,
                "addresses": processed_addresses,
                "total": len(processed_addresses)
            }
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}

    except requests.exceptions.RequestException as e:
        return {"error": f"Erro na requisição à API: {e}"}
    except Exception as e:
        return {"error": f"Erro inesperado: {e}"}


def get_service_lines_with_location(account_id=None):
    """
    Obtém Service Lines com localização correta usando o endpoint /service-lines
    """
    if account_id is None:
        account_id = DEFAULT_ACCOUNT
        
    try:
        token = get_valid_token()
        if not token:
            return {"error": "Não foi possível obter token de acesso"}

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Primeiro, obter dados dos endereços
        addresses_result = get_starlink_addresses(account_id)
        addresses_dict = {}
        if addresses_result.get("success"):
            addresses_dict = addresses_result.get("addresses", {})

        # Usar o endpoint correto para Service Lines com limit maior
        service_lines_url = f"{get_account_base_url(account_id)}/service-lines?limit=100"
        
        response = requests.get(service_lines_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        service_lines = []
        correlations_found = 0
        
        if "content" in data and "results" in data["content"]:
            for i, result in enumerate(data["content"]["results"], 1):
                service_line_number = result.get("serviceLineNumber", f"SL-UNKNOWN-{i}")
                
                # Sempre processar todos os Service Lines, mesmo sem serviceLineNumber
                # Extrair informações de localização
                location_info = "Localização não informada"
                address_ref_id = result.get("addressReferenceId")
                
                # Tentar correlacionar com endereços
                if address_ref_id and address_ref_id in addresses_dict:
                    addr = addresses_dict[address_ref_id]
                    location_parts = []
                    if addr["locality"]:
                        location_parts.append(addr["locality"])
                    if addr["state"]:
                        location_parts.append(addr["state"])
                    if addr["country"]:
                        location_parts.append(addr["country"])
                    
                    if location_parts:
                        location_info = ", ".join(location_parts)
                        correlations_found += 1
                    elif addr["formatted"]:
                        # Usar endereço formatado como fallback
                        location_info = addr["formatted"][:50] + "..." if len(addr["formatted"]) > 50 else addr["formatted"]
                        correlations_found += 1
                
                # Fallback: tentar extrair de outros campos se não encontrou nos endereços
                if location_info == "Localização não informada":
                    if "nickname" in result and result["nickname"]:
                        location_info = result["nickname"]
                
                # Determinar status detalhado
                detailed_status = "Ativo"
                status_class = "active"
                
                if not result.get("active", True):
                    detailed_status = "Offline"
                    status_class = "offline"
                else:
                    # Verificar se há dados recentes (últimos 30 dias)
                    import dateutil.parser
                    
                    try:
                        end_date = result.get("endDate")
                        if end_date:
                            end_datetime = dateutil.parser.parse(end_date)
                            thirty_days_ago = datetime.now(end_datetime.tzinfo) - timedelta(days=30)
                            
                            if end_datetime < thirty_days_ago:
                                detailed_status = "Sem Dados"
                                status_class = "no_data"
                    except:
                        pass  # Se não conseguir processar a data, mantém como ativo
                
                service_lines.append({
                    "index": i,
                    "serviceLineNumber": service_line_number,
                    "nickname": result.get("nickname", ""),
                    "status": detailed_status,
                    "statusClass": status_class,
                    "serviceLocation": location_info,
                    "lastUpdate": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "addressReferenceId": address_ref_id,
                    "startDate": result.get("startDate", ""),
                    "endDate": result.get("endDate", ""),
                    "publicIp": result.get("publicIp", ""),
                    "hasAddress": bool(address_ref_id and address_ref_id in addresses_dict),
                    "rawData": result  # Para debug
                })

        # Calcular estatísticas detalhadas
        total_service_lines = len(service_lines)
        with_address = len([sl for sl in service_lines if sl["hasAddress"]])
        without_address = total_service_lines - with_address
        with_nickname = len([sl for sl in service_lines if sl["nickname"]])
        
        # Contar por status detalhado - incluindo TODOS os status possíveis
        active_lines = len([sl for sl in service_lines if sl["status"] == "Ativo"])
        offline_lines = len([sl for sl in service_lines if sl["status"] == "Offline"])
        no_data_lines = len([sl for sl in service_lines if sl["status"] == "Sem Dados"])
        pending_lines = len([sl for sl in service_lines if sl["status"] == "Pendente"])
        suspended_lines = len([sl for sl in service_lines if sl["status"] == "Suspenso"])
        indeterminate_lines = len([sl for sl in service_lines if sl["status"] == "Indeterminado"])
        
        # Verificar se há discrepância na contagem
        total_counted = active_lines + offline_lines + no_data_lines + pending_lines + suspended_lines + indeterminate_lines
        discrepancy = total_service_lines - total_counted
        
        return {
            "success": True,
            "service_lines": service_lines,
            "total": total_service_lines,
            "addresses_loaded": len(addresses_dict),
            "correlations_found": correlations_found,
            "statistics": {
                "total_service_lines": total_service_lines,
                "with_address": with_address,
                "without_address": without_address,
                "with_nickname": with_nickname,
                "active_lines": active_lines,
                "offline_lines": offline_lines,
                "no_data_lines": no_data_lines,
                "pending_lines": pending_lines,
                "suspended_lines": suspended_lines,
                "indeterminate_lines": indeterminate_lines,
                "total_counted": total_counted
            },
            "account_id": account_id,
            "last_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Erro na requisição à API: {e}"}
    except Exception as e:
        return {"error": f"Erro inesperado: {e}"}


def get_usage_report_data(account_id=None, cycle_start=None, cycle_end=None):
    """
    Obtém dados de consumo de franquia para relatório usando dados reais da API
    """
    if account_id is None:
        account_id = DEFAULT_ACCOUNT
        
    try:
        from datetime import datetime, date
        print(f"🚀 Obtendo dados de uso REAIS para conta: {account_id}")
        if cycle_start and cycle_end:
            print(f"📅 Ciclo: {cycle_start} até {cycle_end}")
        start_time = time.time()
        
        # Primeiro, obter todos os service lines com localização
        service_lines_result = get_service_lines_with_location(account_id)
        
        if "error" in service_lines_result:
            return service_lines_result
        
        service_lines = service_lines_result.get("service_lines", [])
        total_count = len(service_lines)
        
        print(f"📋 {total_count} Service Lines encontrados")
        
        # Obter dados reais de billing para cada service line
        usage_data = []
        statistics = {
            "total_lines": total_count,
            "lines_under_70": 0,
            "lines_70_plus": 0,
            "lines_80_plus": 0,
            "lines_90_plus": 0,
            "lines_100_plus": 0,
            "total_priority_gb": 0,
            "total_standard_gb": 0,
            "total_consumption_gb": 0
        }
        
        # Consultar dados de billing reais
        token = get_valid_token()
        if not token:
            print("❌ Token não disponível, retornando erro")
            return {
                "error": "Token de autenticação não disponível",
                "usage_data": [],
                "statistics": {},
                "total_lines": 0,
                "account_id": account_id,
                "last_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Preparar lista de service lines para consulta
        service_line_numbers = [sl.get("serviceLineNumber") for sl in service_lines if sl.get("serviceLineNumber")]
        
        if not service_line_numbers:
            print("❌ Nenhuma service line encontrada")
            return {
                "error": "Nenhuma service line encontrada",
                "usage_data": [],
                "statistics": {},
                "total_lines": 0
            }
        
        # Consultar billing cycles
        url = f"https://web-api.starlink.com/enterprise/v1/accounts/{account_id}/billing-cycles/query"
        payload = {
            "serviceLinesFilter": service_line_numbers,
            "previousBillingCycles": 2,  # Últimos 2 ciclos para garantir que temos o atual
            "pageIndex": 0,
            "pageLimit": 100
        }
        
        print(f"🔍 Consultando billing cycles para {len(service_line_numbers)} service lines...")
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Erro na consulta de billing: {response.status_code}")
            return {
                "error": f"Erro na consulta de billing: {response.status_code}",
                "usage_data": [],
                "statistics": {},
                "total_lines": 0
            }
        
        billing_data = response.json()
        
        # Processar dados de cada service line
        for service_line in service_lines:
            service_line_number = service_line.get("serviceLineNumber", "")
            location = service_line.get("serviceLocation", "N/A")
            
            if not service_line_number:
                continue
            
            # Encontrar dados de billing para esta service line
            billing_result = None
            if "content" in billing_data and "results" in billing_data["content"]:
                for result in billing_data["content"]["results"]:
                    if result.get("serviceLineNumber") == service_line_number:
                        billing_result = result
                        break
            
            if not billing_result:
                print(f"⚠️  Dados de billing não encontrados para {service_line_number}")
                continue
            
            # Encontrar o ciclo atual nos dados de billing
            current_cycle_data = None
            billing_cycles = billing_result.get("billingCycles", [])
            
            # Converter cycle_start e cycle_end para formato da API se fornecidos
            if cycle_start and cycle_end:
                # Converter de DD/MM/YYYY para YYYY-MM-DD
                cycle_start_api = datetime.strptime(cycle_start, "%d/%m/%Y").strftime("%Y-%m-%d")
                cycle_end_api = datetime.strptime(cycle_end, "%d/%m/%Y").strftime("%Y-%m-%d")
                
                print(f"🔍 Procurando ciclo que contenha: {cycle_start_api} até {cycle_end_api}")
                
                # Procurar pelo ciclo que contenha o período atual
                for cycle in billing_cycles:
                    start_date = cycle.get("startDate", "")[:10]  # Só a data, sem hora
                    end_date = cycle.get("endDate", "")[:10]
                    
                    # Verificar se o ciclo atual está dentro do período do billing cycle
                    if start_date <= cycle_start_api and end_date >= cycle_end_api:
                        current_cycle_data = cycle
                        print(f"✅ Ciclo encontrado: {start_date} até {end_date}")
                        break
            
            # Se não encontrou com filtro de data, pegar o mais recente
            if not current_cycle_data and billing_cycles:
                current_cycle_data = billing_cycles[0]
                print(f"⚠️  Usando ciclo mais recente disponível")
            
            if not current_cycle_data:
                print(f"⚠️  Ciclo atual não encontrado para {service_line_number}")
                continue
            
            # Calcular consumo real baseado em dailyDataUsage
            daily_usage = current_cycle_data.get("dailyDataUsage", [])
            
            # Filtrar apenas os dias do ciclo atual se cycle_start e cycle_end foram fornecidos
            if cycle_start and cycle_end and daily_usage:
                cycle_start_api = datetime.strptime(cycle_start, "%d/%m/%Y").strftime("%Y-%m-%d")
                cycle_end_api = datetime.strptime(cycle_end, "%d/%m/%Y").strftime("%Y-%m-%d")
                
                filtered_usage = []
                for day in daily_usage:
                    day_date = day.get("date", "")[:10]  # Só a data, sem hora
                    if cycle_start_api <= day_date <= cycle_end_api:
                        filtered_usage.append(day)
                
                daily_usage = filtered_usage
                print(f"📊 Filtrados {len(daily_usage)} dias do período {cycle_start} até {cycle_end}")
            
            priority_gb = 0
            standard_gb = 0
            
            for day in daily_usage:
                priority_gb += day.get("priorityGB", 0)
                standard_gb += day.get("standardGB", 0)
            
            total_gb = priority_gb + standard_gb
            total_tb = round(total_gb / 1024, 2)
            
            # Assumir franquia de 1TB como padrão
            quota_gb = 1024
            usage_percentage = round((total_gb / quota_gb) * 100, 1) if quota_gb > 0 else 0
            
            # Determinar threshold baseado na porcentagem
            if usage_percentage < 70:
                threshold = "normal"
                statistics["lines_under_70"] += 1
            elif usage_percentage < 80:
                threshold = "caution"
            elif usage_percentage < 90:
                threshold = "warning"
            elif usage_percentage < 100:
                threshold = "danger"
            else:
                threshold = "critical"
            
            # Atualizar estatísticas cumulativas
            if usage_percentage >= 70:
                statistics["lines_70_plus"] += 1
            if usage_percentage >= 80:
                statistics["lines_80_plus"] += 1
            if usage_percentage >= 90:
                statistics["lines_90_plus"] += 1
            if usage_percentage >= 100:
                statistics["lines_100_plus"] += 1
            
            # Atualizar estatísticas totais
            statistics["total_priority_gb"] += priority_gb
            statistics["total_standard_gb"] += standard_gb
            statistics["total_consumption_gb"] += total_gb
            
            usage_data.append({
                "serviceLineNumber": service_line_number,
                "location": location,
                "priorityGB": round(priority_gb, 2),
                "standardGB": round(standard_gb, 2),
                "totalGB": round(total_gb, 2),
                "totalTB": total_tb,
                "usagePercentage": usage_percentage,
                "threshold": threshold,
                "quotaGB": quota_gb,
                "nickname": service_line.get("nickname", ""),
                "status": service_line.get("status", "Ativo"),
                "days_analyzed": len(daily_usage),
                "data_source": "real_api"
            })
            
            print(f"✅ {service_line_number}: {total_gb:.2f} GB ({len(daily_usage)} dias)")
        
        # Ordenar por maior consumo
        usage_data.sort(key=lambda x: x["totalGB"], reverse=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"✅ Relatório de uso gerado com dados REAIS em {total_time:.2f} segundos")
        
        return {
            "success": True,
            "usage_data": usage_data,
            "statistics": statistics,
            "total_lines": len(usage_data),
            "account_id": account_id,
            "cycle_start": cycle_start,
            "cycle_end": cycle_end,
            "data_source": "real_api",
            "performance_stats": {
                "total_time": total_time,
                "lines_processed": len(usage_data)
            },
            "last_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório de uso: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "error": f"Erro ao consultar dados de uso: {str(e)}",
            "usage_data": [],
            "statistics": {},
            "total_lines": 0,
            "account_id": account_id,
            "last_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }




def check_auto_recharge_status_fast(account_id, service_line_number):
    """
    Versão otimizada para verificar status de recarga automática
    Com timeout reduzido e menos logs verbosos
    """
    try:
        token = get_valid_token()
        if not token:
            return {
                "active": False,
                "error": "Token inválido",
                "data": None
            }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # URL para verificar o status de opt-in (recarga automática)
        url = f"https://web-api.starlink.com/enterprise/v1/account/{account_id}/service-lines/{service_line_number}/opt-in"
        
        # Requisição com timeout reduzido - usando POST como na função original
        response = requests.post(url, headers=headers, json={}, timeout=10)  # Timeout de 10s em vez do padrão
        
        if response.status_code == 200:
            data = response.json()
            # Se retornou 200, significa que a recarga automática está ativa
            return {
                "active": True,
                "error": None,
                "data": data
            }
        elif response.status_code == 404:
            # Se retornou 404, significa que a recarga automática não está ativa
            return {
                "active": False,
                "error": None,
                "data": None
            }
        else:
            return {
                "active": False,
                "error": f"Status HTTP {response.status_code}",
                "data": None
            }

    except requests.exceptions.Timeout:
        return {
            "active": False,
            "error": "Timeout na verificação",
            "data": None
        }
    except requests.exceptions.RequestException as e:
        return {
            "active": False,
            "error": f"Erro de requisição: {str(e)[:30]}...",
            "data": None
        }
    except Exception as e:
        return {
            "active": False,
            "error": f"Erro inesperado: {str(e)[:30]}...",
            "data": None
        }


# Cache simples para resultados de recarga automática
_auto_recharge_cache = {}
_cache_expiry = {}

def clear_auto_recharge_cache(account_id=None):
    """
    Limpa o cache de recarga automática
    Se account_id for fornecido, limpa apenas para essa conta
    """
    if account_id:
        keys_to_remove = [key for key in _auto_recharge_cache.keys() if key.startswith(f"{account_id}_")]
        for key in keys_to_remove:
            if key in _auto_recharge_cache:
                del _auto_recharge_cache[key]
            if key in _cache_expiry:
                del _cache_expiry[key]
        print(f"🗑️ Cache limpo para conta {account_id}")
    else:
        _auto_recharge_cache.clear()
        _cache_expiry.clear()
        print("🗑️ Cache completo limpo")


def get_service_lines_with_auto_recharge_status(account_id=None):
    """
    Obtém Service Lines com localização e status de recarga automática
    Versão otimizada com cache para melhor performance
    """
    if account_id is None:
        account_id = DEFAULT_ACCOUNT
        
    try:
        print(f"🚀 Iniciando consulta otimizada para conta: {account_id}")
        start_time = time.time()
        
        # Primeiro, obter todos os service lines com localização
        service_lines_result = get_service_lines_with_location(account_id)
        
        if "error" in service_lines_result:
            return service_lines_result
        
        service_lines = service_lines_result.get("service_lines", [])
        total_count = len(service_lines)
        
        print(f"📋 {total_count} Service Lines encontrados")
        
        # Adicionar status de recarga automática a cada service line
        processed_lines = []
        cache_hits = 0
        api_calls = 0
        
        for i, service_line in enumerate(service_lines, 1):
            service_line_number = service_line.get("serviceLineNumber", "")
            
            if not service_line_number:
                # Se não tem número, não pode verificar recarga automática
                service_line["auto_recharge_status"] = {
                    "active": False,
                    "error": "Número da Service Line não disponível",
                    "last_check": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }
                processed_lines.append(service_line)
                continue
            
            print(f"🔍 [{i}/{total_count}] Verificando recarga automática para {service_line_number}")
            
            # Usar cache para verificar status
            cache_key = f"{account_id}_{service_line_number}"
            current_time = time.time()
            
            if (cache_key in _auto_recharge_cache and 
                cache_key in _cache_expiry and 
                current_time < _cache_expiry[cache_key]):
                
                # Cache hit
                auto_recharge_status = _auto_recharge_cache[cache_key]
                cache_hits += 1
                print(f"📦 Cache hit para {service_line_number}")
            else:
                # Cache miss - fazer chamada à API
                auto_recharge_status = check_auto_recharge_status_fast(account_id, service_line_number)
                api_calls += 1
                
                # Armazenar no cache por 5 minutos
                _auto_recharge_cache[cache_key] = auto_recharge_status
                _cache_expiry[cache_key] = current_time + 300  # 5 minutos
                
                print(f"🔍 API call para {service_line_number}")
                
                # Pausa mínima entre chamadas para não sobrecarregar a API
                time.sleep(0.05)  # 50ms entre chamadas
            
            # Adicionar status ao service line
            service_line["auto_recharge_status"] = auto_recharge_status
            processed_lines.append(service_line)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"✅ Consulta finalizada em {total_time:.2f} segundos")
        print(f"📊 Cache hits: {cache_hits}, API calls: {api_calls}")
        
        return {
            "success": True,
            "service_lines": processed_lines,
            "total_count": total_count,
            "account_id": account_id,
            "performance_stats": {
                "total_time": total_time,
                "cache_hits": cache_hits,
                "api_calls": api_calls,
                "lines_processed": len(processed_lines)
            },
            "last_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        
    except Exception as e:
        print(f"❌ Erro na consulta: {str(e)}")
        return {
            "error": f"Erro ao consultar service lines: {str(e)}",
            "service_lines": [],
            "total_count": 0
        }


def get_service_lines_with_auto_recharge_status_parallel(account_id=None, max_workers=5):
    """
    Versão paralela da função de consulta de recarga automática
    Usa ThreadPoolExecutor para fazer múltiplas consultas simultaneamente
    """
    if account_id is None:
        account_id = DEFAULT_ACCOUNT
        
    try:
        import concurrent.futures
        
        print(f"🚀 Iniciando consulta paralela para conta: {account_id}")
        start_time = time.time()
        
        # Primeiro, obter todos os service lines com localização
        service_lines_result = get_service_lines_with_location(account_id)
        
        if "error" in service_lines_result:
            return service_lines_result
        
        service_lines = service_lines_result.get("service_lines", [])
        total_count = len(service_lines)
        
        print(f"📋 {total_count} Service Lines encontrados")
        
        # Separar linhas que precisam de verificação de recarga
        lines_to_check = []
        lines_ready = []
        
        for service_line in service_lines:
            service_line_number = service_line.get("serviceLineNumber", "")
            
            if not service_line_number:
                # Se não tem número, não pode verificar recarga automática
                service_line["auto_recharge_status"] = {
                    "active": False,
                    "error": "Número da Service Line não disponível",
                    "last_check": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }
                lines_ready.append(service_line)
            else:
                # Verificar cache primeiro
                cache_key = f"{account_id}_{service_line_number}"
                current_time = time.time()
                
                if (cache_key in _auto_recharge_cache and 
                    cache_key in _cache_expiry and 
                    current_time < _cache_expiry[cache_key]):
                    
                    # Cache hit
                    service_line["auto_recharge_status"] = _auto_recharge_cache[cache_key]
                    lines_ready.append(service_line)
                    print(f"📦 Cache hit para {service_line_number}")
                else:
                    # Precisa fazer chamada à API
                    lines_to_check.append(service_line)
        
        print(f"📊 Cache hits: {len(lines_ready)}, API calls necessárias: {len(lines_to_check)}")
        
        # Função para processar uma linha
        def process_line(service_line):
            service_line_number = service_line.get("serviceLineNumber", "")
            print(f"🔍 Processando {service_line_number}")
            
            auto_recharge_status = check_auto_recharge_status_fast(account_id, service_line_number)
            
            # Armazenar no cache
            cache_key = f"{account_id}_{service_line_number}"
            _auto_recharge_cache[cache_key] = auto_recharge_status
            _cache_expiry[cache_key] = time.time() + 300  # 5 minutos
            
            service_line["auto_recharge_status"] = auto_recharge_status
            return service_line
        
        # Processar em paralelo apenas as linhas que precisam de verificação
        if lines_to_check:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submeter todas as tarefas
                future_to_line = {executor.submit(process_line, line): line for line in lines_to_check}
                
                # Coletar resultados
                for future in concurrent.futures.as_completed(future_to_line):
                    try:
                        result = future.result()
                        lines_ready.append(result)
                    except Exception as exc:
                        line = future_to_line[future]
                        service_line_number = line.get("serviceLineNumber", "UNKNOWN")
                        print(f"❌ Erro ao processar {service_line_number}: {exc}")
                        
                        # Adicionar linha com erro
                        line["auto_recharge_status"] = {
                            "active": False,
                            "error": str(exc),
                            "last_check": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        }
                        lines_ready.append(line)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"✅ Consulta paralela finalizada em {total_time:.2f} segundos")
        print(f"📊 Total processado: {len(lines_ready)}")
        
        return {
            "success": True,
            "service_lines": lines_ready,
            "total_count": len(lines_ready),
            "account_id": account_id,
            "performance_stats": {
                "total_time": total_time,
                "cache_hits": len(lines_ready) - len(lines_to_check),
                "api_calls": len(lines_to_check),
                "lines_processed": len(lines_ready),
                "parallel_workers": max_workers
            },
            "last_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        
    except Exception as e:
        print(f"❌ Erro na consulta paralela: {str(e)}")
        return {
            "error": f"Erro ao consultar service lines: {str(e)}",
            "service_lines": [],
            "total_count": 0
        }


def disable_auto_recharge(account_id, service_line_number):
    """
    Desativa a recarga automática para uma service line específica
    usando o endpoint /opt-out
    """
    try:
        token = get_valid_token()
        if not token:
            return {"error": "Falha na autenticação"}
        
        # Endpoint para desativar recarga automática
        url = f"https://web-api.starlink.com/enterprise/v1/account/{account_id}/service-lines/{service_line_number}/opt-out"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print(f"🔄 Desativando recarga automática para Service Line: {service_line_number}")
        print(f"🌐 URL: {url}")
        
        response = requests.delete(url, headers=headers)
        
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 204:
            print(f"✅ Recarga automática DESATIVADA para {service_line_number}")
            return {
                "success": True,
                "message": f"Recarga automática desativada para {service_line_number}",
                "service_line": service_line_number
            }
        else:
            print(f"⚠️  Erro ao desativar {service_line_number}: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return {
                "error": f"Erro {response.status_code}: {response.text}",
                "service_line": service_line_number
            }
            
    except Exception as e:
        print(f"❌ Erro ao desativar recarga automática para {service_line_number}: {e}")
        return {"error": str(e), "service_line": service_line_number}