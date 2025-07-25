"""
Forms para o sistema de uploads
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import EldUploadVideo

class EldVideoUploadForm(forms.ModelForm):
    """
    Formulário para upload de vídeos ELD com validação de tamanho
    """
    
    class Meta:
        model = EldUploadVideo
        fields = ['video']
        widgets = {
            'video': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': 'video/*',
                'id': 'video-upload'
            })
        }
        labels = {
            'video': 'Selecionar Vídeo'
        }
        help_texts = {
            'video': 'Selecione um arquivo de vídeo (máximo 5MB)'
        }
    
    def clean_video(self):
        """
        Validar arquivo de vídeo
        """
        video = self.cleaned_data.get('video')
        
        if video:
            # Verificar tamanho máximo (5MB)
            max_size = 5 * 1024 * 1024  # 5MB em bytes
            if video.size > max_size:
                raise ValidationError(
                    f'Arquivo muito grande. Tamanho máximo: 5MB. '
                    f'Seu arquivo: {round(video.size / (1024 * 1024), 2)}MB'
                )
            
            # Verificar tipos de arquivo permitidos
            allowed_types = [
                'video/mp4', 'video/avi', 'video/mov', 'video/wmv',
                'video/flv', 'video/webm', 'video/mkv', 'video/3gp'
            ]
            
            if hasattr(video, 'content_type') and video.content_type:
                if video.content_type not in allowed_types:
                    raise ValidationError(
                        f'Tipo de arquivo não permitido. '
                        f'Tipos aceitos: MP4, AVI, MOV, WMV, FLV, WebM, MKV, 3GP'
                    )
            
            # Verificar extensão do arquivo
            import os
            ext = os.path.splitext(video.name)[1].lower()
            allowed_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.3gp']
            
            if ext not in allowed_extensions:
                raise ValidationError(
                    f'Extensão não permitida. '
                    f'Extensões aceitas: {", ".join(allowed_extensions)}'
                )
        
        return video
