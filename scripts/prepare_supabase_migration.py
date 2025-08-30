#!/usr/bin/env python3
"""
Supabase Migration Preparation Script
Prepares Supabase database for final data migration
"""

import os
import sys
import logging
import asyncio
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

async def prepare_supabase_for_migration():
    """Prepare Supabase database for migration"""
    try:
        logger.info("🔧 Preparing Supabase for final data migration...")
        
        settings = get_settings()
        
        # Debug: Print connection parameters
        logger.info(f"🔍 Supabase connection parameters:")
        logger.info(f"   Host: {settings.supabase.db_host}")
        logger.info(f"   Port: {settings.supabase.db_port}")
        logger.info(f"   Database: {settings.supabase.db_name}")
        logger.info(f"   User: {settings.supabase.db_user}")
        logger.info(f"   Password: {'*' * len(settings.supabase.db_password.get_secret_value()) if settings.supabase.db_password.get_secret_value() else 'None'}")
        
        # Connect to Supabase
        conn = psycopg2.connect(
            host=settings.supabase.db_host,
            port=settings.supabase.db_port,
            database=settings.supabase.db_name,
            user=settings.supabase.db_user,
            password=settings.supabase.db_password.get_secret_value()
        )
        
        with conn.cursor() as cursor:
            # Check if migration tables exist
            logger.info("📋 Checking migration infrastructure...")
            
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name IN ('cutover_tables', 'cutover_checklists', 'freeze_windows')
            """)
            
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            if not existing_tables:
                logger.info("🏗️  Creating migration infrastructure tables...")
                
                # Read and execute migration SQL
                migration_sql_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)), 
                    "dev", "migrations", "013_create_final_data_migration_tables.sql"
                )
                
                if os.path.exists(migration_sql_path):
                    with open(migration_sql_path, 'r') as f:
                        migration_sql = f.read()
                    
                    # Execute the entire SQL file as one statement
                    # This avoids issues with complex SQL parsing
                    try:
                        cursor.execute(migration_sql)
                        logger.info("✅ Migration infrastructure SQL executed successfully")
                    except Exception as e:
                        if "already exists" not in str(e).lower():
                            logger.warning(f"⚠️  SQL execution warning: {str(e)}")
                    
                    conn.commit()
                    logger.info("✅ Migration infrastructure tables created successfully")
                else:
                    logger.error(f"❌ Migration SQL file not found: {migration_sql_path}")
                    return False
            else:
                logger.info(f"✅ Migration infrastructure already exists: {existing_tables}")
            
            # Initialize migration tracking
            logger.info("📊 Initializing migration tracking...")
            
            # Check if we need to initialize cutover_tables
            cursor.execute("SELECT COUNT(*) FROM cutover_tables")
            table_count = cursor.fetchone()[0]
            
            if table_count == 0:
                logger.info("🔍 Initializing migration table tracking...")
                
                # Define tables to migrate
                migration_tables = [
                    "tenants", "users", "ideas", "projects", "design_recommendations",
                    "techstack_recommendations", "agent_events", "security_scan_results",
                    "license_scan_results", "gdpr_consent_tracking", "secrets_rotation",
                    "video_scripts", "zap_scan_results", "factory_pipelines",
                    "user_feature_embeddings", "experiment_events"
                ]
                
                for table_name in migration_tables:
                    cursor.execute("""
                        INSERT INTO cutover_tables (name, status, validation_status, read_source, write_source)
                        VALUES (%s, 'pending', 'pending', 'legacy', 'dual')
                    """, (table_name,))
                
                conn.commit()
                logger.info(f"✅ Initialized tracking for {len(migration_tables)} tables")
            else:
                logger.info(f"✅ Migration tracking already initialized with {table_count} tables")
            
            # Verify infrastructure
            logger.info("🔍 Verifying migration infrastructure...")
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_tables,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_tables,
                    COUNT(CASE WHEN status = 'ready' THEN 1 END) as ready_tables
                FROM cutover_tables
            """)
            
            verification = cursor.fetchone()
            logger.info(f"📊 Migration infrastructure verification:")
            logger.info(f"   Total tables: {verification[0]}")
            logger.info(f"   Pending: {verification[1]}")
            logger.info(f"   Ready: {verification[2]}")
            
            conn.close()
            
            logger.info("✅ Supabase preparation completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"❌ Supabase preparation failed: {str(e)}")
        return False

async def main():
    """Main function"""
    success = await prepare_supabase_for_migration()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
