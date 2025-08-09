#!/usr/bin/env python3
"""
Night 73 Demo: DocAgent YouTube Script Generation for Synthesia
Demo of TL;DR video script generation using the enhanced DocAgent
"""

import asyncio
import requests
import json
from datetime import datetime
from typing import Dict, Any

class Night73Demo:
    """Demonstration of DocAgent YouTube script generation for Synthesia"""
    
    def __init__(self):
        self.base_url = "http://localhost:8089"  # DocAgent API
        self.demo_scripts = []
        
    async def demo_youtube_script_generation(self):
        """Main demo function showing YouTube script generation"""
        print("🎬 Night 73 Demo: YouTube Script Generation for Synthesia")
        print("=" * 60)
        
        # Demo different script types
        await self._demo_overview_script()
        await self._demo_technical_demo_script()
        await self._demo_tutorial_script()
        
        print("\n🎉 Night 73 Demo Complete!")
        print(f"Generated {len(self.demo_scripts)} video scripts")
        
    async def _demo_overview_script(self):
        """Generate overview-style script for general audience"""
        print("\n📹 Generating Overview Script for General Audience")
        print("-" * 50)
        
        script_data = {
            "title": "AI SaaS Factory: Turn Ideas into Apps Automatically",
            "duration": 3,
            "style": "overview",
            "target_audience": "general_audience",
            "include_synthesia_cues": True
        }
        
        result = await self._call_api("/generate/youtube-script", script_data)
        if result:
            self.demo_scripts.append(result)
            print(f"✅ Generated {result['word_count']} word script")
            print(f"📝 Title: {result['title']}")
            print(f"⏱️  Duration: 3 minutes")
            print("\nScript Preview:")
            print("-" * 30)
            print(result['content'][:500] + "..." if len(result['content']) > 500 else result['content'])
            
    async def _demo_technical_demo_script(self):
        """Generate technical demo script for developers"""
        print("\n🔧 Generating Technical Demo Script for Developers")
        print("-" * 50)
        
        script_data = {
            "title": "AI SaaS Factory Architecture Deep Dive",
            "duration": 7,
            "style": "demo",
            "target_audience": "developers",
            "include_synthesia_cues": True
        }
        
        result = await self._call_api("/generate/youtube-script", script_data)
        if result:
            self.demo_scripts.append(result)
            print(f"✅ Generated {result['word_count']} word script")
            print(f"📝 Title: {result['title']}")
            print(f"⏱️  Duration: 7 minutes")
            print("\nScript Preview:")
            print("-" * 30)
            print(result['content'][:500] + "..." if len(result['content']) > 500 else result['content'])
            
    async def _demo_tutorial_script(self):
        """Generate tutorial script for users"""
        print("\n📚 Generating Tutorial Script for Users")
        print("-" * 50)
        
        script_data = {
            "title": "How to Build Your First SaaS App with AI",
            "duration": 5,
            "style": "tutorial",
            "target_audience": "users",
            "include_synthesia_cues": True
        }
        
        result = await self._call_api("/generate/youtube-script", script_data)
        if result:
            self.demo_scripts.append(result)
            print(f"✅ Generated {result['word_count']} word script")
            print(f"📝 Title: {result['title']}")
            print(f"⏱️  Duration: 5 minutes")
            print("\nScript Preview:")
            print("-" * 30)
            print(result['content'][:500] + "..." if len(result['content']) > 500 else result['content'])
            
    async def _call_api(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make API call to DocAgent service"""
        try:
            # Add mock tenant headers for demo
            headers = {
                "Content-Type": "application/json",
                "X-Tenant-ID": "demo-tenant",
                "X-User-ID": "demo-user",
                "Authorization": "Bearer demo-token"
            }
            
            url = f"{self.base_url}{endpoint}"
            
            # Use requests for sync demo (in real implementation would use async)
            import requests
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Connection Error: {str(e)}")
            print("💡 Make sure DocAgent is running: cd agents/docs && python main.py")
            return None
    
    async def save_demo_scripts(self):
        """Save generated scripts to files for review"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, script in enumerate(self.demo_scripts):
            filename = f"night73_script_{i+1}_{timestamp}.md"
            with open(filename, 'w') as f:
                f.write(f"# {script['title']}\n\n")
                f.write(f"**Generated:** {script['generated_at']}\n")
                f.write(f"**Word Count:** {script['word_count']}\n")
                f.write(f"**Type:** {script['metadata']['document_type']}\n\n")
                f.write(script['content'])
            
            print(f"💾 Saved script to: {filename}")

async def main():
    """Run the Night 73 demo"""
    demo = Night73Demo()
    
    try:
        await demo.demo_youtube_script_generation()
        await demo.save_demo_scripts()
        
        print("\n🎯 Night 73 Implementation Summary:")
        print("✅ Extended DocAgent with YouTube script generation")
        print("✅ Added Synthesia-specific formatting and timing cues")
        print("✅ Created dedicated video script API endpoint")
        print("✅ Generated TL;DR content from project documentation")
        print("✅ Implemented multiple script styles (overview, demo, tutorial)")
        
        print("\n📋 Next Steps:")
        print("• Review generated scripts for accuracy and engagement")
        print("• Test scripts with Synthesia AI video generation")
        print("• Fine-tune prompts based on video output quality")
        print("• Add script templates for different video types")
        print("• Integrate with CI/CD for automated video generation")
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 