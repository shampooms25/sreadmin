"""
Forms para o sistema de uploads
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import EldUploadVideo, EldPortalSemVideo

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


class EldPortalSemVideoForm(forms.ModelForm):
    """
    Formulário para upload de portais sem vídeo
    """
    
    class Meta:
        model = EldPortalSemVideo
        fields = ['nome', 'versao', 'descricao', 'arquivo_zip', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Portal Poppnet v2.0'
            }),
            'versao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 2.0'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrição das funcionalidades e características deste portal...'
            }),
            'arquivo_zip': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': '.zip',
                'id': 'portal-upload'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'nome': 'Nome do Portal',
            'versao': 'Versão',
            'descricao': 'Descrição',
            'arquivo_zip': 'Arquivo ZIP',
            'ativo': 'Marcar como portal ativo'
        }
        help_texts = {
            'nome': 'Nome descritivo para identificar este portal',
            'versao': 'Versão do portal (usado no nome do arquivo)',
            'descricao': 'Descrição opcional das características do portal',
            'arquivo_zip': 'Arquivo scripts_poppnet_sre.zip (máximo 50MB)',
            'ativo': 'Apenas um portal pode estar ativo por vez'
        }
    
    def clean_arquivo_zip(self):
        """Validar arquivo ZIP"""
        arquivo = self.cleaned_data.get('arquivo_zip')
        
        if arquivo:
            # Verificar tamanho máximo (50MB)
            max_size = 50 * 1024 * 1024  # 50MB em bytes
            if arquivo.size > max_size:
                raise ValidationError(
                    f'Arquivo muito grande. Tamanho máximo: 50MB. '
                    f'Seu arquivo: {round(arquivo.size / (1024 * 1024), 2)}MB'
                )
            
            # Verificar extensão
            if not arquivo.name.lower().endswith('.zip'):
                raise ValidationError('O arquivo deve ter extensão .zip')
            
            # Verificar se é um arquivo ZIP válido
            import zipfile
            try:
                with zipfile.ZipFile(arquivo, 'r') as zip_file:
                    # Verificar se tem arquivos
                    if len(zip_file.filelist) == 0:
                        raise ValidationError('O arquivo ZIP está vazio')
            except zipfile.BadZipFile:
                raise ValidationError('Arquivo ZIP corrompido ou inválido')
        
        return arquivo
    
    def clean_nome(self):
        """Validar nome do portal"""
        nome = self.cleaned_data.get('nome')
        
        if nome and len(nome.strip()) < 3:
            raise ValidationError('O nome deve ter pelo menos 3 caracteres')
        
        return nome.strip() if nome else nome
    
    def clean_versao(self):
        """Validar versão"""
        versao = self.cleaned_data.get('versao')
        
        if versao and len(versao.strip()) < 1:
            raise ValidationError('A versão é obrigatória')
        
        return versao.strip() if versao else versao
