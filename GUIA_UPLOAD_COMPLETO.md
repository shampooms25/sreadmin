# 📦 GUIA DE UPLOAD - SISTEMA PORTAL CAPTIVE

## 🎯 ONDE FAZER UPLOAD DE CADA ARQUIVO

### 1. **🎬 UPLOAD DE VÍDEOS** (máx 5MB cada)
```
📍 Menu: Captive Portal > Gerenciar Vídeos
🔗 URL: http://localhost:8000/admin/painel/uploadvideosproxy/
📋 Função: Upload dos vídeos institucionais
✅ O que fazer:
   1. Clique em "Adicionar Gerenciar Vídeos"
   2. Escolha o arquivo de vídeo (MP4, AVI, MOV, etc.)
   3. Máximo 5MB por arquivo
   4. Preview automático disponível
```

### 2. **📦 UPLOAD DE PORTAL SEM VÍDEO** (scripts_poppnet_sre.zip)
```
📍 Menu: Captive Portal > Portal sem Vídeo
🔗 URL: http://localhost:8000/admin/painel/portalsemvideoproxy/
📋 Função: Upload do ZIP que será usado quando vídeo estiver DESATIVADO
✅ O que fazer:
   1. Clique em "Adicionar Portal sem Vídeo"
   2. Preencha nome e versão
   3. Faça upload do arquivo ZIP (máx 50MB)
   4. Marque como "Ativo" se for o portal padrão
```

### 3. **🗂️ UPLOAD DE PORTAL COM VÍDEO** (src.zip)
```
📍 Menu: Captive Portal > Gerenciar ZIP Portal
🔗 URL: http://localhost:8000/admin/painel/zipmanagerproxy/
📋 Função: Upload do ZIP que será usado quando vídeo estiver ATIVADO
✅ O que fazer:
   1. Faça upload do arquivo src.zip
   2. Este arquivo deve ter estrutura para inserção de vídeo
   3. O vídeo selecionado será inserido automaticamente
```

### 4. **⚙️ CONFIGURAÇÃO FINAL** (Escolher o que usar)
```
📍 Menu: Captive Portal > Gerenciar Captive Portal
🔗 URL: http://localhost:8000/admin/painel/gerenciarportalproxy/
📋 Função: Configurar qual tipo de portal usar
✅ O que fazer:
   1. Clique em "Adicionar Gerenciar Captive Portal"
   2. Escolha uma das opções:
   
   OPÇÃO A - Com Vídeo:
   ✅ Ativar Vídeo = TRUE
   ✅ Selecionar vídeo da lista (com preview)
   ✅ Sistema usará src.zip + vídeo selecionado
   
   OPÇÃO B - Sem Vídeo:
   ❌ Ativar Vídeo = FALSE
   ✅ Selecionar portal sem vídeo
   ✅ Sistema usará scripts_poppnet_sre.zip
```

## 🔄 FLUXO COMPLETO DE CONFIGURAÇÃO

### **Cenário 1: Portal COM Vídeo**
```
1. 📹 Upload vídeo em "Gerenciar Vídeos" (máx 5MB)
2. 🗂️ Upload src.zip em "Gerenciar ZIP Portal"
3. ⚙️ Criar config em "Gerenciar Captive Portal":
   - Ativar Vídeo = TRUE
   - Selecionar vídeo (preview disponível)
4. 🚀 API entregará: src.zip + vídeo inserido
```

### **Cenário 2: Portal SEM Vídeo**
```
1. 📦 Upload scripts_poppnet_sre.zip em "Portal sem Vídeo"
2. ⚙️ Criar config em "Gerenciar Captive Portal":
   - Ativar Vídeo = FALSE
   - Selecionar portal sem vídeo
3. 🚀 API entregará: scripts_poppnet_sre.zip
```

## 🎨 MENU VISUAL

```
📊 Dashboard Principal
│
├── 🎥 Captive Portal
│   ├── 📹 Gerenciar Vídeos          ← VÍDEOS (5MB cada)
│   ├── ⚙️ Gerenciar Captive Portal   ← CONFIGURAÇÃO FINAL
│   ├── 📦 Portal sem Vídeo          ← ZIP SEM VÍDEO (50MB)
│   ├── 🗂️ Gerenciar ZIP Portal       ← ZIP COM VÍDEO (src.zip)
│   └── 🔔 Sistema de Notificações   ← Emails/Telegram
│
├── 🌐 Starlink
├── 📊 Relatórios  
└── 👥 Usuários
```

## 🔧 CORREÇÃO DOS MENUS

✅ **PROBLEMA RESOLVIDO**: Menus que fechavam ao clicar
- JavaScript atualizado para permitir navegação
- Links agora funcionam normalmente
- Menu fecha automaticamente após clicar em um link

## 🧪 TESTE RÁPIDO

### 1. **Testar Menu Corrigido:**
```
1. Clique em "Captive Portal" no menu superior
2. Verifique se o submenu abre
3. Clique em qualquer item do submenu
4. Deve navegar para a página correta
```

### 2. **Testar Upload:**
```
1. Vá em "Portal sem Vídeo"
2. Clique "Adicionar Portal sem Vídeo"
3. Faça upload de um arquivo ZIP pequeno para teste
4. Verifique se aparece na listagem
```

## 🎯 PRÓXIMOS PASSOS

1. ✅ **Testar correção dos menus**
2. 📦 **Fazer upload de portal sem vídeo**
3. 🎬 **Fazer upload de alguns vídeos**
4. ⚙️ **Configurar portal desativando vídeo**
5. 🔗 **Testar API**: http://localhost:8000/api/captive-portal/config/

**Agora os menus devem funcionar corretamente e você já sabe exatamente onde fazer cada upload!**
