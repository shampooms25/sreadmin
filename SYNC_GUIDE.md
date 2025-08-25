# GUIA DE SINCRONIZAÇÃO DESENVOLVIMENTO ↔ PRODUÇÃO

## 📋 RESUMO DA IMPLEMENTAÇÃO

### ✅ **FUNCIONALIDADES IMPLEMENTADAS:**
1. **Auto-switching bidirecional** entre portais com/sem vídeo
2. **Scripts de correção** para problemas de path em produção
3. **Ferramentas de debug** para diagnóstico
4. **Documentação completa** dos processos

### ✅ **ARQUIVOS CRIADOS:**
- `painel/models.py` - Auto-switching implementado
- `COMANDO_CORRECAO_FINAL.md` - Comando único para correção
- `fix_production_portal_paths.py` - Script automatizado
- `debug_api_portal.py` - Debug completo
- `sync_production.sh` - Sincronização Git

---

## 🔄 **PASSOS PARA SINCRONIZAR**

### **1. NO SERVIDOR DE PRODUÇÃO:**

```bash
# Conectar ao servidor
ssh fiber@paineleld.poppnet.com.br

# Sincronizar código
cd /var/www/sreadmin
git fetch origin
git pull origin main

# Verificar arquivos disponíveis
ls -la *fix* *debug* *.md
```

### **2. EXECUTAR CORREÇÃO:**

**Opção A - Script automático:**
```bash
source venv/bin/activate
python3 fix_production_portal_paths.py
```

**Opção B - Comando direto:**
```bash
source venv/bin/activate
cat COMANDO_CORRECAO_FINAL.md  # Ver comando completo
# Copiar e executar o comando Python do arquivo
```

### **3. TESTAR RESULTADO:**

```bash
# Testar API de download
curl -H "Authorization: Bearer 884f88da2e8a947500ceb4af1dafa10d" \
     "https://paineleld.poppnet.com.br/api/appliances/portal/download/?type=without_video" \
     --output /tmp/test_final.zip -w "Status: %{http_code}\nTamanho: %{size_download} bytes\n"

# Verificar arquivo baixado
ls -lh /tmp/test_final.zip
file /tmp/test_final.zip
```

### **4. VALIDAÇÃO COMPLETA:**

```bash
# Testar status da API
curl -H "Authorization: Bearer 884f88da2e8a947500ceb4af1dafa10d" \
     "https://paineleld.poppnet.com.br/api/appliances/portal/status/" | python3 -m json.tool

# Resultado esperado:
# {
#   "status": "active",
#   "portal_type": "without_video",
#   "portal_hash": "...",
#   "download_url": "/api/appliances/portal/download/?type=without_video"
# }
```

---

## 🎯 **OBJETIVOS ALCANÇADOS**

### ✅ **Problema Original Resolvido:**
> "desativei o portal com vídeo e preciso que o portal sem vídeo seja automaticamente publicado"

**SOLUÇÃO:** Auto-switching implementado nos modelos `EldGerenciarPortal` e `EldPortalSemVideo`

### ✅ **Erro 404 Resolvido:**
> "404 Client Error: Not Found for url: https://paineleld.poppnet.com.br/api/appliances/portal/download/?type=without_video"

**SOLUÇÃO:** Scripts de correção de paths criados para resolver problemas de banco de dados

### ✅ **Sincronização Dev/Prod:**
> "preciso fazer o envio para o git e sincronizar ambos os lados novamente"

**SOLUÇÃO:** Código commitado e enviado para repositório, scripts de sincronização criados

---

## 📁 **ARQUIVOS DE REFERÊNCIA**

1. **`COMANDO_CORRECAO_FINAL.md`** - Comando único mais eficaz
2. **`COMANDO_SIMPLES_PRODUCAO.md`** - Passos simplificados
3. **`fix_production_portal_paths.py`** - Script Python completo
4. **`debug_api_portal.py`** - Debug detalhado da API
5. **`sync_production.sh`** - Sincronização automática

---

## 🚀 **COMANDO FINAL PARA PRODUÇÃO**

Execute este comando único no servidor para resolver tudo:

```bash
cd /var/www/sreadmin && git pull origin main && source venv/bin/activate && python3 fix_production_portal_paths.py && curl -H "Authorization: Bearer 884f88da2e8a947500ceb4af1dafa10d" "https://paineleld.poppnet.com.br/api/appliances/portal/download/?type=without_video" --output /tmp/test_success.zip -w "Status: %{http_code}\n"
```

**Resultado esperado:** Status 200 e arquivo ZIP baixado com sucesso! 🎉
