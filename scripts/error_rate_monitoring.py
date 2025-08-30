#!/usr/bin/env python3
"""
Error Rate Monitoring
This script monitors error rates to ensure the new system maintains or improves upon legacy system reliability.
"""

import asyncio
import aiohttp
import time
import statistics
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
import sys
from dataclasses import dataclass
import logging

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ErrorMetric:
    """Error metric data point"""
    timestamp: datetime
    endpoint: str
    status_code: int
    response_time_ms: float
    is_error: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None

class ErrorRateMonitor:
    """Monitors error rates across system endpoints"""
    
    def __init__(self):
        self.base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
        self.monitoring_config = {
            'monitoring_duration_minutes': 10,  # Monitor for 10 minutes
            'request_interval_seconds': 2,  # Make request every 2 seconds
            'concurrent_requests': 5,  # 5 concurrent requests per interval
            'error_threshold_percentage': 5.0,  # Alert if error rate > 5%
            'response_time_threshold_ms': 1000,  # Alert if response time > 1 second
            'timeout_seconds': 10
        }
        
        # Define monitoring endpoints
        self.monitoring_endpoints = [
            {'path': '/health', 'method': 'GET', 'weight': 30},
            {'path': '/api/users', 'method': 'GET', 'weight': 25},
            {'path': '/api/ideas', 'method': 'GET', 'weight': 20},
            {'path': '/api/tenants', 'method': 'GET', 'weight': 15},
            {'path': '/api/health', 'method': 'GET', 'weight': 10},
        ]
        
        self.error_metrics: List[ErrorMetric] = []
        self.monitoring_results = {
            'start_time': None,
            'end_time': None,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'error_rate_percentage': 0.0,
            'avg_response_time_ms': 0.0,
            'p95_response_time_ms': 0.0,
            'endpoint_error_rates': {},
            'error_trends': [],
            'alerts': []
        }
    
    async def monitor_endpoint(self, session: aiohttp.ClientSession, endpoint: Dict) -> ErrorMetric:
        """Monitor a single endpoint for errors"""
        url = f"{self.base_url}{endpoint['path']}"
        method = endpoint['method']
        
        start_time = time.time()
        
        try:
            async with session.request(method, url, timeout=self.monitoring_config['timeout_seconds']) as response:
                response_time = (time.time() - start_time) * 1000
                
                is_error = response.status >= 400
                error_type = None
                error_message = None
                
                if is_error:
                    error_type = f"HTTP {response.status}"
                    if response.status >= 500:
                        error_type = "Server Error"
                    elif response.status >= 400:
                        error_type = "Client Error"
                
                return ErrorMetric(
                    timestamp=datetime.now(),
                    endpoint=endpoint['path'],
                    status_code=response.status,
                    response_time_ms=round(response_time, 2),
                    is_error=is_error,
                    error_type=error_type,
                    error_message=error_message
                )
                
        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return ErrorMetric(
                timestamp=datetime.now(),
                endpoint=endpoint['path'],
                status_code=0,
                response_time_ms=round(response_time, 2),
                is_error=True,
                error_type="Timeout",
                error_message="Request timed out"
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return ErrorMetric(
                timestamp=datetime.now(),
                endpoint=endpoint['path'],
                status_code=0,
                response_time_ms=round(response_time, 2),
                is_error=True,
                error_type="Connection Error",
                error_message=str(e)
            )
    
    async def run_monitoring_cycle(self, session: aiohttp.ClientSession) -> List[ErrorMetric]:
        """Run one monitoring cycle with concurrent requests"""
        tasks = []
        
        # Create concurrent requests to different endpoints
        for _ in range(self.monitoring_config['concurrent_requests']):
            # Select endpoint based on weight
            endpoint = self._select_weighted_endpoint()
            task = asyncio.create_task(self.monitor_endpoint(session, endpoint))
            tasks.append(task)
        
        # Wait for all requests to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid metrics
        valid_metrics = []
        for result in results:
            if isinstance(result, ErrorMetric):
                valid_metrics.append(result)
            else:
                logger.warning(f"Monitoring request failed: {result}")
        
        return valid_metrics
    
    def _select_weighted_endpoint(self) -> Dict:
        """Select endpoint based on weight distribution"""
        import random
        
        total_weight = sum(endpoint['weight'] for endpoint in self.monitoring_endpoints)
        rand_val = random.uniform(0, total_weight)
        
        cumulative_weight = 0
        for endpoint in self.monitoring_endpoints:
            cumulative_weight += endpoint['weight']
            if rand_val <= cumulative_weight:
                return endpoint
        
        return self.monitoring_endpoints[0]  # Fallback
    
    async def start_monitoring(self):
        """Start the error rate monitoring process"""
        print("🚀 ERROR RATE MONITORING")
        print("=" * 60)
        print(f"Target: {self.base_url}")
        print(f"Duration: {self.monitoring_config['monitoring_duration_minutes']} minutes")
        print(f"Request Interval: {self.monitoring_config['request_interval_seconds']} seconds")
        print(f"Concurrent Requests: {self.monitoring_config['concurrent_requests']}")
        print(f"Error Threshold: {self.monitoring_config['error_threshold_percentage']}%")
        print(f"Response Time Threshold: {self.monitoring_config['response_time_threshold_ms']}ms")
        print("=" * 60)
        
        self.monitoring_results['start_time'] = datetime.now()
        start_time = time.time()
        
        # Test endpoint availability first
        print("\n🔍 Testing Endpoint Availability...")
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for endpoint in self.monitoring_endpoints:
                try:
                    url = f"{self.base_url}{endpoint['path']}"
                    async with session.get(url) as response:
                        status = "✅" if response.status < 400 else "❌"
                        print(f"   {status} {endpoint['method']} {endpoint['path']} - {response.status}")
                except Exception as e:
                    print(f"   ❌ {endpoint['method']} {endpoint['path']} - Error: {e}")
        
        # Start monitoring
        print(f"\n📊 Starting monitoring for {self.monitoring_config['monitoring_duration_minutes']} minutes...")
        print("   Press Ctrl+C to stop early")
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.monitoring_config['timeout_seconds'])
            async with aiohttp.ClientSession(timeout=timeout) as session:
                
                cycle_count = 0
                while True:
                    cycle_start = time.time()
                    
                    # Run monitoring cycle
                    metrics = await self.run_monitoring_cycle(session)
                    self.error_metrics.extend(metrics)
                    
                    # Update real-time statistics
                    cycle_count += 1
                    elapsed_minutes = (time.time() - start_time) / 60
                    
                    if metrics:
                        error_count = sum(1 for m in metrics if m.is_error)
                        total_count = len(metrics)
                        error_rate = (error_count / total_count * 100) if total_count > 0 else 0
                        
                        print(f"   Cycle {cycle_count}: {error_count}/{total_count} errors ({error_rate:.1f}%) - {elapsed_minutes:.1f}min elapsed")
                        
                        # Check for immediate alerts
                        if error_rate > self.monitoring_config['error_threshold_percentage']:
                            alert_msg = f"⚠️  HIGH ERROR RATE: {error_rate:.1f}% (threshold: {self.monitoring_config['error_threshold_percentage']}%)"
                            print(f"   {alert_msg}")
                            self.monitoring_results['alerts'].append({
                                'timestamp': datetime.now().isoformat(),
                                'type': 'High Error Rate',
                                'message': alert_msg,
                                'error_rate': error_rate
                            })
                    
                    # Check if monitoring duration has elapsed
                    if elapsed_minutes >= self.monitoring_config['monitoring_duration_minutes']:
                        break
                    
                    # Wait for next cycle
                    cycle_duration = time.time() - cycle_start
                    wait_time = max(0, self.monitoring_config['request_interval_seconds'] - cycle_duration)
                    if wait_time > 0:
                        await asyncio.sleep(wait_time)
                        
        except KeyboardInterrupt:
            print("\n\n⚠️  Monitoring stopped by user")
        
        # Complete monitoring
        self.monitoring_results['end_time'] = datetime.now()
        await self._analyze_results()
        
        return True
    
    async def _analyze_results(self):
        """Analyze monitoring results and generate comprehensive report"""
        print("\n🔍 Analyzing monitoring results...")
        
        if not self.error_metrics:
            print("   ❌ No metrics collected")
            return
        
        # Calculate overall statistics
        total_requests = len(self.error_metrics)
        successful_requests = len([m for m in self.error_metrics if not m.is_error])
        failed_requests = total_requests - successful_requests
        
        self.monitoring_results.update({
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'error_rate_percentage': (failed_requests / total_requests * 100) if total_requests > 0 else 0
        })
        
        # Response time analysis
        response_times = [m.response_time_ms for m in self.error_metrics if not m.is_error]
        if response_times:
            self.monitoring_results['avg_response_time_ms'] = round(statistics.mean(response_times), 2)
            self.monitoring_results['p95_response_time_ms'] = round(self._calculate_percentile(response_times, 95), 2)
        
        # Endpoint-specific error rates
        endpoint_stats = {}
        for endpoint in self.monitoring_endpoints:
            path = endpoint['path']
            endpoint_metrics = [m for m in self.error_metrics if m.endpoint == path]
            
            if endpoint_metrics:
                total = len(endpoint_metrics)
                errors = sum(1 for m in endpoint_metrics if m.is_error)
                error_rate = (errors / total * 100) if total > 0 else 0
                
                endpoint_stats[path] = {
                    'total_requests': total,
                    'errors': errors,
                    'error_rate_percentage': round(error_rate, 2),
                    'avg_response_time_ms': round(statistics.mean([m.response_time_ms for m in endpoint_metrics]), 2)
                }
        
        self.monitoring_results['endpoint_error_rates'] = endpoint_stats
        
        # Error trend analysis (by minute)
        self._analyze_error_trends()
        
        # Generate alerts
        self._generate_alerts()
        
        # Print summary
        self._print_summary()
        
        # Save results
        self._save_results()
    
    def _analyze_error_trends(self):
        """Analyze error trends over time"""
        if not self.error_metrics:
            return
        
        # Group metrics by minute
        minute_groups = {}
        for metric in self.error_metrics:
            minute_key = metric.timestamp.replace(second=0, microsecond=0)
            if minute_key not in minute_groups:
                minute_groups[minute_key] = []
            minute_groups[minute_key].append(metric)
        
        # Calculate error rate for each minute
        for minute, metrics in sorted(minute_groups.items()):
            total = len(metrics)
            errors = sum(1 for m in metrics if m.is_error)
            error_rate = (errors / total * 100) if total > 0 else 0
            
            self.monitoring_results['error_trends'].append({
                'timestamp': minute.isoformat(),
                'total_requests': total,
                'errors': errors,
                'error_rate_percentage': round(error_rate, 2)
            })
    
    def _generate_alerts(self):
        """Generate alerts based on thresholds"""
        # High error rate alert
        if self.monitoring_results['error_rate_percentage'] > self.monitoring_config['error_threshold_percentage']:
            self.monitoring_results['alerts'].append({
                'timestamp': datetime.now().isoformat(),
                'type': 'Overall High Error Rate',
                'message': f"Overall error rate {self.monitoring_results['error_rate_percentage']:.1f}% exceeds threshold of {self.monitoring_config['error_threshold_percentage']}%",
                'error_rate': self.monitoring_results['error_rate_percentage']
            })
        
        # High response time alert
        if self.monitoring_results['avg_response_time_ms'] > self.monitoring_config['response_time_threshold_ms']:
            self.monitoring_results['alerts'].append({
                'timestamp': datetime.now().isoformat(),
                'type': 'High Response Time',
                'message': f"Average response time {self.monitoring_results['avg_response_time_ms']}ms exceeds threshold of {self.monitoring_config['response_time_threshold_ms']}ms",
                'response_time': self.monitoring_results['avg_response_time_ms']
            })
        
        # Endpoint-specific alerts
        for endpoint, stats in self.monitoring_results['endpoint_error_rates'].items():
            if stats['error_rate_percentage'] > self.monitoring_config['error_threshold_percentage']:
                self.monitoring_results['alerts'].append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'Endpoint High Error Rate',
                    'message': f"Endpoint {endpoint} has error rate {stats['error_rate_percentage']}%",
                    'endpoint': endpoint,
                    'error_rate': stats['error_rate_percentage']
                })
    
    def _print_summary(self):
        """Print monitoring summary"""
        print("\n" + "=" * 60)
        print("📊 MONITORING SUMMARY")
        print("=" * 60)
        
        results = self.monitoring_results
        print(f"Monitoring Duration: {results['start_time']} to {results['end_time']}")
        print(f"Total Requests: {results['total_requests']:,}")
        print(f"Successful Requests: {results['successful_requests']:,}")
        print(f"Failed Requests: {results['failed_requests']:,}")
        print(f"Overall Error Rate: {results['error_rate_percentage']:.2f}%")
        print(f"Average Response Time: {results['avg_response_time_ms']}ms")
        print(f"P95 Response Time: {results['p95_response_time_ms']}ms")
        
        print(f"\nEndpoint Error Rates:")
        for endpoint, stats in results['endpoint_error_rates'].items():
            print(f"  {endpoint}: {stats['error_rate_percentage']}% ({stats['errors']}/{stats['total_requests']})")
        
        if results['alerts']:
            print(f"\n⚠️  Alerts Generated: {len(results['alerts'])}")
            for alert in results['alerts']:
                print(f"  {alert['type']}: {alert['message']}")
        else:
            print(f"\n✅ No alerts generated - all metrics within thresholds")
    
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
    
    def _save_results(self):
        """Save monitoring results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON report
        json_filename = f"error_rate_monitoring_{timestamp}.json"
        with open(json_filename, 'w') as f:
            # Convert datetime objects to strings for JSON serialization
            json_data = self.monitoring_results.copy()
            if json_data['start_time']:
                json_data['start_time'] = json_data['start_time'].isoformat()
            if json_data['end_time']:
                json_data['end_time'] = json_data['end_time'].isoformat()
            
            json.dump(json_data, f, indent=2)
        
        # Save human-readable summary
        summary_filename = f"error_rate_monitoring_summary_{timestamp}.txt"
        with open(summary_filename, 'w') as f:
            f.write(self._generate_summary())
        
        print(f"\n📁 Monitoring report saved to: {json_filename}")
        print(f"📁 Monitoring summary saved to: {summary_filename}")
    
    def _generate_summary(self) -> str:
        """Generate human-readable monitoring summary"""
        summary = []
        summary.append("ERROR RATE MONITORING SUMMARY")
        summary.append("=" * 50)
        summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")
        
        results = self.monitoring_results
        
        # Basic Info
        summary.append("MONITORING INFORMATION:")
        summary.append(f"  Start Time: {results['start_time']}")
        summary.append(f"  End Time: {results['end_time']}")
        summary.append(f"  Duration: {self.monitoring_config['monitoring_duration_minutes']} minutes")
        
        # Overall Results
        summary.append("\nOVERALL RESULTS:")
        summary.append(f"  Total Requests: {results['total_requests']:,}")
        summary.append(f"  Successful Requests: {results['successful_requests']:,}")
        summary.append(f"  Failed Requests: {results['failed_requests']:,}")
        summary.append(f"  Error Rate: {results['error_rate_percentage']:.2f}%")
        summary.append(f"  Average Response Time: {results['avg_response_time_ms']}ms")
        summary.append(f"  P95 Response Time: {results['p95_response_time_ms']}ms")
        
        # Endpoint Results
        summary.append("\nENDPOINT ERROR RATES:")
        for endpoint, stats in results['endpoint_error_rates'].items():
            summary.append(f"  {endpoint}: {stats['error_rate_percentage']}% ({stats['errors']}/{stats['total_requests']})")
        
        # Alerts
        if results['alerts']:
            summary.append(f"\nALERTS ({len(results['alerts'])}):")
            for alert in results['alerts']:
                summary.append(f"  {alert['type']}: {alert['message']}")
        
        return "\n".join(summary)

async def main():
    """Main function"""
    monitor = ErrorRateMonitor()
    
    try:
        success = await monitor.start_monitoring()
        
        if success:
            print("\n🎉 Error rate monitoring completed successfully!")
            print("📊 Use these results to compare against new system performance")
            sys.exit(0)
        else:
            print("\n⚠️  Error rate monitoring failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error rate monitoring failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
