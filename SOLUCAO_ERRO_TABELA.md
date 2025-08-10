# SOLUÇÃO PARA O ERRO: "não existe a relação captive_portal_appliancetoken"

## 🚨 PROBLEMA
```
ProgrammingError at /admin/captive_portal/appliancetoken/
ERRO: não existe a relação "captive_portal_appliancetoken"
```

## ✅ SOLUÇÃO RÁPIDA

### Opção 1: Via URL de Setup (RECOMENDADO)

1. **Acesse a URL de setup no navegador:**
   ```
   http://localhost:8000/api/setup/tokens/
   ```

2. **Aguarde a execução** - A página mostrará um JSON com o resultado da configuração

3. **Verifique se funcionou:**
   ```
   http://localhost:8000/api/setup/check/
   ```

4. **Acesse o admin:**
   ```
   http://localhost:8000/admin/captive_portal/appliancetoken/
   ```

### Opção 2: Via Terminal (se o terminal funcionar)

```bash
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Executar migrações
python manage.py migrate

# Se não funcionar, tentar migração específica
python manage.py migrate captive_portal 0004_appliancetoken
```

### Opção 3: Via Script Python

Execute o arquivo `create_table_direct.py` que foi criado:
```bash
python create_table_direct.py
```

## 🔧 O QUE A SOLUÇÃO FAZ

1. **Cria a tabela `captive_portal_appliancetoken`** diretamente no banco PostgreSQL
2. **Configura os índices** necessários para performance
3. **Sincroniza tokens** do arquivo JSON para o banco
4. **Marca a migração** como aplicada no Django
5. **Testa o acesso** via Django ORM

## 📊 ESTRUTURA DA TABELA CRIADA

```sql
CREATE TABLE captive_portal_appliancetoken (
    id SERIAL PRIMARY KEY,
    token VARCHAR(64) UNIQUE NOT NULL,
    appliance_id VARCHAR(100) UNIQUE NOT NULL,
    appliance_name VARCHAR(200) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE,
    ip_address INET
);
```

## 🎯 APÓS A SOLUÇÃO

### Você poderá:

1. **Acessar o Admin:**
   - http://localhost:8000/admin/captive_portal/appliancetoken/

2. **Gerenciar tokens:**
   - Criar novos tokens
   - Ativar/desativar tokens existentes
   - Ver estatísticas de uso

3. **Usar a API:**
   ```bash
   # Testar com Postman ou curl
   curl -H "Authorization: Bearer test-token-123456789" \
        http://localhost:8000/api/appliances/info/
   ```

### Tokens Disponíveis (após sincronização):

1. **`test-token-123456789`** - Appliance de Teste
2. **`f8e7d6c5b4a3928170695e4c3d2b1a0f`** - Appliance POPPFIRE 001  
3. **`1234567890abcdef1234567890abcdef`** - Appliance de Desenvolvimento

## 🔍 VERIFICAÇÃO

Para verificar se tudo está funcionando:

1. **Check via API:**
   ```
   GET http://localhost:8000/api/setup/check/
   ```

2. **Check via Admin:**
   - Acesse `/admin/captive_portal/appliancetoken/`
   - Deve mostrar a lista de tokens

3. **Check via API de teste:**
   ```
   GET http://localhost:8000/api/appliances/info/
   Authorization: Bearer test-token-123456789
   ```

## 🚀 RESULTADO ESPERADO

Após executar a solução, você deve ver:

- ✅ Tabela criada no banco
- ✅ Tokens sincronizados
- ✅ Admin funcionando
- ✅ API respondendo corretamente
- ✅ Autenticação funcionando

## 📞 SE AINDA HOUVER PROBLEMAS

1. Verifique se o PostgreSQL está rodando
2. Confirme as credenciais do banco no settings.py
3. Execute as URLs de setup novamente
4. Verifique os logs do Django para erros específicos
