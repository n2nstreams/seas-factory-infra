"""
Auto-Rollback Cloud Function for Blue-Green Deployments
Night 48 - Multi-region rollout script support

This function is triggered by Cloud Monitoring alerts when deployment health
checks fail and automatically rolls back the deployment to the stable version.
"""

import json
import logging
import os
import base64
from typing import Dict, Any

from google.cloud import run_v2
from google.cloud import logging as cloud_logging
from google.cloud import monitoring_v3

# Initialize clients
run_client = run_v2.ServicesClient()
logging_client = cloud_logging.Client()
monitoring_client = monitoring_v3.MetricServiceClient()

# Configuration from environment variables
PROJECT_ID = os.environ.get('PROJECT_ID', '${project_id}')
PRIMARY_REGION = os.environ.get('PRIMARY_REGION', '${primary_region}')
SECONDARY_REGION = os.environ.get('SECONDARY_REGION', '${secondary_region}')

# Setup structured logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rollback_handler(cloud_event: Dict[str, Any]) -> None:
    """
    Main handler for rollback events triggered by Pub/Sub.
    
    Args:
        cloud_event: Cloud Event containing the alert information
    """
    try:
        # Parse the Pub/Sub message
        pubsub_message = cloud_event.get('data', {})
        if isinstance(pubsub_message, str):
            message_data = base64.b64decode(pubsub_message).decode('utf-8')
        else:
            message_data = json.dumps(pubsub_message)
        
        alert_data = json.loads(message_data)
        
        logger.info(f"Received rollback trigger: {alert_data}")
        
        # Extract incident information
        incident = alert_data.get('incident', {})
        policy_name = incident.get('policy_name', '')
        condition_name = incident.get('condition_name', '')
        state = incident.get('state', '')
        
        # Only process OPEN incidents (active alerts)
        if state != 'OPEN':
            logger.info(f"Ignoring incident with state: {state}")
            return
        
        logger.info(f"Processing rollback for policy: {policy_name}, condition: {condition_name}")
        
        # Determine which services to rollback based on the alert
        services_to_rollback = determine_affected_services(alert_data)
        
        # Perform rollback for each affected service
        rollback_results = []
        for service_info in services_to_rollback:
            result = perform_rollback(service_info)
            rollback_results.append(result)
            
            # Log the rollback action
            log_rollback_action(service_info, result)
        
        # Send notification about rollback completion
        send_rollback_notification(rollback_results)
        
        logger.info("Rollback process completed successfully")
        
    except Exception as e:
        logger.error(f"Error in rollback handler: {e}", exc_info=True)
        raise

def determine_affected_services(alert_data: Dict[str, Any]) -> list:
    """
    Determine which services need to be rolled back based on the alert.
    
    Args:
        alert_data: Alert data from Cloud Monitoring
        
    Returns:
        List of service information dictionaries
    """
    services = []
    
    # Default to rolling back both regions if we can't determine specifics
    default_services = [
        {
            'name': 'api-backend',
            'region': PRIMARY_REGION,
            'service_id': f'projects/{PROJECT_ID}/locations/{PRIMARY_REGION}/services/api-backend'
        },
        {
            'name': 'api-backend-east',
            'region': SECONDARY_REGION,
            'service_id': f'projects/{PROJECT_ID}/locations/{SECONDARY_REGION}/services/api-backend-east'
        }
    ]
    
    # Try to extract specific service information from the alert
    try:
        incident = alert_data.get('incident', {})
        resource_name = incident.get('resource_name', '')
        
        if 'us-central1' in resource_name:
            services.append(default_services[0])
        elif 'us-east1' in resource_name:
            services.append(default_services[1])
        else:
            # If we can't determine the specific region, rollback both
            services = default_services
            
    except Exception as e:
        logger.warning(f"Could not determine specific service from alert: {e}")
        services = default_services
    
    logger.info(f"Services to rollback: {[s['name'] for s in services]}")
    return services

def perform_rollback(service_info: Dict[str, str]) -> Dict[str, Any]:
    """
    Perform rollback for a specific service.
    
    Args:
        service_info: Dictionary containing service name, region, and service_id
        
    Returns:
        Dictionary with rollback result information
    """
    service_name = service_info['name']
    region = service_info['region']
    service_id = service_info['service_id']
    
    logger.info(f"Starting rollback for {service_name} in {region}")
    
    try:
        # Get current service configuration
        service = run_client.get_service(name=service_id)
        
        # Find the blue (stable) revision
        blue_revision = None
        green_revision = None
        
        for traffic_entry in service.status.traffic:
            if hasattr(traffic_entry, 'tag'):
                if traffic_entry.tag == 'blue':
                    blue_revision = traffic_entry.revision_name
                elif traffic_entry.tag == 'green':
                    green_revision = traffic_entry.revision_name
        
        if not blue_revision:
            logger.error(f"No blue revision found for {service_name}")
            return {
                'service': service_name,
                'region': region,
                'success': False,
                'error': 'No blue revision found'
            }
        
        logger.info(f"Rolling back from green revision {green_revision} to blue revision {blue_revision}")
        
        # Update traffic to send 100% to blue revision
        new_traffic = [
            run_v2.TrafficTarget(
                type_=run_v2.TrafficTargetAllocationType.TRAFFIC_TARGET_ALLOCATION_TYPE_REVISION,
                revision=blue_revision,
                percent=100,
                tag='blue'
            )
        ]
        
        # Create update request
        update_request = run_v2.UpdateServiceRequest(
            service=run_v2.Service(
                name=service_id,
                spec=run_v2.ServiceSpec(
                    traffic=new_traffic
                )
            )
        )
        
        # Execute the rollback
        operation = run_client.update_service(request=update_request)
        logger.info(f"Rollback operation started for {service_name}: {operation.name}")
        
        # Wait for operation to complete (with timeout)
        result = operation.result(timeout=300)  # 5 minutes timeout
        
        logger.info(f"Rollback completed successfully for {service_name}")
        
        return {
            'service': service_name,
            'region': region,
            'success': True,
            'blue_revision': blue_revision,
            'green_revision': green_revision,
            'operation_name': operation.name
        }
        
    except Exception as e:
        logger.error(f"Rollback failed for {service_name}: {e}", exc_info=True)
        return {
            'service': service_name,
            'region': region,
            'success': False,
            'error': str(e)
        }

