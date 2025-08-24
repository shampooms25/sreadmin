# 🎥 Correção Automática de Vídeo no Portal - Implementação Final

## 📋 Problema Resolvido

**Situação**: O index.html do portal sempre apontava para `eld01.mp4` mesmo quando um vídeo diferente era selecionado na dropdown (ex: `Eld02.mp4`).

**Solução**: Sistema automatizado que corrige as referências de vídeo em **todos os HTMLs** quando um novo vídeo é selecionado no admin.

## ⚙️ Funcionalidades Implementadas

### 1. **Correção Automática no Admin**
- Quando admin seleciona novo vídeo e salva, o sistema:
  - Detecta mudança automaticamente
  - Substitui vídeo no ZIP (`src/assets/videos/`)
  - Corrige **todas** as referências nos HTMLs
  - Cria `selected_video.txt` para override futuro

### 2. **HTMLs Corrigidos Automaticamente**
- `src/index.html`
- `src/login.html` 
- `src/login2.html`

**Correções aplicadas:**
- `<source src="assets/videos/eld01.mp4">` → `<source src="assets/videos/Eld02.mp4">`
- `poster="assets/videos/eld01.jpg"` → `poster="assets/videos/Eld02.jpg"` (se existir)

### 3. **Override no Appliance**
- `selected_video.txt` criado automaticamente
- Variável `POPPFIRE_VIDEO_NAME` respeitada
- Updater detecta e usa vídeo correto mesmo se HTML não foi corrigido

## 🔧 Arquivos Modificados

### **painel/models.py**
```python
class EldGerenciarPortal:
    def _substitute_video_in_zip(self):
        # Substitui vídeo + corrige HTMLs + cria selected_video.txt
        
    def _patch_html_video_references(self, extract_dir, video_filename):
        # Corrige referências em index.html, login.html, login2.html
```

### **painel/services.py**
```python
class ZipManagerService:
    def update_zip_with_video(zip_path, video_file):
        # Atualiza ZIP + corrige HTMLs + cria selected_video.txt
        
    def _patch_html_video_references(temp_dir, video_filename):
        # Método auxiliar para correção de HTMLs
```

### **opnsense_captive_updater.py**
```python
def _auto_update_video_source(self, htdocs: str):
    # Override explícito via selected_video.txt ou POPPFIRE_VIDEO_NAME
    # Estratégia: override > eldNN mais alto > maior tamanho
```

### **patch_portal_zip.py** (utilitário)
```python
# Script auxiliar para correção manual de ZIPs se necessário
# Uso: python patch_portal_zip.py -i portal.zip -v Eld02.mp4
```

## 🚀 Fluxo Completo Automatizado

### **No Admin (Servidor)**
1. Admin acessa "Gerenciar Portal com Vídeo"
2. Seleciona vídeo diferente (ex: `Eld02.mp4`)
3. Clica em "Salvar"
4. **Sistema automaticamente:**
   - Remove `eld01.mp4` do ZIP
   - Adiciona `Eld02.mp4` ao ZIP
   - Corrige `index.html`: `<source src="assets/videos/Eld02.mp4">`
   - Corrige `login.html` e `login2.html` 
   - Cria `selected_video.txt` contendo `Eld02.mp4`
   - Recompacta ZIP completo

### **No Appliance (Cliente)**
1. Appliance baixa ZIP já corrigido
2. `selected_video.txt` garante override correto
3. Updater detecta vídeo correto automaticamente
4. Portal funciona imediatamente com `Eld02.mp4`

## ✅ Resultado Final

### **Antes** (Problema):
```html
<source src="assets/videos/eld01.mp4" type="video/mp4">
```
↳ Sempre apontava para `eld01.mp4` independente do vídeo selecionado

### **Depois** (Corrigido):
```html
<source src="assets/videos/Eld02.mp4" type="video/mp4">
```
↳ Aponta automaticamente para o vídeo selecionado na dropdown

## 🧪 Como Testar

1. **Admin**: Acesse `/admin/painel/gerenciarportalproxy/`
2. **Seleção**: Escolha vídeo diferente (ex: `Eld02.mp4`)  
3. **Salvar**: Clique em "Salvar"
4. **Verificar**: Mensagem de sucesso aparece
5. **Download**: Baixe o ZIP e confirme:
   - ✅ `src/assets/videos/Eld02.mp4` (presente)
   - ✅ `src/assets/videos/selected_video.txt` (contém "Eld02.mp4")
   - ✅ `src/index.html` (referência corrigida)
   - ✅ `src/login.html` e `src/login2.html` (referências corrigidas)

## 📊 Status da Implementação

- [x] **Detecção automática** de mudança de vídeo
- [x] **Substituição** do arquivo no ZIP
- [x] **Correção automática** de HTMLs
- [x] **Override via selected_video.txt**
- [x] **Override via variável de ambiente**
- [x] **Correção de poster** (se existir)
- [x] **Logs detalhados** para debug
- [x] **Validações** e tratamento de erros
- [x] **Teste funcional** completo

**Data**: 24/08/2025  
**Status**: ✅ **COMPLETO E FUNCIONAL**

## 🎯 Vantagens da Solução

1. **Zero Intervenção Manual**: Tudo automático no admin
2. **Múltiplas Camadas**: Correção no ZIP + override no appliance
3. **Compatibilidade**: Funciona com qualquer nome de vídeo
4. **Robustez**: Fallbacks e validações múltiplas
5. **Logs**: Debug completo para troubleshooting
6. **Performance**: Só processa quando há mudança real

---

**💡 Resumo**: Agora quando você selecionar `Eld02.mp4` na dropdown, o `index.html` será automaticamente corrigido para apontar para `assets/videos/Eld02.mp4` sem nenhuma intervenção manual!
