#!/usr/bin/env python3
"""
Privacy Routes for API Gateway
Night 65: Privacy stub with linkable DPA and GDPR checkbox

This module provides:
- GDPR consent management endpoints
- Data export for GDPR compliance
- Data deletion (right to erasure)
- Privacy settings management
"""

import os
import logging
import sys
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Depends, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

from privacy_service import PrivacyService, ConsentRequest, DataExportRequest, get_privacy_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/privacy", tags=["privacy"])

class ConsentUpdateRequest(BaseModel):
    """Request to update user consent"""
    consent_type: str  # 'gdpr', 'terms', 'privacy_policy', 'dpa', 'marketing'
    consent_given: bool

class DataExportRequestModel(BaseModel):
    """Request for data export"""
    include_audit_trail: bool = True
    format: str = "json"

class ConsentStatusResponse(BaseModel):
    """Response for consent status"""
    consent_type: str
    consent_given: bool
    last_updated: Optional[str]

class PrivacyDashboardResponse(BaseModel):
    """Privacy dashboard information"""
    user_id: str
    tenant_id: str
    consents: Dict[str, bool]
    last_data_export: Optional[str]
    data_retention_period: str
    privacy_policy_version: str
    dpa_version: str

@router.post("/consent")
async def update_consent(
    consent_request: ConsentUpdateRequest,
    request: Request,
    user_id: str = Header(..., alias="X-User-ID"),
    tenant_id: str = Header(..., alias="X-Tenant-ID")
):
    """Update user consent for GDPR compliance"""
    try:
        privacy_service = get_privacy_service()
        
        # Get client information for audit trail
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        consent_req = ConsentRequest(
            user_id=user_id,
            consent_type=consent_request.consent_type,
            consent_given=consent_request.consent_given,
            client_ip=client_ip,
            user_agent=user_agent,
            notes=f"Consent {'granted' if consent_request.consent_given else 'withdrawn'} via privacy dashboard"
        )
        
        consent_id = await privacy_service.record_consent(consent_req, tenant_id)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "consent_id": consent_id,
                "message": f"Consent {consent_request.consent_type} {'granted' if consent_request.consent_given else 'withdrawn'} successfully"
            }
        )
        
    except Exception as e:
        logger.error(f"Error updating consent: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update consent"
        )

@router.get("/consent/status")
async def get_consent_status(
    user_id: str = Header(..., alias="X-User-ID"),
    tenant_id: str = Header(..., alias="X-Tenant-ID")
):
    """Get current consent status for user"""
    try:
        privacy_service = get_privacy_service()
        
        # Get consent status for different types
        consent_types = ["gdpr", "terms", "privacy_policy", "dpa", "marketing"]
        consent_status = {}
        
        for consent_type in consent_types:
            status = await privacy_service.check_consent_status(user_id, tenant_id, consent_type)
            consent_status[consent_type] = status if status is not None else False
        
        # Get consent history
        consent_records = await privacy_service.get_user_consents(user_id, tenant_id)
        
        return JSONResponse(
            status_code=200,
            content={
                "user_id": user_id,
                "tenant_id": tenant_id,
                "current_consents": consent_status,
                "consent_history": [
                    {
                        "consent_type": record.consent_type,
                        "consent_given": record.consent_given,
                        "consent_date": record.consent_date.isoformat(),
                        "document_version": record.document_version
                    }
                    for record in consent_records
                ]
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting consent status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get consent status"
        )

@router.post("/export")
async def export_user_data(
    export_request: DataExportRequestModel,
    user_id: str = Header(..., alias="X-User-ID"),
    tenant_id: str = Header(..., alias="X-Tenant-ID")
):
    """Export user data for GDPR compliance"""
    try:
        privacy_service = get_privacy_service()
        
        export_req = DataExportRequest(
            user_id=user_id,
            tenant_id=tenant_id,
            include_audit_trail=export_request.include_audit_trail,
            format=export_request.format
        )
        
        export_data = await privacy_service.export_user_data(export_req)
        
        # For security, don't include sensitive data in the response
        # In a real implementation, this might generate a secure download link
        response_data = {
            "export_id": str(uuid.uuid4()),
            "export_date": export_data["export_date"],
            "export_format": export_data["export_format"],
            "data_summary": {
                "user_profile": "included",
                "consent_history_records": len(export_data.get("consent_history", [])),
                "ideas_submitted": len(export_data.get("ideas_submitted", [])),
                "factory_projects": len(export_data.get("factory_projects", []))
            },
            "download_instructions": "Your data export has been prepared. In a production environment, you would receive a secure download link via email.",
            "data_preview": {
                "user_email": export_data["user_profile"].get("email"),
                "account_created": export_data["user_profile"].get("created_at"),
                "gdpr_consent_status": export_data["user_profile"].get("gdpr_consent_given")
            }
        }
        
        return JSONResponse(
            status_code=200,
            content=response_data
        )
        
    except Exception as e:
        logger.error(f"Error exporting user data: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to export user data"
        )

@router.delete("/delete-account")
async def delete_user_account(
    keep_audit_trail: bool = True,
    user_id: str = Header(..., alias="X-User-ID"),
    tenant_id: str = Header(..., alias="X-Tenant-ID")
):
    """Delete user account and data (GDPR right to erasure)"""
    try:
        privacy_service = get_privacy_service()
        
        deletion_summary = await privacy_service.delete_user_data(
            user_id, tenant_id, keep_audit_trail
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "User account and data have been deleted successfully",
                "deletion_summary": deletion_summary
            }
        )
        
    except Exception as e:
        logger.error(f"Error deleting user account: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete user account"
        )

