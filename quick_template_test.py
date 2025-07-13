#!/usr/bin/env python
import os
import sys

# Add the project directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

def test_template_syntax():
    """Quick syntax test for dashboard template"""
    template_path = os.path.join('painel', 'templates', 'admin', 'painel', 'starlink', 'dashboard.html')
    
    if not os.path.exists(template_path):
        print(f"✗ Template not found: {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count blocks
    block_starts = content.count('{% block ')
    block_ends = content.count('{% endblock %}')
    
    print(f"📊 Template Statistics:")
    print(f"   - Block starts: {block_starts}")
    print(f"   - Block ends: {block_ends}")
    print(f"   - Lines: {len(content.splitlines())}")
    
    # Check for common issues
    if '{% endblock %}' in content and block_starts == block_ends:
        print("✓ Block structure appears balanced")
    else:
        print("✗ Block structure may be unbalanced")
        return False
    
    # Check for unclosed if statements
    if_count = content.count('{% if ')
    endif_count = content.count('{% endif %}')
    
    print(f"   - If statements: {if_count}")
    print(f"   - Endif statements: {endif_count}")
    
    if if_count == endif_count:
        print("✓ If/endif structure appears balanced")
    else:
        print("✗ If/endif structure may be unbalanced")
        return False
    
    # Check for specific problematic patterns
    if '{% endblock %}  </div>' in content:
        print("✗ Found problematic endblock pattern")
        return False
    
    print("✓ Template basic syntax check passed")
    return True

if __name__ == '__main__':
    print("Quick Dashboard Template Syntax Check")
    print("=" * 40)
    
    if test_template_syntax():
        print("\n✅ Template syntax looks good!")
        print("You can now test: http://127.0.0.1:8000/admin/starlink/dashboard/")
    else:
        print("\n❌ Template syntax issues found")
    
    print("=" * 40)
