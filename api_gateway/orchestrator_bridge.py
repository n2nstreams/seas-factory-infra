#!/usr/bin/env python3
"""
Orchestrator Bridge Service
Connects the orchestrator's event system to the API Gateway's factory pipeline updates
"""

import os
import logging
import asyncio
import httpx
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class OrchestratorBridge:
    """Bridge between orchestrator events and API Gateway factory updates"""
    
    def __init__(self):
        self.api_gateway_url = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
        self.orchestrator_url = os.getenv("ORCHESTRATOR_URL", "http://localhost:8001")
        self.tenant_id = os.getenv("DEFAULT_TENANT_ID", "5aff78c7-413b-4e0e-bbfb-090765835bab")
        self.user_id = os.getenv("DEFAULT_USER_ID", None)
        
        # Stage mapping from orchestrator to factory pipeline
        self.stage_mapping = {
            "greet": "idea_validation",
            "idea": "idea_validation",
            "techstack": "tech_stack",
            "design": "design",
            "ui_dev": "development",
            "playwright_qa": "qa",
            "github_merge": "deployment"
        }
        
        # Progress calculation per stage
        self.stage_progress = {
            "idea_validation": (0, 15),    # 0-15%
            "tech_stack": (15, 30),         # 15-30%
            "design": (30, 50),             # 30-50%
            "development": (50, 75),        # 50-75%
            "qa": (75, 90),                 # 75-90%
            "deployment": (90, 100)         # 90-100%
        }
        
    async def trigger_pipeline(self, idea_data: Dict[str, Any]) -> Optional[str]:
        """Trigger a new factory pipeline for an idea"""
        try:
            # Create factory pipeline
            async with httpx.AsyncClient() as client:
                factory_trigger = {
                    "idea_id": idea_data.get("id", ""),
                    "project_name": idea_data.get("project_name", "Untitled Project"),
                    "description": idea_data.get("description", ""),
                    "stage": "idea_validation",
                    "priority": idea_data.get("priority", "normal"),
                    "metadata": {
                        "source": "orchestrator_bridge",
                        "user_email": idea_data.get("user_email"),
                        "key_features": idea_data.get("key_features", []),
                        "target_audience": idea_data.get("target_audience"),
                        "budget": idea_data.get("budget")
                    }
                }
                
                response = await client.post(
                    f"{self.api_gateway_url}/api/factory/trigger",
                    json=factory_trigger,
                    headers={
                        "X-Tenant-Id": self.tenant_id,
                        "X-User-Id": self.user_id or ""
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    pipeline_id = result["pipeline_id"]
                    logger.info(f"Created factory pipeline: {pipeline_id}")
                    
                    # Now trigger orchestrator with the pipeline ID
                    await self.trigger_orchestrator(pipeline_id, idea_data)
                    
                    return pipeline_id
                else:
                    logger.error(f"Failed to create factory pipeline: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error triggering pipeline: {e}")
            return None
    
    async def trigger_orchestrator(self, pipeline_id: str, idea_data: Dict[str, Any]):
        """Trigger the orchestrator with the pipeline ID"""
        try:
            async with httpx.AsyncClient() as client:
                # Start with idea validation
                orchestrator_payload = {
                    "task_type": "idea",
                    "pipeline_id": pipeline_id,
                    "name": idea_data.get("project_name", ""),
                    "description": idea_data.get("description", ""),
                    "features": idea_data.get("key_features", []),
                    "target_audience": idea_data.get("target_audience", ""),
                    "budget": idea_data.get("budget", ""),
                    "metadata": {
                        "tenant_id": self.tenant_id,
                        "user_id": self.user_id
                    }
                }
                
                response = await client.post(
                    f"{self.orchestrator_url}/orchestrator",
                    json=orchestrator_payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully triggered orchestrator for pipeline {pipeline_id}")
                else:
                    logger.error(f"Orchestrator trigger failed: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"Error triggering orchestrator: {e}")
    
    async def handle_orchestrator_event(self, event: Dict[str, Any]):
        """Handle an event from the orchestrator"""
        event_type = event.get("type", "")
        pipeline_id = event.get("pipeline_id") or event.get("request_id")
        
        if not pipeline_id:
            logger.warning(f"Received event without pipeline_id: {event}")
            return
        
        # Map orchestrator stage to factory stage
        orchestrator_stage = event.get("stage", "")
        factory_stage = self.stage_mapping.get(orchestrator_stage, orchestrator_stage)
        
        if event_type == "START":
            await self.update_stage_status(pipeline_id, factory_stage, "running", 0)
            
        elif event_type == "FINISH":
            status = event.get("status", "completed")
            factory_status = "completed" if status == "success" else "failed"
            progress = self.stage_progress.get(factory_stage, (0, 100))[1]
            
            await self.update_stage_status(
                pipeline_id, 
                factory_stage, 
                factory_status, 
                progress,
                description=f"Stage {factory_stage} completed successfully"
            )
            
            # Trigger next stage if current succeeded
            if factory_status == "completed":
                await self.trigger_next_stage(pipeline_id, factory_stage, event.get("result", {}))
                
        elif event_type == "ERROR":
            error_msg = event.get("error", "Unknown error")
            await self.update_stage_status(
                pipeline_id,
                factory_stage,
                "failed",
                self.stage_progress.get(factory_stage, (0, 100))[0],
                error_message=error_msg
            )
            
        elif event_type == "PROGRESS":
            # Handle progress updates within a stage
            stage_progress = event.get("progress", 0)
            stage_range = self.stage_progress.get(factory_stage, (0, 100))
            overall_progress = stage_range[0] + (stage_range[1] - stage_range[0]) * (stage_progress / 100)
            
            await self.update_stage_status(
                pipeline_id,
                factory_stage,
                "running",
                overall_progress,
                description=event.get("description", "")
            )
    
    async def update_stage_status(
        self, 
        pipeline_id: str,
        stage: str,
        status: str,
        progress: float,
        description: str = "",
        error_message: str = None
    ):
        """Update factory pipeline stage status"""
        try:
            async with httpx.AsyncClient() as client:
                update_data = {
                    "stage": stage,
                    "status": status,
                    "progress": progress,
                    "description": description,
                    "error_message": error_message,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                response = await client.post(
                    f"{self.api_gateway_url}/api/factory/pipelines/{pipeline_id}/update",
                    json=update_data,
                    headers={
                        "X-Tenant-Id": self.tenant_id,
                        "X-User-Id": self.user_id or ""
                    }
                )
                
                if response.status_code == 200:
                    logger.info(f"Updated pipeline {pipeline_id}: {stage} -> {status} ({progress}%)")
                else:
                    logger.error(f"Failed to update pipeline: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"Error updating pipeline status: {e}")
    
    async def trigger_next_stage(self, pipeline_id: str, current_stage: str, stage_result: Dict[str, Any]):
        """Trigger the next stage in the pipeline"""
        # Define stage flow
        stage_flow = [
            "idea_validation",
            "tech_stack", 
            "design",
            "development",
            "qa",
            "deployment"
        ]
        
        try:
            current_index = stage_flow.index(current_stage)
            if current_index < len(stage_flow) - 1:
                next_stage = stage_flow[current_index + 1]
                
                # Map to orchestrator task type
                orchestrator_task_map = {
                    "tech_stack": "techstack",
                    "design": "design",
                    "development": "ui_dev",
                    "qa": "playwright_qa",
                    "deployment": "github_merge"
                }
                
                task_type = orchestrator_task_map.get(next_stage)
                if task_type:
                    async with httpx.AsyncClient() as client:
                        orchestrator_payload = {
                            "task_type": task_type,
                            "pipeline_id": pipeline_id,
                            "previous_result": stage_result,
                            "metadata": {
                                "tenant_id": self.tenant_id,
                                "user_id": self.user_id,
                                "current_stage": current_stage,
                                "next_stage": next_stage
                            }
                        }
                        
                        response = await client.post(
                            f"{self.orchestrator_url}/orchestrator",
                            json=orchestrator_payload,
                            timeout=30.0
                        )
                        
                        if response.status_code == 200:
                            logger.info(f"Triggered next stage {next_stage} for pipeline {pipeline_id}")
                        else:
                            logger.error(f"Failed to trigger next stage: {response.status_code}")
                            
        except ValueError:
            logger.warning(f"Unknown stage: {current_stage}")
        except Exception as e:
            logger.error(f"Error triggering next stage: {e}")


# Demo usage for testing
async def demo_bridge():
    """Demo the orchestrator bridge"""
    bridge = OrchestratorBridge()
    
    # Simulate an idea submission
    test_idea = {
        "id": "test-idea-123",
        "project_name": "AI Task Manager",
        "description": "An AI-powered task management app",
        "key_features": ["Smart prioritization", "Natural language input", "Team collaboration"],
        "target_audience": "Remote teams",
        "budget": "$10k-50k",
        "user_email": "test@example.com"
    }
    
    # Trigger the pipeline
    pipeline_id = await bridge.trigger_pipeline(test_idea)
    
    if pipeline_id:
        print(f"Pipeline created: {pipeline_id}")
        
        # Simulate some orchestrator events
        await asyncio.sleep(2)
        
        # Start event
        await bridge.handle_orchestrator_event({
            "type": "START",
            "pipeline_id": pipeline_id,
            "stage": "idea",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        await asyncio.sleep(3)
        
        # Progress event
        await bridge.handle_orchestrator_event({
            "type": "PROGRESS",
            "pipeline_id": pipeline_id,
            "stage": "idea",
            "progress": 50,
            "description": "Validating idea feasibility..."
        })
        
        await asyncio.sleep(3)
        
        # Finish event
        await bridge.handle_orchestrator_event({
            "type": "FINISH",
            "pipeline_id": pipeline_id,
            "stage": "idea",
            "status": "success",
            "result": {
                "feasibility_score": 85,
                "market_fit": "high",
                "recommended_tech": ["React", "Node.js", "PostgreSQL"]
            }
        })


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(demo_bridge())
