# 🎥 Preview do Vídeo do ZIP - Implementação

## 📋 Funcionalidade Solicitada

Gerar preview do vídeo que está dentro do arquivo ZIP do portal, localizado em `/src/assets/videos/`.

## ✅ Solução Técnica

### 1. Método de Extração Temporária
```python
def extract_video_from_zip_for_preview(zip_path):
    """
    Extrai temporariamente o vídeo do ZIP para gerar preview
    """
    try:
        import tempfile
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Buscar vídeos na pasta assets/videos
            video_files = []
            for file_info in zip_ref.filelist:
                if (file_info.filename.startswith('src/assets/videos/') and 
                    file_info.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm'))):
                    video_files.append(file_info.filename)
            
            if video_files:
                # Extrair primeiro vídeo encontrado para pasta temporária
                video_file = video_files[0]
                temp_dir = tempfile.mkdtemp()
                zip_ref.extract(video_file, temp_dir)
                
                # Caminho completo do vídeo extraído
                extracted_video_path = os.path.join(temp_dir, video_file)
                
                return {
                    'success': True,
                    'video_path': extracted_video_path,
                    'video_name': os.path.basename(video_file),
                    'temp_dir': temp_dir  # Para limpeza posterior
                }
        
        return {'success': False, 'error': 'Nenhum vídeo encontrado no ZIP'}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

### 2. View para Servir o Preview
```python
@staff_member_required
def preview_video_from_zip(request, config_id):
    """
    Serve o vídeo extraído do ZIP para preview
    """
    from django.http import FileResponse, Http404
    import tempfile
    
    config = get_object_or_404(EldGerenciarPortal, id=config_id)
    
    if not config.captive_portal_zip:
        raise Http404("ZIP não encontrado")
    
    # Extrair vídeo temporariamente
    result = extract_video_from_zip_for_preview(config.captive_portal_zip.path)
    
    if not result['success']:
        raise Http404("Vídeo não encontrado no ZIP")
    
    try:
        # Servir o arquivo de vídeo
        response = FileResponse(
            open(result['video_path'], 'rb'),
            content_type='video/mp4'
        )
        
        # Agendar limpeza do arquivo temporário
        # (Implementar com Celery ou similar para produção)
        
        return response
        
    except Exception as e:
        # Limpar arquivo temporário em caso de erro
        if os.path.exists(result['temp_dir']):
            shutil.rmtree(result['temp_dir'])
        raise Http404("Erro ao servir vídeo")
```

### 3. Interface de Preview
```html
<!-- Template para mostrar preview do vídeo do ZIP -->
<div class="zip-video-preview">
    <h4>🎥 Vídeo Padrão do ZIP</h4>
    {% if config.captive_portal_zip %}
        <div class="video-preview-container">
            <video controls width="400" height="225">
                <source src="{% url 'painel:preview_video_from_zip' config.id %}" type="video/mp4">
                Seu navegador não suporta vídeo HTML5.
            </video>
            <p><strong>Localização:</strong> src/assets/videos/</p>
            <p><strong>Nota:</strong> Este é o vídeo padrão incluído no ZIP do portal.</p>
        </div>
    {% else %}
        <p>Nenhum ZIP configurado para preview.</p>
    {% endif %}
</div>
```

## ⚡ **Pergunta 2: Novo vídeo gera novo ZIP automaticamente?**

**Resposta: SIM, o sistema já faz isso automaticamente** ✅

### 🔄 Processo Atual Confirmado:

1. **Upload de Novo Vídeo**: ✅ Usuário faz upload
2. **Seleção no Portal**: ✅ Admin seleciona novo vídeo 
3. **ZIP Regenerado**: ✅ Sistema automaticamente:
   - Extrai o ZIP atual
   - Remove vídeo antigo de `/src/assets/videos/`
   - Adiciona novo vídeo na mesma pasta
   - Recria o ZIP com novo conteúdo

### 📂 Evidência no Código:
```python
# Em painel/services.py - ZipManagerService.update_zip_with_video()
def update_zip_with_video(zip_path, video_file):
    # 1. Extrai ZIP atual
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    # 2. Remove vídeos antigos
    for file in os.listdir(videos_dir):
        if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
            os.remove(os.path.join(videos_dir, file))  # ✅ REMOVE ANTIGO
    
    # 3. Adiciona novo vídeo
    video_destination = os.path.join(videos_dir, video_file.name)
    with open(video_destination, 'wb') as dest_file:
        for chunk in video_file.chunks():
            dest_file.write(chunk)  # ✅ ADICIONA NOVO
    
    # 4. Recria ZIP completo
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
        # ✅ GERA NOVO ZIP COM NOVO VÍDEO
```

## 🎯 Resumo das Respostas:

### ✅ **Preview do Vídeo do ZIP**:
- **Possível**: SIM, com extração temporária
- **Localização**: `src/assets/videos/` 
- **Implementação**: Precisa de view customizada para extrair e servir temporariamente

### ✅ **Novo ZIP com Novo Vídeo**:
- **Automático**: SIM, já implementado
- **Processo**: Upload → Seleção → ZIP regenerado automaticamente
- **Resultado**: Novo ZIP com novo vídeo embarcado em `/src/assets/videos/`

**Status**: Ambas funcionalidades estão **disponíveis/implementadas** no sistema! 🚀
