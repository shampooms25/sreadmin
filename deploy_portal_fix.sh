#!/bin/bash
echo "=== Correção de Caminhos de Portal - Produção ==="
echo "Executando em $(date)"

# Navegar para diretório do projeto
cd /var/www/sreadmin

# Ativar ambiente virtual se existir
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Ambiente virtual ativado"
fi

# Executar script de correção
echo "🔧 Executando correção de caminhos..."
python fix_portal_paths_production.py

# Verificar se houve erro
if [ $? -eq 0 ]; then
    echo "✅ Correção concluída com sucesso"
    
    # Reiniciar serviços se necessário
    echo "🔄 Reiniciando serviços..."
    
    # Apache/Nginx
    if systemctl is-active --quiet apache2; then
        sudo systemctl reload apache2
        echo "✅ Apache recarregado"
    fi
    
    if systemctl is-active --quiet nginx; then
        sudo systemctl reload nginx
        echo "✅ Nginx recarregado"
    fi
    
    # Django se usando Gunicorn
    if systemctl is-active --quiet gunicorn; then
        sudo systemctl restart gunicorn
        echo "✅ Gunicorn reiniciado"
    fi
    
    echo "🎉 Deploy da correção concluído!"
else
    echo "❌ Erro durante a correção"
    exit 1
fi
