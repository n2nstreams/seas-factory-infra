import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typing import List, Dict, Optional
import openai
from enum import Enum
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Marketing Agent with CopyWriter",
    description="Manages email drips and generates compelling marketing landing copy via AI.",
    version="2.0.0"
)

# --- Configuration ---
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FROM_EMAIL = "noreply@saasfactory.com"

# Initialize OpenAI client
openai_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# --- Enums and Data Models ---
class CopyType(str, Enum):
    HERO_SECTION = "hero_section"
    FEATURES = "features"
    PRICING = "pricing"
    TESTIMONIALS = "testimonials"
    FAQ = "faq"
    CTA = "cta"
    ABOUT = "about"
    FULL_LANDING = "full_landing"

class ToneOfVoice(str, Enum):
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    TECHNICAL = "technical"
    STARTUP = "startup"
    ENTERPRISE = "enterprise"

class User(BaseModel):
    email: str
    name: str
    last_active: int  # Days since last active

class CopyRequest(BaseModel):
    copy_type: CopyType = Field(..., description="Type of marketing copy to generate")
    product_name: str = Field(..., description="Name of the SaaS product")
    product_description: str = Field(..., description="Brief description of what the product does")
    target_audience: str = Field(..., description="Primary target audience")
    key_features: List[str] = Field(default=[], description="Key features to highlight")
    tone: ToneOfVoice = Field(default=ToneOfVoice.PROFESSIONAL, description="Tone of voice for the copy")
    pricing_tiers: Optional[List[Dict[str, str]]] = Field(default=None, description="Pricing information if relevant")
    company_values: Optional[str] = Field(default="", description="Company values and mission")
    competitor_analysis: Optional[str] = Field(default="", description="Information about competitors")

class GeneratedCopy(BaseModel):
    copy_type: CopyType
    content: str
    alternatives: List[str] = Field(default=[], description="Alternative versions of the copy")
    metadata: Dict[str, str] = Field(default={}, description="Additional metadata about the generated copy")

class LandingPageCopy(BaseModel):
    hero_section: GeneratedCopy
    features: GeneratedCopy
    pricing: GeneratedCopy
    testimonials: GeneratedCopy
    faq: GeneratedCopy
    cta: GeneratedCopy
    about: GeneratedCopy

