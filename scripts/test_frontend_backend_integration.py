#!/usr/bin/env python3
"""
Frontend-Backend Integration Test Runner
Quick script to test the critical user flows without running full pytest suite

Usage:
    python scripts/test_frontend_backend_integration.py
    python scripts/test_frontend_backend_integration.py --api-url http://localhost:8000
    python scripts/test_frontend_backend_integration.py --quick
"""

import asyncio
import argparse
import sys
import os
import uuid
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the test class directly since we're running from scripts directory
import sys
sys.path.insert(0, str(project_root / 'tests' / 'integration'))

from test_frontend_backend_integration import (
    TestFrontendBackendIntegration,
    run_integration_tests
)


async def run_quick_tests(api_url: str):
    """Run a subset of critical tests for quick validation"""
    print("🚀 Running Quick Frontend-Backend Integration Tests...")
    
    # Create test instance
    test_instance = TestFrontendBackendIntegration()
    
    # Quick tests that validate core connectivity
    quick_tests = [
        ("API Gateway Health", test_instance.test_api_gateway_health_and_routing),
        ("Signup API", test_instance.test_signup_form_connects_to_backend),
        ("Login API", test_instance.test_login_form_connects_to_backend),
    ]
    
    results = []
    for test_name, test_func in quick_tests:
        try:
            print(f"\n🧪 Running {test_name}...")
            # Pass the API URL directly to the test methods
            if test_name == "API Gateway Health":
                await test_func(api_url)
            elif test_name == "Signup API":
                # Create test data directly instead of using fixtures
                signup_data = {
                    "firstName": "Jane",
                    "lastName": "Smith",
                    "email": f"test-{uuid.uuid4().hex[:8]}@example.com",
                    "password": "SecurePass123!",
                    "confirmPassword": "SecurePass123!",
                    "agreeToTerms": True
                }
                await test_func(api_url, signup_data)
            elif test_name == "Login API":
                # Create test data directly instead of using fixtures
                login_data = {
                    "email": "test@example.com",
                    "password": "SecurePass123!"
                }
                await test_func(api_url, login_data)
            results.append((test_name, "PASSED"))
            print(f"✅ {test_name} PASSED")
        except Exception as e:
            results.append((test_name, f"FAILED: {e}"))
            print(f"❌ {test_name} FAILED: {e}")
    
    # Print summary
    print("\n📊 Quick Test Results:")
    print("=" * 40)
    for test_name, result in results:
        status = "✅" if "PASSED" in result else "❌"
        print(f"{status} {test_name}: {result}")
    
    passed = sum(1 for _, result in results if "PASSED" in result)
    total = len(results)
    
    print(f"\n🎯 Quick Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All quick tests passed! Frontend-backend integration is working.")
        return True
    else:
        print("⚠️ Some quick tests failed. Check the backend API connectivity.")
        return False


async def run_full_tests(api_url: str):
    """Run all integration tests"""
    print("🚀 Running Full Frontend-Backend Integration Tests...")
    
    # Set environment variable for API URL
    if api_url:
        os.environ['TEST_API_URL'] = api_url
    
    # Run the full test suite
    await run_integration_tests()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Test frontend-backend integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run quick tests against localhost
    python scripts/test_frontend_backend_integration.py --quick
    
    # Run full tests against specific API
    python scripts/test_frontend_backend_integration.py --api-url http://localhost:8000
    
    # Run full tests against production
    python scripts/test_frontend_backend_integration.py --api-url https://api.forge95.com
        """
    )
    
    parser.add_argument(
        '--api-url',
        default='http://localhost:8000',
        help='API base URL to test against (default: http://localhost:8000)'
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run only quick tests for fast validation'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Set environment variable
    os.environ['TEST_API_URL'] = args.api_url
    
    print("🎯 Testing Frontend-Backend Integration")
    print(f"🔗 API URL: {args.api_url}")
    print(f"⚡ Mode: {'Quick' if args.quick else 'Full'}")
    print("=" * 60)
    
    try:
        if args.quick:
            success = asyncio.run(run_quick_tests(args.api_url))
        else:
            asyncio.run(run_full_tests(args.api_url))
            success = True  # Full tests will raise exceptions on failure
        
        if success:
            print("\n🎉 Frontend-Backend Integration Tests Completed Successfully!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Check the output above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
