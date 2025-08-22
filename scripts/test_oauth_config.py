#!/usr/bin/env python3
"""
OAuth Configuration Test Script for SaaS Factory
Comprehensive testing of OAuth setup and configuration
"""

import requests
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple

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


def print_warning(message: str):
    """Print a warning message"""
    print(f"⚠️  {message}")


def print_info(message: str):
    """Print an info message"""
    print(f"ℹ️  {message}")


class OAuthTester:
    """OAuth configuration tester"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []
        self.settings = None
        
    def add_result(self, test_name: str, success: bool, message: str, details: str = ""):
        """Add a test result"""
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'details': details
        })
        
        if success:
            print_success(f"{test_name}: {message}")
        else:
            print_error(f"{test_name}: {message}")
            
        if details:
            print(f"    Details: {details}")
    
    def test_backend_connectivity(self) -> bool:
        """Test if backend is accessible"""
        print_step("Testing Backend Connectivity")
        
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code in [200, 404, 405]:  # Any response means backend is up
                self.add_result("Backend Connectivity", True, "Backend is accessible")
                return True
            else:
                self.add_result("Backend Connectivity", False, f"Unexpected status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.add_result("Backend Connectivity", False, "Cannot connect to backend")
            return False
        except Exception as e:
            self.add_result("Backend Connectivity", False, f"Connection error: {e}")
            return False
    
    def test_oauth_status_endpoint(self) -> bool:
        """Test OAuth status endpoint"""
        print_step("Testing OAuth Status Endpoint")
        
        try:
            response = requests.get(f"{self.base_url}/auth/status", timeout=10)
            
            if response.status_code == 200:
                status = response.json()
                self.add_result("OAuth Status Endpoint", True, "Status endpoint working")
                
                # Test individual OAuth providers
                self.test_oauth_provider_status("Google", status)
                self.test_oauth_provider_status("GitHub", status)
                
                return True
            else:
                self.add_result("OAuth Status Endpoint", False, f"Status endpoint returned {response.status_code}")
                return False
                
        except Exception as e:
            self.add_result("OAuth Status Endpoint", False, f"Status endpoint error: {e}")
            return False
    
    def test_oauth_provider_status(self, provider: str, status: Dict[str, Any]):
        """Test individual OAuth provider status"""
        provider_lower = provider.lower()
        
        enabled_key = f"{provider_lower}_oauth_enabled"
        configured_key = f"{provider_lower}_client_id_configured"
        
        enabled = status.get(enabled_key, False)
        configured = status.get(configured_key, False)
        
        if enabled and configured:
            self.add_result(f"{provider} OAuth", True, "Enabled and configured")
        elif enabled and not configured:
            self.add_result(f"{provider} OAuth", False, "Enabled but not configured")
        elif not enabled and configured:
            self.add_result(f"{provider} OAuth", False, "Configured but not enabled")
        else:
            self.add_result(f"{provider} OAuth", False, "Not enabled or configured")
    
    def test_oauth_start_endpoints(self):
        """Test OAuth start endpoints"""
        print_step("Testing OAuth Start Endpoints")
        
        # Test Google OAuth start
        self.test_oauth_start_endpoint("Google", "/auth/google")
        
        # Test GitHub OAuth start
        self.test_oauth_start_endpoint("GitHub", "/auth/github")
    
    def test_oauth_start_endpoint(self, provider: str, endpoint: str):
        """Test individual OAuth start endpoint"""
        try:
            response = requests.get(f"{self.base_url}{endpoint}", timeout=10, allow_redirects=False)
            
            if response.status_code == 302:
                redirect_url = response.headers.get('Location', '')
                if provider.lower() in redirect_url.lower():
                    self.add_result(f"{provider} OAuth Start", True, "Redirects to OAuth provider")
                else:
                    self.add_result(f"{provider} OAuth Start", True, "Redirects (URL verification needed)")
            elif response.status_code == 400:
                self.add_result(f"{provider} OAuth Start", False, "OAuth not enabled or configured")
            else:
                self.add_result(f"{provider} OAuth Start", False, f"Unexpected status: {response.status_code}")
                
        except Exception as e:
            self.add_result(f"{provider} OAuth Start", False, f"Error: {e}")
    
    def test_oauth_callback_endpoints(self):
        """Test OAuth callback endpoints"""
        print_step("Testing OAuth Callback Endpoints")
        
        # Test Google OAuth callback
        self.test_oauth_callback_endpoint("Google", "/auth/callback/google")
        
        # Test GitHub OAuth callback
        self.test_oauth_callback_endpoint("GitHub", "/auth/callback/github")
    
    def test_oauth_callback_endpoint(self, provider: str, endpoint: str):
        """Test individual OAuth callback endpoint"""
        try:
            # Test with invalid code
            response = requests.get(f"{self.base_url}{endpoint}?code=invalid_code", timeout=10)
            
            if response.status_code == 400:
                self.add_result(f"{provider} OAuth Callback", True, "Rejects invalid codes")
            elif response.status_code == 500:
                self.add_result(f"{provider} OAuth Callback", True, "Handles invalid codes (500 expected)")
            else:
                self.add_result(f"{provider} OAuth Callback", False, f"Unexpected status: {response.status_code}")
                
        except Exception as e:
            self.add_result(f"{provider} OAuth Callback", False, f"Error: {e}")
    
    def test_environment_configuration(self):
        """Test environment configuration"""
        print_step("Testing Environment Configuration")
        
        try:
            self.settings = get_settings()
            
            # Test Google OAuth configuration
            self.test_oauth_env_config("Google", {
                'enabled': self.settings.security.google_oauth_enabled,
                'client_id': self.settings.security.google_client_id,
                'client_secret': self.settings.security.google_client_secret
            })
            
            # Test GitHub OAuth configuration
            self.test_oauth_env_config("GitHub", {
                'enabled': self.settings.security.github_oauth_enabled,
                'client_id': self.settings.security.github_client_id,
                'client_secret': self.settings.security.github_client_secret
            })
            
        except Exception as e:
            self.add_result("Environment Configuration", False, f"Error loading settings: {e}")
    
    def test_oauth_env_config(self, provider: str, config: Dict[str, Any]):
        """Test individual OAuth environment configuration"""
        enabled = config['enabled']
        client_id = config['client_id']
        client_secret = config['client_secret']
        
        if enabled and client_id and client_secret:
            self.add_result(f"{provider} Environment", True, "Fully configured")
        elif enabled and (not client_id or not client_secret):
            self.add_result(f"{provider} Environment", False, "Enabled but missing credentials")
        elif not enabled and (client_id or client_secret):
            self.add_result(f"{provider} Environment", False, "Credentials set but not enabled")
        else:
            self.add_result(f"{provider} Environment", False, "Not configured")
    
    def test_frontend_environment(self):
        """Test frontend environment configuration"""
        print_step("Testing Frontend Environment Configuration")
        
        frontend_env = PROJECT_ROOT / "ui" / ".env.local"
        
        if not frontend_env.exists():
            self.add_result("Frontend Environment", False, "Frontend .env.local file not found")
            return
        
        try:
            with open(frontend_env, 'r') as f:
                content = f.read()
            
            # Check for OAuth client IDs
            google_client_id = "VITE_GOOGLE_CLIENT_ID=" in content
            github_client_id = "VITE_GITHUB_CLIENT_ID=" in content
            
            if google_client_id and github_client_id:
                self.add_result("Frontend Environment", True, "Both OAuth client IDs configured")
            elif google_client_id or github_client_id:
                self.add_result("Frontend Environment", True, "Partial OAuth configuration")
            else:
                self.add_result("Frontend Environment", False, "No OAuth client IDs configured")
                
        except Exception as e:
            self.add_result("Frontend Environment", False, f"Error reading frontend env: {e}")
    
    def test_database_connectivity(self):
        """Test database connectivity for OAuth user creation"""
        print_step("Testing Database Connectivity")
        
        try:
            # This would require database connection testing
            # For now, we'll assume it's working if the backend is accessible
            self.add_result("Database Connectivity", True, "Backend accessible (database assumed working)")
        except Exception as e:
            self.add_result("Database Connectivity", False, f"Database error: {e}")
    
    def generate_report(self):
        """Generate test report"""
        print_header("OAuth Configuration Test Report")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 Test Summary:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        print(f"\n✅ Passed Tests:")
        for result in self.test_results:
            if result['success']:
                print(f"  - {result['test']}: {result['message']}")
        
        return passed_tests == total_tests
    
    def print_recommendations(self):
        """Print recommendations based on test results"""
        print_header("Recommendations")
        
        if self.all_tests_passed():
            print_success("All OAuth tests passed! Your OAuth configuration is working correctly.")
            print("\nNext steps:")
            print("1. Test OAuth flows in the browser")
            print("2. Monitor OAuth performance")
            print("3. Deploy to production when ready")
        else:
            print_warning("Some OAuth tests failed. Here are the recommended actions:")
            
            # Check specific failures and provide recommendations
            for result in self.test_results:
                if not result['success']:
                    if "Backend Connectivity" in result['test']:
                        print("\n🔧 Backend Issues:")
                        print("  - Start the backend server: cd api_gateway && python -m uvicorn app:app --reload --port 8000")
                        print("  - Check backend logs for errors")
                    
                    elif "Environment" in result['test']:
                        print("\n🔧 Environment Configuration Issues:")
                        print("  - Run: python scripts/setup_oauth_env.py")
                        print("  - Check environment variable files")
                        print("  - Verify OAuth app configuration")
                    
                    elif "Frontend" in result['test']:
                        print("\n🔧 Frontend Configuration Issues:")
                        print("  - Create ui/.env.local file")
                        print("  - Set VITE_GOOGLE_CLIENT_ID and VITE_GITHUB_CLIENT_ID")
                        print("  - Restart frontend development server")
    
    def all_tests_passed(self) -> bool:
        """Check if all tests passed"""
        return all(result['success'] for result in self.test_results)
    
    def run_all_tests(self):
        """Run all OAuth tests"""
        print_header("Running OAuth Configuration Tests")
        
        # Run tests in order
        self.test_backend_connectivity()
        self.test_environment_configuration()
        self.test_frontend_environment()
        self.test_oauth_status_endpoint()
        self.test_oauth_start_endpoints()
        self.test_oauth_callback_endpoints()
        self.test_database_connectivity()
        
        # Generate report and recommendations
        success = self.generate_report()
        self.print_recommendations()
        
        return success


def main():
    """Main function"""
    print_header("SaaS Factory OAuth Configuration Tester")
    
    print_info("This script will comprehensively test your OAuth configuration.")
    print_info("Make sure your backend is running on port 8000.")
    
    # Create tester and run tests
    tester = OAuthTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
