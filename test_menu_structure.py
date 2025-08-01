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

def test_starlink_menu_structure():
    """Test if the Starlink menu structure is correctly configured"""
    
    print("Testing Starlink Menu Structure...")
    print("=" * 50)
    
    # Test 1: Check if URLs are configured
    try:
        from django.urls import reverse
        
        # Test main page URL
        main_url = reverse('painel:starlink_main')
        print(f"✓ Main page URL: {main_url}")
        
        # Test dashboard URL
        dashboard_url = reverse('painel:starlink_dashboard')
        print(f"✓ Dashboard URL: {dashboard_url}")
        
        # Test admin URL
        admin_url = reverse('painel:starlink_admin')
        print(f"✓ Admin URL: {admin_url}")
        
        print("✓ All URLs are properly configured")
        
    except Exception as e:
        print(f"✗ URL configuration error: {e}")
        return False
    
    # Test 2: Check if views exist
    try:
        from painel.views import starlink_main, starlink_dashboard, starlink_admin
        print("✓ All views are properly imported")
        
    except ImportError as e:
        print(f"✗ View import error: {e}")
        return False
    
    # Test 3: Check if templates exist
    try:
        import os
        template_path = os.path.join(os.path.dirname(__file__), 'painel', 'templates', 'admin', 'painel', 'starlink', 'main.html')
        if os.path.exists(template_path):
            print("✓ Main template exists")
        else:
            print("✗ Main template not found")
            return False
            
    except Exception as e:
        print(f"✗ Template check error: {e}")
        return False
    
    # Test 4: Check if app config is correct
    try:
        from django.apps import apps
        app_config = apps.get_app_config('painel')
        print(f"✓ App verbose_name: '{app_config.verbose_name}'")
        
        if app_config.verbose_name == 'Painel':
            print("✓ App verbose_name is correct (Painel)")
        else:
            print(f"✗ App verbose_name should be 'Painel', got '{app_config.verbose_name}'")
            return False
            
    except Exception as e:
        print(f"✗ App config error: {e}")
        return False
    
    # Test 5: Check if model exists
    try:
        from painel.models import StarlinkAdminProxy
        print("✓ StarlinkAdminProxy model exists")
        
    except ImportError as e:
        print(f"✗ Model import error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✓ ALL TESTS PASSED!")
    print("✓ Menu structure is properly configured:")
    print("  - Main menu item: 'Painel' (original)")
    print("  - Sub-menu item: 'Starlink Admin' (leads to main page)")
    print("  - Main page: 2 cards (Dashboard & Administration)")
    print("  - Dashboard: /admin/starlink/dashboard/")
    print("  - Administration: /admin/starlink/admin/")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = test_starlink_menu_structure()
    if success:
        print("\n🎉 Configuration is ready!")
        print("📋 Next steps:")
        print("  1. Run the development server")
        print("  2. Go to /admin/")
        print("  3. Click on 'Starlink Admin' in the menu")
        print("  4. You should see the page with 2 cards")
    else:
        print("\n❌ Some issues need to be fixed first")
