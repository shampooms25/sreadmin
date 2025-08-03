# 🚨 CORREÇÃO DEFINITIVA - 3 Soluções para o Erro /videos

## 📊 PROBLEMA CONFIRMADO

**Erro**: `❌ Erro ao salvar vídeo: [Errno 13] Permission denied: '/videos'`  
**Causa**: Django está tentando acessar `/videos` na raiz do sistema ao invés de `/var/www/sreadmin/media/videos/eld/`  
**Confirmação**: Logs mostram POST para upload retornando 200, mas erro interno no processamento

## ⚡ SOLUÇÃO 1: LINK SIMBÓLICO (MAIS RÁPIDA - 30 segundos)

### Execute no servidor:
```bash
cd /var/www/sreadmin
chmod +x create_symlink_fix.sh
./create_symlink_fix.sh
```

**O que faz**: Cria um link simbólico `/videos` → `/var/www/sreadmin/media/videos`  
**Vantagem**: Funciona imediatamente  
**Desvantagem**: É um workaround, não corrige a causa raiz

---

## 🔧 SOLUÇÃO 2: CORREÇÃO NO MODELO (INTERMEDIÁRIA - 2 minutos)

### Execute no servidor:
```bash
cd /var/www/sreadmin
python3 force_correct_upload_path.py
sudo systemctl restart apache2
```

**O que faz**: Modifica o campo `upload_to` para usar função personalizada  
**Vantagem**: Corrige no código Django  
**Desvantagem**: Requer modificação de código

---

## 🎯 SOLUÇÃO 3: CORREÇÃO DEFINITIVA (MAIS COMPLETA - 5 minutos)

### Execute no servidor:
```bash
cd /var/www/sreadmin
python3 definitive_upload_fix.py
python3 test_upload_path.py  # Para verificar
sudo systemctl restart apache2
```

**O que faz**: 
- Corrige `upload_to` com lambda function
- Força caminhos absolutos no settings
- Adiciona logs de debug
- Remove `/videos` se existir
- Cria script de teste

**Vantagem**: Solução completa e robusta  
**Desvantagem**: Mais demorada

---

## 🚀 RECOMENDAÇÃO PARA CORREÇÃO IMEDIATA

### Execute AGORA (30 segundos):
```bash
cd /var/www/sreadmin
chmod +x create_symlink_fix.sh
./create_symlink_fix.sh
```

**Depois teste**: https://paineleld.poppnet.com.br/admin/

### Se funcionar, depois aplique correção definitiva:
```bash
sudo rm /videos  # Remove o link temporário
python3 definitive_upload_fix.py
sudo systemctl restart apache2
```

---

## 📋 SCRIPTS CRIADOS

| Script | Função | Tempo |
|--------|---------|-------|
| `create_symlink_fix.sh` | Link simbólico temporário | 30s |
| `force_correct_upload_path.py` | Correção no modelo | 2min |
| `definitive_upload_fix.py` | Correção completa | 5min |

---

## 🧪 COMO TESTAR

### 1. Após aplicar qualquer solução:
```bash
# Verificar estrutura
ls -la /var/www/sreadmin/media/videos/eld/

# Se usou link simbólico, verificar
ls -la /videos

# Testar permissão de escrita
sudo -u www-data touch /var/www/sreadmin/media/videos/eld/test.txt
```

### 2. Testar no browser:
- Acesse: https://paineleld.poppnet.com.br/admin/
- Vá em: CAPTIVE PORTAL > Upload de Vídeos  
- Faça upload de um vídeo pequeno
- **Deve funcionar sem erro**

### 3. Verificar resultado:
```bash
# Vídeo deve aparecer aqui
ls -la /var/www/sreadmin/media/videos/eld/
```

---

## 🔄 PLANO DE ROLLBACK

### Se algo der errado:
```bash
# Para Solução 1 (link simbólico)
sudo rm /videos

# Para Soluções 2 e 3 (código)
cp /var/www/sreadmin/painel/models.py.backup* /var/www/sreadmin/painel/models.py
sudo systemctl restart apache2
```

---

## 💡 POR QUE ISSO ACONTECE?

**Hipóteses**:
1. **Código legado**: Algum código antigo pode ter referência hardcoded para `/videos`
2. **Configuração Apache**: mod_wsgi pode estar interpretando caminhos relativos incorretamente  
3. **Cache Python**: Bytecode compilado pode ter caminho incorreto
4. **Environment**: Variável de ambiente pode estar definindo caminho errado

**A solução do link simbólico vai funcionar independente da causa!**

---

## ✅ RESULTADO ESPERADO

Após aplicar qualquer solução:
- ✅ Upload de vídeos funcionando
- ✅ Arquivos salvos em `/var/www/sreadmin/media/videos/eld/`
- ✅ Sistema de notificações funcionando
- ✅ Processamento de ZIP funcionando
- ✅ Erro `/videos` eliminado

---

# 🎯 EXECUTE AGORA:

```bash
cd /var/www/sreadmin
chmod +x create_symlink_fix.sh
./create_symlink_fix.sh
```

**Isso vai resolver o problema em 30 segundos!** 🚀
