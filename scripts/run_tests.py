#!/usr/bin/env python3
"""
Test Runner Script
Comprehensive test execution with proper setup and teardown
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any
import json


class TestRunner:
    """Main test runner class"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tests_dir = self.project_root / "tests"
        self.logs_dir = self.tests_dir / "logs"
        
        # Ensure logs directory exists
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Test categories
        self.test_categories = {
            "unit": "tests/unit",
            "integration": "tests/integration", 
            "load": "tests/load",
            "smoke": "tests/smoke",
            "security": "tests/security"
        }
    
    def setup_test_environment(self):
        """Set up test environment"""
        print("🔧 Setting up test environment...")
        
        # Set environment variables
        os.environ["ENVIRONMENT"] = "test"
        os.environ["DEBUG"] = "true"
        os.environ["LOG_LEVEL"] = "DEBUG"
        os.environ["DB_NAME"] = "factorydb_test"
        os.environ["DB_PASSWORD"] = "testpass"
        os.environ["OPENAI_API_KEY"] = "test-key"
        os.environ["JWT_SECRET_KEY"] = "test-jwt-secret"
        
        # Switch to test configuration
        config_script = self.project_root / "scripts" / "manage_config.py"
        if config_script.exists():
            try:
                subprocess.run([
                    sys.executable, str(config_script), "create", "test", 
                    "--template", "development"
                ], check=True, capture_output=True)
                
                subprocess.run([
                    sys.executable, str(config_script), "switch", "test"
                ], check=True, capture_output=True)
                
                print("✅ Test configuration activated")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Warning: Could not set test configuration: {e}")
        
        print("✅ Test environment setup complete")
    
    def run_tests(self, category: str = "all", verbose: bool = True, 
                  coverage: bool = True, markers: List[str] = None) -> Dict[str, Any]:
        """Run tests with specified parameters"""
        
        print(f"🧪 Running {category} tests...")
        
        # Build pytest command
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add test paths
        if category == "all":
            cmd.append(str(self.tests_dir))
        elif category in self.test_categories:
            test_path = self.project_root / self.test_categories[category]
            if test_path.exists():
                cmd.append(str(test_path))
            else:
                print(f"⚠️  Warning: Test path {test_path} does not exist")
                return {"success": False, "error": f"Test path not found: {test_path}"}
        else:
            print(f"❌ Unknown test category: {category}")
            return {"success": False, "error": f"Unknown category: {category}"}
        
        # Add markers
        if markers:
            for marker in markers:
                cmd.extend(["-m", marker])
        
        # Add options
        if verbose:
            cmd.append("-v")
        
        if coverage:
            cmd.extend([
                "--cov=agents",
                "--cov=config",
                "--cov-report=html:htmlcov",
                "--cov-report=term-missing",
                "--cov-fail-under=70"
            ])
        
        # Set working directory
        original_dir = os.getcwd()
        os.chdir(self.project_root)
        
        try:
            # Run tests
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True)
            duration = time.time() - start_time
            
            # Parse results
            success = result.returncode == 0
            
            if success:
                print(f"✅ Tests passed in {duration:.2f} seconds")
            else:
                print(f"❌ Tests failed in {duration:.2f} seconds")
                if result.stderr:
                    print(f"Error output:\n{result.stderr}")
            
            return {
                "success": success,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        finally:
            os.chdir(original_dir)
    
    def run_specific_test(self, test_file: str, test_function: str = None) -> Dict[str, Any]:
        """Run a specific test file or function"""
        
        cmd = [sys.executable, "-m", "pytest", "-v"]
        
        if test_function:
            cmd.append(f"{test_file}::{test_function}")
        else:
            cmd.append(test_file)
        
        # Set working directory
        original_dir = os.getcwd()
        os.chdir(self.project_root)
        
        try:
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True)
            duration = time.time() - start_time
            
            success = result.returncode == 0
            
            if success:
                print(f"✅ Test passed in {duration:.2f} seconds")
            else:
                print(f"❌ Test failed in {duration:.2f} seconds")
                if result.stderr:
                    print(f"Error output:\n{result.stderr}")
            
            return {
                "success": success,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        finally:
            os.chdir(original_dir)
    
    def run_smoke_tests(self) -> Dict[str, Any]:
        """Run smoke tests to verify basic functionality"""
        
        print("🔥 Running smoke tests...")
        
        return self.run_tests(
            category="smoke",
            verbose=True,
            coverage=False,
            markers=["smoke"]
        )
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        
        print("🔗 Running integration tests...")
        
        return self.run_tests(
            category="integration",
            verbose=True,
            coverage=True,
            markers=["integration"]
        )
    
    def run_load_tests(self) -> Dict[str, Any]:
        """Run load/performance tests"""
        
        print("⚡ Running load tests...")
        
        return self.run_tests(
            category="load",
            verbose=True,
            coverage=False,
            markers=["slow"]
        )
    
    def run_security_tests(self) -> Dict[str, Any]:
        """Run security tests"""
        
        print("🔒 Running security tests...")
        
        return self.run_tests(
            category="security",
            verbose=True,
            coverage=True,
            markers=["security"]
        )
    
    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """Generate test report"""
        
        report_file = self.logs_dir / f"test_report_{int(time.time())}.json"
        
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Test report saved to: {report_file}")
        
        return str(report_file)
    
    def cleanup_test_environment(self):
        """Clean up test environment"""
        print("🧹 Cleaning up test environment...")
        
        # Remove test database (if exists)
        try:
            import asyncpg
            import asyncio
            
            async def cleanup_db():
                try:
                    conn = await asyncpg.connect(
                        host="localhost",
                        port=5432,
                        database="postgres",
                        user="factoryadmin",
                        password="testpass"
                    )
                    await conn.execute("DROP DATABASE IF EXISTS factorydb_test")
                    await conn.close()
                    print("✅ Test database cleaned up")
                except Exception as e:
                    print(f"⚠️  Warning: Could not clean up test database: {e}")
            
            asyncio.run(cleanup_db())
            
        except ImportError:
            print("⚠️  Warning: Could not clean up test database - asyncpg not available")
        
        # Reset environment
        config_script = self.project_root / "scripts" / "manage_config.py"
        if config_script.exists():
            try:
                subprocess.run([
                    sys.executable, str(config_script), "switch", "development"
                ], check=True, capture_output=True)
                print("✅ Switched back to development configuration")
            except subprocess.CalledProcessError:
                print("⚠️  Warning: Could not switch back to development configuration")
        
        print("✅ Test environment cleanup complete")
    
    def run_full_test_suite(self) -> Dict[str, Any]:
        """Run complete test suite"""
        
        print("🚀 Running full test suite...")
        
        results = {
            "start_time": time.time(),
            "tests": {}
        }
        
        # Run different test categories
        test_categories = [
            ("smoke", self.run_smoke_tests),
            ("unit", lambda: self.run_tests("unit", coverage=True)),
            ("integration", self.run_integration_tests),
            ("security", self.run_security_tests)
        ]
        
        for category, test_func in test_categories:
            print(f"\n{'='*50}")
            print(f"Running {category.upper()} tests")
            print(f"{'='*50}")
            
            try:
                result = test_func()
                results["tests"][category] = result
                
                if not result["success"]:
                    print(f"❌ {category} tests failed - stopping test suite")
                    break
                    
            except Exception as e:
                print(f"❌ Error running {category} tests: {e}")
                results["tests"][category] = {
                    "success": False,
                    "error": str(e)
                }
                break
        
        # Calculate overall results
        results["end_time"] = time.time()
        results["total_duration"] = results["end_time"] - results["start_time"]
        results["overall_success"] = all(
            test_result.get("success", False) 
            for test_result in results["tests"].values()
        )
        
        # Generate report
        report_file = self.generate_test_report(results)
        
        # Print summary
        print(f"\n{'='*50}")
        print("TEST SUITE SUMMARY")
        print(f"{'='*50}")
        print(f"Total duration: {results['total_duration']:.2f} seconds")
        print(f"Overall success: {'✅' if results['overall_success'] else '❌'}")
        print(f"Report saved to: {report_file}")
        
        for category, result in results["tests"].items():
            status = "✅" if result.get("success", False) else "❌"
            duration = result.get("duration", 0)
            print(f"{category}: {status} ({duration:.2f}s)")
        
        return results


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="SaaS Factory Test Runner")
    parser.add_argument(
        "category",
        choices=["all", "unit", "integration", "load", "smoke", "security", "full"],
        default="all",
        nargs="?",
        help="Test category to run"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--no-coverage", action="store_true", help="Skip coverage reporting")
    parser.add_argument("--markers", "-m", nargs="+", help="Test markers to filter")
    parser.add_argument("--file", "-f", help="Run specific test file")
    parser.add_argument("--function", help="Run specific test function")
    parser.add_argument("--setup-only", action="store_true", help="Only setup test environment")
    parser.add_argument("--cleanup-only", action="store_true", help="Only cleanup test environment")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    try:
        if args.setup_only:
            runner.setup_test_environment()
            return 0
        
        if args.cleanup_only:
            runner.cleanup_test_environment()
            return 0
        
        # Setup test environment
        runner.setup_test_environment()
        
        # Run tests
        if args.file:
            result = runner.run_specific_test(args.file, args.function)
        elif args.category == "full":
            result = runner.run_full_test_suite()
        else:
            result = runner.run_tests(
                category=args.category,
                verbose=args.verbose,
                coverage=not args.no_coverage,
                markers=args.markers
            )
        
        # Return appropriate exit code
        if isinstance(result, dict) and "overall_success" in result:
            return 0 if result["overall_success"] else 1
        elif isinstance(result, dict) and "success" in result:
            return 0 if result["success"] else 1
        else:
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1
    finally:
        # Always cleanup
        if not args.setup_only:
            runner.cleanup_test_environment()


if __name__ == "__main__":
    sys.exit(main()) 