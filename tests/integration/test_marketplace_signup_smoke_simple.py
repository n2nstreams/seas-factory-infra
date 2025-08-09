#!/usr/bin/env python3
"""
Simplified Marketplace Signup Smoke Tests
Runs without complex dependencies for CI environment
"""

import pytest
import sys
import os

# Add api-gateway to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'api-gateway'))

def test_api_routes_exist():
    """Test that critical API route files exist"""
    api_files = [
        'api-gateway/user_routes.py',
        'api-gateway/admin_routes.py', 
        'api-gateway/factory_routes.py',
        'api-gateway/ideas_routes.py'
    ]
    
    for file_path in api_files:
        full_path = os.path.join(os.path.dirname(__file__), '..', '..', file_path)
        assert os.path.exists(full_path), f"Missing API route file: {file_path}"
    
    print("✅ All API route files exist")

def test_signup_endpoint_exists():
    """Test that signup endpoint is defined in user_routes"""
    user_routes_path = os.path.join(os.path.dirname(__file__), '..', '..', 'api-gateway', 'user_routes.py')
    
    with open(user_routes_path, 'r') as f:
        content = f.read()
    
    # Check for critical endpoints
    endpoints = [
        '/api/users/register',
        '/api/users/login', 
        '/api/users/profile'
    ]
    
    for endpoint in endpoints:
        assert endpoint in content, f"Missing endpoint: {endpoint}"
    
    print("✅ All critical user endpoints defined")

def test_signup_form_validation():
    """Test that signup form has required fields"""
    signup_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ui', 'src', 'pages', 'Signup.tsx')
    
    if os.path.exists(signup_path):
        with open(signup_path, 'r') as f:
            content = f.read()
        
        # Check for required form fields
        required_fields = ['firstName', 'lastName', 'email', 'password', 'confirmPassword', 'agreeToTerms']
        
        for field in required_fields:
            assert field in content, f"Missing required field: {field}"
        
        print("✅ All required signup form fields present")
    else:
        print("⚠️  Signup form not found (may not be included in CI)")

if __name__ == "__main__":
    # Run basic smoke tests
    test_api_routes_exist()
    test_signup_endpoint_exists()
    test_signup_form_validation()
    print("🎉 Basic smoke tests passed!")
