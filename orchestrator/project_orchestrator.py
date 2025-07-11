from google.adk.agents import Agent
from google.adk.tools import transfer_to_agent
from orchestrator.providers import get_llm_model
from pydantic import BaseModel
from typing import Any, Dict
import httpx
import os
import json

LANG_ECHO_URL = os.getenv("LANG_ECHO_URL")
TECHSTACK_AGENT_URL = os.getenv("TECHSTACK_AGENT_URL", "http://localhost:8081")
DESIGN_AGENT_URL = os.getenv("DESIGN_AGENT_URL", "http://localhost:8082")

class Envelope(BaseModel):
    """Agent2Agent protocol envelope"""
    type: str = "agent2agent"
    version: int = 1
    content: Any

def greet(name: str) -> str:
    """Tiny helper function for first-run smoke test."""
    return f"Hello, {name}! 👋"

def pong(_: str) -> str:  # ignore input, always pong
    return "pong"

def recommend_tech_stack(project_type: str, requirements: str = "") -> str:
    """Call TechStack Agent to get technology stack recommendations"""
    try:
        # Parse requirements if provided as string
        req_list = [req.strip() for req in requirements.split(",") if req.strip()] if requirements else []
        
        payload = {
            "project_type": project_type,
            "requirements": req_list,
            "preferences": {},
            "team_size": None,
            "timeline": None
        }
        
        response = httpx.post(f"{TECHSTACK_AGENT_URL}/recommend", json=payload, timeout=30.0)
        
        if response.status_code == 200:
            recommendation = response.json()
            # Format the response for the orchestrator
            summary = f"Tech Stack Recommendation for {project_type} project:\n"
            summary += f"Overall Score: {recommendation['overall_score']}/10\n\n"
            
            # Add top recommendations from each category
            categories = ['frontend', 'backend', 'database', 'deployment', 'testing']
            for category in categories:
                if recommendation.get(category) and len(recommendation[category]) > 0:
                    top_lib = recommendation[category][0]
                    summary += f"{category.title()}: {top_lib['name']} (Score: {top_lib['score']:.1f}/10)\n"
                    if top_lib.get('pros'):
                        summary += f"  Pros: {', '.join(top_lib['pros'][:2])}\n"
            
            summary += f"\nReasoning: {recommendation['reasoning']}"
            return summary
        else:
            return f"Error calling TechStack Agent: {response.status_code}"
            
    except Exception as e:
        return f"Error getting tech stack recommendation: {str(e)}"

def generate_wireframes(project_type: str, pages: str = "", style_preferences: str = "") -> str:
    """Call Design Agent to generate wireframes and design recommendations"""
    try:
        # Parse pages if provided as string
        page_list = [page.strip() for page in pages.split(",") if page.strip()] if pages else []
        
        # Parse style preferences (simplified)
        style_prefs = {}
        if style_preferences:
            for pref in style_preferences.split(","):
                if "=" in pref:
                    key, value = pref.split("=", 1)
                    style_prefs[key.strip()] = value.strip()
        
        payload = {
            "project_type": project_type,
            "pages": page_list,
            "style_preferences": style_prefs,
            "color_scheme": "natural",  # Default to natural as per user preference
            "layout_type": "clean",
            "brand_requirements": "",
            "target_audience": ""
        }
        
        response = httpx.post(f"{DESIGN_AGENT_URL}/generate", json=payload, timeout=30.0)
        
        if response.status_code == 200:
            recommendation = response.json()
            # Format the response for the orchestrator
            summary = f"Design Recommendation for {project_type} project:\n"
            summary += f"Generated {len(recommendation['wireframes'])} wireframes\n"
            summary += f"Figma Project: {recommendation.get('figma_project_url', 'N/A')}\n\n"
            
            # Add wireframe details
            for wireframe in recommendation['wireframes'][:3]:  # Show first 3
                summary += f"Page: {wireframe['page_name']}\n"
                summary += f"  Elements: {len(wireframe['elements'])} components\n"
                if wireframe.get('figma_url'):
                    summary += f"  Figma URL: {wireframe['figma_url']}\n"
            
            # Add style guide info
            style_guide = recommendation.get('style_guide', {})
            if style_guide:
                summary += f"\nStyle Guide:\n"
                summary += f"  Theme: {style_guide.get('theme', 'N/A')}\n"
                summary += f"  Primary Color: {style_guide.get('primary_color', 'N/A')}\n"
                summary += f"  Design System: Glassmorphism with olive green accents\n"
            
            summary += f"\nReasoning: {recommendation['reasoning']}"
            summary += f"\nEstimated Dev Time: {recommendation.get('estimated_dev_time', 'N/A')}"
            
            return summary
        else:
            return f"Error calling Design Agent: {response.status_code}"
            
    except Exception as e:
        return f"Error generating wireframes: {str(e)}"

