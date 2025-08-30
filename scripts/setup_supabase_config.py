#!/usr/bin/env python3
"""
Supabase Configuration Setup Script
This script helps set up Supabase environment variables for data integrity verification.
"""

import os
import re
from pathlib import Path
from typing import Dict, Optional

class SupabaseConfigSetup:
    """Helps set up Supabase configuration"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.env_file = self.root_dir / ".env"
        self.backup_file = self.root_dir / ".env.backup.supabase"
        
    def backup_env_file(self) -> bool:
        """Backup the current .env file"""
        try:
            if self.env_file.exists():
                import shutil
                shutil.copy2(self.env_file, self.backup_file)
                print(f"✅ Backed up .env to {self.backup_file}")
                return True
            return False
        except Exception as e:
            print(f"❌ Failed to backup .env file: {e}")
            return False
    
    def get_current_supabase_config(self) -> Dict[str, Optional[str]]:
        """Get current Supabase configuration from .env file"""
        config = {}
        
        if not self.env_file.exists():
            return config
        
        with open(self.env_file, 'r') as f:
            content = f.read()
            
        # Extract Supabase-related variables
        supabase_vars = [
            'SUPABASE_URL',
            'SUPABASE_ANON_KEY',
            'SUPABASE_SERVICE_ROLE_KEY',
            'SUPABASE_DB_HOST',
            'SUPABASE_DB_PORT',
            'SUPABASE_DB_NAME',
            'SUPABASE_DB_USER',
            'SUPABASE_DB_PASSWORD'
        ]
        
        for var in supabase_vars:
            pattern = rf'^{var}=(.*)$'
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                config[var] = match.group(1).strip()
            else:
                config[var] = None
                
        return config
    
    def add_supabase_config(self, config: Dict[str, str]) -> bool:
        """Add Supabase configuration to .env file"""
        try:
            if not self.env_file.exists():
                print("❌ .env file not found")
                return False
            
            with open(self.env_file, 'r') as f:
                content = f.read()
            
            # Check if Supabase section already exists
            if 'SUPABASE_URL' in content:
                print("⚠️  Supabase configuration already exists in .env file")
                print("   Current configuration:")
                current_config = self.get_current_supabase_config()
                for key, value in current_config.items():
                    if value:
                        print(f"   {key}={value}")
                    else:
                        print(f"   {key}=<not set>")
                return True
            
            # Add Supabase configuration section
            supabase_section = """
# Supabase Configuration
# Add your Supabase project details below
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# Supabase Database Connection (for direct database access)
SUPABASE_DB_HOST=your_supabase_db_host_here
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your_supabase_db_password_here
"""
            
            # Add to end of file
            new_content = content.rstrip() + supabase_section
            
            with open(self.env_file, 'w') as f:
                f.write(new_content)
            
            print("✅ Added Supabase configuration section to .env file")
            print("   Please update the values with your actual Supabase credentials")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add Supabase configuration: {e}")
            return False
    
    def validate_supabase_config(self) -> bool:
        """Validate that Supabase configuration is complete"""
        config = self.get_current_supabase_config()
        
        required_vars = [
            'SUPABASE_URL',
            'SUPABASE_ANON_KEY',
            'SUPABASE_DB_HOST',
            'SUPABASE_DB_USER',
            'SUPABASE_DB_PASSWORD'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not config.get(var) or config[var] == f'your_{var.lower()}_here':
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing or incomplete Supabase configuration:")
            for var in missing_vars:
                print(f"   - {var}")
            return False
        
        print("✅ Supabase configuration appears complete")
        return True
    
    def get_setup_instructions(self) -> str:
        """Get setup instructions for Supabase"""
        return """
🔧 SUPABASE SETUP INSTRUCTIONS

1. **Create Supabase Project**
   - Go to https://supabase.com
   - Sign up/Login and create a new project
   - Choose a region close to your users
   - Wait for project setup to complete

2. **Get Project Credentials**
   - Go to Project Settings > API
   - Copy the following values:
     * Project URL (e.g., https://abc123.supabase.co)
     * anon/public key
     * service_role key (keep this secret!)

3. **Get Database Credentials**
   - Go to Project Settings > Database
   - Copy the following values:
     * Host (e.g., db.abc123.supabase.co)
     * Database name (usually 'postgres')
     * Port (usually 5432)
     * User (usually 'postgres')
     * Password (the one you set during project creation)

4. **Update .env File**
   - Replace the placeholder values in your .env file
   - Example:
     SUPABASE_URL=https://abc123.supabase.co
     SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
     SUPABASE_DB_HOST=db.abc123.supabase.co
     SUPABASE_DB_PASSWORD=your_actual_password

5. **Test Connection**
   - Run: python scripts/test_supabase_connection.py
   - Verify connection is successful

6. **Run Full Verification**
   - Run: python scripts/data_integrity_verification.py
   - This will compare legacy vs Supabase systems
"""

def main():
    """Main function"""
    print("🚀 Supabase Configuration Setup")
    print("=" * 50)
    
    setup = SupabaseConfigSetup()
    
    # Backup current .env file
    setup.backup_env_file()
    
    # Check current configuration
    print("\n📋 Current Supabase Configuration:")
    current_config = setup.get_current_supabase_config()
    if not any(current_config.values()):
        print("   No Supabase configuration found")
    else:
        for key, value in current_config.items():
            if value:
                print(f"   {key}={value}")
            else:
                print(f"   {key}=<not set>")
    
    # Add Supabase configuration section if needed
    if not current_config.get('SUPABASE_URL'):
        print("\n🔧 Adding Supabase configuration section...")
        setup.add_supabase_config({})
    
    # Validate configuration
    print("\n✅ Configuration Status:")
    is_valid = setup.validate_supabase_config()
    
    if not is_valid:
        print("\n" + setup.get_setup_instructions())
        print("\n⚠️  Please complete the Supabase setup before running verification")
    else:
        print("\n🎉 Supabase configuration is ready!")
        print("   You can now run the full data integrity verification")
    
    print("\n📁 Files:")
    print(f"   .env: {setup.env_file}")
    if setup.backup_file.exists():
        print(f"   Backup: {setup.backup_file}")

if __name__ == "__main__":
    main()
