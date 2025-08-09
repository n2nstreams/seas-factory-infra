#!/usr/bin/env python3
"""
Smoke Test Runner for AI SaaS Factory
Runs critical path tests for marketplace signup flow

Usage:
    python scripts/run_smoke_tests.py
    python scripts/run_smoke_tests.py --fast
    python scripts/run_smoke_tests.py --verbose
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path


def setup_environment():
    """Set up environment variables for smoke tests"""
    os.environ.update({
        'ENVIRONMENT': 'test',
        'DEBUG': 'true',
        'MOCK_EMAIL_SERVICE': 'true',
        'MOCK_STRIPE_SERVICE': 'true',
        'SMOKE_TEST_MODE': 'true',
        'DATABASE_URL': 'postgresql://factoryadmin:localpass@localhost:5432/factorydb',
        'DB_HOST': 'localhost',
        'DB_USER': 'factoryadmin',
        'DB_PASS': 'localpass',
        'DB_NAME': 'factorydb',
        'DB_PORT': '5432'
    })


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'pytest',
        'pytest-asyncio',
        'fastapi',
        'asyncpg',
        'bcrypt',
        'pydantic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    return True


def check_database_connection():
    """Check if database is accessible"""
    try:
        import asyncpg
        import asyncio
        
        async def test_connection():
            try:
                conn = await asyncpg.connect(
                    host='localhost',
                    port=5432,
                    user='factoryadmin',
                    password='localpass',
                    database='factorydb'
                )
                await conn.close()
                return True
            except Exception:
                return False
        
        return asyncio.run(test_connection())
    except Exception:
        return False


def run_api_health_check():
    """Run quick API health check"""
    print("🔍 Running API health check...")
    
    try:
        # Check API routes can be imported
        sys.path.insert(0, 'api-gateway')
        
        try:
            from user_routes import router
            print("✅ User routes imported successfully")
            
            # Check for critical endpoints
            routes = [route.path for route in router.routes]
            critical_endpoints = ['/api/users/register', '/api/users/login', '/api/users/profile']
            
            for endpoint in critical_endpoints:
                if any(endpoint in route for route in routes):
                    print(f"✅ Found critical endpoint: {endpoint}")
                else:
                    print(f"❌ Missing critical endpoint: {endpoint}")
                    return False
            
            print("🎉 All critical API endpoints are present")
            return True
            
        except ImportError as e:
            print(f"❌ Failed to import API routes: {e}")
            return False
            
    except Exception as e:
        print(f"❌ API health check failed: {e}")
        return False


def run_frontend_validation():
    """Validate frontend signup form exists and has required fields"""
    print("🔍 Validating frontend signup form...")
    
    signup_file = Path("ui/src/pages/Signup.tsx")
    
    if not signup_file.exists():
        print("❌ Signup page not found!")
        return False
    
    print("✅ Signup page exists")
    
    # Check for required form fields
    required_fields = [
        "firstName", "lastName", "email", "password",
        "confirmPassword", "agreeToTerms"
    ]
    
    content = signup_file.read_text()
    
    for field in required_fields:
        if field in content:
            print(f"✅ Found required field: {field}")
        else:
            print(f"❌ Missing required field: {field}")
            return False
    
    print("🎉 All required form fields are present")
    return True


def run_smoke_tests(test_mode="normal", verbose=False):
    """Run the actual smoke tests"""
    print("🚀 Running marketplace signup smoke tests...")
    
    # Build pytest command
    cmd = [
        "python", "-m", "pytest", 
        "tests/integration/test_marketplace_signup_smoke.py",
        "--tb=short"
    ]
    
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    if test_mode == "fast":
        # Run only the end-to-end test for fast feedback
        cmd.append("::test_end_to_end_marketplace_signup")
        cmd.extend(["--durations=5", "-x"])
    elif test_mode == "full":
        # Run all smoke tests
        cmd.extend(["--durations=10", "--timeout=300"])
    
    # Run the tests
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=False)
    end_time = time.time()
    
    duration = end_time - start_time
    
    if result.returncode == 0:
        print(f"✅ Smoke tests passed in {duration:.2f}s!")
        return True
    else:
        print(f"❌ Smoke tests failed after {duration:.2f}s")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run marketplace signup smoke tests")
    parser.add_argument("--fast", action="store_true", 
                       help="Run only the critical end-to-end test")
    parser.add_argument("--full", action="store_true",
                       help="Run all smoke tests (default)")
    parser.add_argument("--verbose", action="store_true",
                       help="Verbose output")
    parser.add_argument("--skip-deps", action="store_true",
                       help="Skip dependency checks")
    
    args = parser.parse_args()
    
    print("🎯 AI SaaS Factory - Marketplace Signup Smoke Tests")
    print("=" * 60)
    
    # Determine test mode
    if args.fast:
        test_mode = "fast"
    else:
        test_mode = "full"
    
    print(f"Test mode: {test_mode}")
    print(f"Verbose: {args.verbose}")
    print()
    
    # Set up environment
    setup_environment()
    
    # Run pre-flight checks
    if not args.skip_deps:
        print("🔧 Checking dependencies...")
        if not check_dependencies():
            return 1
        print("✅ Dependencies OK")
        print()
    
    print("🗄️  Checking database connection...")
    if not check_database_connection():
        print("❌ Database connection failed!")
        print("   Make sure PostgreSQL is running on localhost:5432")
        print("   with user 'factoryadmin', password 'localpass', database 'factorydb'")
        return 1
    print("✅ Database connection OK")
    print()
    
    # Run health checks
    if not run_api_health_check():
        return 1
    print()
    
    if not run_frontend_validation():
        return 1
    print()
    
    # Run smoke tests
    success = run_smoke_tests(test_mode, args.verbose)
    
    print()
    print("📊 Smoke Test Summary:")
    print("=" * 30)
    
    if success:
        print("✅ All smoke tests passed!")
        print("🎉 Marketplace signup flow is healthy and ready for production")
        return 0
    else:
        print("❌ Smoke tests failed!")
        print("🔍 Review the test output above for details")
        print("💡 Run with --verbose for more detailed output")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 