def log_rollback_action(service_info: Dict[str, str], result: Dict[str, Any]) -> None:
    """
    Log the rollback action to Cloud Logging with structured data.
    
    Args:
        service_info: Service information
        result: Rollback result
    """
    log_entry = {
        'severity': 'WARNING' if result['success'] else 'ERROR',
        'message': f"Automated rollback for {service_info['name']}",
        'rollback_details': {
            'service_name': service_info['name'],
            'region': service_info['region'],
            'success': result['success'],
            'timestamp': cloud_logging.Client().get_default_time(),
        }
    }
    
    if result['success']:
        log_entry['rollback_details'].update({
            'blue_revision': result.get('blue_revision'),
            'green_revision': result.get('green_revision'),
            'operation_name': result.get('operation_name')
        })
    else:
        log_entry['rollback_details']['error'] = result.get('error')
    
    # Log to Cloud Logging
    logger.info(json.dumps(log_entry))

def send_rollback_notification(rollback_results: list) -> None:
    """
    Send notification about rollback completion.
    
    Args:
        rollback_results: List of rollback results
    """
    successful_rollbacks = [r for r in rollback_results if r['success']]
    failed_rollbacks = [r for r in rollback_results if not r['success']]
    
    notification = {
        'type': 'automated_rollback_completed',
        'summary': f"Rollback completed: {len(successful_rollbacks)} successful, {len(failed_rollbacks)} failed",
        'successful_rollbacks': successful_rollbacks,
        'failed_rollbacks': failed_rollbacks,
        'timestamp': cloud_logging.Client().get_default_time()
    }
    
    logger.info(f"Rollback notification: {json.dumps(notification)}")
    
    # Here you could integrate with additional notification systems
    # like Slack, PagerDuty, etc. based on your requirements

def get_service_health_metrics(service_name: str, region: str) -> Dict[str, float]:
    """
    Get health metrics for a service to help determine rollback necessity.
    
    Args:
        service_name: Name of the Cloud Run service
        region: Region where the service is deployed
        
    Returns:
        Dictionary with health metrics
    """
    try:
        # This is a placeholder for more sophisticated health checking
        # You could query metrics like error rate, latency, etc.
        project_name = f"projects/{PROJECT_ID}"
        
        # Example metric query for error rate
        interval = monitoring_v3.TimeInterval({
            "end_time": {"seconds": int(cloud_logging.Client().get_default_time().timestamp())},
            "start_time": {"seconds": int(cloud_logging.Client().get_default_time().timestamp()) - 300}  # Last 5 minutes
        })
        
        results = monitoring_client.list_time_series(
            request={
                "name": project_name,
                "filter": f'resource.type="cloud_run_revision" AND resource.labels.service_name="{service_name}" AND resource.labels.location="{region}"',
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            }
        )
        
        # Process the metrics (simplified example)
        error_rate = 0.0
        latency_p95 = 0.0
        
        # Extract metrics from results
        for result in results:
            # This would contain actual metric processing logic
            pass
        
        return {
            'error_rate': error_rate,
            'latency_p95': latency_p95
        }
        
    except Exception as e:
        logger.warning(f"Could not retrieve health metrics: {e}")
        return {}

# Additional utility functions for testing and validation
def validate_service_exists(service_name: str, region: str) -> bool:
    """
    Validate that a service exists before attempting rollback.
    
    Args:
        service_name: Name of the Cloud Run service
        region: Region where the service should exist
        
    Returns:
        True if service exists, False otherwise
    """
    try:
        service_id = f'projects/{PROJECT_ID}/locations/{region}/services/{service_name}'
        service = run_client.get_service(name=service_id)
        return service is not None
    except Exception:
        return False

def get_current_traffic_allocation(service_name: str, region: str) -> Dict[str, int]:
    """
    Get current traffic allocation for a service.
    
    Args:
        service_name: Name of the Cloud Run service
        region: Region where the service is deployed
        
    Returns:
        Dictionary mapping revision names to traffic percentages
    """
    try:
        service_id = f'projects/{PROJECT_ID}/locations/{region}/services/{service_name}'
        service = run_client.get_service(name=service_id)
        
        traffic_allocation = {}
        for traffic_entry in service.status.traffic:
            revision_name = traffic_entry.revision_name
            percent = traffic_entry.percent
            traffic_allocation[revision_name] = percent
            
        return traffic_allocation
        
    except Exception as e:
        logger.error(f"Could not get traffic allocation: {e}")
        return {}

# Entry point for testing
if __name__ == "__main__":
    # This allows for local testing of the function
    test_event = {
        'data': {
            'incident': {
                'policy_name': 'test-policy',
                'condition_name': 'test-condition',
                'state': 'OPEN',
                'resource_name': f'projects/{PROJECT_ID}/locations/{PRIMARY_REGION}/services/api-backend'
            }
        }
    }
    
    rollback_handler(test_event) 