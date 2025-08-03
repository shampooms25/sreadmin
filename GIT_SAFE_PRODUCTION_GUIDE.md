# 🚨 PROBLEMAS COM ALTERAÇÕES DIRETAS NO SERVIDOR

## ❌ O que acontece se você modificar arquivos versionados:

1. **Conflitos no git pull:**
   ```bash
   error: Your local changes to the following files would be overwritten by merge:
       painel/models.py
       sreadmin/settings.py
   Please commit your changes or stash them before you merge.
   ```

2. **Perda de alterações:**
   - `git pull` pode sobrescrever suas correções
   - Suas modificações podem ser perdidas

3. **Inconsistência entre dev/prod:**
   - Código diferente entre desenvolvimento e produção
   - Bugs difíceis de reproduzir

## ✅ SOLUÇÃO SEGURA - SEM CONFLITO GIT

### Opção 1: local_settings.py (RECOMENDADO)
- **Arquivo:** `production_safe_fix.py` (criado agora)
- **Vantagem:** ZERO conflito com Git
- **Como funciona:**
  1. Cria `local_settings.py` (não versionado)
  2. Modifica apenas `wsgi.py` para usar local_settings
  3. Todas as configurações específicas ficam separadas

### Opção 2: Variáveis de ambiente
```bash
# No servidor
export DJANGO_SETTINGS_MODULE=sreadmin.production_settings
export MEDIA_ROOT=/var/www/sreadmin/media
```

### Opção 3: Branch específica para produção
```bash
# Criar branch apenas para produção
git checkout -b production
# Fazer alterações específicas
git add -A && git commit -m "Production specific changes"
# Para atualizar: merge da main
git merge main
```

## 🛡️ COMO USAR A SOLUÇÃO SEGURA

### 1. Executar correção segura:
```bash
cd /var/www/sreadmin
python3 production_safe_fix.py
sudo systemctl restart apache2
```

### 2. Para git pull futuro:
```bash
# OPÇÃO A: Não precisa fazer nada (arquivos não versionados)
git pull origin main

# OPÇÃO B: Se wsgi.py foi modificado:
git stash
git pull origin main
git stash pop
```

### 3. Para reverter se necessário:
```bash
./revert_safe_fix.sh
```

## 📁 ESTRUTURA APÓS CORREÇÃO SEGURA

```
/var/www/sreadmin/
├── sreadmin/
│   ├── settings.py          # Original (versionado)
│   ├── local_settings.py    # Específico produção (NÃO versionado)
│   └── wsgi.py             # Modificado para usar local_settings
├── .gitignore              # Atualizado
└── media/videos/eld/       # Criado com permissões
```

## 🔄 WORKFLOW RECOMENDADO

1. **Desenvolvimento:** Use `settings.py` normal
2. **Produção:** Use `local_settings.py` (herda de settings.py)
3. **Deploy:** `git pull` + restart Apache
4. **Configurações específicas:** Só no `local_settings.py`

## ⚡ EXECUÇÃO IMEDIATA

Execute agora mesmo:
```bash
cd /var/www/sreadmin
python3 production_safe_fix.py
```

Esta solução garante:
- ✅ Zero conflito com Git
- ✅ `git pull` funciona normalmente  
- ✅ Configurações específicas isoladas
- ✅ Fácil de reverter
- ✅ Não afeta desenvolvimento
