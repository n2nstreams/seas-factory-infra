from google.adk.agents import Agent
from .providers import get_llm_model

def greet(name: str) -> str:
    """Tiny helper function for first-run smoke test."""
    return f"Hello, {name}! 👋"

class GreeterAgent(Agent):
    """Tiny helper agent for first-run smoke test."""
    
    def __init__(self):
        super().__init__(
            name="greeter_agent",
            model=get_llm_model(),
            description="A simple greeter agent",
            instruction="You are a helpful assistant that greets users.",
            tools=[greet]
        )

class ProjectOrchestrator(Agent):
    """Root agent — will later delegate to Idea, Dev, QA agents."""
    
    def __init__(self):
        super().__init__(
            name="project_orchestrator",
            model=get_llm_model(), 
            description="Root orchestrator agent that coordinates all other agents",
            instruction="You are the root orchestrator that coordinates between different specialized agents for idea generation, development, and quality assurance.",
            sub_agents=[GreeterAgent()]
        )
    
    def run(self, payload: dict) -> str:
        """Main entry point for the orchestrator (compatibility with original plan)"""
        name = payload.get("name", "world")
        # For now just call sub-agent. Later we'll branch by payload["stage"].
        return f"Hello, {name}! 👋"

if __name__ == "__main__":  # quick local smoke test
    from .providers import get_provider_config, validate_provider_config
    
    # Debug info about provider configuration
    if validate_provider_config():
        config = get_provider_config()
        print(f"🤖 Using provider: {config['provider']} with model: {config['model']}")
    else:
        print("❌ Provider configuration is invalid")
        exit(1)
    
    orchestrator = ProjectOrchestrator()
    print(orchestrator.run({"name": "Factory"})) 