# --- CopyWriter Agent Class ---
class CopyWriterAgent:
    """Advanced AI-powered copywriter for SaaS marketing materials"""
    
    def __init__(self):
        self.client = openai_client
        self.model = "gpt-4o"
        
    def _get_system_prompt(self, copy_type: CopyType, tone: ToneOfVoice) -> str:
        """Generate system prompt based on copy type and tone"""
        base_prompt = f"""You are a world-class copywriter specializing in SaaS marketing copy with a {tone.value} tone. 
You understand conversion psychology, user pain points, and how to craft compelling calls-to-action.

Key principles:
- Focus on benefits over features
- Address specific pain points
- Use social proof when appropriate
- Create urgency without being pushy
- Write with clarity and precision
- Follow modern web copy best practices"""

        type_specific_prompts = {
            CopyType.HERO_SECTION: """
For hero sections:
- Lead with a clear value proposition
- Address the main pain point immediately
- Include a compelling headline and subheadline
- End with a strong call-to-action
- Keep it scannable and concise""",
            
            CopyType.FEATURES: """
For features sections:
- Transform features into benefits
- Use outcome-focused language
- Include specific use cases
- Highlight competitive advantages
- Structure for easy scanning""",
            
            CopyType.PRICING: """
For pricing sections:
- Emphasize value over cost
- Use anchoring techniques
- Highlight the most popular option
- Address common objections
- Include compelling tier benefits""",
            
            CopyType.TESTIMONIALS: """
For testimonials:
- Create believable, specific testimonials
- Include metrics and outcomes
- Vary the testimonial types
- Include company context
- Focus on transformation stories""",
            
            CopyType.FAQ: """
For FAQ sections:
- Address common objections
- Include practical questions
- Provide clear, helpful answers
- Reduce purchase friction
- Build trust and confidence""",
            
            CopyType.CTA: """
For call-to-action copy:
- Create urgency and desire
- Use action-oriented language
- Reduce friction words
- Test multiple variations
- Focus on the outcome, not the action""",
            
            CopyType.ABOUT: """
For about sections:
- Tell a compelling story
- Connect with user pain points
- Establish credibility
- Show the human side
- Link back to the product value"""
        }
        
        return base_prompt + "\n\n" + type_specific_prompts.get(copy_type, "")
    
    def _build_copy_prompt(self, request: CopyRequest) -> str:
        """Build the specific prompt for copy generation"""
        prompt = f"""Generate compelling {request.copy_type.value} copy for a SaaS product with these details:

Product Name: {request.product_name}
Product Description: {request.product_description}
Target Audience: {request.target_audience}
Key Features: {', '.join(request.key_features)}
Tone: {request.tone.value}"""

        if request.company_values:
            prompt += f"\nCompany Values: {request.company_values}"
        
        if request.competitor_analysis:
            prompt += f"\nCompetitor Context: {request.competitor_analysis}"
        
        if request.pricing_tiers and request.copy_type == CopyType.PRICING:
            prompt += f"\nPricing Tiers: {json.dumps(request.pricing_tiers, indent=2)}"
        
        # Add specific instructions based on copy type
        if request.copy_type == CopyType.HERO_SECTION:
            prompt += "\n\nGenerate a complete hero section including: headline, subheadline, and primary CTA button text."
        elif request.copy_type == CopyType.FEATURES:
            prompt += "\n\nGenerate 3-5 key feature sections with benefit-focused headlines and descriptions."
        elif request.copy_type == CopyType.TESTIMONIALS:
            prompt += "\n\nGenerate 3-4 believable customer testimonials with names, companies, and specific outcomes."
        elif request.copy_type == CopyType.FAQ:
            prompt += "\n\nGenerate 5-7 FAQ items that address common objections and build confidence."
        elif request.copy_type == CopyType.CTA:
            prompt += "\n\nGenerate multiple CTA button texts and supporting copy for different page sections."
        
        return prompt
    
    async def generate_copy(self, request: CopyRequest) -> GeneratedCopy:
        """Generate marketing copy based on the request"""
        if not self.client:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        try:
            system_prompt = self._get_system_prompt(request.copy_type, request.tone)
            user_prompt = self._build_copy_prompt(request)
            
            # Generate main copy
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            main_content = response.choices[0].message.content
            
            # Generate alternatives
            alt_prompt = user_prompt + "\n\nGenerate 2 alternative versions with different approaches but same core message."
            alt_response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": alt_prompt}
                ],
                temperature=0.8,
                max_tokens=1500
            )
            
            alternatives = alt_response.choices[0].message.content.split("\n\n---\n\n") if alt_response.choices[0].message.content else []
            
            return GeneratedCopy(
                copy_type=request.copy_type,
                content=main_content,
                alternatives=alternatives[:2],  # Limit to 2 alternatives
                metadata={
                    "product_name": request.product_name,
                    "tone": request.tone.value,
                    "target_audience": request.target_audience,
                    "generated_at": str(os.times())
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating copy: {e}")
            raise HTTPException(status_code=500, detail=f"Copy generation failed: {str(e)}")
    
    async def generate_full_landing_page(self, request: CopyRequest) -> LandingPageCopy:
        """Generate a complete landing page with all sections"""
        sections = {}
        
        for copy_type in [CopyType.HERO_SECTION, CopyType.FEATURES, CopyType.PRICING, 
                         CopyType.TESTIMONIALS, CopyType.FAQ, CopyType.CTA, CopyType.ABOUT]:
            section_request = CopyRequest(
                copy_type=copy_type,
                product_name=request.product_name,
                product_description=request.product_description,
                target_audience=request.target_audience,
                key_features=request.key_features,
                tone=request.tone,
                pricing_tiers=request.pricing_tiers,
                company_values=request.company_values,
                competitor_analysis=request.competitor_analysis
            )
            
            sections[copy_type.value] = await self.generate_copy(section_request)
        
        return LandingPageCopy(
            hero_section=sections["hero_section"],
            features=sections["features"],
            pricing=sections["pricing"],
            testimonials=sections["testimonials"],
            faq=sections["faq"],
            cta=sections["cta"],
            about=sections["about"]
        )

# Initialize CopyWriter Agent
copywriter = CopyWriterAgent()

# --- Email Templates ---
def get_email_template(user: User):
    if user.last_active == 7:
        return {
            "subject": "We miss you at SaaS Factory!",
            "html_content": f"Hi {user.name},<br><br>It's been a week since you last logged in. We're constantly adding new features to help you build amazing SaaS products. Come back and check them out!"
        }
    elif user.last_active == 30:
        return {
            "subject": "Your SaaS Factory projects are waiting for you",
            "html_content": f"Hi {user.name},<br><br>It's been a month since you last visited. Don't let your great ideas gather dust. Log back in to continue building the next big thing."
        }
    return None

# --- CopyWriter API Endpoints ---
@app.post("/generate-copy", response_model=GeneratedCopy)
async def generate_copy(request: CopyRequest):
    """Generate specific marketing copy section"""
    logger.info(f"Generating {request.copy_type} copy for {request.product_name}")
    return await copywriter.generate_copy(request)

@app.post("/generate-landing-page", response_model=LandingPageCopy)
async def generate_landing_page(request: CopyRequest):
    """Generate complete landing page copy"""
    logger.info(f"Generating full landing page for {request.product_name}")
    return await copywriter.generate_full_landing_page(request)

@app.get("/copy-templates")
async def get_copy_templates():
    """Get available copy types and templates"""
    return {
        "copy_types": [e.value for e in CopyType],
        "tones": [e.value for e in ToneOfVoice],
        "example_request": {
            "copy_type": "hero_section",
            "product_name": "TaskFlow Pro",
            "product_description": "AI-powered project management for remote teams",
            "target_audience": "Remote team managers and productivity enthusiasts",
            "key_features": ["AI task prioritization", "Real-time collaboration", "Advanced analytics"],
            "tone": "professional"
        }
    }

# --- Email Drip Endpoints ---
@app.post("/trigger-drip")
async def trigger_drip_campaign():
    """Triggers the email drip campaign. This endpoint will be called by Cloud Scheduler."""
    if not SENDGRID_API_KEY:
        raise HTTPException(status_code=500, detail="SENDGRID_API_KEY not configured.")
    
    # In a real application, this would fetch users from a database
    dummy_users = [
        User(email="user1@example.com", name="Alex", last_active=7),
        User(email="user2@example.com", name="Maria", last_active=30),
        User(email="user3@example.com", name="John", last_active=2),
    ]

    sg = SendGridAPIClient(SENDGRID_API_KEY)
    
    for user in dummy_users:
        template = get_email_template(user)
        if template:
            message = Mail(
                from_email=FROM_EMAIL,
                to_emails=user.email,
                subject=template["subject"],
                html_content=template["html_content"]
            )
            try:
                response = sg.send(message)
                logger.info(f"Sent email to {user.email}, status code: {response.status_code}")
            except Exception as e:
                logger.error(f"Error sending email to {user.email}: {e}")

    return {"status": "success", "detail": "Email drip campaign process completed."}

@app.get("/health")
async def health_check():
    """Health check endpoint to verify service is running."""
    return {"status": "ok", "copywriter_enabled": openai_client is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8091) 