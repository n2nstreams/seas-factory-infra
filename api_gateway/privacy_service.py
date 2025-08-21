#!/usr/bin/env python3
"""
Privacy Service for GDPR Compliance
Night 65: Privacy stub with linkable DPA and GDPR checkbox

This module provides:
- GDPR consent management
- Data subject rights (access, deletion, portability)
- Privacy consent audit trail
- Data export for compliance
"""

import os
import logging
import sys
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

import asyncpg
from pydantic import BaseModel, EmailStr

# Add shared modules to path
sys.path.append(os.path.dirname(__file__))
from tenant_db import TenantDatabase, TenantContext

logger = logging.getLogger(__name__)

class ConsentRequest(BaseModel):
    """Model for consent requests"""
    user_id: str
    consent_type: str  # 'gdpr', 'terms', 'privacy_policy', 'dpa', 'marketing'
    consent_given: bool
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    notes: Optional[str] = None

class DataExportRequest(BaseModel):
    """Model for data export requests"""
    user_id: str
    tenant_id: str
    include_audit_trail: bool = True
    format: str = "json"  # json, csv

class ConsentRecord(BaseModel):
    """Model for consent records"""
    id: str
    user_id: str
    tenant_id: str
    consent_type: str
    consent_given: bool
    consent_date: datetime
    consent_ip: Optional[str]
    document_version: Optional[str]
    user_agent: Optional[str]
    notes: Optional[str]

