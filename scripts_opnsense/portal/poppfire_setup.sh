#!/bin/sh

# =============================================================================
# POPPFIRE Portal Setup Script
# =============================================================================

# =============================================================================
# FUNÇÃO: Garantir permissões do próprio script
# =============================================================================
ensure_self_executable() {
    SCRIPT_PATH=$(readlink -f "$0" 2>/dev/null || echo "$0")
    if [ -f "$SCRIPT_PATH" ]; then
        chmod +x "$SCRIPT_PATH" 2>/dev/null || true
    fi
}

# --- VARIÁVEIS DE CONFIGURAÇÃO ---
GITHUB_USER="shampooms25"
GITHUB_REPO="poppfire"
# PAT: aceita via env (setenv PAT xxx) ou argumento --pat
PAT="${PAT:-${POPPFIRE_PAT:-}}"
PORTAL_DIR="/root/portal"
VENV_DIR="$PORTAL_DIR/venv"
ACTIONS_DIR="/usr/local/opnsense/service/conf/actions.d"
ACTIONS_FILE="$ACTIONS_DIR/actions_atualiza_portal.conf"
MAIN_SCRIPT="install_opnsense_updater.py"
GUARD_SCRIPT="poppfire_portal_guard.sh"
GUARD_RC_SCRIPT="rc.d/poppfire_guard"
GUARD_URL="https://raw.githubusercontent.com/$GITHUB_USER/poppfire/main/portal/$GUARD_SCRIPT"
GUARD_RC_URL="https://raw.githubusercontent.com/$GITHUB_USER/poppfire/main/portal/rc.d/poppfire_guard"
GUARD_ACTIONS_FILE="$ACTIONS_DIR/actions_poppfire_guard.conf"
REQUIREMENTS_FILE="requirements.txt"
REQUIREMENTS_URL="https://raw.githubusercontent.com/$GITHUB_USER/poppfire/main/portal/$REQUIREMENTS_FILE"
SCRIPT_URL="https://raw.githubusercontent.com/$GITHUB_USER/poppfire/main/portal/$MAIN_SCRIPT"
API_URL="https://127.0.0.1:5555/api"
# Zenarmor
ZENARMOR_DIR="/root/zenarmor"
ZENARMOR_REPLICADOR_ZIP="zenarmor_replicador.zip"
ZENARMOR_REPLICADOR_URL="https://raw.githubusercontent.com/$GITHUB_USER/$GITHUB_REPO/main/portal/$ZENARMOR_REPLICADOR_ZIP"
ES_HOST="http://172.18.25.252:9200"
# ---------------------------------

# =============================================================================
# FUNÇÃO: Exibir banner
# =============================================================================
show_banner() {
    clear
    echo ""
    echo "══════════════════════════════════════════════════════════════════════"
    echo ""
    echo "    ██████╗  ██████╗ ██████╗ ██████╗ ███████╗██╗██████╗ ███████╗"
    echo "    ██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔════╝██║██╔══██╗██╔════╝"
    echo "    ██████╔╝██║   ██║██████╔╝██████╔╝█████╗  ██║██████╔╝█████╗  "
    echo "    ██╔═══╝ ██║   ██║██╔═══╝ ██╔═══╝ ██╔══╝  ██║██╔══██╗██╔══╝  "
    echo "    ██║     ╚██████╔╝██║     ██║     ██║     ██║██║  ██║███████╗"
    echo "    ╚═╝      ╚═════╝ ╚═╝     ╚═╝     ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝"
    echo ""
    echo "         Solução e gestão de acesso e conectividade"
    echo ""
    echo "══════════════════════════════════════════════════════════════════════"
    echo ""
}

