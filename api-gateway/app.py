from fastapi import FastAPI, Request, HTTPException
import httpx
import os

ORCH_ENDPOINT = os.getenv("ORCH_ENDPOINT")  # Vertex AI Agent URL
TIMEOUT = int(os.getenv("ORCH_TIMEOUT", "30"))
app = FastAPI()

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

@app.get("/health")
async def health():
    return {"status": "healthy", "orch_endpoint": ORCH_ENDPOINT} 