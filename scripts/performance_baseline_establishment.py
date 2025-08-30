#!/usr/bin/env python3
"""
Performance Baseline Establishment
This script establishes performance baselines for the legacy system to compare against the new system.
"""

import asyncio
import asyncpg
import time
import statistics
import json
from datetime import datetime
from typing import Dict, List, Any
import os
import sys

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")

class PerformanceBaseline:
    """Establishes performance baselines for the legacy system"""
    
    def __init__(self):
        # Legacy database configuration
        self.legacy_db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5433')),
            'database': os.getenv('DB_NAME', 'saas_factory'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres')
        }
        
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'database_performance': {},
            'query_performance': {},
            'connection_performance': {},
            'overall_metrics': {}
        }
    
    async def connect_to_legacy_db(self) -> asyncpg.Connection:
        """Connect to legacy database"""
        try:
            conn = await asyncpg.connect(
                host=self.legacy_db_config['host'],
                port=self.legacy_db_config['port'],
                database=self.legacy_db_config['database'],
                user=self.legacy_db_config['user'],
                password=self.legacy_db_config['password']
            )
            print("✅ Connected to legacy database")
            return conn
        except Exception as e:
            print(f"❌ Failed to connect to legacy database: {e}")
            raise
    
    async def test_database_performance(self, conn: asyncpg.Connection):
        """Test basic database performance metrics"""
        print("\n🔍 Testing Database Performance...")
        
        # Test connection speed
        start_time = time.time()
        await conn.fetchval("SELECT 1")
        connection_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Test basic query performance
        start_time = time.time()
        await conn.fetchval("SELECT COUNT(*) FROM users")
        count_query_time = (time.time() - start_time) * 1000
        
        # Test table scan performance
        start_time = time.time()
        await conn.fetch("SELECT * FROM users LIMIT 10")
        scan_query_time = (time.time() - start_time) * 1000
        
        self.results['database_performance'] = {
            'connection_time_ms': round(connection_time, 2),
            'count_query_time_ms': round(count_query_time, 2),
            'scan_query_time_ms': round(scan_query_time, 2),
            'database_version': await conn.fetchval("SELECT version()")
        }
        
        print(f"   Connection Time: {connection_time:.2f}ms")
        print(f"   Count Query Time: {count_query_time:.2f}ms")
        print(f"   Scan Query Time: {scan_query_time:.2f}ms")
    
    async def test_critical_queries(self, conn: asyncpg.Connection):
        """Test performance of critical business queries"""
        print("\n🔍 Testing Critical Query Performance...")
        
        critical_queries = {
            'active_users_count': "SELECT COUNT(*) FROM users WHERE status = 'active'",
            'tenant_user_distribution': "SELECT tenant_id, COUNT(*) FROM users GROUP BY tenant_id",
            'recent_ideas': "SELECT * FROM ideas ORDER BY created_at DESC LIMIT 10",
            'user_authentication': "SELECT * FROM users WHERE email = $1 AND password_hash = $2",
            'tenant_settings': "SELECT * FROM tenants WHERE id = $1"
        }
        
        query_times = {}
        
        for query_name, query_sql in critical_queries.items():
            try:
                # Test query performance multiple times for accuracy
                times = []
                for _ in range(5):
                    start_time = time.time()
                    if '$' in query_sql:
                        # Use dummy parameters for parameterized queries
                        if 'email' in query_sql:
                            await conn.fetchval(query_sql, 'test@example.com', 'dummy_hash')
                        else:
                            await conn.fetchval(query_sql, 1)
                    else:
                        await conn.fetch(query_sql)
                    times.append((time.time() - start_time) * 1000)
                
                avg_time = statistics.mean(times)
                min_time = min(times)
                max_time = max(times)
                
                query_times[query_name] = {
                    'avg_time_ms': round(avg_time, 2),
                    'min_time_ms': round(min_time, 2),
                    'max_time_ms': round(max_time, 2),
                    'std_dev_ms': round(statistics.stdev(times), 2) if len(times) > 1 else 0
                }
                
                print(f"   {query_name}: {avg_time:.2f}ms avg ({min_time:.2f}ms - {max_time:.2f}ms)")
                
            except Exception as e:
                print(f"   ❌ {query_name}: Error - {e}")
                query_times[query_name] = {'error': str(e)}
        
        self.results['query_performance'] = query_times
    
    async def test_connection_scaling(self, conn: asyncpg.Connection):
        """Test connection scaling and concurrency"""
        print("\n🔍 Testing Connection Scaling...")
        
        # Test multiple concurrent connections
        connection_times = []
        max_connections = 10
        
        for i in range(max_connections):
            start_time = time.time()
            try:
                test_conn = await asyncpg.connect(
                    host=self.legacy_db_config['host'],
                    port=self.legacy_db_config['port'],
                    database=self.legacy_db_config['database'],
                    user=self.legacy_db_config['user'],
                    password=self.legacy_db_config['password']
                )
                connection_time = (time.time() - start_time) * 1000
                connection_times.append(connection_time)
                
                # Test a simple query
                await test_conn.fetchval("SELECT 1")
                await test_conn.close()
                
                print(f"   Connection {i+1}: {connection_time:.2f}ms")
                
            except Exception as e:
                print(f"   ❌ Connection {i+1}: Failed - {e}")
                break
        
        if connection_times:
            self.results['connection_performance'] = {
                'max_concurrent_connections': len(connection_times),
                'avg_connection_time_ms': round(statistics.mean(connection_times), 2),
                'min_connection_time_ms': round(min(connection_times), 2),
                'max_connection_time_ms': round(max(connection_times), 2),
                'connection_success_rate': len(connection_times) / max_connections * 100
            }
    
    async def calculate_overall_metrics(self):
        """Calculate overall performance metrics"""
        print("\n🔍 Calculating Overall Metrics...")
        
        # Calculate database performance score
        db_perf = self.results['database_performance']
        if 'connection_time_ms' in db_perf:
            db_score = max(0, 100 - (db_perf['connection_time_ms'] * 2))  # Lower time = higher score
        else:
            db_score = 0
        
        # Calculate query performance score
        query_perf = self.results['query_performance']
        if query_perf:
            valid_queries = [q for q in query_perf.values() if 'avg_time_ms' in q]
            if valid_queries:
                avg_query_time = statistics.mean([q['avg_time_ms'] for q in valid_queries])
                query_score = max(0, 100 - (avg_query_time * 5))  # Lower time = higher score
            else:
                query_score = 0
        else:
            query_score = 0
        
        # Calculate connection performance score
        conn_perf = self.results['connection_performance']
        if 'connection_success_rate' in conn_perf:
            conn_score = conn_perf['connection_success_rate']
        else:
            conn_score = 0
        
        # Overall score (weighted average)
        overall_score = (db_score * 0.3 + query_score * 0.4 + conn_score * 0.3)
        
        self.results['overall_metrics'] = {
            'database_performance_score': round(db_score, 1),
            'query_performance_score': round(query_score, 1),
            'connection_performance_score': round(conn_score, 1),
            'overall_performance_score': round(overall_score, 1),
            'performance_grade': self._get_performance_grade(overall_score)
        }
        
        print(f"   Database Performance: {db_score:.1f}/100")
        print(f"   Query Performance: {query_score:.1f}/100")
        print(f"   Connection Performance: {conn_score:.1f}/100")
        print(f"   Overall Score: {overall_score:.1f}/100 ({self._get_performance_grade(overall_score)})")
    
    def _get_performance_grade(self, score: float) -> str:
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
    
    async def run_performance_baseline(self):
        """Run complete performance baseline establishment"""
        print("🚀 PERFORMANCE BASELINE ESTABLISHMENT")
        print("=" * 60)
        print(f"Target: Legacy System Performance Baseline")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        try:
            # Connect to database
            conn = await self.connect_to_legacy_db()
            
            # Run performance tests
            await self.test_database_performance(conn)
            await self.test_critical_queries(conn)
            await self.test_connection_scaling(conn)
            
            # Calculate overall metrics
            await self.calculate_overall_metrics()
            
            # Close connection
            await conn.close()
            
            # Save results
            self._save_results()
            
            print("\n" + "=" * 60)
            print("✅ PERFORMANCE BASELINE ESTABLISHMENT COMPLETE")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Performance baseline establishment failed: {e}")
            return False
    
    def _save_results(self):
        """Save performance baseline results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_baseline_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📁 Performance baseline saved to: {filename}")
        
        # Also save a human-readable summary
        summary_filename = f"performance_baseline_summary_{timestamp}.txt"
        with open(summary_filename, 'w') as f:
            f.write(self._generate_summary())
        
        print(f"📁 Performance summary saved to: {summary_filename}")
    
    def _generate_summary(self) -> str:
        """Generate human-readable performance summary"""
        summary = []
        summary.append("PERFORMANCE BASELINE SUMMARY")
        summary.append("=" * 50)
        summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")
        
        # Database Performance
        summary.append("DATABASE PERFORMANCE:")
        db_perf = self.results['database_performance']
        for key, value in db_perf.items():
            if key == 'database_version':
                summary.append(f"  {key}: {value}")
            else:
                summary.append(f"  {key}: {value}ms")
        
        # Query Performance
        summary.append("\nQUERY PERFORMANCE:")
        query_perf = self.results['query_performance']
        for query_name, metrics in query_perf.items():
            if 'avg_time_ms' in metrics:
                summary.append(f"  {query_name}: {metrics['avg_time_ms']}ms avg")
            else:
                summary.append(f"  {query_name}: Error - {metrics.get('error', 'Unknown')}")
        
        # Connection Performance
        summary.append("\nCONNECTION PERFORMANCE:")
        conn_perf = self.results['connection_performance']
        for key, value in conn_perf.items():
            if 'rate' in key:
                summary.append(f"  {key}: {value:.1f}%")
            else:
                summary.append(f"  {key}: {value}")
        
        # Overall Metrics
        summary.append("\nOVERALL METRICS:")
        overall = self.results['overall_metrics']
        for key, value in overall.items():
            summary.append(f"  {key}: {value}")
        
        return "\n".join(summary)

async def main():
    """Main function"""
    baseline = PerformanceBaseline()
    success = await baseline.run_performance_baseline()
    
    if success:
        print("\n🎉 Performance baseline establishment completed successfully!")
        print("📊 Use these baselines to compare against new system performance")
        sys.exit(0)
    else:
        print("\n⚠️  Performance baseline establishment failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