# =============================================================================
# FUNÇÃO: Instalar Replicador Zenarmor
# =============================================================================
install_zenarmor_replicador() {
    echo "### 10. Instalando replicador Zenarmor"

    if ! command -v /usr/local/bin/python3 >/dev/null 2>&1; then
        echo "ERRO: Python 3 não encontrado em /usr/local/bin/python3"
        echo "Instale o pacote 'os-python' via interface web."
        exit 1
    fi

    echo "Verificando dependência Python: requests..."
    if ! /usr/local/bin/python3 -c "import requests" >/dev/null 2>&1; then
        echo "ERRO: Módulo Python 'requests' não encontrado."
        echo "Instale com: /usr/local/bin/python3 -m pip install requests"
        exit 1
    fi

    mkdir -p "$ZENARMOR_DIR"

    echo "Baixando pacote do replicador..."
    curl -sS -L -o "$ZENARMOR_DIR/$ZENARMOR_REPLICADOR_ZIP" -H "Authorization: token $PAT" "$ZENARMOR_REPLICADOR_URL"
    if [ $? -ne 0 ]; then
        echo "ERRO: Falha ao baixar $ZENARMOR_REPLICADOR_ZIP"
        exit 1
    fi

    echo "Extraindo pacote..."
    unzip -o "$ZENARMOR_DIR/$ZENARMOR_REPLICADOR_ZIP" -d "$ZENARMOR_DIR" >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "ERRO: Falha ao extrair $ZENARMOR_REPLICADOR_ZIP"
        exit 1
    fi

    echo "Instalando script em /usr/local/etc/zenarmor/"
    mkdir -p /usr/local/etc/zenarmor
    cp "$ZENARMOR_DIR/zenarmor_replicador/replicador.py" /usr/local/etc/zenarmor/
    chmod +x /usr/local/etc/zenarmor/replicador.py

    echo "Instalando serviço em /usr/local/etc/rc.d/replicador"
    cp "$ZENARMOR_DIR/zenarmor_replicador/rc.d/replicador" /usr/local/etc/rc.d/
    chmod +x /usr/local/etc/rc.d/replicador

    if ! grep -q '^replicador_enable="YES"' /etc/rc.conf; then
        echo 'replicador_enable="YES"' >> /etc/rc.conf
        echo "replicador_enable adicionado ao rc.conf"
    else
        echo "replicador já estava ativado em /etc/rc.conf"
    fi

    echo "Criando template do Data Stream para este host..."
    HOSTNAME=$(hostname -f)
    INDEX_NAME="zenarmor-${HOSTNAME}-conn"
    TEMPLATE_NAME="zenarmor-ds-${HOSTNAME}"

    curl -s -X PUT "${ES_HOST}/_index_template/${TEMPLATE_NAME}" \
    -H 'Content-Type: application/json' \
    -d "{
      \"index_patterns\": [\"${INDEX_NAME}\"],
      \"data_stream\": {},
      \"template\": {
        \"mappings\": {
          \"properties\": {
            \"@timestamp\":      { \"type\": \"date\" },
            \"dst_hostname\":    { \"type\": \"keyword\" },
            \"start_time\":      { \"type\": \"long\" },
            \"dominio_raiz\":    { \"type\": \"keyword\" },
            \"conn_size\":       { \"type\": \"long\" },
            \"src_hostname\":    { \"type\": \"keyword\" },
            \"dst_nbytes\":      { \"type\": \"long\" }
          }
        },
        \"settings\": {
          \"number_of_shards\": 1,
          \"number_of_replicas\": 0
        }
      },
      \"priority\": 100
    }" && echo "Template criado para ${INDEX_NAME}"

    echo "Iniciando o serviço replicador..."
    service replicador start
}


# =============================================================================
# FUNÇÃO: Configurar Zabbix Agent (monitoramento de serviços)
# =============================================================================
configure_zabbix_agent_services() {
    echo "### 11. Configurando Zabbix Agent (serviços monitorados)"

    SERVICOS="replicador nginx sshd"

    # Diretório para scripts do Zabbix Agent 7
    mkdir -p /usr/local/etc/zabbix7/scripts

    # Script de status dos serviços
    cat << 'EOF' > /usr/local/etc/zabbix7/scripts/service_status.sh
#!/bin/sh
sudo /usr/sbin/service "$1" status >/dev/null 2>&1
if [ $? -eq 0 ]; then
  echo 1
else
  echo 0
fi
EOF

    chmod +x /usr/local/etc/zabbix7/scripts/service_status.sh

    # UserParameter no zabbix_agentd.conf (caso ainda não exista)
    if [ -f /usr/local/etc/zabbix_agentd.conf ]; then
        grep -q 'service.status\[\*\]' /usr/local/etc/zabbix_agentd.conf || \
        echo 'UserParameter=service.status[*],/usr/local/etc/zabbix7/scripts/service_status.sh $1' >> /usr/local/etc/zabbix_agentd.conf
    fi

    # Permissões no sudoers para cada serviço
    for SVC in $SERVICOS; do
        echo "zabbix ALL=(ALL) NOPASSWD: /usr/sbin/service $SVC status" >> /usr/local/etc/sudoers.d/zabbix_$SVC
        chmod 0440 /usr/local/etc/sudoers.d/zabbix_$SVC
        chown root:wheel /usr/local/etc/sudoers.d/zabbix_$SVC
    done

    # Reiniciar o agente Zabbix
    pkill -f zabbix_agentd
    sleep 2
    /usr/local/sbin/zabbix_agentd -c /usr/local/etc/zabbix_agentd.conf
}

