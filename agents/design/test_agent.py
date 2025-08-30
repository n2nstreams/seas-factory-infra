#!/usr/bin/env python3
"""
Test script for DesignAgent
"""
import asyncio
import httpx
from main import DesignAgent, DesignRequest

async def test_agent_direct():
    """Test the agent directly without HTTP"""
    print("🧪 Testing DesignAgent directly...")
    
    agent = DesignAgent()
    
    # Test request
    request = DesignRequest(
        project_type="web",
        pages=["Home", "About", "Contact", "Dashboard"],
        style_preferences={"theme": "glassmorphism"},
        color_scheme="natural",
        layout_type="clean",
        target_audience="business users"
    )
    
    try:
        recommendation = await agent.generate_design(request)
        print("✅ Direct test successful!")
        print(f"Project Type: {recommendation.project_type}")
        print(f"Generated Wireframes: {len(recommendation.wireframes)}")
        print(f"Figma Project URL: {recommendation.figma_project_url}")
        print(f"Style Theme: {recommendation.style_guide.get('theme', 'N/A')}")
        print(f"Primary Color: {recommendation.style_guide.get('primary_color', 'N/A')}")
        print(f"Reasoning: {recommendation.reasoning[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Direct test failed: {e}")
        return False

async def test_agent_http():
    """Test the agent via HTTP endpoints"""
    print("\n🌐 Testing DesignAgent HTTP API...")
    
    base_url = "http://localhost:8082"
    
    try:
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            health_response = await client.get(f"{base_url}/health")
            if health_response.status_code == 200:
                print("✅ Health check passed")
            else:
                print(f"❌ Health check failed: {health_response.status_code}")
                return False
            
            # Test styles endpoint
            styles_response = await client.get(f"{base_url}/styles")
            if styles_response.status_code == 200:
                styles = styles_response.json()
                print(f"✅ Styles endpoint works: {styles['themes']}")
            
            # Test templates endpoint
            templates_response = await client.get(f"{base_url}/templates")
            if templates_response.status_code == 200:
                templates = templates_response.json()
                print(f"✅ Templates endpoint works: {len(templates['web'])} web templates")
            
            # Test design generation endpoint
            test_request = {
                "project_type": "mobile",
                "pages": ["Welcome", "Login", "Dashboard"],
                "style_preferences": {"theme": "glassmorphism"},
                "color_scheme": "natural",
                "target_audience": "mobile users"
            }
            
            generate_response = await client.post(
                f"{base_url}/generate", 
                json=test_request
            )
            
            if generate_response.status_code == 200:
                recommendation = generate_response.json()
                print("✅ Design generation endpoint works!")
                print(f"Generated {len(recommendation['wireframes'])} wireframes")
                print(f"Style theme: {recommendation['style_guide']['theme']}")
                print(f"Figma URL: {recommendation['figma_project_url']}")
                return True
            else:
                print(f"❌ Design generation failed: {generate_response.status_code}")
                print(f"Response: {generate_response.text}")
                return False
                
    except Exception as e:
        print(f"❌ HTTP test failed: {e}")
        print("💡 Make sure to start the agent with: uvicorn main:app --host 0.0.0.0 --port 8082")
        return False

async def test_glassmorphism_theme():
    """Test glassmorphism theme generation"""
    print("\n🎨 Testing Glassmorphism Theme Generation...")
    
    agent = DesignAgent()
    
    # Test glassmorphism-specific request
    request = DesignRequest(
        project_type="web",
        pages=["Landing"],
        style_preferences={"glassmorphism": True, "natural_colors": True},
        color_scheme="natural",
        layout_type="clean"
    )
    
    try:
        recommendation = await agent.generate_design(request)
        
        # Check if glassmorphism properties are present
        style_guide = recommendation.style_guide
        glassmorphism_props = style_guide.get('glassmorphism_properties', {})
        
        if glassmorphism_props:
            print("✅ Glassmorphism properties found:")
            print(f"  Backdrop Filter: {glassmorphism_props.get('backdrop_filter')}")
            print(f"  Border Radius: {glassmorphism_props.get('border_radius')}")
            print(f"  Primary Color: {style_guide.get('primary_color')}")
            print(f"  Secondary Color: {style_guide.get('secondary_color')}")
            
            # Check for natural olive green colors
            primary_color = style_guide.get('primary_color', '')
            if '#6B7B4F' in primary_color or 'olive' in primary_color.lower():
                print("✅ Natural olive green color scheme detected")
                return True
            else:
                print("⚠️  Expected olive green colors not found")
                return False
        else:
            print("❌ Glassmorphism properties not found")
            return False
            
    except Exception as e:
        print(f"❌ Glassmorphism test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting DesignAgent Tests\n")
    
    # Run direct test
    direct_success = await test_agent_direct()
    
    # Run HTTP test (only if server is running)
    http_success = await test_agent_http()
    
    # Run glassmorphism theme test
    theme_success = await test_glassmorphism_theme()
    
    print("\n📊 Test Results:")
    print(f"Direct API: {'✅ PASS' if direct_success else '❌ FAIL'}")
    print(f"HTTP API: {'✅ PASS' if http_success else '❌ FAIL'}")
    print(f"Glassmorphism Theme: {'✅ PASS' if theme_success else '❌ FAIL'}")
    
    if direct_success and http_success and theme_success:
        print("\n🎉 All tests passed! DesignAgent with glassmorphism theme is ready.")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")

if __name__ == "__main__":
    asyncio.run(main()) 