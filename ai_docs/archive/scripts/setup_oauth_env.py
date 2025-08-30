#!/usr/bin/env python3
"""
OAuth Environment Setup Script for SaaS Factory
Helps configure OAuth environment variables for development and production
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config" / "environments"
UI_DIR = PROJECT_ROOT / "ui"


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


def get_oauth_config() -> Dict[str, Any]:
    """Get OAuth configuration from user input"""
    print_header("OAuth Configuration Setup")
    print_info("This script will help you configure OAuth environment variables.")
    print_info("You'll need your Google and GitHub OAuth app credentials.")
    
    config = {}
    
    # Google OAuth
    print_step("Google OAuth Configuration")
    config['google_enabled'] = input("Enable Google OAuth? (y/n): ").lower().startswith('y')
    
    if config['google_enabled']:
        config['google_client_id'] = input("Google Client ID: ").strip()
        config['google_client_secret'] = input("Google Client Secret: ").strip()
        
        if not config['google_client_id'] or not config['google_client_secret']:
            print_error("Google OAuth credentials are required if enabled")
            return None
    
    # GitHub OAuth
    print_step("GitHub OAuth Configuration")
    config['github_enabled'] = input("Enable GitHub OAuth? (y/n): ").lower().startswith('y')
    
    if config['github_enabled']:
        config['github_client_id'] = input("GitHub Client ID: ").strip()
        config['github_client_secret'] = input("GitHub Client Secret: ").strip()
        
        if not config['github_client_id'] or not config['github_client_secret']:
            print_error("GitHub OAuth credentials are required if enabled")
            return None
    
    return config


def update_backend_env(env_file: Path, config: Dict[str, Any], environment: str):
    """Update backend environment file with OAuth configuration"""
    print_step(f"Updating {environment} backend environment file")
    
    if not env_file.exists():
        print_error(f"Environment file {env_file} does not exist")
        return False
    
    # Read existing content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Update OAuth configuration
    updates = []
    
    if config['google_enabled']:
        updates.extend([
            ('GOOGLE_OAUTH_ENABLED=false', 'GOOGLE_OAUTH_ENABLED=true'),
            ('GOOGLE_CLIENT_ID=', f"GOOGLE_CLIENT_ID={config['google_client_id']}"),
            ('GOOGLE_CLIENT_SECRET=', f"GOOGLE_CLIENT_SECRET={config['google_client_secret']}")
        ])
    
    if config['github_enabled']:
        updates.extend([
            ('GITHUB_OAUTH_ENABLED=false', 'GITHUB_OAUTH_ENABLED=true'),
            ('GITHUB_CLIENT_ID=', f"GITHUB_CLIENT_ID={config['github_client_id']}"),
            ('GITHUB_CLIENT_SECRET=', f"GITHUB_CLIENT_SECRET={config['github_client_secret']}")
        ])
    
    # Apply updates
    for old, new in updates:
        if old in content:
            content = content.replace(old, new)
            print_success(f"Updated: {old.split('=')[0]}")
        else:
            print_error(f"Could not find: {old}")
    
    # Write updated content
    with open(env_file, 'w') as f:
        f.write(content)
    
    print_success(f"Updated {env_file}")
    return True


def create_frontend_env(config: Dict[str, Any]):
    """Create frontend environment file with OAuth configuration"""
    print_step("Creating frontend environment file")
    
    env_file = UI_DIR / ".env.local"
    
    # Create frontend environment content
    env_content = [
        "# SaaS Factory Frontend Environment Configuration",
        "# OAuth Configuration",
    ]
    
    if config['google_enabled']:
        env_content.append(f"VITE_GOOGLE_CLIENT_ID={config['google_client_id']}")
    
    if config['github_enabled']:
        env_content.append(f"VITE_GITHUB_CLIENT_ID={config['github_client_id']}")
    
    env_content.extend([
        "",
        "# API Configuration",
        "VITE_API_BASE_URL=http://localhost:8000",
        "",
        "# Feature Flags",
        "VITE_GROWTHBOOK_CLIENT_KEY=your_growthbook_key_here"
    ])
    
    # Write frontend environment file
    with open(env_file, 'w') as f:
        f.write('\n'.join(env_content))
    
    print_success(f"Created {env_file}")
    return True


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate OAuth configuration"""
    print_step("Validating OAuth Configuration")
    
    errors = []
    
    if config['google_enabled']:
        if not config['google_client_id']:
            errors.append("Google Client ID is required when Google OAuth is enabled")
        if not config['google_client_secret']:
            errors.append("Google Client Secret is required when Google OAuth is enabled")
    
    if config['github_enabled']:
        if not config['github_client_id']:
            errors.append("GitHub Client ID is required when GitHub OAuth is enabled")
        if not config['github_client_secret']:
            errors.append("GitHub Client Secret is required when GitHub OAuth is enabled")
    
    if not config['google_enabled'] and not config['github_enabled']:
        errors.append("At least one OAuth provider must be enabled")
    
    if errors:
        print_error("Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print_success("OAuth configuration validation passed")
    return True


def create_oauth_status_check():
    """Create a script to check OAuth status"""
    print_step("Creating OAuth status check script")
    
    script_content = '''#!/usr/bin/env python3
"""
OAuth Status Check Script
Quickly check OAuth configuration status
"""

import requests
import sys

def check_oauth_status():
    """Check OAuth status from the API"""
    try:
        # Try to connect to the API
        response = requests.get("http://localhost:8000/auth/status", timeout=5)
        
        if response.status_code == 200:
            status = response.json()
            print("OAuth Status:")
            print(f"  Google OAuth: {'✅ Enabled' if status['google_oauth_enabled'] else '❌ Disabled'}")
            print(f"  GitHub OAuth: {'✅ Enabled' if status['github_oauth_enabled'] else '❌ Disabled'}")
            print(f"  Google Client ID: {'✅ Configured' if status['google_client_id_configured'] else '❌ Not Configured'}")
            print(f"  GitHub Client ID: {'✅ Configured' if status['github_client_id_configured'] else '❌ Not Configured'}")
        else:
            print(f"❌ API returned status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Is the backend running?")
    except Exception as e:
        print(f"❌ Error checking OAuth status: {e}")

if __name__ == "__main__":
    check_oauth_status()
'''
    
    script_file = PROJECT_ROOT / "scripts" / "check_oauth_status.py"
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(script_file, 0o755)
    
    print_success(f"Created {script_file}")
    return True


def print_next_steps(config: Dict[str, Any]):
    """Print next steps for the user"""
    print_header("Next Steps")
    
    print_info("OAuth environment configuration complete!")
    
    if config['google_enabled']:
        print("1. ✅ Google OAuth configured")
    if config['github_enabled']:
        print("1. ✅ GitHub OAuth configured")
    
    print("\nNext steps:")
    print("1. Start the backend server:")
    print("   cd api_gateway && python -m uvicorn app:app --reload --port 8000")
    
    print("2. Start the frontend server:")
    print("   cd ui && npm run dev")
    
    print("3. Test OAuth flows:")
    print("   - Navigate to http://localhost:3000/signin")
    print("   - Click 'Continue with Google' or 'Continue with GitHub'")
    
    print("4. Check OAuth status:")
    print("   python scripts/check_oauth_status.py")
    
    print("\nFor production deployment:")
    print("1. Update OAuth app settings with production URLs")
    print("2. Update production environment files")
    print("3. Deploy with updated configuration")


def main():
    """Main function"""
    print_header("SaaS Factory OAuth Environment Setup")
    
    # Check if we're in the right directory
    if not CONFIG_DIR.exists():
        print_error("This script must be run from the SaaS Factory project root")
        sys.exit(1)
    
    # Get OAuth configuration
    config = get_oauth_config()
    if not config:
        print_error("Failed to get OAuth configuration")
        sys.exit(1)
    
    # Validate configuration
    if not validate_config(config):
        print_error("OAuth configuration validation failed")
        sys.exit(1)
    
    # Update backend environment files
    success = True
    
    # Update development environment
    dev_env = CONFIG_DIR / "development.env"
    if dev_env.exists():
        success &= update_backend_env(dev_env, config, "development")
    
    # Update production environment
    prod_env = CONFIG_DIR / "production.env"
    if prod_env.exists():
        success &= update_backend_env(prod_env, config, "production")
    
    # Create frontend environment file
    success &= create_frontend_env(config)
    
    # Create OAuth status check script
    success &= create_oauth_status_check()
    
    if success:
        print_next_steps(config)
    else:
        print_error("Some configuration updates failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
