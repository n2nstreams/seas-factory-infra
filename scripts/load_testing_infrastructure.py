#!/usr/bin/env python3
"""
Load Testing Infrastructure
This script provides load testing capabilities to verify system performance at 1.5x expected peak traffic.
"""

import asyncio
import aiohttp
import time
import statistics
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
import sys
from dataclasses import dataclass

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")

@dataclass
class LoadTestResult:
    """Result of a load test"""
    endpoint: str
    method: str
    response_time_ms: float
    status_code: int
    success: bool
    error_message: Optional[str] = None

class LoadTestingInfrastructure:
    """Load testing infrastructure for system performance validation"""
    
    def __init__(self):
        self.base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
        self.results: List[LoadTestResult] = []
        self.test_config = {
            'concurrent_users': 50,  # Simulate 50 concurrent users
            'requests_per_user': 10,  # Each user makes 10 requests
            'ramp_up_time_seconds': 30,  # Ramp up over 30 seconds
            'peak_load_multiplier': 1.5,  # Test at 1.5x expected peak
            'timeout_seconds': 30
        }
        
        # Define test endpoints
        self.test_endpoints = [
            {'path': '/health', 'method': 'GET', 'weight': 30},  # Health checks (30% of traffic)
            {'path': '/api/users', 'method': 'GET', 'weight': 25},  # User queries (25% of traffic)
            {'path': '/api/ideas', 'method': 'GET', 'weight': 20},  # Idea queries (20% of traffic)
            {'path': '/api/tenants', 'method': 'GET', 'weight': 15},  # Tenant queries (15% of traffic)
            {'path': '/api/health', 'method': 'GET', 'weight': 10},  # API health (10% of traffic)
        ]
    
    async def test_endpoint(self, session: aiohttp.ClientSession, endpoint: Dict, user_id: int) -> LoadTestResult:
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint['path']}"
        method = endpoint['method']
        
        start_time = time.time()
        
        try:
            async with session.request(method, url, timeout=self.test_config['timeout_seconds']) as response:
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                return LoadTestResult(
                    endpoint=endpoint['path'],
                    method=method,
                    response_time_ms=round(response_time, 2),
                    status_code=response.status,
                    success=200 <= response.status < 400,
                    error_message=None
                )
                
        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return LoadTestResult(
                endpoint=endpoint['path'],
                method=method,
                response_time_ms=round(response_time, 2),
                status_code=0,
                success=False,
                error_message="Timeout"
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return LoadTestResult(
                endpoint=endpoint['path'],
                method=method,
                response_time_ms=round(response_time, 2),
                status_code=0,
                success=False,
                error_message=str(e)
            )
    
    async def simulate_user_workload(self, session: aiohttp.ClientSession, user_id: int) -> List[LoadTestResult]:
        """Simulate a single user's workload"""
        user_results = []
        
        # Generate weighted random endpoint selection
        total_weight = sum(endpoint['weight'] for endpoint in self.test_endpoints)
        
        for _ in range(self.test_config['requests_per_user']):
            # Simple weighted random selection
            rand_val = total_weight * (user_id % 100) / 100
            cumulative_weight = 0
            selected_endpoint = None
            
            for endpoint in self.test_endpoints:
                cumulative_weight += endpoint['weight']
                if rand_val <= cumulative_weight:
                    selected_endpoint = endpoint
                    break
            
            if selected_endpoint:
                result = await self.test_endpoint(session, selected_endpoint, user_id)
                user_results.append(result)
                
                # Small delay between requests to simulate real user behavior
                await asyncio.sleep(0.1)
        
        return user_results
    
    async def run_load_test(self) -> Dict[str, Any]:
        """Run the complete load test"""
        print("🚀 LOAD TESTING INFRASTRUCTURE")
        print("=" * 60)
        print(f"Target: {self.base_url}")
        print(f"Concurrent Users: {self.test_config['concurrent_users']}")
        print(f"Requests per User: {self.test_config['requests_per_user']}")
        print(f"Total Requests: {self.test_config['concurrent_users'] * self.test_config['requests_per_user']}")
        print(f"Peak Load Multiplier: {self.test_config['peak_load_multiplier']}x")
        print(f"Ramp Up Time: {self.test_config['ramp_up_time_seconds']} seconds")
        print("=" * 60)
        
        start_time = time.time()
        
        # Create HTTP session
        timeout = aiohttp.ClientTimeout(total=self.test_config['timeout_seconds'])
        async with aiohttp.ClientSession(timeout=timeout) as session:
            
            # Test endpoints availability first
            print("\n🔍 Testing Endpoint Availability...")
            for endpoint in self.test_endpoints:
                try:
                    url = f"{self.base_url}{endpoint['path']}"
                    async with session.get(url, timeout=5) as response:
                        status = "✅" if response.status < 400 else "❌"
                        print(f"   {status} {endpoint['method']} {endpoint['path']} - {response.status}")
                except Exception as e:
                    print(f"   ❌ {endpoint['method']} {endpoint['path']} - Error: {e}")
            
            # Run load test
            print(f"\n🔥 Starting Load Test with {self.test_config['concurrent_users']} concurrent users...")
            
            # Create tasks for concurrent users
            tasks = []
            for user_id in range(self.test_config['concurrent_users']):
                # Stagger user start times to simulate ramp-up
                delay = (user_id / self.test_config['concurrent_users']) * self.test_config['ramp_up_time_seconds']
                task = asyncio.create_task(
                    self._delayed_user_workload(session, user_id, delay)
                )
                tasks.append(task)
            
            # Wait for all users to complete
            user_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Flatten results
            for user_result in user_results:
                if isinstance(user_result, list):
                    self.results.extend(user_result)
                else:
                    print(f"⚠️  User workload failed: {user_result}")
        
        total_time = time.time() - start_time
        
        # Generate comprehensive report
        report = self._generate_report(total_time)
        
        # Save results
        self._save_results(report)
        
        return report
    
    async def _delayed_user_workload(self, session: aiohttp.ClientSession, user_id: int, delay: float):
        """Run user workload with delay for ramp-up simulation"""
        if delay > 0:
            await asyncio.sleep(delay)
        
        return await self.simulate_user_workload(session, user_id)
    
    def _generate_report(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive load test report"""
        if not self.results:
            return {"error": "No test results available"}
        
        # Calculate basic metrics
        total_requests = len(self.results)
        successful_requests = len([r for r in self.results if r.success])
        failed_requests = total_requests - successful_requests
        
        # Response time statistics
        response_times = [r.response_time_ms for r in self.results if r.success]
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p50_response_time = statistics.median(response_times)
            p95_response_time = self._calculate_percentile(response_times, 95)
            p99_response_time = self._calculate_percentile(response_times, 99)
        else:
            avg_response_time = min_response_time = max_response_time = p50_response_time = p95_response_time = p99_response_time = 0
        
        # Endpoint-specific metrics
        endpoint_metrics = {}
        for endpoint in self.test_endpoints:
            path = endpoint['path']
            endpoint_results = [r for r in self.results if r.endpoint == path]
            
            if endpoint_results:
                endpoint_times = [r.response_time_ms for r in endpoint_results if r.success]
                endpoint_metrics[path] = {
                    'total_requests': len(endpoint_results),
                    'successful_requests': len([r for r in endpoint_results if r.success]),
                    'avg_response_time_ms': round(statistics.mean(endpoint_times), 2) if endpoint_times else 0,
                    'p95_response_time_ms': round(self._calculate_percentile(endpoint_times, 95), 2) if endpoint_times else 0,
                    'error_rate': (len(endpoint_results) - len(endpoint_times)) / len(endpoint_results) * 100
                }
        
        # Calculate throughput
        requests_per_second = total_requests / total_time if total_time > 0 else 0
        
        # Performance score calculation
        performance_score = self._calculate_performance_score(
            avg_response_time, p95_response_time, failed_requests, total_requests
        )
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'test_configuration': self.test_config,
            'summary': {
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'failed_requests': failed_requests,
                'success_rate': (successful_requests / total_requests * 100) if total_requests > 0 else 0,
                'total_time_seconds': round(total_time, 2),
                'requests_per_second': round(requests_per_second, 2)
            },
            'response_time_metrics': {
                'average_ms': round(avg_response_time, 2),
                'minimum_ms': round(min_response_time, 2),
                'maximum_ms': round(max_response_time, 2),
                'p50_ms': round(p50_response_time, 2),
                'p95_ms': round(p95_response_time, 2),
                'p99_ms': round(p99_response_time, 2)
            },
            'endpoint_metrics': endpoint_metrics,
            'performance_score': performance_score,
            'load_test_grade': self._get_load_test_grade(performance_score)
        }
        
        return report
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile value from list of numbers"""
        if not values:
            return 0
        
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower_index = int(index)
            upper_index = lower_index + 1
            weight = index - lower_index
            
            if upper_index >= len(sorted_values):
                return sorted_values[lower_index]
            
            return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight
    
    def _calculate_performance_score(self, avg_response_time: float, p95_response_time: float, 
                                   failed_requests: int, total_requests: int) -> float:
        """Calculate overall performance score"""
        # Response time score (lower is better)
        response_time_score = max(0, 100 - (avg_response_time * 0.5))
        
        # P95 score (lower is better)
        p95_score = max(0, 100 - (p95_response_time * 0.3))
        
        # Reliability score (higher success rate is better)
        success_rate = (total_requests - failed_requests) / total_requests if total_requests > 0 else 0
        reliability_score = success_rate * 100
        
        # Weighted average
        overall_score = (response_time_score * 0.4 + p95_score * 0.3 + reliability_score * 0.3)
        
        return round(overall_score, 1)
    
    def _get_load_test_grade(self, score: float) -> str:
        """Convert performance score to letter grade"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def _save_results(self, report: Dict[str, Any]):
        """Save load test results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON report
        json_filename = f"load_test_report_{timestamp}.json"
        with open(json_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save human-readable summary
        summary_filename = f"load_test_summary_{timestamp}.txt"
        with open(summary_filename, 'w') as f:
            f.write(self._generate_summary(report))
        
        print(f"\n📁 Load test report saved to: {json_filename}")
        print(f"📁 Load test summary saved to: {summary_filename}")
    
    def _generate_summary(self, report: Dict[str, Any]) -> str:
        """Generate human-readable load test summary"""
        summary = []
        summary.append("LOAD TEST SUMMARY")
        summary.append("=" * 50)
        summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")
        
        # Test Configuration
        summary.append("TEST CONFIGURATION:")
        config = report['test_configuration']
        summary.append(f"  Base URL: {self.base_url}")
        summary.append(f"  Concurrent Users: {config['concurrent_users']}")
        summary.append(f"  Requests per User: {config['requests_per_user']}")
        summary.append(f"  Peak Load Multiplier: {config['peak_load_multiplier']}x")
        summary.append(f"  Ramp Up Time: {config['ramp_up_time_seconds']} seconds")
        
        # Summary
        summary.append("\nSUMMARY:")
        summ = report['summary']
        summary.append(f"  Total Requests: {summ['total_requests']:,}")
        summary.append(f"  Successful Requests: {summ['successful_requests']:,}")
        summary.append(f"  Failed Requests: {summ['failed_requests']:,}")
        summary.append(f"  Success Rate: {summ['success_rate']:.1f}%")
        summary.append(f"  Total Time: {summ['total_time_seconds']} seconds")
        summary.append(f"  Throughput: {summ['requests_per_second']:.1f} req/s")
        
        # Response Time Metrics
        summary.append("\nRESPONSE TIME METRICS:")
        rtm = report['response_time_metrics']
        summary.append(f"  Average: {rtm['average_ms']}ms")
        summary.append(f"  P50: {rtm['p50_ms']}ms")
        summary.append(f"  P95: {rtm['p95_ms']}ms")
        summary.append(f"  P99: {rtm['p99_ms']}ms")
        summary.append(f"  Min: {rtm['minimum_ms']}ms")
        summary.append(f"  Max: {rtm['maximum_ms']}ms")
        
        # Performance Score
        summary.append("\nPERFORMANCE ASSESSMENT:")
        summary.append(f"  Performance Score: {report['performance_score']}/100")
        summary.append(f"  Load Test Grade: {report['load_test_grade']}")
        
        return "\n".join(summary)

async def main():
    """Main function"""
    load_tester = LoadTestingInfrastructure()
    
    try:
        report = await load_tester.run_load_test()
        
        print("\n" + "=" * 60)
        print("📊 LOAD TEST RESULTS")
        print("=" * 60)
        
        summary = report['summary']
        print(f"Total Requests: {summary['total_requests']:,}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Throughput: {summary['requests_per_second']:.1f} req/s")
        
        rtm = report['response_time_metrics']
        print(f"Average Response Time: {rtm['average_ms']}ms")
        print(f"P95 Response Time: {rtm['p95_ms']}ms")
        
        print(f"Performance Score: {report['performance_score']}/100 ({report['load_test_grade']})")
        
        print("\n🎉 Load testing completed successfully!")
        print("📊 Use these results to compare against new system performance")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Load testing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
