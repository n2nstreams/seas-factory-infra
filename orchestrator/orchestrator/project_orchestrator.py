try:
    from google.adk.agents import Agent  # type: ignore
except Exception:  # pragma: no cover
    class Agent:  # minimal stub for local tests
        def __init__(self, **_: object) -> None:
            pass

def greet(name: str) -> str:
    """Tiny helper function for first-run smoke test."""
    return f"Hello, {name}! 👋"

class GreeterAgent(Agent):
    """Tiny helper agent for first-run smoke test."""
    
    def __init__(self):
        super().__init__(
            name="greeter_agent",
            model="gemini-2.0-flash",
            description="A simple greeter agent",
            instruction="You are a helpful assistant that greets users.",
            tools=[greet]
        )

class ProjectOrchestrator(Agent):
    """Root agent — will later delegate to Idea, Dev, QA agents."""
    
    def __init__(self):
        super().__init__(
            name="project_orchestrator",
            model="gemini-2.0-flash", 
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
    orchestrator = ProjectOrchestrator()
    print(orchestrator.run({"name": "Factory"})) 