#!/usr/bin/env python3
"""
SaaS Factory - Dependency Management Script
Updates all service requirements to use unified dependency versions
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Service configurations
SERVICES = {
    'orchestrator': {
        'path': 'orchestrator',
        'requirements': 'requirements-orchestrator.txt',
        'backup_existing': True
    },
    'agents': {
        'path': 'agents',
        'requirements': 'requirements-agents.txt',
        'backup_existing': True
    },
    'api_gateway': {
        'path': 'api_gateway',
        'requirements': 'requirements-agents.txt',
        'backup_existing': True
    },
    'dashboard': {
        'path': 'dashboard',
        'requirements': 'requirements-agents.txt',
        'backup_existing': True
    },
    'event-relay': {
        'path': 'event-relay',
        'requirements': 'requirements-agents.txt',
        'backup_existing': True
    },
    'agents/qa': {
        'path': 'agents/qa',
        'requirements': 'requirements-agents.txt',
        'backup_existing': True
    },
    'agents/dev': {
        'path': 'agents/dev',
        'requirements': 'requirements-agents.txt',
        'backup_existing': True
    },
    'agents/ui': {
        'path': 'agents/ui',
        'requirements': 'requirements-agents.txt',
        'backup_existing': True
    }
}

def backup_existing_requirements(service_path: str) -> bool:
    """Backup existing requirements.txt file"""
    req_file = os.path.join(service_path, 'requirements.txt')
    if os.path.exists(req_file):
        backup_file = os.path.join(service_path, 'requirements.txt.backup')
        shutil.copy2(req_file, backup_file)
        print(f"✅ Backed up {req_file} to {backup_file}")
        return True
    return False

def update_service_requirements(service_name: str, config: Dict) -> bool:
    """Update requirements.txt for a specific service"""
    service_path = config['path']
    requirements_file = config['requirements']
    
    print(f"\n🔄 Updating {service_name} ({service_path})...")
    
    # Check if service directory exists
    if not os.path.exists(service_path):
        print(f"⚠️  Directory {service_path} does not exist, skipping...")
        return False
    
    # Backup existing requirements
    if config.get('backup_existing', False):
        backup_existing_requirements(service_path)
    
    # Create new requirements.txt pointing to unified requirements
    req_file = os.path.join(service_path, 'requirements.txt')
    
    # Get relative path to requirements file from service directory
    rel_path = os.path.relpath(requirements_file, service_path)
    
    with open(req_file, 'w') as f:
        f.write(f"# SaaS Factory - Unified Dependencies\n")
        f.write(f"# This file uses unified dependency management\n")
        f.write(f"# See {requirements_file} for actual dependencies\n\n")
        f.write(f"-r {rel_path}\n")
    
    print(f"✅ Updated {req_file}")
    return True

def validate_requirements() -> bool:
    """Validate that all requirement files exist and are valid"""
    base_files = [
        'requirements-base.txt',
        'requirements-orchestrator.txt',
        'requirements-agents.txt'
    ]
    
    print("\n🔍 Validating requirement files...")
    
    for file in base_files:
        if not os.path.exists(file):
            print(f"❌ Missing required file: {file}")
            return False
        print(f"✅ Found {file}")
    
    return True

def test_pip_compatibility() -> bool:
    """Test if the unified requirements can be installed"""
    print("\n🧪 Testing pip compatibility...")
    
    # Test base requirements
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--dry-run', '-r', 'requirements-base.txt'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Base requirements are compatible")
            return True
        else:
            print(f"❌ Base requirements compatibility issues:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Pip dry-run timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing compatibility: {e}")
        return False

def main():
    """Main function to update all dependencies"""
    print("🚀 SaaS Factory - Dependency Management Update")
    print("=" * 50)
    
    # Validate requirement files exist
    if not validate_requirements():
        print("\n❌ Validation failed. Please ensure all requirement files are present.")
        sys.exit(1)
    
    # Test pip compatibility
    if not test_pip_compatibility():
        print("\n⚠️  Compatibility issues detected. Proceed with caution.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(1)
    
    # Update all services
    success_count = 0
    total_services = len(SERVICES)
    
    for service_name, config in SERVICES.items():
        if update_service_requirements(service_name, config):
            success_count += 1
    
    print(f"\n📊 Update Summary:")
    print(f"✅ Successfully updated: {success_count}/{total_services} services")
    
    if success_count == total_services:
        print("\n🎉 All dependencies updated successfully!")
        print("\nNext steps:")
        print("1. Test each service individually")
        print("2. Run integration tests")
        print("3. Update Docker files if needed")
        print("4. Commit changes to version control")
    else:
        print(f"\n⚠️  {total_services - success_count} services had issues")
        print("Please check the output above for details")
    
    return success_count == total_services

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 