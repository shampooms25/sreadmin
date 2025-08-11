# 🚨 SOLUÇÃO DEFINITIVA - Erro 500 Produção

## ❌ Problema Identificado
```
ERRO: relation "eld_gerenciar_portal" does not exist
STATUS: 500 Internal Server Error
LOCAL: Produção Ubuntu (/var/www/sreadmin)
```

## ✅ Soluções Disponíveis

### 🔥 OPÇÃO 1: Script Bash Completo (RECOMENDADO)
```bash
# No servidor de produção:
cd /var/www/sreadmin
chmod +x emergency_table_fix.sh
sudo ./emergency_table_fix.sh
```

### 🔥 OPÇÃO 2: Script Python Independente
```bash
# No servidor de produção:
cd /var/www/sreadmin
python emergency_fix.py
```

### 🔥 OPÇÃO 3: Script Completo com Backup
```bash
# Script com backup completo:
cd /var/www/sreadmin
chmod +x safe_db_update.sh
sudo ./safe_db_update.sh
```

### 🔥 OPÇÃO 4: Correção Manual Direta
```bash
# Acesso direto ao Django shell:
cd /var/www/sreadmin
python manage.py shell
```

```python
# Dentro do shell Django:
from django.db import connection

with connection.cursor() as cursor:
    # Criar eld_gerenciar_portal
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eld_gerenciar_portal (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(200) NOT NULL,
            ativo BOOLEAN NOT NULL DEFAULT false,
            captive_portal_zip VARCHAR(100),
            video_file VARCHAR(100),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)
    
    # Criar eld_portal_sem_video
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eld_portal_sem_video (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(200) NOT NULL,
            ativo BOOLEAN NOT NULL DEFAULT false,
            arquivo_zip VARCHAR(100),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)
    
    print("✅ Tabelas criadas!")

# Sair do shell
exit()

# Reiniciar servidor
sudo systemctl reload apache2  # ou nginx
python manage.py runserver 0.0.0.0:8000
```

## 🧪 Verificação da Correção

### 1. Testar Tabelas
```bash
python manage.py shell -c "
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT COUNT(*) FROM eld_gerenciar_portal;')
    print('eld_gerenciar_portal:', cursor.fetchone()[0])
    cursor.execute('SELECT COUNT(*) FROM eld_portal_sem_video;')
    print('eld_portal_sem_video:', cursor.fetchone()[0])
"
```

### 2. Testar API
```bash
curl -H "Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0" \
     http://127.0.0.1:8000/api/appliances/info/
```

### 3. Verificar Logs
```bash
# Logs do Django
tail -f emergency_fix.log

# Logs do Apache
tail -f /var/log/apache2/error.log

# Logs do Nginx
tail -f /var/log/nginx/error.log
```

## 🔍 Diagnóstico Avançado

### Verificar Estado do Banco
```bash
python manage.py dbshell -c "\dt"  # Listar tabelas
python manage.py showmigrations    # Ver migrações
python manage.py migrate --plan    # Ver plano de migração
```

### Verificar Servidor
```bash
# Processos ativos
ps aux | grep python
ps aux | grep apache
ps aux | grep nginx

# Portas ocupadas
netstat -tlnp | grep :8000
netstat -tlnp | grep :80
```

## 🛠️ Scripts Criados

| Script | Finalidade | Execução |
|--------|------------|----------|
| `emergency_table_fix.sh` | Correção rápida completa | `sudo ./emergency_table_fix.sh` |
| `emergency_fix.py` | Correção Python independente | `python emergency_fix.py` |
| `safe_db_update.sh` | Correção com backup completo | `sudo ./safe_db_update.sh` |
| `diagnose_production.sh` | Diagnóstico completo | `./diagnose_production.sh` |

## 🔑 Tokens de Teste

### Token Principal
```
Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0
```

### URLs de Teste
```
http://SEU_IP:8000/api/appliances/info/
http://SEU_IP:8000/admin/
http://SEU_IP/api/appliances/info/  (produção)
```

## 📋 Checklist Pós-Correção

- [ ] Tabelas `eld_gerenciar_portal` e `eld_portal_sem_video` criadas
- [ ] Migrações marcadas como aplicadas
- [ ] Servidor web reiniciado (Apache/Nginx)
- [ ] API respondendo status 200
- [ ] Admin Django acessível
- [ ] Logs sem erros 500
- [ ] Token de autenticação funcionando

## 🚀 Próximos Passos

1. **Executar um dos scripts de correção**
2. **Verificar se API retorna status 200**
3. **Testar funcionalidades no admin**
4. **Monitorar logs por algumas horas**
5. **Documentar ambiente para evitar recorrência**

## ⚠️ Prevenção

Para evitar este problema no futuro:

1. **Sempre executar migrações em produção:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Verificar tabelas antes do deploy:**
   ```bash
   python manage.py showmigrations
   ```

3. **Backup automático:**
   ```bash
   pg_dump nome_do_banco > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

---

**Status:** 🟢 Soluções prontas para execução
**Prioridade:** 🔥 CRÍTICA - Resolver imediatamente
**Tempo estimado:** ⏱️ 5-10 minutos
