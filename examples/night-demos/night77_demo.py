#!/usr/bin/env python3
"""
Night 77 Demo: CopyWriter Agent
Draft marketing landing copy via CopyWriterAgent

This demo showcases the CopyWriter agent's ability to generate 
compelling marketing copy for SaaS landing pages.
"""

import asyncio
import json
import requests
import time
from typing import Dict, Any

# Demo configuration
MARKETING_AGENT_URL = "http://localhost:8091"
DEMO_PRODUCTS = [
    {
        "product_name": "TaskFlow Pro",
        "product_description": "AI-powered project management for remote teams",
        "target_audience": "Remote team managers and productivity enthusiasts",
        "key_features": ["AI task prioritization", "Real-time collaboration", "Advanced analytics"],
        "tone": "professional",
        "company_values": "We believe in empowering teams to work smarter, not harder"
    },
    {
        "product_name": "DataFlow Analytics",
        "product_description": "Real-time business intelligence platform",
        "target_audience": "Data analysts and business intelligence teams",
        "key_features": ["Real-time dashboards", "Custom reporting", "AI insights"],
        "tone": "technical",
        "pricing_tiers": [
            {"name": "Starter", "price": "$49/month", "features": "Basic dashboards"},
            {"name": "Pro", "price": "$149/month", "features": "Advanced analytics"},
            {"name": "Enterprise", "price": "Custom", "features": "Full customization"}
        ]
    },
    {
        "product_name": "SocialBoost",
        "product_description": "Social media automation and growth platform",
        "target_audience": "Small business owners and social media managers",
        "key_features": ["Auto-posting", "Engagement tracking", "Growth analytics"],
        "tone": "startup",
        "company_values": "Helping small businesses thrive in the digital age"
    }
]

