#!/bin/bash
"""
Script para configurar autenticação Git no servidor de produção
"""

echo "🔐 CONFIGURAÇÃO DE AUTENTICAÇÃO GIT - SERVIDOR"
echo "=" * 50

echo "📋 OPÇÕES DE AUTENTICAÇÃO:"
echo "1. Personal Access Token (PAT) - RECOMENDADO"
echo "2. SSH Key"
echo "3. Git Credential Helper"
echo ""

read -p "Escolha uma opção (1-3): " option

case $option in
    1)
        echo "🎯 CONFIGURANDO PERSONAL ACCESS TOKEN"
        echo ""
        echo "📝 PASSOS:"
        echo "1. Vá para: https://github.com/settings/tokens"
        echo "2. Clique em 'Generate new token' > 'Generate new token (classic)'"
        echo "3. Configure:"
        echo "   - Note: 'Server Production Access'"
        echo "   - Expiration: 90 days (ou No expiration)"
        echo "   - Scopes: ✅ repo (full control)"
        echo "4. Clique em 'Generate token'"
        echo "5. COPIE o token (só aparece uma vez!)"
        echo ""
        
        read -p "Cole o token aqui (não será exibido): " -s token
        echo ""
        
        if [ -n "$token" ]; then
            # Configurar credenciais
            git config --global credential.helper store
            
            # Criar arquivo de credenciais
            echo "https://shampooms25:$token@github.com" > ~/.git-credentials
            chmod 600 ~/.git-credentials
            
            echo "✅ Token configurado!"
            echo "🧪 Testando autenticação..."
            
            # Testar
            if git ls-remote https://github.com/shampooms25/sreadmin.git > /dev/null 2>&1; then
                echo "✅ Autenticação funcionando!"
            else
                echo "❌ Erro na autenticação. Verifique o token."
            fi
        else
            echo "❌ Token não fornecido."
        fi
        ;;
    
    2)
        echo "🔑 CONFIGURANDO SSH KEY"
        echo ""
        
        # Verificar se já existe chave SSH
        if [ -f ~/.ssh/id_rsa ]; then
            echo "🔍 Chave SSH já existe:"
            cat ~/.ssh/id_rsa.pub
        else
            echo "🆕 Gerando nova chave SSH..."
            ssh-keygen -t rsa -b 4096 -C "server-production@sreadmin"
            
            echo "📋 Chave SSH gerada:"
            cat ~/.ssh/id_rsa.pub
        fi
        
        echo ""
        echo "📝 PRÓXIMOS PASSOS:"
        echo "1. Copie a chave SSH acima"
        echo "2. Vá para: https://github.com/settings/ssh/new"
        echo "3. Title: 'Production Server'"
        echo "4. Cole a chave SSH"
        echo "5. Clique em 'Add SSH key'"
        echo ""
        echo "6. Altere o remote para SSH:"
        echo "   git remote set-url origin git@github.com:shampooms25/sreadmin.git"
        ;;
    
    3)
        echo "💾 CONFIGURANDO CREDENTIAL HELPER"
        echo ""
        
        # Configurar credential helper
        git config --global credential.helper 'cache --timeout=86400'
        
        echo "✅ Credential helper configurado (24 horas)"
        echo ""
        echo "🧪 Teste agora:"
        echo "git push origin main"
        echo "(será solicitado usuário e token uma vez)"
        ;;
        
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac

echo ""
echo "📋 COMANDOS ÚTEIS:"
echo "• Verificar configuração: git config --list"
echo "• Testar conexão: git ls-remote origin"
echo "• Ver remote atual: git remote -v"
