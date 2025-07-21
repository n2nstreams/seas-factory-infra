#!/usr/bin/env python3
"""
Access Control Module for SaaS Factory
Night 53: Comprehensive access control system with role-based permissions

This module provides:
- Role-based access control (RBAC)
- Multi-tenant isolation
- Admin privilege management
- Session management
- Activity logging
"""

import logging
import json
import uuid
from typing import Optional, Dict, Any, List, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """User roles in the system"""
    ADMIN = "admin"
    TENANT_OWNER = "tenant_owner"
    TENANT_USER = "tenant_user"
    GUEST = "guest"

class Permission(Enum):
    """System permissions"""
    # Admin permissions
    ADMIN_READ_ALL = "admin:read_all"
    ADMIN_WRITE_ALL = "admin:write_all"
    ADMIN_MANAGE_TENANTS = "admin:manage_tenants"
    ADMIN_MANAGE_USERS = "admin:manage_users"
    ADMIN_REVIEW_IDEAS = "admin:review_ideas"
    ADMIN_ISOLATE_TENANTS = "admin:isolate_tenants"
    ADMIN_VIEW_ANALYTICS = "admin:view_analytics"
    
    # Tenant permissions
    TENANT_READ = "tenant:read"
    TENANT_WRITE = "tenant:write"
    TENANT_MANAGE_USERS = "tenant:manage_users"
    TENANT_SUBMIT_IDEAS = "tenant:submit_ideas"
    TENANT_MANAGE_PROJECTS = "tenant:manage_projects"
    
    # Project permissions
    PROJECT_READ = "project:read"
    PROJECT_WRITE = "project:write"
    PROJECT_DELETE = "project:delete"
    
    # Agent permissions
    AGENT_EXECUTE = "agent:execute"
    AGENT_READ_LOGS = "agent:read_logs"

@dataclass
class UserContext:
    """User context for access control"""
    user_id: str
    tenant_id: str
    role: UserRole
    permissions: Set[Permission]
    session_id: Optional[str] = None
    created_at: datetime = None
    last_activity: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.last_activity is None:
            self.last_activity = datetime.utcnow()

