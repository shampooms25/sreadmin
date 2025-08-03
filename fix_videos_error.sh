#!/bin/bash
"""
Script para corrigir definitivamente o erro /videos em produção
Execute no servidor Ubuntu: chmod +x fix_videos_error.sh && ./fix_videos_error.sh
"""

echo "🚨 CORREÇÃO DEFINITIVA - ERRO /videos"
echo "===================================="

# Verificar se estamos na raiz correta
if [ ! -d "/var/www/sreadmin" ]; then
    echo "❌ Diretório /var/www/sreadmin não encontrado!"
    exit 1
fi

cd /var/www/sreadmin

echo "📁 Diretório atual: $(pwd)"

# 1. VERIFICAR E REMOVER /videos PROBLEMÁTICO
echo ""
echo "🔍 Verificando diretório /videos problemático..."

if [ -e "/videos" ]; then
    echo "⚠️  ENCONTRADO: /videos existe na raiz do sistema"
    
    if [ -L "/videos" ]; then
        echo "   É um link simbólico - removendo..."
        sudo rm "/videos"
        echo "   ✅ Link simbólico removido"
    elif [ -d "/videos" ]; then
        echo "   É um diretório - verificando conteúdo..."
        ls -la "/videos"
        echo ""
        echo "   ⚠️  CUIDADO: É um diretório real!"
        echo "   Se estiver vazio ou contém apenas arquivos de teste, pode ser removido"
        echo "   Execute manualmente: sudo rm -rf /videos"
    else
        echo "   É um arquivo - removendo..."
        sudo rm "/videos"
        echo "   ✅ Arquivo removido"
    fi
else
    echo "✅ /videos não existe na raiz (correto)"
fi

# 2. CRIAR ESTRUTURA CORRETA
echo ""
echo "📂 Criando estrutura correta de diretórios..."

sudo mkdir -p /var/www/sreadmin/media
sudo mkdir -p /var/www/sreadmin/media/videos
sudo mkdir -p /var/www/sreadmin/media/videos/eld
sudo mkdir -p /var/www/sreadmin/media/captive_portal_zips
sudo mkdir -p /var/www/sreadmin/staticfiles

echo "✅ Estrutura de diretórios criada"

# 3. CONFIGURAR PERMISSÕES
echo ""
echo "🔐 Configurando permissões..."

sudo chown -R www-data:www-data /var/www/sreadmin/media
sudo chown -R www-data:www-data /var/www/sreadmin/staticfiles

sudo chmod -R 755 /var/www/sreadmin/media
sudo chmod -R 775 /var/www/sreadmin/media/videos
sudo chmod -R 775 /var/www/sreadmin/media/videos/eld
sudo chmod -R 775 /var/www/sreadmin/media/captive_portal_zips

echo "✅ Permissões configuradas"

# 4. VERIFICAR CONFIGURAÇÃO DJANGO
echo ""
echo "🔧 Verificando configuração Django..."

cd /var/www/sreadmin

# Verificar se manage.py existe
if [ -f "manage.py" ]; then
    echo "✅ manage.py encontrado"
    
    # Testar configuração
    python3 manage.py check --deploy 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Configuração Django OK"
    else
        echo "⚠️  Possíveis problemas na configuração Django"
    fi
else
    echo "❌ manage.py não encontrado - verifique o diretório"
fi

# 5. TESTE DE ESCRITA
echo ""
echo "🧪 Testando escrita no diretório correto..."

test_file="/var/www/sreadmin/media/videos/eld/test_write.txt"

echo "teste de upload" > "$test_file"
if [ -f "$test_file" ]; then
    echo "✅ Escrita funcionando!"
    rm "$test_file"
else
    echo "❌ Erro na escrita - verificar permissões"
fi

# 6. VERIFICAR CONFIGURAÇÃO APACHE
echo ""
echo "🌐 Verificando configuração Apache..."

# Procurar arquivos de configuração do site
config_files=$(find /etc/apache2/sites-available/ -name "*painel*" -o -name "*eld*" 2>/dev/null)

if [ -n "$config_files" ]; then
    echo "📝 Arquivos de configuração encontrados:"
    echo "$config_files"
    
    echo ""
    echo "🔍 Verificando configuração de arquivos estáticos..."
    
    for config in $config_files; do
        if grep -q "media" "$config"; then
            echo "✅ Configuração de media encontrada em: $config"
        else
            echo "⚠️  Configuração de media não encontrada em: $config"
            echo "   Adicione estas linhas:"
            echo "   Alias /media/ /var/www/sreadmin/media/"
            echo "   <Directory /var/www/sreadmin/media>"
            echo "       Require all granted"
            echo "   </Directory>"
        fi
    done
else
    echo "⚠️  Arquivos de configuração não encontrados"
    echo "   Verifique: ls /etc/apache2/sites-available/"
fi

# 7. REINICIAR SERVIÇOS
echo ""
echo "🔄 Reiniciando serviços..."

sudo systemctl reload apache2
if [ $? -eq 0 ]; then
    echo "✅ Apache recarregado"
else
    echo "❌ Erro ao recarregar Apache"
fi

# 8. VERIFICAÇÕES FINAIS
echo ""
echo "✅ VERIFICAÇÕES FINAIS:"

echo "   📁 Estrutura criada:"
ls -la /var/www/sreadmin/media/

echo ""
echo "   🔐 Permissões:"
ls -ld /var/www/sreadmin/media/videos/eld/

echo ""
echo "   🚫 Diretório problemático:"
if [ -e "/videos" ]; then
    echo "   ❌ /videos ainda existe - REMOVER MANUALMENTE!"
else
    echo "   ✅ /videos não existe (correto)"
fi

# 9. INSTRUÇÕES FINAIS
echo ""
echo "🎯 PRÓXIMOS PASSOS:"
echo "   1. Teste o upload em: https://paineleld.poppnet.com.br/admin/"
echo "   2. Se ainda houver erro, execute: python3 debug_upload_error.py"
echo "   3. Verifique logs: sudo tail -f /var/log/apache2/error.log"
echo ""

# 10. Se ainda existir /videos, dar instruções específicas
if [ -e "/videos" ]; then
    echo "⚠️  ATENÇÃO: /videos ainda existe!"
    echo "   Execute este comando APENAS se tiver certeza:"
    echo "   sudo rm -rf /videos"
    echo ""
fi

echo "✅ CORREÇÃO CONCLUÍDA!"
echo "   Teste agora o upload de vídeos no admin"
