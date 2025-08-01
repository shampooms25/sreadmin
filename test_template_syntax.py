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

def test_template_syntax():
    """Test if the admin template has correct syntax"""
    try:
        from django.template import loader
        
        # Try to load the template
        template = loader.get_template('admin/painel/starlink/admin.html')
        print("✓ Template loaded successfully")
        
        # Check for duplicate blocks by looking at the template source
        source = template.template.source
        content_blocks = source.count('{% block content %}')
        endcontent_blocks = source.count('{% endblock %}')
        
        print(f"✓ Template has {content_blocks} content block(s)")
        print(f"✓ Template has {endcontent_blocks} endblock tag(s)")
        
        if content_blocks == 1:
            print("✓ No duplicate content blocks found")
        else:
            print(f"✗ Found {content_blocks} content blocks (should be 1)")
            return False
        
        # Check for proper block structure
        lines = source.split('\n')
        block_content_line = -1
        endblock_line = -1
        
        for i, line in enumerate(lines):
            if '{% block content %}' in line:
                block_content_line = i + 1
            elif '{% endblock %}' in line and block_content_line > 0 and endblock_line == -1:
                endblock_line = i + 1
                break
        
        if block_content_line > 0 and endblock_line > 0:
            print(f"✓ Content block starts at line {block_content_line}")
            print(f"✓ Content block ends at line {endblock_line}")
            print(f"✓ Content block contains {endblock_line - block_content_line} lines")
        
        return True
        
    except Exception as e:
        print(f"✗ Error loading template: {e}")
        return False

def test_apps_config():
    """Test if the app config has the correct verbose_name"""
    try:
        from django.apps import apps
        app_config = apps.get_app_config('painel')
        print(f"✓ App verbose_name: '{app_config.verbose_name}'")
        
        if app_config.verbose_name == 'Starlink Admin':
            print("✓ App verbose_name is correct")
            return True
        else:
            print(f"✗ App verbose_name should be 'Starlink Admin', got '{app_config.verbose_name}'")
            return False
            
    except Exception as e:
        print(f"✗ Error testing app config: {e}")
        return False

if __name__ == '__main__':
    print("Testing Starlink Admin Template Fix...")
    print("=" * 50)
    
    template_ok = test_template_syntax()
    print()
    
    app_ok = test_apps_config()
    print()
    
    if template_ok and app_ok:
        print("✓ ALL TESTS PASSED - Template fix successful!")
        print("✓ The /admin/starlink/ page should now load correctly")
        print("✓ The admin menu should display 'Starlink Admin'")
        print("✓ No duplicate block content errors should occur")
    else:
        print("✗ Some tests failed - please check the errors above")
    
    print("=" * 50)
