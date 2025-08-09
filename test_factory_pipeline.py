#!/usr/bin/env python3
"""
Test script for Factory Pipeline Real-time Updates
Demonstrates the end-to-end flow from idea submission to factory pipeline progress
"""

import asyncio
import httpx
import json
import time
from datetime import datetime

# Configuration
API_GATEWAY_URL = "http://localhost:8000"
TENANT_ID = "5aff78c7-413b-4e0e-bbfb-090765835bab"
USER_ID = "550e8400-e29b-41d4-a716-446655440000"  # Valid UUID for testing


async def submit_test_idea():
    """Submit a test idea to trigger the factory pipeline"""
    idea_data = {
        "title": f"AI Meeting Assistant - {datetime.now().strftime('%H:%M:%S')}",
        "description": "An AI-powered tool that automatically transcribes, summarizes, and extracts action items from meetings",
        "category": "productivity",
        "problem": "Teams waste hours in meetings and struggle to track action items and decisions",
        "solution": "AI assistant that joins meetings, provides real-time transcription, and automatically generates summaries with key decisions and action items",
        "target_audience": "Remote teams and project managers",
        "key_features": [
            "Real-time transcription",
            "Automatic summary generation",
            "Action item extraction",
            "Integration with calendar apps",
            "Multi-language support"
        ],
        "business_model": "subscription",
        "timeline": "3 months",
        "budget_range": "$25k-50k"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_GATEWAY_URL}/api/ideas/submit",
            json=idea_data,
            headers={
                "X-Tenant-Id": TENANT_ID,
                "X-User-Id": USER_ID
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Idea submitted successfully!")
            print(f"   ID: {result['id']}")
            print(f"   Title: {result['title']}")
            print(f"   Status: {result['status']}")
            print(f"   Submission ID: {result['submission_id']}")
            return result['id']
        else:
            print(f"❌ Failed to submit idea: {response.status_code}")
            print(f"   Response: {response.text}")
            return None


async def monitor_factory_pipelines():
    """Monitor factory pipeline progress"""
    print("\n📊 Monitoring Factory Pipelines...")
    print("-" * 60)
    
    last_update = {}
    
    for i in range(30):  # Monitor for 30 iterations
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_GATEWAY_URL}/api/factory/pipelines",
                headers={
                    "X-Tenant-Id": TENANT_ID,
                    "X-User-Id": USER_ID
                },
                params={"limit": 5}
            )
            
            if response.status_code == 200:
                pipelines = response.json()
                
                for pipeline in pipelines:
                    pipeline_id = pipeline['pipeline_id']
                    
                    # Check if this is a new update
                    update_key = f"{pipeline_id}:{pipeline['current_stage']}:{pipeline['progress']}"
                    if update_key != last_update.get(pipeline_id):
                        last_update[pipeline_id] = update_key
                        
                        print(f"\n🏭 Pipeline: {pipeline['project_name']}")
                        print(f"   ID: {pipeline_id}")
                        print(f"   Stage: {pipeline['current_stage']}")
                        print(f"   Progress: {pipeline['progress']}%")
                        print(f"   Status: {pipeline['status']}")
                        
                        # Show stage statuses
                        if pipeline.get('stages'):
                            print("   Stages:")
                            for stage, status in pipeline['stages'].items():
                                emoji = {
                                    'completed': '✅',
                                    'running': '🔄',
                                    'pending': '⏳',
                                    'failed': '❌',
                                    'skipped': '⏭️'
                                }.get(status, '❓')
                                print(f"     {emoji} {stage}: {status}")
            
            await asyncio.sleep(2)  # Check every 2 seconds
    
    print("\n✅ Monitoring complete!")


async def simulate_pipeline_progress(idea_id: str):
    """Simulate pipeline progress updates (for testing without orchestrator)"""
    print(f"\n🎭 Simulating pipeline progress for idea {idea_id}...")
    
    # Wait a bit for the pipeline to be created
    await asyncio.sleep(3)
    
    # Get the pipeline ID
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_GATEWAY_URL}/api/factory/pipelines",
            headers={
                "X-Tenant-Id": TENANT_ID,
                "X-User-Id": USER_ID
            },
            params={"limit": 1}
        )
        
        if response.status_code != 200 or not response.json():
            print("❌ No pipeline found")
            return
        
        pipeline = response.json()[0]
        pipeline_id = pipeline['pipeline_id']
        print(f"   Found pipeline: {pipeline_id}")
        
        # Simulate stage progression
        stages = [
            ("idea_validation", [
                (10, "running", "Analyzing market fit..."),
                (50, "running", "Validating technical feasibility..."),
                (100, "completed", "Idea validation complete!")
            ]),
            ("tech_stack", [
                (10, "running", "Selecting optimal technologies..."),
                (60, "running", "Evaluating framework compatibility..."),
                (100, "completed", "Tech stack selected: React, Node.js, PostgreSQL")
            ]),
            ("design", [
                (20, "running", "Creating wireframes..."),
                (70, "running", "Designing UI components..."),
                (100, "completed", "Design system ready!")
            ])
        ]
        
        for stage_name, updates in stages:
            for progress, status, description in updates:
                update_data = {
                    "stage": stage_name,
                    "status": status,
                    "progress": progress,
                    "description": description,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                response = await client.post(
                    f"{API_GATEWAY_URL}/api/factory/pipelines/{pipeline_id}/update",
                    json=update_data,
                    headers={
                        "X-Tenant-Id": TENANT_ID,
                        "X-User-Id": USER_ID
                    }
                )
                
                if response.status_code == 200:
                    print(f"   ✅ Updated {stage_name}: {progress}% - {description}")
                else:
                    print(f"   ❌ Failed to update: {response.text}")
                
                await asyncio.sleep(2)


async def main():
    """Main test flow"""
    print("🚀 Testing Factory Pipeline Real-time Updates")
    print("=" * 60)
    
    # Submit a test idea
    idea_id = await submit_test_idea()
    
    if idea_id:
        # Start monitoring in background
        monitor_task = asyncio.create_task(monitor_factory_pipelines())
        
        # Simulate pipeline progress (remove this when orchestrator is connected)
        await simulate_pipeline_progress(idea_id)
        
        # Wait for monitoring to complete
        await monitor_task
    
    print("\n✅ Test complete!")


if __name__ == "__main__":
    asyncio.run(main())
