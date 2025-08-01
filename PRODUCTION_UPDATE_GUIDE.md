# 🚀 GUIA DE ATUALIZAÇÃO PASSO A PASSO - SERVIDOR DE PRODUÇÃO

## 📋 Pré-requisitos

Antes de executar a atualização, certifique-se de que:

- [ ] Você tem acesso ao servidor de produção
- [ ] O ambiente virtual está configurado
- [ ] Há backup recente do banco de dados
- [ ] Os serviços podem ser interrompidos temporariamente

## 🔧 MÉTODO 1: Automático (Recomendado)

### 1. Executar Deploy no Desenvolvimento
```powershell
# No ambiente de desenvolvimento, execute:
.\deploy_updates.ps1
```

### 2. Executar Atualização na Produção
```powershell
# No servidor de produção, execute:
.\production_update.ps1
```

---

## 🛠️ MÉTODO 2: Manual (Passo a Passo)

### No Servidor de Produção:

#### 1. Preparação
```powershell
# Navegar para o diretório do projeto
cd C:\caminho\para\seu\projeto\sreadmin

# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Verificar status atual
git status
```

#### 2. Backup (IMPORTANTE!)
```powershell
# Fazer backup do banco de dados PostgreSQL
pg_dump -h localhost -U seu_usuario -d nome_banco > backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql

# Ou usar comando específico do seu ambiente
python manage.py dumpdata > backup_data_$(Get-Date -Format 'yyyyMMdd_HHmmss').json
```

#### 3. Atualizar Código
```powershell
# Salvar alterações locais (se houver)
git stash push -m "Backup antes do deploy"

# Baixar atualizações
git fetch origin
git pull origin main
```

#### 4. Verificar Migrações
```powershell
# Ver migrações pendentes
python manage.py showmigrations

# Verificar migrações específicas
python manage.py showmigrations painel
```

#### 5. Aplicar Migrações
```powershell
# ATENÇÃO: Sempre fazer backup antes das migrações!

# Aplicar migrações
python manage.py migrate

# Verificar se aplicou corretamente
python manage.py showmigrations painel
```

#### 6. Atualizar Dependências
```powershell
# Instalar/atualizar bibliotecas
pip install -r requirements.txt

# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

#### 7. Verificar Sistema
```powershell
# Verificar configuração
python manage.py check --deploy

# Teste rápido do modelo corrigido
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()
from painel.models import EldGerenciarPortal
print('✅ Modelo funcionando!')
print(f'Registros: {EldGerenciarPortal.objects.count()}')
"
```

#### 8. Reiniciar Serviços
```powershell
# Reiniciar servidor web (Apache/Nginx/IIS)
# Exemplo para IIS:
iisreset

# Ou reiniciar serviço específico:
# Restart-Service "NomeDoServiço"
```

---

## 🚨 MIGRAÇÕES ESPECÍFICAS DESTA ATUALIZAÇÃO

### Importante: Esta atualização inclui correção crítica!

**Migração**: `painel/migrations/0008_auto_20250801_1339.py`
**Objetivo**: Recriar tabela `eld_gerenciar_portal` que foi removida incorretamente

**O que a migração faz:**
```sql
CREATE TABLE IF NOT EXISTS eld_gerenciar_portal (
    id SERIAL PRIMARY KEY,
    ativar_video BOOLEAN NOT NULL DEFAULT FALSE,
    nome_video_id INTEGER,
    captive_portal_zip VARCHAR(100),
    data_criacao TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    data_atualizacao TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);
```

---

## ✅ CHECKLIST PÓS-ATUALIZAÇÃO

Após a atualização, verifique:

- [ ] Sistema carrega sem erros
- [ ] Admin panel acessível em `/admin/`
- [ ] Modelo `EldGerenciarPortal` visível no admin
- [ ] Não há erros 500 nos logs
- [ ] API Starlink funcionando (se aplicável)
- [ ] Portal captivo operacional

### Comandos de Verificação:
```powershell
# Verificar logs de erro (ajuste o caminho)
Get-Content "C:\logs\django.log" -Tail 50

# Testar acesso ao admin
curl http://localhost:8000/admin/

# Verificar modelo no shell
python manage.py shell -c "from painel.models import EldGerenciarPortal; print('OK')"
```

---

## 🆘 RESOLUÇÃO DE PROBLEMAS

### Erro durante migração:
```powershell
# Se a migração falhar, reverta e tente novamente
python manage.py migrate painel 0007
python manage.py migrate painel 0008
```

### Erro de tabela ainda não existe:
```powershell
# Execute SQL diretamente no banco
python manage.py dbshell
# Cole o SQL da migração manualmente
```

### Erro de importação:
```powershell
# Reinstalar dependências
pip install --force-reinstall -r requirements.txt
```

---

## 📞 SUPORTE

Em caso de problemas:

1. **Verificar logs:** Sempre consulte os logs do Django e do servidor web
2. **Restaurar backup:** Se necessário, use o backup feito antes da atualização
3. **Contato:** Documente o erro e contexto para suporte técnico

---

**⚠️ IMPORTANTE:** 
- Sempre faça backup antes de atualizações
- Teste em ambiente de desenvolvimento primeiro
- Mantenha uma janela de manutenção programada
- Tenha plano de rollback preparado
