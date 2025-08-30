#!/usr/bin/env python3
"""
Data Integrity & Consistency Verification Script
This script systematically verifies data integrity between legacy and Supabase systems
as part of the pre-decommissioning checklist.
"""

import asyncio
import asyncpg
import os
import sys
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
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
class VerificationResult:
    """Result of a verification check"""
    check_name: str
    status: str  # 'PASS', 'FAIL', 'WARNING'
    details: Dict[str, Any]
    timestamp: datetime
    error_message: Optional[str] = None

class DataIntegrityVerifier:
    """Verifies data integrity between legacy and Supabase systems"""
    
    def __init__(self):
        # Legacy database configuration (current system) - using docker-compose settings
        self.legacy_db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5433')),  # Docker maps to 5433
            'database': os.getenv('DB_NAME', 'saas_factory'),  # Matches docker-compose
            'user': os.getenv('DB_USER', 'postgres'),  # Matches docker-compose
            'password': os.getenv('DB_PASSWORD', 'postgres')  # Matches docker-compose
        }
        
        # Supabase configuration (target system)
        self.supabase_config = {
            'host': os.getenv('SUPABASE_DB_HOST'),
            'port': int(os.getenv('SUPABASE_DB_PORT', '5432')),
            'database': os.getenv('SUPABASE_DB_NAME'),
            'user': os.getenv('SUPABASE_DB_USER'),
            'password': os.getenv('SUPABASE_DB_PASSWORD'),
            'url': os.getenv('SUPABASE_URL'),
            'anon_key': os.getenv('SUPABASE_ANON_KEY')
        }
        
        self.results: List[VerificationResult] = []
        
    async def connect_legacy_db(self) -> asyncpg.Connection:
        """Connect to legacy database"""
        try:
            conn = await asyncpg.connect(
                host=self.legacy_db_config['host'],
                port=self.legacy_db_config['port'],
                database=self.legacy_db_config['database'],
                user=self.legacy_db_config['user'],
                password=self.legacy_db_config['password']
            )
            logger.info("Connected to legacy database")
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to legacy database: {e}")
            raise
    
    async def connect_supabase_db(self) -> asyncpg.Connection:
        """Connect to Supabase database"""
        if not all([self.supabase_config['host'], self.supabase_config['database'], 
                   self.supabase_config['user'], self.supabase_config['password']]):
            raise ValueError("Supabase database configuration incomplete")
        
        try:
            conn = await asyncpg.connect(
                host=self.supabase_config['host'],
                port=self.supabase_config['port'],
                database=self.supabase_config['database'],
                user=self.supabase_config['user'],
                password=self.supabase_config['password']
            )
            logger.info("Connected to Supabase database")
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to Supabase database: {e}")
            raise
    
    async def verify_database_parity(self) -> VerificationResult:
        """Verify database parity with <0.05% drift"""
        logger.info("Starting database parity verification...")
        
        try:
            legacy_conn = await self.connect_legacy_db()
            supabase_conn = await self.connect_supabase_db()
            
            # Get table list from both databases
            legacy_tables = await self.get_table_list(legacy_conn)
            supabase_tables = await self.get_table_list(supabase_conn)
            
            # Check table coverage
            missing_tables = set(legacy_tables) - set(supabase_tables)
            extra_tables = set(supabase_tables) - set(legacy_tables)
            
            if missing_tables or extra_tables:
                return VerificationResult(
                    check_name="Database Parity - Table Coverage",
                    status="FAIL",
                    details={
                        "missing_tables": list(missing_tables),
                        "extra_tables": list(extra_tables),
                        "legacy_table_count": len(legacy_tables),
                        "supabase_table_count": len(supabase_tables)
                    },
                    timestamp=datetime.now(),
                    error_message="Table coverage mismatch detected"
                )
            
            # Check record counts for each table
            drift_results = {}
            total_drift = 0
            total_records = 0
            
            for table in legacy_tables:
                legacy_count = await self.get_table_record_count(legacy_conn, table)
                supabase_count = await self.get_table_record_count(supabase_conn, table)
                
                if legacy_count > 0:
                    drift = abs(legacy_count - supabase_count) / legacy_count
                    drift_results[table] = {
                        "legacy_count": legacy_count,
                        "supabase_count": supabase_count,
                        "drift_percentage": drift * 100
                    }
                    total_drift += abs(legacy_count - supabase_count)
                    total_records += legacy_count
            
            overall_drift = total_drift / total_records if total_records > 0 else 0
            
            if overall_drift > 0.0005:  # 0.05%
                return VerificationResult(
                    check_name="Database Parity - Record Count Drift",
                    status="FAIL",
                    details={
                        "overall_drift_percentage": overall_drift * 100,
                        "threshold": 0.05,
                        "table_drifts": drift_results,
                        "total_records": total_records,
                        "total_drift": total_drift
                    },
                    timestamp=datetime.now(),
                    error_message=f"Drift {overall_drift*100:.4f}% exceeds threshold of 0.05%"
                )
            
            await legacy_conn.close()
            await supabase_conn.close()
            
            return VerificationResult(
                check_name="Database Parity - Record Count Drift",
                status="PASS",
                details={
                    "overall_drift_percentage": overall_drift * 100,
                    "threshold": 0.05,
                    "table_drifts": drift_results,
                    "total_records": total_records,
                    "total_drift": total_drift
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return VerificationResult(
                check_name="Database Parity",
                status="FAIL",
                details={},
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    async def verify_golden_queries(self) -> VerificationResult:
        """Verify that critical business queries return identical results"""
        logger.info("Starting golden query validation...")
        
        try:
            legacy_conn = await self.connect_legacy_db()
            supabase_conn = await self.connect_supabase_db()
            
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
                }
            ]
            
            query_results = {}
            all_queries_match = True
            
            for query_info in golden_queries:
                try:
                    legacy_result = await legacy_conn.fetch(query_info["query"])
                    supabase_result = await supabase_conn.fetch(query_info["query"])
                    
                    # Compare results
                    legacy_data = [dict(row) for row in legacy_result]
                    supabase_data = [dict(row) for row in supabase_result]
                    
                    match = legacy_data == supabase_data
                    query_results[query_info["name"]] = {
                        "match": match,
                        "legacy_result": legacy_data,
                        "supabase_result": supabase_data
                    }
                    
                    if not match:
                        all_queries_match = False
                        
                except Exception as e:
                    query_results[query_info["name"]] = {
                        "match": False,
                        "error": str(e)
                    }
                    all_queries_match = False
            
            await legacy_conn.close()
            await supabase_conn.close()
            
            if not all_queries_match:
                return VerificationResult(
                    check_name="Golden Query Validation",
                    status="FAIL",
                    details={
                        "query_results": query_results,
                        "total_queries": len(golden_queries),
                        "matching_queries": sum(1 for r in query_results.values() if r.get("match", False))
                    },
                    timestamp=datetime.now(),
                    error_message="Some golden queries returned different results"
                )
            
            return VerificationResult(
                check_name="Golden Query Validation",
                status="PASS",
                details={
                    "query_results": query_results,
                    "total_queries": len(golden_queries),
                    "matching_queries": len(golden_queries)
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return VerificationResult(
                check_name="Golden Query Validation",
                status="FAIL",
                details={},
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    async def verify_referential_integrity(self) -> VerificationResult:
        """Confirm all foreign key relationships are intact"""
        logger.info("Starting referential integrity verification...")
        
        try:
            legacy_conn = await self.connect_legacy_db()
            supabase_conn = await self.connect_supabase_db()
            
            # Get foreign key constraints from both databases
            legacy_fks = await self.get_foreign_key_constraints(legacy_conn)
            supabase_fks = await self.get_foreign_key_constraints(supabase_conn)
            
            # Check for missing foreign keys
            missing_fks = []
            for fk in legacy_fks:
                if not any(self._fk_matches(fk, supabase_fk) for supabase_fk in supabase_fks):
                    missing_fks.append(fk)
            
            # Check for orphaned records
            orphaned_records = await self.check_orphaned_records(legacy_conn, supabase_conn)
            
            await legacy_conn.close()
            await supabase_conn.close()
            
            if missing_fks or orphaned_records:
                return VerificationResult(
                    check_name="Referential Integrity",
                    status="FAIL",
                    details={
                        "missing_foreign_keys": missing_fks,
                        "orphaned_records": orphaned_records,
                        "legacy_fk_count": len(legacy_fks),
                        "supabase_fk_count": len(supabase_fks)
                    },
                    timestamp=datetime.now(),
                    error_message="Referential integrity issues detected"
                )
            
            return VerificationResult(
                check_name="Referential Integrity",
                status="PASS",
                details={
                    "legacy_fk_count": len(legacy_fks),
                    "supabase_fk_count": len(supabase_fks),
                    "orphaned_records": orphaned_records
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return VerificationResult(
                check_name="Referential Integrity",
                status="FAIL",
                details={},
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    async def verify_data_completeness(self) -> VerificationResult:
        """Validate 100% of user data, settings, and configurations migrated"""
        logger.info("Starting data completeness verification...")
        
        try:
            legacy_conn = await self.connect_legacy_db()
            supabase_conn = await self.connect_supabase_db()
            
            # Check critical data tables
            critical_tables = ['users', 'tenants', 'ideas', 'factory_pipelines']
            completeness_results = {}
            
            for table in critical_tables:
                try:
                    legacy_count = await self.get_table_record_count(legacy_conn, table)
                    supabase_count = await self.get_table_record_count(supabase_conn, table)
                    
                    if legacy_count > 0:
                        completeness = supabase_count / legacy_count
                        completeness_results[table] = {
                            "legacy_count": legacy_count,
                            "supabase_count": supabase_count,
                            "completeness_percentage": completeness * 100
                        }
                    else:
                        completeness_results[table] = {
                            "legacy_count": 0,
                            "supabase_count": supabase_count,
                            "completeness_percentage": 100 if supabase_count == 0 else 0
                        }
                        
                except Exception as e:
                    completeness_results[table] = {
                        "error": str(e)
                    }
            
            # Check if any table has less than 100% completeness
            incomplete_tables = [
                table for table, result in completeness_results.items()
                if "completeness_percentage" in result and result["completeness_percentage"] < 100
            ]
            
            await legacy_conn.close()
            await supabase_conn.close()
            
            if incomplete_tables:
                return VerificationResult(
                    check_name="Data Completeness",
                    status="FAIL",
                    details={
                        "completeness_results": completeness_results,
                        "incomplete_tables": incomplete_tables,
                        "total_tables": len(critical_tables)
                    },
                    timestamp=datetime.now(),
                    error_message=f"Incomplete data migration detected in tables: {incomplete_tables}"
                )
            
            return VerificationResult(
                check_name="Data Completeness",
                status="PASS",
                details={
                    "completeness_results": completeness_results,
                    "total_tables": len(critical_tables),
                    "all_tables_complete": True
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return VerificationResult(
                check_name="Data Completeness",
                status="FAIL",
                details={},
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    async def get_table_list(self, conn: asyncpg.Connection) -> List[str]:
        """Get list of tables from database"""
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """
        result = await conn.fetch(query)
        return [row['table_name'] for row in result]
    
    async def get_table_record_count(self, conn: asyncpg.Connection, table: str) -> int:
        """Get record count for a table"""
        try:
            query = f"SELECT COUNT(*) FROM {table}"
            result = await conn.fetchval(query)
            return result or 0
        except Exception:
            return 0
    
    async def get_foreign_key_constraints(self, conn: asyncpg.Connection) -> List[Dict]:
        """Get foreign key constraints from database"""
        query = """
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
        """
        result = await conn.fetch(query)
        return [dict(row) for row in result]
    
    def _fk_matches(self, fk1: Dict, fk2: Dict) -> bool:
        """Check if two foreign key constraints match"""
        return (fk1['table_name'] == fk2['table_name'] and
                fk1['column_name'] == fk2['column_name'] and
                fk1['foreign_table_name'] == fk2['foreign_table_name'] and
                fk1['foreign_column_name'] == fk2['foreign_column_name'])
    
    async def check_orphaned_records(self, legacy_conn: asyncpg.Connection, 
                                   supabase_conn: asyncpg.Connection) -> List[Dict]:
        """Check for orphaned records in foreign key relationships"""
        # This is a simplified check - in practice you'd want to check each FK relationship
        orphaned_records = []
        
        # Example: Check if users reference valid tenants
        try:
            query = """
            SELECT u.id, u.tenant_id 
            FROM users u 
            LEFT JOIN tenants t ON u.tenant_id = t.id 
            WHERE t.id IS NULL AND u.tenant_id IS NOT NULL
            """
            result = await legacy_conn.fetch(query)
            if result:
                orphaned_records.append({
                    "table": "users",
                    "orphaned_count": len(result),
                    "details": "Users referencing non-existent tenants"
                })
        except Exception:
            pass
        
        return orphaned_records
    
    async def run_all_verifications(self) -> List[VerificationResult]:
        """Run all verification checks"""
        logger.info("Starting comprehensive data integrity verification...")
        
        verifications = [
            self.verify_database_parity(),
            self.verify_golden_queries(),
            self.verify_referential_integrity(),
            self.verify_data_completeness()
        ]
        
        results = await asyncio.gather(*verifications, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.results.append(VerificationResult(
                    check_name=f"Verification {i+1}",
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
        report.append("DATA INTEGRITY VERIFICATION REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
                    else:
                        report.append(f"  {key}: {value}")
            
            if result.error_message:
                report.append(f"  Error: {result.error_message}")
            
            report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 40)
        
        if failed_checks == 0:
            report.append("🎉 All checks passed! Data integrity verification is complete.")
            report.append("✅ Database Parity: <0.05% drift threshold met")
            report.append("✅ Golden Query Validation: All critical queries return identical results")
            report.append("✅ Referential Integrity: All foreign key relationships intact")
            report.append("✅ Data Completeness: 100% of critical data migrated")
        else:
            report.append("⚠️  Some checks failed. Review the details above and address issues before proceeding.")
            report.append("🔧 Recommended actions:")
            for result in self.results:
                if result.status == "FAIL":
                    report.append(f"  - Fix {result.check_name}: {result.error_message}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)

async def main():
    """Main function"""
    logger.info("Starting Data Integrity Verification...")
    
    # Check if Supabase configuration is available
    if not os.getenv('SUPABASE_DB_HOST'):
        logger.warning("Supabase configuration not found. Running in legacy-only mode.")
        logger.info("Set SUPABASE_DB_HOST, SUPABASE_DB_NAME, SUPABASE_DB_USER, SUPABASE_DB_PASSWORD to enable full verification.")
    
    verifier = DataIntegrityVerifier()
    
    try:
        results = await verifier.run_all_verifications()
        report = verifier.generate_report()
        
        print(report)
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"data_integrity_report_{timestamp}.txt"
        
        with open(report_filename, 'w') as f:
            f.write(report)
        
        logger.info(f"Report saved to {report_filename}")
        
        # Return exit code based on results
        failed_checks = sum(1 for r in results if r.status == "FAIL")
        if failed_checks > 0:
            logger.error(f"Verification failed with {failed_checks} failed checks")
            sys.exit(1)
        else:
            logger.info("All verifications passed successfully!")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Verification failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
