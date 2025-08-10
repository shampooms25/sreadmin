#!/usr/bin/env python
"""
Teste para verificar se o sistema de upload com preview está funcionando
"""
import os
import sys
import django

# Adicionar o diretório do projeto ao Python path
sys.path.append(r'c:\\Projetos\\Poppnet\\sreadmin')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'captive_portal.settings')
django.setup()

from painel.models import EldPortalSemVideo
from painel.admin import PortalSemVideoUploadForm, ImagePreviewWidget

def test_form_and_widget():
    """Testa o formulário e widget"""
    print("=== TESTE DO FORMULÁRIO E WIDGET ===")
    
    # Testar instanciação do formulário
    try:
        form = PortalSemVideoUploadForm()
        print("✅ Formulário criado com sucesso")
        
        # Verificar campos
        expected_fields = ['nome', 'versao', 'descricao', 'arquivo_zip', 'ativo', 'preview']
        actual_fields = list(form.fields.keys())
        
        print(f"Campos esperados: {expected_fields}")
        print(f"Campos encontrados: {actual_fields}")
        
        if set(expected_fields) == set(actual_fields):
            print("✅ Todos os campos estão presentes")
        else:
            print("❌ Campos não conferem")
        
        # Verificar widget de preview
        preview_widget = form.fields['preview'].widget
        print(f"Widget do preview: {type(preview_widget).__name__}")
        
        if isinstance(preview_widget, ImagePreviewWidget):
            print("✅ Widget personalizado aplicado com sucesso")
        else:
            print("❌ Widget personalizado não aplicado")
            
    except Exception as e:
        print(f"❌ Erro ao criar formulário: {e}")

def test_model_save():
    """Testa a função save do modelo"""
    print("\n=== TESTE DO MODELO ===")
    
    try:
        # Verificar se o método _resize_preview existe
        portal = EldPortalSemVideo()
        if hasattr(portal, '_resize_preview'):
            print("✅ Método _resize_preview existe")
        else:
            print("❌ Método _resize_preview não encontrado")
            
        # Verificar campo preview
        preview_field = EldPortalSemVideo._meta.get_field('preview')
        print(f"Campo preview: {preview_field}")
        print(f"Upload to: {preview_field.upload_to}")
        
        print("✅ Modelo configurado corretamente")
        
    except Exception as e:
        print(f"❌ Erro ao testar modelo: {e}")

def check_template_files():
    """Verifica se os templates existem"""
    print("\n=== VERIFICAÇÃO DE TEMPLATES ===")
    
    templates = [
        r'c:\\Projetos\\Poppnet\\sreadmin\\painel\\templates\\admin\\widgets\\image_preview_widget.html',
        r'c:\\Projetos\\Poppnet\\sreadmin\\painel\\templates\\admin\\painel\\portalsemvideoproxy\\upload_list.html',
        r'c:\\Projetos\\Poppnet\\sreadmin\\painel\\static\\admin\\css\\image_preview.css'
    ]
    
    for template_path in templates:
        if os.path.exists(template_path):
            print(f"✅ {os.path.basename(template_path)} existe")
        else:
            print(f"❌ {os.path.basename(template_path)} não encontrado")

if __name__ == "__main__":
    test_form_and_widget()
    test_model_save()
    check_template_files()
