#!/usr/bin/env python3
"""
Tenant Isolation Promotion Script
Promotes a tenant from shared infrastructure to dedicated isolated database.

Usage:
    python tenant_isolation.py promote --tenant-slug=acme-corp --confirm
    python tenant_isolation.py rollback --tenant-slug=acme-corp --confirm
    python tenant_isolation.py status --tenant-slug=acme-corp
"""

import asyncio
import asyncpg
import argparse
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TenantIsolationError(Exception):
    """Custom exception for tenant isolation operations"""
    pass

class TenantIsolationManager:
    """Manages tenant isolation operations"""
    
    def __init__(self):
        self.source_db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'factorydb'),
            'user': os.getenv('DB_USER', 'factoryadmin'),
            'password': os.getenv('DB_PASSWORD', 'localpass')
        }
        
        # For isolation, we'll create separate databases
        self.postgres_admin_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': 'postgres',  # Connect to postgres DB for admin operations
            'user': os.getenv('DB_USER', 'factoryadmin'),
            'password': os.getenv('DB_PASSWORD', 'localpass')
        }
        
    async def get_tenant_info(self, tenant_slug: str) -> Optional[Dict[str, Any]]:
        """Get tenant information from the source database"""
        try:
            conn = await asyncpg.connect(**self.source_db_config)
            
            # Disable RLS temporarily for admin operations
            await conn.execute("SET row_security = off")
            
            row = await conn.fetchrow(
                "SELECT * FROM tenants WHERE slug = $1",
                tenant_slug
            )
            
            await conn.close()
            
            if row:
                return dict(row)
            else:
                raise TenantIsolationError(f"Tenant '{tenant_slug}' not found")
                
        except Exception as e:
            logger.error(f"Error fetching tenant info: {e}")
            raise TenantIsolationError(f"Failed to fetch tenant info: {e}")
    
    async def create_isolated_database(self, tenant_slug: str, tenant_id: str) -> str:
        """Create a new database for the isolated tenant"""
        isolated_db_name = f"tenant_{tenant_slug.replace('-', '_')}"
        
        try:
            # Connect to postgres database for admin operations
            conn = await asyncpg.connect(**self.postgres_admin_config)
            
            # Check if database already exists
            exists = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1",
                isolated_db_name
            )
            
            if exists:
                logger.warning(f"Database {isolated_db_name} already exists")
            else:
                # Create the database
                await conn.execute(f'CREATE DATABASE "{isolated_db_name}"')
                logger.info(f"Created isolated database: {isolated_db_name}")
            
            await conn.close()
            return isolated_db_name
            
        except Exception as e:
            logger.error(f"Error creating isolated database: {e}")
            raise TenantIsolationError(f"Failed to create isolated database: {e}")
    
    async def clone_schema(self, isolated_db_name: str):
        """Clone the database schema to the isolated database"""
        try:
            # Connect to the isolated database
            isolated_config = self.source_db_config.copy()
            isolated_config['database'] = isolated_db_name
            
            conn = await asyncpg.connect(**isolated_config)
            
            # Read and execute the schema migration
            schema_file = 'dev/migrations/001_create_tenant_model.sql'
            if os.path.exists(schema_file):
                with open(schema_file, 'r') as f:
                    schema_sql = f.read()
                
                # Execute the schema creation
                await conn.execute(schema_sql)
                logger.info(f"Schema cloned to {isolated_db_name}")
            else:
                raise TenantIsolationError(f"Schema file not found: {schema_file}")
            
            await conn.close()
            
        except Exception as e:
            logger.error(f"Error cloning schema: {e}")
            raise TenantIsolationError(f"Failed to clone schema: {e}")
    
    async def migrate_tenant_data(self, tenant_id: str, isolated_db_name: str):
        """Migrate tenant data from shared to isolated database"""
        try:
            # Source connection (shared database)
            source_conn = await asyncpg.connect(**self.source_db_config)
            
            # Target connection (isolated database)
            isolated_config = self.source_db_config.copy()
            isolated_config['database'] = isolated_db_name
            target_conn = await asyncpg.connect(**isolated_config)
            
            # Disable RLS on source for data extraction
            await source_conn.execute("SET row_security = off")
            
            # Tables to migrate in order (respecting foreign key dependencies)
            tables_to_migrate = [
                'tenants',
                'users', 
                'projects',
                'design_recommendations',
                'tech_stack_recommendations',
                'agent_events',
                'audit_logs'
            ]
            
            total_migrated = 0
            
            for table in tables_to_migrate:
                logger.info(f"Migrating table: {table}")
                
                # Get tenant-specific data
                if table == 'tenants':
                    rows = await source_conn.fetch(
                        f"SELECT * FROM {table} WHERE id = $1",
                        tenant_id
                    )
                else:
                    rows = await source_conn.fetch(
                        f"SELECT * FROM {table} WHERE tenant_id = $1",
                        tenant_id
                    )
                
                if rows:
                    # Get column names
                    columns = list(rows[0].keys())
                    column_names = ', '.join(columns)
                    placeholders = ', '.join([f'${i+1}' for i in range(len(columns))])
                    
                    # Prepare insert statement
                    insert_sql = f"""
                        INSERT INTO {table} ({column_names}) 
                        VALUES ({placeholders})
                        ON CONFLICT DO NOTHING
                    """
                    
                    # Insert data into isolated database
                    for row in rows:
                        values = [row[col] for col in columns]
                        await target_conn.execute(insert_sql, *values)
                    
                    logger.info(f"Migrated {len(rows)} records from {table}")
                    total_migrated += len(rows)
                else:
                    logger.info(f"No data to migrate for table: {table}")
            
            await source_conn.close()
            await target_conn.close()
            
            logger.info(f"Migration completed. Total records migrated: {total_migrated}")
            
        except Exception as e:
            logger.error(f"Error migrating tenant data: {e}")
            raise TenantIsolationError(f"Failed to migrate tenant data: {e}")
    
    async def update_tenant_status(self, tenant_id: str, isolated_db_name: str):
        """Update tenant status to isolated and store database info"""
        try:
            conn = await asyncpg.connect(**self.source_db_config)
            
            # Disable RLS for admin operations
            await conn.execute("SET row_security = off")
            
            # Update tenant record
            isolation_config = {
                'isolated_db_name': isolated_db_name,
                'isolated_at': datetime.utcnow().isoformat(),
                'migration_version': '001'
            }
            
            await conn.execute(
                """
                UPDATE tenants 
                SET isolation_mode = 'isolated',
                    settings = settings || $2::jsonb,
                    updated_at = NOW()
                WHERE id = $1
                """,
                tenant_id,
                json.dumps({'isolation': isolation_config})
            )
            
            await conn.close()
            logger.info(f"Updated tenant status to isolated")
            
        except Exception as e:
            logger.error(f"Error updating tenant status: {e}")
            raise TenantIsolationError(f"Failed to update tenant status: {e}")
    
    async def create_routing_config(self, tenant_slug: str, isolated_db_name: str):
        """Create routing configuration for the isolated tenant"""
        try:
            # Create routing configuration file
            routing_config = {
                'tenant_slug': tenant_slug,
                'isolation_mode': 'isolated',
                'database': {
                    'name': isolated_db_name,
                    'host': self.source_db_config['host'],
                    'port': self.source_db_config['port'],
                    'user': self.source_db_config['user']
                },
                'created_at': datetime.utcnow().isoformat(),
                'endpoints': {
                    'api': f"api-{tenant_slug}.factory.local",
                    'ui': f"app-{tenant_slug}.factory.local"
                }
            }
            
            # Ensure routing directory exists
            os.makedirs('config/routing', exist_ok=True)
            
            # Write routing configuration
            config_file = f"config/routing/{tenant_slug}.json"
            with open(config_file, 'w') as f:
                json.dump(routing_config, f, indent=2)
            
            logger.info(f"Created routing configuration: {config_file}")
            
        except Exception as e:
            logger.error(f"Error creating routing config: {e}")
            raise TenantIsolationError(f"Failed to create routing config: {e}")
    
    async def cleanup_shared_data(self, tenant_id: str):
        """Remove tenant data from shared database after successful migration"""
        try:
            conn = await asyncpg.connect(**self.source_db_config)
            
            # Disable RLS for admin operations
            await conn.execute("SET row_security = off")
            
            # Tables to clean up in reverse order (respecting foreign key dependencies)
            tables_to_cleanup = [
                'audit_logs',
                'agent_events', 
                'tech_stack_recommendations',
                'design_recommendations',
                'projects',
                'users'
                # Note: We keep the tenant record in shared DB for routing
            ]
            
            total_deleted = 0
            
            for table in tables_to_cleanup:
                result = await conn.execute(
                    f"DELETE FROM {table} WHERE tenant_id = $1",
                    tenant_id
                )
                deleted_count = int(result.split()[-1])
                logger.info(f"Deleted {deleted_count} records from {table}")
                total_deleted += deleted_count
            
            await conn.close()
            logger.info(f"Cleanup completed. Total records deleted: {total_deleted}")
            
        except Exception as e:
            logger.error(f"Error cleaning up shared data: {e}")
            raise TenantIsolationError(f"Failed to cleanup shared data: {e}")
    
    async def promote_tenant(self, tenant_slug: str, cleanup_shared: bool = True) -> Dict[str, Any]:
        """Promote a tenant to isolated infrastructure"""
        logger.info(f"Starting tenant isolation promotion for: {tenant_slug}")
        
        try:
            # Step 1: Get tenant information
            tenant_info = await self.get_tenant_info(tenant_slug)
            tenant_id = str(tenant_info['id'])
            
            if tenant_info['isolation_mode'] == 'isolated':
                raise TenantIsolationError(f"Tenant {tenant_slug} is already isolated")
            
            # Step 2: Create isolated database
            isolated_db_name = await self.create_isolated_database(tenant_slug, tenant_id)
            
            # Step 3: Clone schema
            await self.clone_schema(isolated_db_name)
            
            # Step 4: Migrate tenant data
            await self.migrate_tenant_data(tenant_id, isolated_db_name)
            
            # Step 5: Update tenant status
            await self.update_tenant_status(tenant_id, isolated_db_name)
            
            # Step 6: Create routing configuration
            await self.create_routing_config(tenant_slug, isolated_db_name)
            
            # Step 7: Cleanup shared data (optional)
            if cleanup_shared:
                await self.cleanup_shared_data(tenant_id)
            
            result = {
                'status': 'success',
                'tenant_slug': tenant_slug,
                'tenant_id': tenant_id,
                'isolated_db_name': isolated_db_name,
                'completed_at': datetime.utcnow().isoformat(),
                'cleanup_shared': cleanup_shared
            }
            
            logger.info(f"Tenant isolation promotion completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Tenant isolation promotion failed: {e}")
            raise TenantIsolationError(f"Promotion failed: {e}")
    
    async def get_isolation_status(self, tenant_slug: str) -> Dict[str, Any]:
        """Get the current isolation status of a tenant"""
        try:
            tenant_info = await self.get_tenant_info(tenant_slug)
            
            status = {
                'tenant_slug': tenant_slug,
                'tenant_id': str(tenant_info['id']),
                'isolation_mode': tenant_info['isolation_mode'],
                'plan': tenant_info['plan'],
                'status': tenant_info['status'],
                'created_at': tenant_info['created_at'].isoformat(),
                'updated_at': tenant_info['updated_at'].isoformat()
            }
            
            # Check for isolation configuration
            settings = tenant_info.get('settings', {})
            if isinstance(settings, str):
                settings = json.loads(settings)
            
            isolation_config = settings.get('isolation', {})
            if isolation_config:
                status['isolation'] = isolation_config
            
            # Check for routing configuration
            config_file = f"config/routing/{tenant_slug}.json"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    routing_config = json.load(f)
                status['routing'] = routing_config
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting isolation status: {e}")
            raise TenantIsolationError(f"Failed to get isolation status: {e}")

