from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import json
import asyncio
from typing import List, Dict, Any, Optional
import os
import logging
from contextlib import asynccontextmanager
import base64
import sys

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from tenant_db import TenantDatabase, TenantContext, get_tenant_context_from_headers
from access_control import require_subscription, AccessLevel, TenantSubscription

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DesignRequest(BaseModel):
    """Request model for design generation"""
    project_type: str  # web, mobile, desktop
    pages: List[str] = []  # list of page names/types
    style_preferences: Dict[str, Any] = {}
    color_scheme: Optional[str] = "modern"
    layout_type: Optional[str] = "clean"
    brand_requirements: Optional[str] = ""
    target_audience: Optional[str] = ""

class WireframeElement(BaseModel):
    """Model for wireframe elements"""
    type: str  # header, navigation, content, footer, etc.
    position: Dict[str, float]  # x, y, width, height
    content: str
    style_properties: Dict[str, Any] = {}

class PageWireframe(BaseModel):
    """Model for a single page wireframe"""
    page_name: str
    page_type: str
    elements: List[WireframeElement]
    figma_url: Optional[str] = None
    preview_url: Optional[str] = None
    metadata: Dict[str, Any] = {}

class DesignRecommendation(BaseModel):
    """Model for complete design recommendation"""
    project_type: str
    wireframes: List[PageWireframe]
    style_guide: Dict[str, Any]
    figma_project_url: Optional[str] = None
    design_system: Dict[str, Any] = {}
    reasoning: str
    estimated_dev_time: Optional[str] = None

