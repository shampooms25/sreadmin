#!/bin/bash

# Script para corrigir permissões de upload em produção Ubuntu 24
# Execute este script na raiz do projeto: /var/www/sreadmin

echo "🔧 Corrigindo permissões para upload de vídeos em produção..."

# 1. Criar diretórios necessários
echo "📁 Criando estrutura de diretórios..."
sudo mkdir -p /var/www/sreadmin/media
sudo mkdir -p /var/www/sreadmin/media/videos
sudo mkdir -p /var/www/sreadmin/media/videos/eld
sudo mkdir -p /var/www/sreadmin/media/captive_portal_zips
sudo mkdir -p /var/www/sreadmin/staticfiles

# 2. Definir propriedade correta (substitua 'www-data' pelo usuário do seu servidor web)
echo "👤 Definindo propriedade dos diretórios..."
sudo chown -R www-data:www-data /var/www/sreadmin/media
sudo chown -R www-data:www-data /var/www/sreadmin/staticfiles

# 3. Definir permissões corretas
echo "🔐 Configurando permissões..."
sudo chmod -R 755 /var/www/sreadmin/media
sudo chmod -R 755 /var/www/sreadmin/staticfiles

# Permissões específicas para upload de vídeos
sudo chmod -R 775 /var/www/sreadmin/media/videos
sudo chmod -R 775 /var/www/sreadmin/media/videos/eld
sudo chmod -R 775 /var/www/sreadmin/media/captive_portal_zips

# 4. Se estiver usando Apache, adicionar usuário ao grupo www-data
echo "🌐 Configurando grupo do servidor web..."
# Para Apache
sudo usermod -a -G www-data $USER

# Para Nginx (descomente se usar Nginx)
# sudo usermod -a -G www-data $USER

# 5. Definir permissões para o diretório do projeto
echo "📂 Configurando permissões do projeto..."
sudo chown -R www-data:www-data /var/www/sreadmin
sudo chmod -R 755 /var/www/sreadmin

# Permissões específicas para arquivos Python
sudo chmod -R 644 /var/www/sreadmin/*.py
sudo chmod -R 644 /var/www/sreadmin/*/*.py

# 6. Verificar se existe link simbólico problemático
echo "🔍 Verificando links simbólicos..."
if [ -L "/videos" ]; then
    echo "⚠️  Encontrado link simbólico /videos - removendo..."
    sudo rm /videos
fi

# 7. Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
cd /var/www/sreadmin
python3 manage.py collectstatic --noinput

# 8. Reiniciar serviços
echo "🔄 Reiniciando serviços..."
# Para Apache
sudo systemctl restart apache2

# Para Nginx + Gunicorn (descomente se usar)
# sudo systemctl restart nginx
# sudo systemctl restart gunicorn

echo "✅ Configuração de permissões concluída!"
echo ""
echo "📋 Resumo das configurações:"
echo "   - Diretório media: /var/www/sreadmin/media"
echo "   - Diretório vídeos: /var/www/sreadmin/media/videos/eld"
echo "   - Propriedade: www-data:www-data"
echo "   - Permissões: 775 para uploads, 755 para outros"
echo ""
echo "🔗 URLs de teste:"
echo "   - Admin: https://paineleld.poppnet.com.br/admin/"
echo "   - Upload: https://paineleld.poppnet.com.br/admin/eld/videos/upload/"
echo ""
echo "🧪 Para testar:"
echo "   1. Acesse o admin do Django"
echo "   2. Vá em 'Upload de Vídeos'"
echo "   3. Tente fazer upload de um vídeo"
echo ""
echo "📝 Se ainda houver problemas, verifique:"
echo "   - Configurações do servidor web (Apache/Nginx)"
echo "   - Configurações do MEDIA_ROOT no settings.py"
echo "   - Logs do servidor: sudo tail -f /var/log/apache2/error.log"
