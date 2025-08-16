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
CAPTIVE_DIR="/usr/local/captiveportal"
VIDEOS_DIR="/usr/local/captiveportal/videos"
BACKUP_DIR="/usr/local/captiveportal/backup"
SCRIPTS_DIR="/usr/local/captiveportal/scripts"
LOG_DIR="/var/log"

echo "Criando diretórios necessários..."
mkdir -p "$CAPTIVE_DIR"
mkdir -p "$VIDEOS_DIR"
mkdir -p "$BACKUP_DIR"
mkdir -p "$SCRIPTS_DIR"

echo "Instalando script updater..."
cat > "$SCRIPTS_DIR/captive_updater.py" << 'EOF'
#!/usr/bin/env python3
import os, sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC = BASE_DIR / 'sreadmin' / 'opnsense_captive_updater.py'

if SRC.exists():
    # Executa o updater a partir do arquivo distribuído (mantém uma cópia única)
    with open(SRC, 'rb') as f:
        code = compile(f.read(), str(SRC), 'exec')
        exec(code, {'__name__': '__main__'})
else:
    print(f"Arquivo de origem não encontrado: {SRC}")
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

SCRIPT_DIR="/usr/local/captiveportal/scripts"
LOG_FILE="/var/log/poppfire_portal_updater.log"
LOCK_FILE="/tmp/captive_updater.lock"

# Verificar se já está executando
if [ -f "$LOCK_FILE" ]; then
    echo "$(date): Updater já está executando" >> "$LOG_FILE"
    exit 1
fi

# Criar lock
echo $$ > "$LOCK_FILE"

# Executar updater
echo "$(date): Iniciando verificação de atualizações" >> "$LOG_FILE"
python3 "$SCRIPT_DIR/captive_updater.py" >> "$LOG_FILE" 2>&1
exit_code=$?

# Remover lock
rm -f "$LOCK_FILE"

echo "$(date): Verificação finalizada com código $exit_code" >> "$LOG_FILE"
exit $exit_code
EOF

chmod +x "$SCRIPTS_DIR/update_captive_portal.sh"

# Configurar cron para execução automática
echo "Configurando execução automática (cron)..."

# Adicionar entrada no crontab para executar a cada 5 minutos (idempotente)
CRON_LINE="*/5 * * * * /usr/local/captiveportal/scripts/update_captive_portal.sh"
(crontab -l 2>/dev/null | grep -F "$CRON_LINE") || (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -

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

LOG_FILE="/var/log/captive_portal_updater.log"
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
echo "  Log em tempo real: tail -f $LOG_FILE"
echo ""
echo "Antes de rodar em produção, edite o token no arquivo Python em: /usr/local/captiveportal/scripts/captive_updater.py (ou no fonte opnsense_captive_updater.py) e ajuste API_BASE_URL se necessário."
echo ""
echo "Configuração do cron: verificação a cada 5 minutos"
echo "Para alterar: crontab -e"
echo ""
echo "Diretórios:"
echo "  Portal:  $CAPTIVE_DIR"
echo "  Vídeos:  $VIDEOS_DIR"
echo "  Backup:  $BACKUP_DIR"
echo "  Scripts: $SCRIPTS_DIR"
