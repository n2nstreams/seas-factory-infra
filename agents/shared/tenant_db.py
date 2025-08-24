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
from datetime import datetime
import json

# Use improved logging utilities
from .logging_utils import get_tenant_logger, log_tenant_operation

# Get logger instance
logger = get_tenant_logger(__name__)

class TenantContext:
    """Manages tenant context for database operations"""
    
    def __init__(self, tenant_id: str, user_id: Optional[str] = None, user_role: Optional[str] = None):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.user_role = user_role or 'user'
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
        
    @log_tenant_operation("init_pool")
    async def init_pool(self):
        """Initialize connection pool"""
        if self._pool is None:
            try:
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
            except Exception as e:
                logger.error(f"Failed to initialize database connection pool: {e}")
                raise
    
    @log_tenant_operation("close_pool")
    async def close_pool(self):
        """Close connection pool"""
        if self._pool:
            try:
                await self._pool.close()
                self._pool = None
                logger.info("Database connection pool closed")
            except Exception as e:
                logger.error(f"Error closing database connection pool: {e}")
                raise
    
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
                
                if tenant_context.user_role:
                    await conn.execute(
                        "SET app.current_user_role = $1",
                        tenant_context.user_role
                    )
                
                # Set role for RLS policies
                await conn.execute("SET ROLE application_role")
                
                yield conn
                
            finally:
                # Reset context
                await conn.execute("RESET app.current_tenant_id")
                await conn.execute("RESET app.current_user_id")
                await conn.execute("RESET app.current_user_role")
                await conn.execute("RESET ROLE")

    @asynccontextmanager
    async def get_admin_connection(self, admin_context: TenantContext):
        """Get a database connection with admin privileges (bypasses some RLS)"""
        if self._pool is None:
            await self.init_pool()
        
        async with self._pool.acquire() as conn:
            try:
                # Set admin context
                await conn.execute(
                    "SET app.current_user_id = $1",
                    admin_context.user_id
                )
                await conn.execute("SET app.current_user_role = 'admin'")
                
                # Set role for RLS policies
                await conn.execute("SET ROLE application_role")
                
                yield conn
                
            finally:
                # Reset context
                await conn.execute("RESET app.current_user_id")
                await conn.execute("RESET app.current_user_role")
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

    async def save_idea(
        self,
        tenant_context: TenantContext,
        idea_data: Dict[str, Any]
    ) -> str:
        """Save a new idea submission"""
        async with self.get_tenant_connection(tenant_context) as conn:
            idea_id = str(uuid.uuid4())
            await conn.execute(
                """
                INSERT INTO ideas (
                    id, tenant_id, submitted_by, project_name, description, problem, 
                    solution, target_audience, key_features, business_model, category,
                    priority, timeline, budget, submission_data
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                """,
                idea_id,
                tenant_context.tenant_id,
                tenant_context.user_id,
                idea_data.get('projectName', ''),
                idea_data.get('description', ''),
                idea_data.get('problem', ''),
                idea_data.get('solution', ''),
                idea_data.get('targetAudience', ''),
                idea_data.get('keyFeatures', ''),
                idea_data.get('businessModel', ''),
                idea_data.get('category', ''),
                idea_data.get('priority', 'medium'),
                idea_data.get('timeline', ''),
                idea_data.get('budget', ''),
                json.dumps(idea_data)
            )
            return idea_id

    async def get_all_ideas(
        self,
        admin_context: TenantContext,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all ideas across tenants (admin only)"""
        async with self.get_admin_connection(admin_context) as conn:
            query = """
                SELECT i.*, 
                       t.name as tenant_name, t.slug as tenant_slug,
                       u.name as submitted_by_name, u.email as submitted_by_email,
                       r.name as reviewed_by_name
                FROM ideas i
                LEFT JOIN tenants t ON i.tenant_id = t.id
                LEFT JOIN users u ON i.submitted_by = u.id
                LEFT JOIN users r ON i.reviewed_by = r.id
                WHERE ($1::text IS NULL OR i.status = $1)
                AND ($2::text IS NULL OR i.priority = $2)
                ORDER BY i.created_at DESC
                LIMIT $3 OFFSET $4
            """
            
            rows = await conn.fetch(query, status, priority, limit, offset)
            return [dict(row) for row in rows]

    async def get_tenant_ideas(
        self,
        tenant_context: TenantContext,
        status: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get ideas for a specific tenant"""
        async with self.get_tenant_connection(tenant_context) as conn:
            query = """
                SELECT i.*, 
                       u.name as submitted_by_name, u.email as submitted_by_email,
                       r.name as reviewed_by_name
                FROM ideas i
                LEFT JOIN users u ON i.submitted_by = u.id
                LEFT JOIN users r ON i.reviewed_by = r.id
                WHERE ($1::text IS NULL OR i.status = $1)
                ORDER BY i.created_at DESC
                LIMIT $2
            """
            rows = await conn.fetch(query, status, limit)
            return [dict(row) for row in rows]

    async def update_idea_status(
        self,
        admin_context: TenantContext,
        idea_id: str,
        status: str,
        admin_notes: Optional[str] = None
    ) -> bool:
        """Update idea status (admin action)"""
        async with self.get_admin_connection(admin_context) as conn:
            result = await conn.execute(
                """
                UPDATE ideas 
                SET status = $2, 
                    reviewed_by = $3,
                    reviewed_at = NOW(),
                    admin_notes = $4,
                    updated_at = NOW()
                WHERE id = $1
                """,
                idea_id,
                status,
                admin_context.user_id,
                admin_notes
            )
            
            # Log admin action
            await self.log_admin_action(
                admin_context,
                action_type='idea_status_update',
                target_type='idea',
                target_id=idea_id,
                action_data={'new_status': status, 'admin_notes': admin_notes}
            )
            
            return int(result.split()[-1]) > 0

    async def promote_idea_to_project(
        self,
        admin_context: TenantContext,
        idea_id: str
    ) -> Optional[str]:
        """Promote an approved idea to a project"""
        async with self.get_admin_connection(admin_context) as conn:
            # Get idea details
            idea_row = await conn.fetchrow(
                "SELECT * FROM ideas WHERE id = $1 AND status = 'approved'",
                idea_id
            )
            
            if not idea_row:
                return None
            
            idea = dict(idea_row)
            
            # Create project from idea
            project_id = str(uuid.uuid4())
            await conn.execute(
                """
                INSERT INTO projects (
                    id, tenant_id, name, description, project_type, 
                    config, created_by
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                project_id,
                idea['tenant_id'],
                idea['project_name'],
                idea['description'],
                'web',  # Default project type
                json.dumps({
                    'problem': idea['problem'],
                    'solution': idea['solution'],
                    'target_audience': idea['target_audience'],
                    'key_features': idea['key_features'],
                    'business_model': idea['business_model'],
                    'category': idea['category'],
                    'priority': idea['priority'],
                    'from_idea_id': idea_id
                }),
                idea['submitted_by']
            )
            
            # Update idea with project link
            await conn.execute(
                """
                UPDATE ideas 
                SET project_id = $2, promoted_at = NOW()
                WHERE id = $1
                """,
                idea_id,
                project_id
            )
            
            # Log admin action
            await self.log_admin_action(
                admin_context,
                action_type='idea_promoted',
                target_type='idea',
                target_id=idea_id,
                action_data={'project_id': project_id}
            )
            
            return project_id

    async def get_all_tenants(
        self,
        admin_context: TenantContext,
        status: Optional[str] = None,
        isolation_mode: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all tenants (admin only)"""
        async with self.get_admin_connection(admin_context) as conn:
            # Temporarily bypass RLS for admin operations
            await conn.execute("SET row_security = off")
            
            try:
                query = """
                    SELECT t.*, 
                           COUNT(u.id) as user_count,
                           COUNT(p.id) as project_count,
                           COUNT(i.id) as idea_count
                    FROM tenants t
                    LEFT JOIN users u ON t.id = u.tenant_id
                    LEFT JOIN projects p ON t.id = p.tenant_id
                    LEFT JOIN ideas i ON t.id = i.tenant_id
                    WHERE ($1::text IS NULL OR t.status = $1)
                    AND ($2::text IS NULL OR t.isolation_mode = $2)
                    GROUP BY t.id
                    ORDER BY t.created_at DESC
                """
                
                rows = await conn.fetch(query, status, isolation_mode)
                return [dict(row) for row in rows]
            finally:
                await conn.execute("SET row_security = on")

    async def update_tenant_isolation(
        self,
        admin_context: TenantContext,
        tenant_id: str,
        isolation_mode: str,
        settings_update: Dict[str, Any] = None
    ) -> bool:
        """Update tenant isolation mode"""
        async with self.get_admin_connection(admin_context) as conn:
            await conn.execute("SET row_security = off")
            
            try:
                if settings_update:
                    result = await conn.execute(
                        """
                        UPDATE tenants 
                        SET isolation_mode = $2,
                            settings = settings || $3::jsonb,
                            updated_at = NOW()
                        WHERE id = $1
                        """,
                        tenant_id,
                        isolation_mode,
                        json.dumps(settings_update)
                    )
                else:
                    result = await conn.execute(
                        """
                        UPDATE tenants 
                        SET isolation_mode = $2,
                            updated_at = NOW()
                        WHERE id = $1
                        """,
                        tenant_id,
                        isolation_mode
                    )
                
                # Log admin action
                await self.log_admin_action(
                    admin_context,
                    action_type='tenant_isolation_update',
                    target_type='tenant',
                    target_id=tenant_id,
                    action_data={'new_isolation_mode': isolation_mode, 'settings': settings_update}
                )
                
                return int(result.split()[-1]) > 0
            finally:
                await conn.execute("SET row_security = on")

    async def log_admin_action(
        self,
        admin_context: TenantContext,
        action_type: str,
        target_type: str,
        target_id: str,
        action_data: Dict[str, Any] = None,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """Log an admin action for audit trail"""
        async with self.get_admin_connection(admin_context) as conn:
            action_id = str(uuid.uuid4())
            await conn.execute(
                """
                INSERT INTO admin_actions (
                    id, admin_user_id, action_type, target_type, target_id,
                    action_data, reason, ip_address, user_agent
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                action_id,
                admin_context.user_id,
                action_type,
                target_type,
                target_id,
                json.dumps(action_data or {}),
                reason,
                ip_address,
                user_agent
            )
            return action_id

    async def get_idea_statistics(self, admin_context: TenantContext) -> Dict[str, Any]:
        """Get idea submission and approval statistics"""
        async with self.get_admin_connection(admin_context) as conn:
            row = await conn.fetchrow("SELECT * FROM idea_statistics")
            return dict(row) if row else {}

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
    user_role = headers.get('x-user-role', 'user')
    
    if tenant_id:
        return TenantContext(tenant_id=tenant_id, user_id=user_id, user_role=user_role)
    
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
def _safe_close_pool():
    try:
        # Try to get existing loop first
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, schedule the cleanup as a task
                asyncio.create_task(tenant_db.close_pool())
                return
        except RuntimeError:
            # No running loop; create a temporary loop to close cleanly
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(tenant_db.close_pool())
        finally:
            if 'loop' in locals():
                loop.close()
    except Exception as e:
        # Silent failure for cleanup - don't crash on exit
        print(f"[INFO] Database cleanup failed: {e}")

atexit.register(_safe_close_pool)