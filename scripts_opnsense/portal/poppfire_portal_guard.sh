#!/bin/sh

# =============================================================================
# POPPFIRE Portal Guard
# =============================================================================
# Garante que o Captive Portal NUNCA exiba o template padrão do OPNsense.
#
# Modos de operação:
#   boot    - Executado na inicialização do OPNsense (via rc.d)
#   check   - Executado via cron a cada 1 minuto
#   backup  - Força backup manual do portal customizado
#   restore - Força restore manual do backup
#   status  - Mostra status do túnel, portal e backup
#
# Lógica:
#   1. Verifica se o túnel WireGuard está UP (handshake recente)
#   2. Se UP:  restaura backup customizado → inicia captive portal
#   3. Se DOWN: mantém captive portal PARADO (nunca mostra default)
#   4. Sempre que conectado e portal customizado instalado, faz backup
# =============================================================================

GUARD_NAME="poppfire_guard"
LOG_TAG="poppfire_guard"
BACKUP_DIR="/var/db/poppfire_portal_backups"
BACKUP_LATEST="$BACKUP_DIR/portal_latest.tar.gz"
BACKUP_BOOT="$BACKUP_DIR/portal_boot_restore.tar.gz"
STATE_FILE="/var/db/poppfire_guard_state"
LOCK_FILE="/var/run/poppfire_guard.lock"
CAPTIVEPORTAL_BASE="/var/captiveportal"
HTDOCS_DEFAULT="/usr/local/opnsense/scripts/captiveportal/htdocs_default"

# Tempo máximo (segundos) desde o último handshake para considerar o túnel UP
WG_HANDSHAKE_MAX_AGE=180

# Marcadores que identificam nosso template POPPFIRE (qualquer um basta)
POPPFIRE_MARKERS="poppfire|POPPFIRE|Portal de Acesso|videoPlayer|checkVideo|captive_video_tracker"

# =============================================================================
# FUNÇÕES UTILITÁRIAS
# =============================================================================

log_info() {
    logger -t "$LOG_TAG" -p user.info "$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $1"
}

log_warn() {
    logger -t "$LOG_TAG" -p user.warning "$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [WARN] $1"
}

log_error() {
    logger -t "$LOG_TAG" -p user.err "$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $1"
}

# Lock para evitar execuções simultâneas
acquire_lock() {
    if [ -f "$LOCK_FILE" ]; then
        LOCK_PID=$(cat "$LOCK_FILE" 2>/dev/null)
        if [ -n "$LOCK_PID" ] && kill -0 "$LOCK_PID" 2>/dev/null; then
            log_warn "Outra instância em execução (PID $LOCK_PID). Abortando."
            exit 0
        fi
        rm -f "$LOCK_FILE"
    fi
    echo $$ > "$LOCK_FILE"
}

release_lock() {
    rm -f "$LOCK_FILE"
}

save_state() {
    # $1 = tunnel_status (up/down), $2 = portal_status (running/stopped), $3 = action
    echo "timestamp=$(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "$STATE_FILE"
    echo "tunnel=$1" >> "$STATE_FILE"
    echo "portal=$2" >> "$STATE_FILE"
    echo "last_action=$3" >> "$STATE_FILE"
}

# =============================================================================
# VERIFICAÇÃO DO TÚNEL WIREGUARD
# =============================================================================

