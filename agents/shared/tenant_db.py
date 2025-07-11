"""
Tenant-aware database service for SaaS Factory
Handles multi-tenancy with Row Level Security (RLS)
"""

import os
import uuid
import asyncio
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
import asyncpg
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class TenantContext:
    """Manages tenant context for database operations"""
    
    def __init__(self, tenant_id: str, user_id: Optional[str] = None):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.created_at = datetime.utcnow()

class TenantDatabase:
    """Tenant-aware database service with Row Level Security"""
    
    def __init__(self):
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_port = int(os.getenv("DB_PORT", "5432"))
        self.db_name = os.getenv("DB_NAME", "factorydb")
        self.db_user = os.getenv("DB_USER", "factoryadmin")
        self.db_password = os.getenv("DB_PASSWORD", "localpass")
        self._pool = None
        
    async def init_pool(self):
        """Initialize connection pool"""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool initialized")
    
    async def close_pool(self):
        """Close connection pool"""
        if self._pool:
            await self._pool.close()
            self._pool = None
            logger.info("Database connection pool closed")
    
    @asynccontextmanager
    async def get_tenant_connection(self, tenant_context: TenantContext):
        """Get a database connection with tenant context set for RLS"""
        if self._pool is None:
            await self.init_pool()
        
        async with self._pool.acquire() as conn:
            try:
                # Set tenant context for Row Level Security
                await conn.execute(
                    "SET app.current_tenant_id = $1",
                    tenant_context.tenant_id
                )
                
                if tenant_context.user_id:
                    await conn.execute(
                        "SET app.current_user_id = $1",
                        tenant_context.user_id
                    )
                
                # Set role for RLS policies
                await conn.execute("SET ROLE application_role")
                
                yield conn
                
            finally:
                # Reset context
                await conn.execute("RESET app.current_tenant_id")
                await conn.execute("RESET app.current_user_id")
                await conn.execute("RESET ROLE")
    
    async def get_tenant_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get tenant information by slug (bypass RLS for tenant lookup)"""
        if self._pool is None:
            await self.init_pool()
        
        async with self._pool.acquire() as conn:
            # Bypass RLS for tenant lookup
            await conn.execute("SET row_security = off")
            try:
                row = await conn.fetchrow(
                    "SELECT * FROM tenants WHERE slug = $1 AND status = 'active'",
                    slug
                )
                return dict(row) if row else None
            finally:
                await conn.execute("SET row_security = on")
    
    async def get_tenant_by_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get tenant information by domain (bypass RLS for tenant lookup)"""
        if self._pool is None:
            await self.init_pool()
        
        async with self._pool.acquire() as conn:
            await conn.execute("SET row_security = off")
            try:
                row = await conn.fetchrow(
                    "SELECT * FROM tenants WHERE domain = $1 AND status = 'active'",
                    domain
                )
                return dict(row) if row else None
            finally:
                await conn.execute("SET row_security = on")
    
    async def create_project(
        self, 
        tenant_context: TenantContext,
        name: str,
        description: str,
        project_type: str,
        config: Dict[str, Any] = None
    ) -> str:
        """Create a new project"""
        async with self.get_tenant_connection(tenant_context) as conn:
            project_id = str(uuid.uuid4())
            await conn.execute(
                """
                INSERT INTO projects (id, tenant_id, name, description, project_type, config, created_by)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                project_id,
                tenant_context.tenant_id,
                name,
                description,
                project_type,
                json.dumps(config or {}),
                tenant_context.user_id
            )
            return project_id
    
    async def save_design_recommendation(
        self,
        tenant_context: TenantContext,
        project_id: Optional[str],
        recommendation: Dict[str, Any]
    ) -> str:
        """Save design recommendation to database"""
        async with self.get_tenant_connection(tenant_context) as conn:
            rec_id = str(uuid.uuid4())
            await conn.execute(
                """
                INSERT INTO design_recommendations (
                    id, tenant_id, project_id, project_type, wireframes, 
                    style_guide, figma_project_url, design_system, 
                    reasoning, estimated_dev_time, created_by
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """,
                rec_id,
                tenant_context.tenant_id,
                project_id,
                recommendation.get('project_type', 'web'),
                json.dumps(recommendation.get('wireframes', [])),
                json.dumps(recommendation.get('style_guide', {})),
                recommendation.get('figma_project_url'),
                json.dumps(recommendation.get('design_system', {})),
                recommendation.get('reasoning'),
                recommendation.get('estimated_dev_time'),
                tenant_context.user_id
            )
            return rec_id
    
    async def save_techstack_recommendation(
        self,
        tenant_context: TenantContext,
        project_id: Optional[str],
        recommendation: Dict[str, Any]
    ) -> str:
        """Save tech stack recommendation to database"""
        async with self.get_tenant_connection(tenant_context) as conn:
            rec_id = str(uuid.uuid4())
            await conn.execute(
                """
                INSERT INTO tech_stack_recommendations (
                    id, tenant_id, project_id, project_type, frontend, backend,
                    database, deployment, testing, overall_score, reasoning, created_by
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """,
                rec_id,
                tenant_context.tenant_id,
                project_id,
                recommendation.get('project_type', 'web'),
                json.dumps(recommendation.get('frontend', [])),
                json.dumps(recommendation.get('backend', [])),
                json.dumps(recommendation.get('database', [])),
                json.dumps(recommendation.get('deployment', [])),
                json.dumps(recommendation.get('testing', [])),
                recommendation.get('overall_score', 0.0),
                recommendation.get('reasoning'),
                tenant_context.user_id
            )
            return rec_id
    
    async def log_agent_event(
        self,
        tenant_context: TenantContext,
        event_type: str,
        agent_name: str,
        stage: Optional[str] = None,
        status: str = 'started',
        project_id: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None
    ) -> str:
        """Log agent event"""
        async with self.get_tenant_connection(tenant_context) as conn:
            event_id = str(uuid.uuid4())
            await conn.execute(
                """
                INSERT INTO agent_events (
                    id, tenant_id, project_id, event_type, agent_name, stage, status,
                    input_data, output_data, error_message, duration_ms,
                    started_at, completed_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                """,
                event_id,
                tenant_context.tenant_id,
                project_id,
                event_type,
                agent_name,
                stage,
                status,
                json.dumps(input_data) if input_data else None,
                json.dumps(output_data) if output_data else None,
                error_message,
                duration_ms,
                datetime.utcnow() if status == 'started' else None,
                datetime.utcnow() if status in ['completed', 'failed'] else None
            )
            return event_id
    
    async def get_tenant_designs(
        self,
        tenant_context: TenantContext,
        project_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get design recommendations for tenant"""
        async with self.get_tenant_connection(tenant_context) as conn:
            query = """
                SELECT d.*, p.name as project_name
                FROM design_recommendations d
                LEFT JOIN projects p ON d.project_id = p.id
                WHERE ($1::UUID IS NULL OR d.project_id = $1)
                ORDER BY d.created_at DESC
                LIMIT $2
            """
            rows = await conn.fetch(query, project_id, limit)
            return [dict(row) for row in rows]
    
    async def get_tenant_events(
        self,
        tenant_context: TenantContext,
        event_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get agent events for tenant"""
        async with self.get_tenant_connection(tenant_context) as conn:
            query = """
                SELECT * FROM agent_events
                WHERE ($1::text IS NULL OR event_type = $1)
                ORDER BY created_at DESC
                LIMIT $2
            """
            rows = await conn.fetch(query, event_type, limit)
            return [dict(row) for row in rows]
    
    async def get_tenant_projects(
        self,
        tenant_context: TenantContext,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get projects for tenant"""
        async with self.get_tenant_connection(tenant_context) as conn:
            query = """
                SELECT * FROM projects
                WHERE ($1::text IS NULL OR status = $1)
                ORDER BY created_at DESC
            """
            rows = await conn.fetch(query, status)
            return [dict(row) for row in rows]

# Global database instance
tenant_db = TenantDatabase()

def get_tenant_context_from_headers(headers: Dict[str, str]) -> Optional[TenantContext]:
    """Extract tenant context from HTTP headers"""
    tenant_id = headers.get('x-tenant-id')
    user_id = headers.get('x-user-id')
    
    if not tenant_id:
        # Try to extract from host header for domain-based routing
        host = headers.get('host', '')
        if host and host != 'localhost':
            # In production, you'd look up tenant by domain
            # For now, use default tenant
            tenant_id = 'default'
    
    if tenant_id:
        return TenantContext(tenant_id=tenant_id, user_id=user_id)
    
    return None

async def get_default_tenant_context() -> TenantContext:
    """Get default tenant context for development"""
    # In production, this would require proper tenant resolution
    default_tenant = await tenant_db.get_tenant_by_slug('default')
    if default_tenant:
        return TenantContext(tenant_id=str(default_tenant['id']))
    
    # Create default tenant if it doesn't exist
    raise Exception("Default tenant not found. Please run database migrations.")

# Ensure cleanup on shutdown
import atexit
atexit.register(lambda: asyncio.run(tenant_db.close_pool())) 