# =============================================================================
# FUNÇÃO: Solicitar credenciais da API
# =============================================================================
# Suporta 3 modos (em ordem de prioridade):
#   1. Argumentos: --api-key KEY --api-secret SECRET
#   2. Variáveis de ambiente: OPNSENSE_API_KEY e OPNSENSE_API_SECRET
#   3. Interativo: solicita via prompt (modo padrão manual)
# =============================================================================
get_api_credentials() {
    # 1. Verificar se já foi definido via argumentos de linha de comando
    if [ -n "$API_KEY" ] && [ -n "$API_SECRET" ]; then
        echo "🔑 Credenciais da API recebidas via argumentos."
        echo ""
        return 0
    fi
    
    # 2. Verificar variáveis de ambiente
    if [ -n "$OPNSENSE_API_KEY" ] && [ -n "$OPNSENSE_API_SECRET" ]; then
        API_KEY="$OPNSENSE_API_KEY"
        API_SECRET="$OPNSENSE_API_SECRET"
        echo "🔑 Credenciais da API recebidas via variáveis de ambiente."
        echo ""
        return 0
    fi
    
    # 3. Modo não-interativo sem credenciais = erro
    if [ "$NON_INTERACTIVE" = "1" ]; then
        echo "❌ ERRO: Modo não-interativo ativo mas credenciais não fornecidas."
        echo "   Use: --api-key KEY --api-secret SECRET"
        echo "   Ou defina: OPNSENSE_API_KEY e OPNSENSE_API_SECRET"
        exit 1
    fi
    
    # 4. Modo interativo (padrão - execução manual)
    echo "┌─────────────────────────────────────────────────────────────────────┐"
    echo "│              CONFIGURAÇÃO DA API DO APPLIANCE                       │"
    echo "└─────────────────────────────────────────────────────────────────────┘"
    echo ""
    echo "Para continuar, você precisa das credenciais da API do Appliance."
    echo ""
    echo "Se ainda não criou, acesse:"
    echo "  → System → Access → Users → [seu usuário] → API Keys → +"
    echo ""
    echo "───────────────────────────────────────────────────────────────────────"
    echo ""
    
    printf "Digite a API Key: "
    read API_KEY
    
    if [ -z "$API_KEY" ]; then
        echo ""
        echo "❌ ERRO: API Key não pode ser vazia."
        exit 1
    fi
    
    printf "Digite a API Secret: "
    read API_SECRET
    
    if [ -z "$API_SECRET" ]; then
        echo ""
        echo "❌ ERRO: API Secret não pode ser vazio."
        exit 1
    fi
    
    echo ""
}

