#!/bin/sh

# Lista de serviços a monitorar (separados por espaço)
SERVICOS="replicador nginx sshd"

# Instala o agente Zabbix, se necessário
#pkg info | grep -q zabbix-agent || pkg install -y zabbix-agent

# Cria diretório para scripts
#mkdir -p /usr/local/etc/zabbix7/scripts

# Cria o script de status dos serviços
cat << 'EOF' > /usr/local/etc/zabbix7/scripts/service_status.sh
#!/bin/sh
sudo /usr/sbin/service "$1" status >/dev/null 2>&1
if [ $? -eq 0 ]; then
  echo 1
else
  echo 0
fi
EOF

chmod +x /usr/local/etc/zabbix7/scripts/service_status.sh

# Adiciona linha no zabbix_agentd.conf
#grep -q 'service.status[*]' /usr/local/etc/zabbix_agentd.conf || echo 'UserParameter=service.status[*],/usr/local/etc/zabbix7/scripts/service_status.sh $1' >> /usr/local/etc/zabbix_agentd.conf

# Adiciona permissões no sudoers para cada serviço
for SVC in $SERVICOS; do
  echo "zabbix ALL=(ALL) NOPASSWD: /usr/sbin/service $SVC status" >> /usr/local/etc/sudoers.d/zabbix_$SVC
  chmod 0440 /usr/local/etc/sudoers.d/zabbix_$SVC
  chown root:wheel /usr/local/etc/sudoers.d/zabbix_$SVC

done

# Reinicia o agente Zabbix com segurança
pkill -f zabbix_agentd
sleep 2
/usr/local/sbin/zabbix_agentd -c /usr/local/etc/zabbix_agentd.conf

