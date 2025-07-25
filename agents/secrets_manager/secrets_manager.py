"""
SecretsManagerAgent - Core secret rotation and management logic
Handles automatic rotation, scheduling, and multi-cloud secret management
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import sys
import os

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from providers import get_provider, SecretProvider, SecretRotationResult
from tenant_db import TenantDatabase, TenantContext

logger = logging.getLogger(__name__)

class SecretGenerator:
    """Generates new secret values for rotation"""
    
    @staticmethod
    def generate_api_key(length: int = 32) -> str:
        """Generate a new API key"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def generate_token(length: int = 64) -> str:
        """Generate a new token"""
        import secrets
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_password(length: int = 16) -> str:
        """Generate a secure password"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

class SecretsManagerAgent:
    """Main agent for managing secret rotation and scheduling"""
    
    def __init__(self, tenant_context: TenantContext):
        self.tenant_context = tenant_context
        self.tenant_db = TenantDatabase()
        self.providers: Dict[str, SecretProvider] = {}
        self.secret_generator = SecretGenerator()
    
    async def initialize(self):
        """Initialize the agent and database connection"""
        await self.tenant_db.init_pool()
        logger.info(f"SecretsManagerAgent initialized for tenant {self.tenant_context.tenant_id}")
    
    async def add_provider(self, provider_name: str, config: Dict[str, Any]):
        """Add a secret provider (GCP, AWS, Azure)"""
        try:
            provider = get_provider(provider_name, config)
            self.providers[provider_name] = provider
            logger.info(f"Added {provider_name} provider for tenant {self.tenant_context.tenant_id}")
        except Exception as e:
            logger.error(f"Failed to add {provider_name} provider: {e}")
            raise
    
    async def register_secret(
        self,
        secret_name: str,
        provider_name: str,
        secret_type: str,
        rotation_interval_days: int = 30,
        auto_rotation_enabled: bool = True,
        criticality: str = "medium",
        description: Optional[str] = None,
        provider_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Register a secret for rotation tracking"""
        
        if provider_name not in self.providers:
            raise ValueError(f"Provider {provider_name} not configured")
        
        next_rotation_date = datetime.utcnow() + timedelta(days=rotation_interval_days)
        
        async with self.tenant_db.get_tenant_connection(self.tenant_context) as conn:
            query = """
                INSERT INTO secrets_rotation_schedule (
                    tenant_id, secret_name, secret_provider, secret_type,
                    rotation_interval_days, next_rotation_date, auto_rotation_enabled,
                    criticality, description, provider_config, created_by, updated_by
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                RETURNING id
            """
            
            result = await conn.fetchrow(
                query,
                uuid.UUID(self.tenant_context.tenant_id),
                secret_name,
                provider_name,
                secret_type,
                rotation_interval_days,
                next_rotation_date,
                auto_rotation_enabled,
                criticality,
                description,
                provider_config or {},
                uuid.UUID(self.tenant_context.user_id) if self.tenant_context.user_id else None,
                uuid.UUID(self.tenant_context.user_id) if self.tenant_context.user_id else None
            )
            
            schedule_id = str(result['id'])
            logger.info(f"Registered secret {secret_name} for rotation with ID {schedule_id}")
            return schedule_id
    
    async def rotate_secret(
        self,
        secret_name: str,
        new_value: Optional[str] = None,
        rotation_method: str = "automatic"
    ) -> SecretRotationResult:
        """Rotate a single secret"""
        
        # Get secret schedule info
        async with self.tenant_db.get_tenant_connection(self.tenant_context) as conn:
            schedule_query = """
                SELECT id, secret_provider, secret_type, provider_config, criticality
                FROM secrets_rotation_schedule
                WHERE secret_name = $1 AND tenant_id = $2
            """
            schedule = await conn.fetchrow(
                schedule_query,
                secret_name,
                uuid.UUID(self.tenant_context.tenant_id)
            )
            
            if not schedule:
                return SecretRotationResult(
                    success=False,
                    error_message=f"Secret {secret_name} not found in rotation schedule"
                )
            
            provider_name = schedule['secret_provider']
            secret_type = schedule['secret_type']
            
            if provider_name not in self.providers:
                return SecretRotationResult(
                    success=False,
                    error_message=f"Provider {provider_name} not configured"
                )
            
            provider = self.providers[provider_name]
            
            # Generate new value if not provided
            if new_value is None:
                if secret_type == "api_key":
                    new_value = self.secret_generator.generate_api_key()
                elif secret_type == "token":
                    new_value = self.secret_generator.generate_token()
                elif secret_type == "password":
                    new_value = self.secret_generator.generate_password()
                else:
                    return SecretRotationResult(
                        success=False,
                        error_message=f"Unsupported secret type: {secret_type}"
                    )
            
            # Perform rotation via provider
            rotation_result = await provider.update_secret(
                secret_name,
                new_value,
                metadata={
                    "rotated_at": datetime.utcnow().isoformat(),
                    "tenant_id": self.tenant_context.tenant_id,
                    "rotation_method": rotation_method
                }
            )
            
            # Update schedule and create history entry
            if rotation_result.success:
                await self._update_rotation_schedule(conn, schedule['id'], rotation_result)
                await self._create_history_entry(conn, schedule['id'], rotation_result, rotation_method)
                
                logger.info(f"Successfully rotated secret {secret_name}")
            else:
                await self._create_history_entry(
                    conn, schedule['id'], rotation_result, rotation_method, failed=True
                )
                logger.error(f"Failed to rotate secret {secret_name}: {rotation_result.error_message}")
            
            return rotation_result
    
    async def check_due_rotations(self) -> List[Dict[str, Any]]:
        """Check for secrets due for rotation"""
        
        async with self.tenant_db.get_tenant_connection(self.tenant_context) as conn:
            query = """
                SELECT id, secret_name, secret_provider, secret_type, 
                       next_rotation_date, criticality, auto_rotation_enabled
                FROM secrets_rotation_schedule
                WHERE tenant_id = $1 
                  AND auto_rotation_enabled = true
                  AND next_rotation_date <= $2
                ORDER BY criticality DESC, next_rotation_date ASC
            """
            
            due_secrets = await conn.fetch(
                query,
                uuid.UUID(self.tenant_context.tenant_id),
                datetime.utcnow()
            )
            
            return [dict(row) for row in due_secrets]
    
    async def rotate_due_secrets(self) -> Dict[str, Any]:
        """Rotate all secrets that are due for rotation"""
        
        due_secrets = await self.check_due_rotations()
        results = {
            "total": len(due_secrets),
            "successful": 0,
            "failed": 0,
            "results": []
        }
        
        for secret_info in due_secrets:
            secret_name = secret_info['secret_name']
            
            try:
                rotation_result = await self.rotate_secret(secret_name)
                
                if rotation_result.success:
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                
                results["results"].append({
                    "secret_name": secret_name,
                    "success": rotation_result.success,
                    "error": rotation_result.error_message,
                    "duration": rotation_result.duration_seconds
                })
                
            except Exception as e:
                results["failed"] += 1
                results["results"].append({
                    "secret_name": secret_name,
                    "success": False,
                    "error": str(e)
                })
                logger.error(f"Unexpected error rotating {secret_name}: {e}")
        
        logger.info(f"Rotation batch completed: {results['successful']} successful, {results['failed']} failed")
        return results
    
    async def get_rotation_history(
        self,
        secret_name: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get rotation history for secrets"""
        
        async with self.tenant_db.get_tenant_connection(self.tenant_context) as conn:
            if secret_name:
                query = """
                    SELECT h.*, s.secret_name, s.secret_provider
                    FROM secrets_rotation_history h
                    JOIN secrets_rotation_schedule s ON h.schedule_id = s.id
                    WHERE h.tenant_id = $1 AND s.secret_name = $2
                    ORDER BY h.rotation_date DESC
                    LIMIT $3
                """
                history = await conn.fetch(
                    query,
                    uuid.UUID(self.tenant_context.tenant_id),
                    secret_name,
                    limit
                )
            else:
                query = """
                    SELECT h.*, s.secret_name, s.secret_provider
                    FROM secrets_rotation_history h
                    JOIN secrets_rotation_schedule s ON h.schedule_id = s.id
                    WHERE h.tenant_id = $1
                    ORDER BY h.rotation_date DESC
                    LIMIT $2
                """
                history = await conn.fetch(
                    query,
                    uuid.UUID(self.tenant_context.tenant_id),
                    limit
                )
            
            return [dict(row) for row in history]
    
    async def get_secret_schedules(self) -> List[Dict[str, Any]]:
        """Get all secret rotation schedules for the tenant"""
        
        async with self.tenant_db.get_tenant_connection(self.tenant_context) as conn:
            query = """
                SELECT id, secret_name, secret_provider, secret_type,
                       rotation_interval_days, next_rotation_date, auto_rotation_enabled,
                       criticality, description, created_at, updated_at
                FROM secrets_rotation_schedule
                WHERE tenant_id = $1
                ORDER BY next_rotation_date ASC
            """
            
            schedules = await conn.fetch(
                query,
                uuid.UUID(self.tenant_context.tenant_id)
            )
            
            return [dict(row) for row in schedules]
    
    async def update_secret_schedule(
        self,
        secret_name: str,
        rotation_interval_days: Optional[int] = None,
        auto_rotation_enabled: Optional[bool] = None,
        criticality: Optional[str] = None
    ) -> bool:
        """Update a secret's rotation schedule"""
        
        async with self.tenant_db.get_tenant_connection(self.tenant_context) as conn:
            # Build dynamic update query
            updates = []
            params = []
            param_count = 1
            
            if rotation_interval_days is not None:
                updates.append(f"rotation_interval_days = ${param_count}")
                params.append(rotation_interval_days)
                param_count += 1
            
            if auto_rotation_enabled is not None:
                updates.append(f"auto_rotation_enabled = ${param_count}")
                params.append(auto_rotation_enabled)
                param_count += 1
            
            if criticality is not None:
                updates.append(f"criticality = ${param_count}")
                params.append(criticality)
                param_count += 1
            
            if not updates:
                return False
            
            updates.append(f"updated_at = ${param_count}")
            params.append(datetime.utcnow())
            param_count += 1
            
            updates.append(f"updated_by = ${param_count}")
            params.append(uuid.UUID(self.tenant_context.user_id) if self.tenant_context.user_id else None)
            param_count += 1
            
            # Add WHERE conditions
            params.extend([secret_name, uuid.UUID(self.tenant_context.tenant_id)])
            
            query = f"""
                UPDATE secrets_rotation_schedule 
                SET {', '.join(updates)}
                WHERE secret_name = ${param_count - 1} AND tenant_id = ${param_count}
            """
            
            result = await conn.execute(query, *params)
            success = result == "UPDATE 1"
            
            if success:
                logger.info(f"Updated schedule for secret {secret_name}")
            
            return success
    
    async def _update_rotation_schedule(
        self,
        conn,
        schedule_id: uuid.UUID,
        rotation_result: SecretRotationResult
    ):
        """Update the rotation schedule after successful rotation"""
        
        # Calculate next rotation date based on current interval
        query = """
            UPDATE secrets_rotation_schedule
            SET next_rotation_date = CURRENT_TIMESTAMP + (rotation_interval_days || ' days')::interval,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
        """
        
        await conn.execute(query, schedule_id)
    
    async def _create_history_entry(
        self,
        conn,
        schedule_id: uuid.UUID,
        rotation_result: SecretRotationResult,
        rotation_method: str,
        failed: bool = False
    ):
        """Create a history entry for the rotation"""
        
        query = """
            INSERT INTO secrets_rotation_history (
                schedule_id, tenant_id, rotation_status, previous_version,
                new_version, error_message, rotation_method, duration_seconds,
                performed_by
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """
        
        status = "failed" if failed or not rotation_result.success else "success"
        
        await conn.execute(
            query,
            schedule_id,
            uuid.UUID(self.tenant_context.tenant_id),
            status,
            rotation_result.previous_version,
            rotation_result.new_version,
            rotation_result.error_message,
            rotation_method,
            rotation_result.duration_seconds,
            uuid.UUID(self.tenant_context.user_id) if self.tenant_context.user_id else None
        )
    
    async def emergency_rotate(self, secret_name: str, new_value: str) -> SecretRotationResult:
        """Perform emergency rotation of a secret"""
        return await self.rotate_secret(secret_name, new_value, "emergency")
    
    async def close(self):
        """Clean up resources"""
        await self.tenant_db.close_pool()
        logger.info("SecretsManagerAgent closed") 