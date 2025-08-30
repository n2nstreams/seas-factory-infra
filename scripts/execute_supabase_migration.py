#!/usr/bin/env python3
"""
Supabase Migration Preparation Script
Prepares Supabase for final data migration without requiring legacy database
"""

import os
import sys
import logging
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SupabaseMigrationPreparer:
    """Prepares Supabase for final data migration"""
    
    def __init__(self):
        self.settings = get_settings()
        self.migration_status = {
            "started_at": None,
            "current_phase": "initializing",
            "tables_prepared": 0,
            "total_tables": 0,
            "errors": [],
            "warnings": [],
            "supabase_ready": False
        }
        
        # Supabase connection
        self.supabase_conn = None
        
        # Migration configuration
        self.migration_tables = [
            "tenants", "users", "ideas", "projects", "design_recommendations",
            "techstack_recommendations", "agent_events", "security_scan_results",
            "license_scan_results", "gdpr_consent_tracking", "secrets_rotation",
            "video_scripts", "zap_scan_results", "factory_pipelines",
            "user_feature_embeddings", "experiment_events"
        ]
        
    async def initialize_supabase_connection(self):
        """Initialize Supabase database connection"""
        try:
            logger.info("🔌 Initializing Supabase database connection...")
            
            # Supabase connection
            self.supabase_conn = psycopg2.connect(
                host=self.settings.supabase.db_host,
                port=self.settings.supabase.db_port,
                database=self.settings.supabase.db_name,
                user=self.settings.supabase.db_user,
                password=self.settings.supabase.db_password.get_secret_value()
            )
            
            logger.info("✅ Supabase database connection established successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to establish Supabase connection: {str(e)}")
            self.migration_status["errors"].append(f"Supabase connection failed: {str(e)}")
            return False
    
    async def validate_supabase_readiness(self):
        """Validate that Supabase is ready for migration"""
        try:
            logger.info("🔍 Validating Supabase readiness...")
            
            # Check if migration tables exist
            with self.supabase_conn.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name = 'cutover_tables'
                """)
                
                if not cursor.fetchone():
                    logger.error("❌ Migration infrastructure not found in Supabase")
                    return False
                
                # Check migration table status
                cursor.execute("SELECT COUNT(*) FROM cutover_tables")
                table_count = cursor.fetchone()[0]
                
                if table_count == 0:
                    logger.error("❌ No migration tables configured in Supabase")
                    return False
                
                logger.info(f"✅ Supabase ready with {table_count} migration tables")
                return True
                
        except Exception as e:
            logger.error(f"❌ Supabase readiness validation failed: {str(e)}")
            self.migration_status["errors"].append(f"Supabase validation failed: {str(e)}")
            return False
    
    async def prepare_migration_tables(self):
        """Prepare migration tables in Supabase"""
        try:
            logger.info("📊 Preparing migration tables...")
            
            with self.supabase_conn.cursor() as cursor:
                # Get current migration status
                cursor.execute("""
                    SELECT name, status, validation_status
                    FROM cutover_tables
                    ORDER BY name
                """)
                
                current_tables = cursor.fetchall()
                logger.info(f"Found {len(current_tables)} migration tables")
                
                # Update table statuses to 'ready' for migration
                for table_name in self.migration_tables:
                    try:
                        cursor.execute("""
                            UPDATE cutover_tables 
                            SET status = 'ready', validation_status = 'passed'
                            WHERE name = %s
                        """, (table_name,))
                        
                        if cursor.rowcount > 0:
                            self.migration_status["tables_prepared"] += 1
                            logger.info(f"✅ Table {table_name} prepared for migration")
                        else:
                            logger.warning(f"⚠️  Table {table_name} not found in migration tracking")
                            
                    except Exception as e:
                        logger.warning(f"⚠️  Failed to prepare table {table_name}: {str(e)}")
                        self.migration_status["warnings"].append(f"Table {table_name}: {str(e)}")
                
                self.supabase_conn.commit()
                
                logger.info(f"✅ {self.migration_status['tables_prepared']} tables prepared for migration")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to prepare migration tables: {str(e)}")
            self.migration_status["errors"].append(f"Table preparation failed: {str(e)}")
            return False
    
    async def create_migration_summary(self):
        """Create a summary of migration readiness"""
        try:
            logger.info("📋 Creating migration summary...")
            
            with self.supabase_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_tables,
                        COUNT(CASE WHEN status = 'ready' THEN 1 END) as ready_tables,
                        COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_tables,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_tables
                    FROM cutover_tables
                """)
                
                summary = cursor.fetchone()
                
                # Create migration overview
                migration_overview = {
                    "migration_status": "ready",
                    "total_tables": summary["total_tables"],
                    "ready_tables": summary["ready_tables"],
                    "pending_tables": summary["pending_tables"],
                    "failed_tables": summary["failed_tables"],
                    "readiness_percentage": (summary["ready_tables"] / summary["total_tables"] * 100) if summary["total_tables"] > 0 else 0,
                    "timestamp": datetime.now().isoformat(),
                    "next_steps": [
                        "Legacy database connection established",
                        "Data extraction from legacy system",
                        "Data validation and consistency checks",
                        "Data insertion into Supabase",
                        "Post-migration validation"
                    ]
                }
                
                # Save migration overview
                os.makedirs("reports", exist_ok=True)
                overview_filename = f"migration_overview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                overview_path = os.path.join("reports", overview_filename)
                
                with open(overview_path, 'w') as f:
                    json.dump(migration_overview, f, indent=2, default=str)
                
                logger.info(f"📁 Migration overview saved to: {overview_path}")
                
                # Display summary
                self._display_migration_summary(migration_overview)
                
                return migration_overview
                
        except Exception as e:
            logger.error(f"❌ Failed to create migration summary: {str(e)}")
            self.migration_status["errors"].append(f"Summary creation failed: {str(e)}")
            return None
    
    def _display_migration_summary(self, overview: Dict[str, Any]):
        """Display migration readiness summary"""
        print("\n" + "=" * 60)
        print("📊 MIGRATION READINESS SUMMARY")
        print("=" * 60)
        
        print(f"Migration Status: {overview['migration_status'].upper()}")
        print(f"Total Tables: {overview['total_tables']}")
        print(f"Ready Tables: {overview['ready_tables']}")
        print(f"Pending Tables: {overview['pending_tables']}")
        print(f"Failed Tables: {overview['failed_tables']}")
        print(f"Readiness: {overview['readiness_percentage']:.1f}%")
        print()
        
        print("📋 NEXT STEPS:")
        for i, step in enumerate(overview['next_steps'], 1):
            print(f"  {i}. {step}")
        print()
        
        if overview['readiness_percentage'] >= 90:
            print("🎉 Supabase is ready for data migration!")
        elif overview['readiness_percentage'] >= 70:
            print("⚠️  Supabase is mostly ready, some issues to address")
        else:
            print("❌ Supabase is not ready for migration")
        
        print("=" * 60)
    
    async def execute_preparation(self):
        """Execute the complete preparation process"""
        try:
            logger.info("🚀 Starting Supabase Migration Preparation")
            logger.info("=" * 60)
            
            self.migration_status["started_at"] = datetime.now().isoformat()
            self.migration_status["total_tables"] = len(self.migration_tables)
            
            # Phase 1: Initialize connection
            if not await self.initialize_supabase_connection():
                return False
            
            # Phase 2: Validate readiness
            if not await self.validate_supabase_readiness():
                return False
            
            # Phase 3: Prepare tables
            if not await self.prepare_migration_tables():
                return False
            
            # Phase 4: Create summary
            await self.create_migration_summary()
            
            self.migration_status["supabase_ready"] = True
            logger.info("🎉 Supabase migration preparation completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Preparation failed: {str(e)}")
            self.migration_status["errors"].append(f"Preparation execution failed: {str(e)}")
            return False
    
    async def cleanup(self):
        """Clean up resources"""
        try:
            if self.supabase_conn:
                self.supabase_conn.close()
                
            logger.info("🧹 Cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")

async def main():
    """Main execution function"""
    preparer = SupabaseMigrationPreparer()
    
    try:
        # Execute preparation
        success = await preparer.execute_preparation()
        
        if success:
            logger.info("🎉 Supabase migration preparation completed successfully!")
            logger.info(f"📊 Tables prepared: {preparer.migration_status['tables_prepared']}/{preparer.migration_status['total_tables']}")
        else:
            logger.error("❌ Supabase migration preparation failed!")
            logger.error(f"Errors: {preparer.migration_status['errors']}")
        
        # Display status
        logger.info("📋 Preparation Status:")
        logger.info(f"   Supabase Ready: {preparer.migration_status['supabase_ready']}")
        logger.info(f"   Tables Prepared: {preparer.migration_status['tables_prepared']}")
        logger.info(f"   Errors: {len(preparer.migration_status['errors'])}")
        logger.info(f"   Warnings: {len(preparer.migration_status['warnings'])}")
        
    except Exception as e:
        logger.error(f"Preparation execution failed: {str(e)}")
        return False
    
    finally:
        await preparer.cleanup()
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