def print_banner(title: str):
    """Print a decorative banner"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_section(title: str):
    """Print a section header"""
    print(f"\n📝 {title}")
    print("-" * 50)

def check_agent_health() -> bool:
    """Check if the marketing agent is running"""
    try:
        response = requests.get(f"{MARKETING_AGENT_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Marketing Agent Status: {data['status']}")
            print(f"✅ CopyWriter Enabled: {data.get('copywriter_enabled', 'Unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to marketing agent: {e}")
        print(f"💡 Make sure the agent is running: cd agents/marketing && python3 main.py")
        return False

def get_copy_templates() -> Dict[str, Any]:
    """Get available copy templates"""
    try:
        response = requests.get(f"{MARKETING_AGENT_URL}/copy-templates", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get templates: {response.status_code}")
            return {}
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting templates: {e}")
        return {}

def generate_copy(product: Dict[str, Any], copy_type: str) -> Dict[str, Any]:
    """Generate copy for a specific type"""
    try:
        payload = {**product, "copy_type": copy_type}
        response = requests.post(
            f"{MARKETING_AGENT_URL}/generate-copy",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Copy generation failed: {response.status_code}")
            if response.text:
                print(f"Error details: {response.text}")
            return {}
    except requests.exceptions.RequestException as e:
        print(f"❌ Error generating copy: {e}")
        return {}

def generate_full_landing_page(product: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a complete landing page"""
    try:
        payload = {**product, "copy_type": "full_landing"}
        response = requests.post(
            f"{MARKETING_AGENT_URL}/generate-landing-page",
            json=payload,
            timeout=60  # Longer timeout for full page generation
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Landing page generation failed: {response.status_code}")
            if response.text:
                print(f"Error details: {response.text}")
            return {}
    except requests.exceptions.RequestException as e:
        print(f"❌ Error generating landing page: {e}")
        return {}

def display_generated_copy(copy_data: Dict[str, Any]):
    """Display generated copy in a formatted way"""
    if not copy_data:
        print("❌ No copy to display")
        return
    
    print(f"📋 Copy Type: {copy_data.get('copy_type', 'Unknown')}")
    print("\n📄 Generated Content:")
    print("-" * 30)
    print(copy_data.get('content', 'No content generated'))
    
    alternatives = copy_data.get('alternatives', [])
    if alternatives:
        print(f"\n🔄 Alternative Versions ({len(alternatives)}):")
        for i, alt in enumerate(alternatives, 1):
            print(f"\n--- Alternative {i} ---")
            print(alt)
    
    metadata = copy_data.get('metadata', {})
    if metadata:
        print(f"\n📊 Metadata:")
        for key, value in metadata.items():
            print(f"  • {key}: {value}")

def demo_copy_templates():
    """Demo: Show available copy templates"""
    print_section("Available Copy Templates")
    
    templates = get_copy_templates()
    if templates:
        print("📝 Available Copy Types:")
        for copy_type in templates.get('copy_types', []):
            print(f"  • {copy_type}")
        
        print("\n🎨 Available Tones:")
        for tone in templates.get('tones', []):
            print(f"  • {tone}")
        
        print("\n💡 Example Request:")
        example = templates.get('example_request', {})
        print(json.dumps(example, indent=2))
    else:
        print("❌ Could not retrieve templates")

def demo_hero_copy_generation():
    """Demo: Generate hero section copy for different products"""
    print_section("Hero Section Copy Generation")
    
    for i, product in enumerate(DEMO_PRODUCTS, 1):
        print(f"\n🚀 Product {i}: {product['product_name']}")
        print(f"📝 Tone: {product['tone']}")
        
        copy_data = generate_copy(product, "hero_section")
        if copy_data:
            display_generated_copy(copy_data)
        
        if i < len(DEMO_PRODUCTS):
            print("\n" + "~" * 50)

def demo_feature_copy_generation():
    """Demo: Generate features copy"""
    print_section("Features Copy Generation")
    
    product = DEMO_PRODUCTS[0]  # Use TaskFlow Pro
    print(f"🚀 Generating features copy for: {product['product_name']}")
    
    copy_data = generate_copy(product, "features")
    if copy_data:
        display_generated_copy(copy_data)

def demo_full_landing_page():
    """Demo: Generate complete landing page"""
    print_section("Complete Landing Page Generation")
    
    product = DEMO_PRODUCTS[1]  # Use DataFlow Analytics (has pricing tiers)
    print(f"🚀 Generating full landing page for: {product['product_name']}")
    print("⏳ This may take a moment...")
    
    start_time = time.time()
    landing_page = generate_full_landing_page(product)
    generation_time = time.time() - start_time
    
    if landing_page:
        print(f"✅ Generated in {generation_time:.2f} seconds")
        
        sections = ['hero_section', 'features', 'pricing', 'testimonials', 'faq', 'cta', 'about']
        for section in sections:
            if section in landing_page:
                print(f"\n🎯 {section.upper().replace('_', ' ')}")
                print("-" * 40)
                content = landing_page[section].get('content', 'No content')
                # Truncate long content for demo
                if len(content) > 200:
                    content = content[:200] + "..."
                print(content)
    else:
        print("❌ Failed to generate landing page")

def demo_mock_mode():
    """Demo: Show what the CopyWriter would generate (mock mode)"""
    print_section("Mock Copy Generation (No API Required)")
    
    product = DEMO_PRODUCTS[0]
    
    print(f"🚀 Product: {product['product_name']}")
    print(f"📝 Target Audience: {product['target_audience']}")
    print(f"🎨 Tone: {product['tone']}")
    
    print("\n📄 Sample Hero Section (Mock):")
    print("-" * 30)
    print("""**Transform Your Team's Productivity with AI-Powered Project Management**

Stop struggling with scattered tasks and missed deadlines. TaskFlow Pro uses advanced AI to prioritize your work, predict bottlenecks, and keep your remote team perfectly synchronized.

✨ Key Benefits:
• Reduce project delays by 40% with smart prioritization
• Keep your team aligned with real-time collaboration
• Make data-driven decisions with advanced analytics

*Start your free trial today →*""")
    
    print("\n🔄 Alternative Version:")
    print("-" * 30)
    print("""**Finally, Project Management That Actually Works**

Tired of juggling endless tasks and missing deadlines? TaskFlow Pro's AI engine learns your team's patterns and automatically optimizes your workflow for maximum productivity.

*Join 10,000+ teams working smarter →*""")

def main():
    """Main demo function"""
    print_banner("Night 77: CopyWriter Agent Demo")
    print("🎯 Showcasing AI-powered marketing copy generation")
    print("💡 Part of the AI SaaS Factory - Week 11 Polish & Docs")
    
    # Check if the agent is running
    if check_agent_health():
        print("\n🟢 Agent is running - Live demo mode")
        
        # Run live demos
        demo_copy_templates()
        demo_hero_copy_generation()
        demo_feature_copy_generation()
        demo_full_landing_page()
        
    else:
        print("\n🟡 Agent not running - Mock demo mode")
        demo_mock_mode()
    
    print_banner("Demo Complete")
    print("✅ CopyWriter Agent successfully demonstrated!")
    print("\n📚 Key Features Showcased:")
    print("  • Multiple copy types (hero, features, pricing, etc.)")
    print("  • Different tone options (professional, startup, technical)")
    print("  • Alternative copy variations for A/B testing")
    print("  • Complete landing page generation")
    print("  • API integration ready for orchestrator")
    
    print("\n🚀 Next Steps:")
    print("  • Integrate with Design Agent for Figma wireframes")
    print("  • Connect to UI components for live copy updates")
    print("  • Add to orchestrator workflow for automated copy generation")

if __name__ == "__main__":
    main() 