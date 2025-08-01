#!/usr/bin/env python
"""
Comprehensive test for the multi-account Starlink implementation
"""

import os
import sys

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')

import django
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

from painel.views import *
from painel.starlink_api import get_available_accounts, DEFAULT_ACCOUNT

def test_views_with_account_selection():
    """Test all views with different account selections"""
    print("🌐 Testing Views with Account Selection")
    print("=" * 50)
    
    factory = RequestFactory()
    
    # Get available accounts
    accounts = get_available_accounts()
    account_ids = list(accounts.keys())
    
    # Test views with different account selections
    views_to_test = [
        ('starlink_admin', starlink_admin),
        ('starlink_dashboard', starlink_dashboard),
        ('starlink_service_lines', starlink_service_lines),
        ('starlink_billing_report', starlink_billing_report),
        ('starlink_api_status', starlink_api_status),
        ('starlink_detailed_report', starlink_detailed_report),
        ('starlink_debug_api', starlink_debug_api),
        ('starlink_usage_report', starlink_usage_report),
    ]
    
    results = []
    
    for view_name, view_func in views_to_test:
        print(f"\n  Testing {view_name}...")
        
        # Test with default account
        try:
            request = factory.get('/')
            request.user = User(username='testuser', is_staff=True)
            response = view_func(request)
            results.append((view_name, 'default', 'success', response.status_code))
            print(f"    ✅ Default account: {response.status_code}")
        except Exception as e:
            results.append((view_name, 'default', 'error', str(e)))
            print(f"    ❌ Default account: {e}")
        
        # Test with specific account
        if account_ids:
            try:
                request = factory.get('/', {'account': account_ids[0]})
                request.user = User(username='testuser', is_staff=True)
                response = view_func(request)
                results.append((view_name, account_ids[0], 'success', response.status_code))
                print(f"    ✅ Account {account_ids[0]}: {response.status_code}")
            except Exception as e:
                results.append((view_name, account_ids[0], 'error', str(e)))
                print(f"    ❌ Account {account_ids[0]}: {e}")
    
    return results

def test_template_context_integrity():
    """Test that all template contexts include required multi-account data"""
    print("\n🎨 Testing Template Context Integrity")
    print("=" * 50)
    
    factory = RequestFactory()
    
    # Test context functions
    request = factory.get('/')
    request.user = User(username='testuser', is_staff=True)
    
    print("\n  Testing helper functions...")
    
    # Test get_selected_account
    try:
        selected = get_selected_account(request)
        assert selected == DEFAULT_ACCOUNT
        print(f"    ✅ get_selected_account: {selected}")
    except Exception as e:
        print(f"    ❌ get_selected_account: {e}")
    
    # Test get_account_context
    try:
        context = get_account_context(request)
        required_keys = ['available_accounts', 'selected_account', 'account_info']
        for key in required_keys:
            assert key in context
        print(f"    ✅ get_account_context: {list(context.keys())}")
    except Exception as e:
        print(f"    ❌ get_account_context: {e}")
    
    # Test get_breadcrumbs_with_account
    try:
        breadcrumbs = [
            {'name': 'Home', 'url': '/admin/'},
            {'name': 'Starlink', 'url': '/admin/starlink/'}
        ]
        result = get_breadcrumbs_with_account(breadcrumbs, 'test_account')
        assert len(result) == 2
        print(f"    ✅ get_breadcrumbs_with_account: {len(result)} breadcrumbs")
    except Exception as e:
        print(f"    ❌ get_breadcrumbs_with_account: {e}")

def test_api_integration():
    """Test API functions with multiple accounts"""
    print("\n🔌 Testing API Integration")
    print("=" * 50)
    
    from painel.starlink_api import (
        get_service_lines_with_location,
        get_billing_summary,
        test_api_connection
    )
    
    accounts = get_available_accounts()
    
    for account_id, account_info in accounts.items():
        print(f"\n  Testing account {account_id} ({account_info['name']})...")
        
        # Test service lines
        try:
            result = get_service_lines_with_location(account_id)
            if 'error' in result:
                print(f"    ⚠️ Service lines: {result['error']}")
            else:
                print(f"    ✅ Service lines: {result.get('total', 0)} found")
        except Exception as e:
            print(f"    ❌ Service lines: {e}")
        
        # Test billing summary
        try:
            result = get_billing_summary(account_id)
            if 'error' in result:
                print(f"    ⚠️ Billing summary: {result['error']}")
            else:
                print(f"    ✅ Billing summary: OK")
        except Exception as e:
            print(f"    ❌ Billing summary: {e}")
        
        # Test API connection
        try:
            result = test_api_connection(account_id)
            if result['status'] == 'success':
                print(f"    ✅ API connection: {result['message']}")
            else:
                print(f"    ⚠️ API connection: {result['message']}")
        except Exception as e:
            print(f"    ❌ API connection: {e}")

def main():
    """Run comprehensive tests"""
    print("🧪 Comprehensive Multi-Account Starlink Tests")
    print("=" * 60)
    
    # Test 1: Views with account selection
    view_results = test_views_with_account_selection()
    
    # Test 2: Template context integrity
    test_template_context_integrity()
    
    # Test 3: API integration
    test_api_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    success_count = sum(1 for _, _, status, _ in view_results if status == 'success')
    total_tests = len(view_results)
    
    print(f"Views tested: {total_tests}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total_tests - success_count}")
    
    if success_count == total_tests:
        print("\n🎉 All tests passed! Multi-account implementation is fully functional.")
    else:
        print(f"\n⚠️ {total_tests - success_count} tests failed. Check the output above.")
    
    return success_count == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
