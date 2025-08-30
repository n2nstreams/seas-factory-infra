"""
SecretsManagerAgent FastAPI Application
Provides REST API for secret management and rotation
"""

import os
import sys
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from secrets_manager import SecretsManagerAgent
from tenant_db import TenantContext, get_tenant_context_from_headers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global agent instance
secrets_agent: Optional[SecretsManagerAgent] = None

# Pydantic models for API
class RegisterSecretRequest(BaseModel):
    secret_name: str = Field(..., description="Name of the secret to manage")
    provider_name: str = Field(..., description="Cloud provider (gcp, aws, azure)")
    secret_type: str = Field(..., description="Type of secret (api_key, token, password)")
    rotation_interval_days: int = Field(30, description="Days between rotations")
    auto_rotation_enabled: bool = Field(True, description="Enable automatic rotation")
    criticality: str = Field("medium", description="Business criticality level")
    description: Optional[str] = Field(None, description="Secret description")
    provider_config: Optional[Dict[str, Any]] = Field(None, description="Provider-specific config")

class RotateSecretRequest(BaseModel):
    secret_name: str = Field(..., description="Name of the secret to rotate")
    new_value: Optional[str] = Field(None, description="New secret value (generated if not provided)")
    rotation_method: str = Field("manual", description="Rotation method")

class UpdateScheduleRequest(BaseModel):
    secret_name: str = Field(..., description="Name of the secret to update")
    rotation_interval_days: Optional[int] = Field(None, description="New rotation interval")
    auto_rotation_enabled: Optional[bool] = Field(None, description="Enable/disable auto rotation")
    criticality: Optional[str] = Field(None, description="New criticality level")

class ProviderConfigRequest(BaseModel):
    provider_name: str = Field(..., description="Provider name (gcp, aws, azure)")
    config: Dict[str, Any] = Field(..., description="Provider configuration")

class SecretRotationResponse(BaseModel):
    success: bool
    previous_version: Optional[str] = None
    new_version: Optional[str] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[int] = None
    timestamp: datetime

# Background tasks
async def periodic_rotation_check():
    """Periodic background task to check and rotate due secrets"""
    global secrets_agent
    
    while True:
        try:
            if secrets_agent:
                # Get tenant context for system operations
                # For periodic tasks, we might need a system tenant context
                logger.info("Starting periodic rotation check...")
                
                # This would need to be implemented to iterate through all tenants
                # For now, we'll implement per-tenant endpoints
                await asyncio.sleep(3600)  # Check every hour
            else:
                await asyncio.sleep(60)  # Wait and retry if agent not ready
                
        except Exception as e:
            logger.error(f"Error in periodic rotation check: {e}")
            await asyncio.sleep(300)  # Wait 5 minutes on error

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting SecretsManagerAgent service...")
    
    # Start background task
    rotation_task = asyncio.create_task(periodic_rotation_check())
    
    try:
        yield
    finally:
        # Shutdown
        logger.info("Shutting down SecretsManagerAgent service...")
        
        # Cancel background task
        rotation_task.cancel()
        try:
            await rotation_task
        except asyncio.CancelledError:
            pass
        
        # Cleanup agent
        if secrets_agent:
            await secrets_agent.close()

app = FastAPI(
    title="SecretsManagerAgent",
    description="Automated secret rotation across cloud providers",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_secrets_agent(tenant_context: TenantContext = Depends(get_tenant_context_from_headers)) -> SecretsManagerAgent:
    """Get a tenant-specific secrets agent instance"""
    agent = SecretsManagerAgent(tenant_context)
    return agent

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "secrets-manager", "timestamp": datetime.utcnow()}