check_wireguard_tunnel() {
    # Retorna 0 se o túnel está UP (handshake recente), 1 se DOWN
    
    if ! command -v wg >/dev/null 2>&1; then
        log_warn "Comando 'wg' não encontrado"
        return 1
    fi

    # Obter últimos handshakes de todos os peers
    WG_OUTPUT=$(wg show all latest-handshakes 2>/dev/null)
    
    if [ -z "$WG_OUTPUT" ]; then
        log_warn "Nenhuma interface WireGuard ativa"
        return 1
    fi

    # Verificar se algum peer teve handshake nos últimos WG_HANDSHAKE_MAX_AGE segundos
    NOW=$(date +%s)
    TUNNEL_UP=1  # 1 = false em shell

    echo "$WG_OUTPUT" | while read -r IFACE PUBKEY TIMESTAMP; do
        if [ -n "$TIMESTAMP" ] && [ "$TIMESTAMP" != "0" ]; then
            AGE=$((NOW - TIMESTAMP))
            if [ "$AGE" -le "$WG_HANDSHAKE_MAX_AGE" ]; then
                # Handshake recente encontrado
                exit 0  # sai do subshell com sucesso
            fi
        fi
    done
    
    RESULT=$?
    
    if [ $RESULT -eq 0 ]; then
        return 0  # Túnel UP
    fi

    # Fallback: verificar se a interface wg tem tráfego (ifconfig)
    if ifconfig wg0 >/dev/null 2>&1; then
        # Verificar se tem IP atribuído
        WG_IP=$(ifconfig wg0 2>/dev/null | grep "inet " | awk '{print $2}')
        if [ -n "$WG_IP" ]; then
            # Tentar ping no gateway do túnel (primeiro IP da rede)
            # Detectar rede a partir do IP do túnel
            TUNNEL_NET=$(echo "$WG_IP" | sed 's/\.[0-9]*$/.1/')
            if ping -c 1 -W 2 "$TUNNEL_NET" >/dev/null 2>&1; then
                return 0  # Túnel funcional
            fi
            # Tentar pingar hosts conhecidos da rede
            for HOST in 172.18.25.252 172.18.25.253; do
                if ping -c 1 -W 2 "$HOST" >/dev/null 2>&1; then
                    return 0
                fi
            done
        fi
    fi

    return 1  # Túnel DOWN
}

# =============================================================================
# DETECÇÃO DE HTDOCS DO CAPTIVE PORTAL
# =============================================================================

discover_htdocs_paths() {
    # Lista caminhos de htdocs ativos (zone0/htdocs, zone1/htdocs, etc.)
    PATHS=""
    if [ -d "$CAPTIVEPORTAL_BASE" ]; then
        for ZONE_DIR in "$CAPTIVEPORTAL_BASE"/zone*; do
            if [ -d "$ZONE_DIR/htdocs" ]; then
                PATHS="$PATHS $ZONE_DIR/htdocs"
            fi
        done
    fi
    # Fallback
    if [ -z "$PATHS" ]; then
        for ALT in "/usr/local/captiveportal/htdocs" "/usr/local/captiveportal"; do
            if [ -d "$ALT" ]; then
                PATHS="$PATHS $ALT"
            fi
        done
    fi
    echo "$PATHS"
}

get_primary_htdocs() {
    PATHS=$(discover_htdocs_paths)
    echo "$PATHS" | awk '{print $1}'
}

# =============================================================================
# VERIFICAÇÃO SE O PORTAL TEM NOSSO TEMPLATE CUSTOMIZADO
# =============================================================================

is_custom_portal() {
    # $1 = caminho do diretório a verificar
    DIR="$1"
    INDEX="$DIR/index.html"
    
    if [ ! -f "$INDEX" ]; then
        return 1
    fi
    
    if grep -qE "$POPPFIRE_MARKERS" "$INDEX" 2>/dev/null; then
        return 0  # É nosso template
    fi
    
    return 1  # Template padrão ou outro
}

# =============================================================================
# BACKUP DO PORTAL CUSTOMIZADO
# =============================================================================

do_backup() {
    HTDOCS=$(get_primary_htdocs)
    
    if [ -z "$HTDOCS" ] || [ ! -d "$HTDOCS" ]; then
        log_warn "Nenhum htdocs encontrado para backup"
        return 1
    fi
    
    if ! is_custom_portal "$HTDOCS"; then
        log_warn "Portal atual não é customizado POPPFIRE. Backup cancelado."
        return 1
    fi
    
    mkdir -p "$BACKUP_DIR"
    
    # Criar backup timestamped
    TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
    BACKUP_TS="$BACKUP_DIR/portal_backup_${TIMESTAMP}.tar.gz"
    
    tar -czf "$BACKUP_TS" -C "$HTDOCS" . 2>/dev/null
    if [ $? -ne 0 ]; then
        log_error "Falha ao criar backup em $BACKUP_TS"
        return 1
    fi
    
    # Copiar como latest (sempre sobrescrito)
    cp -f "$BACKUP_TS" "$BACKUP_LATEST"
    
    # Copiar como boot restore (usado na inicialização)
    cp -f "$BACKUP_TS" "$BACKUP_BOOT"
    
    # Também copiar para o htdocs_default do OPNsense (persistência pós-reboot)
    if [ -d "$HTDOCS_DEFAULT" ] || [ -d "$(dirname "$HTDOCS_DEFAULT")" ]; then
        mkdir -p "$HTDOCS_DEFAULT"
        tar -xzf "$BACKUP_LATEST" -C "$HTDOCS_DEFAULT" 2>/dev/null
        log_info "Template default do OPNsense atualizado com portal POPPFIRE"
    fi
    
    # Limpar backups antigos (manter últimos 5)
    ls -1t "$BACKUP_DIR"/portal_backup_*.tar.gz 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null
    
    BACKUP_SIZE=$(ls -lh "$BACKUP_LATEST" 2>/dev/null | awk '{print $5}')
    log_info "Backup realizado: $BACKUP_LATEST ($BACKUP_SIZE)"
    
    return 0
}

