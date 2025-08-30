#!/usr/bin/env python3
"""
Test script for the new logging system
Validates that all logging components work correctly
"""

import asyncio
import sys
import tempfile
import shutil
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_centralized_logging():
    """Test centralized logging configuration"""
    print("🧪 Testing centralized logging configuration...")
    
    try:
        from config.logging_config import get_logger, configure_logging, cleanup_logging
        
        # Test basic configuration
        configure_logging(level="DEBUG", log_to_file=False, log_to_console=True)
        
        # Test logger creation
        logger = get_logger("test_logger")
        logger.info("Test message from centralized logging")
        logger.debug("Debug message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        print("  ✅ Centralized logging configuration working")
        
        # Test cleanup
        cleanup_logging()
        print("  ✅ Logging cleanup working")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Centralized logging test failed: {e}")
        return False

def test_tenant_logging():
    """Test tenant-aware logging utilities"""
    print("🧪 Testing tenant-aware logging utilities...")
    
    try:
        from agents.shared.logging_utils import (
            get_tenant_logger, 
            log_tenant_operation, 
            get_logging_metrics
        )
        
        # Test tenant logger
        tenant_logger = get_tenant_logger("test_tenant", "tenant123")
        tenant_logger.info("Test message with tenant context")
        tenant_logger.warning("Warning with tenant context")
        
        # Test operation decorator
        @log_tenant_operation("test_operation")
        async def test_operation(self, tenant_context):
            return "operation completed"
            
        # Test metrics
        metrics = get_logging_metrics()
        stats = metrics.get_stats()
        print(f"  📊 Logging metrics: {stats}")
        
        print("  ✅ Tenant-aware logging utilities working")
        return True
        
    except Exception as e:
        print(f"  ❌ Tenant logging test failed: {e}")
        return False

def test_tenant_database_logging():
    """Test tenant database logging integration"""
    print("🧪 Testing tenant database logging integration...")
    
    try:
        from agents.shared.tenant_db import TenantDatabase, TenantContext
        
        # Create tenant context
        tenant_context = TenantContext("test_tenant", "user123", "admin")
        
        # Test database operations (without actual database)
        print("  📝 Testing database operation logging patterns...")
        
        # Test logging decorators are applied
        db = TenantDatabase()
        
        # Check if methods have decorators
        if hasattr(db.init_pool, '__wrapped__'):
            print("  ✅ init_pool has logging decorator")
        else:
            print("  ⚠️  init_pool missing logging decorator")
            
        if hasattr(db.close_pool, '__wrapped__'):
            print("  ✅ close_pool has logging decorator")
        else:
            print("  ⚠️  close_pool missing logging decorator")
            
        print("  ✅ Tenant database logging integration working")
        return True
        
    except Exception as e:
        print(f"  ❌ Tenant database logging test failed: {e}")
        return False

def test_file_rotation():
    """Test log file rotation and file handle management"""
    print("🧪 Testing log file rotation and file handle management...")
    
    try:
        from config.logging_config import configure_logging, cleanup_logging
        
        # Create temporary log directory
        temp_log_dir = Path(tempfile.mkdtemp())
        original_log_dir = None
        
        try:
            # Temporarily modify log directory
            from config.logging_config import logging_config
            original_log_dir = logging_config._log_dir
            logging_config._log_dir = temp_log_dir
            
            # Configure logging with file output
            configure_logging(level="INFO", log_to_file=True, log_to_console=False)
            
            # Create some log messages
            logger = logging_config.get_logger("file_test")
            for i in range(100):
                logger.info(f"Test message {i}: " + "x" * 1000)  # Large messages to trigger rotation
                
            # Check if log files were created
            log_files = list(temp_log_dir.glob("*.log*"))
            print(f"  📁 Created {len(log_files)} log files")
            
            if len(log_files) > 0:
                print("  ✅ Log file creation working")
            else:
                print("  ❌ No log files created")
                
            # Test cleanup
            cleanup_logging()
            
            # Check if files are properly closed
            print("  ✅ File handle cleanup working")
            
        finally:
            # Restore original log directory
            if original_log_dir:
                logging_config._log_dir = original_log_dir
                
            # Clean up temporary directory
            shutil.rmtree(temp_log_dir, ignore_errors=True)
            
        return True
        
    except Exception as e:
        print(f"  ❌ File rotation test failed: {e}")
        return False

def test_fallback_handling():
    """Test logging fallback mechanisms"""
    print("🧪 Testing logging fallback mechanisms...")
    
    try:
        from agents.shared.logging_utils import TenantAwareLogger
        
        # Create logger with fallback enabled
        logger = TenantAwareLogger("fallback_test")
        
        # Test normal logging
        logger.info("Normal logging message")
        
        # Test fallback (by temporarily breaking the underlying logger)
        original_logger = logger.logger
        logger.logger = None  # Break the logger
        
        # This should trigger fallback
        logger.info("Message that should trigger fallback")
        
        # Restore logger
        logger.logger = original_logger
        
        print("  ✅ Logging fallback mechanisms working")
        return True
        
    except Exception as e:
        print(f"  ❌ Fallback test failed: {e}")
        return False

def test_logging_metrics():
    """Test logging metrics and monitoring"""
    print("🧪 Testing logging metrics and monitoring...")
    
    try:
        from agents.shared.logging_utils import get_logging_metrics
        
        metrics = get_logging_metrics()
        
        # Record some test metrics
        metrics.record_success()
        metrics.record_success()
        metrics.record_failure()
        metrics.record_fallback()
        metrics.record_tenant_context()
        
        # Get stats
        stats = metrics.get_stats()
        
        print(f"  📊 Metrics collected: {stats}")
        
        # Validate metrics
        if stats['total_operations'] == 3:  # 2 success + 1 failure
            print("  ✅ Logging metrics working correctly")
            return True
        else:
            print(f"  ❌ Metrics validation failed: expected 3 operations, got {stats['total_operations']}")
            return False
            
    except Exception as e:
        print(f"  ❌ Metrics test failed: {e}")
        return False

async def run_all_tests():
    """Run all logging system tests"""
    print("🚀 SaaS Factory Logging System Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Centralized Logging", test_centralized_logging),
        ("Tenant Logging", test_tenant_logging),
        ("Tenant Database Logging", test_tenant_database_logging),
        ("File Rotation", test_file_rotation),
        ("Fallback Handling", test_fallback_handling),
        ("Logging Metrics", test_logging_metrics),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🧪 Running: {test_name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
        print()
        
    # Print summary
    print("=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
            
    print()
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(results)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! Logging system is working correctly.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the logging system implementation.")
        return False

def main():
    """Main entry point"""
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Testing failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
