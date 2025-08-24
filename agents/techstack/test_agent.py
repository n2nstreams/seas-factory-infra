#!/usr/bin/env python3
"""
Test script for TechStackAgent
"""
import asyncio
import httpx
from main import TechStackAgent, TechStackRequest

async def test_agent_direct():
    """Test the agent directly without HTTP"""
    print("🧪 Testing TechStackAgent directly...")
    
    agent = TechStackAgent()
    
    # Test request
    request = TechStackRequest(
        project_type="web",
        requirements=["user authentication", "database", "responsive design"],
        team_size=3,
        timeline="3 months"
    )
    
    try:
        recommendation = await agent.generate_recommendation(request)
        print("✅ Direct test successful!")
        print(f"Project Type: {recommendation.project_type}")
        print(f"Overall Score: {recommendation.overall_score}/10")
        print(f"Frontend recommendations: {len(recommendation.frontend)}")
        print(f"Backend recommendations: {len(recommendation.backend)}")
        print(f"Reasoning: {recommendation.reasoning[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Direct test failed: {e}")
        return False

async def test_agent_http():
    """Test the agent via HTTP endpoints"""
    print("\n🌐 Testing TechStackAgent HTTP API...")
    
    base_url = "http://localhost:8081"
    
    try:
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            health_response = await client.get(f"{base_url}/health")
            if health_response.status_code == 200:
                print("✅ Health check passed")
            else:
                print(f"❌ Health check failed: {health_response.status_code}")
                return False
            
            # Test categories endpoint
            categories_response = await client.get(f"{base_url}/categories")
            if categories_response.status_code == 200:
                categories = categories_response.json()
                print(f"✅ Categories endpoint works: {categories['categories']}")
            
            # Test recommendation endpoint
            test_request = {
                "project_type": "api",
                "requirements": ["REST API", "authentication", "database"],
                "team_size": 2
            }
            
            recommend_response = await client.post(
                f"{base_url}/recommend", 
                json=test_request
            )
            
            if recommend_response.status_code == 200:
                recommendation = recommend_response.json()
                print("✅ Recommendation endpoint works!")
                print(f"Overall Score: {recommendation['overall_score']}/10")
                print(f"Backend options: {len(recommendation['backend'])}")
                return True
            else:
                print(f"❌ Recommendation failed: {recommend_response.status_code}")
                print(f"Response: {recommend_response.text}")
                return False
                
    except Exception as e:
        print(f"❌ HTTP test failed: {e}")
        print("💡 Make sure to start the agent with: uvicorn main:app --host 0.0.0.0 --port 8081")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting TechStackAgent Tests\n")
    
    # Run direct test
    direct_success = await test_agent_direct()
    
    # Run HTTP test (only if server is running)
    http_success = await test_agent_http()
    
    print("\n📊 Test Results:")
    print(f"Direct API: {'✅ PASS' if direct_success else '❌ FAIL'}")
    print(f"HTTP API: {'✅ PASS' if http_success else '❌ FAIL'}")
    
    if direct_success and http_success:
        print("\n🎉 All tests passed! TechStackAgent is ready.")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")

if __name__ == "__main__":
    asyncio.run(main()) 