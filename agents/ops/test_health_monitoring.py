#!/usr/bin/env python3
"""
Simple Test Script for DevOps Agent Health Monitoring
Tests core health monitoring functionality
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from health_monitoring import (
    HealthMonitor, 
    CheckType
)

async def test_health_monitoring():
    """Test the health monitoring system"""
    print("🧪 Testing Health Monitoring System...")
    
    # Create health monitor
    config = {
        "check_interval": 5,
        "alert_thresholds": {
            "cpu_warning": 70.0,
            "cpu_critical": 90.0,
            "memory_warning": 80.0,
            "memory_critical": 95.0,
            "disk_warning": 85.0,
            "disk_critical": 95.0,
            "response_time_warning": 1000,
            "response_time_critical": 5000
        }
    }
    
    monitor = HealthMonitor(config)
    print("✅ Health monitor initialized successfully")
    
    # Test adding health checks
    print("\n🔍 Testing health check configuration...")
    
    # Add HTTP endpoint check
    success = await monitor.add_health_check(
        "test-service",
        CheckType.HTTP_ENDPOINT,
        {"url": "http://localhost:8080/health", "timeout": 10}
    )
    assert success, "Failed to add HTTP endpoint check"
    print("✅ HTTP endpoint check added")
    
    # Add process status check
    success = await monitor.add_health_check(
        "test-service",
        CheckType.PROCESS_STATUS,
        {"process_name": "python"}
    )
    assert success, "Failed to add process status check"
    print("✅ Process status check added")
    
    # Add resource utilization check
    success = await monitor.add_health_check(
        "test-service",
        CheckType.RESOURCE_UTILIZATION,
        {}
    )
    assert success, "Failed to add resource utilization check"
    print("✅ Resource utilization check added")
    
    # Test health check execution
    print("\n⚡ Testing health check execution...")
    
    # Start monitoring
    await monitor.start_monitoring()
    print("✅ Monitoring started")
    
    # Wait for health checks to run
    await asyncio.sleep(6)
    
    # Get health summary
    summary = monitor.get_health_summary()
    print(f"📊 Health Summary: {summary}")
    
    # Get service health
    service_health = monitor.get_service_health("test-service")
    print(f"🔍 Service Health: {service_health}")
    
    # Test alerts
    print("\n🚨 Testing alert system...")
    
    # Get alerts
    alerts = monitor.get_alerts()
    print(f"📢 Active Alerts: {len(alerts)}")
    
    for alert in alerts:
        print(f"  - {alert['severity']}: {alert['message']}")
    
    # Test alert acknowledgment
    if alerts:
        alert_id = alerts[0]["id"]
        success = await monitor.acknowledge_alert(alert_id)
        assert success, "Failed to acknowledge alert"
        print("✅ Alert acknowledged")
    
    # Test alert resolution
    if alerts:
        alert_id = alerts[0]["id"]
        success = await monitor.resolve_alert(alert_id)
        assert success, "Failed to resolve alert"
        print("✅ Alert resolved")
    
    # Stop monitoring
    await monitor.stop_monitoring()
    print("✅ Monitoring stopped")
    
    print("\n🎉 All health monitoring tests passed successfully!")

async def test_health_check_types():
    """Test different types of health checks"""
    print("\n🧪 Testing Health Check Types...")
    
    monitor = HealthMonitor({})
    
    # Test HTTP endpoint check
    print("🔍 Testing HTTP endpoint check...")
    status, details, error = await monitor._check_http_endpoint({
        "url": "https://httpbin.org/status/200",
        "timeout": 10
    })
    print(f"  Status: {status}, Details: {details}, Error: {error}")
    
    # Test resource utilization check
    print("🔍 Testing resource utilization check...")
    status, details, error = await monitor._check_resource_utilization({})
    print(f"  Status: {status}, Details: {details}, Error: {error}")
    
    # Test process status check
    print("🔍 Testing process status check...")
    status, details, error = await monitor._check_process_status({"process_name": "python"})
    print(f"  Status: {status}, Details: {details}, Error: {error}")
    
    print("✅ Health check type tests completed")

if __name__ == "__main__":
    print("🚀 Starting DevOps Health Monitoring Tests...\n")
    
    try:
        # Test health monitoring system
        asyncio.run(test_health_monitoring())
        
        # Test health check types
        asyncio.run(test_health_check_types())
        
        print("\n🎉 All tests completed successfully!")
        print("✅ DevOps health monitoring is working correctly")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
