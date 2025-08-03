# 🚨 SOLUÇÃO DEFINITIVA - Erro /videos em Produção

## 📊 SITUAÇÃO ATUAL
```bash
# Diretório correto existe e tem permissões OK:
(venv) root@srvEldRadius:/var/www/sreadmin# ls -la /var/www/sreadmin/media/videos/eld
drwxr-xr-x 2 www-data www-data 4096 ago  3 14:45 .

# MAS o erro ainda persiste:
❌ Erro ao salvar vídeo: [Errno 13] Permission denied: '/videos'
```

## 🔍 DIAGNÓSTICO
O Django está tentando acessar `/videos` na **raiz do sistema** ao invés do diretório correto. Isso indica que:
1. Pode existir um diretório/link `/videos` na raiz
2. Alguma configuração está apontando para o local errado

## ⚡ SOLUÇÃO IMEDIATA

### 1. Execute no servidor (como root):
```bash
# Verificar se existe /videos problemático
ls -la /videos

# Se existir, verificar se é link ou diretório
file /videos

# REMOVER se for link simbólico ou diretório vazio
sudo rm -rf /videos
```

### 2. Execute o script de diagnóstico:
```bash
cd /var/www/sreadmin
python3 debug_upload_error.py
```

### 3. Execute o script de correção:
```bash
chmod +x fix_videos_error.sh
./fix_videos_error.sh
```

## 🔧 COMANDOS MANUAIS (se preferir)

### Passo 1: Verificar e remover /videos problemático
```bash
# Verificar se existe
ls -la /videos

# Se existir, remover (CUIDADO!)
sudo rm -rf /videos
```

### Passo 2: Garantir estrutura correta
```bash
# Criar diretórios
sudo mkdir -p /var/www/sreadmin/media/videos/eld

# Permissões corretas
sudo chown -R www-data:www-data /var/www/sreadmin/media
sudo chmod -R 775 /var/www/sreadmin/media/videos/eld
```

### Passo 3: Testar escrita
```bash
# Teste como www-data
sudo -u www-data touch /var/www/sreadmin/media/videos/eld/test.txt

# Se funcionar, remover
sudo rm /var/www/sreadmin/media/videos/eld/test.txt
```

### Passo 4: Verificar configuração Apache
```bash
# Verificar configuração do site
sudo nano /etc/apache2/sites-available/paineleld.conf

# Deve conter algo como:
# Alias /media/ /var/www/sreadmin/media/
# <Directory /var/www/sreadmin/media>
#     Require all granted
# </Directory>
```

### Passo 5: Reiniciar Apache
```bash
sudo systemctl restart apache2
```

## 🧪 TESTE FINAL

### 1. Verificar estrutura:
```bash
ls -la /var/www/sreadmin/media/videos/eld/
# Deve mostrar: drwxrwxr-x www-data www-data
```

### 2. Verificar que /videos NÃO existe:
```bash
ls -la /videos
# Deve mostrar: No such file or directory
```

### 3. Testar upload:
- Acesse: https://paineleld.poppnet.com.br/admin/
- Vá em: CAPTIVE PORTAL > Upload de Vídeos
- Tente fazer upload de um vídeo pequeno

## 📝 SE O PROBLEMA PERSISTIR

### Verificar logs em tempo real:
```bash
# Em uma janela:
sudo tail -f /var/log/apache2/error.log

# Em outra janela, tentar o upload
```

### Verificar configuração Django:
```bash
cd /var/www/sreadmin
python3 manage.py shell

# No shell Django:
from django.conf import settings
print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"BASE_DIR: {settings.BASE_DIR}")

from painel.models import EldUploadVideo
field = EldUploadVideo._meta.get_field('video')
print(f"upload_to: {field.upload_to}")
```

### Verificar processo Django:
```bash
# Ver se Django está rodando corretamente
ps aux | grep python
ps aux | grep apache
```

## 🎯 CAUSA MAIS PROVÁVEL

O problema mais comum é existir um diretório ou link simbólico `/videos` na raiz do sistema que está interferindo com o Django. A remoção deste diretório deve resolver:

```bash
sudo rm -rf /videos
sudo systemctl restart apache2
```

## 📋 CHECKLIST DE VERIFICAÇÃO

- [ ] ✅ Diretório `/videos` na raiz NÃO existe
- [ ] ✅ Diretório `/var/www/sreadmin/media/videos/eld/` existe
- [ ] ✅ Permissões são `www-data:www-data` e `775`
- [ ] ✅ Apache reiniciado
- [ ] ✅ Configuração Apache inclui alias para /media/
- [ ] ✅ Django settings.py tem MEDIA_ROOT correto
- [ ] ✅ Teste de escrita manual funcionando

## 🚀 APÓS A CORREÇÃO

O upload deve funcionar e você deve ver:
- ✅ Vídeo salvo com sucesso
- ✅ Arquivo em `/var/www/sreadmin/media/videos/eld/`
- ✅ Notificação Telegram enviada
- ✅ ZIP atualizado automaticamente

---

**⚡ EXECUTE IMEDIATAMENTE:**
```bash
sudo rm -rf /videos
sudo systemctl restart apache2
```

Depois teste o upload novamente!
