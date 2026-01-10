#!/bin/sh

echo ">>> Configurando script de inicializacao (Boot Hook)..."

# O diretório rc.syshook.d/start contém scripts que rodam no final do boot
mkdir -p /usr/local/etc/rc.syshook.d/start

# Criar o script que força a atualização ao ligar
cat <<EOF > /usr/local/etc/rc.syshook.d/start/99-poppfire-portal
#!/bin/sh
# Poppfire Portal Restore on Boot
# Garante que o layout customizado seja aplicado mesmo se o OPNsense restaurar o default

echo "[\$(date)] Poppfire: Restaurando portal customizado no boot..." >> /var/log/poppfire_boot.log
/root/portal/venv/bin/python3 /root/portal/install_opnsense_updater.py --force >> /var/log/poppfire_boot.log 2>&1
EOF

# Tornar executável
chmod +x /usr/local/etc/rc.syshook.d/start/99-poppfire-portal

echo ">>> Sucesso! O script de boot foi criado em: /usr/local/etc/rc.syshook.d/start/99-poppfire-portal"
echo ">>> O portal sera corrigido automaticamente toda vez que o servidor reiniciar."