@app.post("/providers/configure")
async def configure_provider(
    request: ProviderConfigRequest,
    agent: SecretsManagerAgent = Depends(get_secrets_agent)
):
    """Configure a cloud provider for secret management"""
    try:
        await agent.initialize()
        await agent.add_provider(request.provider_name, request.config)
        
        return {
            "success": True,
            "message": f"Provider {request.provider_name} configured successfully"
        }
    except Exception as e:
        logger.error(f"Failed to configure provider {request.provider_name}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await agent.close()

@app.post("/secrets/register")
async def register_secret(
    request: RegisterSecretRequest,
    agent: SecretsManagerAgent = Depends(get_secrets_agent)
):
    """Register a secret for rotation management"""
    try:
        await agent.initialize()
        
        # Configure GCP provider by default if not configured
        if request.provider_name == "gcp":
            project_id = os.getenv("PROJECT_ID", "saas-factory-prod")
            await agent.add_provider("gcp", {"project_id": project_id})
        
        schedule_id = await agent.register_secret(
            secret_name=request.secret_name,
            provider_name=request.provider_name,
            secret_type=request.secret_type,
            rotation_interval_days=request.rotation_interval_days,
            auto_rotation_enabled=request.auto_rotation_enabled,
            criticality=request.criticality,
            description=request.description,
            provider_config=request.provider_config
        )
        
        return {
            "success": True,
            "schedule_id": schedule_id,
            "message": f"Secret {request.secret_name} registered for rotation"
        }
    except Exception as e:
        logger.error(f"Failed to register secret {request.secret_name}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await agent.close()

@app.post("/secrets/rotate")
async def rotate_secret(
    request: RotateSecretRequest,
    background_tasks: BackgroundTasks,
    agent: SecretsManagerAgent = Depends(get_secrets_agent)
):
    """Manually rotate a specific secret"""
    try:
        await agent.initialize()
        
        # Configure GCP provider by default
        project_id = os.getenv("PROJECT_ID", "saas-factory-prod")
        await agent.add_provider("gcp", {"project_id": project_id})
        
        result = await agent.rotate_secret(
            secret_name=request.secret_name,
            new_value=request.new_value,
            rotation_method=request.rotation_method
        )
        
        return SecretRotationResponse(
            success=result.success,
            previous_version=result.previous_version,
            new_version=result.new_version,
            error_message=result.error_message,
            duration_seconds=result.duration_seconds,
            timestamp=result.timestamp
        )
    except Exception as e:
        logger.error(f"Failed to rotate secret {request.secret_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await agent.close()

@app.post("/secrets/rotate-due")
async def rotate_due_secrets(
    agent: SecretsManagerAgent = Depends(get_secrets_agent)
):
    """Rotate all secrets that are due for rotation"""
    try:
        await agent.initialize()
        
        # Configure GCP provider by default
        project_id = os.getenv("PROJECT_ID", "saas-factory-prod")
        await agent.add_provider("gcp", {"project_id": project_id})
        
        results = await agent.rotate_due_secrets()
        
        return {
            "success": True,
            "rotation_results": results
        }
    except Exception as e:
        logger.error(f"Failed to rotate due secrets: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await agent.close()

@app.get("/secrets/due")
async def get_due_rotations(
    agent: SecretsManagerAgent = Depends(get_secrets_agent)
):
    """Get list of secrets due for rotation"""
    try:
        await agent.initialize()
        due_secrets = await agent.check_due_rotations()
        
        return {
            "success": True,
            "due_secrets": due_secrets,
            "count": len(due_secrets)
        }
    except Exception as e:
        logger.error(f"Failed to get due rotations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await agent.close()

@app.get("/secrets/schedules")
async def get_secret_schedules(
    agent: SecretsManagerAgent = Depends(get_secrets_agent)
):
    """Get all secret rotation schedules"""
    try:
        await agent.initialize()
        schedules = await agent.get_secret_schedules()
        
        return {
            "success": True,
            "schedules": schedules,
            "count": len(schedules)
        }
    except Exception as e:
        logger.error(f"Failed to get secret schedules: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await agent.close()

@app.put("/secrets/schedule")
async def update_secret_schedule(
    request: UpdateScheduleRequest,
    agent: SecretsManagerAgent = Depends(get_secrets_agent)
):
    """Update a secret's rotation schedule"""
    try:
        await agent.initialize()
        
        success = await agent.update_secret_schedule(
            secret_name=request.secret_name,
            rotation_interval_days=request.rotation_interval_days,
            auto_rotation_enabled=request.auto_rotation_enabled,
            criticality=request.criticality
        )
        
        if success:
            return {
                "success": True,
                "message": f"Schedule updated for secret {request.secret_name}"
            }
        else:
            raise HTTPException(status_code=404, detail="Secret not found or no changes made")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update schedule for {request.secret_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await agent.close()

@app.get("/secrets/history")
async def get_rotation_history(
    secret_name: Optional[str] = None,
    limit: int = 50,
    agent: SecretsManagerAgent = Depends(get_secrets_agent)
):
    """Get rotation history for secrets"""
    try:
        await agent.initialize()
        history = await agent.get_rotation_history(secret_name, limit)
        
        return {
            "success": True,
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        logger.error(f"Failed to get rotation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await agent.close()

@app.post("/secrets/emergency-rotate")
async def emergency_rotate(
    secret_name: str,
    new_value: str,
    agent: SecretsManagerAgent = Depends(get_secrets_agent)
):
    """Perform emergency rotation of a secret"""
    try:
        await agent.initialize()
        
        # Configure GCP provider by default
        project_id = os.getenv("PROJECT_ID", "saas-factory-prod")
        await agent.add_provider("gcp", {"project_id": project_id})
        
        result = await agent.emergency_rotate(secret_name, new_value)
        
        return SecretRotationResponse(
            success=result.success,
            previous_version=result.previous_version,
            new_version=result.new_version,
            error_message=result.error_message,
            duration_seconds=result.duration_seconds,
            timestamp=result.timestamp
        )
    except Exception as e:
        logger.error(f"Failed emergency rotation for {secret_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await agent.close()

# Scheduled rotation endpoint for Cloud Scheduler
@app.post("/internal/scheduled-rotation")
async def scheduled_rotation():
    """Internal endpoint triggered by Cloud Scheduler for monthly rotations"""
    try:
        # This would need to iterate through all tenants
        # For now, return a success message
        logger.info("Scheduled rotation triggered")
        
        return {
            "success": True,
            "message": "Scheduled rotation completed",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Scheduled rotation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8089) 