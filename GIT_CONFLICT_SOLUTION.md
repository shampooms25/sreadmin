# 🚨 RESOLUÇÃO IMEDIATA - Conflito Git Produção

## ❌ Problema
```
error: Your local changes to the following files would be overwritten by merge:
        production_deploy.sh
Please commit your changes or stash them before you merge.
```

## ✅ SOLUÇÃO RÁPIDA (Execute no servidor)

### 🔧 Passo 1: Backup e Resolução
```bash
cd /var/www/sreadmin

# Fazer backup do arquivo em conflito
cp production_deploy.sh production_deploy_backup_$(date +%Y%m%d_%H%M%S).sh

# Descartar mudanças locais
git checkout -- production_deploy.sh

# Fazer pull das atualizações
git pull origin main
```

### 🔧 Passo 2: Verificar Scripts Baixados
```bash
# Verificar se os scripts de correção foram baixados
ls -la *fix*.sh
ls -la emergency*.sh
ls -la production_deploy_fixed.sh

# Dar permissão de execução
chmod +x fix_on_conflict_error.sh
chmod +x production_deploy_fixed.sh
chmod +x emergency_table_fix.sh
```

### 🔧 Passo 3: EXECUTAR CORREÇÃO DO ERRO 500
```bash
# OPÇÃO 1: Correção específica do ON CONFLICT
./fix_on_conflict_error.sh

# OU OPÇÃO 2: Deploy corrigido completo
./production_deploy_fixed.sh

# OU OPÇÃO 3: Correção emergencial
./emergency_table_fix.sh
```

## 🚀 COMANDOS COMPLETOS (Copie e Cole)

```bash
# Execute tudo de uma vez:
cd /var/www/sreadmin
cp production_deploy.sh production_deploy_backup_$(date +%Y%m%d_%H%M%S).sh
git checkout -- production_deploy.sh
git pull origin main
chmod +x *.sh
./fix_on_conflict_error.sh
```

## 🧪 Verificação
```bash
# Testar se o erro 500 foi corrigido:
curl -H "Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0" \
     http://127.0.0.1:8000/api/appliances/info/
```

## ⚠️ Se Ainda Não Funcionar
```bash
# Force pull completo:
git reset --hard HEAD
git pull origin main --force
chmod +x *.sh
./fix_on_conflict_error.sh
```

## 📋 Status Esperado Após Correção
- ✅ Git pull funcionando
- ✅ Scripts de correção disponíveis
- ✅ Erro 500 resolvido
- ✅ API respondendo status 200

---
**Execute os comandos acima e o problema será resolvido em 2 minutos!**
