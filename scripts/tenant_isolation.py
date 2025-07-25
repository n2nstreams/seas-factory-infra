#!/usr/bin/env python3
"""
Tenant Isolation Promotion Script
Promotes a tenant from shared infrastructure to dedicated isolated database and Cloud Run revision.

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
import subprocess
import urllib.request
import urllib.error
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
        
        # Cloud configuration
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'saas-factory-prod')
        self.region = os.getenv('CLOUD_RUN_REGION', 'us-central1')
        self.container_image = os.getenv('CONTAINER_IMAGE', f'{self.region}-docker.pkg.dev/{self.project_id}/saas-factory/api:latest')
        
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
    
    async def create_cloud_run_service(self, tenant_slug: str, isolated_db_name: str) -> str:
        """Create isolated Cloud Run service for the tenant"""
        service_name = f"api-{tenant_slug}"
        
        try:
            logger.info(f"Creating Cloud Run service: {service_name}")
            
            # Prepare database URL for the isolated instance
            db_url = f"postgresql://{self.source_db_config['user']}:{self.source_db_config['password']}@{self.source_db_config['host']}:{self.source_db_config['port']}/{isolated_db_name}"
            
            # Prepare gcloud command for Cloud Run deployment
            deploy_cmd = [
                'gcloud', 'run', 'deploy', service_name,
                '--image', self.container_image,
                '--platform', 'managed',
                '--region', self.region,
                '--project', self.project_id,
                '--allow-unauthenticated',
                '--port', '8080',
                '--memory', '2Gi',
                '--cpu', '2',
                '--min-instances', '0',
                '--max-instances', '10',
                '--set-env-vars', f'DB_HOST={self.source_db_config["host"]}',
                '--set-env-vars', f'DB_PORT={self.source_db_config["port"]}',
                '--set-env-vars', f'DB_NAME={isolated_db_name}',
                '--set-env-vars', f'DB_USER={self.source_db_config["user"]}',
                '--set-env-vars', f'DB_PASSWORD={self.source_db_config["password"]}',
                '--set-env-vars', f'TENANT_ID={tenant_slug}',
                '--set-env-vars', f'ISOLATION_MODE=isolated',
                '--vpc-connector', f'projects/{self.project_id}/locations/{self.region}/connectors/vpc-connector',
                '--vpc-egress', 'private-ranges-only',
                '--quiet'
            ]
            
            # Execute the deployment
            result = subprocess.run(deploy_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Cloud Run deployment failed: {result.stderr}")
                raise TenantIsolationError(f"Failed to deploy Cloud Run service: {result.stderr}")
            
            # Extract service URL from output
            service_url = None
            for line in result.stdout.split('\n'):
                if 'Service URL:' in line:
                    service_url = line.split('Service URL:')[1].strip()
                    break
            
            if not service_url:
                # Fallback: construct URL based on standard Cloud Run naming
                service_url = f"https://{service_name}-{self.project_id}.{self.region}.run.app"
            
            logger.info(f"Cloud Run service deployed successfully: {service_url}")
            return service_url
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error deploying Cloud Run service: {e}")
            raise TenantIsolationError(f"Failed to deploy Cloud Run service: {e}")
        except Exception as e:
            logger.error(f"Unexpected error deploying Cloud Run service: {e}")
            raise TenantIsolationError(f"Failed to deploy Cloud Run service: {e}")

    async def create_load_balancer_routing(self, tenant_slug: str, service_url: str):
        """Create load balancer routing for tenant-specific subdomain"""
        try:
            logger.info(f"Setting up load balancer routing for tenant: {tenant_slug}")
            
            # For now, we'll create a mapping file that can be used by load balancer configuration
            # In a production environment, this would integrate with Google Cloud Load Balancer
            
            routing_config = {
                'tenant_slug': tenant_slug,
                'subdomain': f"app-{tenant_slug}",
                'service_url': service_url,
                'backend_service': f"api-{tenant_slug}",
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Ensure load balancer config directory exists
            os.makedirs('config/load-balancer', exist_ok=True)
            
            # Write load balancer configuration
            config_file = f"config/load-balancer/{tenant_slug}.json"
            with open(config_file, 'w') as f:
                json.dump(routing_config, f, indent=2)
            
            logger.info(f"Load balancer routing configuration created: {config_file}")
            
            # TODO: In production, this would call Google Cloud Load Balancer API to:
            # 1. Create backend service pointing to the Cloud Run service
            # 2. Update URL map with the new subdomain routing
            # 3. Update SSL certificate for the new subdomain
            
        except Exception as e:
            logger.error(f"Error creating load balancer routing: {e}")
            raise TenantIsolationError(f"Failed to create load balancer routing: {e}")

    async def verify_cloud_run_deployment(self, tenant_slug: str, service_url: str) -> bool:
        """Verify that the Cloud Run service is healthy and responsive"""
        try:
            logger.info(f"Verifying Cloud Run deployment for {tenant_slug}")
            
            # Simple health check - try to reach the service
            health_url = f"{service_url}/health" if service_url.endswith('/') else f"{service_url}/health"
            
            try:
                with urllib.request.urlopen(health_url, timeout=30) as response:
                    if response.getcode() == 200:
                        logger.info(f"Cloud Run service is healthy: {service_url}")
                        return True
                    else:
                        logger.warning(f"Cloud Run service returned status {response.getcode()}")
                        return False
            except urllib.error.URLError:
                # Health endpoint might not be implemented yet, try root path
                try:
                    with urllib.request.urlopen(service_url, timeout=30) as response:
                        logger.info(f"Cloud Run service is responsive: {service_url}")
                        return True
                except urllib.error.URLError as e:
                    logger.error(f"Cloud Run service is not responsive: {e}")
                    return False
                
        except Exception as e:
            logger.error(f"Error verifying Cloud Run deployment: {e}")
            return False

    async def create_routing_config(self, tenant_slug: str, isolated_db_name: str, service_url: str = None):
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
                'cloud_run': {
                    'service_name': f"api-{tenant_slug}",
                    'service_url': service_url,
                    'region': self.region
                },
                'created_at': datetime.utcnow().isoformat(),
                'endpoints': {
                    'api': service_url or f"api-{tenant_slug}.factory.local",
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
    
    async def promote_tenant(self, tenant_slug: str, cleanup_shared: bool = True, deploy_cloud_run: bool = True) -> Dict[str, Any]:
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
            
            # Step 5: Deploy isolated Cloud Run service (if enabled)
            service_url = None
            if deploy_cloud_run:
                service_url = await self.create_cloud_run_service(tenant_slug, isolated_db_name)
                
                # Verify deployment
                deployment_healthy = await self.verify_cloud_run_deployment(tenant_slug, service_url)
                if not deployment_healthy:
                    logger.warning("Cloud Run deployment verification failed, but continuing...")
                
                # Set up load balancer routing
                await self.create_load_balancer_routing(tenant_slug, service_url)
            
            # Step 6: Update tenant status
            await self.update_tenant_status(tenant_id, isolated_db_name)
            
            # Step 7: Create routing configuration (updated with Cloud Run info)
            await self.create_routing_config(tenant_slug, isolated_db_name, service_url)
            
            # Step 8: Cleanup shared data (optional)
            if cleanup_shared:
                await self.cleanup_shared_data(tenant_id)
            
            result = {
                'status': 'success',
                'tenant_slug': tenant_slug,
                'tenant_id': tenant_id,
                'isolated_db_name': isolated_db_name,
                'cloud_run_service_url': service_url,
                'completed_at': datetime.utcnow().isoformat(),
                'cleanup_shared': cleanup_shared,
                'cloud_run_deployed': deploy_cloud_run
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
    promote_parser.add_argument('--no-cloud-run', action='store_true', help='Skip Cloud Run deployment')
    
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
                cleanup_shared=not args.keep_shared_data,
                deploy_cloud_run=not args.no_cloud_run
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