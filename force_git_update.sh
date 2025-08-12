#!/bin/bash
# Script para forçar atualização Git no servidor

echo "🔄 FORÇANDO ATUALIZAÇÃO GIT NO SERVIDOR"
echo "======================================="

# Verificar se estamos em um repositório git
if [ ! -d ".git" ]; then
    echo "❌ Este não é um repositório Git!"
    exit 1
fi

echo "📂 Diretório: $(pwd)"
echo "🌿 Branch: $(git branch --show-current)"

echo ""
echo "🔍 STATUS ANTES DA ATUALIZAÇÃO:"
echo "=============================="
git status --short

echo ""
echo "📥 FAZENDO BACKUP DE ARQUIVOS LOCAIS..."
BACKUP_DIR="backup_local_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup de arquivos modificados
MODIFIED_FILES=$(git diff --name-only)
if [ -n "$MODIFIED_FILES" ]; then
    echo "Fazendo backup de arquivos modificados..."
    for file in $MODIFIED_FILES; do
        if [ -f "$file" ]; then
            cp "$file" "$BACKUP_DIR/"
            echo "  ✅ $file"
        fi
    done
fi

# Backup de arquivos não rastreados
UNTRACKED_FILES=$(git ls-files --others --exclude-standard)
if [ -n "$UNTRACKED_FILES" ]; then
    echo "Fazendo backup de arquivos não rastreados..."
    for file in $UNTRACKED_FILES; do
        if [ -f "$file" ]; then
            cp "$file" "$BACKUP_DIR/"
            echo "  ✅ $file"
        fi
    done
fi

echo ""
echo "🔄 FORÇANDO ATUALIZAÇÃO..."
echo "========================"

# Fetch todos os branches
echo "1. Fazendo fetch de todas as atualizações..."
git fetch --all

# Verificar branch remoto
CURRENT_BRANCH=$(git branch --show-current)
echo "2. Branch atual: $CURRENT_BRANCH"

# Resetar para o estado do remote
echo "3. Resetando para origin/$CURRENT_BRANCH..."
git reset --hard origin/$CURRENT_BRANCH

echo ""
echo "🔍 STATUS APÓS ATUALIZAÇÃO:"
echo "=========================="
git status --short

echo ""
echo "📊 ÚLTIMOS COMMITS:"
echo "=================="
git log --oneline -5

echo ""
echo "✅ ATUALIZAÇÃO CONCLUÍDA!"
echo "========================"

if [ -d "$BACKUP_DIR" ] && [ "$(ls -A $BACKUP_DIR)" ]; then
    echo "📦 Backup salvo em: $BACKUP_DIR"
    echo "   Arquivos:"
    ls -la "$BACKUP_DIR"
    echo ""
    echo "💡 Para restaurar um arquivo específico:"
    echo "   cp $BACKUP_DIR/nome_arquivo ."
else
    rmdir "$BACKUP_DIR" 2>/dev/null
fi

echo ""
echo "🎯 PRÓXIMOS PASSOS:"
echo "=================="
echo "1. Verificar se os novos arquivos estão presentes:"
echo "   ls -la *.sh *.py *.md"
echo ""
echo "2. Dar permissões aos scripts:"
echo "   chmod +x *.sh"
echo ""
echo "3. Testar um script:"
echo "   ./fix_on_conflict_error.sh"
