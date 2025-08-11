# Guia: Diferenças Windows vs Linux para POPPFIRE API

## Principais Diferenças

### 1. Caminhos de Arquivo
- **Windows**: `C:\Projetos\Poppnet\sreadmin`
- **Linux**: `/var/www/sreadmin`

### 2. Permissões
- **Windows**: Não há conceito de owner/group como no Linux
- **Linux**: Precisa configurar `www-data:www-data` e permissões 755/775

### 3. Servidor Web
- **Windows**: Geralmente desenvolvimento com `python manage.py runserver`
- **Linux**: Produção com nginx/apache + systemd service

### 4. Endereços de Rede
- **Windows**: `127.0.0.1` ou `localhost`
- **Linux**: IP do servidor (ex: `172.18.25.253`)

### 5. Arquivo appliance_tokens.json
- **Windows**: Pode não existir, usa tokens do banco
- **Linux**: Precisa de permissões corretas se existir

## Configuração para Desenvolvimento (Windows)

```bash
# Instalar dependências
pip install -r requirements.txt

# Aplicar migrações
python manage.py migrate

# Criar tokens
python debug_multiplatform.py

# Iniciar servidor
python manage.py runserver 127.0.0.1:8000
```

## Configuração para Produção (Linux)

```bash
# Executar script de produção
./production_deploy.sh

# Ou configuração manual
python linux_production_setup.py
./setup_linux_production.sh
```

## URLs de Teste

### Windows (Desenvolvimento)
- API Info: `http://127.0.0.1:8000/api/appliances/info/`
- Admin: `http://127.0.0.1:8000/admin/`

### Linux (Produção)
- API Info: `http://SEU-IP:8000/api/appliances/info/`
- Admin: `http://SEU-IP:8000/admin/`

## Headers de Autenticação

```
Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0
Content-Type: application/json
```

## Troubleshooting

### Windows
- Verificar se o servidor está rodando
- Confirmar que não há firewall bloqueando
- Usar 127.0.0.1 em vez de 0.0.0.0

### Linux
- Verificar permissões de arquivos
- Confirmar que a porta 8000 está liberada
- Checar logs: `journalctl -u poppfire-django -f`
- Verificar nginx: `sudo nginx -t`

### Ambos
- Confirmar que o token existe no banco
- Verificar logs do Django
- Testar autenticação com script debug
