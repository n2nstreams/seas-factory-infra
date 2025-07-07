import os
from google.adk.agents import Agent

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def greet(name: str) -> str:
    """Greet a user by name."""
    return f"Hello, {name}! 👋 Welcome to the SaaS Factory!"

def get_project_status() -> str:
    """Get the current project status."""
    return "SaaS Factory is ready to build amazing applications!"

# Force Google AI Studio configuration
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "false"
os.environ["GOOGLE_API_KEY"] = "AIzaSyBHn3TFuegsbJz1I-pzE-ktA8SziQxwv2s"

# This is the root agent that ADK web interface will load
root_agent = Agent(
    name="project_orchestrator",
    model="gemini-1.5-flash",  # Use a model that works better with AI Studio
    description="Root orchestrator agent that coordinates all SaaS Factory operations",
    instruction="""You are the Project Orchestrator for the SaaS Factory. 
    You coordinate between different specialized agents and help users build SaaS applications.
    You can greet users and provide project status information.
    Be helpful, professional, and enthusiastic about building great software!""",
    tools=[greet, get_project_status]
)