# =============================================================================
# FUNÇÃO: Validar credenciais da API
# =============================================================================
validate_api_credentials() {
    echo "🔐 Validando credenciais da API..."
    echo ""
    
    RESPONSE=$(curl -sk -w "\n%{http_code}" -u "$API_KEY:$API_SECRET" "$API_URL/core/firmware/status" 2>/dev/null)
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ Autenticação validada com sucesso!"
        echo ""
        return 0
    elif [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
        echo "❌ ERRO: Credenciais inválidas (HTTP $HTTP_CODE)"
        echo ""
        echo "Verifique:"
        echo "  1. Se a API Key e Secret estão corretos"
        echo "  2. Se o usuário tem permissões adequadas"
        echo ""
        exit 1
    elif [ "$HTTP_CODE" = "000" ]; then
        echo "❌ ERRO: Não foi possível conectar à API local"
        echo ""
        echo "Verifique se o serviço web do Appliance está rodando."
        echo ""
        exit 1
    else
        echo "⚠️  AVISO: Resposta inesperada (HTTP $HTTP_CODE)"
        echo "Continuando mesmo assim..."
        echo ""
        return 0
    fi
}

# =============================================================================
# FUNÇÃO: Criar Cron Job via API
# =============================================================================
create_cron_job() {
    echo "### 7. Configurando agendamento automático (Cron Job)"
    
    echo "Verificando se o agendamento já existe..."
    
    SEARCH_RESPONSE=$(curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/cron/settings/searchJobs" -X POST -H "Content-Type: application/json" -d '{"searchPhrase":"atualiza_portal"}' 2>/dev/null)
    
    if echo "$SEARCH_RESPONSE" | grep -q "atualiza_portal"; then
        echo "⚠️  Agendamento já existe. Pulando criação."
        return 0
    fi
    
    echo "Criando agendamento para execução a cada 1 minuto..."
    
    CREATE_RESPONSE=$(curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/cron/settings/addJob" -X POST -H "Content-Type: application/json" -d '{"job":{"enabled":"1","minutes":"*/1","hours":"*","days":"*","months":"*","weekdays":"*","command":"atualiza_portal run","parameters":"","description":"Executar Atualizacao do Portal POPPFIRE"}}' 2>/dev/null)
    
    if echo "$CREATE_RESPONSE" | grep -q '"uuid"'; then
        echo "✅ Agendamento criado com sucesso!"
        
        echo "Aplicando configurações do cron..."
        curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/cron/service/reconfigure" -X POST >/dev/null 2>&1
        
        return 0
    else
        echo "⚠️  Não foi possível criar o agendamento via API."
        echo ""
        echo "Crie manualmente em: System → Settings → Cron"
        return 1
    fi
}

# =============================================================================
# FUNÇÃO: Configurar Captive Portal via API
# =============================================================================
configure_captive_portal() {
    echo "### 8. Configurando Captive Portal"
    
    # Obter hostname do sistema (ex: box1000)
    SYSTEM_HOSTNAME=$(hostname -s 2>/dev/null || hostname)
    PORTAL_HOSTNAME="${SYSTEM_HOSTNAME}.poppfire.com.br"
    PORTAL_DESCRIPTION="Eldorado - Captive Portal"
    
    # Verificar se já existe uma zona
    echo "Verificando zonas existentes..."
    ZONES_RESPONSE=$(curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/captiveportal/settings/search_zones" -X POST -H "Content-Type: application/json" -d '{}' 2>/dev/null)
    
    if ! echo "$ZONES_RESPONSE" | grep -q '"total":0'; then
        echo "⚠️  Captive Portal já configurado. Pulando criação."
        return 0
    fi
    
    # Obter modelo de zona para extrair o UUID do certificado
    echo "Buscando certificado poppfire.com.br..."
    ZONE_MODEL=$(curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/captiveportal/settings/get_zone" 2>/dev/null)
    
    # Extrair UUID do certificado poppfire.com.br
    # Formato no JSON: "UUID":{"value":"nome do cert"...}
    CERT_UUID=$(echo "$ZONE_MODEL" | grep -o '"[0-9a-f]*":{"value":"[^"]*poppfire[^"]*"' | head -1 | cut -d'"' -f2)
    
    if [ -n "$CERT_UUID" ]; then
        CERT_NAME=$(echo "$ZONE_MODEL" | grep -o "\"$CERT_UUID\":{\"value\":\"[^\"]*\"" | cut -d'"' -f6)
        echo "✅ Certificado encontrado: $CERT_NAME"
        echo "   UUID: $CERT_UUID"
    else
        echo "⚠️  Certificado poppfire.com.br não encontrado"
        echo "   O Captive Portal será criado sem certificado específico."
        echo "   Configure manualmente em: Services → Captive Portal → Zones"
        CERT_UUID=""
    fi
    
    # Criar zona do Captive Portal
    echo "Criando zona do Captive Portal..."
    echo "   Interface: LAN"
    echo "   Hard Timeout: 480 minutos (8 horas)"
    echo "   Hostname: $PORTAL_HOSTNAME"
    echo "   Description: $PORTAL_DESCRIPTION"
    echo "   Auth Server: Freeradius"
    echo "   Always send accounting: Enabled"
    
    CREATE_ZONE=$(curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/captiveportal/settings/add_zone" -X POST -H "Content-Type: application/json" -d "{\"zone\":{\"enabled\":\"1\",\"interfaces\":\"lan\",\"authservers\":\"Freeradius\",\"alwaysSendAccountingReqs\":\"1\",\"idletimeout\":\"0\",\"hardtimeout\":\"480\",\"concurrentlogins\":\"1\",\"servername\":\"$PORTAL_HOSTNAME\",\"description\":\"$PORTAL_DESCRIPTION\"}}" 2>/dev/null)
    
    if echo "$CREATE_ZONE" | grep -q '"uuid"'; then
        ZONE_UUID=$(echo "$CREATE_ZONE" | grep -o '"uuid":"[^"]*"' | cut -d'"' -f4)
        echo "✅ Zona criada com sucesso! UUID: $ZONE_UUID"
        
        # Se encontrou certificado, atualizar a zona
        if [ -n "$CERT_UUID" ]; then
            echo "Vinculando certificado à zona..."
            UPDATE_RESULT=$(curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/captiveportal/settings/set_zone/$ZONE_UUID" -X POST -H "Content-Type: application/json" -d "{\"zone\":{\"certificate\":\"$CERT_UUID\"}}" 2>/dev/null)
            
            if echo "$UPDATE_RESULT" | grep -q '"result":"saved"'; then
                echo "✅ Certificado vinculado com sucesso!"
            else
                echo "⚠️  Não foi possível vincular o certificado automaticamente."
                echo "   Configure manualmente em: Services → Captive Portal → Zones"
            fi
        fi
        
        # Aplicar configuração
        echo "Aplicando configuração do Captive Portal..."
        curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/captiveportal/service/reconfigure" -X POST >/dev/null 2>&1
        
        # Iniciar serviço
        echo "Iniciando serviço do Captive Portal..."
        curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/captiveportal/service/start" -X POST >/dev/null 2>&1
        
        # Verificar status
        sleep 2
        STATUS=$(curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/captiveportal/service/status" 2>/dev/null)
        
        if echo "$STATUS" | grep -q '"status":"running"'; then
            echo "✅ Captive Portal está rodando!"
        else
            echo "⚠️  Status do Captive Portal: $STATUS"
        fi
        
        return 0
    else
        echo "❌ Falha ao criar zona do Captive Portal."
        echo "   Configure manualmente em: Services → Captive Portal → Zones"
        return 1
    fi
}

# =============================================================================
# FUNÇÃO: Liberar acesso WebGUI (porta 5555) no Captive Portal
# =============================================================================
add_captive_portal_allowed_webgui() {
    echo "### Liberando acesso WebGUI no Captive Portal (porta 5555)"

    # Verificar se já existe regra para porta 5555
    EXISTING=$(curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/captiveportal/settings/searchAllowedAddresses" -X POST -H "Content-Type: application/json" -d '{"searchPhrase":"WebGUI"}' 2>/dev/null)
    if echo "$EXISTING" | grep -q "5555"; then
        echo "⚠️  Regra de acesso WebGUI já existe. Pulando."
        return 0
    fi

    # Detectar IP da interface LAN via API
    echo "Detectando IP da interface LAN..."
    LAN_IP=$(curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/diagnostics/interface/getInterfaceConfig" 2>/dev/null | python3 -c "
import json,sys
try:
    data = json.loads(sys.stdin.read())
    for name, info in data.items():
        desc = info.get('description','').lower()
        if desc == 'lan' or name.lower() == 'lan':
            for addr in info.get('ipv4', []):
                ip = addr.get('ipaddr','')
                if ip:
                    print(ip)
                    sys.exit(0)
except:
    pass
" 2>/dev/null)

    if [ -z "$LAN_IP" ]; then
        echo "⚠️  Não foi possível detectar o IP da LAN automaticamente."
        echo "   Adicione manualmente em: Services → Captive Portal → Allowed Addresses"
        echo "   IP: <IP_DA_LAN>/32  Proto: TCP  Porta: 5555"
        return 1
    fi

    echo "   IP da LAN detectado: $LAN_IP"

    # Adicionar regra: permitir tráfego TCP para o IP da LAN na porta 5555 (WebGUI)
    echo "Adicionando regra de acesso WebGUI..."
    ADD_RESULT=$(curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/captiveportal/settings/addAllowedAddress" -X POST -H "Content-Type: application/json" -d "{\"address\":{\"ip\":\"$LAN_IP/32\",\"proto\":\"tcp\",\"port\":\"5555\",\"description\":\"Acesso WebGUI OPNsense (porta 5555)\"}}" 2>/dev/null)

    if echo "$ADD_RESULT" | grep -q '"uuid"'; then
        echo "✅ Regra de acesso WebGUI adicionada com sucesso!"
        echo "   → $LAN_IP:5555 liberado no Captive Portal"

        # Aplicar configuração
        curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/captiveportal/service/reconfigure" -X POST >/dev/null 2>&1
        return 0
    else
        echo "⚠️  Falha ao adicionar regra via API."
        echo "   Adicione manualmente em: Services → Captive Portal → Allowed Addresses"
        echo "   IP: $LAN_IP/32  Proto: TCP  Porta: 5555"
        return 1
    fi
}

# =============================================================================
# FUNÇÃO: Criar Cron Job do Guard (verificação a cada 1 minuto)
# =============================================================================
create_guard_cron_job() {
    echo "### Configurando agendamento do Portal Guard (Cron Job)"
    
    SEARCH_RESPONSE=$(curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/cron/settings/searchJobs" -X POST -H "Content-Type: application/json" -d '{"searchPhrase":"poppfire_guard"}' 2>/dev/null)
    
    if echo "$SEARCH_RESPONSE" | grep -q "poppfire_guard"; then
        echo "⚠️  Agendamento do Guard já existe. Pulando criação."
        return 0
    fi
    
    echo "Criando agendamento do Guard para execução a cada 1 minuto..."
    
    CREATE_RESPONSE=$(curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/cron/settings/addJob" -X POST -H "Content-Type: application/json" -d '{"job":{"enabled":"1","minutes":"*/1","hours":"*","days":"*","months":"*","weekdays":"*","command":"poppfire_guard check","parameters":"","description":"POPPFIRE Guard - Verificacao tunnel e portal"}}' 2>/dev/null)
    
    if echo "$CREATE_RESPONSE" | grep -q '"uuid"'; then
        echo "✅ Agendamento do Guard criado!"
        curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/cron/service/reconfigure" -X POST >/dev/null 2>&1
        return 0
    else
        echo "⚠️  Não foi possível criar o agendamento do Guard via API."
        return 1
    fi
}

# =============================================================================
# FUNÇÃO: Instalar POPPFIRE Portal Guard (tunnel check + backup/restore)
# =============================================================================
install_portal_guard() {
    echo "### Instalando POPPFIRE Portal Guard"
    
    # Baixar script guard
    echo "Baixando script guard..."
    curl -sS -o "$PORTAL_DIR/$GUARD_SCRIPT" -H "Authorization: token $PAT" "$GUARD_URL"
    if [ $? -ne 0 ]; then
        echo "AVISO: Falha ao baixar guard do GitHub. Verificando cópia local..."
    fi
    
    if [ ! -f "$PORTAL_DIR/$GUARD_SCRIPT" ]; then
        echo "ERRO: Script guard não encontrado."
        return 1
    fi
    
    chmod +x "$PORTAL_DIR/$GUARD_SCRIPT"
    echo "✅ Script guard instalado em $PORTAL_DIR/$GUARD_SCRIPT"
    
    # Instalar serviço rc.d para boot
    echo "Instalando serviço de boot (rc.d)..."
    curl -sS -o /usr/local/etc/rc.d/poppfire_guard -H "Authorization: token $PAT" "$GUARD_RC_URL" 2>/dev/null
    if [ $? -ne 0 ] || [ ! -f /usr/local/etc/rc.d/poppfire_guard ]; then
        # Criar manualmente se download falhar
        cat << 'RCEOF' > /usr/local/etc/rc.d/poppfire_guard
#!/bin/sh

# PROVIDE: poppfire_guard
# REQUIRE: NETWORKING wireguard
# BEFORE: captiveportal
# KEYWORD: shutdown

. /etc/rc.subr

name="poppfire_guard"
rcvar="${name}_enable"
guard_script="/root/portal/poppfire_portal_guard.sh"

start_cmd="${name}_start"
stop_cmd="${name}_stop"
status_cmd="${name}_status"

poppfire_guard_start()
{
    if [ ! -f "$guard_script" ]; then
        echo "ERRO: $guard_script nao encontrado"
        return 1
    fi
    echo "Iniciando POPPFIRE Portal Guard (boot mode)..."
    /bin/sh "$guard_script" boot &
}

poppfire_guard_stop()
{
    echo "Parando POPPFIRE Portal Guard..."
    rm -f /var/run/poppfire_guard.lock
}

poppfire_guard_status()
{
    if [ -f "$guard_script" ]; then
        /bin/sh "$guard_script" status
    else
        echo "Script guard nao encontrado em $guard_script"
    fi
}

load_rc_config $name
: ${poppfire_guard_enable:="NO"}
run_rc_command "$1"
RCEOF
    fi
    
    chmod +x /usr/local/etc/rc.d/poppfire_guard
    echo "✅ Serviço rc.d instalado"
    
    # Habilitar no rc.conf
    if ! grep -q '^poppfire_guard_enable="YES"' /etc/rc.conf; then
        echo 'poppfire_guard_enable="YES"' >> /etc/rc.conf
        echo "✅ poppfire_guard habilitado no rc.conf"
    else
        echo "Guard já habilitado no rc.conf"
    fi
    
    # Criar ação configd para o cron
    echo "Criando ação configd para o Guard..."
    cat << 'ACTEOF' > "$GUARD_ACTIONS_FILE"
[check]
command:/bin/sh /root/portal/poppfire_portal_guard.sh check
parameters:
type:script
message:POPPFIRE Guard - Verificacao tunnel e portal
description:POPPFIRE Guard - Verificacao tunnel e portal

[boot]
command:/bin/sh /root/portal/poppfire_portal_guard.sh boot
parameters:
type:script
message:POPPFIRE Guard - Boot inicializacao
description:POPPFIRE Guard - Boot inicializacao

[backup]
command:/bin/sh /root/portal/poppfire_portal_guard.sh backup
parameters:
type:script
message:POPPFIRE Guard - Backup do portal
description:POPPFIRE Guard - Backup do portal

[restore]
command:/bin/sh /root/portal/poppfire_portal_guard.sh restore
parameters:
type:script
message:POPPFIRE Guard - Restore do portal
description:POPPFIRE Guard - Restore do portal

[status]
command:/bin/sh /root/portal/poppfire_portal_guard.sh status
parameters:
type:script_output
message:POPPFIRE Guard - Status
description:POPPFIRE Guard - Status
ACTEOF
    
    echo "✅ Ação configd criada em $GUARD_ACTIONS_FILE"
    
    # Recarregar configd
    service configd restart
    sleep 2
    
    # Fazer backup inicial do portal se existir
    echo "Realizando backup inicial do portal..."
    /bin/sh "$PORTAL_DIR/$GUARD_SCRIPT" backup
    
    echo "✅ POPPFIRE Portal Guard instalado!"
    return 0
}

# =============================================================================
# FUNÇÃO: Limpar instalação anterior (modo reinstall)
# =============================================================================
cleanup_previous_install() {
    echo "⚠️  MODO REINSTALL: limpando instalação anterior..."

    # Serviços monitorados pelo Zabbix (para remover sudoers antigos)
    SERVICOS_REINSTALL="replicador nginx sshd"

    # Remover arquivos locais
    if [ -d "$PORTAL_DIR" ]; then
        rm -rf "$PORTAL_DIR"
        echo "Removido: $PORTAL_DIR"
    fi

    if [ -f "$ACTIONS_FILE" ]; then
        rm -f "$ACTIONS_FILE"
        echo "Removido: $ACTIONS_FILE"
    fi

    # Remover guard instalado anteriormente
    if [ -f /usr/local/etc/rc.d/poppfire_guard ]; then
        rm -f /usr/local/etc/rc.d/poppfire_guard
        echo "Removido: /usr/local/etc/rc.d/poppfire_guard"
    fi
    if [ -f "$GUARD_ACTIONS_FILE" ]; then
        rm -f "$GUARD_ACTIONS_FILE"
        echo "Removido: $GUARD_ACTIONS_FILE"
    fi
    sed -i '' '/poppfire_guard_enable/d' /etc/rc.conf 2>/dev/null || true

    # Remover cron do guard
    GUARD_SEARCH=$(curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/cron/settings/searchJobs" -X POST -H "Content-Type: application/json" -d '{"searchPhrase":"poppfire_guard"}' 2>/dev/null)
    if [ -n "$GUARD_SEARCH" ] && command -v python3 >/dev/null 2>&1; then
        GUARD_UUIDS=$(printf '%s' "$GUARD_SEARCH" | python3 -c "
import json,sys
try:
    data=json.loads(sys.stdin.read())
    rows=data.get('rows',[])
    uuids=[r.get('uuid') for r in rows if 'poppfire_guard' in r.get('command','') or 'poppfire_guard' in r.get('description','')]
    print(' '.join([u for u in uuids if u]))
except Exception:
    print('')
")
        for UUID in $GUARD_UUIDS; do
            curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/cron/settings/delJob/$UUID" -X POST >/dev/null 2>&1
            echo "Removido cron guard: $UUID"
        done
    fi

    # Remover replicador do Zenarmor instalado anteriormente
    if [ -f /usr/local/etc/zenarmor/replicador.py ]; then
        rm -f /usr/local/etc/zenarmor/replicador.py
        echo "Removido: /usr/local/etc/zenarmor/replicador.py"
    fi
    if [ -f /usr/local/etc/rc.d/replicador ]; then
        rm -f /usr/local/etc/rc.d/replicador
        echo "Removido: /usr/local/etc/rc.d/replicador"
    fi
    if [ -d "$ZENARMOR_DIR" ]; then
        rm -rf "$ZENARMOR_DIR"
        echo "Removido: $ZENARMOR_DIR"
    fi

    # Remover configurações do Zabbix Agent criadas pelo script
    if [ -f /usr/local/etc/zabbix7/scripts/service_status.sh ]; then
        rm -f /usr/local/etc/zabbix7/scripts/service_status.sh
        echo "Removido: /usr/local/etc/zabbix7/scripts/service_status.sh"
    fi
    if [ -f /usr/local/etc/zabbix_agentd.conf ]; then
        sed -i '' '/service.status\[\*\]/d' /usr/local/etc/zabbix_agentd.conf 2>/dev/null || true
    fi
    for SVC in $SERVICOS_REINSTALL; do
        if [ -f "/usr/local/etc/sudoers.d/zabbix_$SVC" ]; then
            rm -f "/usr/local/etc/sudoers.d/zabbix_$SVC"
            echo "Removido: /usr/local/etc/sudoers.d/zabbix_$SVC"
        fi
    done

    # Remover cron job se existir
    SEARCH_RESPONSE=$(curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/cron/settings/searchJobs" -X POST -H "Content-Type: application/json" -d '{"searchPhrase":"atualiza_portal"}' 2>/dev/null)

    if [ -n "$SEARCH_RESPONSE" ]; then
        if command -v python3 >/dev/null 2>&1; then
            # Extrair UUIDs via Python para evitar dependência do jq
            CRON_UUIDS=$(printf '%s' "$SEARCH_RESPONSE" | python3 - << 'PY'
import json,sys
try:
    data=json.loads(sys.stdin.read())
    rows=data.get('rows',[])
    uuids=[r.get('uuid') for r in rows if r.get('description','').find('Atualizacao do Portal POPPFIRE')!=-1 or r.get('command','').find('atualiza_portal')!=-1]
    print(" ".join([u for u in uuids if u]))
except Exception:
    print("")
PY
            )

            for UUID in $CRON_UUIDS; do
                curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/cron/settings/delJob/$UUID" -X POST >/dev/null 2>&1
                echo "Removido cron job: $UUID"
            done
        else
            echo "AVISO: python3 não encontrado, não foi possível remover cron job automaticamente."
        fi
    fi

    # Recarregar configd para refletir remoções
    service configd restart
    sleep 2
}

# =============================================================================
# INÍCIO DO SCRIPT
# =============================================================================

ensure_self_executable

# =============================================================================
# PARSER DE ARGUMENTOS
# =============================================================================
# Uso:
#   sh poppfire_setup.sh                                    (interativo)
#   sh poppfire_setup.sh --reinstall                         (reinstall interativo)
#   sh poppfire_setup.sh --api-key KEY --api-secret SECRET  (não-interativo)
#   sh poppfire_setup.sh -r --api-key KEY --api-secret SECRET
# =============================================================================
REINSTALL_MODE=0
NON_INTERACTIVE=0
API_KEY=""
API_SECRET=""

while [ $# -gt 0 ]; do
    case "$1" in
        --reinstall|-r)
            REINSTALL_MODE=1
            shift
            ;;
        --api-key)
            API_KEY="$2"
            NON_INTERACTIVE=1
            shift 2
            ;;
        --api-secret)
            API_SECRET="$2"
            NON_INTERACTIVE=1
            shift 2
            ;;
        --pat)
            PAT="$2"
            shift 2
            ;;
        --non-interactive|-ni)
            NON_INTERACTIVE=1
            shift
            ;;
        --help|-h)
            echo "Uso: sh poppfire_setup.sh [OPÇÕES]"
            echo ""
            echo "Opções:"
            echo "  --pat TOKEN          GitHub Personal Access Token"
            echo "  --api-key KEY        API Key do OPNsense (não-interativo)"
            echo "  --api-secret SECRET  API Secret do OPNsense (não-interativo)"
            echo "  --reinstall, -r      Limpar e reinstalar tudo"
            echo "  --non-interactive    Forçar modo não-interativo"
            echo "  --help, -h           Exibir esta ajuda"
            echo ""
            echo "Variáveis de ambiente (alternativa aos argumentos):"
            echo "  OPNSENSE_API_KEY     API Key do OPNsense"
            echo "  OPNSENSE_API_SECRET  API Secret do OPNsense"
            echo ""
            echo "Exemplos:"
            echo "  # Instalação manual (interativa):"
            echo "  sh poppfire_setup.sh"
            echo ""
            echo "  # Instalação via Ansible (não-interativa):"
            echo "  sh poppfire_setup.sh --api-key abc123 --api-secret xyz789"
            echo ""
            echo "  # Reinstalação via Ansible:"
            echo "  sh poppfire_setup.sh -r --api-key abc123 --api-secret xyz789"
            exit 0
            ;;
        *)
            echo "Argumento desconhecido: $1"
            echo "Use --help para ver as opções disponíveis."
            exit 1
            ;;
    esac
done

# Validar PAT (necessário para downloads do GitHub)
if [ -z "$PAT" ]; then
    echo "❌ ERRO: Token de acesso (PAT) não definido."
    echo ""
    echo "   Defina antes de executar:"
    echo "     setenv PAT ghp_xxxxx           (csh/tcsh - FreeBSD)"
    echo "     export PAT=ghp_xxxxx           (sh/bash)"
    echo "   Ou passe como argumento:"
    echo "     sh poppfire_setup.sh --pat ghp_xxxxx"
    exit 1
fi

export PAT="$PAT"

show_banner

get_api_credentials
validate_api_credentials

if [ $REINSTALL_MODE -eq 1 ]; then
    cleanup_previous_install
else
    # Aviso se já existe instalação anterior
    if [ -d "$PORTAL_DIR" ] || [ -f "$ACTIONS_FILE" ]; then
        echo "⚠️  Instalação anterior detectada."
        echo "   Execute novamente com --reinstall para zerar e reinstalar."
    fi
fi

echo "┌─────────────────────────────────────────────────────────────────────┐"
echo "│                    INICIANDO INSTALAÇÃO                             │"
echo "└─────────────────────────────────────────────────────────────────────┘"
echo ""

echo "### 1. Criando diretório $PORTAL_DIR"
mkdir -p "$PORTAL_DIR"
if [ $? -ne 0 ]; then
    echo "ERRO: Não foi possível criar o diretório $PORTAL_DIR."
    exit 1
fi

echo "### 2. Baixando o script principal ($MAIN_SCRIPT)"
curl -sS -o "$PORTAL_DIR/$MAIN_SCRIPT" -H "Authorization: token $PAT" "$SCRIPT_URL"
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao baixar o script $MAIN_SCRIPT."
    exit 1
fi

echo "### 3. Criando o Ambiente Virtual (venv)"
if ! command -v python3 >/dev/null 2>&1; then
    echo "ERRO: Python 3 não encontrado. Instale o pacote 'os-python' via interface web."
    exit 1
fi

python3 -m venv "$VENV_DIR"
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao criar o ambiente virtual em $VENV_DIR."
    exit 1
fi

echo "### 4. Instalando dependências do $REQUIREMENTS_FILE"
curl -sS -o "$PORTAL_DIR/$REQUIREMENTS_FILE" -H "Authorization: token $PAT" "$REQUIREMENTS_URL"

if [ $? -ne 0 ]; then
    echo "AVISO: Falha ao baixar requirements.txt."
else
    echo "Instalando pacotes via pip..."
    echo "Atualizando pip..."
    "$VENV_DIR/bin/python3" -m pip install --upgrade pip
    "$VENV_DIR/bin/pip" install -r "$PORTAL_DIR/$REQUIREMENTS_FILE"
    if [ $? -ne 0 ]; then
        echo "ERRO: Falha ao instalar as dependências."
        exit 1
    fi
fi

echo "### 5. Criando o arquivo de Ação para o Agendador"
ACTIONS_CONTENT="[run]
command:$VENV_DIR/bin/python3 $PORTAL_DIR/$MAIN_SCRIPT
parameters:
type:script
message:Executando Atualizacao do Portal POPPFIRE
description:Executar Atualizacao do Portal POPPFIRE"

echo "$ACTIONS_CONTENT" > "$ACTIONS_FILE"
if [ $? -ne 0 ]; then
    echo "ERRO: Não foi possível criar o arquivo de ações em $ACTIONS_FILE."
    exit 1
fi

echo "### 6. Reiniciando os serviços para reconhecer a nova ação"
service configd restart
sleep 2

# Criar o Cron Job via API
create_cron_job

# Configurar Captive Portal via API
configure_captive_portal

# Liberar acesso WebGUI no Captive Portal
add_captive_portal_allowed_webgui

# Instalar POPPFIRE Portal Guard
install_portal_guard

# Criar Cron Job do Guard
create_guard_cron_job

# Executar primeira atualização do portal
echo "### 9. Executando primeira atualização do Portal"
echo "Aguarde enquanto o portal é atualizado..."
"$VENV_DIR/bin/python3" "$PORTAL_DIR/$MAIN_SCRIPT"
if [ $? -eq 0 ]; then
    echo "✅ Portal atualizado com sucesso!"
else
    echo "⚠️  Houve um problema na atualização do portal."
    echo "   O cron tentará novamente em até 1 minuto."
fi

# Instalar replicador do Zenarmor
install_zenarmor_replicador

# Configurar Zabbix Agent (serviços monitorados)
configure_zabbix_agent_services

echo ""
echo "══════════════════════════════════════════════════════════════════════"
echo ""
echo "    ██████╗  ██████╗ ██████╗ ██████╗ ███████╗██╗██████╗ ███████╗"
echo "    ██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔════╝██║██╔══██╗██╔════╝"
echo "    ██████╔╝██║   ██║██████╔╝██████╔╝█████╗  ██║██████╔╝█████╗  "
echo "    ██╔═══╝ ██║   ██║██╔═══╝ ██╔═══╝ ██╔══╝  ██║██╔══██╗██╔══╝  "
echo "    ██║     ╚██████╔╝██║     ██║     ██║     ██║██║  ██║███████╗"
echo "    ╚═╝      ╚═════╝ ╚═╝     ╚═╝     ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝"
echo ""
echo "              ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo ""
echo "══════════════════════════════════════════════════════════════════════"
echo ""