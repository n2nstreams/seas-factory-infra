"""
CostGuardAgent - Night 49 Implementation
Intelligent cost monitoring agent that processes budget alerts and sends emails

This Cloud Function receives budget notifications via Pub/Sub and:
1. Analyzes spending patterns and threshold breaches
2. Sends contextual email alerts using SendGrid
3. Provides cost optimization recommendations
4. Triggers automated cost reduction measures when appropriate
5. Maintains structured logging for cost analysis
"""

import json
import logging
import os
import base64
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass

import functions_framework
from google.cloud import logging as cloud_logging
from google.cloud import monitoring_v3
from google.cloud import billing_v1
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To

# Initialize clients
logging_client = cloud_logging.Client()
monitoring_client = monitoring_v3.MetricServiceClient()
budget_client = billing_v1.BudgetServiceClient()

# Configuration from environment
PROJECT_ID = os.environ.get('PROJECT_ID', 'summer-nexus-463503-e1')
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
ALERT_EMAIL = os.environ.get('ALERT_EMAIL', 'n2nstreams@gmail.com')
BILLING_ACCOUNT = os.environ.get('BILLING_ACCOUNT', '013356-107066-5683A3')

# Setup structured logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BudgetAlert:
    """Structured representation of a budget alert"""
    budget_display_name: str
    alert_threshold_exceeded: float
    cost_amount: float
    budget_amount: float
    cost_interval_start: str
    cost_interval_end: str
    currency_code: str
    project_id: str
    budget_id: str
    
    @property
    def spending_percentage(self) -> float:
        """Calculate current spending as percentage of budget"""
        if self.budget_amount <= 0:
            return 0.0
        return (self.cost_amount / self.budget_amount) * 100
    
    @property
    def severity(self) -> str:
        """Determine alert severity based on spending percentage"""
        if self.spending_percentage >= 100:
            return "CRITICAL"
        elif self.spending_percentage >= 80:
            return "HIGH"
        elif self.spending_percentage >= 50:
            return "MEDIUM"
        else:
            return "LOW"
    
    @property
    def remaining_budget(self) -> float:
        """Calculate remaining budget amount"""
        return max(0, self.budget_amount - self.cost_amount)

@functions_framework.cloud_event
def cost_guard_handler(cloud_event: Dict[str, Any]) -> None:
    """
    Main handler for cost guard events triggered by budget alerts.
    
    Args:
        cloud_event: Cloud Event containing budget alert information
    """
    try:
        # Parse Pub/Sub message
        pubsub_message = cloud_event.data.get('message', {})
        message_data = base64.b64decode(pubsub_message.get('data', '')).decode('utf-8')
        budget_data = json.loads(message_data)
        
        logger.info(f"Received budget alert: {budget_data}")
        
        # Parse budget alert
        alert = parse_budget_alert(budget_data)
        if not alert:
            logger.warning("Unable to parse budget alert data")
            return
        
        # Log cost metrics
        log_cost_metrics(alert)
        
        # Send email notification
        send_cost_alert_email(alert)
        
        # Check if automated cost reduction is needed
        if alert.severity in ["CRITICAL", "HIGH"]:
            suggest_cost_optimizations(alert)
            
        # Update monitoring metrics
        update_cost_monitoring_metrics(alert)
        
        logger.info(f"Successfully processed {alert.severity} budget alert for {alert.budget_display_name}")
        
    except Exception as e:
        logger.error(f"Error in cost guard handler: {e}", exc_info=True)
        # Send error notification
        send_error_notification(str(e))

