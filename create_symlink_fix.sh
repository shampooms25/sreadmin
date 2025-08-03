#!/bin/bash
"""
Script para criar link simbólico temporário que resolve o problema imediatamente
Este é um workaround que força /videos a apontar para o local correto
"""

echo "🔗 CRIANDO LINK SIMBÓLICO TEMPORÁRIO"
echo "===================================="

# Verificar se estamos no diretório correto
if [ ! -d "/var/www/sreadmin" ]; then
    echo "❌ Diretório /var/www/sreadmin não encontrado!"
    exit 1
fi

# Garantir que o diretório correto existe
echo "📁 Criando estrutura correta..."
sudo mkdir -p /var/www/sreadmin/media/videos/eld
sudo chown -R www-data:www-data /var/www/sreadmin/media
sudo chmod -R 775 /var/www/sreadmin/media/videos

# Verificar se /videos já existe
if [ -e "/videos" ]; then
    echo "⚠️  /videos já existe!"
    
    if [ -L "/videos" ]; then
        echo "   É um link simbólico - removendo..."
        sudo rm "/videos"
    elif [ -d "/videos" ]; then
        echo "   É um diretório - fazendo backup..."
        sudo mv "/videos" "/videos.backup.$(date +%Y%m%d_%H%M%S)"
    else
        echo "   É um arquivo - fazendo backup..."
        sudo mv "/videos" "/videos.backup.$(date +%Y%m%d_%H%M%S)"
    fi
fi

# Criar link simbólico
echo "🔗 Criando link simbólico..."
sudo ln -s /var/www/sreadmin/media/videos /videos

if [ -L "/videos" ]; then
    echo "✅ Link simbólico criado com sucesso!"
    echo "   /videos -> /var/www/sreadmin/media/videos"
    
    # Verificar o link
    echo "🔍 Verificando link:"
    ls -la /videos
    
    # Testar escrita
    echo "🧪 Testando escrita..."
    sudo -u www-data touch /videos/eld/test_file.txt
    if [ -f "/videos/eld/test_file.txt" ]; then
        echo "✅ Escrita funcionando!"
        sudo rm /videos/eld/test_file.txt
    else
        echo "❌ Erro na escrita"
    fi
    
    # Reiniciar Apache
    echo "🔄 Reiniciando Apache..."
    sudo systemctl restart apache2
    
    if [ $? -eq 0 ]; then
        echo "✅ Apache reiniciado com sucesso!"
    else
        echo "❌ Erro ao reiniciar Apache"
    fi
    
    echo ""
    echo "🎯 TESTE AGORA:"
    echo "   1. Acesse: https://paineleld.poppnet.com.br/admin/"
    echo "   2. Teste upload de vídeo"
    echo "   3. Vídeo deve ser salvo em: /var/www/sreadmin/media/videos/eld/"
    
    echo ""
    echo "🔄 PARA REMOVER O LINK (depois que funcionar):"
    echo "   sudo rm /videos"
    echo "   # E então aplicar correção definitiva no código"
    
else
    echo "❌ Erro ao criar link simbólico"
fi

echo ""
echo "✅ WORKAROUND APLICADO!"
