# Como Testar a Substituição de Vídeo no ZIP

## 🧪 Roteiro de Teste Prático

### Pré-requisitos
1. ✅ Sistema Django rodando
2. ✅ Acesso ao admin Django
3. ✅ Um arquivo ZIP de portal com vídeo
4. ✅ Dois vídeos diferentes para teste

### Passo a Passo

#### 1. Primeira Configuração
```bash
# 1. Acesse o admin Django
http://localhost:8000/admin/

# 2. Vá em "Captive Portal" → "Gerenciar Vídeos"
# 3. Faça upload do primeiro vídeo (ex: video1.mp4)

# 4. Vá em "Captive Portal" → "Gerenciar Portal com Vídeo"
# 5. Faça upload do arquivo ZIP do portal
# 6. Selecione o video1.mp4
# 7. Clique em "Salvar"
```

**Resultado esperado**: 
```
✅ Portal com Vídeo configurado! Vídeo customizado "video1.mp4" está ativo e pronto para o OpenSense.
```

#### 2. Upload do Segundo Vídeo
```bash
# 1. Vá em "Captive Portal" → "Gerenciar Vídeos" 
# 2. Faça upload do segundo vídeo (ex: video2.mp4)
```

#### 3. Substituição do Vídeo
```bash
# 1. Volte em "Captive Portal" → "Gerenciar Portal com Vídeo"
# 2. Mude a seleção para video2.mp4
# 3. Clique em "Salvar"
```

**Resultado esperado**:
```
✅ Portal com Vídeo atualizado! Vídeo "video2.mp4" foi substituído no arquivo ZIP e está ativo para o OpenSense.
```

#### 4. Verificação do ZIP
```bash
# 1. Baixe o ZIP do portal atual
# 2. Extraia o conteúdo
# 3. Navegue para: src/assets/videos/
# 4. Verifique que apenas video2.mp4 está presente
# 5. Confirme que video1.mp4 foi removido
```

### Logs de Acompanhamento

Durante o processo, você pode monitorar os logs do Django:

```python
# No console do Django, você verá:
[INFO] Iniciando substituição de vídeo no ZIP...
[INFO] ZIP: /path/to/portal.zip
[INFO] Novo vídeo: /path/to/video2.mp4
[INFO] Removendo vídeo antigo: src/assets/videos/video1.mp4
[INFO] Novo vídeo adicionado: src/assets/videos/video2.mp4
[SUCESSO] Vídeo substituído com sucesso no ZIP!
```

### Cenários de Teste Adicionais

#### Teste 1: Múltiplas Substituições
- Suba 3 vídeos diferentes
- Mude entre eles várias vezes
- Verifique que sempre apenas o último selecionado permanece no ZIP

#### Teste 2: Vídeo para Vídeo Padrão
- Configure um vídeo customizado
- Mude para "--- Selecione um vídeo ---" (vídeo padrão)
- Verifique que o vídeo customizado foi removido

#### Teste 3: Diferentes Formatos
- Teste com .mp4, .avi, .mov, .webm
- Verifique que todos os formatos são suportados
- Confirme remoção correta de diferentes extensões

### Troubleshooting

#### Se não funcionar:
1. **Verifique os logs do Django**:
```bash
tail -f logs/django.log
# ou no console onde Django está rodando
```

2. **Verifique permissões de arquivo**:
```bash
# O Django precisa de permissão para escrever nos arquivos ZIP
ls -la media/captive_portal_zips/
```

3. **Verifique estrutura do ZIP**:
```bash
# O ZIP deve ter a pasta src/assets/videos/
unzip -l portal.zip | grep "src/assets/videos"
```

4. **Verifique espaço em disco**:
```bash
df -h
# O processo precisa de espaço para o arquivo temporário
```

### Comandos de Debug

#### Ver estrutura do ZIP:
```bash
python manage.py shell
>>> from painel.models import EldGerenciarPortal
>>> portal = EldGerenciarPortal.objects.get(ativo=True)
>>> import zipfile
>>> with zipfile.ZipFile(portal.captive_portal_zip.path) as z:
...     for file in z.filelist:
...         if 'videos' in file.filename:
...             print(file.filename)
```

#### Testar substituição manual:
```bash
python manage.py shell
>>> from painel.models import EldGerenciarPortal
>>> portal = EldGerenciarPortal.objects.get(ativo=True)
>>> portal._substitute_video_in_zip()
```

## ✅ Checklist de Validação

- [ ] Primeiro vídeo configurado com sucesso
- [ ] Segundo vídeo configurado com sucesso  
- [ ] Mensagem de substituição exibida
- [ ] ZIP contém apenas o último vídeo
- [ ] Vídeo antigo foi removido
- [ ] Estrutura do portal preservada
- [ ] URLs funcionam corretamente no OpenSense
- [ ] Performance aceitável na substituição

**Data do Teste**: ___________
**Testado por**: ___________
**Resultado**: ✅ APROVADO / ❌ FALHOU
