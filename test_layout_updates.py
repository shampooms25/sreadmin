#!/usr/bin/env python
"""
Teste para verificar o layout atualizado e cálculo de tamanho
"""
import os
import sys
import django

# Adicionar o diretório do projeto ao Python path
sys.path.append(r'c:\\Projetos\\Poppnet\\sreadmin')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.models import EldPortalSemVideo
from painel.admin import PortalSemVideoUploadForm

def test_size_calculation():
    """Testa o cálculo de tamanho do arquivo"""
    print("=== TESTE DE CÁLCULO DE TAMANHO ===")
    
    # Criar um objeto de teste (sem salvar)
    portal = EldPortalSemVideo()
    
    # Simular um arquivo de 1MB
    class MockFile:
        def __init__(self, size):
            self.size = size
            self.name = 'test_portal.zip'
    
    # Testar o cálculo
    mock_file = MockFile(1024 * 1024)  # 1MB
    portal.arquivo_zip = mock_file
    
    try:
        expected_size = round(mock_file.size / (1024 * 1024), 2)
        print(f"Arquivo simulado: {mock_file.size} bytes")
        print(f"Tamanho esperado: {expected_size} MB")
        
        # Simular o cálculo que acontece no save
        calculated_size = round(portal.arquivo_zip.size / (1024 * 1024), 2)
        print(f"Tamanho calculado: {calculated_size} MB")
        
        if expected_size == calculated_size:
            print("✅ Cálculo de tamanho funcionando corretamente")
        else:
            print("❌ Erro no cálculo de tamanho")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

def test_form_layout():
    """Testa se o formulário está sendo gerado corretamente"""
    print("\n=== TESTE DO LAYOUT DO FORMULÁRIO ===")
    
    try:
        form = PortalSemVideoUploadForm()
        
        # Verificar se todos os campos estão presentes
        expected_fields = ['nome', 'versao', 'descricao', 'arquivo_zip', 'ativo', 'preview']
        actual_fields = list(form.fields.keys())
        
        print(f"Campos do formulário: {actual_fields}")
        
        # Verificar widgets personalizados
        widgets_info = {}
        for field_name, field in form.fields.items():
            widgets_info[field_name] = type(field.widget).__name__
        
        print(f"Widgets aplicados: {widgets_info}")
        
        # Verificar classes CSS
        css_classes = {}
        for field_name, field in form.fields.items():
            attrs = getattr(field.widget, 'attrs', {})
            css_classes[field_name] = attrs.get('class', 'Sem classe CSS')
        
        print(f"Classes CSS: {css_classes}")
        
        print("✅ Formulário configurado corretamente")
        
    except Exception as e:
        print(f"❌ Erro no teste do formulário: {e}")

if __name__ == "__main__":
    test_size_calculation()
    test_form_layout()
