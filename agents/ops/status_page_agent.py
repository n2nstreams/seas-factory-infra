"""
Status Page Agent - Night 79 Implementation
Manages public status page and incident communications for SaaS Factory

This agent implements:
- Real-time status monitoring integration with Google Cloud Monitoring
- Automated incident detection and status page updates
- Public status page API for transparency
- Integration with existing alert systems
- Incident communication management
"""

import asyncio
import json
import logging
import os
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, AsyncGenerator
import uuid

# FastAPI imports
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Google Cloud imports
try:
    from google.cloud import monitoring_v3
    from google.cloud import logging as cloud_logging
    from google.cloud import secretmanager
    import vertexai
    from vertexai.generative_models import GenerativeModel
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    logging.warning("Google Cloud libraries not available")

# Import shared components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from tenant_db import TenantDatabase, TenantContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status levels"""
    OPERATIONAL = "operational"
    DEGRADED_PERFORMANCE = "degraded_performance"
    PARTIAL_OUTAGE = "partial_outage"
    MAJOR_OUTAGE = "major_outage"
    MAINTENANCE = "maintenance"


class IncidentSeverity(Enum):
    """Incident severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(Enum):
    """Incident status tracking"""
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"
    POSTMORTEM = "postmortem"


@dataclass
class ServiceComponent:
    """Represents a monitored service component"""
    id: str
    name: str
    description: str
    status: ServiceStatus = ServiceStatus.OPERATIONAL
    uptime_check_ids: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    performance_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class Incident:
    """Represents an active or historical incident"""
    id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    affected_components: List[str]
    created_at: datetime
    resolved_at: Optional[datetime] = None
    updates: List[Dict[str, Any]] = field(default_factory=list)
    impact_description: str = ""
    root_cause: Optional[str] = None
    postmortem_url: Optional[str] = None


class StatusPageRequest(BaseModel):
    """Request model for status page data"""
    include_incidents: bool = True
    include_metrics: bool = False
    component_ids: Optional[List[str]] = None


class IncidentCreateRequest(BaseModel):
    """Request model for creating an incident"""
    title: str
    description: str
    severity: IncidentSeverity
    affected_components: List[str]
    impact_description: str = ""


class IncidentUpdateRequest(BaseModel):
    """Request model for updating an incident"""
    status: Optional[IncidentStatus] = None
    update_message: str
    resolved: bool = False


class StatusPageResponse(BaseModel):
    """Response model for status page data"""
    overall_status: ServiceStatus
    components: List[Dict[str, Any]]
    active_incidents: List[Dict[str, Any]]
    recent_incidents: List[Dict[str, Any]]
    uptime_stats: Dict[str, float]
    last_updated: datetime


class StatusPageAgent:
    """
    Status Page Agent - Manages public status page and incident communications
    """
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize Google Cloud clients
        if GOOGLE_CLOUD_AVAILABLE:
            self.monitoring_client = monitoring_v3.MetricServiceClient()
            self.logging_client = cloud_logging.Client(project=project_id)
            self.secret_client = secretmanager.SecretManagerServiceClient()
            
            # Initialize Vertex AI for incident analysis
            vertexai.init(project=project_id, location="us-central1")
            self.ai_model = GenerativeModel("gemini-1.5-pro-002")
        else:
            self.monitoring_client = None
            self.logging_client = None
            self.secret_client = None
            self.ai_model = None
        
        # Internal state
        self.tenant_db = TenantDatabase()
        self.components: Dict[str, ServiceComponent] = {}
        self.incidents: Dict[str, Incident] = {}
        self.uptime_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1440))  # 24h of minutes
        
        # Configuration
        self.status_check_interval = 60  # seconds
        self.uptime_threshold = 0.999  # 99.9% SLA target
        self.performance_degradation_threshold = 2.0  # 2x normal response time
        
        # Initialize default components
        self._initialize_components()
        
        # Start background monitoring
        if GOOGLE_CLOUD_AVAILABLE:
            asyncio.create_task(self._start_status_monitoring())
    
    def _initialize_components(self):
        """Initialize monitored service components"""
        components_config = [
            {
                "id": "orchestrator",
                "name": "Project Orchestrator",
                "description": "AI project orchestration service",
                "uptime_check_ids": ["orchestrator-health-check"]
            },
            {
                "id": "api_gateway",
                "name": "API Gateway",
                "description": "Main API gateway service",
                "uptime_check_ids": ["gateway-health-check"]
            },
            {
                "id": "frontend",
                "name": "Web Dashboard",
                "description": "User interface and dashboard",
                "uptime_check_ids": ["frontend-health-check"]
            },
            {
                "id": "event_relay",
                "name": "Event Relay",
                "description": "Event processing and notifications",
                "uptime_check_ids": ["event-relay-health-check"]
            },
            {
                "id": "database",
                "name": "Database",
                "description": "Cloud SQL database services",
                "uptime_check_ids": []
            },
            {
                "id": "agents",
                "name": "AI Agents",
                "description": "Worker agent services",
                "uptime_check_ids": []
            }
        ]
        
        for config in components_config:
            component = ServiceComponent(**config)
            self.components[component.id] = component
            self.logger.info(f"Initialized component: {component.name}")
    
    async def _start_status_monitoring(self):
        """Start background status monitoring loop"""
        self.logger.info("Starting status monitoring loop")
        
        while True:
            try:
                await self._check_component_status()
                await self._update_uptime_metrics()
                await self._detect_incidents()
                await asyncio.sleep(self.status_check_interval)
            except Exception as e:
                self.logger.error(f"Error in status monitoring loop: {e}")
                await asyncio.sleep(30)  # Shorter retry interval on error
    
    async def _check_component_status(self):
        """Check status of all monitored components"""
        if not self.monitoring_client:
            return
        
        project_name = f"projects/{self.project_id}"
        
        for component_id, component in self.components.items():
            try:
                # Check uptime checks
                is_up = await self._check_uptime_status(component)
                
                # Check performance metrics
                performance = await self._check_performance_metrics(component)
                component.performance_metrics = performance
                
                # Determine component status
                new_status = self._determine_component_status(is_up, performance)
                
                if new_status != component.status:
                    self.logger.info(f"Component {component.name} status changed: {component.status.value} -> {new_status.value}")
                    component.status = new_status
                    component.last_updated = datetime.utcnow()
                    
                    # Auto-create incidents for major status changes
                    if new_status in [ServiceStatus.PARTIAL_OUTAGE, ServiceStatus.MAJOR_OUTAGE]:
                        await self._auto_create_incident(component, new_status)
                
            except Exception as e:
                self.logger.error(f"Error checking status for component {component.name}: {e}")
                component.status = ServiceStatus.PARTIAL_OUTAGE
                component.last_updated = datetime.utcnow()
    
    async def _check_uptime_status(self, component: ServiceComponent) -> bool:
        """Check uptime status for a component"""
        if not component.uptime_check_ids:
            return True  # Assume up if no checks configured
        
        try:
            # Query uptime check results from Cloud Monitoring
            # This is a simplified implementation - in production, you'd query actual metrics
            for check_id in component.uptime_check_ids:
                # Simulate uptime check (replace with actual monitoring query)
                pass
            
            return True  # Placeholder - implement actual uptime checking
        except Exception as e:
            self.logger.error(f"Error checking uptime for {component.name}: {e}")
            return False
    
    async def _check_performance_metrics(self, component: ServiceComponent) -> Dict[str, float]:
        """Check performance metrics for a component"""
        metrics = {}
        
        try:
            # Query performance metrics from Cloud Monitoring
            # This would include response time, error rate, etc.
            metrics["response_time_ms"] = 150.0  # Placeholder
            metrics["error_rate"] = 0.001  # Placeholder
            metrics["throughput_rps"] = 10.0  # Placeholder
            
        except Exception as e:
            self.logger.error(f"Error checking performance for {component.name}: {e}")
        
        return metrics
    
    def _determine_component_status(self, is_up: bool, performance: Dict[str, float]) -> ServiceStatus:
        """Determine component status based on uptime and performance"""
        if not is_up:
            return ServiceStatus.MAJOR_OUTAGE
        
        response_time = performance.get("response_time_ms", 0)
        error_rate = performance.get("error_rate", 0)
        
        if error_rate > 0.05:  # > 5% error rate
            return ServiceStatus.PARTIAL_OUTAGE
        elif error_rate > 0.01 or response_time > 1000:  # > 1% error rate or > 1s response time
            return ServiceStatus.DEGRADED_PERFORMANCE
        else:
            return ServiceStatus.OPERATIONAL
    
    async def _update_uptime_metrics(self):
        """Update uptime metrics for all components"""
        current_time = datetime.utcnow()
        
        for component_id, component in self.components.items():
            is_operational = component.status == ServiceStatus.OPERATIONAL
            self.uptime_history[component_id].append({
                "timestamp": current_time,
                "operational": is_operational
            })
    
    async def _detect_incidents(self):
        """Detect and auto-create incidents based on status changes"""
        # Check for patterns that might indicate incidents
        for component_id, component in self.components.items():
            if component.status in [ServiceStatus.PARTIAL_OUTAGE, ServiceStatus.MAJOR_OUTAGE]:
                # Check if there's already an active incident for this component
                active_incident = None
                for incident in self.incidents.values():
                    if (incident.status not in [IncidentStatus.RESOLVED, IncidentStatus.POSTMORTEM] and
                        component_id in incident.affected_components):
                        active_incident = incident
                        break
                
                if not active_incident:
                    await self._auto_create_incident(component, component.status)
    
    async def _auto_create_incident(self, component: ServiceComponent, status: ServiceStatus):
        """Auto-create incident for component issues"""
        severity = IncidentSeverity.HIGH if status == ServiceStatus.MAJOR_OUTAGE else IncidentSeverity.MEDIUM
        
        incident_id = f"auto-{int(time.time())}-{component.id}"
        
        # Use AI to generate incident description
        description = await self._generate_incident_description(component, status)
        
        incident = Incident(
            id=incident_id,
            title=f"{component.name} {status.value.replace('_', ' ').title()}",
            description=description,
            severity=severity,
            status=IncidentStatus.INVESTIGATING,
            affected_components=[component.id],
            created_at=datetime.utcnow(),
            impact_description=f"{component.name} is experiencing {status.value.replace('_', ' ')}"
        )
        
        self.incidents[incident_id] = incident
        self.logger.warning(f"Auto-created incident: {incident.title}")
        
        # Add initial update
        await self.add_incident_update(incident_id, "Incident automatically detected. Investigation in progress.")
    
    async def _generate_incident_description(self, component: ServiceComponent, status: ServiceStatus) -> str:
        """Generate incident description using AI"""
        if not self.ai_model:
            return f"Automatic incident created for {component.name} status change to {status.value}"
        
        try:
            prompt = f"""
            Generate a concise incident description for a status page.
            
            Component: {component.name} - {component.description}
            Status: {status.value}
            Performance Metrics: {component.performance_metrics}
            
            Provide a brief, professional description suitable for a public status page.
            Focus on user impact and current status. Keep it under 100 words.
            """
            
            response = await self.ai_model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            self.logger.error(f"Error generating incident description: {e}")
            return f"We are investigating issues with {component.name}. Updates will be provided as they become available."
    
    def calculate_overall_status(self) -> ServiceStatus:
        """Calculate overall system status"""
        component_statuses = [comp.status for comp in self.components.values()]
        
        if ServiceStatus.MAJOR_OUTAGE in component_statuses:
            return ServiceStatus.MAJOR_OUTAGE
        elif ServiceStatus.PARTIAL_OUTAGE in component_statuses:
            return ServiceStatus.PARTIAL_OUTAGE
        elif ServiceStatus.DEGRADED_PERFORMANCE in component_statuses:
            return ServiceStatus.DEGRADED_PERFORMANCE
        elif ServiceStatus.MAINTENANCE in component_statuses:
            return ServiceStatus.MAINTENANCE
        else:
            return ServiceStatus.OPERATIONAL
    
    def calculate_uptime_stats(self) -> Dict[str, float]:
        """Calculate uptime statistics"""
        stats = {}
        
        for component_id, history in self.uptime_history.items():
            if not history:
                stats[component_id] = 1.0
                continue
            
            operational_count = sum(1 for entry in history if entry["operational"])
            uptime = operational_count / len(history) if history else 1.0
            stats[component_id] = round(uptime, 4)
        
        # Overall uptime (average of all components)
        if stats:
            stats["overall"] = round(sum(stats.values()) / len(stats), 4)
        else:
            stats["overall"] = 1.0
        
        return stats
    
    async def get_status_page_data(self, request: StatusPageRequest) -> StatusPageResponse:
        """Get complete status page data"""
        # Filter components if requested
        components_data = []
        for comp_id, component in self.components.items():
            if request.component_ids is None or comp_id in request.component_ids:
                comp_data = {
                    "id": component.id,
                    "name": component.name,
                    "description": component.description,
                    "status": component.status.value,
                    "last_updated": component.last_updated.isoformat()
                }
                
                if request.include_metrics:
                    comp_data["performance_metrics"] = component.performance_metrics
                
                components_data.append(comp_data)
        
        # Get incidents
        active_incidents = []
        recent_incidents = []
        
        if request.include_incidents:
            for incident in self.incidents.values():
                incident_data = {
                    "id": incident.id,
                    "title": incident.title,
                    "description": incident.description,
                    "severity": incident.severity.value,
                    "status": incident.status.value,
                    "affected_components": incident.affected_components,
                    "created_at": incident.created_at.isoformat(),
                    "impact_description": incident.impact_description,
                    "updates": incident.updates
                }
                
                if incident.resolved_at:
                    incident_data["resolved_at"] = incident.resolved_at.isoformat()
                
                if incident.status in [IncidentStatus.RESOLVED, IncidentStatus.POSTMORTEM]:
                    # Include resolved incidents from last 7 days
                    if incident.resolved_at and incident.resolved_at > datetime.utcnow() - timedelta(days=7):
                        recent_incidents.append(incident_data)
                else:
                    active_incidents.append(incident_data)
        
        return StatusPageResponse(
            overall_status=self.calculate_overall_status(),
            components=components_data,
            active_incidents=active_incidents,
            recent_incidents=recent_incidents,
            uptime_stats=self.calculate_uptime_stats(),
            last_updated=datetime.utcnow()
        )
    
    async def create_incident(self, request: IncidentCreateRequest) -> str:
        """Create a new incident"""
        incident_id = f"manual-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        
        incident = Incident(
            id=incident_id,
            title=request.title,
            description=request.description,
            severity=request.severity,
            status=IncidentStatus.INVESTIGATING,
            affected_components=request.affected_components,
            created_at=datetime.utcnow(),
            impact_description=request.impact_description
        )
        
        self.incidents[incident_id] = incident
        self.logger.info(f"Created manual incident: {incident.title}")
        
        # Add initial update
        await self.add_incident_update(incident_id, "Incident created. Investigation in progress.")
        
        return incident_id
    
    async def update_incident(self, incident_id: str, request: IncidentUpdateRequest) -> bool:
        """Update an existing incident"""
        if incident_id not in self.incidents:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        incident = self.incidents[incident_id]
        
        # Update status if provided
        if request.status:
            incident.status = request.status
        
        # Mark as resolved if requested
        if request.resolved and incident.status != IncidentStatus.RESOLVED:
            incident.status = IncidentStatus.RESOLVED
            incident.resolved_at = datetime.utcnow()
        
        # Add update message
        await self.add_incident_update(incident_id, request.update_message)
        
        self.logger.info(f"Updated incident {incident_id}: {request.update_message}")
        return True
    
    async def add_incident_update(self, incident_id: str, message: str) -> bool:
        """Add an update to an incident"""
        if incident_id not in self.incidents:
            return False
        
        incident = self.incidents[incident_id]
        update = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "status": incident.status.value
        }
        
        incident.updates.append(update)
        return True
    
    async def set_maintenance_mode(self, component_ids: List[str], enabled: bool, message: str = "") -> bool:
        """Set maintenance mode for components"""
        for comp_id in component_ids:
            if comp_id in self.components:
                component = self.components[comp_id]
                if enabled:
                    component.status = ServiceStatus.MAINTENANCE
                else:
                    component.status = ServiceStatus.OPERATIONAL
                component.last_updated = datetime.utcnow()
                
                self.logger.info(f"Set maintenance mode for {component.name}: {enabled}")
        
        # Create maintenance incident if enabled
        if enabled and message:
            incident_id = f"maintenance-{int(time.time())}"
            incident = Incident(
                id=incident_id,
                title="Scheduled Maintenance",
                description=message,
                severity=IncidentSeverity.LOW,
                status=IncidentStatus.MONITORING,
                affected_components=component_ids,
                created_at=datetime.utcnow(),
                impact_description="Scheduled maintenance in progress"
            )
            self.incidents[incident_id] = incident
        
        return True
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary metrics for monitoring"""
        return {
            "total_components": len(self.components),
            "operational_components": len([c for c in self.components.values() if c.status == ServiceStatus.OPERATIONAL]),
            "active_incidents": len([i for i in self.incidents.values() if i.status not in [IncidentStatus.RESOLVED, IncidentStatus.POSTMORTEM]]),
            "uptime_stats": self.calculate_uptime_stats(),
            "overall_status": self.calculate_overall_status().value,
            "last_updated": datetime.utcnow().isoformat()
        } 