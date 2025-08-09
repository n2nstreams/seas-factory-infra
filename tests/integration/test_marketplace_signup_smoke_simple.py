#!/usr/bin/env python3
"""
Simplified Marketplace Signup Smoke Tests
Runs without complex dependencies for CI environment
"""

import sys
import os

def test_api_routes_exist():
    """Test that critical API route files exist"""
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {os.path.dirname(__file__)}")
    
    # List files in api-gateway directory to debug
    if os.path.exists('api-gateway'):
        print(f"Files in api-gateway: {os.listdir('api-gateway')}")
    else:
        print("api-gateway directory not found in current directory")
    
    api_files = [
        'user_routes.py',
        'admin_routes.py', 
        'factory_routes.py',
        'ideas_routes.py'
    ]
    
    missing_files = []
    for file_name in api_files:
        file_path = os.path.join('api-gateway', file_name)
        if os.path.exists(file_path):
            print(f"✅ Found route file: {file_name}")
        else:
            missing_files.append(file_name)
            print(f"❌ Missing route file: {file_name}")
    
    assert len(missing_files) == 0, f"Missing API route files: {missing_files}"
    
    print("✅ All API route files exist")

def test_signup_endpoint_exists():
    """Test that signup endpoint is defined in user_routes"""
    user_routes_path = os.path.join('api-gateway', 'user_routes.py')
    
    if not os.path.exists(user_routes_path):
        print(f"ERROR: Could not find {user_routes_path}")
        print(f"Current directory: {os.getcwd()}")
        assert False, f"Could not find user_routes.py at {user_routes_path}"
    
    with open(user_routes_path, 'r') as f:
        content = f.read()
    
    # Check for critical endpoints - look for route decorators
    endpoints = [
        ('register', '@router.post("/register"'),
        ('login', '@router.post("/login")'),
        ('profile', '@router.get("/profile")')
    ]
    
    missing_endpoints = []
    for name, pattern in endpoints:
        # Look for the route decorator pattern
        if pattern in content or f'"{name}"' in content or f"'{name}'" in content:
            print(f"✅ Found endpoint: {name}")
        else:
            missing_endpoints.append(name)
            print(f"❌ Missing endpoint: {name}")
    
    assert len(missing_endpoints) == 0, f"Missing endpoints: {missing_endpoints}"
    
    print("✅ All critical user endpoints defined")

def test_signup_form_validation():
    """Test that signup form has required fields"""
    signup_path = os.path.join('ui', 'src', 'pages', 'Signup.tsx')
    
    if os.path.exists(signup_path):
        with open(signup_path, 'r') as f:
            content = f.read()
        
        # Check for required form fields
        required_fields = ['firstName', 'lastName', 'email', 'password', 'confirmPassword', 'agreeToTerms']
        
        missing_fields = []
        for field in required_fields:
            if field in content:
                print(f"✅ Found required field: {field}")
            else:
                missing_fields.append(field)
                print(f"❌ Missing required field: {field}")
        
        assert len(missing_fields) == 0, f"Missing required fields: {missing_fields}"
        
        print("✅ All required signup form fields present")
    else:
        print("⚠️  Signup form not found (may not be included in CI)")

if __name__ == "__main__":
    print("=" * 60)
    print("Running Marketplace Signup Smoke Tests")
    print("=" * 60)
    
    try:
        test_api_routes_exist()
        print()
        test_signup_endpoint_exists()
        print()
        test_signup_form_validation()
        print()
        print("🎉 All basic smoke tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)