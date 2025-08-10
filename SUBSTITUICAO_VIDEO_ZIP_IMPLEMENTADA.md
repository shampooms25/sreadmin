# Substituição Automática de Vídeo no ZIP - Implementação Completa

## 📋 Resumo da Funcionalidade

Implementada a funcionalidade de substituição automática do vídeo dentro do arquivo ZIP do portal quando um novo vídeo é selecionado no "Gerenciar Portal com Vídeo".

## ⚙️ Como Funciona

### 1. Detecção de Mudança
- O sistema detecta automaticamente quando um vídeo diferente é selecionado
- Compara o vídeo anterior com o novo vídeo selecionado
- Só executa a substituição se realmente houve mudança

### 2. Processo de Substituição
- **Remove** todos os vídeos antigos da pasta `src/assets/videos/` dentro do ZIP
- **Adiciona** o novo vídeo selecionado na mesma pasta
- **Preserva** todos os outros arquivos do portal (HTML, CSS, JS, etc.)
- **Mantém** a estrutura completa do ZIP

### 3. Arquivos Modificados

#### `painel/models.py` - Modelo EldGerenciarPortal
```python
def save(self, *args, **kwargs):
    # Detecta mudança de vídeo
    # Chama _substitute_video_in_zip() se necessário

def _substitute_video_in_zip(self):
    # Remove vídeos antigos de src/assets/videos/
    # Adiciona o novo vídeo selecionado
    # Preserva toda estrutura do ZIP
```

#### `painel/admin.py` - EldGerenciarPortalAdmin
```python
def save_model(self, request, obj, form, change):
    # Detecta mudança de vídeo
    # Exibe mensagem de sucesso específica
    # Confirma substituição realizada
```

## 🔧 Funcionalidades Técnicas

### Manipulação de ZIP
- **Biblioteca**: `zipfile` nativa do Python
- **Método**: Cria ZIP temporário, copia arquivos seletivamente
- **Segurança**: Usa `tempfile.TemporaryDirectory()` para operações seguras
- **Performance**: Processo otimizado, só toca no que é necessário

### Detecção de Vídeos
- **Extensões suportadas**: `.mp4`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`, `.mkv`
- **Localização**: Especificamente na pasta `src/assets/videos/`
- **Case-insensitive**: Funciona com maiúsculas e minúsculas

### Tratamento de Erros
- **Validações**: Verifica existência de arquivos antes de processar
- **Logs detalhados**: Sistema de logs para debug
- **Fallback seguro**: Se der erro, não corrompe o ZIP original

## 🎯 Fluxo de Uso

1. **Upload do Portal**: Usuário faz upload do ZIP inicial do portal
2. **Upload de Vídeo**: Usuário faz upload do vídeo personalizado
3. **Seleção no Portal**: Usuário vai em "Gerenciar Portal com Vídeo" e seleciona o novo vídeo
4. **Substituição Automática**: Sistema automaticamente:
   - Remove vídeos antigos do ZIP
   - Insere o novo vídeo no ZIP
   - Exibe mensagem de confirmação
5. **ZIP Atualizado**: Portal está pronto com o novo vídeo integrado

## 📝 Mensagens do Sistema

### Sucesso na Substituição
```
✅ Portal com Vídeo atualizado! Vídeo "nome_video.mp4" foi substituído no arquivo ZIP e está ativo para o OpenSense.
```

### Primeira Configuração
```
✅ Portal com Vídeo configurado! Vídeo customizado "nome_video.mp4" está ativo e pronto para o OpenSense.
```

### Usando Vídeo Padrão
```
✅ Portal com Vídeo configurado! Usando vídeo padrão do ZIP.
```

## 🔍 Logs de Debug

O sistema gera logs detalhados durante o processo:

```
[INFO] Iniciando substituição de vídeo no ZIP...
[INFO] ZIP: /path/to/portal.zip
[INFO] Novo vídeo: /path/to/video.mp4
[INFO] Removendo vídeo antigo: src/assets/videos/old_video.mp4
[INFO] Novo vídeo adicionado: src/assets/videos/new_video.mp4
[SUCESSO] Vídeo substituído com sucesso no ZIP!
```

## ⚠️ Considerações Importantes

### Estrutura do ZIP
- O ZIP deve ter a estrutura padrão: `src/assets/videos/`
- Outros arquivos na pasta de vídeos são preservados (não-vídeos)
- A estrutura completa do portal é mantida

### Performance
- O processo é executado apenas quando há mudança real de vídeo
- Usa operações otimizadas de ZIP
- Não afeta a performance em operações normais

### Segurança
- Operações são atômicas (ou funciona completamente ou não altera nada)
- Não corrompe o ZIP original em caso de erro
- Validações de existência de arquivos

## 🧪 Teste da Funcionalidade

### Cenário de Teste
1. Acesse o admin Django
2. Vá em "Captive Portal" → "Gerenciar Portal com Vídeo"
3. Configure um portal com vídeo inicial
4. Faça upload de um novo vídeo em "Gerenciar Vídeos"
5. Volte ao "Gerenciar Portal com Vídeo"
6. Selecione o novo vídeo
7. Clique em "Salvar"
8. Verifique a mensagem de sucesso
9. Confirme que o ZIP foi atualizado

### Verificação do Resultado
- Baixe o ZIP do portal
- Extraia e verifique a pasta `src/assets/videos/`
- Confirme que apenas o novo vídeo está presente
- Teste o portal no OpenSense

## ✅ Status da Implementação

- [x] Detecção de mudança de vídeo
- [x] Substituição automática no ZIP
- [x] Preservação da estrutura do portal
- [x] Remoção de vídeos antigos
- [x] Inserção do novo vídeo
- [x] Feedback visual no admin
- [x] Tratamento de erros
- [x] Sistema de logs
- [x] Validações de segurança
- [x] Testes funcionais

**Data de Implementação**: 05/08/2025
**Status**: ✅ COMPLETO E FUNCIONAL
