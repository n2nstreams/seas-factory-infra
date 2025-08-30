#!/usr/bin/env python3
"""
Test Environment Configuration
Checks environment variables and provides guidance for third-party integrations
"""

import os
from typing import Dict, List

def check_environment_config():
    """Check environment configuration and provide guidance"""
    print("🔧 Environment Configuration Check")
    print("=" * 50)
    
    # Required environment variables
    required_vars = {
        "STRIPE_SECRET_KEY": "Stripe payment integration",
        "SENDGRID_API_KEY": "SendGrid email service", 
        "GITHUB_TOKEN": "GitHub API integration"
    }
    
    # Optional but recommended
    optional_vars = {
        "DATABASE_URL": "Database connection string",
        "REDIS_URL": "Redis cache connection",
        "JWT_SECRET": "JWT token signing",
        "CORS_ORIGINS": "CORS allowed origins"
    }
    
    print("\n📋 Required Environment Variables:")
    print("-" * 35)
    
    missing_required = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {description} - Configured")
        else:
            print(f"❌ {var}: {description} - NOT CONFIGURED")
            missing_required.append(var)
    
    print("\n📋 Optional Environment Variables:")
    print("-" * 35)
    
    missing_optional = []
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {description} - Configured")
        else:
            print(f"⚠️ {var}: {description} - Not configured (optional)")
            missing_optional.append(var)
    
    print("\n🎯 Configuration Status:")
    print("-" * 25)
    
    if not missing_required:
        print("✅ All required environment variables are configured!")
        print("🎉 Your system is ready for production use.")
    else:
        print(f"❌ {len(missing_required)} required environment variables are missing:")
        for var in missing_required:
            print(f"   - {var}")
        print("\n🔧 To configure these variables:")
        print("   1. Create a .env file in your project root")
        print("   2. Add the missing variables with their values")
        print("   3. Restart your application")
    
    print("\n📝 Sample .env file:")
    print("-" * 20)
    print("# SaaS Factory Environment Configuration")
    print("# Copy this to .env and fill in your values")
    print("")
    
    for var, description in required_vars.items():
        print(f"# {description}")
        print(f"{var}=your_{var.lower()}_here")
        print("")
    
    for var, description in optional_vars.items():
        print(f"# {description} (optional)")
        print(f"# {var}=your_{var.lower()}_here")
        print("")
    
    print("# Other configuration")
    print("API_BASE_URL=http://localhost:8000")
    print("ENVIRONMENT=development")
    
    return len(missing_required) == 0

if __name__ == "__main__":
    check_environment_config()