async def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='Tenant Isolation Management')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Promote command
    promote_parser = subparsers.add_parser('promote', help='Promote tenant to isolated infrastructure')
    promote_parser.add_argument('--tenant-slug', required=True, help='Tenant slug to promote')
    promote_parser.add_argument('--confirm', action='store_true', help='Confirm the promotion')
    promote_parser.add_argument('--keep-shared-data', action='store_true', help='Keep data in shared database')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get tenant isolation status')
    status_parser.add_argument('--tenant-slug', required=True, help='Tenant slug to check')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all tenants and their isolation status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = TenantIsolationManager()
    
    try:
        if args.command == 'promote':
            if not args.confirm:
                print("❌ Promotion requires --confirm flag for safety")
                return
            
            print(f"🚀 Starting tenant isolation promotion for: {args.tenant_slug}")
            result = await manager.promote_tenant(
                args.tenant_slug, 
                cleanup_shared=not args.keep_shared_data
            )
            
            print("✅ Tenant isolation promotion completed!")
            print(json.dumps(result, indent=2))
            
        elif args.command == 'status':
            print(f"📊 Getting isolation status for: {args.tenant_slug}")
            status = await manager.get_isolation_status(args.tenant_slug)
            print(json.dumps(status, indent=2))
            
        elif args.command == 'list':
            print("📋 Listing all tenants... (Not implemented yet)")
            
    except TenantIsolationError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main()) 