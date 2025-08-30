#!/usr/bin/env python3
"""
Feature Flag Validation Master Script
Runs all three feature flag validation tests in sequence:
1. Flag Dependencies Testing
2. Rollback Testing  
3. Real-time Monitoring Testing
"""

import os
import sys
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Tuple

class FeatureFlagValidationRunner:
    """Runs comprehensive feature flag validation tests"""
    
    def __init__(self):
        self.scripts_dir = os.path.dirname(os.path.abspath(__file__))
        self.test_results: Dict[str, bool] = {}
        self.reports: List[str] = []
        
        # Test scripts to run
        self.test_scripts = [
            {
                'name': 'Flag Dependencies',
                'script': 'test_feature_flag_dependencies.py',
                'description': 'Tests that no feature flags have interdependencies that could cause issues'
            },
            {
                'name': 'Rollback Testing',
                'script': 'test_feature_flag_rollbacks.py', 
                'description': 'Tests that disabling any feature flag immediately reverts to legacy functionality'
            },
            {
                'name': 'Real-time Monitoring',
                'script': 'test_feature_flag_monitoring.py',
                'description': 'Tests that feature flag status is being monitored in real-time'
            }
        ]
    
    def run_single_test(self, test_info: Dict) -> bool:
        """Run a single feature flag validation test"""
        script_name = test_info['script']
        test_name = test_info['name']
        
        print(f"\n🚀 Running {test_name}")
        print("=" * 60)
        print(f"Description: {test_info['description']}")
        print(f"Script: {script_name}")
        print("")
        
        script_path = os.path.join(self.scripts_dir, script_name)
        
        if not os.path.exists(script_path):
            print(f"❌ Script not found: {script_path}")
            return False
        
        try:
            # Run the test script
            start_time = time.time()
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                cwd=self.scripts_dir,
                timeout=300  # 5 minute timeout
            )
            execution_time = time.time() - start_time
            
            # Print output
            if result.stdout:
                print(result.stdout)
            
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
            
            # Determine success
            success = result.returncode == 0
            
            # Print result
            if success:
                print(f"✅ {test_name} PASSED ({execution_time:.1f}s)")
            else:
                print(f"❌ {test_name} FAILED ({execution_time:.1f}s)")
                print(f"Exit code: {result.returncode}")
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_name} TIMED OUT (after 5 minutes)")
            return False
            
        except Exception as e:
            print(f"💥 {test_name} ERROR: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all feature flag validation tests"""
        print("🎯 Starting Comprehensive Feature Flag Validation")
        print("=" * 80)
        print("This will run three critical validation tests:")
        print("")
        
        for i, test in enumerate(self.test_scripts, 1):
            print(f"{i}. {test['name']}")
            print(f"   {test['description']}")
        
        print("")
        print("Press Enter to continue or Ctrl+C to cancel...")
        try:
            input()
        except KeyboardInterrupt:
            print("\n❌ Validation cancelled by user")
            return False
        
        # Run each test
        total_tests = len(self.test_scripts)
        passed_tests = 0
        
        for test_info in self.test_scripts:
            success = self.run_single_test(test_info)
            self.test_results[test_info['name']] = success
            
            if success:
                passed_tests += 1
            
            # Small delay between tests
            if test_info != self.test_scripts[-1]:  # Not the last test
                print("\n⏳ Waiting 3 seconds before next test...")
                time.sleep(3)
        
        # Generate summary
        self._generate_validation_summary(passed_tests, total_tests)
        
        return passed_tests == total_tests
    
    def _generate_validation_summary(self, passed: int, total: int):
        """Generate comprehensive validation summary"""
        print("\n" + "=" * 80)
        print("📊 FEATURE FLAG VALIDATION SUMMARY")
        print("=" * 80)
        
        # Overall results
        success_rate = (passed / total) * 100
        print(f"Overall Results: {passed}/{total} tests passed ({success_rate:.1f}%)")
        print("")
        
        # Individual test results
        print("Individual Test Results:")
        for test_name, success in self.test_results.items():
            status_icon = "✅" if success else "❌"
            status_text = "PASSED" if success else "FAILED"
            print(f"  {status_icon} {test_name}: {status_text}")
        
        print("")
        
        # Recommendations
        if passed == total:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Feature flag system is fully validated and ready for production")
            print("✅ Dependencies are properly configured")
            print("✅ Rollback procedures are working correctly")
            print("✅ Real-time monitoring is functioning")
        else:
            failed_count = total - passed
            print(f"⚠️  {failed_count} TEST(S) FAILED")
            print("🚨 Feature flag system needs attention before production deployment")
            
            if not self.test_results.get('Flag Dependencies', True):
                print("   - Review and fix flag dependencies")
            
            if not self.test_results.get('Rollback Testing', True):
                print("   - Ensure rollback procedures are working")
            
            if not self.test_results.get('Real-time Monitoring', True):
                print("   - Fix real-time monitoring functionality")
        
        print("")
        
        # Next steps
        print("📋 Next Steps:")
        if passed == total:
            print("   ✅ Feature flag system is production-ready")
            print("   ✅ Continue with deployment planning")
            print("   ✅ Monitor system in staging environment")
        else:
            print("   🔧 Fix failed validation tests")
            print("   🔧 Re-run validation after fixes")
            print("   🔧 Do not deploy until all tests pass")
        
        print("")
        
        # Report files
        print("📁 Detailed reports generated:")
        self._collect_generated_reports()
        for report in self.reports:
            print(f"   - {report}")
    
    def _collect_generated_reports(self):
        """Collect all generated report files"""
        try:
            # Look for report files in the scripts directory
            for filename in os.listdir(self.scripts_dir):
                if filename.startswith('feature_flag_') and filename.endswith('_report_'):
                    # This is a report file, get the full path
                    report_path = os.path.join(self.scripts_dir, filename)
                    self.reports.append(report_path)
        except Exception as e:
            print(f"   ⚠️  Could not collect report files: {e}")
    
    def cleanup_test_files(self):
        """Clean up test files and reports"""
        print("\n🧹 Cleaning up test files...")
        
        try:
            # Remove generated report files
            for report in self.reports:
                if os.path.exists(report):
                    os.remove(report)
                    print(f"   🗑️  Removed: {os.path.basename(report)}")
            
            # Remove any other test artifacts
            for filename in os.listdir(self.scripts_dir):
                if filename.startswith('feature_flag_') and filename.endswith('.txt'):
                    file_path = os.path.join(self.scripts_dir, filename)
                    os.remove(file_path)
                    print(f"   🗑️  Removed: {filename}")
            
            print("   ✅ Cleanup completed")
            
        except Exception as e:
            print(f"   ⚠️  Cleanup error: {e}")

def main():
    """Main function to run feature flag validation"""
    runner = FeatureFlagValidationRunner()
    
    try:
        print("🔍 Feature Flag Validation Suite")
        print("=" * 80)
        print("This suite will validate:")
        print("1. Flag dependencies and conflicts")
        print("2. Rollback procedures")
        print("3. Real-time monitoring")
        print("")
        
        # Run all tests
        success = runner.run_all_tests()
        
        # Ask about cleanup
        if success:
            print("\n🎉 All validation tests passed!")
            print("Feature flag system is ready for production.")
        else:
            print("\n❌ Some validation tests failed.")
            print("Please fix the issues before proceeding.")
        
        # Cleanup option
        print("\nWould you like to clean up test files? (y/n): ", end="")
        try:
            cleanup = input().lower().strip()
            if cleanup in ['y', 'yes']:
                runner.cleanup_test_files()
        except KeyboardInterrupt:
            print("\nCleanup skipped.")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n❌ Validation cancelled by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n💥 Unexpected error during validation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
