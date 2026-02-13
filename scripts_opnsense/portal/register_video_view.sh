#!/bin/sh
#
# Script para registrar visualização de vídeo no portal captive
# Uso: ./register_video_view.sh <username> <video>
#
# Exemplo: ./register_video_view.sh "202020" "eld01.mp4"
#

# URL da API
API_URL="https://paineleld.poppnet.com.br/api/captive-portal/success/"

# Parâmetros
USERNAME="$1"
VIDEO="$2"
ORIGIN="${3:-captive_portal}"

# Validar parâmetros
if [ -z "$USERNAME" ] || [ -z "$VIDEO" ]; then
    echo "Uso: $0 <username> <video> [origin]"
    echo "Exemplo: $0 '202020' 'eld01.mp4' 'captive_portal'"
    exit 1
fi

# Obter timestamp atual do OPNsense no formato esperado pela API
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Fazer requisição POST com curl
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"video\":\"$VIDEO\",\"origin\":\"$ORIGIN\",\"timestamp\":\"$TIMESTAMP\"}" \
  --max-time 10 \
  --silent \
  --show-error

# Log local (opcional)
logger -t captive_portal "Video view registered: $USERNAME watched $VIDEO at $TIMESTAMP"
