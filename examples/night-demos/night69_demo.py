#!/usr/bin/env python3
"""
Night 69 Demo: k6 Load Testing via AIOpsAgent
Demonstration of the comprehensive load testing capabilities integrated with AIOpsAgent

This demo shows:
1. Starting different types of load tests (spike, load, stress, soak)
2. Monitoring test progress and results
3. Analyzing anomalies detected during load tests
4. Using Gemini AI for intelligent result analysis
5. Integration with existing monitoring and alerting systems
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List

import requests


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Night69Demo:
    """Demonstration of Night 69 load testing features"""
    
    def __init__(self, aiops_base_url: str = "http://localhost:8086"):
        self.aiops_base_url = aiops_base_url.rstrip('/')
        self.demo_results = {}
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request to AIOps agent"""
        url = f"{self.aiops_base_url}{endpoint}"
        
        headers = kwargs.get('headers', {})
        headers.update({
            'Content-Type': 'application/json',
            'X-Tenant-ID': 'demo-tenant'
        })
        kwargs['headers'] = headers
        
        logger.info(f"Making {method} request to {url}")
        
        response = requests.request(method, url, **kwargs)
        
        if response.status_code >= 400:
            logger.error(f"Request failed: {response.status_code} - {response.text}")
            response.raise_for_status()
            
        return response
    
    def check_aiops_health(self) -> bool:
        """Check if AIOps agent is running and healthy"""
        try:
            response = self._make_request('GET', '/health')
            health_data = response.json()
            
            logger.info(f"AIOps Agent Health: {health_data}")
            return health_data.get('status') == 'healthy'
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def start_load_test(self, test_name: str, test_config: Dict) -> str:
        """Start a load test with given configuration"""
        
        logger.info(f"🚀 Starting load test: {test_name}")
        logger.info(f"Configuration: {json.dumps(test_config, indent=2)}")
        
        try:
            response = self._make_request('POST', '/load-test/start', json=test_config)
            result = response.json()
            
            test_id = result['test_id']
            logger.info(f"✅ Load test started successfully: {test_id}")
            
            self.demo_results[test_name] = {
                'test_id': test_id,
                'config': test_config,
                'started_at': datetime.now().isoformat(),
                'status': 'started'
            }
            
            return test_id
            
        except Exception as e:
            logger.error(f"❌ Failed to start load test {test_name}: {e}")
            raise
    
    def monitor_load_test(self, test_id: str, test_name: str = None) -> Dict:
        """Monitor a running load test"""
        
        name = test_name or test_id
        logger.info(f"📊 Monitoring load test: {name}")
        
        while True:
            try:
                response = self._make_request('GET', f'/load-test/{test_id}/status')
                status = response.json()
                
                progress = status.get('progress_percentage', 0)
                current_status = status.get('status')
                
                logger.info(f"Status: {current_status} | Progress: {progress:.1f}% | "
                          f"Requests: {status.get('total_requests', 0)} | "
                          f"Error Rate: {status.get('error_rate', 0):.1%}")
                
                if current_status in ['completed', 'failed', 'cancelled']:
                    logger.info(f"🏁 Load test {name} finished with status: {current_status}")
                    
                    if test_name and test_name in self.demo_results:
                        self.demo_results[test_name]['final_status'] = status
                        self.demo_results[test_name]['completed_at'] = datetime.now().isoformat()
                    
                    return status
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"❌ Error monitoring load test {name}: {e}")
                return None
    
    def get_load_test_results(self, test_id: str) -> Dict:
        """Get detailed results of a completed load test"""
        
        try:
            response = self._make_request('GET', f'/load-test/{test_id}/result')
            return response.json()
            
        except Exception as e:
            logger.error(f"❌ Failed to get load test results for {test_id}: {e}")
            return None
    
    def analyze_results(self, test_name: str, results: Dict):
        """Analyze and display load test results"""
        
        if not results or 'result' not in results:
            logger.warning(f"⚠️ No results available for {test_name}")
            return
        
        result = results['result']
        
        logger.info(f"\n📈 LOAD TEST RESULTS: {test_name}")
        logger.info("=" * 60)
        
        # Basic metrics
        logger.info(f"Test ID: {result['test_id']}")
        logger.info(f"Test Type: {result['test_type']}")
        logger.info(f"Status: {result['status']}")
        logger.info(f"Duration: {result.get('duration_seconds', 0):.1f} seconds")
        
        # Performance metrics
        logger.info(f"\n📊 Performance Metrics:")
        logger.info(f"  Total Requests: {result['total_requests']:,}")
        logger.info(f"  Failed Requests: {result['failed_requests']:,}")
        logger.info(f"  Error Rate: {result['error_rate']:.1%}")
        logger.info(f"  Avg Response Time: {result['avg_response_time']:.2f}ms")
        logger.info(f"  95th Percentile: {result['p95_response_time']:.2f}ms")
        logger.info(f"  Requests/Second: {result['requests_per_second']:.2f}")
        logger.info(f"  Data Received: {result['data_received_mb']:.2f} MB")
        
        # Threshold results
        logger.info(f"\n🎯 Threshold Results:")
        thresholds = result.get('thresholds_passed', {})
        for threshold, passed in thresholds.items():
            status_icon = "✅" if passed else "❌"
            logger.info(f"  {status_icon} {threshold}: {'PASS' if passed else 'FAIL'}")
        
        overall_passed = result.get('overall_passed', False)
        overall_icon = "✅" if overall_passed else "❌"
        logger.info(f"\n{overall_icon} Overall Result: {'PASS' if overall_passed else 'FAIL'}")
        
        # Anomalies
        anomalies = result.get('anomalies_detected', [])
        if anomalies:
            logger.info(f"\n⚠️ Anomalies Detected: {len(anomalies)}")
            for anomaly_id in anomalies:
                logger.info(f"  - {anomaly_id}")
        else:
            logger.info(f"\n✅ No anomalies detected")
        
        # Store results for summary
        if test_name in self.demo_results:
            self.demo_results[test_name]['results'] = result
    
    def get_anomalies(self) -> List[Dict]:
        """Get all detected anomalies"""
        
        try:
            response = self._make_request('GET', '/anomalies?limit=100')
            return response.json().get('anomalies', [])
            
        except Exception as e:
            logger.error(f"❌ Failed to get anomalies: {e}")
            return []
    
    def get_alerts(self) -> List[Dict]:
        """Get all active alerts"""
        
        try:
            response = self._make_request('GET', '/alerts')
            return response.json().get('alerts', [])
            
        except Exception as e:
            logger.error(f"❌ Failed to get alerts: {e}")
            return []
    
    def quick_stress_test(self, target_url: str, duration: int = 2, users: int = 50) -> str:
        """Run a quick stress test using the simplified endpoint"""
        
        logger.info(f"⚡ Running quick stress test on {target_url}")
        
        try:
            params = {
                'target_url': target_url,
                'duration_minutes': duration,
                'virtual_users': users
            }
            
            response = self._make_request('POST', '/load-test/quick-stress', params=params)
            result = response.json()
            
            test_id = result['test_id']
            logger.info(f"✅ Quick stress test started: {test_id}")
            
            return test_id
            
        except Exception as e:
            logger.error(f"❌ Quick stress test failed: {e}")
            raise
    
    async def run_comprehensive_demo(self):
        """Run comprehensive demonstration of all load testing features"""
        
        logger.info("🎬 Starting Night 69 Load Testing Demo")
        logger.info("=" * 60)
        
        # 1. Health check
        logger.info("\n1️⃣ Checking AIOps Agent Health...")
        if not self.check_aiops_health():
            logger.error("❌ AIOps agent is not healthy. Please start the service first.")
            return
        
        # 2. Define test configurations
        test_configs = {
            "spike_test": {
                "test_type": "spike",
                "target": {
                    "name": "orchestrator-spike",
                    "base_url": "http://localhost:8080",
                    "endpoints": ["/health", "/orchestrator/agents"]
                },
                "duration_minutes": 3,
                "virtual_users": 30,
                "ramp_up_duration_seconds": 20,
                "thresholds": {
                    "http_req_duration": ["p(95)<3000"],
                    "http_req_failed": ["rate<0.15"]
                }
            },
            
            "load_test": {
                "test_type": "load",
                "target": {
                    "name": "orchestrator-sustained",
                    "base_url": "http://localhost:8080",
                    "endpoints": ["/health", "/metrics"]
                },
                "duration_minutes": 5,
                "virtual_users": 20,
                "ramp_up_duration_seconds": 30,
                "thresholds": {
                    "http_req_duration": ["p(95)<2000"],
                    "http_req_failed": ["rate<0.1"]
                }
            },
            
            "stress_test": {
                "test_type": "stress",
                "target": {
                    "name": "orchestrator-stress",
                    "base_url": "http://localhost:8080",
                    "endpoints": ["/health"]
                },
                "duration_minutes": 4,
                "virtual_users": 50,
                "ramp_up_duration_seconds": 45,
                "thresholds": {
                    "http_req_duration": ["p(95)<5000"],
                    "http_req_failed": ["rate<0.2"]
                }
            }
        }
        
        # 3. Start load tests
        logger.info("\n2️⃣ Starting Multiple Load Tests...")
        test_ids = {}
        
        for test_name, config in test_configs.items():
            try:
                test_id = self.start_load_test(test_name, config)
                test_ids[test_name] = test_id
                time.sleep(5)  # Stagger test starts
            except Exception as e:
                logger.error(f"Failed to start {test_name}: {e}")
        
        # 4. Monitor tests (run one at a time for demo)
        logger.info("\n3️⃣ Monitoring Load Tests...")
        
        for test_name, test_id in test_ids.items():
            logger.info(f"\n--- Monitoring {test_name} ---")
            status = self.monitor_load_test(test_id, test_name)
            
            if status:
                # Get detailed results
                results = self.get_load_test_results(test_id)
                if results:
                    self.analyze_results(test_name, results)
            
            logger.info(f"Waiting before next test...")
            time.sleep(10)
        
        # 5. Quick stress test demo
        logger.info("\n4️⃣ Quick Stress Test Demo...")
        try:
            quick_test_id = self.quick_stress_test("http://localhost:8080", duration=2, users=25)
            self.monitor_load_test(quick_test_id, "quick_stress")
            
            quick_results = self.get_load_test_results(quick_test_id)
            if quick_results:
                self.analyze_results("quick_stress", quick_results)
                
        except Exception as e:
            logger.error(f"Quick stress test failed: {e}")
        
        # 6. Check for anomalies and alerts
        logger.info("\n5️⃣ Checking Anomalies and Alerts...")
        
        anomalies = self.get_anomalies()
        if anomalies:
            logger.info(f"🔍 Found {len(anomalies)} anomalies:")
            for anomaly in anomalies[:5]:  # Show first 5
                logger.info(f"  - {anomaly['anomaly_type']}: {anomaly['description']}")
        else:
            logger.info("✅ No anomalies detected")
        
        alerts = self.get_alerts()
        if alerts:
            logger.info(f"🚨 Found {len(alerts)} active alerts:")
            for alert in alerts[:3]:  # Show first 3
                logger.info(f"  - {alert['anomaly']['anomaly_type']}: {alert['anomaly']['severity']}")
        else:
            logger.info("✅ No active alerts")
        
        # 7. Summary
        self.print_demo_summary()
    
    def print_demo_summary(self):
        """Print summary of all demo results"""
        
        logger.info("\n🎯 DEMO SUMMARY")
        logger.info("=" * 60)
        
        total_tests = len(self.demo_results)
        successful_tests = sum(1 for result in self.demo_results.values() 
                             if result.get('final_status', {}).get('status') == 'completed')
        
        logger.info(f"Total Tests Run: {total_tests}")
        logger.info(f"Successful Tests: {successful_tests}")
        logger.info(f"Success Rate: {successful_tests/total_tests*100:.1f}%" if total_tests > 0 else "N/A")
        
        for test_name, result in self.demo_results.items():
            status = result.get('final_status', {}).get('status', 'unknown')
            duration = result.get('final_status', {}).get('duration_seconds', 0)
            
            logger.info(f"\n{test_name}:")
            logger.info(f"  Status: {status}")
            logger.info(f"  Duration: {duration:.1f}s")
            
            if 'results' in result:
                test_result = result['results']
                logger.info(f"  Requests: {test_result['total_requests']:,}")
                logger.info(f"  Error Rate: {test_result['error_rate']:.1%}")
                logger.info(f"  Avg Response: {test_result['avg_response_time']:.2f}ms")
                logger.info(f"  Thresholds: {'PASS' if test_result['overall_passed'] else 'FAIL'}")
        
        logger.info(f"\n✨ Night 69 Demo Completed Successfully!")
        logger.info("Key Features Demonstrated:")
        logger.info("  ✅ Multiple load test types (spike, load, stress)")
        logger.info("  ✅ Real-time monitoring and progress tracking")
        logger.info("  ✅ Comprehensive result analysis")
        logger.info("  ✅ Anomaly detection integration")
        logger.info("  ✅ Alert system integration")
        logger.info("  ✅ Quick stress testing")
        logger.info("  ✅ Gemini AI analysis (if configured)")


def main():
    """Main demo function"""
    
    # Configuration
    AIOPS_URL = "http://localhost:8086"
    
    # Create demo instance
    demo = Night69Demo(AIOPS_URL)
    
    # Run the demo
    try:
        asyncio.run(demo.run_comprehensive_demo())
    except KeyboardInterrupt:
        logger.info("\n🛑 Demo interrupted by user")
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        raise


if __name__ == "__main__":
    main() 