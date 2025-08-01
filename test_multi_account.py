#!/usr/bin/env python
"""
Test script to verify multi-account Starlink functionality
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import (
    get_available_accounts, 
    get_account_info, 
    get_all_accounts_summary,
    DEFAULT_ACCOUNT
)

def test_multi_account_functionality():
    """Test basic multi-account functionality"""
    print("🚀 Testing Multi-Account Starlink Functionality")
    print("=" * 50)
    
    # Test 1: Get available accounts
    print("\n1. Testing available accounts...")
    try:
        accounts = get_available_accounts()
        print(f"✅ Available accounts: {accounts}")
        print(f"✅ Default account: {DEFAULT_ACCOUNT}")
    except Exception as e:
        print(f"❌ Error getting accounts: {e}")
        return False
    
    # Test 2: Get account info
    print("\n2. Testing account info...")
    try:
        for account_id in accounts:
            info = get_account_info(account_id)
            print(f"✅ Account {account_id}: {info}")
    except Exception as e:
        print(f"❌ Error getting account info: {e}")
        return False
    
    # Test 3: Get all accounts summary
    print("\n3. Testing all accounts summary...")
    try:
        summary = get_all_accounts_summary()
        if summary.get('success'):
            print(f"✅ Total accounts: {summary['total_accounts']}")
            print(f"✅ Summary generated at: {summary['last_update']}")
        else:
            print(f"⚠️ Summary failed: {summary.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Error getting summary: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Multi-account functionality tests completed!")
    return True

def test_template_context():
    """Test template context functions"""
    print("\n🎨 Testing Template Context Functions")
    print("=" * 50)
    
    from painel.views import get_selected_account, get_account_context
    from django.http import HttpRequest
    
    # Create mock request
    request = HttpRequest()
    request.GET = {'account': 'test_account'}
    
    print("\n1. Testing get_selected_account...")
    try:
        selected = get_selected_account(request)
        print(f"✅ Selected account: {selected}")
    except Exception as e:
        print(f"❌ Error getting selected account: {e}")
        return False
    
    print("\n2. Testing get_account_context...")
    try:
        context = get_account_context(request)
        print(f"✅ Account context keys: {list(context.keys())}")
    except Exception as e:
        print(f"❌ Error getting account context: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Template context tests completed!")
    return True

def main():
    """Run all tests"""
    print("🔍 Starting Starlink Multi-Account Tests")
    print("=" * 60)
    
    success = True
    
    # Test backend functionality
    success &= test_multi_account_functionality()
    
    # Test template context
    success &= test_template_context()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! Multi-account functionality is working.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
