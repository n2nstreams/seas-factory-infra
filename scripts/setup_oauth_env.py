#!/usr/bin/env python3
"""
OAuth Environment Setup Script
Interactive script to set up OAuth environment variables for SaaS Factory
"""

import os
import sys
from pathlib import Path
import getpass

def setup_backend_oauth():
    """Set up backend OAuth environment variables"""
    print("\n🔧 Backend OAuth Configuration")
    print("=" * 40)
    
    # Get Google OAuth credentials
    print("\n📱 Google OAuth Setup:")
    google_enabled = input("Enable Google OAuth? (y/n): ").lower().strip() == 'y'
    
    google_client_id = ""
    google_client_secret = ""
    
    if google_enabled:
        google_client_id = input("Enter Google Client ID: ").strip()
        google_client_secret = getpass.getpass("Enter Google Client Secret: ").strip()
    
    # Get GitHub OAuth credentials
    print("\n🐙 GitHub OAuth Setup:")
    github_enabled = input("Enable GitHub OAuth? (y/n): ").lower().strip() == 'y'
    
    github_client_id = ""
    github_client_secret = ""
    
    if github_enabled:
        github_client_id = input("Enter GitHub Client ID: ").strip()
        github_client_secret = getpass.getpass("Enter GitHub Client Secret: ").strip()
    
    # Generate backend environment configuration
    backend_config = f"""# OAuth Configuration
GOOGLE_OAUTH_ENABLED={str(google_enabled).lower()}
GOOGLE_CLIENT_ID={google_client_id}
GOOGLE_CLIENT_SECRET={google_client_secret}
GOOGLE_REDIRECT_URI=/auth/callback/google

GITHUB_OAUTH_ENABLED={str(github_enabled).lower()}
GITHUB_CLIENT_ID={github_client_id}
GITHUB_CLIENT_SECRET={github_client_secret}
GITHUB_REDIRECT_URI=/auth/callback/github
"""
    
    return backend_config, {
        'google_enabled': google_enabled,
        'google_client_id': google_client_id,
        'github_enabled': github_enabled,
        'github_client_id': github_client_id
    }

def setup_frontend_oauth(oauth_info):
    """Set up frontend OAuth environment variables"""
    print("\n🎨 Frontend OAuth Configuration")
    print("=" * 40)
    
    frontend_config = """# OAuth Configuration
"""
    
    if oauth_info['google_enabled'] and oauth_info['google_client_id']:
        frontend_config += f"VITE_GOOGLE_CLIENT_ID={oauth_info['google_client_id']}\n"
    
    if oauth_info['github_enabled'] and oauth_info['github_client_id']:
        frontend_config += f"VITE_GITHUB_CLIENT_ID={oauth_info['github_client_id']}\n"
    
    frontend_config += """# API Configuration
VITE_API_BASE_URL=http://localhost:8000
"""
    
    return frontend_config

def write_environment_file(content, filepath, description):
    """Write environment configuration to file"""
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ {description} written to {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error writing {filepath}: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 SaaS Factory OAuth Environment Setup")
    print("=" * 50)
    print("This script will help you configure OAuth environment variables")
    print("You'll need to create OAuth apps in Google Cloud Console and GitHub first")
    print("\nSee docs/oauth_setup_complete.md for detailed OAuth app setup instructions")
    
    # Check if user wants to proceed
    proceed = input("\nDo you have your OAuth credentials ready? (y/n): ").lower().strip()
    if proceed != 'y':
        print("\n📋 Please complete these steps first:")
        print("1. Create Google OAuth app in Google Cloud Console")
        print("2. Create GitHub OAuth app in GitHub Developer Settings")
        print("3. Get your Client ID and Client Secret for each")
        print("4. Run this script again")
        return
    
    # Set up backend OAuth
    backend_config, oauth_info = setup_backend_oauth()
    
    # Set up frontend OAuth
    frontend_config = setup_frontend_oauth(oauth_info)
    
    # Write configuration files
    print("\n💾 Writing Configuration Files")
    print("=" * 40)
    
    # Backend configuration
    backend_env_path = Path("config/environments/development.env")
    if backend_env_path.exists():
        # Read existing file and update OAuth section
        with open(backend_env_path, 'r') as f:
            existing_content = f.read()
        
        # Find and replace OAuth section
        oauth_start = existing_content.find("# OAuth Configuration")
        if oauth_start != -1:
            # Find the end of OAuth section
            lines = existing_content.split('\n')
            oauth_end = oauth_start
            for i, line in enumerate(lines[oauth_start:], oauth_start):
                if line.strip() == "" or (line.startswith("#") and "OAuth" not in line):
                    oauth_end = i
                    break
            
            # Replace OAuth section
            new_content = lines[:oauth_start] + [backend_config] + lines[oauth_end:]
            backend_config = '\n'.join(new_content)
        
        write_environment_file(backend_config, backend_env_path, "Backend OAuth configuration")
    else:
        print(f"⚠️  Backend environment file not found: {backend_env_path}")
        print("   Please create it manually or copy from config/environments/development.env.example")
    
    # Frontend configuration
    frontend_env_path = Path("ui/.env.local")
    write_environment_file(frontend_config, frontend_env_path, "Frontend OAuth configuration")
    
    # Summary
    print("\n" + "=" * 50)
    print("🎉 OAuth Environment Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Restart your backend service to load new environment variables")
    print("2. Restart your frontend service to load new environment variables")
    print("3. Test OAuth configuration with: python scripts/test_oauth_config.py")
    print("4. Test OAuth flows in your application")
    
    if oauth_info['google_enabled'] or oauth_info['github_enabled']:
        print("\n🔍 To test OAuth:")
        print("1. Start backend: cd api_gateway && python -m uvicorn app:app --reload --port 8000")
        print("2. Start frontend: cd ui && npm run dev")
        print("3. Go to http://localhost:3000/signin")
        print("4. Click OAuth buttons to test flows")

if __name__ == "__main__":
    main()
