#!/bin/bash
"""
Script para resolver conflito de arquivos não versionados no git pull
"""

echo "🔧 RESOLVENDO CONFLITO DE ARQUIVOS NÃO VERSIONADOS"
echo "=" * 55

PROJECT_PATH="/var/www/sreadmin"
BACKUP_DIR="$PROJECT_PATH/scripts_backup_$(date +%Y%m%d_%H%M%S)"

echo "📁 Criando backup dos scripts em: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Lista dos arquivos que estão causando conflito
CONFLICTING_FILES=(
    "check_git_status.py"
    "create_symlink_fix.sh" 
    "definitive_upload_fix.py"
    "production_safe_fix.py"
    "setup_git_auth.sh"
    "GITHUB_AUTH_GUIDE.md"
    "GIT_SAFE_PRODUCTION_GUIDE.md"
)

echo "📦 Fazendo backup dos arquivos de correção..."
for file in "${CONFLICTING_FILES[@]}"; do
    if [ -f "$PROJECT_PATH/$file" ]; then
        cp "$PROJECT_PATH/$file" "$BACKUP_DIR/"
        echo "✅ Backup: $file"
    fi
done

echo ""
echo "🗑️  Removendo arquivos conflitantes do diretório de trabalho..."
for file in "${CONFLICTING_FILES[@]}"; do
    if [ -f "$PROJECT_PATH/$file" ]; then
        rm "$PROJECT_PATH/$file"
        echo "🗑️  Removido: $file"
    fi
done

echo ""
echo "🔄 Executando git pull..."
cd "$PROJECT_PATH"
git pull origin main

if [ $? -eq 0 ]; then
    echo "✅ Git pull executado com sucesso!"
    
    echo ""
    echo "📋 PRÓXIMOS PASSOS:"
    echo "1. Seus scripts estão salvos em: $BACKUP_DIR"
    echo "2. Você pode restaurá-los se necessário:"
    echo "   cp $BACKUP_DIR/* $PROJECT_PATH/"
    echo ""
    echo "3. Se ainda há problema de upload, execute:"
    echo "   cp $BACKUP_DIR/production_safe_fix.py $PROJECT_PATH/"
    echo "   python3 production_safe_fix.py"
    echo ""
    echo "4. Para verificar se há alterações locais pendentes:"
    echo "   cp $BACKUP_DIR/check_git_status.py $PROJECT_PATH/"
    echo "   python3 check_git_status.py"
    
else
    echo "❌ Erro no git pull. Restaurando arquivos..."
    cp "$BACKUP_DIR"/* "$PROJECT_PATH/"
    echo "🔄 Arquivos restaurados. Verifique o erro e tente novamente."
fi

echo ""
echo "📂 Conteúdo do backup:"
ls -la "$BACKUP_DIR"