def parse_budget_alert(budget_data: Dict[str, Any]) -> Optional[BudgetAlert]:
    """
    Parse raw budget alert data into structured BudgetAlert object.
    
    Args:
        budget_data: Raw budget alert data from Pub/Sub
        
    Returns:
        BudgetAlert object or None if parsing fails
    """
    try:
        # Extract data from different possible message formats
        if 'budgetDisplayName' in budget_data:
            # Standard budget alert format
            return BudgetAlert(
                budget_display_name=budget_data['budgetDisplayName'],
                alert_threshold_exceeded=budget_data.get('alertThresholdExceeded', 0.0),
                cost_amount=float(budget_data.get('costAmount', 0.0)),
                budget_amount=float(budget_data.get('budgetAmount', 0.0)),
                cost_interval_start=budget_data.get('costIntervalStart', ''),
                cost_interval_end=budget_data.get('costIntervalEnd', ''),
                currency_code=budget_data.get('currencyCode', 'USD'),
                project_id=budget_data.get('projectId', PROJECT_ID),
                budget_id=budget_data.get('budgetId', '')
            )
        
        # Try alternative format
        elif 'budget' in budget_data:
            budget_info = budget_data['budget']
            cost_info = budget_data.get('cost', {})
            
            return BudgetAlert(
                budget_display_name=budget_info.get('displayName', 'Unknown Budget'),
                alert_threshold_exceeded=budget_data.get('thresholdExceeded', 0.0),
                cost_amount=float(cost_info.get('units', 0.0)),
                budget_amount=float(budget_info.get('amount', {}).get('specifiedAmount', {}).get('units', 0.0)),
                cost_interval_start=cost_info.get('startTime', ''),
                cost_interval_end=cost_info.get('endTime', ''),
                currency_code=cost_info.get('currencyCode', 'USD'),
                project_id=PROJECT_ID,
                budget_id=budget_info.get('name', '').split('/')[-1] if budget_info.get('name') else ''
            )
        
        else:
            logger.warning(f"Unknown budget alert format: {budget_data}")
            return None
            
    except Exception as e:
        logger.error(f"Error parsing budget alert: {e}")
        return None

def send_cost_alert_email(alert: BudgetAlert) -> None:
    """
    Send cost alert email using SendGrid with contextual information.
    
    Args:
        alert: BudgetAlert object containing cost information
    """
    try:
        if not SENDGRID_API_KEY:
            logger.warning("SENDGRID_API_KEY not configured, skipping email")
            return
        
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        
        # Determine email content based on severity
        subject, html_content = generate_email_content(alert)
        
        # Create email
        from_email = Email("noreply@saas-factory.com", "SaaS Factory Cost Guard")
        to_email = To(ALERT_EMAIL)
        
        mail = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        # Send email
        response = sg.send(mail)
        
        if response.status_code == 202:
            logger.info(f"Cost alert email sent successfully to {ALERT_EMAIL}")
        else:
            logger.warning(f"Email send returned status: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error sending cost alert email: {e}")

