#!/usr/bin/env python3
"""
Logging System Migration Script
Converts existing files from old logging system to new centralized logging
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Tuple

class LoggingMigrationScript:
    """Script to migrate logging system from old to new architecture"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.migration_stats = {
            'files_processed': 0,
            'files_migrated': 0,
            'files_skipped': 0,
            'errors': []
        }
        
        # Patterns to search for
        self.patterns = {
            'logging_basic_config': r'logging\.basicConfig\([^)]*\)',
            'logging_get_logger': r'logging\.getLogger\([^)]*\)',
            'import_logging': r'^import logging$',
            'from_logging': r'^from logging import',
        }
        
        # Replacement patterns
        self.replacements = {
            'logging_basic_config': 'from config.logging_config import get_logger',
            'logging_get_logger': 'get_logger(__name__)',
            'import_logging': '# import logging  # Migrated to centralized logging',
            'from_logging': '# from logging import  # Migrated to centralized logging',
        }
        
    def find_python_files(self) -> List[Path]:
        """Find all Python files in the project"""
        python_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', 'venv', 'env']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
                    
        return python_files
        
    def analyze_file(self, file_path: Path) -> Dict[str, any]:
        """Analyze a Python file for logging usage"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            analysis = {
                'file_path': file_path,
                'has_logging_basic_config': bool(re.search(self.patterns['logging_basic_config'], content)),
                'has_logging_get_logger': bool(re.search(self.patterns['logging_get_logger'], content)),
                'has_import_logging': bool(re.search(self.patterns['import_logging'], content, re.MULTILINE)),
                'has_from_logging': bool(re.search(self.patterns['from_logging'], content, re.MULTILINE)),
                'needs_migration': False,
                'migration_actions': []
            }
            
            # Determine if file needs migration
            if (analysis['has_logging_basic_config'] or 
                analysis['has_logging_get_logger'] or
                analysis['has_import_logging'] or
                analysis['has_from_logging']):
                analysis['needs_migration'] = True
                
            return analysis
            
        except Exception as e:
            self.migration_stats['errors'].append(f"Error analyzing {file_path}: {e}")
            return {'file_path': file_path, 'error': str(e)}
            
    def migrate_file(self, file_path: Path, analysis: Dict[str, any]) -> bool:
        """Migrate a single file to the new logging system"""
        try:
            # Create backup
            backup_path = file_path.with_suffix('.py.backup')
            shutil.copy2(file_path, backup_path)
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            migration_made = False
            
            # Apply replacements
            for pattern_name, pattern in self.patterns.items():
                if analysis.get(f'has_{pattern_name}', False):
                    replacement = self.replacements[pattern_name]
                    
                    if pattern_name == 'logging_basic_config':
                        # Remove the basicConfig line
                        content = re.sub(pattern, '', content)
                        migration_made = True
                        
                    elif pattern_name == 'logging_get_logger':
                        # Replace getLogger calls
                        content = re.sub(pattern, replacement, content)
                        migration_made = True
                        
                    elif pattern_name == 'import_logging':
                        # Comment out logging import
                        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                        migration_made = True
                        
                    elif pattern_name == 'from_logging':
                        # Comment out from logging imports
                        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                        migration_made = True
                        
            # Add import if needed
            if (analysis.get('has_logging_get_logger', False) and 
                'from config.logging_config import get_logger' not in content):
                # Find the first import line
                lines = content.split('\n')
                import_index = -1
                
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        import_index = i
                        break
                        
                if import_index >= 0:
                    # Insert after the last import
                    while (import_index + 1 < len(lines) and 
                           (lines[import_index + 1].strip().startswith('import ') or 
                            lines[import_index + 1].strip().startswith('from '))):
                        import_index += 1
                        
                    lines.insert(import_index + 1, 'from config.logging_config import get_logger')
                    content = '\n'.join(lines)
                    migration_made = True
                    
            # Write updated content
            if migration_made and content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                # Remove backup if migration successful
                backup_path.unlink()
                return True
            else:
                # No changes made, remove backup
                backup_path.unlink()
                return False
                
        except Exception as e:
            self.migration_stats['errors'].append(f"Error migrating {file_path}: {e}")
            return False
            
    def run_migration(self, dry_run: bool = False) -> Dict[str, any]:
        """Run the complete migration process"""
        print("🔍 Logging System Migration Script")
        print("=" * 50)
        
        if dry_run:
            print("📋 DRY RUN MODE - No files will be modified")
            print()
            
        # Find Python files
        print("🔍 Scanning for Python files...")
        python_files = self.find_python_files()
        print(f"📁 Found {len(python_files)} Python files")
        print()
        
        # Analyze files
        print("📊 Analyzing files for logging usage...")
        files_to_migrate = []
        
        for file_path in python_files:
            analysis = self.analyze_file(file_path)
            
            if analysis.get('needs_migration', False):
                files_to_migrate.append(analysis)
                print(f"  ⚠️  {file_path.relative_to(self.project_root)} - Needs migration")
            else:
                print(f"  ✅ {file_path.relative_to(self.project_root)} - No migration needed")
                
        print(f"\n📋 Found {len(files_to_migrate)} files that need migration")
        print()
        
        if not files_to_migrate:
            print("🎉 No files need migration!")
            return self.migration_stats
            
        # Confirm migration
        if not dry_run:
            response = input("🚀 Proceed with migration? (y/N): ").strip().lower()
            if response != 'y':
                print("❌ Migration cancelled")
                return self.migration_stats
                
        # Perform migration
        print("\n🚀 Starting migration...")
        for analysis in files_to_migrate:
            file_path = analysis['file_path']
            print(f"  🔄 Migrating {file_path.relative_to(self.project_root)}...")
            
            if not dry_run:
                success = self.migrate_file(file_path, analysis)
                if success:
                    self.migration_stats['files_migrated'] += 1
                    print(f"    ✅ Migration successful")
                else:
                    print(f"    ⚠️  No changes needed")
            else:
                print(f"    📋 Would migrate (dry run)")
                
            self.migration_stats['files_processed'] += 1
            
        # Print summary
        print("\n" + "=" * 50)
        print("📊 MIGRATION SUMMARY")
        print("=" * 50)
        print(f"Files processed: {self.migration_stats['files_processed']}")
        print(f"Files migrated: {self.migration_stats['files_migrated']}")
        print(f"Files skipped: {self.migration_stats['files_skipped']}")
        
        if self.migration_stats['errors']:
            print(f"\n❌ Errors encountered:")
            for error in self.migration_stats['errors']:
                print(f"  - {error}")
                
        if dry_run:
            print(f"\n📋 This was a dry run. Run without --dry-run to perform actual migration.")
        else:
            print(f"\n🎉 Migration completed successfully!")
            
        return self.migration_stats
        
    def generate_migration_report(self) -> str:
        """Generate a detailed migration report"""
        report = []
        report.append("# Logging System Migration Report")
        report.append("")
        report.append(f"Generated: {__import__('datetime').datetime.now().isoformat()}")
        report.append("")
        report.append("## Summary")
        report.append(f"- Files processed: {self.migration_stats['files_processed']}")
        report.append(f"- Files migrated: {self.migration_stats['files_migrated']}")
        report.append(f"- Files skipped: {self.migration_stats['files_skipped']}")
        report.append(f"- Errors: {len(self.migration_stats['errors'])}")
        report.append("")
        
        if self.migration_stats['errors']:
            report.append("## Errors")
            for error in self.migration_stats['errors']:
                report.append(f"- {error}")
            report.append("")
            
        report.append("## Next Steps")
        report.append("1. Test the migrated files to ensure they work correctly")
        report.append("2. Remove any remaining old logging imports if not needed")
        report.append("3. Update any custom logging configurations")
        report.append("4. Test the new centralized logging system")
        report.append("")
        report.append("## Manual Review Required")
        report.append("Some files may require manual review, especially those with:")
        report.append("- Custom logging configurations")
        report.append("- Complex logging patterns")
        report.append("- Third-party logging integrations")
        
        return "\n".join(report)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate logging system to centralized configuration")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without making changes")
    parser.add_argument("--project-root", default=".", help="Project root directory (default: current directory)")
    parser.add_argument("--report", action="store_true", help="Generate migration report")
    
    args = parser.parse_args()
    
    # Run migration
    migrator = LoggingMigrationScript(args.project_root)
    stats = migrator.run_migration(dry_run=args.dry_run)
    
    # Generate report if requested
    if args.report:
        report = migrator.generate_migration_report()
        report_file = Path("logging_migration_report.md")
        
        with open(report_file, 'w') as f:
            f.write(report)
            
        print(f"\n📄 Migration report saved to: {report_file}")
        
    # Exit with error code if there were errors
    if stats['errors']:
        exit(1)

if __name__ == "__main__":
    main()