class DesignAgent:
    """Agent for generating wireframes and design recommendations"""
    
    def __init__(self):
        self.figma_token = os.getenv("FIGMA_ACCESS_TOKEN")
        self.galileo_api_key = os.getenv("GALILEO_API_KEY")
        self.design_cache = {}
        
    async def call_galileo_ai(self, prompt: str, style_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Call Galileo AI API for design generation (mock implementation)"""
        # Note: This is a mock implementation since Galileo AI API details aren't publicly available
        # In production, this would integrate with actual Galileo AI API
        
        logger.info(f"Calling Galileo AI with prompt: {prompt[:100]}...")
        
        try:
            # Mock Galileo AI response based on glassmorphism preference
            design_elements = self.generate_mock_design_elements(prompt, style_preferences)
            
            # Simulate API call delay
            await asyncio.sleep(0.5)
            
            return {
                "status": "success",
                "design_elements": design_elements,
                "style_recommendations": self.get_style_recommendations(style_preferences),
                "layout_suggestions": self.get_layout_suggestions(prompt)
            }
            
        except Exception as e:
            logger.error(f"Error calling Galileo AI: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_mock_design_elements(self, prompt: str, style_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate mock design elements based on prompt and preferences"""
        # Base elements for any web/mobile interface
        elements = [
            {
                "type": "header",
                "content": "Navigation Header",
                "position": {"x": 0, "y": 0, "width": 100, "height": 80},
                "style": "glassmorphism-nav"
            },
            {
                "type": "hero",
                "content": "Hero Section with Call-to-Action",
                "position": {"x": 0, "y": 80, "width": 100, "height": 400},
                "style": "glassmorphism-hero"
            },
            {
                "type": "content",
                "content": "Main Content Area",
                "position": {"x": 0, "y": 480, "width": 100, "height": 300},
                "style": "glassmorphism-content"
            },
            {
                "type": "footer",
                "content": "Footer Links",
                "position": {"x": 0, "y": 780, "width": 100, "height": 120},
                "style": "glassmorphism-footer"
            }
        ]
        
        # Add specific elements based on project type mentioned in prompt
        if "dashboard" in prompt.lower():
            elements.extend([
                {
                    "type": "sidebar",
                    "content": "Navigation Sidebar",
                    "position": {"x": 0, "y": 0, "width": 20, "height": 100},
                    "style": "glassmorphism-sidebar"
                },
                {
                    "type": "metrics",
                    "content": "Metrics Cards",
                    "position": {"x": 20, "y": 80, "width": 80, "height": 200},
                    "style": "glassmorphism-cards"
                }
            ])
        
        if "ecommerce" in prompt.lower() or "shop" in prompt.lower():
            elements.extend([
                {
                    "type": "product-grid",
                    "content": "Product Grid",
                    "position": {"x": 0, "y": 480, "width": 100, "height": 400},
                    "style": "glassmorphism-grid"
                },
                {
                    "type": "cart",
                    "content": "Shopping Cart",
                    "position": {"x": 80, "y": 0, "width": 20, "height": 80},
                    "style": "glassmorphism-cart"
                }
            ])
            
        return elements
    
    def get_style_recommendations(self, style_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Get style recommendations based on preferences"""
        # Default to glassmorphism with olive greens as per user memory
        return {
            "theme": "glassmorphism",
            "primary_color": "#6B7B4F",  # Natural olive green
            "secondary_color": "#8AA159", 
            "accent_color": "#A8C573",
            "background": "linear-gradient(135deg, rgba(107,123,79,0.1), rgba(138,161,89,0.1))",
            "glassmorphism_properties": {
                "backdrop_filter": "blur(16px)",
                "background": "rgba(255, 255, 255, 0.1)",
                "border": "1px solid rgba(255, 255, 255, 0.2)",
                "border_radius": "16px",
                "box_shadow": "0 8px 32px 0 rgba(31, 38, 135, 0.37)"
            },
            "typography": {
                "font_family": "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
                "font_sizes": {
                    "h1": "2.5rem",
                    "h2": "2rem", 
                    "h3": "1.5rem",
                    "body": "1rem",
                    "small": "0.875rem"
                }
            }
        }
    
    def get_layout_suggestions(self, prompt: str) -> List[Dict[str, Any]]:
        """Get layout suggestions based on project prompt"""
        layouts = [
            {
                "name": "Modern Grid",
                "description": "Clean grid-based layout with glassmorphism cards",
                "suitable_for": ["dashboard", "portfolio", "business"]
            },
            {
                "name": "Center-focused",
                "description": "Centered content with hero section and glassmorphism effects",
                "suitable_for": ["landing", "saas", "marketing"]
            },
            {
                "name": "Sidebar Navigation",
                "description": "Side navigation with main content area and glassmorphism panels",
                "suitable_for": ["app", "dashboard", "admin"]
            }
        ]
        
        # Filter based on prompt content
        if "dashboard" in prompt.lower():
            return [l for l in layouts if "dashboard" in l["suitable_for"]]
        elif "landing" in prompt.lower():
            return [l for l in layouts if "landing" in l["suitable_for"]]
        
        return layouts
    
    async def create_figma_project(self, project_name: str, wireframes: List[PageWireframe]) -> str:
        """Create Figma project with wireframes"""
        if not self.figma_token:
            logger.warning("No Figma token provided, returning mock URL")
            return f"https://figma.com/mock-project/{project_name.lower().replace(' ', '-')}"
        
        try:
            headers = {
                "X-Figma-Token": self.figma_token,
                "Content-Type": "application/json"
            }
            
            # Create a new file in Figma (simplified)
            create_payload = {
                "name": f"{project_name} - Wireframes",
                "node_type": "FRAME"
            }
            
            async with httpx.AsyncClient() as client:
                # This is a simplified Figma API call - actual implementation would be more complex
                response = await client.post(
                    "https://api.figma.com/v1/files",
                    headers=headers,
                    json=create_payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    figma_data = response.json()
                    file_key = figma_data.get("key", "mock-file-key")
                    return f"https://figma.com/file/{file_key}/{project_name.replace(' ', '-')}"
                else:
                    logger.error(f"Figma API error: {response.status_code}")
                    return f"https://figma.com/mock-project/{project_name.lower().replace(' ', '-')}"
                    
        except Exception as e:
            logger.error(f"Error creating Figma project: {e}")
            return f"https://figma.com/mock-project/{project_name.lower().replace(' ', '-')}"
    
    def create_wireframe_elements(self, design_elements: List[Dict[str, Any]]) -> List[WireframeElement]:
        """Convert design elements to wireframe elements"""
        wireframe_elements = []
        
        for element in design_elements:
            wireframe_element = WireframeElement(
                type=element["type"],
                position=element["position"],
                content=element["content"],
                style_properties={
                    "style": element.get("style", "default"),
                    "glassmorphism": True
                }
            )
            wireframe_elements.append(wireframe_element)
            
        return wireframe_elements
    
    async def generate_design(self, request: DesignRequest) -> DesignRecommendation:
        """Generate complete design recommendation"""
        logger.info(f"Generating design for project type: {request.project_type}")
        
        # Ensure we have pages to design
        if not request.pages:
            if request.project_type == "web":
                request.pages = ["Home", "About", "Contact", "Services"]
            elif request.project_type == "mobile":
                request.pages = ["Welcome", "Dashboard", "Profile", "Settings"]
            else:
                request.pages = ["Main", "Secondary"]
        
        wireframes = []
        
        # Generate wireframes for each page
        for page_name in request.pages[:4]:  # Limit to 4 pages
            prompt = f"Create a {request.project_type} wireframe for {page_name} page with {request.color_scheme} style"
            
            # Call Galileo AI (mock)
            galileo_response = await self.call_galileo_ai(prompt, request.style_preferences)
            
            if galileo_response["status"] == "success":
                # Convert to wireframe elements
                wireframe_elements = self.create_wireframe_elements(
                    galileo_response["design_elements"]
                )
                
                # Create page wireframe
                page_wireframe = PageWireframe(
                    page_name=page_name,
                    page_type=page_name.lower(),
                    elements=wireframe_elements,
                    metadata={
                        "generated_by": "DesignAgent",
                        "style": request.color_scheme,
                        "project_type": request.project_type
                    }
                )
                
                wireframes.append(page_wireframe)
        
        # Create Figma project
        project_name = f"{request.project_type.title()} Project"
        figma_url = await self.create_figma_project(project_name, wireframes)
        
        # Update wireframes with Figma URLs
        for i, wireframe in enumerate(wireframes):
            wireframe.figma_url = f"{figma_url}?page-id={i+1}"
            wireframe.preview_url = f"{figma_url}/preview?page-id={i+1}"
        
        # Get style recommendations
        style_guide = self.get_style_recommendations(request.style_preferences)
        
        # Create design system
        design_system = {
            "components": [
                "Button", "Card", "Modal", "Navigation", "Form", "Table"
            ],
            "glassmorphism_theme": True,
            "responsive_breakpoints": {
                "mobile": "768px",
                "tablet": "1024px", 
                "desktop": "1200px"
            },
            "spacing_scale": [4, 8, 16, 24, 32, 48, 64]
        }
        
        # Generate reasoning
        reasoning = f"Generated {len(wireframes)} wireframes for {request.project_type} project using glassmorphism design with natural olive green color scheme. "
        reasoning += f"Focused on modern UX patterns with accessible, clean layouts optimized for {request.target_audience or 'general users'}."
        
        return DesignRecommendation(
            project_type=request.project_type,
            wireframes=wireframes,
            style_guide=style_guide,
            figma_project_url=figma_url,
            design_system=design_system,
            reasoning=reasoning,
            estimated_dev_time=f"{len(wireframes) * 2}-{len(wireframes) * 3} days"
        )

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Design Agent")
    yield
    # Shutdown
    logger.info("Shutting down Design Agent")

app = FastAPI(
    title="Design Agent",
    description="Intelligent design and wireframe generation agent",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
design_agent = DesignAgent()

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Design Agent v1.0", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "OK", "agent": "design", "version": "1.0.0"}

@app.post("/generate", response_model=DesignRecommendation)
async def generate_design(
    request: DesignRequest,
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers),
    subscription: TenantSubscription = Depends(require_subscription(
        required_level=AccessLevel.STARTER,
        feature="basic_design",
        check_limits=True
    ))
):
    """Generate wireframes and design recommendations (Requires Starter+ subscription)"""
    try:
        recommendation = await design_agent.generate_design(request)
        return recommendation
    except Exception as e:
        logger.error(f"Error generating design: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/styles")
async def get_style_options():
    """Get available style options"""
    return {
        "themes": ["glassmorphism", "minimal", "modern", "classic"],
        "color_schemes": ["natural", "blue", "green", "purple", "orange"],
        "layout_types": ["clean", "grid", "asymmetric", "centered"]
    }

@app.get("/templates")
async def get_design_templates():
    """Get available design templates"""
    return {
        "web": ["Landing Page", "Dashboard", "E-commerce", "Blog", "Portfolio"],
        "mobile": ["Onboarding", "Social App", "E-commerce", "Productivity", "Health"],
        "dashboard": ["Analytics", "CRM", "Admin Panel", "Metrics", "Reports"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082) 