import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
from typing import List, Optional, Dict, Any
from google.cloud import bigquery
import uuid
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Experiment Agent",
    description="Manages A/B tests and logs metrics to BigQuery.",
    version="1.0.0"
)

# --- GrowthBook API Configuration ---
GROWTHBOOK_API_HOST = os.getenv("GROWTHBOOK_API_HOST", "https://api.growthbook.io")
GROWTHBOOK_API_KEY = os.getenv("GROWTHBOOK_API_KEY")

# --- BigQuery Configuration ---
BQ_PROJECT_ID = os.getenv("BQ_PROJECT_ID")
BQ_DATASET_ID = "saas_factory_experiments"
BQ_TABLE_ID = "experiment_events"
bq_client = bigquery.Client(project=BQ_PROJECT_ID) if BQ_PROJECT_ID else None


# --- Pydantic Models ---
class Variation(BaseModel):
    name: str
    key: Optional[str] = None
    screenshots: List[str] = []
    description: Optional[str] = None

class Experiment(BaseModel):
    key: str
    name: str
    datasourceId: str
    variations: List[Variation]

class ExperimentEvent(BaseModel):
    user_id: str
    experiment_key: str
    variation_id: str
    event_name: str
    properties: Optional[Dict[str, Any]] = {}


@app.post("/experiment")
async def create_experiment(experiment: Experiment):
    """
    Creates an experiment in GrowthBook.
    """
    if not GROWTHBOOK_API_KEY:
        raise HTTPException(status_code=500, detail="GROWTHBOOK_API_KEY not set.")
    
    headers = {
        "Authorization": f"Bearer {GROWTHBOOK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # The GrowthBook API endpoint for creating an experiment might be different,
    # this is a placeholder. You'll need to replace it with the actual endpoint.
    url = f"{GROWTHBOOK_API_HOST}/api/v1/experiments"
    
    try:
        response = requests.post(url, headers=headers, json=experiment.dict())
        response.raise_for_status()
        logger.info(f"Successfully created experiment: {experiment.key}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating experiment in GrowthBook: {e}")
        raise HTTPException(status_code=502, detail="Failed to communicate with GrowthBook API.")


@app.post("/log_event")
async def log_event(event: ExperimentEvent):
    """ Logs an experiment event to BigQuery. """
    if not bq_client:
        raise HTTPException(status_code=500, detail="BigQuery client not configured.")

    table_ref = bq_client.dataset(BQ_DATASET_ID).table(BQ_TABLE_ID)
    row_to_insert = {
        "event_id": str(uuid.uuid4()),
        "user_id": event.user_id,
        "experiment_key": event.experiment_key,
        "variation_id": event.variation_id,
        "event_name": event.event_name,
        "timestamp": datetime.utcnow().isoformat(),
        "properties": json.dumps(event.properties)
    }

    errors = bq_client.insert_rows_json(table_ref, [row_to_insert])
    if errors:
        logger.error(f"Error inserting rows to BigQuery: {errors}")
        raise HTTPException(status_code=500, detail="Failed to log event to BigQuery.")

    logger.info(f"Successfully logged event: {event.event_name}")
    return {"status": "success"}


@app.get("/health")
async def health_check():
    """Health check endpoint to verify service is running."""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    # Example of how to add the API key for local testing
    # In a real scenario, this would be in your .env file
    os.environ["GROWTHBOOK_API_KEY"] = "your_growthbook_api_key"
    # For local testing, you might need to set up Google Application Credentials
    # export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
    uvicorn.run(app, host="0.0.0.0", port=8090) 