class PrivacyService:
    """Service for handling GDPR and privacy compliance operations"""
    
    def __init__(self):
        self.tenant_db = TenantDatabase()
    
    async def record_consent(self, consent_request: ConsentRequest, tenant_id: str) -> str:
        """Record a consent or consent withdrawal"""
        try:
            await self.tenant_db.init_pool()
            
            async with self.tenant_db.get_tenant_connection(TenantContext(tenant_id)) as conn:
                consent_id = str(uuid.uuid4())
                now = datetime.utcnow()
                
                # Insert consent audit record
                await conn.execute(
                    """
                    INSERT INTO privacy_consent_audit (
                        id, user_id, tenant_id, consent_type, consent_given, consent_date,
                        consent_ip, document_version, user_agent, notes, created_at
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    """,
                    consent_id,
                    consent_request.user_id,
                    tenant_id,
                    consent_request.consent_type,
                    consent_request.consent_given,
                    now,
                    consent_request.client_ip,
                    "1.0",  # Current document version
                    consent_request.user_agent,
                    consent_request.notes,
                    now
                )
                
                # Update user record if it's GDPR consent
                if consent_request.consent_type == "gdpr":
                    await conn.execute(
                        """
                        UPDATE users 
                        SET gdpr_consent_given = $1, 
                            gdpr_consent_date = $2,
                            gdpr_consent_ip = $3,
                            updated_at = $4
                        WHERE id = $5 AND tenant_id = $6
                        """,
                        consent_request.consent_given,
                        now if consent_request.consent_given else None,
                        consent_request.client_ip if consent_request.consent_given else None,
                        now,
                        consent_request.user_id,
                        tenant_id
                    )
                
                logger.info(f"Consent recorded: {consent_request.consent_type} = {consent_request.consent_given} for user {consent_request.user_id}")
                return consent_id
                
        except Exception as e:
            logger.error(f"Error recording consent: {e}")
            raise
    
    async def get_user_consents(self, user_id: str, tenant_id: str) -> List[ConsentRecord]:
        """Get all consent records for a user"""
        try:
            await self.tenant_db.init_pool()
            
            async with self.tenant_db.get_tenant_connection(TenantContext(tenant_id)) as conn:
                records = await conn.fetch(
                    """
                    SELECT * FROM privacy_consent_audit 
                    WHERE user_id = $1 AND tenant_id = $2
                    ORDER BY consent_date DESC
                    """,
                    user_id, tenant_id
                )
                
                return [
                    ConsentRecord(
                        id=str(record['id']),
                        user_id=str(record['user_id']),
                        tenant_id=str(record['tenant_id']),
                        consent_type=record['consent_type'],
                        consent_given=record['consent_given'],
                        consent_date=record['consent_date'],
                        consent_ip=record['consent_ip'],
                        document_version=record['document_version'],
                        user_agent=record['user_agent'],
                        notes=record['notes']
                    )
                    for record in records
                ]
                
        except Exception as e:
            logger.error(f"Error getting user consents: {e}")
            raise
    
    async def export_user_data(self, export_request: DataExportRequest) -> Dict[str, Any]:
        """Export all user data for GDPR compliance"""
        try:
            await self.tenant_db.init_pool()
            
            async with self.tenant_db.get_tenant_connection(TenantContext(export_request.tenant_id)) as conn:
                # Get user profile data
                user_data = await conn.fetchrow(
                    """
                    SELECT id, tenant_id, email, name, role, status, created_at, updated_at,
                           last_login_at, gdpr_consent_given, gdpr_consent_date, gdpr_consent_ip,
                           privacy_policy_version, dpa_version
                    FROM users 
                    WHERE id = $1 AND tenant_id = $2
                    """,
                    export_request.user_id, export_request.tenant_id
                )
                
                if not user_data:
                    raise ValueError("User not found")
                
                export_data = {
                    "export_date": datetime.utcnow().isoformat(),
                    "export_format": export_request.format,
                    "user_profile": dict(user_data) if user_data else {},
                    "consent_history": [],
                    "ideas_submitted": [],
                    "factory_projects": []
                }
                
                # Convert datetime objects to ISO strings for JSON serialization
                if export_data["user_profile"]:
                    for key, value in export_data["user_profile"].items():
                        if isinstance(value, datetime):
                            export_data["user_profile"][key] = value.isoformat()
                
                # Get consent history if requested
                if export_request.include_audit_trail:
                    consent_records = await self.get_user_consents(
                        export_request.user_id, 
                        export_request.tenant_id
                    )
                    export_data["consent_history"] = [
                        {
                            "consent_type": record.consent_type,
                            "consent_given": record.consent_given,
                            "consent_date": record.consent_date.isoformat(),
                            "document_version": record.document_version,
                            "notes": record.notes
                        }
                        for record in consent_records
                    ]
                
                # Get user's submitted ideas (if table exists)
                try:
                    ideas = await conn.fetch(
                        """
                        SELECT id, title, description, status, created_at, updated_at
                        FROM ideas 
                        WHERE user_id = $1 AND tenant_id = $2
                        """,
                        export_request.user_id, export_request.tenant_id
                    )
                    
                    export_data["ideas_submitted"] = [
                        {
                            "id": str(idea['id']),
                            "title": idea['title'],
                            "description": idea['description'],
                            "status": idea['status'],
                            "created_at": idea['created_at'].isoformat() if idea['created_at'] else None,
                            "updated_at": idea['updated_at'].isoformat() if idea['updated_at'] else None
                        }
                        for idea in ideas
                    ]
                except Exception:
                    # Table might not exist yet
                    pass
                
                # Get factory pipeline data (if table exists)
                try:
                    pipelines = await conn.fetch(
                        """
                        SELECT id, pipeline_name, status, created_at, updated_at
                        FROM factory_pipelines 
                        WHERE user_id = $1 AND tenant_id = $2
                        """,
                        export_request.user_id, export_request.tenant_id
                    )
                    
                    export_data["factory_projects"] = [
                        {
                            "id": str(pipeline['id']),
                            "pipeline_name": pipeline['pipeline_name'],
                            "status": pipeline['status'],
                            "created_at": pipeline['created_at'].isoformat() if pipeline['created_at'] else None,
                            "updated_at": pipeline['updated_at'].isoformat() if pipeline['updated_at'] else None
                        }
                        for pipeline in pipelines
                    ]
                except Exception:
                    # Table might not exist yet
                    pass
                
                logger.info(f"Data export completed for user {export_request.user_id}")
                return export_data
                
        except Exception as e:
            logger.error(f"Error exporting user data: {e}")
            raise
    
    async def delete_user_data(self, user_id: str, tenant_id: str, keep_audit_trail: bool = True) -> Dict[str, Any]:
        """Delete user data (GDPR right to erasure)"""
        try:
            await self.tenant_db.init_pool()
            
            async with self.tenant_db.get_tenant_connection(TenantContext(tenant_id)) as conn:
                deletion_summary = {
                    "deletion_date": datetime.utcnow().isoformat(),
                    "user_id": user_id,
                    "tenant_id": tenant_id,
                    "keep_audit_trail": keep_audit_trail,
                    "deleted_records": {}
                }
                
                # Start transaction
                async with conn.transaction():
                    # Delete from related tables first (foreign key constraints)
                    
                    # Delete ideas
                    try:
                        deleted_ideas = await conn.fetchval(
                            "DELETE FROM ideas WHERE user_id = $1 AND tenant_id = $2 RETURNING COUNT(*)",
                            user_id, tenant_id
                        )
                        deletion_summary["deleted_records"]["ideas"] = deleted_ideas or 0
                    except Exception:
                        deletion_summary["deleted_records"]["ideas"] = 0
                    
                    # Delete factory pipelines
                    try:
                        deleted_pipelines = await conn.fetchval(
                            "DELETE FROM factory_pipelines WHERE user_id = $1 AND tenant_id = $2 RETURNING COUNT(*)",
                            user_id, tenant_id
                        )
                        deletion_summary["deleted_records"]["factory_pipelines"] = deleted_pipelines or 0
                    except Exception:
                        deletion_summary["deleted_records"]["factory_pipelines"] = 0
                    
                    # Delete consent audit trail (if not keeping it for legal reasons)
                    if not keep_audit_trail:
                        deleted_consents = await conn.fetchval(
                            "DELETE FROM privacy_consent_audit WHERE user_id = $1 AND tenant_id = $2 RETURNING COUNT(*)",
                            user_id, tenant_id
                        )
                        deletion_summary["deleted_records"]["consent_audit"] = deleted_consents or 0
                    else:
                        # Anonymize consent records instead of deleting
                        await conn.execute(
                            """
                            UPDATE privacy_consent_audit 
                            SET consent_ip = 'ANONYMIZED', 
                                user_agent = 'ANONYMIZED',
                                notes = COALESCE(notes, '') || ' - User data deleted on ' || $3
                            WHERE user_id = $1 AND tenant_id = $2
                            """,
                            user_id, tenant_id, datetime.utcnow().isoformat()
                        )
                        deletion_summary["deleted_records"]["consent_audit"] = "anonymized"
                    
                    # Finally delete the user record
                    deleted_user = await conn.fetchval(
                        "DELETE FROM users WHERE id = $1 AND tenant_id = $2 RETURNING COUNT(*)",
                        user_id, tenant_id
                    )
                    deletion_summary["deleted_records"]["users"] = deleted_user or 0
                
                logger.info(f"User data deletion completed for user {user_id}")
                return deletion_summary
                
        except Exception as e:
            logger.error(f"Error deleting user data: {e}")
            raise
    
    async def check_consent_status(self, user_id: str, tenant_id: str, consent_type: str = "gdpr") -> Optional[bool]:
        """Check current consent status for a user"""
        try:
            await self.tenant_db.init_pool()
            
            async with self.tenant_db.get_tenant_connection(TenantContext(tenant_id)) as conn:
                # Get the most recent consent record
                consent_record = await conn.fetchrow(
                    """
                    SELECT consent_given FROM privacy_consent_audit 
                    WHERE user_id = $1 AND tenant_id = $2 AND consent_type = $3
                    ORDER BY consent_date DESC
                    LIMIT 1
                    """,
                    user_id, tenant_id, consent_type
                )
                
                return consent_record['consent_given'] if consent_record else None
                
        except Exception as e:
            logger.error(f"Error checking consent status: {e}")
            raise

# Global privacy service instance
privacy_service = PrivacyService()

def get_privacy_service() -> PrivacyService:
    """Get the global privacy service instance"""
    return privacy_service 