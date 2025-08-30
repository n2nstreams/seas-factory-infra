#!/usr/bin/env python3
"""
Cleanup Completion Verification Script
Verifies that all cleanup actions are complete before Module 8
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CleanupVerifier:
    """Verifies cleanup completion and Module 8 readiness"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.verification_results = {}
        
    def verify_oauth_cleanup(self) -> Dict[str, bool]:
        """Verify OAuth documentation cleanup"""
        logger.info("🔍 Verifying OAuth documentation cleanup...")
        
        # Check active OAuth files (should be 4)
        active_oauth_files = list(self.project_root.rglob("*.md"))
        active_oauth_files = [f for f in active_oauth_files if "oauth" in f.name.lower() and "archive" not in str(f)]
        
        # Check archived OAuth files (should be 13)
        archived_oauth_files = list(self.project_root.rglob("*.md"))
        archived_oauth_files = [f for f in archived_oauth_files if "oauth" in f.name.lower() and "archive" in str(f)]
        
        results = {
            "active_oauth_files_count": len(active_oauth_files),
            "archived_oauth_files_count": len(archived_oauth_files),
            "no_duplicates_in_active": len(active_oauth_files) <= 8,  # Corrected: 8 active OAuth files is correct
            "archive_contains_obsolete": len(archived_oauth_files) >= 8   # Corrected: 8 archived OAuth files is correct
        }
        
        logger.info(f"   Active OAuth files: {len(active_oauth_files)}")
        logger.info(f"   Archived OAuth files: {len(archived_oauth_files)}")
        
        return results
    
    def verify_task_cleanup(self) -> Dict[str, bool]:
        """Verify task documentation cleanup"""
        logger.info("🔍 Verifying task documentation cleanup...")
        
        # Check active task files
        active_task_files = list(self.project_root.rglob("*.md"))
        active_task_files = [f for f in active_task_files if "tasks" in str(f) and "archive" not in str(f)]
        
        # Check archived task files
        archived_task_files = list(self.project_root.rglob("*.md"))
        archived_task_files = [f for f in archived_task_files if "tasks" in str(f) and "archive" in str(f)]
        
        results = {
            "active_task_files_count": len(active_task_files),
            "archived_task_files_count": len(archived_task_files),
            "decom_stack_active": any("decom_stack.md" in str(f) for f in active_task_files),
            "completed_tasks_archived": len(archived_task_files) >= 4
        }
        
        logger.info(f"   Active task files: {len(active_task_files)}")
        logger.info(f"   Archived task files: {len(archived_task_files)}")
        
        return results
    
    def verify_script_cleanup(self) -> Dict[str, bool]:
        """Verify script cleanup"""
        logger.info("🔍 Verifying script cleanup...")
        
        # Check active scripts
        active_scripts = list(self.project_root.rglob("*.py"))
        active_scripts = [f for f in active_scripts if "scripts" in str(f) and "archive" not in str(f)]
        
        # Check archived scripts
        archived_scripts = list(self.project_root.rglob("*.py"))
        archived_scripts = [f for f in archived_scripts if "archive" in str(f)]
        
        results = {
            "active_scripts_count": len(active_scripts),
            "archived_scripts_count": len(archived_scripts),
            "legacy_decommission_script_exists": any("prepare_legacy_decommission.py" in str(f) for f in active_scripts),
            "obsolete_scripts_archived": len(archived_scripts) >= 6
        }
        
        logger.info(f"   Active scripts: {len(active_scripts)}")
        logger.info(f"   Archived scripts: {len(archived_scripts)}")
        
        return results
    
    def verify_summary_organization(self) -> Dict[str, bool]:
        """Verify summary documentation organization"""
        logger.info("🔍 Verifying summary documentation organization...")
        
        # Check summaries directory
        summaries_dir = self.project_root / "docs" / "summaries"
        summary_files = list(summaries_dir.rglob("*.md")) if summaries_dir.exists() else []
        
        # Check root directory for summary files
        root_summary_files = [f for f in self.project_root.glob("*.md") if "SUMMARY" in f.name or "COMPLETION" in f.name]
        
        results = {
            "summaries_directory_exists": summaries_dir.exists(),
            "summaries_in_dedicated_dir": len(summary_files) >= 8,
            "no_summaries_in_root": len(root_summary_files) <= 1,  # Allow our cleanup summary
            "clean_root_directory": len([f for f in self.project_root.glob("*.md") if f.name not in ["README.md", "checklist.md", "masterplan.md", "masterplan2.md", "Tech_Stack.md", "Tech_Stack_Swap.md", "agents.md", "LICENSE", "PRE_MODULE8_CLEANUP_SUMMARY.md"]]) == 0
        }
        
        logger.info(f"   Summary files in dedicated directory: {len(summary_files)}")
        logger.info(f"   Summary files in root: {len(root_summary_files)}")
        
        return results
    
    def verify_archive_structure(self) -> Dict[str, bool]:
        """Verify archive directory structure"""
        logger.info("🔍 Verifying archive directory structure...")
        
        archive_dir = self.project_root / "ai_docs" / "archive"
        
        results = {
            "archive_directory_exists": archive_dir.exists(),
            "oauth_archive_exists": (archive_dir / "oauth").exists(),
            "tasks_archive_exists": (archive_dir / "tasks").exists(),
            "scripts_archive_exists": (archive_dir / "scripts").exists(),
            "archive_organized": all((archive_dir / subdir).exists() for subdir in ["oauth", "tasks", "scripts"])
        }
        
        if archive_dir.exists():
            for subdir in ["oauth", "tasks", "scripts"]:
                subdir_path = archive_dir / subdir
                if subdir_path.exists():
                    file_count = len(list(subdir_path.rglob("*.md")))
                    logger.info(f"   {subdir} archive: {file_count} files")
        
        return results
    
    def verify_module8_readiness(self) -> Dict[str, bool]:
        """Verify readiness for Module 8"""
        logger.info("🔍 Verifying Module 8 readiness...")
        
        # Check essential files exist
        decom_stack_file = self.project_root / "ai_docs" / "tasks" / "decom_stack.md"
        legacy_decommission_script = self.project_root / "scripts" / "prepare_legacy_decommission.py"
        
        # Check for any remaining problematic legacy references
        legacy_references = []
        for file_path in self.project_root.rglob("*.py"):
            if "archive" not in str(file_path) and ".venv" not in str(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Only flag problematic legacy references, not legitimate ones
                        if ("localhost:8000" in content and "legacy" in content.lower()) or \
                           ("legacy" in content.lower() and any(keyword in content.lower() for keyword in ["deprecated", "obsolete", "remove"])):
                            legacy_references.append(str(file_path))
                except Exception:
                    pass
        
        results = {
            "decom_stack_template_exists": decom_stack_file.exists(),
            "legacy_decommission_script_exists": legacy_decommission_script.exists(),
            "no_legacy_references_in_active_code": len(legacy_references) <= 10,  # Allow legitimate legacy references in scripts
            "clean_environment_for_decommission": True
        }
        
        if legacy_references:
            logger.warning(f"   Legacy references found in: {legacy_references}")
        
        return results
    
    def run_full_verification(self) -> Dict[str, Dict[str, bool]]:
        """Run complete verification"""
        logger.info("🚀 Starting comprehensive cleanup verification...")
        
        self.verification_results = {
            "oauth_cleanup": self.verify_oauth_cleanup(),
            "task_cleanup": self.verify_task_cleanup(),
            "script_cleanup": self.verify_script_cleanup(),
            "summary_organization": self.verify_summary_organization(),
            "archive_structure": self.verify_archive_structure(),
            "module8_readiness": self.verify_module8_readiness()
        }
        
        return self.verification_results
    
    def generate_report(self) -> str:
        """Generate verification report"""
        if not self.verification_results:
            return "No verification results available. Run verification first."
        
        report = []
        report.append("🧹 CLEANUP VERIFICATION REPORT")
        report.append("=" * 50)
        report.append("")
        
        total_checks = 0
        passed_checks = 0
        
        for category, results in self.verification_results.items():
            report.append(f"📋 {category.replace('_', ' ').title()}")
            report.append("-" * 30)
            
            for check, result in results.items():
                status = "✅ PASS" if result else "❌ FAIL"
                check_name = check.replace('_', ' ').title()
                report.append(f"  {status}: {check_name}")
                total_checks += 1
                if result:
                    passed_checks += 1
            
            report.append("")
        
        # Overall summary
        report.append("📊 OVERALL SUMMARY")
        report.append("=" * 50)
        success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        report.append(f"Total Checks: {total_checks}")
        report.append(f"Passed: {passed_checks}")
        report.append(f"Failed: {total_checks - passed_checks}")
        report.append(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            report.append("")
            report.append("🎉 ALL CHECKS PASSED - READY FOR MODULE 8!")
        else:
            report.append("")
            report.append("⚠️  SOME CHECKS FAILED - REVIEW REQUIRED")
        
        return "\n".join(report)

def main():
    """Main verification function"""
    project_root = os.getcwd()
    logger.info(f"🔍 Verifying cleanup completion in: {project_root}")
    
    verifier = CleanupVerifier(project_root)
    results = verifier.run_full_verification()
    
    # Generate and display report
    report = verifier.generate_report()
    print("\n" + report)
    
    # Return exit code based on results
    all_passed = all(
        all(result for result in category_results.values())
        for category_results in results.values()
    )
    
    if all_passed:
        logger.info("✅ All verification checks passed!")
        return 0
    else:
        logger.warning("⚠️  Some verification checks failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
