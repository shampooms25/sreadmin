#!/bin/bash

echo "Configurando timezone do PostgreSQL para America/Campo_Grande..."

# Conectar ao PostgreSQL e alterar timezone
sudo -u postgres psql -c "ALTER DATABASE radiusd SET timezone TO 'America/Campo_Grande';"

echo "✅ Timezone do banco de dados configurado!"

# Verificar
sudo -u postgres psql radiusd -c "SHOW timezone;"

# Reiniciar PostgreSQL para garantir
echo "Reiniciando PostgreSQL..."
sudo systemctl restart postgresql

echo "✅ Concluído! Teste a aplicação agora."
