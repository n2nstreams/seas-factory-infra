import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typing import List

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Marketing Agent",
    description="Manages and sends retention email drips via SendGrid.",
    version="1.0.0"
)

# --- SendGrid Configuration ---
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = "noreply@saasfactory.com"

# --- User Data Model ---
class User(BaseModel):
    email: str
    name: str
    last_active: int  # Days since last active

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

# --- Email Drip Logic ---
@app.post("/trigger-drip")
async def trigger_drip_campaign():
    """
    Triggers the email drip campaign. This endpoint will be called by Cloud Scheduler.
    """
    if not SENDGRID_API_KEY:
        raise HTTPException(status_code=500, detail="SENDGRID_API_KEY not configured.")
    
    # In a real application, this would fetch users from a database
    # For this example, we'll use a dummy list of users
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
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    os.environ["SENDGRID_API_KEY"] = "your_sendgrid_api_key"
    uvicorn.run(app, host="0.0.0.0", port=8091) 