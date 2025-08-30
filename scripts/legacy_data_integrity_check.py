#!/usr/bin/env python3
"""
Legacy Data Integrity Check
This script performs data integrity checks on the current legacy database
to establish a baseline for future Supabase migration verification.
"""

import asyncio
import asyncpg
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class IntegrityCheckResult:
    """Result of an integrity check"""
    check_name: str
    status: str  # 'PASS', 'FAIL', 'WARNING'
    details: Dict[str, Any]
    timestamp: datetime
    error_message: Optional[str] = None

class LegacyDataIntegrityChecker:
    """Performs data integrity checks on the legacy database"""
    
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5433')),
            'database': os.getenv('DB_NAME', 'saas_factory'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres')
        }
        self.results: List[IntegrityCheckResult] = []
        
    async def connect_db(self) -> asyncpg.Connection:
        """Connect to database"""
        try:
            conn = await asyncpg.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            logger.info("Connected to database")
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def check_database_parity_baseline(self) -> IntegrityCheckResult:
        """Establish baseline for database parity (legacy system only)"""
        logger.info("Establishing database parity baseline...")
        
        try:
            conn = await self.connect_db()
            
            # Get all tables and their record counts
            tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """
            
            tables = await conn.fetch(tables_query)
            table_counts = {}
            total_records = 0
            
            for table in tables:
                table_name = table['table_name']
                try:
                    count_query = f"SELECT COUNT(*) FROM {table_name}"
                    count = await conn.fetchval(count_query)
                    table_counts[table_name] = count
                    total_records += count
                except Exception as e:
                    table_counts[table_name] = f"Error: {e}"
            
            await conn.close()
            
            return IntegrityCheckResult(
                check_name="Database Parity Baseline",
                status="PASS",
                details={
                    "total_tables": len(tables),
                    "total_records": total_records,
                    "table_counts": table_counts,
                    "note": "Baseline established for future Supabase comparison"
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return IntegrityCheckResult(
                check_name="Database Parity Baseline",
                status="FAIL",
                details={},
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    async def check_golden_queries_baseline(self) -> IntegrityCheckResult:
        """Establish baseline for golden queries (legacy system only)"""
        logger.info("Establishing golden queries baseline...")
        
        try:
            conn = await self.connect_db()
            
            # Define critical business queries
            golden_queries = [
                {
                    "name": "Active Users Count",
                    "query": "SELECT COUNT(*) FROM users WHERE status = 'active'"
                },
                {
                    "name": "Tenant User Distribution",
                    "query": "SELECT tenant_id, COUNT(*) as user_count FROM users GROUP BY tenant_id ORDER BY user_count DESC"
                },
                {
                    "name": "Recent Ideas",
                    "query": "SELECT COUNT(*) FROM ideas WHERE created_at >= NOW() - INTERVAL '7 days'"
                },
                {
                    "name": "Total Ideas by Status",
                    "query": "SELECT status, COUNT(*) FROM ideas GROUP BY status"
                },
                {
                    "name": "User Activity Summary",
                    "query": "SELECT COUNT(DISTINCT submitted_by) as active_users FROM ideas"
                }
            ]
            
            query_results = {}
            
            for query_info in golden_queries:
                try:
                    result = await conn.fetch(query_info["query"])
                    query_results[query_info["name"]] = {
                        "result": [dict(row) for row in result],
                        "record_count": len(result)
                    }
                except Exception as e:
                    query_results[query_info["name"]] = {
                        "error": str(e),
                        "record_count": 0
                    }
            
            await conn.close()
            
            return IntegrityCheckResult(
                check_name="Golden Queries Baseline",
                status="PASS",
                details={
                    "total_queries": len(golden_queries),
                    "query_results": query_results,
                    "note": "Baseline established for future Supabase comparison"
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return IntegrityCheckResult(
                check_name="Golden Queries Baseline",
                status="FAIL",
                details={},
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    async def check_referential_integrity(self) -> IntegrityCheckResult:
        """Check referential integrity in the current system"""
        logger.info("Checking referential integrity...")
        
        try:
            conn = await self.connect_db()
            
            # Get foreign key constraints
            fk_query = """
            SELECT 
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            ORDER BY tc.table_name, kcu.column_name
            """
            
            fks = await conn.fetch(fk_query)
            
            # Check for orphaned records
            orphaned_records = []
            
            for fk in fks:
                table_name = fk['table_name']
                column_name = fk['column_name']
                foreign_table = fk['foreign_table_name']
                foreign_column = fk['foreign_column_name']
                
                try:
                    # Check for orphaned records
                    orphan_query = f"""
                    SELECT COUNT(*) 
                    FROM {table_name} t1
                    LEFT JOIN {foreign_table} t2 ON t1.{column_name} = t2.{foreign_column}
                    WHERE t2.{foreign_column} IS NULL AND t1.{column_name} IS NOT NULL
                    """
                    
                    orphan_count = await conn.fetchval(orphan_query)
                    if orphan_count > 0:
                        orphaned_records.append({
                            "table": table_name,
                            "column": column_name,
                            "foreign_table": foreign_table,
                            "orphaned_count": orphan_count
                        })
                        
                except Exception as e:
                    # Skip if table doesn't exist or other error
                    pass
            
            await conn.close()
            
            if orphaned_records:
                return IntegrityCheckResult(
                    check_name="Referential Integrity",
                    status="FAIL",
                    details={
                        "foreign_key_count": len(fks),
                        "orphaned_records": orphaned_records,
                        "total_orphaned": sum(r["orphaned_count"] for r in orphaned_records)
                    },
                    timestamp=datetime.now(),
                    error_message=f"Found {len(orphaned_records)} referential integrity issues"
                )
            
            return IntegrityCheckResult(
                check_name="Referential Integrity",
                status="PASS",
                details={
                    "foreign_key_count": len(fks),
                    "orphaned_records": orphaned_records,
                    "total_orphaned": 0
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return IntegrityCheckResult(
                check_name="Referential Integrity",
                status="FAIL",
                details={},
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    async def check_data_completeness_baseline(self) -> IntegrityCheckResult:
        """Establish baseline for data completeness (legacy system only)"""
        logger.info("Establishing data completeness baseline...")
        
        try:
            conn = await self.connect_db()
            
            # Check critical data tables
            critical_tables = ['users', 'tenants', 'ideas', 'projects']
            completeness_results = {}
            
            for table in critical_tables:
                try:
                    count_query = f"SELECT COUNT(*) FROM {table}"
                    count = await conn.fetchval(count_query)
                    completeness_results[table] = {
                        "record_count": count,
                        "status": "present" if count > 0 else "empty"
                    }
                except Exception as e:
                    completeness_results[table] = {
                        "error": str(e),
                        "status": "error"
                    }
            
            # Check for any critical tables with errors
            error_tables = [
                table for table, result in completeness_results.items()
                if result.get("status") == "error"
            ]
            
            await conn.close()
            
            if error_tables:
                return IntegrityCheckResult(
                    check_name="Data Completeness Baseline",
                    status="FAIL",
                    details={
                        "completeness_results": completeness_results,
                        "error_tables": error_tables,
                        "note": "Baseline established for future Supabase comparison"
                    },
                    timestamp=datetime.now(),
                    error_message=f"Errors accessing tables: {error_tables}"
                )
            
            return IntegrityCheckResult(
                check_name="Data Completeness Baseline",
                status="PASS",
                details={
                    "completeness_results": completeness_results,
                    "total_tables": len(critical_tables),
                    "note": "Baseline established for future Supabase comparison"
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return IntegrityCheckResult(
                check_name="Data Completeness Baseline",
                status="FAIL",
                details={},
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    async def run_all_checks(self) -> List[IntegrityCheckResult]:
        """Run all integrity checks"""
        logger.info("Starting comprehensive legacy data integrity checks...")
        
        checks = [
            self.check_database_parity_baseline(),
            self.check_golden_queries_baseline(),
            self.check_referential_integrity(),
            self.check_data_completeness_baseline()
        ]
        
        results = await asyncio.gather(*checks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.results.append(IntegrityCheckResult(
                    check_name=f"Check {i+1}",
                    status="FAIL",
                    details={},
                    timestamp=datetime.now(),
                    error_message=str(result)
                ))
            else:
                self.results.append(result)
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate a comprehensive verification report"""
        report = []
        report.append("=" * 80)
        report.append("LEGACY DATA INTEGRITY VERIFICATION REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("Note: This is a baseline check for the legacy system")
        report.append("")
        
        # Summary
        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results if r.status == "PASS")
        failed_checks = sum(1 for r in self.results if r.status == "FAIL")
        
        report.append("SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Checks: {total_checks}")
        report.append(f"Passed: {passed_checks}")
        report.append(f"Failed: {failed_checks}")
        report.append(f"Success Rate: {(passed_checks/total_checks)*100:.1f}%")
        report.append("")
        
        # Detailed results
        report.append("DETAILED RESULTS")
        report.append("-" * 40)
        
        for result in self.results:
            status_icon = "✅" if result.status == "PASS" else "❌"
            report.append(f"{status_icon} {result.check_name}: {result.status}")
            
            if result.details:
                for key, value in result.details.items():
                    if isinstance(value, (int, float)):
                        report.append(f"  {key}: {value}")
                    elif isinstance(value, list):
                        report.append(f"  {key}: {len(value)} items")
                    elif isinstance(value, dict):
                        report.append(f"  {key}:")
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, (int, float)):
                                report.append(f"    {sub_key}: {sub_value}")
                            else:
                                report.append(f"    {sub_key}: {sub_value}")
                    else:
                        report.append(f"  {key}: {value}")
            
            if result.error_message:
                report.append(f"  Error: {result.error_message}")
            
            report.append("")
        
        # Next Steps
        report.append("NEXT STEPS FOR SUPABASE MIGRATION")
        report.append("-" * 40)
        report.append("1. ✅ Baseline established for legacy system")
        report.append("2. 🔄 Configure Supabase connection")
        report.append("3. 🔄 Run full data integrity verification")
        report.append("4. 🔄 Compare results between legacy and Supabase")
        report.append("5. 🔄 Address any drift or integrity issues")
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)

async def main():
    """Main function"""
    logger.info("Starting Legacy Data Integrity Verification...")
    
    checker = LegacyDataIntegrityChecker()
    
    try:
        results = await checker.run_all_checks()
        report = checker.generate_report()
        
        print(report)
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"legacy_data_integrity_report_{timestamp}.txt"
        
        with open(report_filename, 'w') as f:
            f.write(report)
        
        logger.info(f"Report saved to {report_filename}")
        
        # Return exit code based on results
        failed_checks = sum(1 for r in results if r.status == "FAIL")
        if failed_checks > 0:
            logger.error(f"Verification failed with {failed_checks} failed checks")
            sys.exit(1)
        else:
            logger.info("All baseline checks completed successfully!")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Verification failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
