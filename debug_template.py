#!/usr/bin/env python3
import re

def analyze_template_blocks(file_path):
    """Analisa os blocos Django em um template"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Contar blocos if/endif
    if_blocks = []
    endif_blocks = []
    
    for i, line in enumerate(lines, 1):
        # Procurar por {% if %} (mas não {% endif %})
        if_matches = re.findall(r'{%\s*if\s+[^%]*%}', line)
        for match in if_matches:
            if 'endif' not in match:
                if_blocks.append((i, match))
        
        # Procurar por {% endif %}
        endif_matches = re.findall(r'{%\s*endif\s*%}', line)
        for match in endif_matches:
            endif_blocks.append((i, match))
    
    print(f"Template: {file_path}")
    print(f"Total if blocks: {len(if_blocks)}")
    print(f"Total endif blocks: {len(endif_blocks)}")
    
    print("\nif blocks found:")
    for line_num, block in if_blocks:
        print(f"  Line {line_num}: {block}")
    
    print("\nendif blocks found:")
    for line_num, block in endif_blocks:
        print(f"  Line {line_num}: {block}")
    
    if len(if_blocks) != len(endif_blocks):
        print(f"\n⚠️  MISMATCH: {len(if_blocks)} if blocks vs {len(endif_blocks)} endif blocks")
        return False
    else:
        print("\n✅ All if blocks have corresponding endif blocks")
        return True

if __name__ == "__main__":
    template_path = r"c:\Projetos\Poppnet\sreadmin\painel\templates\admin\painel\starlink\dashboard.html"
    analyze_template_blocks(template_path)
