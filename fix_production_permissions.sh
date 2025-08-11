#!/bin/bash
# Fix de permissões para produção
# Execute como root no servidor

echo "🔧 Corrigindo permissões em produção..."

# Navegar para o diretório do projeto
cd /var/www/sreadmin

# Ajustar ownership para www-data
echo "👤 Ajustando ownership..."
chown -R www-data:www-data .
find . -type d -exec chmod 755 {} \;
find . -type f -exec chmod 644 {} \;

# Permissões especiais para arquivos Python
chmod 755 manage.py
find . -name "*.py" -exec chmod 644 {} \;

# Permissões especiais para diretórios media
if [ -d "media" ]; then
    echo "📁 Configurando diretório media..."
    chmod -R 755 media/
    chown -R www-data:www-data media/
fi

# Permissões para logs
if [ -d "logs" ]; then
    chmod -R 755 logs/
    chown -R www-data:www-data logs/
fi

# Permissões específicas para arquivo de tokens
if [ -f "appliance_tokens.json" ]; then
    echo "🔑 Configurando arquivo de tokens..."
    chmod 644 appliance_tokens.json
    chown www-data:www-data appliance_tokens.json
else
    echo "⚠️ Arquivo appliance_tokens.json não encontrado"
fi

# Criar diretórios necessários se não existem
mkdir -p media/videos media/uploads static logs
chown -R www-data:www-data media/ static/ logs/ 2>/dev/null
chmod -R 755 media/ static/ logs/ 2>/dev/null

# Ajustar permissões do ambiente virtual
if [ -d "venv" ]; then
    echo "🐍 Ajustando permissões do venv..."
    chown -R www-data:www-data venv/
fi

echo "✅ Permissões corrigidas!"
echo ""
echo "🔍 Verificando status final:"
ls -la appliance_tokens.json 2>/dev/null || echo "❌ appliance_tokens.json não existe"
ls -ld media/ 2>/dev/null || echo "❌ Diretório media não existe"
ls -ld static/ 2>/dev/null || echo "❌ Diretório static não existe"

echo ""
echo "🚀 Execute agora:"
echo "   cd /var/www/sreadmin"
echo "   source venv/bin/activate"
echo "   python quick_migration_fix.py"
