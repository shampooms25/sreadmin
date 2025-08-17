# Portal Captive Updater - OpenSense Integration

## Visão Geral

Sistema completo para sincronização automática do portal captive entre o servidor Django (172.18.25.253) e o OpenSense. O sistema monitora alterações no portal e atualiza automaticamente os arquivos no OpenSense.

## Arquitetura

```
Django Server (172.18.25.253:8000)
├── API Endpoints
│   ├── /api/captive-portal/status/      - Status e configuração
│   ├── /api/captive-portal/config/      - Configuração detalhada  
│   ├── /api/captive-portal/video/<id>/  - Download de vídeos
│   └── /api/captive-portal/zip/<id>/    - Download de arquivos ZIP
│
OpenSense
├── /root/portal/
│   ├── captive_updater.py               - Launcher (executa opnsense_captive_updater.py)
│   ├── opnsense_captive_updater.py      - Script principal
│   ├── venv/                            - Ambiente virtual (opcional)
│   └── logs/estado em /var/log e /var/db (ver abaixo)
```

## Instalação no OpenSense

### 1. Teste Inicial (Recomendado)

```bash
# Fazer upload do script de teste
scp test_opnsense_updater.sh root@<opnsense-ip>:/tmp/

# No OpenSense, executar teste
ssh root@<opnsense-ip>
chmod +x /tmp/test_opnsense_updater.sh
/tmp/test_opnsense_updater.sh
```

### 2. Instalação Completa

```bash
# Fazer upload dos scripts
scp install_opnsense_updater.sh root@<opnsense-ip>:/tmp/
scp opnsense_captive_updater.py root@<opnsense-ip>:/tmp/

# No OpenSense, executar instalação
ssh root@<opnsense-ip>
chmod +x /tmp/install_opnsense_updater.sh
/tmp/install_opnsense_updater.sh
```

## APIs Disponíveis

### 1. Status API
```bash
GET http://172.18.25.253:8000/api/captive-portal/status/
```
Retorna status geral e hash dos arquivos para verificação de mudanças.

### 2. Configuração API
```bash
GET http://172.18.25.253:8000/api/captive-portal/config/
```
Retorna configuração detalhada do portal ativo.

### 3. Download de Vídeo
```bash
GET http://172.18.25.253:8000/api/captive-portal/video/<video_id>/
```
Baixa arquivo de vídeo específico.

### 4. Download de ZIP
```bash
GET http://172.18.25.253:8000/api/captive-portal/zip/<portal_id>/
```
Baixa arquivo ZIP do portal específico.

## Comandos no OpenSense

### Verificar Status
```bash
/root/portal/status.sh
```

### Executar Manualmente
```bash
/root/portal/update_captive_portal.sh
```

### Ver Log em Tempo Real
```bash
tail -f /var/log/poppfire_portal_updater.log
```

### Alterar Frequência do Cron
```bash
crontab -e
# Ajuste recomendado: executar 1x/dia à meia-noite
# 0 0 * * * /root/portal/update_captive_portal.sh
```

## Funcionamento

1. **Verificação Automática**: O cron executa o script a cada 5 minutos
2. **Comparação de Hash**: Script compara hash local com hash do servidor
3. **Download Seletivo**: Baixa apenas arquivos que mudaram
4. **Backup Automático**: Faz backup antes de substituir arquivos
5. **Verificação de Integridade**: Valida hash dos arquivos baixados
6. **Restart de Serviços**: Reinicia serviços necessários após atualização

## Logs e Monitoramento

### Localização dos Logs
- **Principal**: `/var/log/poppfire_portal_updater.log`
- **Estado**: `/var/db/poppfire_portal_state.json`
- **Lock**: `/tmp/captive_updater.lock` (temporário)

### Estrutura do Log
```
[2024-01-20 10:30:00] Verificando atualizações...
[2024-01-20 10:30:01] Hash atual: abc123...
[2024-01-20 10:30:01] Hash servidor: def456...
[2024-01-20 10:30:01] Mudanças detectadas - iniciando download
[2024-01-20 10:30:05] ✓ Video baixado: video1.mp4
[2024-01-20 10:30:10] ✓ ZIP baixado: portal.zip
[2024-01-20 10:30:15] ✓ Serviços reiniciados
[2024-01-20 10:30:15] Atualização concluída
```

## Troubleshooting

### Problema: API não acessível
```bash
# Verificar conectividade
ping 172.18.25.253

# Testar porta
telnet 172.18.25.253 8000

# Testar API diretamente
curl http://172.18.25.253:8000/api/captive-portal/status/
```

### Problema: Script não executa
```bash
# Verificar permissões
ls -la /root/portal/

# Verificar Python
python3 --version

# Executar com debug
python3 -u /root/portal/captive_updater.py
```

### Problema: Downloads falham
```bash
# Verificar espaço em disco
df -h

# Verificar permissões de escrita
touch /usr/local/captiveportal/test.txt

# Verificar conectividade específica
curl -I http://172.18.25.253:8000/api/captive-portal/video/1/
```

## Configuração Avançada

### Alterar Diretórios
Editar `/root/portal/opnsense_captive_updater.py`:
```python
self.captive_dir = "/seu/diretorio/customizado"
self.videos_dir = "/seu/diretorio/videos"
```

### Alterar Servidor
```python
self.server_url = "http://seu-servidor:porta"
```

### Customizar Timeout
```python
response = requests.get(url, timeout=30)  # 30 segundos
```

## Segurança

- Script executa como root (necessário para restart de serviços)
- Lock file previne execuções simultâneas
- Backup automático antes de substituir arquivos
- Verificação de integridade por hash
- Logs detalhados para auditoria

## Manutenção

### Backup Manual
```bash
cp -r /usr/local/captiveportal /backup/captiveportal-$(date +%Y%m%d)
```

### Limpeza de Logs
```bash
# Log rotation automático configurado
# Para limpeza manual:
> /var/log/captive_portal_updater.log
```

### Atualização do Script
```bash
# Backup do script atual
cp /root/portal/opnsense_captive_updater.py /backup/

# Substituir por nova versão
# Depois reiniciar cron se necessário
```