# =============================================================================
# RESTORE DO PORTAL CUSTOMIZADO
# =============================================================================

do_restore() {
    # Prioridade: 1) boot restore, 2) latest backup
    RESTORE_FILE=""
    if [ -f "$BACKUP_BOOT" ]; then
        RESTORE_FILE="$BACKUP_BOOT"
    elif [ -f "$BACKUP_LATEST" ]; then
        RESTORE_FILE="$BACKUP_LATEST"
    else
        # Procurar o backup mais recente
        RESTORE_FILE=$(ls -1t "$BACKUP_DIR"/portal_backup_*.tar.gz 2>/dev/null | head -1)
    fi
    
    if [ -z "$RESTORE_FILE" ] || [ ! -f "$RESTORE_FILE" ]; then
        log_error "Nenhum backup disponível para restore"
        return 1
    fi
    
    HTDOCS_LIST=$(discover_htdocs_paths)
    
    if [ -z "$HTDOCS_LIST" ]; then
        log_warn "Nenhum htdocs encontrado. Criando diretório padrão."
        mkdir -p "$CAPTIVEPORTAL_BASE/zone0/htdocs"
        HTDOCS_LIST="$CAPTIVEPORTAL_BASE/zone0/htdocs"
    fi
    
    RESTORED=0
    for HTDOCS in $HTDOCS_LIST; do
        mkdir -p "$HTDOCS"
        
        # Limpar conteúdo atual
        rm -rf "$HTDOCS"/* 2>/dev/null
        
        # Extrair backup
        tar -xzf "$RESTORE_FILE" -C "$HTDOCS" 2>/dev/null
        if [ $? -eq 0 ]; then
            # Corrigir permissões
            chown -R www:www "$HTDOCS" 2>/dev/null || chown -R root:wheel "$HTDOCS" 2>/dev/null
            chmod -R 755 "$HTDOCS" 2>/dev/null
            log_info "Portal restaurado em $HTDOCS (de $RESTORE_FILE)"
            RESTORED=$((RESTORED + 1))
        else
            log_error "Falha ao restaurar em $HTDOCS"
        fi
    done
    
    # Também restaurar no htdocs_default
    if [ -d "$(dirname "$HTDOCS_DEFAULT")" ]; then
        mkdir -p "$HTDOCS_DEFAULT"
        tar -xzf "$RESTORE_FILE" -C "$HTDOCS_DEFAULT" 2>/dev/null
    fi
    
    if [ $RESTORED -gt 0 ]; then
        return 0
    fi
    return 1
}

# =============================================================================
# CONTROLE DO CAPTIVE PORTAL
# =============================================================================

stop_captive_portal() {
    log_info "Parando Captive Portal..."
    configctl captiveportal stop >/dev/null 2>&1
    # Limpar IPFW e states residuais
    ipfw -f flush >/dev/null 2>&1
    pfctl -F states >/dev/null 2>&1
    log_info "Captive Portal parado e regras limpas"
}

start_captive_portal() {
    log_info "Iniciando Captive Portal..."
    configctl captiveportal start >/dev/null 2>&1
    sleep 2
    
    # Verificar se iniciou
    STATUS=$(configctl captiveportal status 2>/dev/null)
    if echo "$STATUS" | grep -qi "running"; then
        log_info "Captive Portal iniciado com sucesso"
        return 0
    else
        log_warn "Captive Portal pode não ter iniciado: $STATUS"
        return 1
    fi
}

is_captive_portal_running() {
    STATUS=$(configctl captiveportal status 2>/dev/null)
    echo "$STATUS" | grep -qi "running"
    return $?
}

# =============================================================================
# MODO BOOT - Executado na inicialização
# =============================================================================

mode_boot() {
    log_info "=== POPPFIRE Guard: Inicialização do sistema ==="
    
    # Passo 1: IMEDIATAMENTE parar o captive portal (evitar template padrão)
    stop_captive_portal
    log_info "Captive Portal parado preventivamente (boot)"
    
    # Passo 2: Restaurar backup do portal customizado
    if do_restore; then
        log_info "Portal customizado restaurado do backup"
    else
        log_warn "Sem backup para restaurar. Captive Portal permanecerá DESLIGADO."
        save_state "unknown" "stopped" "boot_no_backup"
        return 0
    fi
    
    # Passo 3: Aguardar WireGuard subir (tentar por até 120 segundos)
    log_info "Aguardando túnel WireGuard..."
    WAIT=0
    MAX_WAIT=120
    TUNNEL_OK=1
    
    while [ $WAIT -lt $MAX_WAIT ]; do
        if check_wireguard_tunnel; then
            TUNNEL_OK=0
            break
        fi
        sleep 5
        WAIT=$((WAIT + 5))
        if [ $((WAIT % 30)) -eq 0 ]; then
            log_info "Aguardando túnel... ${WAIT}s/${MAX_WAIT}s"
        fi
    done
    
    if [ $TUNNEL_OK -eq 0 ]; then
        log_info "Túnel WireGuard UP após ${WAIT}s"
        
        # Passo 4: Com túnel UP e portal restaurado, iniciar captive portal
        start_captive_portal
        save_state "up" "running" "boot_tunnel_up"
    else
        log_warn "Túnel WireGuard DOWN após ${MAX_WAIT}s de espera"
        log_warn "Captive Portal NÃO será iniciado (sem FreeRADIUS)"
        save_state "down" "stopped" "boot_tunnel_down"
    fi
    
    log_info "=== POPPFIRE Guard: Boot finalizado ==="
}

# =============================================================================
# MODO CHECK - Executado via cron a cada 1 minuto
# =============================================================================

mode_check() {
    TUNNEL_STATUS="down"
    PORTAL_STATUS="stopped"
    
    # Verificar túnel
    if check_wireguard_tunnel; then
        TUNNEL_STATUS="up"
    fi
    
    # Verificar captive portal
    if is_captive_portal_running; then
        PORTAL_STATUS="running"
    fi
    
    HTDOCS=$(get_primary_htdocs)
    HAS_CUSTOM=1
    if [ -n "$HTDOCS" ] && is_custom_portal "$HTDOCS"; then
        HAS_CUSTOM=0
    fi
    
    # --- Lógica de decisão ---
    
    if [ "$TUNNEL_STATUS" = "up" ]; then
        # Túnel UP
        
        if [ "$PORTAL_STATUS" = "running" ]; then
            # Portal rodando - verificar se é nosso template
            if [ $HAS_CUSTOM -eq 0 ]; then
                # Tudo OK: portal customizado rodando com túnel UP
                # Fazer backup (silencioso)
                do_backup >/dev/null 2>&1
                save_state "up" "running" "check_ok"
            else
                # Portal rodando mas com template ERRADO!
                log_warn "Portal com template incorreto detectado!"
                stop_captive_portal
                if do_restore; then
                    start_captive_portal
                    save_state "up" "running" "check_restored_wrong_template"
                else
                    log_error "Sem backup para corrigir template. Portal DESLIGADO."
                    save_state "up" "stopped" "check_no_backup_wrong_template"
                fi
            fi
        else
            # Portal parado com túnel UP - restaurar e iniciar
            log_info "Túnel UP, restaurando e iniciando portal..."
            if do_restore; then
                start_captive_portal
                save_state "up" "running" "check_started"
            elif [ -f "$BACKUP_LATEST" ] || [ -f "$BACKUP_BOOT" ]; then
                do_restore
                start_captive_portal
                save_state "up" "running" "check_started_retry"
            else
                log_warn "Túnel UP mas sem backup. Portal permanece DESLIGADO."
                save_state "up" "stopped" "check_no_backup"
            fi
        fi
    else
        # Túnel DOWN
        
        if [ "$PORTAL_STATUS" = "running" ]; then
            # Portal rodando sem túnel - PARAR (sem FreeRADIUS não funciona)
            log_warn "Túnel DOWN! Parando Captive Portal (sem FreeRADIUS)"
            stop_captive_portal
            save_state "down" "stopped" "check_stopped_no_tunnel"
        else
            # Portal parado, túnel down - nada a fazer
            save_state "down" "stopped" "check_waiting"
        fi
    fi
}

# =============================================================================
# MODO STATUS - Exibe informações
# =============================================================================

mode_status() {
    echo ""
    echo "══════════════════════════════════════════════════════════════"
    echo "  POPPFIRE Portal Guard - Status"
    echo "══════════════════════════════════════════════════════════════"
    echo ""
    
    # Túnel WireGuard
    printf "  WireGuard Tunnel: "
    if check_wireguard_tunnel; then
        echo "🟢 UP"
    else
        echo "🔴 DOWN"
    fi
    
    # Captive Portal
    printf "  Captive Portal:   "
    if is_captive_portal_running; then
        echo "🟢 Running"
    else
        echo "🔴 Stopped"
    fi
    
    # Template
    HTDOCS=$(get_primary_htdocs)
    printf "  Template:         "
    if [ -n "$HTDOCS" ] && is_custom_portal "$HTDOCS"; then
        echo "✅ POPPFIRE Customizado"
    elif [ -n "$HTDOCS" ] && [ -f "$HTDOCS/index.html" ]; then
        echo "⚠️  OPNsense Padrão (NÃO é POPPFIRE)"
    else
        echo "❌ Nenhum template instalado"
    fi
    
    # Backup
    printf "  Último Backup:    "
    if [ -f "$BACKUP_LATEST" ]; then
        BSIZE=$(ls -lh "$BACKUP_LATEST" 2>/dev/null | awk '{print $5}')
        BDATE=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$BACKUP_LATEST" 2>/dev/null || stat -c "%y" "$BACKUP_LATEST" 2>/dev/null | cut -d. -f1)
        echo "✅ $BSIZE ($BDATE)"
    else
        echo "❌ Nenhum backup"
    fi
    
    printf "  Backup Boot:      "
    if [ -f "$BACKUP_BOOT" ]; then
        echo "✅ Disponível"
    else
        echo "❌ Não disponível"
    fi
    
    # Último estado
    if [ -f "$STATE_FILE" ]; then
        echo ""
        echo "  Último estado registrado:"
        sed 's/^/    /' "$STATE_FILE"
    fi
    
    # WireGuard details
    echo ""
    echo "  WireGuard peers:"
    wg show all latest-handshakes 2>/dev/null | while read -r IFACE PUBKEY TS; do
        if [ -n "$TS" ] && [ "$TS" != "0" ]; then
            NOW=$(date +%s)
            AGE=$((NOW - TS))
            echo "    $IFACE: handshake ${AGE}s atrás"
        else
            echo "    $IFACE: sem handshake"
        fi
    done
    
    # Htdocs paths
    echo ""
    echo "  Htdocs detectados:"
    discover_htdocs_paths | tr ' ' '\n' | while read -r P; do
        if [ -n "$P" ]; then
            COUNT=$(find "$P" -type f 2>/dev/null | wc -l | tr -d ' ')
            echo "    $P ($COUNT arquivos)"
        fi
    done
    
    echo ""
    echo "══════════════════════════════════════════════════════════════"
    echo ""
}

# =============================================================================
# MAIN
# =============================================================================

mkdir -p "$BACKUP_DIR"

MODE="${1:-check}"

case "$MODE" in
    boot)
        acquire_lock
        mode_boot
        release_lock
        ;;
    check)
        acquire_lock
        mode_check
        release_lock
        ;;
    backup)
        acquire_lock
        do_backup
        release_lock
        ;;
    restore)
        acquire_lock
        do_restore
        release_lock
        ;;
    status)
        mode_status
        ;;
    *)
        echo "Uso: $0 {boot|check|backup|restore|status}"
        echo ""
        echo "  boot    - Executar na inicialização (via rc.d)"
        echo "  check   - Verificação periódica (via cron)"
        echo "  backup  - Forçar backup do portal customizado"
        echo "  restore - Forçar restore do backup"
        echo "  status  - Exibir status completo"
        exit 1
        ;;
esac
