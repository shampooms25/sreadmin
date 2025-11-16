#!/bin/bash

echo "Limpando cache do servidor..."

cd /var/www/sreadmin

# Parar Apache
echo "Parando Apache..."
sudo systemctl stop apache2

# Limpar cache Python
echo "Limpando __pycache__..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# Git pull
echo "Atualizando código..."
git pull

# Tocar WSGI
echo "Atualizando WSGI..."
touch sreadmin/wsgi.py

# Reiniciar Apache
echo "Reiniciando Apache..."
sudo systemctl start apache2

# Verificar status
sudo systemctl status apache2 --no-pager

echo "✅ Concluído! Teste a aplicação agora."
