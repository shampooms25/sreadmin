# 🚨 CORREÇÃO URGENTE - Erro de Upload em Produção

## ❌ PROBLEMA IDENTIFICADO
```
❌ Erro ao salvar vídeo: [Errno 13] Permission denied: '/videos'
URL: https://paineleld.poppnet.com.br/admin/eld/videos/upload/
Servidor: Ubuntu 24 - /var/www/sreadmin
```

## 🔍 DIAGNÓSTICO
O erro indica que o Django está tentando acessar `/videos` na **raiz do sistema** ao invés de usar o `MEDIA_ROOT` configurado (`/var/www/sreadmin/media/videos/eld/`).

## ⚡ CORREÇÃO RÁPIDA (Execute no servidor)

### 1. Acesse o servidor
```bash
ssh usuario@paineleld.poppnet.com.br
cd /var/www/sreadmin
```

### 2. Execute o script de correção rápida
```bash
# Fazer download dos scripts (ou copiar manualmente)
python3 quick_fix_upload.py
```

### 3. OU execute manualmente:
```bash
# Verificar se existe /videos problemático
ls -la /videos

# Se existir, remover (CUIDADO!)
sudo rm -rf /videos  # Apenas se for link simbólico ou diretório vazio

# Criar estrutura correta
sudo mkdir -p /var/www/sreadmin/media/videos/eld
sudo mkdir -p /var/www/sreadmin/media/captive_portal_zips

# Corrigir permissões
sudo chown -R www-data:www-data /var/www/sreadmin/media
sudo chmod -R 775 /var/www/sreadmin/media/videos
sudo chmod -R 775 /var/www/sreadmin/media/captive_portal_zips

# Reiniciar Apache
sudo systemctl restart apache2
```

## 🔧 SCRIPTS DISPONÍVEIS

### 1. `quick_fix_upload.py` - Correção Rápida ⚡
```bash
python3 quick_fix_upload.py
```
- Diagnostica o problema
- Corrige automaticamente
- Testa a solução

### 2. `fix_upload_production.py` - Diagnóstico Completo 🔍
```bash
python3 fix_upload_production.py
```
- Análise detalhada
- Correção abrangente
- Relatório completo

### 3. `fix_upload_permissions.sh` - Script Bash 🐧
```bash
chmod +x fix_upload_permissions.sh
./fix_upload_permissions.sh
```
- Correção via shell script
- Configuração de servidor web
- Reinicialização de serviços

## 🎯 CAUSA PROVÁVEL

### Possível Problema 1: Diretório /videos na raiz
```bash
# Verificar se existe
ls -la /videos

# Se for link simbólico problemático
sudo rm /videos
```

### Possível Problema 2: MEDIA_ROOT incorreto
Verificar em `/var/www/sreadmin/sreadmin/settings.py`:
```python
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Deve ser assim
# NÃO deve ser: MEDIA_ROOT = '/videos'
```

### Possível Problema 3: Permissões
```bash
# Verificar propriedade
ls -la /var/www/sreadmin/media/

# Deve ser: www-data:www-data
# Se não for, executar:
sudo chown -R www-data:www-data /var/www/sreadmin/media
```

## 📋 CHECKLIST DE VERIFICAÇÃO

- [ ] ✅ Diretório `/var/www/sreadmin/media/videos/eld/` existe
- [ ] ✅ Propriedade é `www-data:www-data`
- [ ] ✅ Permissões são `775` ou `755`
- [ ] ✅ Não existe `/videos` na raiz do sistema
- [ ] ✅ MEDIA_ROOT correto no settings.py
- [ ] ✅ Apache reiniciado
- [ ] ✅ Teste de upload funcionando

## 🧪 TESTE FINAL

1. **Acesse**: https://paineleld.poppnet.com.br/admin/
2. **Login**: Use credenciais de admin
3. **Navegue**: CAPTIVE PORTAL > Upload de Vídeos
4. **Teste**: Faça upload de um vídeo pequeno

## 📝 SE AINDA HOUVER PROBLEMA

### Verificar logs:
```bash
# Apache
sudo tail -f /var/log/apache2/error.log

# Django (se configurado)
tail -f /var/www/sreadmin/django_errors.log
```

### Verificar configuração Apache:
```bash
# Verificar se está servindo arquivos media
cat /etc/apache2/sites-available/paineleld.conf
```

### Verificar processo Django:
```bash
# Se usando mod_wsgi
sudo systemctl status apache2

# Se usando Gunicorn
sudo systemctl status gunicorn
```

## 🚀 APÓS A CORREÇÃO

### ✅ Funcionalidades que voltarão a funcionar:
1. **Upload de vídeos** via admin
2. **Notificações automáticas** (email/Telegram)
3. **Atualização automática de ZIP**
4. **Interface de gerenciamento**

### 📱 URLs funcionais:
- Admin: https://paineleld.poppnet.com.br/admin/
- Upload: https://paineleld.poppnet.com.br/admin/eld/videos/upload/
- ZIP Manager: https://paineleld.poppnet.com.br/admin/painel/zip-manager/
- Notificações: https://paineleld.poppnet.com.br/admin/painel/test-notifications/

## 🎉 RESULTADO ESPERADO

Após a correção, o upload deve funcionar normalmente e você deve ver:
- ✅ Vídeo salvo com sucesso
- ✅ Notificação enviada via Telegram
- ✅ ZIP atualizado automaticamente
- ✅ Interface funcionando perfeitamente

---

**⚡ AÇÃO IMEDIATA RECOMENDADA:** Execute `python3 quick_fix_upload.py` no servidor para correção automática!