class AccessControlManager:
    """Manages access control for the SaaS Factory"""
    
    def __init__(self):
        self.role_permissions = self._initialize_role_permissions()
        self.active_sessions: Dict[str, UserContext] = {}
        self.activity_log: List[Dict[str, Any]] = []
        
    def _initialize_role_permissions(self) -> Dict[UserRole, Set[Permission]]:
        """Initialize default permissions for each role"""
        return {
            UserRole.ADMIN: {
                # Admin has all permissions
                Permission.ADMIN_READ_ALL,
                Permission.ADMIN_WRITE_ALL,
                Permission.ADMIN_MANAGE_TENANTS,
                Permission.ADMIN_MANAGE_USERS,
                Permission.ADMIN_REVIEW_IDEAS,
                Permission.ADMIN_ISOLATE_TENANTS,
                Permission.ADMIN_VIEW_ANALYTICS,
                Permission.TENANT_READ,
                Permission.TENANT_WRITE,
                Permission.TENANT_MANAGE_USERS,
                Permission.TENANT_SUBMIT_IDEAS,
                Permission.TENANT_MANAGE_PROJECTS,
                Permission.PROJECT_READ,
                Permission.PROJECT_WRITE,
                Permission.PROJECT_DELETE,
                Permission.AGENT_EXECUTE,
                Permission.AGENT_READ_LOGS,
            },
            UserRole.TENANT_OWNER: {
                Permission.TENANT_READ,
                Permission.TENANT_WRITE,
                Permission.TENANT_MANAGE_USERS,
                Permission.TENANT_SUBMIT_IDEAS,
                Permission.TENANT_MANAGE_PROJECTS,
                Permission.PROJECT_READ,
                Permission.PROJECT_WRITE,
                Permission.PROJECT_DELETE,
                Permission.AGENT_EXECUTE,
                Permission.AGENT_READ_LOGS,
            },
            UserRole.TENANT_USER: {
                Permission.TENANT_READ,
                Permission.TENANT_SUBMIT_IDEAS,
                Permission.PROJECT_READ,
                Permission.PROJECT_WRITE,
                Permission.AGENT_EXECUTE,
            },
            UserRole.GUEST: {
                Permission.TENANT_SUBMIT_IDEAS,
                Permission.PROJECT_READ,
            }
        }
    
    def create_user_context(
        self,
        user_id: str,
        tenant_id: str,
        role: str,
        session_id: Optional[str] = None
    ) -> UserContext:
        """Create a user context with appropriate permissions"""
        try:
            user_role = UserRole(role.lower())
        except ValueError:
            logger.warning(f"Invalid role '{role}' for user {user_id}, defaulting to GUEST")
            user_role = UserRole.GUEST
            
        permissions = self.role_permissions.get(user_role, set())
        
        context = UserContext(
            user_id=user_id,
            tenant_id=tenant_id,
            role=user_role,
            permissions=permissions,
            session_id=session_id or str(uuid.uuid4())
        )
        
        # Store active session
        if context.session_id:
            self.active_sessions[context.session_id] = context
            
        self._log_activity(
            user_id=user_id,
            tenant_id=tenant_id,
            action="login",
            details={"role": role, "session_id": context.session_id}
        )
        
        return context
    
    def validate_permission(
        self,
        user_context: UserContext,
        required_permission: Permission,
        resource_tenant_id: Optional[str] = None
    ) -> bool:
        """Validate if user has required permission"""
        
        # Admin users have access to everything
        if user_context.role == UserRole.ADMIN:
            return True
            
        # Check if user has the required permission
        if required_permission not in user_context.permissions:
            return False
            
        # For tenant-specific resources, ensure tenant isolation
        if resource_tenant_id and resource_tenant_id != user_context.tenant_id:
            # Only admin can access cross-tenant resources
            return user_context.role == UserRole.ADMIN
            
        return True
    
    def validate_admin_access(self, user_context: UserContext) -> bool:
        """Validate if user has admin access"""
        return user_context.role == UserRole.ADMIN
    
    def validate_idea_review_permission(self, user_context: UserContext) -> bool:
        """Validate if user can review ideas (admin only)"""
        return (
            user_context.role == UserRole.ADMIN and
            Permission.ADMIN_REVIEW_IDEAS in user_context.permissions
        )
    
    def validate_tenant_isolation_permission(self, user_context: UserContext) -> bool:
        """Validate if user can isolate tenants (admin only)"""
        return (
            user_context.role == UserRole.ADMIN and
            Permission.ADMIN_ISOLATE_TENANTS in user_context.permissions
        )
    
    def validate_tenant_management_permission(self, user_context: UserContext) -> bool:
        """Validate if user can manage tenants (admin only)"""
        return (
            user_context.role == UserRole.ADMIN and
            Permission.ADMIN_MANAGE_TENANTS in user_context.permissions
        )
    
    def validate_analytics_permission(self, user_context: UserContext) -> bool:
        """Validate if user can view system analytics (admin only)"""
        return (
            user_context.role == UserRole.ADMIN and
            Permission.ADMIN_VIEW_ANALYTICS in user_context.permissions
        )
    
    def get_session_context(self, session_id: str) -> Optional[UserContext]:
        """Get user context from session ID"""
        context = self.active_sessions.get(session_id)
        if context:
            # Update last activity
            context.last_activity = datetime.utcnow()
        return context
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a user session"""
        if session_id in self.active_sessions:
            context = self.active_sessions[session_id]
            self._log_activity(
                user_id=context.user_id,
                tenant_id=context.tenant_id,
                action="logout",
                details={"session_id": session_id}
            )
            del self.active_sessions[session_id]
            return True
        return False
    
    def cleanup_expired_sessions(self, expiry_hours: int = 24) -> int:
        """Clean up expired sessions"""
        cutoff_time = datetime.utcnow() - timedelta(hours=expiry_hours)
        expired_sessions = [
            session_id for session_id, context in self.active_sessions.items()
            if context.last_activity < cutoff_time
        ]
        
        for session_id in expired_sessions:
            self.invalidate_session(session_id)
            
        return len(expired_sessions)
    
    def _log_activity(
        self,
        user_id: str,
        tenant_id: str,
        action: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log user activity"""
        activity = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "tenant_id": tenant_id,
            "action": action,
            "details": details or {}
        }
        
        self.activity_log.append(activity)
        
        # Keep only last 10000 entries to prevent memory issues
        if len(self.activity_log) > 10000:
            self.activity_log = self.activity_log[-10000:]
            
        logger.info(f"Activity logged: {json.dumps(activity)}")
    
    def get_user_permissions(self, user_context: UserContext) -> List[str]:
        """Get list of user permissions as strings"""
        return [perm.value for perm in user_context.permissions]
    
    def has_tenant_access(
        self,
        user_context: UserContext,
        target_tenant_id: str
    ) -> bool:
        """Check if user has access to specific tenant"""
        # Admin can access any tenant
        if user_context.role == UserRole.ADMIN:
            return True
            
        # Users can only access their own tenant
        return user_context.tenant_id == target_tenant_id
    
    def create_admin_context(
        self,
        admin_user_id: str = "system-admin",
        session_id: Optional[str] = None
    ) -> UserContext:
        """Create an admin context for system operations"""
        return self.create_user_context(
            user_id=admin_user_id,
            tenant_id="admin",
            role="admin",
            session_id=session_id
        )
    
    def get_activity_log(
        self,
        user_context: UserContext,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get activity log (admin only)"""
        if not self.validate_admin_access(user_context):
            return []
            
        return self.activity_log[-limit:]

# Global access control manager instance
access_control = AccessControlManager()

def require_permission(permission: Permission):
    """Decorator to require specific permission"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract user context from kwargs or args
            user_context = kwargs.get('user_context') or args[0] if args else None
            
            if not isinstance(user_context, UserContext):
                raise ValueError("User context required for permission check")
                
            if not access_control.validate_permission(user_context, permission):
                raise PermissionError(f"Permission {permission.value} required")
                
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_admin():
    """Decorator to require admin access"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract user context from kwargs or args
            user_context = kwargs.get('user_context') or args[0] if args else None
            
            if not isinstance(user_context, UserContext):
                raise ValueError("User context required for admin check")
                
            if not access_control.validate_admin_access(user_context):
                raise PermissionError("Admin access required")
                
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_tenant_isolation(user_context: UserContext, tenant_id: str) -> bool:
    """Validate tenant isolation - users can only access their tenant unless admin"""
    return access_control.has_tenant_access(user_context, tenant_id)

def create_user_context_from_headers(
    headers: Dict[str, str]
) -> Optional[UserContext]:
    """Create user context from HTTP headers"""
    user_id = headers.get('x-user-id')
    tenant_id = headers.get('x-tenant-id')
    user_role = headers.get('x-user-role', 'guest')
    session_id = headers.get('x-session-id')
    
    if not user_id or not tenant_id:
        return None
        
    return access_control.create_user_context(
        user_id=user_id,
        tenant_id=tenant_id,
        role=user_role,
        session_id=session_id
    )

# Export commonly used functions
__all__ = [
    'UserRole',
    'Permission', 
    'UserContext',
    'AccessControlManager',
    'access_control',
    'require_permission',
    'require_admin',
    'validate_tenant_isolation',
    'create_user_context_from_headers'
] 