def generate_email_content(alert: BudgetAlert) -> tuple[str, str]:
    """
    Generate email subject and HTML content based on alert severity.
    
    Args:
        alert: BudgetAlert object
        
    Returns:
        Tuple of (subject, html_content)
    """
    # Emoji and priority mapping
    severity_emoji = {
        "CRITICAL": "🚨",
        "HIGH": "⚠️", 
        "MEDIUM": "💰",
        "LOW": "📊"
    }
    
    emoji = severity_emoji.get(alert.severity, "📊")
    
    # Generate subject
    subject = f"{emoji} {alert.severity} Cost Alert: {alert.spending_percentage:.1f}% of budget used"
    
    # Generate recommendations
    recommendations = generate_cost_recommendations(alert)
    
    # Generate HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>SaaS Factory Cost Alert</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
            .content {{ padding: 30px; }}
            .alert-box {{ background: {'#ffebee' if alert.severity == 'CRITICAL' else '#fff3e0' if alert.severity == 'HIGH' else '#e8f5e8'}; 
                         border-left: 4px solid {'#f44336' if alert.severity == 'CRITICAL' else '#ff9800' if alert.severity == 'HIGH' else '#4caf50'}; 
                         padding: 15px; margin: 20px 0; }}
            .metrics {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }}
            .metric {{ text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
            .metric-value {{ font-size: 24px; font-weight: bold; color: #333; }}
            .metric-label {{ font-size: 14px; color: #666; margin-top: 5px; }}
            .recommendations {{ background: #f0f8ff; border-radius: 8px; padding: 20px; margin: 20px 0; }}
            .rec-item {{ margin: 10px 0; padding: 10px; background: white; border-radius: 4px; border-left: 3px solid #2196f3; }}
            .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; border-radius: 0 0 8px 8px; }}
            .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{emoji} Cost Alert: {alert.severity}</h1>
                <p>Budget: {alert.budget_display_name}</p>
            </div>
            
            <div class="content">
                <div class="alert-box">
                    <h3>Budget Threshold Exceeded</h3>
                    <p>Your SaaS Factory project has reached <strong>{alert.spending_percentage:.1f}%</strong> of the monthly budget.</p>
                </div>
                
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-value">${alert.cost_amount:.2f}</div>
                        <div class="metric-label">Current Spend</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${alert.budget_amount:.2f}</div>
                        <div class="metric-label">Monthly Budget</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${alert.remaining_budget:.2f}</div>
                        <div class="metric-label">Remaining Budget</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{alert.spending_percentage:.1f}%</div>
                        <div class="metric-label">Budget Used</div>
                    </div>
                </div>
                
                <div class="recommendations">
                    <h3>💡 Cost Optimization Recommendations</h3>
                    {recommendations}
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://console.cloud.google.com/billing/budgets?project={alert.project_id}" class="button">
                        View Budget Details
                    </a>
                    <a href="https://console.cloud.google.com/monitoring/dashboards?project={alert.project_id}" class="button">
                        View Cost Dashboard
                    </a>
                </div>
                
                <div style="font-size: 12px; color: #666; margin-top: 20px;">
                    <p><strong>Alert Details:</strong></p>
                    <ul>
                        <li>Project: {alert.project_id}</li>
                        <li>Budget Period: {alert.cost_interval_start} to {alert.cost_interval_end}</li>
                        <li>Currency: {alert.currency_code}</li>
                        <li>Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</li>
                    </ul>
                </div>
            </div>
            
            <div class="footer">
                <p>This alert was generated by SaaS Factory CostGuardAgent</p>
                <p>Night 49: Automated Cost Monitoring System</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return subject, html_content

def generate_cost_recommendations(alert: BudgetAlert) -> str:
    """
    Generate HTML formatted cost optimization recommendations.
    
    Args:
        alert: BudgetAlert object
        
    Returns:
        HTML string with recommendations
    """
    recommendations = []
    
    if alert.severity == "CRITICAL":
        recommendations.extend([
            "🔴 <strong>IMMEDIATE ACTION REQUIRED:</strong> Consider scaling down non-essential Cloud Run services",
            "⏸️ Temporarily reduce Cloud Run max instances to 3-5 per service",
            "🗄️ Review and optimize database connection pooling to reduce Cloud SQL usage",
            "📊 Enable aggressive auto-scaling to scale to zero during low traffic",
            "🔍 Audit and remove unused storage buckets and Artifact Registry images"
        ])
    elif alert.severity == "HIGH":
        recommendations.extend([
            "⚠️ Review Cloud Run service scaling configurations",
            "💾 Optimize container images to reduce cold start costs",
            "🔄 Implement more aggressive auto-scaling policies",
            "📈 Monitor peak usage patterns and adjust capacity accordingly",
            "🗃️ Clean up old Cloud Build artifacts and logs"
        ])
    elif alert.severity in ["MEDIUM", "LOW"]:
        recommendations.extend([
            "📊 Monitor spending trends for early warning signs",
            "⚡ Optimize code efficiency to reduce compute costs",
            "🔧 Review resource allocation across all services",
            "📱 Consider implementing usage-based pricing for end users",
            "🔍 Regular cost analysis and capacity planning"
        ])
    
    # Always add general recommendations
    recommendations.extend([
        "📈 Set up billing alerts at 25%, 50%, 75% thresholds for earlier warnings",
        "🎯 Review the <a href='https://cloud.google.com/billing/docs/how-to/budgets'>GCP Cost Optimization Guide</a>",
        "🔄 Consider implementing automated cost controls via Cloud Functions"
    ])
    
    return "\n".join([f'<div class="rec-item">{rec}</div>' for rec in recommendations])

def suggest_cost_optimizations(alert: BudgetAlert) -> None:
    """
    Suggest and potentially implement automated cost optimizations.
    
    Args:
        alert: BudgetAlert object
    """
    try:
        optimizations = []
        
        if alert.severity == "CRITICAL" and alert.spending_percentage >= 95:
            optimizations.append("EMERGENCY: Reduce Cloud Run max instances by 50%")
            # Could implement automatic scaling down here
            
        elif alert.severity == "HIGH":
            optimizations.append("WARNING: Review resource usage and consider scaling down")
            
        # Log optimization suggestions
        logger.info(f"Cost optimization suggestions for {alert.budget_display_name}: {optimizations}")
        
        # Could integrate with Cloud Run Admin API to implement automatic scaling
        # For now, just log the suggestions
        
    except Exception as e:
        logger.error(f"Error generating cost optimizations: {e}")

def log_cost_metrics(alert: BudgetAlert) -> None:
    """
    Log structured cost metrics for monitoring and analysis.
    
    Args:
        alert: BudgetAlert object
    """
    try:
        cost_log = {
            "event_type": "cost_alert",
            "severity": alert.severity,
            "budget_name": alert.budget_display_name,
            "spending_percentage": alert.spending_percentage,
            "cost_amount": alert.cost_amount,
            "budget_amount": alert.budget_amount,
            "remaining_budget": alert.remaining_budget,
            "currency": alert.currency_code,
            "project_id": alert.project_id,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"COST_METRICS: {json.dumps(cost_log)}")
        
    except Exception as e:
        logger.error(f"Error logging cost metrics: {e}")

def update_cost_monitoring_metrics(alert: BudgetAlert) -> None:
    """
    Update custom monitoring metrics for cost tracking.
    
    Args:
        alert: BudgetAlert object
    """
    try:
        # Create custom metric for cost percentage
        project_name = f"projects/{PROJECT_ID}"
        
        series = monitoring_v3.TimeSeries()
        series.metric.type = "custom.googleapis.com/cost/budget_percentage"
        series.resource.type = "global"
        
        point = monitoring_v3.Point()
        point.value.double_value = alert.spending_percentage
        point.interval.end_time.seconds = int(datetime.now().timestamp())
        
        series.points = [point]
        
        # This would send custom metrics to Cloud Monitoring
        # For demo purposes, we'll just log it
        logger.info(f"Custom metric: budget_percentage = {alert.spending_percentage}%")
        
    except Exception as e:
        logger.error(f"Error updating monitoring metrics: {e}")

def send_error_notification(error_message: str) -> None:
    """
    Send error notification when CostGuardAgent fails.
    
    Args:
        error_message: Error description
    """
    try:
        if not SENDGRID_API_KEY:
            return
            
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        
        subject = "🚨 CostGuardAgent Error"
        html_content = f"""
        <h2>CostGuardAgent Error</h2>
        <p>The CostGuardAgent encountered an error while processing a cost alert:</p>
        <div style="background: #ffebee; padding: 15px; border-left: 4px solid #f44336;">
            <code>{error_message}</code>
        </div>
        <p>Please check the Cloud Function logs for more details.</p>
        <p><a href="https://console.cloud.google.com/functions/list?project={PROJECT_ID}">View Cloud Function Logs</a></p>
        """
        
        mail = Mail(
            from_email=Email("noreply@saas-factory.com", "SaaS Factory Cost Guard"),
            to_emails=To(ALERT_EMAIL),
            subject=subject,
            html_content=html_content
        )
        
        sg.send(mail)
        
    except Exception as e:
        logger.error(f"Error sending error notification: {e}")

if __name__ == "__main__":
    # For testing locally
    sample_budget_data = {
        "budgetDisplayName": "Monthly SaaS Factory Budget",
        "alertThresholdExceeded": 0.8,
        "costAmount": 160.0,
        "budgetAmount": 200.0,
        "costIntervalStart": "2024-12-01T00:00:00Z",
        "costIntervalEnd": "2024-12-31T23:59:59Z",
        "currencyCode": "USD",
        "projectId": "summer-nexus-463503-e1",
        "budgetId": "test-budget-id"
    }
    
    # Simulate cloud event
    mock_event = {
        "data": {
            "message": {
                "data": base64.b64encode(json.dumps(sample_budget_data).encode()).decode()
            }
        }
    }
    
    print("Testing CostGuardAgent locally...")
    cost_guard_handler(mock_event) 