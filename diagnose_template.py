#!/usr/bin/env python
"""
Script para diagnosticar o problema do template
"""
import os
import sys

# Verificar se os templates existem
templates = [
    r'c:\Projetos\Poppnet\sreadmin\painel\templates\admin\painel\portalsemvideoproxy\upload_list.html',
    r'c:\Projetos\Poppnet\sreadmin\captive_portal\templates\admin\captive_portal\portalsemvideoproxy\add_form.html'
]

print("=== VERIFICAÇÃO DE TEMPLATES ===")
for template in templates:
    if os.path.exists(template):
        print(f"✅ {template}")
        # Ler as primeiras linhas do template
        with open(template, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:10]
            print(f"   Primeiras linhas:")
            for i, line in enumerate(lines, 1):
                print(f"   {i}: {line.strip()}")
    else:
        print(f"❌ {template} - NÃO ENCONTRADO")
    print()

# Verificar CSS
css_file = r'c:\Projetos\Poppnet\sreadmin\painel\static\admin\css\image_preview.css'
print("=== VERIFICAÇÃO DE CSS ===")
if os.path.exists(css_file):
    print(f"✅ {css_file}")
else:
    print(f"❌ {css_file} - NÃO ENCONTRADO")

print("\n=== INSTRUÇÕES DE TESTE ===")
print("1. Acesse: http://127.0.0.1:8000/admin/captive_portal/portalsemvideoproxy/add/")
print("2. Verifique se o campo 'Portal Ativo' está na primeira linha com destaque")
print("3. Selecione um arquivo ZIP e veja se o tamanho aparece abaixo")
print("4. Pressione F12 e veja se há erros no Console")
