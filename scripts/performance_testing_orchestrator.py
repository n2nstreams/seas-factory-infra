#!/usr/bin/env python3
"""
Performance Testing Orchestrator
This script orchestrates all performance testing activities and generates a unified performance report.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
import subprocess
import time

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")

class PerformanceTestingOrchestrator:
    """Orchestrates all performance testing activities"""
    
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'overall_score': 0,
            'tests_completed': [],
            'performance_baseline': {},
            'load_testing': {},
            'error_rate_monitoring': {},
            'response_time_validation': {},
            'recommendations': []
        }
        
        self.test_scripts = {
            'performance_baseline': 'scripts/performance_baseline_establishment.py',
            'load_testing': 'scripts/load_testing_infrastructure.py',
            'error_rate_monitoring': 'scripts/error_rate_monitoring.py'
        }
    
    async def run_performance_baseline(self) -> bool:
        """Run performance baseline establishment"""
        print("\n🔍 STEP 1: ESTABLISHING PERFORMANCE BASELINE")
        print("=" * 60)
        
        try:
            # Check if script exists
            if not os.path.exists(self.test_scripts['performance_baseline']):
                print(f"❌ Script not found: {self.test_scripts['performance_baseline']}")
                return False
            
            # Run performance baseline script
            print("   Running performance baseline establishment...")
            result = subprocess.run([
                'python', self.test_scripts['performance_baseline']
            ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            if result.returncode == 0:
                print("   ✅ Performance baseline established successfully")
                
                # Try to find and load the results
                baseline_files = [f for f in os.listdir('.') if f.startswith('performance_baseline_') and f.endswith('.json')]
                if baseline_files:
                    latest_baseline = max(baseline_files, key=os.path.getctime)
                    try:
                        with open(latest_baseline, 'r') as f:
                            baseline_data = json.load(f)
                        self.test_results['performance_baseline'] = baseline_data
                        print(f"   📁 Baseline results loaded from: {latest_baseline}")
                    except Exception as e:
                        print(f"   ⚠️  Could not load baseline results: {e}")
                
                return True
            else:
                print(f"   ❌ Performance baseline failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("   ❌ Performance baseline timed out")
            return False
        except Exception as e:
            print(f"   ❌ Performance baseline error: {e}")
            return False
    
    async def run_load_testing(self) -> bool:
        """Run load testing infrastructure"""
        print("\n🔍 STEP 2: LOAD TESTING INFRASTRUCTURE")
        print("=" * 60)
        
        try:
            # Check if script exists
            if not os.path.exists(self.test_scripts['load_testing']):
                print(f"❌ Script not found: {self.test_scripts['load_testing']}")
                return False
            
            # Check if API is available
            api_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
            print(f"   Testing API availability at: {api_url}")
            
            # Simple availability check
            import aiohttp
            try:
                timeout = aiohttp.ClientTimeout(total=5)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(f"{api_url}/health") as response:
                        if response.status < 400:
                            print("   ✅ API is available, proceeding with load testing")
                        else:
                            print(f"   ⚠️  API returned status {response.status}")
            except Exception as e:
                print(f"   ⚠️  API availability check failed: {e}")
                print("   🔧 Load testing will attempt to run anyway")
            
            # Run load testing script
            print("   Running load testing...")
            result = subprocess.run([
                'python', self.test_scripts['load_testing']
            ], capture_output=True, text=True, timeout=600)  # 10 minute timeout
            
            if result.returncode == 0:
                print("   ✅ Load testing completed successfully")
                
                # Try to find and load the results
                load_test_files = [f for f in os.listdir('.') if f.startswith('load_test_report_') and f.endswith('.json')]
                if load_test_files:
                    latest_load_test = max(load_test_files, key=os.path.getctime)
                    try:
                        with open(latest_load_test, 'r') as f:
                            load_test_data = json.load(f)
                        self.test_results['load_testing'] = load_test_data
                        print(f"   📁 Load test results loaded from: {latest_load_test}")
                    except Exception as e:
                        print(f"   ⚠️  Could not load load test results: {e}")
                
                return True
            else:
                print(f"   ❌ Load testing failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("   ❌ Load testing timed out")
            return False
        except Exception as e:
            print(f"   ❌ Load testing error: {e}")
            return False
    
    async def run_error_rate_monitoring(self) -> bool:
        """Run error rate monitoring"""
        print("\n🔍 STEP 3: ERROR RATE MONITORING")
        print("=" * 60)
        
        try:
            # Check if script exists
            if not os.path.exists(self.test_scripts['error_rate_monitoring']):
                print(f"❌ Script not found: {self.test_scripts['error_rate_monitoring']}")
                return False
            
            # Run error rate monitoring script
            print("   Running error rate monitoring...")
            print("   ⏱️  This will take 10 minutes to complete...")
            
            result = subprocess.run([
                'python', self.test_scripts['error_rate_monitoring']
            ], capture_output=True, text=True, timeout=900)  # 15 minute timeout
            
            if result.returncode == 0:
                print("   ✅ Error rate monitoring completed successfully")
                
                # Try to find and load the results
                monitoring_files = [f for f in os.listdir('.') if f.startswith('error_rate_monitoring_') and f.endswith('.json')]
                if monitoring_files:
                    latest_monitoring = max(monitoring_files, key=os.path.getctime)
                    try:
                        with open(latest_monitoring, 'r') as f:
                            monitoring_data = json.load(f)
                        self.test_results['error_rate_monitoring'] = monitoring_data
                        print(f"   📁 Monitoring results loaded from: {latest_monitoring}")
                    except Exception as e:
                        print(f"   ⚠️  Could not load monitoring results: {e}")
                
                return True
            else:
                print(f"   ❌ Error rate monitoring failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("   ❌ Error rate monitoring timed out")
            return False
        except Exception as e:
            print(f"   ❌ Error rate monitoring error: {e}")
            return False
    
    def validate_response_times(self) -> Dict[str, Any]:
        """Validate response times against thresholds"""
        print("\n🔍 STEP 4: RESPONSE TIME VALIDATION")
        print("=" * 60)
        
        validation_results = {
            'overall_status': 'PASS',
            'baseline_validation': 'PASS',
            'load_test_validation': 'PASS',
            'monitoring_validation': 'PASS',
            'thresholds': {
                'baseline_response_time_ms': 100,  # 100ms baseline
                'load_test_p95_ms': 500,  # 500ms P95 under load
                'monitoring_avg_ms': 200,  # 200ms average during monitoring
                'error_rate_threshold': 5.0  # 5% error rate
            },
            'violations': []
        }
        
        # Validate performance baseline
        if self.test_results['performance_baseline']:
            baseline = self.test_results['performance_baseline']
            if 'database_performance' in baseline:
                db_perf = baseline['database_performance']
                if 'connection_time_ms' in db_perf:
                    if db_perf['connection_time_ms'] > validation_results['thresholds']['baseline_response_time_ms']:
                        validation_results['baseline_validation'] = 'FAIL'
                        validation_results['violations'].append({
                            'test': 'Performance Baseline',
                            'metric': 'Connection Time',
                            'value': db_perf['connection_time_ms'],
                            'threshold': validation_results['thresholds']['baseline_response_time_ms']
                        })
        
        # Validate load testing
        if self.test_results['load_testing']:
            load_test = self.test_results['load_testing']
            if 'response_time_metrics' in load_test:
                rtm = load_test['response_time_metrics']
                if 'p95_ms' in rtm:
                    if rtm['p95_ms'] > validation_results['thresholds']['load_test_p95_ms']:
                        validation_results['load_test_validation'] = 'FAIL'
                        validation_results['violations'].append({
                            'test': 'Load Testing',
                            'metric': 'P95 Response Time',
                            'value': rtm['p95_ms'],
                            'threshold': validation_results['thresholds']['load_test_p95_ms']
                        })
        
        # Validate error rate monitoring
        if self.test_results['error_rate_monitoring']:
            monitoring = self.test_results['error_rate_monitoring']
            if 'error_rate_percentage' in monitoring:
                if monitoring['error_rate_percentage'] > validation_results['thresholds']['error_rate_threshold']:
                    validation_results['monitoring_validation'] = 'FAIL'
                    validation_results['violations'].append({
                        'test': 'Error Rate Monitoring',
                        'metric': 'Error Rate',
                        'value': monitoring['error_rate_percentage'],
                        'threshold': validation_results['thresholds']['error_rate_threshold']
                    })
        
        # Overall status
        if any(status == 'FAIL' for status in [
            validation_results['baseline_validation'],
            validation_results['load_test_validation'],
            validation_results['monitoring_validation']
        ]):
            validation_results['overall_status'] = 'FAIL'
        
        # Print validation results
        print(f"   Baseline Validation: {validation_results['baseline_validation']}")
        print(f"   Load Test Validation: {validation_results['load_test_validation']}")
        print(f"   Monitoring Validation: {validation_results['monitoring_validation']}")
        print(f"   Overall Status: {validation_results['overall_status']}")
        
        if validation_results['violations']:
            print(f"\n   ⚠️  Threshold Violations:")
            for violation in validation_results['violations']:
                print(f"      {violation['test']}: {violation['metric']} = {violation['value']} (threshold: {violation['threshold']})")
        
        self.test_results['response_time_validation'] = validation_results
        return validation_results
    
    def calculate_overall_score(self) -> float:
        """Calculate overall performance score"""
        print("\n🔍 STEP 5: CALCULATING OVERALL PERFORMANCE SCORE")
        print("=" * 60)
        
        scores = []
        weights = []
        
        # Performance baseline score
        if self.test_results['performance_baseline']:
            baseline = self.test_results['performance_baseline']
            if 'overall_metrics' in baseline:
                baseline_score = baseline['overall_metrics'].get('overall_performance_score', 0)
                scores.append(baseline_score)
                weights.append(0.3)  # 30% weight
                print(f"   Performance Baseline: {baseline_score}/100 (30% weight)")
        
        # Load testing score
        if self.test_results['load_testing']:
            load_test = self.test_results['load_testing']
            if 'performance_score' in load_test:
                load_test_score = load_test['performance_score']
                scores.append(load_test_score)
                weights.append(0.3)  # 30% weight
                print(f"   Load Testing: {load_test_score}/100 (30% weight)")
        
        # Error rate monitoring score
        if self.test_results['error_rate_monitoring']:
            monitoring = self.test_results['error_rate_monitoring']
            if 'error_rate_percentage' in monitoring:
                error_rate = monitoring['error_rate_percentage']
                # Convert error rate to score (lower error rate = higher score)
                monitoring_score = max(0, 100 - (error_rate * 10))
                scores.append(monitoring_score)
                weights.append(0.2)  # 20% weight
                print(f"   Error Rate Monitoring: {monitoring_score}/100 (20% weight)")
        
        # Response time validation score
        if self.test_results['response_time_validation']:
            validation = self.test_results['response_time_validation']
            if validation['overall_status'] == 'PASS':
                validation_score = 100
            else:
                # Penalize based on number of violations
                violation_count = len(validation['violations'])
                validation_score = max(0, 100 - (violation_count * 20))
            
            scores.append(validation_score)
            weights.append(0.2)  # 20% weight
            print(f"   Response Time Validation: {validation_score}/100 (20% weight)")
        
        # Calculate weighted average
        if scores and weights and len(scores) == len(weights):
            total_weight = sum(weights)
            weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
            overall_score = weighted_sum / total_weight
        else:
            overall_score = 0
        
        self.test_results['overall_score'] = round(overall_score, 1)
        print(f"\n   Overall Performance Score: {self.test_results['overall_score']}/100")
        
        return self.test_results['overall_score']
    
    def generate_recommendations(self):
        """Generate performance improvement recommendations"""
        print("\n🔍 STEP 6: GENERATING RECOMMENDATIONS")
        print("=" * 60)
        
        recommendations = []
        
        # Check performance baseline
        if self.test_results['performance_baseline']:
            baseline = self.test_results['performance_baseline']
            if 'overall_metrics' in baseline:
                baseline_score = baseline['overall_metrics'].get('overall_performance_score', 0)
                if baseline_score < 80:
                    recommendations.append({
                        'priority': 'HIGH',
                        'category': 'Database Performance',
                        'recommendation': 'Optimize database queries and connection pooling',
                        'details': f'Current baseline score: {baseline_score}/100'
                    })
        
        # Check load testing
        if self.test_results['load_testing']:
            load_test = self.test_results['load_testing']
            if 'performance_score' in load_test:
                load_test_score = load_test['performance_score']
                if load_test_score < 80:
                    recommendations.append({
                        'priority': 'HIGH',
                        'category': 'Load Handling',
                        'recommendation': 'Improve system scalability and load distribution',
                        'details': f'Current load test score: {load_test_score}/100'
                    })
        
        # Check error rate monitoring
        if self.test_results['error_rate_monitoring']:
            monitoring = self.test_results['error_rate_monitoring']
            if 'error_rate_percentage' in monitoring:
                error_rate = monitoring['error_rate_percentage']
                if error_rate > 2.0:
                    recommendations.append({
                        'priority': 'CRITICAL',
                        'category': 'System Reliability',
                        'recommendation': 'Investigate and fix high error rates',
                        'details': f'Current error rate: {error_rate:.2f}%'
                    })
        
        # Check response time validation
        if self.test_results['response_time_validation']:
            validation = self.test_results['response_time_validation']
            if validation['overall_status'] == 'FAIL':
                recommendations.append({
                    'priority': 'HIGH',
                    'category': 'Response Time',
                    'recommendation': 'Address response time threshold violations',
                    'details': f'Violations found: {len(validation["violations"])}'
                })
        
        # Add general recommendations based on overall score
        if self.test_results['overall_score'] < 70:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'Overall Performance',
                'recommendation': 'Comprehensive performance review required',
                'details': f'Overall score: {self.test_results['overall_score']}/100'
            })
        elif self.test_results['overall_score'] < 85:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Performance Optimization',
                'recommendation': 'Targeted performance improvements recommended',
                'details': f'Overall score: {self.test_results['overall_score']}/100'
            })
        else:
            recommendations.append({
                'priority': 'LOW',
                'category': 'Maintenance',
                'recommendation': 'Performance is good, maintain current standards',
                'details': f'Overall score: {self.test_results['overall_score']}/100'
            })
        
        self.test_results['recommendations'] = recommendations
        
        # Print recommendations
        if recommendations:
            print(f"   Generated {len(recommendations)} recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. [{rec['priority']}] {rec['category']}: {rec['recommendation']}")
        else:
            print("   ✅ No specific recommendations at this time")
    
    def save_comprehensive_report(self):
        """Save comprehensive performance testing report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON report
        json_filename = f"comprehensive_performance_report_{timestamp}.json"
        with open(json_filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        # Save human-readable summary
        summary_filename = f"comprehensive_performance_summary_{timestamp}.txt"
        with open(summary_filename, 'w') as f:
            f.write(self._generate_summary())
        
        print(f"\n📁 Comprehensive report saved to: {json_filename}")
        print(f"📁 Performance summary saved to: {summary_filename}")
    
    def _generate_summary(self) -> str:
        """Generate human-readable performance summary"""
        summary = []
        summary.append("COMPREHENSIVE PERFORMANCE TESTING SUMMARY")
        summary.append("=" * 60)
        summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")
        
        # Overall Results
        summary.append("OVERALL RESULTS:")
        summary.append(f"  Overall Performance Score: {self.test_results['overall_score']}/100")
        summary.append(f"  Tests Completed: {len(self.test_results['tests_completed'])}")
        summary.append("")
        
        # Test Results Summary
        summary.append("TEST RESULTS SUMMARY:")
        
        if self.test_results['performance_baseline']:
            summary.append("  ✅ Performance Baseline: Completed")
            baseline = self.test_results['performance_baseline']
            if 'overall_metrics' in baseline:
                overall = baseline['overall_metrics']
                summary.append(f"    Score: {overall.get('overall_performance_score', 'N/A')}/100")
                summary.append(f"    Grade: {overall.get('performance_grade', 'N/A')}")
        
        if self.test_results['load_testing']:
            summary.append("  ✅ Load Testing: Completed")
            load_test = self.test_results['load_testing']
            if 'performance_score' in load_test:
                summary.append(f"    Score: {load_test['performance_score']}/100")
                summary.append(f"    Grade: {load_test.get('load_test_grade', 'N/A')}")
        
        if self.test_results['error_rate_monitoring']:
            summary.append("  ✅ Error Rate Monitoring: Completed")
            monitoring = self.test_results['error_rate_monitoring']
            if 'error_rate_percentage' in monitoring:
                summary.append(f"    Error Rate: {monitoring['error_rate_percentage']:.2f}%")
        
        if self.test_results['response_time_validation']:
            summary.append("  ✅ Response Time Validation: Completed")
            validation = self.test_results['response_time_validation']
            summary.append(f"    Status: {validation['overall_status']}")
        
        # Recommendations
        if self.test_results['recommendations']:
            summary.append("\nRECOMMENDATIONS:")
            for i, rec in enumerate(self.test_results['recommendations'], 1):
                summary.append(f"  {i}. [{rec['priority']}] {rec['category']}")
                summary.append(f"     {rec['recommendation']}")
                summary.append(f"     Details: {rec['details']}")
                summary.append("")
        
        return "\n".join(summary)
    
    async def run_complete_performance_testing(self) -> bool:
        """Run complete performance testing suite"""
        print("🚀 COMPREHENSIVE PERFORMANCE TESTING SUITE")
        print("=" * 80)
        print(f"Starting: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        start_time = time.time()
        
        try:
            # Step 1: Performance Baseline
            baseline_success = await self.run_performance_baseline()
            if baseline_success:
                self.test_results['tests_completed'].append('performance_baseline')
            
            # Step 2: Load Testing
            load_test_success = await self.run_load_testing()
            if load_test_success:
                self.test_results['tests_completed'].append('load_testing')
            
            # Step 3: Error Rate Monitoring
            monitoring_success = await self.run_error_rate_monitoring()
            if monitoring_success:
                self.test_results['tests_completed'].append('error_rate_monitoring')
            
            # Step 4: Response Time Validation
            self.validate_response_times()
            
            # Step 5: Calculate Overall Score
            self.calculate_overall_score()
            
            # Step 6: Generate Recommendations
            self.generate_recommendations()
            
            # Save comprehensive report
            self.save_comprehensive_report()
            
            total_time = time.time() - start_time
            
            print("\n" + "=" * 80)
            print("🎉 COMPREHENSIVE PERFORMANCE TESTING COMPLETED")
            print("=" * 80)
            print(f"Total Time: {total_time:.1f} seconds")
            print(f"Tests Completed: {len(self.test_results['tests_completed'])}")
            print(f"Overall Score: {self.test_results['overall_score']}/100")
            print("=" * 80)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Performance testing failed: {e}")
            return False

async def main():
    """Main function"""
    orchestrator = PerformanceTestingOrchestrator()
    
    try:
        success = await orchestrator.run_complete_performance_testing()
        
        if success:
            print("\n🎉 Performance testing suite completed successfully!")
            print("📊 Review the generated reports for detailed analysis")
            sys.exit(0)
        else:
            print("\n⚠️  Performance testing suite failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Performance testing orchestrator failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
