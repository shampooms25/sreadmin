#!/bin/sh
#
# Script de Instalação e Configuração do Portal Captive Updater
# Para OpenSense/FreeBSD
# 
# Este script configura o ambiente no OpenSense para executar 
# o updater do portal captive automaticamente
#

echo "=== Configuração do Portal Captive Updater (POPPFIRE) ==="
echo "Servidor padrão: https://paineleld.poppnet.com.br"
echo ""

# Verificar se é root
if [ "$(id -u)" != "0" ]; then
   echo "Este script deve ser executado como root" 1>&2
   exit 1
fi

# Diretórios necessários
# Ajuste para seu ambiente local (scripts e venv em /root/portal)
SCRIPTS_DIR="/root/portal"
LOG_DIR="/var/log"

echo "Criando diretórios necessários..."
mkdir -p "$SCRIPTS_DIR"

echo "Instalando script updater (launcher)..."
cat > "$SCRIPTS_DIR/captive_updater.py" << 'EOF'
#!/usr/bin/env python3
import os, sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# Preferir opnsense_captive_updater.py, senão usar install_opnsense_updater.py
candidates = [
    SCRIPT_DIR / 'opnsense_captive_updater.py',
    SCRIPT_DIR / 'install_opnsense_updater.py',
]

for src in candidates:
    if src.exists():
        with open(src, 'rb') as f:
            code = compile(f.read(), str(src), 'exec')
            exec(code, {'__name__': '__main__'})
        sys.exit(0)

print("Nenhum arquivo de updater encontrado (opnsense_captive_updater.py ou install_opnsense_updater.py)")
sys.exit(1)
EOF

# Tornar executável
chmod +x "$SCRIPTS_DIR/captive_updater.py"

# Criar script wrapper para logs
cat > "$SCRIPTS_DIR/update_captive_portal.sh" << 'EOF'
#!/bin/sh
#
# Wrapper para executar o updater do portal captive
#

SCRIPT_DIR="/root/portal"
LOG_FILE="/var/log/poppfire_portal_updater.log"
LOCK_FILE="/tmp/captive_updater.lock"

# Garantir PATH adequado quando executado via cron
PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Selecionar Python do venv, se existir
if [ -x "$SCRIPT_DIR/venv/bin/python3" ]; then
    PY="$SCRIPT_DIR/venv/bin/python3"
else
    PY="python3"
fi

# Verificar se já está executando
if [ -f "$LOCK_FILE" ]; then
    echo "$(date): Updater já está executando" >> "$LOG_FILE"
    exit 1
fi

# Criar lock
echo $$ > "$LOCK_FILE"

# Garantir remoção do lock em qualquer saída
trap 'rm -f "$LOCK_FILE"' EXIT INT TERM

# Executar updater
echo "$(date): Iniciando verificação de atualizações" >> "$LOG_FILE"
$PY "$SCRIPT_DIR/captive_updater.py" >> "$LOG_FILE" 2>&1
exit_code=$?

# Remover lock
rm -f "$LOCK_FILE"

echo "$(date): Verificação finalizada com código $exit_code" >> "$LOG_FILE"
exit $exit_code
EOF

chmod +x "$SCRIPTS_DIR/update_captive_portal.sh"

# Configurar cron para execução automática
echo "Configurando execução automática (cron)..."

# Agendar execução diária à meia-noite e remover entradas antigas
NEW_CRON_LINE="0 0 * * * /root/portal/update_captive_portal.sh"
OLD_PATH="/usr/local/captiveportal/scripts/update_captive_portal.sh"

# Captura crontab atual (ou vazio), remove linhas antigas e quaisquer linhas antigas do mesmo script, e aplica nova linha
{
    crontab -l 2>/dev/null | grep -v "$OLD_PATH" | grep -v "/root/portal/update_captive_portal.sh" 2>/dev/null
    echo "$NEW_CRON_LINE"
} | crontab -

# Criar configuração de log rotation
cat > "/etc/newsyslog.conf.d/captive_portal.conf" << 'EOF'
# Log rotation para captive portal updater
/var/log/poppfire_portal_updater.log    644  10   1000 *     JC
EOF

# Criar script de status
cat > "$SCRIPTS_DIR/status.sh" << 'EOF'
#!/bin/sh
#
# Script para verificar status do updater
#

LOG_FILE="/var/log/poppfire_portal_updater.log"
STATE_FILE="/var/db/poppfire_portal_state.json"
LOCK_FILE="/tmp/captive_updater.lock"

echo "=== Status do Portal Captive Updater ==="
echo ""

# Verificar se está executando
if [ -f "$LOCK_FILE" ]; then
    echo "Status: EXECUTANDO (PID: $(cat $LOCK_FILE))"
else
    echo "Status: PARADO"
fi

echo ""

# Mostrar último update
if [ -f "$STATE_FILE" ]; then
    echo "Estado atual:"
    cat "$STATE_FILE" | python3 -m json.tool 2>/dev/null || cat "$STATE_FILE"
else
    echo "Nenhum estado salvo ainda"
fi

echo ""

# Mostrar últimas linhas do log
if [ -f "$LOG_FILE" ]; then
    echo "Últimas 10 linhas do log:"
    tail -10 "$LOG_FILE"
else
    echo "Nenhum log encontrado"
fi
EOF

chmod +x "$SCRIPTS_DIR/status.sh"

# Testar conectividade com servidor
echo "Testando conectividade com servidor..."
if command -v curl > /dev/null 2>&1; then
    if curl -s --connect-timeout 5 "https://paineleld.poppnet.com.br/api/appliances/portal/status/" -o /dev/null; then
        echo "✓ API acessível"
    else
        echo "⚠ API não acessível (verifique URL, DNS e conectividade)"
    fi
else
    echo "⚠ curl não encontrado - instalando..."
    pkg install -y curl
fi

# Executar primeira verificação
echo ""
echo "Executando primeira verificação..."
"$SCRIPTS_DIR/update_captive_portal.sh"

echo ""
echo "=== Instalação Concluída ==="
echo ""
echo "Comandos disponíveis:"
echo "  Status:           $SCRIPTS_DIR/status.sh"
echo "  Executar manual:  $SCRIPTS_DIR/update_captive_portal.sh"
echo "  Log em tempo real: tail -f /var/log/poppfire_portal_updater.log"
echo ""
echo "Antes de rodar em produção, edite o token no arquivo Python em: /root/portal/opnsense_captive_updater.py (ou no launcher /root/portal/captive_updater.py) e ajuste API_BASE_URL se necessário."
echo ""
echo "Configuração do cron: execução diária à meia-noite (00:00)"
echo "Para alterar: crontab -e"
echo ""
echo "Diretórios:"
echo "  Scripts: $SCRIPTS_DIR"