@router.get("/dashboard")
async def get_privacy_dashboard(
    user_id: str = Header(..., alias="X-User-ID"),
    tenant_id: str = Header(..., alias="X-Tenant-ID")
):
    """Get privacy dashboard information for user"""
    try:
        privacy_service = get_privacy_service()
        
        # Get current consent status
        consent_types = ["gdpr", "terms", "privacy_policy", "dpa", "marketing"]
        consent_status = {}
        
        for consent_type in consent_types:
            status = await privacy_service.check_consent_status(user_id, tenant_id, consent_type)
            consent_status[consent_type] = status if status is not None else False
        
        # Get user's most recent export (mock data for now)
        last_export = None  # Would query export history table in real implementation
        
        dashboard_data = PrivacyDashboardResponse(
            user_id=user_id,
            tenant_id=tenant_id,
            consents=consent_status,
            last_data_export=last_export,
            data_retention_period="30 days after account deletion",
            privacy_policy_version="1.0",
            dpa_version="1.0"
        )
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error getting privacy dashboard: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get privacy dashboard"
        )

@router.get("/policy-versions")
async def get_policy_versions():
    """Get current policy versions"""
    return JSONResponse(
        status_code=200,
        content={
            "privacy_policy": {
                "version": "1.0",
                "effective_date": "2025-01-15",
                "url": "/privacy"
            },
            "dpa": {
                "version": "1.0", 
                "effective_date": "2025-01-15",
                "url": "/dpa"
            },
            "terms_of_service": {
                "version": "1.0",
                "effective_date": "2025-01-15",
                "url": "/terms"
            }
        }
    )

@router.post("/withdraw-consent")
async def withdraw_all_consent(
    request: Request,
    user_id: str = Header(..., alias="X-User-ID"),
    tenant_id: str = Header(..., alias="X-Tenant-ID")
):
    """Withdraw all non-essential consent (GDPR compliance)"""
    try:
        privacy_service = get_privacy_service()
        
        # Get client information for audit trail
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Withdraw non-essential consents (keep essential ones for account operation)
        non_essential_consents = ["marketing"]
        withdrawal_results = []
        
        for consent_type in non_essential_consents:
            consent_req = ConsentRequest(
                user_id=user_id,
                consent_type=consent_type,
                consent_given=False,
                client_ip=client_ip,
                user_agent=user_agent,
                notes="Bulk consent withdrawal requested by user"
            )
            
            consent_id = await privacy_service.record_consent(consent_req, tenant_id)
            withdrawal_results.append({
                "consent_type": consent_type,
                "consent_id": consent_id,
                "withdrawn": True
            })
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Non-essential consents have been withdrawn",
                "withdrawals": withdrawal_results
            }
        )
        
    except Exception as e:
        logger.error(f"Error withdrawing consent: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to withdraw consent"
        ) 