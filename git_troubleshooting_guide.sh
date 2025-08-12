#!/bin/bash
# Guia Completo para Resolver Problemas Git no Servidor

echo "🔧 GUIA GIT - Resolver arquivos não atualizando"
echo "==============================================="

echo ""
echo "🎯 DIAGNÓSTICO RÁPIDO:"
echo "====================="

# 1. Verificar status
echo "1️⃣  git status"
echo "2️⃣  git branch"
echo "3️⃣  git remote -v"
echo "4️⃣  git log --oneline -3"

echo ""
echo "🚨 PROBLEMAS MAIS COMUNS:"
echo "========================="

echo ""
echo "❌ PROBLEMA 1: Arquivos não commitados localmente"
echo "SOLUÇÃO:"
echo "git add ."
echo "git commit -m \"Add correction scripts\""
echo "git push origin main"

echo ""
echo "❌ PROBLEMA 2: Remote não configurado ou incorreto"
echo "SOLUÇÃO:"
echo "git remote add origin https://github.com/shampooms25/sreadmin.git"
echo "# ou"
echo "git remote set-url origin https://github.com/shampooms25/sreadmin.git"

echo ""
echo "❌ PROBLEMA 3: Conflitos de merge"
echo "SOLUÇÃO:"
echo "git stash"
echo "git pull origin main"
echo "git stash pop"

echo ""
echo "❌ PROBLEMA 4: Branch divergente"
echo "SOLUÇÃO:"
echo "git fetch origin"
echo "git reset --hard origin/main"

echo ""
echo "❌ PROBLEMA 5: Permissões do sistema"
echo "SOLUÇÃO:"
echo "sudo chown -R \$USER:\$USER /var/www/sreadmin"
echo "chmod -R 755 /var/www/sreadmin"

echo ""
echo "🔥 SOLUÇÃO DEFINITIVA (FORÇA BRUTA):"
echo "===================================="

cat << 'SOLUTION'
# NO SERVIDOR (Ubuntu):
cd /var/www/sreadmin

# 1. Backup de segurança
cp -r . ../sreadmin_backup_$(date +%Y%m%d_%H%M%S)

# 2. Forçar atualização
git fetch --all
git reset --hard origin/main

# 3. Verificar arquivos
ls -la *.sh *.py *.md

# 4. Dar permissões
chmod +x *.sh

# 5. Testar
./fix_on_conflict_error.sh
SOLUTION

echo ""
echo "🔧 COMANDOS ESPECÍFICOS PARA SEU CASO:"
echo "======================================"

echo ""
echo "NO WINDOWS (onde você está desenvolvendo):"
echo "git add fix_on_conflict_error.sh"
echo "git add production_deploy_fixed.sh" 
echo "git add emergency_fix.py"
echo "git add emergency_table_fix.sh"
echo "git add CORRECAO_ON_CONFLICT_ERROR.md"
echo "git add SOLUCAO_ERRO_500_FINAL.md"
echo "git commit -m \"Add ON CONFLICT error correction scripts\""
echo "git push origin main"

echo ""
echo "NO SERVIDOR (Ubuntu):"
echo "cd /var/www/sreadmin"
echo "git pull origin main"
echo "chmod +x *.sh"
echo "ls -la fix_on_conflict_error.sh  # Verificar se existe"

echo ""
echo "🔍 SE AINDA NÃO FUNCIONAR:"
echo "========================="

echo ""
echo "1. Verificar autenticação GitHub:"
echo "   git config --global user.name \"Seu Nome\""
echo "   git config --global user.email \"seu@email.com\""

echo ""
echo "2. Usar token de acesso pessoal:"
echo "   git remote set-url origin https://TOKEN@github.com/shampooms25/sreadmin.git"

echo ""
echo "3. Clonar repositório novamente:"
echo "   cd /var/www"
echo "   mv sreadmin sreadmin_old"
echo "   git clone https://github.com/shampooms25/sreadmin.git"
echo "   cd sreadmin"

echo ""
echo "4. Verificar logs detalhados:"
echo "   git config --global core.autocrlf false"
echo "   git pull origin main --verbose"

echo ""
echo "✅ TESTE FINAL:"
echo "=============="
echo "curl -I https://raw.githubusercontent.com/shampooms25/sreadmin/main/fix_on_conflict_error.sh"
echo ""
echo "Se retornar 200 OK, o arquivo está no GitHub."
echo "Se retornar 404, o arquivo não foi enviado corretamente."
