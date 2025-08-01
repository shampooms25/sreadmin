#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

def test_dashboard_template():
    """Test if the dashboard template loads without errors"""
    try:
        from django.template import loader
        
        # Try to load the template
        template = loader.get_template('admin/painel/starlink/dashboard.html')
        print("✓ Dashboard template loaded successfully")
        
        # Check for proper block structure
        source = template.template.source
        
        # Count blocks
        block_count = source.count('{% block ')
        endblock_count = source.count('{% endblock %}')
        
        print(f"✓ Template has {block_count} block tags")
        print(f"✓ Template has {endblock_count} endblock tags")
        
        # Check specific blocks
        blocks = ['title', 'extrahead', 'content']
        for block in blocks:
            if f'block {block}' in source:
                print(f"✓ Block '{block}' found")
            else:
                print(f"✗ Block '{block}' not found")
        
        # Test basic template rendering
        test_context = {
            'title': 'Dashboard Test',
            'breadcrumbs': [{'name': 'Home', 'url': '/'}],
            'available_accounts': {},
            'selected_account': None,
            'has_statistics': False,
            'statistics': {},
            'total_service_lines': 0,
        }
        
        rendered = template.render(test_context)
        print("✓ Template rendered successfully")
        print(f"✓ Rendered template length: {len(rendered)} characters")
        
        return True
        
    except Exception as e:
        print(f"✗ Error with dashboard template: {e}")
        return False

if __name__ == '__main__':
    print("Testing Dashboard Template Fix...")
    print("=" * 50)
    
    success = test_dashboard_template()
    
    if success:
        print("\n✓ DASHBOARD TEMPLATE FIX SUCCESSFUL!")
        print("✓ The /admin/starlink/dashboard/ page should now load correctly")
    else:
        print("\n✗ Dashboard template still has issues")
    
    print("=" * 50)
