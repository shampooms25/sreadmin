# 🔐 AUTENTICAÇÃO GIT NO SERVIDOR - GUIA COMPLETO

## 🚨 PROBLEMA ATUAL
```
remote: Invalid username or token. Password authentication is not supported for Git operations.
fatal: Authentication failed
```

O GitHub **não aceita mais senhas normais** desde 2021. Você precisa de um **Personal Access Token (PAT)**.

## 🎯 SOLUÇÕES DISPONÍVEIS

### 1. PERSONAL ACCESS TOKEN (RECOMENDADO) ⭐

#### Passo 1: Criar o Token
1. Acesse: https://github.com/settings/tokens
2. Clique em **Generate new token** → **Generate new token (classic)**
3. Configure:
   - **Note:** `Production Server Access`
   - **Expiration:** `90 days` (ou No expiration)
   - **Scopes:** ✅ **repo** (full control of private repositories)
4. Clique em **Generate token**
5. **COPIE O TOKEN** (só aparece uma vez!)

#### Passo 2: Configurar no Servidor
```bash
cd /var/www/sreadmin

# Configurar credential helper
git config --global credential.helper store

# Fazer push (será solicitado credenciais)
git push origin main
# Username: shampooms25
# Password: [COLE_SEU_TOKEN_AQUI]
```

#### Passo 3: Verificar
```bash
# Testar se funcionou
git push origin main
# Não deve pedir credenciais novamente
```

### 2. SSH KEY (ALTERNATIVA)

#### Gerar chave SSH no servidor:
```bash
ssh-keygen -t rsa -b 4096 -C "production-server@sreadmin"
cat ~/.ssh/id_rsa.pub
```

#### Adicionar no GitHub:
1. Copie a chave SSH gerada
2. Acesse: https://github.com/settings/ssh/new  
3. Title: `Production Server`
4. Cole a chave SSH
5. Clique em **Add SSH key**

#### Alterar remote para SSH:
```bash
cd /var/www/sreadmin
git remote set-url origin git@github.com:shampooms25/sreadmin.git
git push origin main
```

## 🚀 SCRIPT AUTOMATIZADO

Execute no servidor:
```bash
cd /var/www/sreadmin
chmod +x setup_git_auth.sh
./setup_git_auth.sh
```

## ⚡ SOLUÇÃO RÁPIDA (30 SEGUNDOS)

1. **Gere o token:** https://github.com/settings/tokens
2. **Execute no servidor:**
```bash
cd /var/www/sreadmin
git config --global credential.helper store
git push origin main
# Username: shampooms25  
# Password: [SEU_TOKEN_AQUI]
```

3. **Pronto!** Próximos pushes não pedirão credenciais.

## 🔒 SEGURANÇA

- ✅ **Token tem escopo limitado** (apenas repo)
- ✅ **Token pode ser revogado** a qualquer momento
- ✅ **Expira automaticamente** (se configurado)
- ✅ **Mais seguro** que senhas

## 🧪 TESTAR AUTENTICAÇÃO

```bash
# Verificar configuração
git config --list | grep credential

# Testar conexão
git ls-remote origin

# Ver remotes
git remote -v
```

**Qual método prefere? Token (mais fácil) ou SSH (mais seguro)?**
