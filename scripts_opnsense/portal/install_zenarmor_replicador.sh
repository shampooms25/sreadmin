#!/bin/sh

echo "🔧 Iniciando instalação do replicador Zenarmor..."

# ✅ Verificar se Python 3 está instalado
if ! command -v /usr/local/bin/python3 >/dev/null 2>&1; then
  echo "❌ Python 3 não encontrado em /usr/local/bin/python3"
  echo "   Verifique se o Python está instalado e disponível nesse caminho."
  exit 1
fi

# ✅ Verificar se módulo requests está disponível
echo "🔍 Verificando dependência Python: requests..."
if ! /usr/local/bin/python3 -c "import requests" >/dev/null 2>&1; then
  echo "❌ Módulo Python 'requests' não encontrado."
  echo "   Você pode instalar com:"
  echo "     /usr/local/bin/python3 -m pip install requests"
  exit 1
fi

# 📦 Extrair pacote
echo "📦 Extraindo pacote..."
unzip replicador_zenarmor.zip || {
  echo "❌ Erro ao extrair o pacote."
  exit 1
}


# 📁 Instalar script
echo "📁 Instalando script em /usr/local/etc/zenarmor/"
mkdir -p /usr/local/etc/zenarmor
cp zenarmor_replicador/replicador.py /usr/local/etc/zenarmor/
chmod +x /usr/local/etc/zenarmor/replicador.py

# 🛠️ Instalar script de serviço
echo "🛠️ Instalando serviço em /usr/local/etc/rc.d/replicador"
cp zenarmor_replicador/rc.d/replicador /usr/local/etc/rc.d/
chmod +x /usr/local/etc/rc.d/replicador

# 🧩 Ativar no rc.conf
if ! grep -q '^replicador_enable="YES"' /etc/rc.conf; then
  echo 'replicador_enable="YES"' >> /etc/rc.conf
  echo "✅ Adicionado replicador_enable ao rc.conf"
else
  echo "ℹ️  replicador já estava ativado em /etc/rc.conf"
fi

# 📡 Criar template do Data Stream para este host
ES_HOST="http://172.18.25.252:9200"  # <-- Substitua pelo IP ou host real do ES
HOSTNAME=$(hostname -f)
INDEX_NAME="zenarmor-${HOSTNAME}-conn"
TEMPLATE_NAME="zenarmor-ds-${HOSTNAME}"

echo "🧱 Criando template do Data Stream: ${TEMPLATE_NAME} para o host ${HOSTNAME}..."

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
  \"priority\": 101
}" && echo "✅ Template criado para ${INDEX_NAME} com sucesso!"

# 🚀 Iniciar serviço
echo "🚀 Iniciando o serviço replicador..."
service replicador start

echo "✅ Instalação concluída com sucesso!"