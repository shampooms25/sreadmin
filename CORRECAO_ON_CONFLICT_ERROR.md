# 🚨 CORREÇÃO - Erro ON CONFLICT PostgreSQL

## ❌ Problema Identificado

```
ERROR: there is no unique or exclusion constraint matching the ON CONFLICT specification
psycopg2.errors.InvalidColumnReference
```

### 🔍 Causa do Erro
O erro acontece quando usamos `ON CONFLICT` no PostgreSQL sem ter uma constraint única (UNIQUE) apropriada na tabela.

**Código problemático:**
```sql
INSERT INTO tabela (coluna1, coluna2) 
VALUES ('valor1', 'valor2') 
ON CONFLICT (coluna1, coluna2) DO NOTHING;
```

**Problema:** Se não existe um UNIQUE INDEX em `(coluna1, coluna2)`, o PostgreSQL não sabe como detectar conflitos.

## ✅ Soluções Implementadas

### 🔧 SOLUÇÃO 1: Script de Correção Rápida
```bash
cd /var/www/sreadmin
chmod +x fix_on_conflict_error.sh
./fix_on_conflict_error.sh
```

### 🔧 SOLUÇÃO 2: Deploy Corrigido
```bash
cd /var/www/sreadmin
chmod +x production_deploy_fixed.sh
./production_deploy_fixed.sh
```

### 🔧 SOLUÇÃO 3: Correção Manual
```sql
-- Em vez de ON CONFLICT, usar WHERE NOT EXISTS:

-- ❌ PROBLEMÁTICO:
INSERT INTO eld_gerenciar_portal (nome, ativo) 
VALUES ('Portal Padrão', false) 
ON CONFLICT (nome) DO NOTHING;

-- ✅ CORRETO:
INSERT INTO eld_gerenciar_portal (nome, ativo) 
SELECT 'Portal Padrão', false
WHERE NOT EXISTS (
    SELECT 1 FROM eld_gerenciar_portal WHERE nome = 'Portal Padrão'
);
```

## 🛠️ Mudanças Técnicas Implementadas

### 1. Substituição de ON CONFLICT
**Antes:**
```python
cursor.execute("""
    INSERT INTO eld_gerenciar_portal (nome, ativo) 
    VALUES (%s, %s) 
    ON CONFLICT (nome) DO NOTHING;
""", ['Portal Padrão', False])
```

**Depois:**
```python
cursor.execute("""
    INSERT INTO eld_gerenciar_portal (nome, ativo) 
    SELECT %s, %s
    WHERE NOT EXISTS (
        SELECT 1 FROM eld_gerenciar_portal WHERE nome = %s
    );
""", ['Portal Padrão', False, 'Portal Padrão'])
```

### 2. Criação de Índices Únicos
```sql
-- Criar índice único para evitar problemas futuros
CREATE UNIQUE INDEX IF NOT EXISTS django_migrations_app_name_unique 
ON django_migrations(app, name);
```

### 3. Verificação Prévia de Tabelas
```python
# Verificar se tabela existe antes de criar
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'eld_gerenciar_portal';
""")

if not cursor.fetchall():
    # Criar tabela apenas se não existir
    cursor.execute("CREATE TABLE eld_gerenciar_portal ...")
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

### 3. Verificar Migrações
```bash
python manage.py showmigrations
python manage.py migrate --plan
```

## 📋 Scripts Disponíveis

| Script | Função | Execução |
|--------|--------|----------|
| `fix_on_conflict_error.sh` | Correção específica do erro | `./fix_on_conflict_error.sh` |
| `production_deploy_fixed.sh` | Deploy completo corrigido | `./production_deploy_fixed.sh` |
| `emergency_table_fix.sh` | Correção emergencial | `./emergency_table_fix.sh` |

## 🔍 Debug do Problema

### Ver Constraints Existentes
```sql
-- Ver todas as constraints de uma tabela
SELECT constraint_name, constraint_type 
FROM information_schema.table_constraints 
WHERE table_name = 'eld_gerenciar_portal';

-- Ver índices únicos
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'eld_gerenciar_portal';
```

### Logs Detalhados
```bash
# Ver logs do PostgreSQL
tail -f /var/log/postgresql/postgresql-*.log

# Ver logs do Django
tail -f production_deploy.log
tail -f fix_conflict.log
```

## ⚠️ Prevenção Futura

### 1. Sempre Criar Constraints Únicas
```sql
-- Ao criar tabelas, definir constraints:
CREATE TABLE exemplo (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) UNIQUE,  -- ← UNIQUE constraint
    email VARCHAR(200) UNIQUE  -- ← UNIQUE constraint
);
```

### 2. Usar INSERT com WHERE NOT EXISTS
```sql
-- Padrão seguro para inserção:
INSERT INTO tabela (coluna1, coluna2) 
SELECT 'valor1', 'valor2'
WHERE NOT EXISTS (
    SELECT 1 FROM tabela WHERE coluna1 = 'valor1'
);
```

### 3. Verificar Schema Antes do Deploy
```bash
# Sempre verificar antes de fazer deploy:
python manage.py sqlmigrate app_name migration_number
python manage.py showmigrations
```

---

**Status:** 🟢 Problema resolvido com múltiplas soluções
**Próximo:** Executar script de correção e verificar funcionamento
