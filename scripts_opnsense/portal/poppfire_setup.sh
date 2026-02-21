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
API_URL="http://127.0.0.1/api"
# Zenarmor
ZENARMOR_DIR="/root/zenarmor"
ZENARMOR_REPLICADOR_ZIP="zenarmor_replicador.zip"
ZENARMOR_REPLICADOR_URL="https://raw.githubusercontent.com/$GITHUB_USER/$GITHUB_REPO/main/portal/$ZENARMOR_REPLICADOR_ZIP"
ES_HOST="http://172.18.25.252:9200"
ZABBIX_SERVER="172.18.25.252"
# Zenarmor ETL (Graylog)
ZENARMOR_ETL_DIR="/root/zenarmor-etl"
ZENARMOR_ETL_SCRIPT="zenarmor_graylog.py"
ZENARMOR_ETL_ACTIONS="actions_zenarmor_etl.conf"
ZENARMOR_ETL_BASE_URL="https://raw.githubusercontent.com/$GITHUB_USER/$GITHUB_REPO/main/zenarmor-etl"
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
        echo "AVISO: Python 3 não encontrado em /usr/local/bin/python3"
        echo "   Instale o pacote 'os-python' via interface web."
        echo "   Replicador Zenarmor não será instalado."
        return 1
    fi

    echo "Verificando dependência Python: requests..."
    if ! /usr/local/bin/python3 -c "import requests" >/dev/null 2>&1; then
        echo "AVISO: Módulo Python 'requests' não encontrado."
        echo "   Instale com: /usr/local/bin/python3 -m pip install requests"
        echo "   Replicador Zenarmor não será instalado."
        return 1
    fi

    mkdir -p "$ZENARMOR_DIR"

    echo "Baixando pacote do replicador..."
    curl -sS -L -o "$ZENARMOR_DIR/$ZENARMOR_REPLICADOR_ZIP" -H "Authorization: token $PAT" "$ZENARMOR_REPLICADOR_URL"
    if [ $? -ne 0 ]; then
        echo "AVISO: Falha ao baixar $ZENARMOR_REPLICADOR_ZIP (sem conexão de rede)"
        echo "   Execute novamente com --reinstall quando houver conectividade."
        return 1
    fi

    echo "Extraindo pacote..."
    unzip -o "$ZENARMOR_DIR/$ZENARMOR_REPLICADOR_ZIP" -d "$ZENARMOR_DIR" >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "AVISO: Falha ao extrair $ZENARMOR_REPLICADOR_ZIP"
        return 1
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
    service replicador start || true
    echo "✅ Replicador Zenarmor instalado com sucesso!"
}


