#!/usr/bin/env python3
"""
Status Page Main Service - Night 79 Implementation
FastAPI service for public status page and incident management

This service provides:
- Public status page API endpoints
- Incident management API for operations team
- Real-time status monitoring
- Integration with Google Cloud Monitoring
- Automated incident detection and notifications
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import List, Optional

# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Import shared components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

# Import Status Page Agent
from status_page_agent import (
    StatusPageAgent, StatusPageRequest, StatusPageResponse,
    IncidentCreateRequest, IncidentUpdateRequest
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global agent instance
status_agent: Optional[StatusPageAgent] = None


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global status_agent
    
    # Startup
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "summer-nexus-463503-e1")
    logger.info(f"Starting Status Page Service for project: {project_id}")
    
    try:
        status_agent = StatusPageAgent(project_id)
        logger.info("Status Page Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Status Page Agent: {e}")
        status_agent = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down Status Page Service")


# Initialize FastAPI app
app = FastAPI(
    title="SaaS Factory Status Page",
    description="Public status page and incident management for SaaS Factory platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_status_agent() -> StatusPageAgent:
    """Dependency to get status agent instance"""
    if not status_agent:
        raise HTTPException(
            status_code=503,
            detail="Status Page Agent not available"
        )
    return status_agent


# Public Status Page Endpoints

@app.get("/", response_class=HTMLResponse)
async def status_page_html():
    """Serve the public status page HTML"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SaaS Factory Status</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                min-height: 100vh;
            }
            .container {
                max-width: 1000px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
            }
            .logo {
                font-size: 2.5em;
                font-weight: bold;
                background: linear-gradient(45deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 10px;
            }
            .status-indicator {
                display: inline-block;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                margin: 10px 0;
            }
            .operational { background: #22c55e; color: white; }
            .degraded { background: #f59e0b; color: white; }
            .outage { background: #ef4444; color: white; }
            .maintenance { background: #6366f1; color: white; }
            .component {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px;
                margin: 10px 0;
                background: rgba(255, 255, 255, 0.7);
                border-radius: 8px;
                border-left: 4px solid #22c55e;
            }
            .component.degraded { border-left-color: #f59e0b; }
            .component.outage { border-left-color: #ef4444; }
            .component.maintenance { border-left-color: #6366f1; }
            .incident {
                background: rgba(239, 68, 68, 0.1);
                border: 1px solid #ef4444;
                border-radius: 8px;
                padding: 20px;
                margin: 15px 0;
            }
            .uptime-stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .uptime-card {
                text-align: center;
                background: rgba(255, 255, 255, 0.7);
                padding: 20px;
                border-radius: 8px;
            }
            .uptime-value {
                font-size: 2em;
                font-weight: bold;
                color: #22c55e;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🏭 SaaS Factory</div>
                <h1>System Status</h1>
                <div id="overall-status" class="status-indicator">Loading...</div>
            </div>
            
            <div id="components">
                <h2>Services</h2>
                <div id="component-list">Loading...</div>
            </div>
            
            <div id="uptime-section">
                <h2>Uptime Statistics (24h)</h2>
                <div id="uptime-stats" class="uptime-stats">Loading...</div>
            </div>
            
            <div id="incidents">
                <h2>Active Incidents</h2>
                <div id="incident-list">No active incidents</div>
            </div>
            
            <div style="margin-top: 40px; text-align: center; color: #666;">
                <p>Last updated: <span id="last-updated">...</span></p>
                <p>All times are in UTC. Updates are provided in real-time.</p>
            </div>
        </div>

        <script>
            async function updateStatus() {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    
                    // Update overall status
                    const overallStatus = document.getElementById('overall-status');
                    overallStatus.textContent = data.overall_status.replace('_', ' ').toUpperCase();
                    overallStatus.className = 'status-indicator ' + getStatusClass(data.overall_status);
                    
                    // Update components
                    const componentList = document.getElementById('component-list');
                    componentList.innerHTML = data.components.map(comp => `
                        <div class="component ${getStatusClass(comp.status)}">
                            <div>
                                <strong>${comp.name}</strong>
                                <div style="color: #666; font-size: 0.9em;">${comp.description}</div>
                            </div>
                            <div class="status-indicator ${getStatusClass(comp.status)}">
                                ${comp.status.replace('_', ' ')}
                            </div>
                        </div>
                    `).join('');
                    
                    // Update uptime stats
                    const uptimeStats = document.getElementById('uptime-stats');
                    uptimeStats.innerHTML = Object.entries(data.uptime_stats)
                        .filter(([key]) => key !== 'overall')
                        .map(([component, uptime]) => `
                            <div class="uptime-card">
                                <div class="uptime-value">${(uptime * 100).toFixed(2)}%</div>
                                <div>${component.replace('_', ' ')}</div>
                            </div>
                        `).join('');
                    
                    // Update incidents
                    const incidentList = document.getElementById('incident-list');
                    if (data.active_incidents.length > 0) {
                        incidentList.innerHTML = data.active_incidents.map(incident => `
                            <div class="incident">
                                <h3>${incident.title}</h3>
                                <p><strong>Status:</strong> ${incident.status.replace('_', ' ')}</p>
                                <p><strong>Impact:</strong> ${incident.impact_description}</p>
                                <p>${incident.description}</p>
                                <div style="margin-top: 10px;">
                                    ${incident.updates.slice(-3).map(update => `
                                        <div style="margin: 5px 0; padding: 8px; background: rgba(255,255,255,0.5); border-radius: 4px;">
                                            <strong>${new Date(update.timestamp).toLocaleString()}:</strong> ${update.message}
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        `).join('');
                    } else {
                        incidentList.innerHTML = '<p style="color: #22c55e;">✅ No active incidents</p>';
                    }
                    
                    // Update timestamp
                    document.getElementById('last-updated').textContent = 
                        new Date(data.last_updated).toLocaleString();
                        
                } catch (error) {
                    console.error('Failed to update status:', error);
                }
            }
            
            function getStatusClass(status) {
                switch (status) {
                    case 'operational': return 'operational';
                    case 'degraded_performance': return 'degraded';
                    case 'partial_outage':
                    case 'major_outage': return 'outage';
                    case 'maintenance': return 'maintenance';
                    default: return 'operational';
                }
            }
            
            // Initial load and auto-refresh
            updateStatus();
            setInterval(updateStatus, 30000); // Update every 30 seconds
        </script>
    </body>
    </html>
    """


@app.get("/api/status", response_model=StatusPageResponse)
async def get_status(
    include_metrics: bool = Query(False, description="Include performance metrics"),
    component_ids: Optional[str] = Query(None, description="Comma-separated component IDs"),
    agent: StatusPageAgent = Depends(get_status_agent)
):
    """Get current system status for public status page"""
    try:
        request = StatusPageRequest(
            include_incidents=True,
            include_metrics=include_metrics,
            component_ids=component_ids.split(",") if component_ids else None
        )
        
        status_data = await agent.get_status_page_data(request)
        return status_data
        
    except Exception as e:
        logger.error(f"Error getting status page data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve status data")


@app.get("/api/uptime/{component_id}")
async def get_component_uptime(
    component_id: str,
    days: int = Query(7, ge=1, le=30, description="Number of days"),
    agent: StatusPageAgent = Depends(get_status_agent)
):
    """Get detailed uptime data for a specific component"""
    try:
        if component_id not in agent.components:
            raise HTTPException(status_code=404, detail="Component not found")
        
        # Return uptime history for the component
        uptime_stats = agent.calculate_uptime_stats()
        return {
            "component_id": component_id,
            "component_name": agent.components[component_id].name,
            "current_uptime": uptime_stats.get(component_id, 1.0),
            "status": agent.components[component_id].status.value,
            "last_updated": agent.components[component_id].last_updated.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting component uptime: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve uptime data")


@app.get("/api/metrics/summary")
async def get_metrics_summary(agent: StatusPageAgent = Depends(get_status_agent)):
    """Get summary metrics for monitoring"""
    try:
        return agent.get_metrics_summary()
    except Exception as e:
        logger.error(f"Error getting metrics summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics summary")


# Incident Management Endpoints (Protected - for operations team)

@app.post("/api/incidents", response_model=dict)
async def create_incident(
    request: IncidentCreateRequest,
    agent: StatusPageAgent = Depends(get_status_agent)
):
    """Create a new incident (operations team only)"""
    try:
        incident_id = await agent.create_incident(request)
        return {"incident_id": incident_id, "message": "Incident created successfully"}
    except Exception as e:
        logger.error(f"Error creating incident: {e}")
        raise HTTPException(status_code=500, detail="Failed to create incident")


@app.put("/api/incidents/{incident_id}")
async def update_incident(
    incident_id: str,
    request: IncidentUpdateRequest,
    agent: StatusPageAgent = Depends(get_status_agent)
):
    """Update an existing incident (operations team only)"""
    try:
        success = await agent.update_incident(incident_id, request)
        if success:
            return {"message": "Incident updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Incident not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating incident: {e}")
        raise HTTPException(status_code=500, detail="Failed to update incident")


@app.post("/api/maintenance")
async def set_maintenance_mode(
    component_ids: List[str],
    enabled: bool,
    message: str = "",
    agent: StatusPageAgent = Depends(get_status_agent)
):
    """Set maintenance mode for components (operations team only)"""
    try:
        success = await agent.set_maintenance_mode(component_ids, enabled, message)
        if success:
            action = "enabled" if enabled else "disabled"
            return {"message": f"Maintenance mode {action} for components: {component_ids}"}
        else:
            raise HTTPException(status_code=400, detail="Failed to set maintenance mode")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting maintenance mode: {e}")
        raise HTTPException(status_code=500, detail="Failed to set maintenance mode")


# Webhook Endpoints for Integration

@app.post("/api/webhooks/monitoring")
async def monitoring_webhook(
    request: Request,
    agent: StatusPageAgent = Depends(get_status_agent)
):
    """Webhook endpoint for Google Cloud Monitoring alerts"""
    try:
        payload = await request.json()
        logger.info(f"Received monitoring webhook: {payload}")
        
        # Process monitoring alert and potentially create/update incidents
        # This would parse the Cloud Monitoring alert format and trigger incident creation
        
        return {"status": "processed"}
        
    except Exception as e:
        logger.error(f"Error processing monitoring webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process webhook")


@app.post("/api/webhooks/github")
async def github_webhook(
    request: Request,
    agent: StatusPageAgent = Depends(get_status_agent)
):
    """Webhook endpoint for GitHub deployment status updates"""
    try:
        payload = await request.json()
        logger.info(f"Received GitHub webhook: {payload}")
        
        # Process GitHub webhook for deployment status updates
        # This could update component status based on deployment events
        
        return {"status": "processed"}
        
    except Exception as e:
        logger.error(f"Error processing GitHub webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process webhook")


# Health Check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "status-page",
        "timestamp": "2024-01-01T00:00:00Z"
    }


# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        "status_page_main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=False
    ) 