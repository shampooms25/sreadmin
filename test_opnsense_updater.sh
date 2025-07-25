#!/bin/sh
#
# Script Simplificado para Teste do Portal Captive Updater
# Execute este primeiro para testar a funcionalidade
#

echo "=== Teste do Portal Captive Updater ==="
echo ""

# Verificar Python3
if ! command -v python3 > /dev/null 2>&1; then
    echo "Instalando Python3..."
    pkg install -y python3
fi

# Verificar curl
if ! command -v curl > /dev/null 2>&1; then
    echo "Instalando curl..."
    pkg install -y curl
fi

# Criar diretório temporário para teste
TEST_DIR="/tmp/captive_test"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# Baixar o script updater
echo "Baixando script updater..."
if curl -s "http://172.18.25.253:8000/static/scripts/opnsense_captive_updater.py" -o "captive_updater.py"; then
    echo "✓ Script baixado com sucesso"
else
    echo "✗ Erro ao baixar script"
    echo "Criando script local..."
    
    # Criar script local para teste
    cat > "captive_updater.py" << 'EOF'
#!/usr/bin/env python3
import json
import requests
import os
import hashlib
import time
from datetime import datetime

class CaptivePortalUpdater:
    def __init__(self):
        self.server_url = "http://172.18.25.253:8000"
        self.api_base = f"{self.server_url}/api/captive-portal"
        self.captive_dir = "/tmp/captive_test"
        self.state_file = os.path.join(self.captive_dir, "update_state.json")
        
        os.makedirs(self.captive_dir, exist_ok=True)
    
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_state(self, state):
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def check_updates(self):
        try:
            self.log("Verificando atualizações...")
            response = requests.get(f"{self.api_base}/status/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Status do servidor: {data.get('status', 'unknown')}")
                return data
            else:
                self.log(f"Erro na API: {response.status_code}")
                return None
                
        except Exception as e:
            self.log(f"Erro ao verificar atualizações: {e}")
            return None
    
    def run(self):
        self.log("=== Iniciando teste do Captive Portal Updater ===")
        
        # Verificar conectividade
        self.log("Testando conectividade...")
        status = self.check_updates()
        
        if status:
            self.log("✓ Conectividade OK")
            self.log(f"Dados recebidos: {json.dumps(status, indent=2)}")
        else:
            self.log("✗ Erro de conectividade")
            return False
        
        self.log("=== Teste concluído ===")
        return True

if __name__ == "__main__":
    updater = CaptivePortalUpdater()
    updater.run()
EOF
fi

chmod +x captive_updater.py

echo ""
echo "Executando teste..."
python3 captive_updater.py

echo ""
echo "=== Teste Concluído ==="
echo "Arquivos em: $TEST_DIR"
echo ""
echo "Se o teste funcionou, execute install_opnsense_updater.sh para instalação completa"