# =============================================================================
# FUNÇÃO: Instalar Zenarmor ETL (envio de dados para Graylog via Syslog)
# =============================================================================
install_zenarmor_etl() {
    echo "### 12. Instalando Zenarmor ETL (Graylog)"

    # Verificar se Zenarmor está presente
    if [ ! -d /usr/local/datastore/sqlite ]; then
        echo "⚠️  Zenarmor não encontrado (/usr/local/datastore/sqlite)."
        echo "   ETL para Graylog não será instalado."
        return 1
    fi

    if ! command -v python3 >/dev/null 2>&1; then
        echo "⚠️  Python3 não encontrado. ETL não será instalado."
        return 1
    fi

    mkdir -p "$ZENARMOR_ETL_DIR"

    # Baixar script principal
    echo "   Baixando $ZENARMOR_ETL_SCRIPT..."
    curl -sS -L -o "$ZENARMOR_ETL_DIR/$ZENARMOR_ETL_SCRIPT" \
        -H "Authorization: token $PAT" \
        "$ZENARMOR_ETL_BASE_URL/$ZENARMOR_ETL_SCRIPT"
    if [ $? -ne 0 ] || [ ! -s "$ZENARMOR_ETL_DIR/$ZENARMOR_ETL_SCRIPT" ]; then
        echo "⚠️  Falha ao baixar $ZENARMOR_ETL_SCRIPT."
        return 1
    fi
    chmod +x "$ZENARMOR_ETL_DIR/$ZENARMOR_ETL_SCRIPT"
    echo "   ✅ Script instalado em $ZENARMOR_ETL_DIR/$ZENARMOR_ETL_SCRIPT"

    # Instalar ação configd para o cron
    echo "   Instalando ação configd..."
    cat > "$ACTIONS_DIR/$ZENARMOR_ETL_ACTIONS" << 'ETLEOF'
[run]
command:/usr/local/bin/python3 /root/zenarmor-etl/zenarmor_graylog.py --once
type:script
message:Enviando dados Zenarmor para Graylog
description:Enviar dados Zenarmor para Graylog
ETLEOF
    echo "   ✅ Ação configd criada em $ACTIONS_DIR/$ZENARMOR_ETL_ACTIONS"

    # Recarregar configd para reconhecer nova ação
    service configd restart >/dev/null 2>&1
    sleep 2

    # Criar cron job (a cada 5 minutos) — idempotente
    echo "   Configurando cron job (a cada 5 minutos)..."
    _ensure_single_cron_job \
        "zenarmor_etl" \
        "zenarmor_etl" \
        '{"job":{"enabled":"1","minutes":"*/5","hours":"*","days":"*","months":"*","weekdays":"*","command":"zenarmor_etl run","parameters":"","description":"Zenarmor ETL - Enviar dados para Graylog"}}' \
        "Cron Zenarmor ETL"

    # Testar info do firewall
    echo "   Testando detecção do firewall..."
    python3 "$ZENARMOR_ETL_DIR/$ZENARMOR_ETL_SCRIPT" --info

    # Executar primeiro envio
    echo "   Executando primeiro envio para Graylog..."
    python3 "$ZENARMOR_ETL_DIR/$ZENARMOR_ETL_SCRIPT" --once
    if [ $? -eq 0 ]; then
        echo "   ✅ Zenarmor ETL instalado e primeiro envio realizado!"
    else
        echo "   ⚠️  Primeiro envio falhou. O cron tentará a cada 5 minutos."
    fi

    return 0
}

