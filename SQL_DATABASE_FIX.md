# CORREÇÃO DIRETA NO BANCO DE DADOS POSTGRESQL

## 🎯 PROBLEMA IDENTIFICADO
O campo `arquivo_zip` na tabela `painel_eldportalsemvideo` contém espaços em branco no final, impedindo que o Django encontre o arquivo.

## 📋 INSTRUÇÕES PARA EXECUTAR NO SERVIDOR

### **PASSO 1: Conectar ao servidor**
```bash
ssh fiber@paineleld.poppnet.com.br
```

### **PASSO 2: Verificar estado atual do banco**
```bash
sudo -u postgres psql -d sreadmin_db -c "
SELECT 
    id, 
    nome, 
    LENGTH(arquivo_zip) as tamanho_campo,
    arquivo_zip,
    ativo 
FROM painel_eldportalsemvideo 
WHERE ativo = true;
"
```

### **PASSO 3: Executar correção SQL**
```bash
sudo -u postgres psql -d sreadmin_db -c "
UPDATE painel_eldportalsemvideo 
SET arquivo_zip = 'portal_sem_video/hotspot-auth-default_G24aTr6.zip' 
WHERE ativo = true;
"
```

### **PASSO 4: Verificar correção**
```bash
sudo -u postgres psql -d sreadmin_db -c "
SELECT 
    id, 
    nome, 
    LENGTH(arquivo_zip) as tamanho_campo,
    arquivo_zip,
    ativo 
FROM painel_eldportalsemvideo 
WHERE ativo = true;
"
```

### **PASSO 5: Testar a API**
```bash
curl -H "Authorization: Bearer 884f88da2e8a947500ceb4af1dafa10d" \
     "https://paineleld.poppnet.com.br/api/appliances/portal/download/?type=without_video" \
     --output /tmp/test_db_fix.zip -w "Status: %{http_code}\nTamanho: %{size_download} bytes\n"
```

### **PASSO 6: Verificar arquivo baixado**
```bash
ls -lh /tmp/test_db_fix.zip
file /tmp/test_db_fix.zip
```

---

## 🔍 COMANDOS DE DIAGNÓSTICO ADICIONAIS

### **Verificar arquivos físicos no servidor:**
```bash
ls -la /var/www/sreadmin/media/portal_sem_video/
```

### **Verificar se o arquivo específico existe:**
```bash
test -f /var/www/sreadmin/media/portal_sem_video/hotspot-auth-default_G24aTr6.zip && echo "EXISTE" || echo "NÃO EXISTE"
```

### **Ver conteúdo atual da tabela:**
```bash
sudo -u postgres psql -d sreadmin_db -c "
SELECT 
    id,
    nome,
    arquivo_zip,
    LENGTH(arquivo_zip) as len,
    TRIM(arquivo_zip) as arquivo_limpo,
    ativo,
    criado_em
FROM painel_eldportalsemvideo 
ORDER BY criado_em DESC;
"
```

### **Comando alternativo se o arquivo for diferente:**
```bash
# Se o arquivo for hotspot-auth-default.zip (sem sufixo):
sudo -u postgres psql -d sreadmin_db -c "
UPDATE painel_eldportalsemvideo 
SET arquivo_zip = 'portal_sem_video/hotspot-auth-default.zip' 
WHERE ativo = true;
"
```

---

## 🎯 RESULTADO ESPERADO

Após executar a correção SQL, você deve ver:
- ✅ **Campo `arquivo_zip`**: `portal_sem_video/hotspot-auth-default_G24aTr6.zip` (sem espaços)
- ✅ **Length**: 49 caracteres (ao invés de 100+)
- ✅ **API retorna**: Status 200 com arquivo ZIP
- ✅ **Arquivo baixado**: ~360KB, tipo ZIP válido

---

## 🚨 COMANDO ÚNICO PARA EXECUTAR TUDO

Execute este comando único no servidor:

```bash
sudo -u postgres psql -d sreadmin_db -c "UPDATE painel_eldportalsemvideo SET arquivo_zip = 'portal_sem_video/hotspot-auth-default_G24aTr6.zip' WHERE ativo = true;" && curl -H "Authorization: Bearer 884f88da2e8a947500ceb4af1dafa10d" "https://paineleld.poppnet.com.br/api/appliances/portal/download/?type=without_video" --output /tmp/test_success.zip -w "Status: %{http_code}\n" && ls -lh /tmp/test_success.zip
```

**Se retornar Status 200 e um arquivo ZIP válido, o problema estará resolvido! 🎉**
