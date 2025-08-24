#!/usr/bin/env python3
"""
Path Consistency Validation Script
Checks for consistent path naming across the SaaS Factory codebase
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Define the correct path patterns
CORRECT_PATHS = {
    'api_gateway': 'api_gateway',  # Not api-gateway
    'ui': 'ui',                    # Not UI or frontend
    'orchestrator': 'orchestrator', # Not orchestrator
    'agents': 'agents',            # Not agent
    'infra': 'infra',              # Not infrastructure
    'docs': 'docs',                # Not documentation
}

# Define incorrect path patterns to flag (more specific to avoid false positives)
INCORRECT_PATTERNS = [
    # Directory paths that should be corrected
    (r'api-gateway/', r'api_gateway/', 'Directory path should use underscore'),
    (r'cd api-gateway', r'cd api_gateway', 'Command should use underscore'),
    (r'context: ../api-gateway', r'context: ../api_gateway', 'Docker context should use underscore'),
    (r'path: \'api-gateway\'', r'path: \'api_gateway\'', 'Path should use underscore'),
    (r'path": "api-gateway"', r'path": "api_gateway"', 'Path should use underscore'),
    
    # Service names that should be corrected
    (r'name = "api-gateway"', r'name = "api_gateway"', 'Service name should use underscore'),
    (r'image.*api-gateway:', r'image.*api_gateway:', 'Image name should use underscore'),
    
    # File references that should be corrected
    (r'`api-gateway/', r'`api_gateway/', 'File path should use underscore'),
    (r'api-gateway/', r'api_gateway/', 'Directory reference should use underscore'),
]

# File types to check
FILE_EXTENSIONS = ['.py', '.md', '.yml', '.yaml', '.tf', '.sh', 'Makefile', 'Dockerfile']

# Patterns that are legitimate and should NOT be flagged
LEGITIMATE_PATTERNS = [
    r'UI/UX',           # UI/UX design is legitimate
    r'UI/',             # UI/ in context of UI/UX
    r'frontend/',       # frontend/ in documentation context
    r'infrastructure/', # infrastructure/ in documentation context
    r'documentation/',  # documentation/ in documentation context
    r'api-gateway-',    # Service URLs like api-gateway-4riidj3biq-uc.a.run.app
    r'@mui/material',   # NPM package names
    r'@chakra-ui/react', # NPM package names
    r'@emotion/react',  # NPM package names
    r'@emotion/styled', # NPM package names
]

def find_files_with_paths(directory: str = '.') -> List[Path]:
    """Find all files that might contain path references"""
    files = []
    for root, dirs, filenames in os.walk(directory):
        # Skip common directories that shouldn't be checked
        dirs[:] = [d for d in dirs if d not in ['.git', '.venv', 'venv', 'env', '__pycache__', 'node_modules', '.pytest_cache']]
        
        for filename in filenames:
            if any(filename.endswith(ext) for ext in FILE_EXTENSIONS) or filename in FILE_EXTENSIONS:
                files.append(Path(root) / filename)
    return files

def is_legitimate_pattern(line: str) -> bool:
    """Check if a line contains legitimate patterns that shouldn't be flagged"""
    for pattern in LEGITIMATE_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return True
    return False

def check_file_for_path_issues(file_path: Path) -> List[Tuple[str, int, str, str, str]]:
    """Check a single file for path consistency issues"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, 1):
            # Skip lines with legitimate patterns
            if is_legitimate_pattern(line):
                continue
                
            # Check for incorrect path patterns
            for pattern, replacement, description in INCORRECT_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append((pattern, line_num, line.strip(), replacement, description))
                    
    except (UnicodeDecodeError, PermissionError):
        # Skip binary files or files we can't read
        pass
        
    return issues

def check_directory_structure() -> Dict[str, bool]:
    """Check if the actual directory structure matches expected paths"""
    issues = {}
    
    for expected_path in CORRECT_PATHS.values():
        if not os.path.exists(expected_path):
            issues[expected_path] = False
        else:
            issues[expected_path] = True
            
    return issues

def validate_paths() -> bool:
    """Main validation function"""
    print("🔍 Validating path consistency across SaaS Factory codebase...")
    print("=" * 60)
    
    # Check directory structure
    print("\n📁 Checking directory structure...")
    dir_issues = check_directory_structure()
    for path, exists in dir_issues.items():
        status = "✅" if exists else "❌"
        print(f"  {status} {path}/")
    
    # Find and check files
    print("\n📄 Checking files for path consistency issues...")
    files = find_files_with_paths()
    
    total_issues = 0
    files_with_issues = 0
    
    for file_path in files:
        issues = check_file_for_path_issues(file_path)
        if issues:
            files_with_issues += 1
            print(f"\n⚠️  {file_path}:")
            for pattern, line_num, line, replacement, description in issues:
                total_issues += 1
                print(f"    Line {line_num}: {description}")
                print(f"      Current: {line[:100]}...")
                print(f"      Should be: {line.replace(pattern, replacement)[:100]}...")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Path Consistency Validation Summary:")
    print(f"  Files checked: {len(files)}")
    print(f"  Files with issues: {files_with_issues}")
    print(f"  Total issues found: {total_issues}")
    
    if total_issues == 0:
        print("\n🎉 All paths are consistent!")
        return True
    else:
        print(f"\n❌ Found {total_issues} path consistency issues that need fixing.")
        print("   Run this script after fixing issues to validate.")
        return False

def suggest_fixes():
    """Suggest common fixes for path issues"""
    print("\n🔧 Common Path Fixes:")
    print("  • Replace 'api-gateway/' with 'api_gateway/' in directory references")
    print("  • Replace 'api-gateway' with 'api_gateway' in service names")
    print("  • Replace 'context: ../api-gateway' with 'context: ../api_gateway' in Docker files")
    print("  • Replace 'path: \"api-gateway\"' with 'path: \"api_gateway\"' in scripts")
    print("\n💡 Use search and replace in your editor:")
    print("  • Search: api-gateway/")
    print("  • Replace: api_gateway/")
    print("  • Search: api-gateway")
    print("  • Replace: api_gateway")

if __name__ == "__main__":
    try:
        success = validate_paths()
        
        if not success:
            suggest_fixes()
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        sys.exit(1)