# =============================================================================
# FUNÇÃO: Configurar Zabbix Agent (monitoramento de serviços)
# =============================================================================
configure_zabbix_agent_services() {
    echo "### 11. Configurando Zabbix Agent (serviços monitorados)"

    SERVICOS="replicador nginx sshd"

    # ── Detectar config do Zabbix Agent ──────────────────────────────
    # Estratégia: verificar qual config o agente EM EXECUÇÃO usa (ps aux),
    # pois o OPNsense pode ter tanto /usr/local/etc/zabbix7/ (plugin)
    # quanto /usr/local/etc/zabbix_agentd.conf (legado), e o agente
    # pode estar rodando com qualquer um deles.
    ZABBIX_CONF=""
    ZABBIX_CONF_DIR=""
    ZABBIX_INCLUDE_DIR=""
    ZABBIX_SCRIPT_DIR=""

    # 1) Tentar detectar a partir do processo em execução
    RUNNING_CONF=$(ps aux | grep '[z]abbix_agentd' | grep -o '\-c [^ ]*' | head -1 | awk '{print $2}')
    if [ -n "$RUNNING_CONF" ] && [ -f "$RUNNING_CONF" ]; then
        ZABBIX_CONF="$RUNNING_CONF"
        ZABBIX_CONF_DIR=$(dirname "$ZABBIX_CONF")
        echo "   Detectado config do agente em execução: $ZABBIX_CONF"
    # 2) Fallback: verificar arquivos no disco
    elif [ -f /usr/local/etc/zabbix7/zabbix_agentd.conf ]; then
        ZABBIX_CONF="/usr/local/etc/zabbix7/zabbix_agentd.conf"
        ZABBIX_CONF_DIR="/usr/local/etc/zabbix7"
        echo "   Detectado: Zabbix Agent 7 (OPNsense plugin)"
    elif [ -f /usr/local/etc/zabbix_agentd.conf ]; then
        ZABBIX_CONF="/usr/local/etc/zabbix_agentd.conf"
        ZABBIX_CONF_DIR="/usr/local/etc"
        echo "   Detectado: Zabbix Agent (instalação manual/legada)"
    else
        echo "⚠️  Zabbix Agent não encontrado. Pulando configuração."
        echo "   Instale via: System → Firmware → Plugins → os-zabbix-agent"
        return 1
    fi

    echo "   Config: $ZABBIX_CONF"

    # ── Limpar UserParameters inline quebrados do config principal ────
    # Versões anteriores inseriam UserParameter direto no config, causando
    # duplicação e linhas corrompidas. Remover — deve ficar apenas no Include.
    if grep -q "^UserParameter=service\.status" "$ZABBIX_CONF" 2>/dev/null; then
        sed -i '' '/^UserParameter=service\.status/d' "$ZABBIX_CONF"
        echo "   🧹 Removido UserParameter inline do config principal (deve ficar no Include)"
    fi

    # ── Script de status dos serviços ────────────────────────────────
    # Colocar em /usr/local/etc/zabbix7/scripts/ (caminho fixo e previsível)
    # independente de qual config o agente usa.
    ZABBIX_SCRIPT_DIR="/usr/local/etc/zabbix7/scripts"
    mkdir -p "$ZABBIX_SCRIPT_DIR"

    cat << 'EOF' > "$ZABBIX_SCRIPT_DIR/service_status.sh"
#!/bin/sh
sudo /usr/sbin/service "$1" status >/dev/null 2>&1
if [ $? -eq 0 ]; then
  echo 1
else
  echo 0
fi
EOF
    chmod +x "$ZABBIX_SCRIPT_DIR/service_status.sh"

    # ── Detectar/configurar Include dir ──────────────────────────────
    EXPECTED_INCLUDE_DIR="$ZABBIX_CONF_DIR/zabbix_agentd.conf.d"
    EXISTING_INCLUDE=$(grep "^Include=" "$ZABBIX_CONF" 2>/dev/null | head -1 | cut -d= -f2 | sed 's|/$||')

    if [ "$EXISTING_INCLUDE" != "$EXPECTED_INCLUDE_DIR" ]; then
        # Corrigir Include se estiver errado ou inexistente
        sed -i '' "s|^Include=.*|Include=$EXPECTED_INCLUDE_DIR/|" "$ZABBIX_CONF"
        if ! grep -q "^Include=$EXPECTED_INCLUDE_DIR/" "$ZABBIX_CONF"; then
            echo "Include=$EXPECTED_INCLUDE_DIR/" >> "$ZABBIX_CONF"
        fi
        echo "   Include corrigido/adicionado: $EXPECTED_INCLUDE_DIR/"
    fi

    ZABBIX_INCLUDE_DIR="$EXPECTED_INCLUDE_DIR"
    mkdir -p "$ZABBIX_INCLUDE_DIR"

    # ── Criar UserParameter no Include dir ───────────────────────────
    # Usa caminho absoluto fixo para o script (independe de ZABBIX_CONF_DIR)
    cat << 'UPEOF' > "$ZABBIX_INCLUDE_DIR/poppfire_services.conf"
# POPPFIRE - Monitoramento de serviços via Zabbix
# Gerado automaticamente por poppfire_setup.sh
UserParameter=service.status[*],/usr/local/etc/zabbix7/scripts/service_status.sh $1
UPEOF
    echo "   ✅ UserParameter criado em $ZABBIX_INCLUDE_DIR/poppfire_services.conf"

    # ── Se existe OUTRO config, instalar lá também ──────────────────
    # OPNsense pode ter ambos os configs; ao reiniciar via service pode usar
    # o outro. Garantir que ambos têm o Include e o UserParameter correto.
    ZABBIX_OTHER_CONF=""
    if [ "$ZABBIX_CONF" = "/usr/local/etc/zabbix_agentd.conf" ] && \
       [ -f /usr/local/etc/zabbix7/zabbix_agentd.conf ]; then
        ZABBIX_OTHER_CONF="/usr/local/etc/zabbix7/zabbix_agentd.conf"
    elif [ "$ZABBIX_CONF" != "/usr/local/etc/zabbix_agentd.conf" ] && \
         [ -f /usr/local/etc/zabbix_agentd.conf ]; then
        ZABBIX_OTHER_CONF="/usr/local/etc/zabbix_agentd.conf"
    fi

    if [ -n "$ZABBIX_OTHER_CONF" ]; then
        echo "   Configurando também: $ZABBIX_OTHER_CONF"

        # Limpar UserParameter inline do outro config
        sed -i '' '/^UserParameter=service\.status/d' "$ZABBIX_OTHER_CONF" 2>/dev/null

        OTHER_INCLUDE=$(grep "^Include=" "$ZABBIX_OTHER_CONF" 2>/dev/null | head -1 | cut -d= -f2 | sed 's|/$||')
        if [ -n "$OTHER_INCLUDE" ]; then
            mkdir -p "$OTHER_INCLUDE"
            cat << 'UPEOF2' > "$OTHER_INCLUDE/poppfire_services.conf"
# POPPFIRE - Monitoramento de serviços via Zabbix
# Gerado automaticamente por poppfire_setup.sh
UserParameter=service.status[*],/usr/local/etc/zabbix7/scripts/service_status.sh $1
UPEOF2
            echo "   ✅ UserParameter replicado em $OTHER_INCLUDE/poppfire_services.conf"
        fi
    fi

    # ── Garantir Server= e ServerActive= em TODOS os configs ─────────
    # Aplicar tanto no config principal quanto no outro (se existir),
    # para que independente de qual config o agente use, ele aceite
    # conexões do servidor Zabbix.
    for ZCONF in "$ZABBIX_CONF" "$ZABBIX_OTHER_CONF"; do
        [ -z "$ZCONF" ] && continue
        [ ! -f "$ZCONF" ] && continue

        echo "   Verificando Server= em $ZCONF..."
        CURRENT_SERVER=$(grep "^Server=" "$ZCONF" 2>/dev/null | head -1 | cut -d= -f2)
        if [ -n "$CURRENT_SERVER" ]; then
            if ! echo "$CURRENT_SERVER" | grep -q "$ZABBIX_SERVER"; then
                NEW_SERVER="${CURRENT_SERVER},${ZABBIX_SERVER}"
                sed -i '' "s|^Server=.*|Server=$NEW_SERVER|" "$ZCONF"
                echo "   ✅ Server= atualizado em $ZCONF"
            fi
        else
            echo "Server=127.0.0.1,$ZABBIX_SERVER" >> "$ZCONF"
            echo "   ✅ Server= adicionado em $ZCONF"
        fi

        CURRENT_ACTIVE=$(grep "^ServerActive=" "$ZCONF" 2>/dev/null | head -1 | cut -d= -f2)
        if [ -n "$CURRENT_ACTIVE" ]; then
            if ! echo "$CURRENT_ACTIVE" | grep -q "$ZABBIX_SERVER"; then
                NEW_ACTIVE="${CURRENT_ACTIVE},${ZABBIX_SERVER}"
                sed -i '' "s|^ServerActive=.*|ServerActive=$NEW_ACTIVE|" "$ZCONF"
                echo "   ✅ ServerActive= atualizado em $ZCONF"
            fi
        else
            echo "ServerActive=$ZABBIX_SERVER" >> "$ZCONF"
            echo "   ✅ ServerActive= adicionado em $ZCONF"
        fi
    done

    # Permissões no sudoers para cada serviço (idempotente: sobrescreve em vez de append)
    for SVC in $SERVICOS; do
        SUDOERS_FILE="/usr/local/etc/sudoers.d/zabbix_$SVC"
        echo "zabbix ALL=(ALL) NOPASSWD: /usr/sbin/service $SVC status" > "$SUDOERS_FILE"
        chmod 0440 "$SUDOERS_FILE"
        chown root:wheel "$SUDOERS_FILE"
    done
    echo "   ✅ Sudoers configurado para: $SERVICOS"

    # Validar sintaxe dos sudoers antes de reiniciar
    if command -v visudo >/dev/null 2>&1; then
        for SVC in $SERVICOS; do
            if ! visudo -cf "/usr/local/etc/sudoers.d/zabbix_$SVC" >/dev/null 2>&1; then
                echo "   ⚠️  Erro de sintaxe em sudoers para $SVC — corrigindo..."
                echo "zabbix ALL=(ALL) NOPASSWD: /usr/sbin/service $SVC status" > "/usr/local/etc/sudoers.d/zabbix_$SVC"
                chmod 0440 "/usr/local/etc/sudoers.d/zabbix_$SVC"
                chown root:wheel "/usr/local/etc/sudoers.d/zabbix_$SVC"
            fi
        done
    fi

    # Reiniciar o agente Zabbix — usar restart direto do processo para
    # evitar que o OPNsense regenere o config e apague o Include
    echo "   Reiniciando Zabbix Agent..."
    pkill -f zabbix_agentd 2>/dev/null
    sleep 2

    # Localizar binário do zabbix_agentd
    ZABBIX_BIN=""
    for ZBIN in /usr/local/sbin/zabbix_agentd /usr/local/sbin/zabbix_agentd2; do
        if [ -x "$ZBIN" ]; then
            ZABBIX_BIN="$ZBIN"
            break
        fi
    done

    if [ -n "$ZABBIX_BIN" ]; then
        "$ZABBIX_BIN" -c "$ZABBIX_CONF"
        echo "   ✅ Zabbix Agent reiniciado ($ZABBIX_BIN)"
    else
        echo "   ⚠️  Binário do Zabbix Agent não encontrado"
        echo "   Reinicie manualmente: service zabbix_agentd restart"
    fi

    # Verificar se o UserParameter está ativo
    sleep 2
    if [ -n "$ZABBIX_BIN" ]; then
        TEST_RESULT=$("$ZABBIX_BIN" -c "$ZABBIX_CONF" -t "service.status[replicador]" 2>&1)
        if echo "$TEST_RESULT" | grep -q '\[t|1\]'; then
            echo "   ✅ Teste: service.status[replicador] = 1 (rodando)"
        elif echo "$TEST_RESULT" | grep -q '\[t|0\]'; then
            echo "   ✅ Teste: service.status[replicador] = 0 (parado)"
        elif echo "$TEST_RESULT" | grep -q 'NOTSUPPORTED'; then
            echo "   ❌ UserParameter não reconhecido pelo Zabbix Agent"
            echo "   Verificando config carregado..."
            echo "   Include dir: $ZABBIX_INCLUDE_DIR"
            ls -la "$ZABBIX_INCLUDE_DIR/" 2>/dev/null
            echo "   Conteúdo do UserParameter:"
            cat "$ZABBIX_INCLUDE_DIR/poppfire_services.conf" 2>/dev/null
            echo "   Linhas Include no config:"
            grep "^Include" "$ZABBIX_CONF" 2>/dev/null
        else
            echo "   Resultado do teste: $TEST_RESULT"
        fi
    fi
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
# FUNÇÃO AUXILIAR: Garantir exatamente 1 cron job por tipo
# Uso: _ensure_single_cron_job "SEARCH_TERM" "MATCH_FIELD" 'JSON_DO_JOB' "DESCRIÇÃO"
#
# Lógica:
#   1. Busca TODOS os cron jobs que contenham SEARCH_TERM
#   2. Filtra pelo campo MATCH_FIELD (command ou description)
#   3. Se encontrar duplicatas: deleta todas, recria 1
#   4. Se encontrar exatamente 1: mantém
#   5. Se não encontrar: cria 1
# =============================================================================
_ensure_single_cron_job() {
    _SEARCH="$1"
    _MATCH="$2"
    _JOB_JSON="$3"
    _LABEL="$4"

    # Buscar TODOS os cron jobs — NÃO confiar no searchPhrase da API
    # Usar rowCount grande e searchPhrase vazio para pegar tudo
    _RESPONSE=$(curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/cron/settings/searchJobs" -X POST -H "Content-Type: application/json" -d '{"searchPhrase":"","rowCount":9999}' 2>/dev/null)

    # Filtrar localmente no Python pelo campo command/description
    _UUIDS=""
    _COUNT=0
    if [ -n "$_RESPONSE" ] && command -v python3 >/dev/null 2>&1; then
        _UUIDS=$(printf '%s' "$_RESPONSE" | python3 -c "
import json,sys
try:
    data=json.loads(sys.stdin.read())
    rows=data.get('rows',[])
    match='$_MATCH'
    uuids=[]
    for r in rows:
        uuid=r.get('uuid','')
        cmd=r.get('command','')
        desc=r.get('description','')
        if uuid and (match in cmd or match in desc):
            uuids.append(uuid)
    print(' '.join(uuids))
except:
    print('')
" 2>/dev/null)
        # Contar resultados
        for _U in $_UUIDS; do
            _COUNT=$((_COUNT + 1))
        done
    fi

    echo "   Encontradas $_COUNT entradas para '$_MATCH'"

    if [ "$_COUNT" -eq 1 ]; then
        echo "   ✅ $_LABEL já existe (1 entrada). OK."
        return 0
    elif [ "$_COUNT" -gt 1 ]; then
        echo "   ⚠️  $_LABEL: $_COUNT duplicatas encontradas. Removendo todas..."
        for _U in $_UUIDS; do
            curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/cron/settings/delJob/$_U" -X POST >/dev/null 2>&1
            echo "      Removido: $_U"
        done
        echo "   Recriando entrada única..."
    else
        echo "   Criando $_LABEL..."
    fi

    # Criar exatamente 1 entrada
    _CREATE=$(curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/cron/settings/addJob" -X POST -H "Content-Type: application/json" -d "$_JOB_JSON" 2>/dev/null)
    if echo "$_CREATE" | grep -q '"uuid"'; then
        echo "   ✅ $_LABEL criado com sucesso!"
        curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/cron/service/reconfigure" -X POST >/dev/null 2>&1
        return 0
    else
        echo "   ⚠️  Falha ao criar $_LABEL via API."
        return 1
    fi
}

# =============================================================================
# FUNÇÃO: Criar Cron Job via API (idempotente — sempre 1 entrada)
# =============================================================================
create_cron_job() {
    echo "### 7. Configurando agendamento automático (Cron Job)"
    _ensure_single_cron_job \
        "atualiza_portal" \
        "atualiza_portal" \
        '{"job":{"enabled":"1","minutes":"*/1","hours":"*","days":"*","months":"*","weekdays":"*","command":"atualiza_portal run","parameters":"","description":"Executar Atualizacao do Portal POPPFIRE"}}' \
        "Cron Atualizacao Portal"
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
    echo "   Concurrent Logins: Ilimitado (evitar re-auth em reconex\u00e3o)"
    
    CREATE_ZONE=$(curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/captiveportal/settings/add_zone" -X POST -H "Content-Type: application/json" -d "{\"zone\":{\"enabled\":\"1\",\"interfaces\":\"lan\",\"authservers\":\"Freeradius\",\"alwaysSendAccountingReqs\":\"1\",\"idletimeout\":\"0\",\"hardtimeout\":\"480\",\"concurrentlogins\":\"0\",\"servername\":\"$PORTAL_HOSTNAME\",\"description\":\"$PORTAL_DESCRIPTION\"}}" 2>/dev/null)
    
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
        
        # Configurar URL de redirecionamento HTTPS transparente
        # Evita problemas de cert mismatch que causam loops de re-auth
        echo "Configurando redirecionamento HTTPS..."
        curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/captiveportal/settings/set_zone/$ZONE_UUID" -X POST -H "Content-Type: application/json" -d "{\"zone\":{\"transparentHTTPSURL\":\"https://$PORTAL_HOSTNAME/\"}}" 2>/dev/null | grep -q '"result":"saved"' && echo "✅ transparentHTTPSURL configurada" || echo "⚠️  transparentHTTPSURL não suportada (versão antiga)"

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
# FUNÇÃO: Adicionar Allowed Addresses essenciais no Captive Portal
# - WebGUI (porta 5555)
# - DNS (porta 53 TCP/UDP)
# - DHCP (portas 67-68 UDP) — via 0.0.0.0/0 pois é broadcast
# =============================================================================
add_captive_portal_allowed_addresses() {
    echo "### Configurando Allowed Addresses no Captive Portal"

    # Detectar IP da interface LAN via API
    echo "   Detectando IP da interface LAN..."
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
        echo "   Adicione manualmente: WebGUI, DNS, DHCP"
        return 1
    fi

    echo "   IP da LAN detectado: $LAN_IP"

    # Função auxiliar para adicionar regra se não existir
    _add_allowed() {
        _SEARCH_KEY="$1"
        _IP="$2"
        _PROTO="$3"
        _PORT="$4"
        _DESC="$5"

        # Verificar se já existe
        _EXISTING=$(curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/captiveportal/settings/searchAllowedAddresses" -X POST -H "Content-Type: application/json" -d "{\"searchPhrase\":\"$_DESC\"}" 2>/dev/null)
        if echo "$_EXISTING" | grep -q "\"$_PORT\""; then
            echo "   ⚠️  $_DESC já existe. Pulando."
            return 0
        fi

        _RESULT=$(curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/captiveportal/settings/addAllowedAddress" -X POST -H "Content-Type: application/json" -d "{\"address\":{\"ip\":\"$_IP\",\"proto\":\"$_PROTO\",\"port\":\"$_PORT\",\"description\":\"$_DESC\"}}" 2>/dev/null)
        if echo "$_RESULT" | grep -q '"uuid"'; then
            echo "   ✅ $_DESC"
        else
            echo "   ⚠️  Falha: $_DESC"
        fi
    }

    # 1. WebGUI (porta 5555)
    _add_allowed "WebGUI" "$LAN_IP/32" "tcp" "5555" "WebGUI OPNsense (TCP 5555)"

    # 2. DNS TCP (porta 53) — para o gateway/LAN IP
    _add_allowed "DNS TCP" "$LAN_IP/32" "tcp" "53" "DNS TCP (porta 53)"

    # 3. DNS UDP (porta 53) — essencial para resolução de nomes
    _add_allowed "DNS UDP" "$LAN_IP/32" "udp" "53" "DNS UDP (porta 53)"

    # 4. DHCP (portas 67-68 UDP) — broadcast, usar 0.0.0.0/0
    _add_allowed "DHCP" "0.0.0.0/0" "udp" "67" "DHCP Server (UDP 67)"
    _add_allowed "DHCP Client" "0.0.0.0/0" "udp" "68" "DHCP Client (UDP 68)"

    # Aplicar configuração
    echo "   Aplicando configurações..."
    curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/captiveportal/service/reconfigure" -X POST >/dev/null 2>&1
    echo "   ✅ Allowed Addresses configuradas"
}

# =============================================================================
# FUNÇÃO: Criar Cron Job do Guard (idempotente — sempre 1 entrada)
# =============================================================================
create_guard_cron_job() {
    echo "### Configurando agendamento do Portal Guard (Cron Job)"
    _ensure_single_cron_job \
        "poppfire_guard" \
        "poppfire_guard" \
        '{"job":{"enabled":"1","minutes":"*/1","hours":"*","days":"*","months":"*","weekdays":"*","command":"poppfire_guard check","parameters":"","description":"POPPFIRE Guard - Verificacao tunnel e portal"}}' \
        "Cron Guard Portal"
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

    # Remover TODOS os cron jobs do POPPFIRE (guard + portal)
    # Buscar TODOS os jobs sem filtro para garantir que nenhum escape
    echo "Removendo cron jobs duplicados..."
    ALL_JOBS=$(curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/cron/settings/searchJobs" -X POST -H "Content-Type: application/json" -d '{"searchPhrase":"","rowCount":9999}' 2>/dev/null)
    if [ -n "$ALL_JOBS" ] && command -v python3 >/dev/null 2>&1; then
        POPPFIRE_UUIDS=$(printf '%s' "$ALL_JOBS" | python3 -c "
import json,sys
try:
    data=json.loads(sys.stdin.read())
    rows=data.get('rows',[])
    uuids=[]
    for r in rows:
        uuid=r.get('uuid','')
        cmd=r.get('command','')
        desc=r.get('description','')
        txt=cmd+' '+desc
        if uuid and ('atualiza_portal' in txt or 'poppfire_guard' in txt or 'POPPFIRE' in txt or 'zenarmor_etl' in txt or 'Zenarmor ETL' in txt):
            uuids.append(uuid)
    print(' '.join(uuids))
except:
    print('')
" 2>/dev/null)
        _DEL_COUNT=0
        for UUID in $POPPFIRE_UUIDS; do
            curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/cron/settings/delJob/$UUID" -X POST >/dev/null 2>&1
            _DEL_COUNT=$((_DEL_COUNT + 1))
        done
        echo "Removidos $_DEL_COUNT cron jobs do POPPFIRE"
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

    # Remover Zenarmor ETL (Graylog) instalado anteriormente
    if [ -d "$ZENARMOR_ETL_DIR" ]; then
        rm -rf "$ZENARMOR_ETL_DIR"
        echo "Removido: $ZENARMOR_ETL_DIR"
    fi
    if [ -f "$ACTIONS_DIR/$ZENARMOR_ETL_ACTIONS" ]; then
        rm -f "$ACTIONS_DIR/$ZENARMOR_ETL_ACTIONS"
        echo "Removido: $ACTIONS_DIR/$ZENARMOR_ETL_ACTIONS"
    fi

    # Remover configurações do Zabbix Agent criadas pelo script
    # Limpar ambos os caminhos possíveis (Zabbix 7 plugin e instalação manual)
    for ZDIR in /usr/local/etc/zabbix7 /usr/local/etc; do
        if [ -f "$ZDIR/scripts/service_status.sh" ]; then
            rm -f "$ZDIR/scripts/service_status.sh"
            echo "Removido: $ZDIR/scripts/service_status.sh"
        fi
    done
    # Remover arquivo de UserParameter include
    for ZINCDIR in /usr/local/etc/zabbix7/zabbix_agentd.conf.d /usr/local/etc/zabbix_agentd.conf.d; do
        if [ -f "$ZINCDIR/poppfire_services.conf" ]; then
            rm -f "$ZINCDIR/poppfire_services.conf"
            echo "Removido: $ZINCDIR/poppfire_services.conf"
        fi
    done
    # Limpar UserParameter legado do config principal (versões anteriores)
    for ZCONF in /usr/local/etc/zabbix7/zabbix_agentd.conf /usr/local/etc/zabbix_agentd.conf; do
        if [ -f "$ZCONF" ]; then
            sed -i '' '/service.status\[\*\]/d' "$ZCONF" 2>/dev/null || true
        fi
    done
    for SVC in $SERVICOS_REINSTALL; do
        if [ -f "/usr/local/etc/sudoers.d/zabbix_$SVC" ]; then
            rm -f "/usr/local/etc/sudoers.d/zabbix_$SVC"
            echo "Removido: /usr/local/etc/sudoers.d/zabbix_$SVC"
        fi
    done

    # Aplicar remoções dos cron jobs
    curl -sk -u "$API_KEY:$API_SECRET" "$API_URL/cron/service/reconfigure" -X POST >/dev/null 2>&1

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

# Atualizar credenciais da API local no updater (cada box tem suas próprias)
echo "   Atualizando credenciais da API local no updater..."
sed -i '' "s|LOCAL_API_KEY = \"[^\"]*\"|LOCAL_API_KEY = \"$API_KEY\"|" "$PORTAL_DIR/$MAIN_SCRIPT"
sed -i '' "s|LOCAL_API_SECRET = \"[^\"]*\"|LOCAL_API_SECRET = \"$API_SECRET\"|" "$PORTAL_DIR/$MAIN_SCRIPT"
echo "   ✅ Credenciais da API local atualizadas no updater"

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

# Configurar Allowed Addresses no Captive Portal (WebGUI, DNS, DHCP)
add_captive_portal_allowed_addresses

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

# Instalar replicador do Zenarmor (Elasticsearch)
install_zenarmor_replicador
if [ $? -ne 0 ]; then
    echo "⚠️  Replicador Zenarmor não instalado (verifique rede/dependências)."
    echo "   Para instalar depois: sh poppfire_setup.sh --reinstall --pat \$PAT --api-key \$API_KEY --api-secret \$API_SECRET"
fi

# Instalar Zenarmor ETL (Graylog)
install_zenarmor_etl
if [ $? -ne 0 ]; then
    echo "⚠️  Zenarmor ETL não instalado (Zenarmor não detectado ou sem rede)."
fi

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