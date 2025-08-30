#!/usr/bin/env python3
"""
Quick OAuth Test Script for SaaS Factory
Tests OAuth configuration and endpoints quickly
"""

import requests
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import get_settings

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_step(step: str):
    """Print a formatted step"""
    print(f"\n🔧 {step}")


def print_success(message: str):
    """Print a success message"""
    print(f"✅ {message}")


def print_error(message: str):
    """Print an error message"""
    print(f"❌ {message}")


def print_info(message: str):
    """Print an info message"""
    print(f"ℹ️  {message}")


def test_oauth_status():
    """Test OAuth status endpoint"""
    print_step("Testing OAuth Status Endpoint")
    
    try:
        response = requests.get("http://localhost:8000/auth/status", timeout=10)
        
        if response.status_code == 200:
            status = response.json()
            print_success("OAuth status endpoint working")
            print(f"  Google OAuth: {'✅ Enabled' if status['google_oauth_enabled'] else '❌ Disabled'}")
            print(f"  GitHub OAuth: {'✅ Enabled' if status['github_oauth_enabled'] else '❌ Disabled'}")
            print(f"  Google Client ID: {'✅ Configured' if status['google_client_id_configured'] else '❌ Not Configured'}")
            print(f"  GitHub Client ID: {'✅ Configured' if status['github_client_id_configured'] else '❌ Not Configured'}")
            
            return status
        else:
            print_error(f"OAuth status endpoint returned {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print_error("Could not connect to OAuth status endpoint. Is the backend running?")
        return None
    except Exception as e:
        print_error(f"Error testing OAuth status: {e}")
        return None


def test_oauth_start_endpoints():
    """Test OAuth start endpoints"""
    print_step("Testing OAuth Start Endpoints")
    
    # Test Google OAuth start
    try:
        response = requests.get("http://localhost:8000/auth/google", timeout=10, allow_redirects=False)
        
        if response.status_code == 302:
            print_success("Google OAuth start endpoint working (redirects to Google)")
            print(f"  Redirect URL: {response.headers.get('Location', 'Not found')}")
        elif response.status_code == 400:
            print_error("Google OAuth start endpoint returned 400 - OAuth may not be enabled")
        else:
            print_error(f"Google OAuth start endpoint returned {response.status_code}")
            
    except Exception as e:
        print_error(f"Error testing Google OAuth start: {e}")
    
    # Test GitHub OAuth start
    try:
        response = requests.get("http://localhost:8000/auth/github", timeout=10, allow_redirects=False)
        
        if response.status_code == 302:
            print_success("GitHub OAuth start endpoint working (redirects to GitHub)")
            print(f"  Redirect URL: {response.headers.get('Location', 'Not found')}")
        elif response.status_code == 400:
            print_error("GitHub OAuth start endpoint returned 400 - OAuth may not be enabled")
        else:
            print_error(f"GitHub OAuth start endpoint returned {response.status_code}")
            
    except Exception as e:
        print_error(f"Error testing GitHub OAuth start: {e}")


def test_oauth_callback_endpoints():
    """Test OAuth callback endpoints (without valid codes)"""
    print_step("Testing OAuth Callback Endpoints")
    
    # Test Google OAuth callback with invalid code
    try:
        response = requests.get("http://localhost:8000/auth/callback/google?code=invalid_code", timeout=10)
        
        if response.status_code == 400:
            print_success("Google OAuth callback endpoint working (rejects invalid codes)")
        else:
            print_error(f"Google OAuth callback endpoint returned {response.status_code}")
            
    except Exception as e:
        print_error(f"Error testing Google OAuth callback: {e}")
    
    # Test GitHub OAuth callback with invalid code
    try:
        response = requests.get("http://localhost:8000/auth/callback/github?code=invalid_code", timeout=10)
        
        if response.status_code == 400:
            print_success("GitHub OAuth callback endpoint working (rejects invalid codes)")
        else:
            print_error(f"GitHub OAuth callback endpoint returned {response.status_code}")
            
    except Exception as e:
        print_error(f"Error testing GitHub OAuth callback: {e}")


def check_environment_config():
    """Check environment configuration"""
    print_step("Checking Environment Configuration")
    
    try:
        settings = get_settings()
        
        print_info("Backend OAuth Configuration:")
        print(f"  Google OAuth Enabled: {settings.security.google_oauth_enabled}")
        print(f"  Google Client ID: {'✅ Set' if settings.security.google_client_id else '❌ Not Set'}")
        print(f"  Google Client Secret: {'✅ Set' if settings.security.google_client_secret else '❌ Not Set'}")
        print(f"  GitHub OAuth Enabled: {settings.security.github_oauth_enabled}")
        print(f"  GitHub Client ID: {'✅ Set' if settings.security.github_client_id else '❌ Not Set'}")
        print(f"  GitHub Client Secret: {'✅ Set' if settings.security.github_client_secret else '❌ Not Set'}")
        
        return True
        
    except Exception as e:
        print_error(f"Error checking environment configuration: {e}")
        return False


def check_frontend_env():
    """Check frontend environment configuration"""
    print_step("Checking Frontend Environment Configuration")
    
    frontend_env = PROJECT_ROOT / "ui" / ".env.local"
    
    if frontend_env.exists():
        print_success("Frontend environment file exists")
        
        with open(frontend_env, 'r') as f:
            content = f.read()
            
        google_client_id = "VITE_GOOGLE_CLIENT_ID=" in content
        github_client_id = "VITE_GITHUB_CLIENT_ID=" in content
        
        print(f"  Google Client ID: {'✅ Set' if google_client_id else '❌ Not Set'}")
        print(f"  GitHub Client ID: {'✅ Set' if github_client_id else '❌ Not Set'}")
        
    else:
        print_error("Frontend environment file (.env.local) not found")
        print_info("Run 'python scripts/setup_oauth_env.py' to create it")


def print_test_summary():
    """Print test summary and next steps"""
    print_header("OAuth Test Summary")
    
    print_info("OAuth testing complete!")
    print("\nIf all tests passed, your OAuth configuration is working correctly.")
    print("\nNext steps:")
    print("1. Test OAuth flows in the browser:")
    print("   - Navigate to http://localhost:3000/signin")
    print("   - Click 'Continue with Google' or 'Continue with GitHub'")
    print("   - Complete the OAuth flow")
    
    print("\n2. Monitor backend logs for OAuth activity")
    print("3. Check database for OAuth user creation")
    
    print("\nIf tests failed:")
    print("1. Check that the backend is running on port 8000")
    print("2. Verify OAuth environment variables are set correctly")
    print("3. Run 'python scripts/setup_oauth_env.py' to configure OAuth")
    print("4. Check OAuth app configuration in Google Cloud Console and GitHub")


def main():
    """Main function"""
    print_header("SaaS Factory OAuth Quick Test")
    
    print_info("This script will test your OAuth configuration quickly.")
    print_info("Make sure your backend is running on port 8000.")
    
    # Check if backend is accessible
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print_success("Backend is accessible")
    except:
        print_error("Backend is not accessible on port 8000")
        print_info("Please start the backend first:")
        print("  cd api_gateway && python -m uvicorn app:app --reload --port 8000")
        return
    
    # Run tests
    check_environment_config()
    check_frontend_env()
    test_oauth_status()
    test_oauth_start_endpoints()
    test_oauth_callback_endpoints()
    
    print_test_summary()


if __name__ == "__main__":
    main()
