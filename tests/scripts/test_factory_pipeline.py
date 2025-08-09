#!/usr/bin/env python3
"""
Relocated from project root to tests/scripts/.
Demonstrates the end-to-end flow from idea submission to factory pipeline progress.
"""
import asyncio
import httpx
from datetime import datetime

API_GATEWAY_URL = "http://localhost:8000"
TENANT_ID = "5aff78c7-413b-4e0e-bbfb-090765835bab"
USER_ID = "550e8400-e29b-41d4-a716-446655440000"


async def submit_test_idea():
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
            "Multi-language support",
        ],
        "business_model": "subscription",
        "timeline": "3 months",
        "budget_range": "$25k-50k",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_GATEWAY_URL}/api/ideas/submit",
            json=idea_data,
            headers={"X-Tenant-Id": TENANT_ID, "X-User-Id": USER_ID},
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ Idea submitted successfully!")
            print(f"   ID: {result['id']}")
            print(f"   Title: {result['title']}")
            print(f"   Status: {result['status']}")
            print(f"   Submission ID: {result['submission_id']}")
            return result["id"]
        print(f"❌ Failed to submit idea: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


async def monitor_factory_pipelines():
    print("\n📊 Monitoring Factory Pipelines...")
    print("-" * 60)
    last_update = {}
    for _ in range(30):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_GATEWAY_URL}/api/factory/pipelines",
                headers={"X-Tenant-Id": TENANT_ID, "X-User-Id": USER_ID},
                params={"limit": 5},
            )
            if response.status_code == 200:
                pipelines = response.json()
                for pipeline in pipelines:
                    pipeline_id = pipeline["pipeline_id"]
                    update_key = f"{pipeline_id}:{pipeline['current_stage']}:{pipeline['progress']}"
                    if update_key != last_update.get(pipeline_id):
                        last_update[pipeline_id] = update_key
                        print(f"\n🏭 Pipeline: {pipeline['project_name']}")
                        print(f"   ID: {pipeline_id}")
                        print(f"   Stage: {pipeline['current_stage']}")
                        print(f"   Progress: {pipeline['progress']}%")
                        print(f"   Status: {pipeline['status']}")
                        if pipeline.get("stages"):
                            print("   Stages:")
                            for stage, status in pipeline["stages"].items():
                                emoji = {
                                    "completed": "✅",
                                    "running": "🔄",
                                    "pending": "⏳",
                                    "failed": "❌",
                                    "skipped": "⏭️",
                                }.get(status, "❓")
                                print(f"     {emoji} {stage}: {status}")
        await asyncio.sleep(2)
    print("\n✅ Monitoring complete!")


async def main():
    print("🚀 Testing Factory Pipeline Real-time Updates")
    print("=" * 60)
    idea_id = await submit_test_idea()
    if idea_id:
        monitor_task = asyncio.create_task(monitor_factory_pipelines())
        await monitor_task
    print("\n✅ Test complete!")


if __name__ == "__main__":
    asyncio.run(main())


