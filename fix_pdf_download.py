#!/usr/bin/env python3
"""
Script para corrigir os headers HTTP dos downloads de PDF
"""

import re

def fix_pdf_headers():
    file_path = r'c:\Projetos\Poppnet\sreadmin\painel\views.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Padrão para encontrar as respostas HTTP de PDF
    old_pattern = r'# Retornar resposta HTTP com PDF\s+response = HttpResponse\(buffer\.getvalue\(\), content_type=\'application/pdf\'\)\s+response\[\'Content-Disposition\'\] = f\'attachment; filename="([^"]+)"\'\s+return response'
    
    # Novo padrão com headers melhorados
    new_pattern = '''# Retornar resposta HTTP com PDF
        pdf_data = buffer.getvalue()
        response = HttpResponse(pdf_data, content_type='application/pdf')
        
        # Headers para forçar download
        filename = f"\\1"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = str(len(pdf_data))
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response'''
    
    # Aplicar as correções
    content = re.sub(old_pattern, new_pattern, content, flags=re.MULTILINE)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Headers de PDF corrigidos com sucesso!")

if __name__ == "__main__":
    fix_pdf_headers()
