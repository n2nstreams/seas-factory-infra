#!/usr/bin/env python3
"""
OAuth Configuration Test Script
Tests OAuth configuration and endpoints for SaaS Factory
"""

import os
import sys
import requests
import json
from pathlib import Path

def test_oauth_status():
    """Test OAuth status endpoint"""
    try:
        response = requests.get("http://localhost:8000/auth/status")
        if response.status_code == 200:
            status = response.json()
            print("✅ OAuth Status Check:")
            print(f"   Google OAuth: {'✅ Enabled' if status.get('google_oauth_enabled') else '❌ Disabled'}")
            print(f"   GitHub OAuth: {'✅ Enabled' if status.get('github_oauth_enabled') else '❌ Disabled'}")
            print(f"   Google Client ID: {'✅ Configured' if status.get('google_client_id_configured') else '❌ Missing'}")
            print(f"   GitHub Client ID: {'✅ Configured' if status.get('github_client_id_configured') else '❌ Missing'}")
            return status
        else:
            print(f"❌ OAuth status check failed: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is the API gateway running on port 8000?")
        return None
    except Exception as e:
        print(f"❌ Error checking OAuth status: {e}")
        return None

def check_environment_variables():
    """Check OAuth environment variables"""
    print("\n🔍 Environment Variable Check:")
    
    # Backend OAuth variables
    backend_vars = {
        'GOOGLE_OAUTH_ENABLED': os.getenv('GOOGLE_OAUTH_ENABLED'),
        'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID'),
        'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET'),
        'GITHUB_OAUTH_ENABLED': os.getenv('GITHUB_OAUTH_ENABLED'),
        'GITHUB_CLIENT_ID': os.getenv('GITHUB_CLIENT_ID'),
        'GITHUB_CLIENT_SECRET': os.getenv('GITHUB_CLIENT_SECRET'),
    }
    
    for var, value in backend_vars.items():
        if value:
            if 'SECRET' in var:
                print(f"   {var}: ✅ Set (hidden)")
            else:
                print(f"   {var}: ✅ Set to '{value}'")
        else:
            print(f"   {var}: ❌ Not set")
    
    # Frontend OAuth variables
    frontend_env_path = Path("ui/.env.local")
    if frontend_env_path.exists():
        print(f"\n   Frontend .env.local: ✅ Found")
        with open(frontend_env_path, 'r') as f:
            content = f.read()
            if 'VITE_GOOGLE_CLIENT_ID' in content:
                print("   VITE_GOOGLE_CLIENT_ID: ✅ Found")
            else:
                print("   VITE_GOOGLE_CLIENT_ID: ❌ Missing")
            if 'VITE_GITHUB_CLIENT_ID' in content:
                print("   VITE_GITHUB_CLIENT_ID: ✅ Found")
            else:
                print("   VITE_GITHUB_CLIENT_ID: ❌ Missing")
    else:
        print(f"\n   Frontend .env.local: ❌ Not found")

def test_oauth_endpoints():
    """Test OAuth endpoints"""
    print("\n🔍 OAuth Endpoint Check:")
    
    endpoints = [
        ("Google OAuth Start", "http://localhost:8000/auth/google"),
        ("GitHub OAuth Start", "http://localhost:8000/auth/github"),
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, allow_redirects=False)
            if response.status_code in [302, 303]:  # Redirect expected
                print(f"   {name}: ✅ Working (redirects to OAuth provider)")
            elif response.status_code == 400:
                print(f"   {name}: ⚠️  Configured but disabled")
            else:
                print(f"   {name}: ❌ Unexpected response: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"   {name}: ❌ Cannot connect to backend")
        except Exception as e:
            print(f"   {name}: ❌ Error: {e}")

def check_database_connection():
    """Check database connection for OAuth user creation"""
    print("\n🔍 Database Connection Check:")
    
    try:
        # Try to import and check database configuration
        sys.path.append('config')
        from settings import get_settings
        
        settings = get_settings()
        db_config = settings.database
        
        print(f"   Database Host: {db_config.host}")
        print(f"   Database Port: {db_config.port}")
        print(f"   Database Name: {db_config.name}")
        print(f"   Database User: {db_config.user}")
        print(f"   Database Password: {'✅ Set' if db_config.password.get_secret_value() else '❌ Not set'}")
        
        return True
    except ImportError:
        print("   ❌ Cannot import database settings")
        return False
    except Exception as e:
        print(f"   ❌ Error checking database config: {e}")
        return False

def generate_oauth_config_template():
    """Generate OAuth configuration template"""
    print("\n📝 OAuth Configuration Template:")
    
    template = """
# Backend OAuth Configuration (config/environments/development.env)
GOOGLE_OAUTH_ENABLED=true
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=/auth/callback/google

GITHUB_OAUTH_ENABLED=true
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here
GITHUB_REDIRECT_URI=/auth/callback/github

# Frontend OAuth Configuration (ui/.env.local)
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here
VITE_GITHUB_CLIENT_ID=your_github_client_id_here
VITE_API_BASE_URL=http://localhost:8000
"""
    
    print(template)

def main():
    """Main test function"""
    print("🚀 SaaS Factory OAuth Configuration Test")
    print("=" * 50)
    
    # Test OAuth status
    oauth_status = test_oauth_status()
    
    # Check environment variables
    check_environment_variables()
    
    # Test OAuth endpoints
    test_oauth_endpoints()
    
    # Check database connection
    check_database_connection()
    
    # Generate configuration template
    generate_oauth_config_template()
    
    print("\n" + "=" * 50)
    print("📋 Next Steps:")
    
    if oauth_status and all([
        oauth_status.get('google_oauth_enabled'),
        oauth_status.get('github_oauth_enabled'),
        oauth_status.get('google_client_id_configured'),
        oauth_status.get('github_client_id_configured')
    ]):
        print("✅ OAuth is fully configured and working!")
        print("   You can now test the OAuth flows:")
        print("   1. Go to http://localhost:3000/signin")
        print("   2. Click 'Continue with Google' or 'Continue with GitHub'")
        print("   3. Complete the OAuth flow")
    else:
        print("❌ OAuth needs configuration:")
        print("   1. Create Google OAuth app in Google Cloud Console")
        print("   2. Create GitHub OAuth app in GitHub Developer Settings")
        print("   3. Update environment variables with OAuth credentials")
        print("   4. Restart backend and frontend services")
        print("\n   See docs/oauth_setup_complete.md for detailed instructions")

if __name__ == "__main__":
    main()