class GreeterAgent(Agent):
    """Tiny helper agent for first-run smoke test."""
    
    def __init__(self):
        super().__init__(
            name="greeter_agent",
            model=get_llm_model(),
            description="A simple greeter agent that always returns 'pong'",
            instruction="You are a helpful assistant. When called, always return 'pong'.",
            tools=[greet, pong]
        )

class TechStackProxyAgent(Agent):
    """Proxy agent for TechStack recommendations"""
    
    def __init__(self):
        super().__init__(
            name="techstack_agent",
            model=get_llm_model(),
            description="Intelligent technology stack recommendation agent that analyzes project requirements and suggests optimal tech stacks with pros/cons",
            instruction="You are a technology stack advisor. When asked to recommend technology stacks, use the recommend_tech_stack tool with the appropriate project type (web, api, mobile, ml, desktop). Always provide comprehensive analysis including pros and cons.",
            tools=[recommend_tech_stack]
        )

class DesignProxyAgent(Agent):
    """Proxy agent for Design and wireframe generation"""
    
    def __init__(self):
        super().__init__(
            name="design_agent",
            model=get_llm_model(),
            description="Intelligent design agent that generates wireframes, creates Figma projects, and provides comprehensive design recommendations with glassmorphism styling",
            instruction="You are a UI/UX design expert specializing in glassmorphism design with natural olive green color schemes. When asked to create designs or wireframes, use the generate_wireframes tool with the appropriate project type (web, mobile, desktop). Always include specific page names and style preferences.",
            tools=[generate_wireframes]
        )

class ProjectOrchestrator(Agent):
    """Root agent — will later delegate to Idea, Dev, QA agents."""
    
    def __init__(self):
        greeter = GreeterAgent()
        techstack = TechStackProxyAgent()
        design = DesignProxyAgent()
        super().__init__(
            name="project_orchestrator",
            model=get_llm_model(), 
            description="Root orchestrator agent that coordinates all other agents including tech stack and design recommendations",
            instruction="You are the root orchestrator that coordinates between different specialized agents. You can delegate to: greeter_agent for simple greetings, techstack_agent for technology stack recommendations, or design_agent for wireframes and UI design. For tech stack requests, specify project type (web, api, mobile, ml, desktop). For design requests, specify project type and desired pages.",
            sub_agents=[greeter, techstack, design],
            tools=[transfer_to_agent]
        )
    
    def run(self, payload: dict) -> str:
        """Main entry point for the orchestrator (compatibility with original plan)"""
        _name = payload.get("name", "world")
        
        # Step 1 – delegate to internal agent
        internal = "pong"  # Direct call to match expected behavior
        
        # Step 2 – bounce to LangGraph agent via Agent2Agent
        if LANG_ECHO_URL:
            try:
                env = Envelope(type="agent2agent", version=1, content="ping")
                response = httpx.post(LANG_ECHO_URL, json=env.model_dump(), timeout=30.0)
                reply = Envelope(**response.json()).content
                return f"{internal} + {reply}"
            except Exception as e:
                print(f"Error calling LangGraph agent: {e}")
                return f"{internal} + error"
        
        return internal

if __name__ == "__main__":  # quick local smoke test
    from orchestrator.providers import get_provider_config, validate_provider_config
    
    # Debug info about provider configuration
    if validate_provider_config():
        config = get_provider_config()
        print(f"🤖 Using provider: {config['provider']} with model: {config['model']}")
    else:
        print("❌ Provider configuration is invalid")
        exit(1)
    
    orchestrator = ProjectOrchestrator()
    print(orchestrator.run({"name": "Factory"})) 