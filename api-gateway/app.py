from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

ORCH_ENDPOINT = os.getenv("ORCH_ENDPOINT")  # Vertex AI Agent URL
DESIGN_AGENT_URL = os.getenv("DESIGN_AGENT_URL", "http://localhost:8082")
TECHSTACK_AGENT_URL = os.getenv("TECHSTACK_AGENT_URL", "http://localhost:8081")
TIMEOUT = int(os.getenv("ORCH_TIMEOUT", "30"))
BILLING_AGENT_URL = os.getenv("BILLING_AGENT_URL", "http://localhost:8084")

app = FastAPI(title="SaaS Factory API Gateway", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/orchestrate")
async def orchestrate(req: Request):
    try:
        payload = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    if not ORCH_ENDPOINT:
        raise HTTPException(status_code=500, detail="ORCH_ENDPOINT not configured")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            r = await client.post(ORCH_ENDPOINT, json=payload)
            # Try to parse as JSON, fallback to text if it fails
            try:
                response_data = r.json()
            except:
                response_data = r.text
            
            return {"data": response_data, "status": r.status_code}
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

@app.post("/api/design/generate")
async def generate_design(req: Request):
    """Proxy requests to Design Agent"""
    try:
        payload = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            r = await client.post(f"{DESIGN_AGENT_URL}/generate", json=payload)
            if r.status_code == 200:
                return r.json()
            else:
                raise HTTPException(status_code=r.status_code, detail=r.text)
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Design service unavailable: {str(e)}")

@app.get("/api/design/styles")
async def get_design_styles():
    """Get available design styles from Design Agent"""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            r = await client.get(f"{DESIGN_AGENT_URL}/styles")
            if r.status_code == 200:
                return r.json()
            else:
                raise HTTPException(status_code=r.status_code, detail=r.text)
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Design service unavailable: {str(e)}")

@app.get("/api/design/templates")
async def get_design_templates():
    """Get available design templates from Design Agent"""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            r = await client.get(f"{DESIGN_AGENT_URL}/templates")
            if r.status_code == 200:
                return r.json()
            else:
                raise HTTPException(status_code=r.status_code, detail=r.text)
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Design service unavailable: {str(e)}")

@app.post("/api/techstack/recommend")
async def recommend_techstack(req: Request):
    """Proxy requests to TechStack Agent"""
    try:
        payload = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            r = await client.post(f"{TECHSTACK_AGENT_URL}/recommend", json=payload)
            if r.status_code == 200:
                return r.json()
            else:
                raise HTTPException(status_code=r.status_code, detail=r.text)
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"TechStack service unavailable: {str(e)}")

@app.get("/api/techstack/categories")
async def get_techstack_categories():
    """Get available project categories from TechStack Agent"""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            r = await client.get(f"{TECHSTACK_AGENT_URL}/categories")
            if r.status_code == 200:
                return r.json()
            else:
                raise HTTPException(status_code=r.status_code, detail=r.text)
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"TechStack service unavailable: {str(e)}")

@app.post("/api/billing/create-customer")
async def billing_create_customer(req: Request):
    try:
        payload = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            r = await client.post(f"{BILLING_AGENT_URL}/create-customer", json=payload)
            return r.json() if r.status_code == 200 else HTTPException(status_code=r.status_code, detail=r.text)
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Billing service unavailable: {str(e)}")

@app.post("/api/billing/create-checkout-session")
async def billing_create_checkout_session(req: Request):
    try:
        payload = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            r = await client.post(f"{BILLING_AGENT_URL}/create-checkout-session", json=payload)
            return r.json() if r.status_code == 200 else HTTPException(status_code=r.status_code, detail=r.text)
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Billing service unavailable: {str(e)}")

@app.post("/api/billing/webhook")
async def billing_webhook(req: Request):
    try:
        payload = await req.body()
        signature = req.headers.get("stripe-signature")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            r = await client.post(f"{BILLING_AGENT_URL}/webhook", content=payload, headers={"stripe-signature": signature or ""})
            return r.json() if r.status_code == 200 else HTTPException(status_code=r.status_code, detail=r.text)
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Billing service unavailable: {str(e)}")

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "orch_endpoint": ORCH_ENDPOINT,
        "design_agent": DESIGN_AGENT_URL,
        "techstack_agent": TECHSTACK_AGENT_URL
    } 