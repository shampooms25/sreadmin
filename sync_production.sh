#!/bin/bash
# Script para sincronizar código entre desenvolvimento e produção

echo "=== SINCRONIZAÇÃO DE CÓDIGO - PRODUÇÃO ==="
echo "Data: $(date)"
echo ""

# Navegar para o diretório do projeto
cd /var/www/sreadmin

# Fazer backup do estado atual
echo "1. Fazendo backup do estado atual..."
git stash push -m "backup-antes-sync-$(date +%Y%m%d-%H%M%S)"

# Buscar as últimas mudanças do repositório
echo "2. Buscando mudanças do repositório..."
git fetch origin

# Atualizar branch main
echo "3. Atualizando código..."
git checkout main
git pull origin main

# Mostrar últimos commits
echo "4. Últimas mudanças aplicadas:"
git log --oneline -5

echo ""
echo "5. Verificando arquivos de correção disponíveis:"
ls -la *fix* *debug* *.md 2>/dev/null | grep -E "(fix|debug|COMANDO)"

echo ""
echo "=== PRÓXIMOS PASSOS ==="
echo "1. Execute o script de correção mais adequado:"
echo "   python3 fix_production_portal_paths.py"
echo ""
echo "2. Ou use o comando direto do arquivo:"
echo "   cat COMANDO_CORRECAO_FINAL.md"
echo ""
echo "3. Teste a API após correção:"
echo "   curl -H \"Authorization: Bearer 884f88da2e8a947500ceb4af1dafa10d\" \\"
echo "        \"https://paineleld.poppnet.com.br/api/appliances/portal/download/?type=without_video\" \\"
echo "        --output /tmp/test_sync.zip -w \"Status: %{http_code}\\n\""

echo ""
echo "✅ SINCRONIZAÇÃO CONCLUÍDA!"
