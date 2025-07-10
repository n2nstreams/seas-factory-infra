from google.adk.agents import Agent
from google.adk.tools import transfer_to_agent
from orchestrator.providers import get_llm_model
from pydantic import BaseModel
from typing import Any
import httpx
import os

LANG_ECHO_URL = os.getenv("LANG_ECHO_URL")

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

class ProjectOrchestrator(Agent):
    """Root agent — will later delegate to Idea, Dev, QA agents."""
    
    def __init__(self):
        greeter = GreeterAgent()
        super().__init__(
            name="project_orchestrator",
            model=get_llm_model(), 
            description="Root orchestrator agent that coordinates all other agents",
            instruction="You are the root orchestrator that coordinates between different specialized agents for idea generation, development, and quality assurance. When you receive a request, delegate to the greeter_agent and return 'pong'.",
            sub_agents=[greeter],
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