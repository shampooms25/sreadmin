# -*- coding: utf-8 -*-
"""
Middleware para aplicar traduções personalizadas no Django Admin
"""

import re
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import activate
from .translation import CUSTOM_TRANSLATIONS


class AdminTranslationMiddleware(MiddlewareMixin):
    """
    Middleware que aplica traduções personalizadas para o Django Admin
    """
    
    def process_response(self, request, response):
        """
        Processa a resposta e aplica traduções se for uma página do admin
        """
        # Só processa se for uma página do admin
        if not request.path.startswith('/admin/'):
            return response
            
        # Só processa respostas HTML
        if not response.get('Content-Type', '').startswith('text/html'):
            return response
            
        # Ativa a localização para português do Brasil
        activate('pt-br')
        
        try:
            # Converte o conteúdo para string
            content = response.content.decode('utf-8')            # Aplica as traduções de forma mais precisa e conservadora
            for english_text, portuguese_text in CUSTOM_TRANSLATIONS.items():
                # Pula traduções que podem interferir com URLs ou caminhos
                if english_text.lower() in ['all', 'css', 'js', 'min', 'src', 'href'] or '.' in english_text:
                    continue
                    
                # Apenas traduções de texto puro em elementos específicos
                # Substitui texto em elementos de texto puro
                content = re.sub(
                    rf'>{re.escape(english_text)}<',
                    f'>{portuguese_text}<',
                    content,
                    flags=re.IGNORECASE
                )
                
                # Substitui texto em labels
                content = re.sub(
                    rf'<label[^>]*>(\s*){re.escape(english_text)}(\s*)</label>',
                    rf'<label>\1{portuguese_text}\2</label>',
                    content,
                    flags=re.IGNORECASE
                )
                
                # Substitui placeholders
                content = re.sub(
                    rf'placeholder=["\'](\s*){re.escape(english_text)}(\s*)["\']',
                    f'placeholder="\\1{portuguese_text}\\2"',
                    content,
                    flags=re.IGNORECASE
                )
                
                # Substitui valores de botões
                content = re.sub(
                    rf'value=["\'](\s*){re.escape(english_text)}(\s*)["\']',
                    f'value="\\1{portuguese_text}\\2"',
                    content,
                    flags=re.IGNORECASE
                )
                
                # Substitui texto em parágrafos
                content = re.sub(
                    rf'<p[^>]*>(\s*){re.escape(english_text)}(\s*)</p>',
                    rf'<p>\1{portuguese_text}\2</p>',
                    content,
                    flags=re.IGNORECASE
                )
                
                # Substitui texto em spans
                content = re.sub(
                    rf'<span[^>]*>(\s*){re.escape(english_text)}(\s*)</span>',
                    rf'<span>\1{portuguese_text}\2</span>',
                    content,
                    flags=re.IGNORECASE
                )
                
                # Substitui texto em divs pequenas
                content = re.sub(
                    rf'<div[^>]*>(\s*){re.escape(english_text)}(\s*)</div>',
                    rf'<div>\1{portuguese_text}\2</div>',
                    content,
                    flags=re.IGNORECASE
                )
            
            # Reconstrói a resposta com o conteúdo traduzido
            response.content = content.encode('utf-8')
            response['Content-Length'] = str(len(response.content))
            
        except Exception as e:
            # Se houver erro, retorna a resposta original
            pass
            
        return response
