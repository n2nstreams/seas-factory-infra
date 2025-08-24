# Service account for API Gateway
resource "google_service_account" "gateway_sa" {
  account_id   = "gateway-sa"
  display_name = "API Gateway to Orchestrator"
  description  = "Service account for API Gateway that forwards to Vertex AI Agent Engine"
  project      = var.project_id
}

# Allow SA to invoke AgentEndpoint
resource "google_project_iam_member" "gateway_aip" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.gateway_sa.email}"
}

# Grant logging permissions to gateway
resource "google_project_iam_member" "gateway_sa_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.gateway_sa.email}"
}

# Grant monitoring permissions to gateway
resource "google_project_iam_member" "gateway_sa_monitoring" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.gateway_sa.email}"
}

# Allow the owner to act as the gateway service account for deployment
resource "google_service_account_iam_member" "gateway_sa_user" {
  service_account_id = google_service_account.gateway_sa.name
  role               = "roles/iam.serviceAccountUser"
  member             = "user:${var.owner_email}"
}

# Cloud Run service for API Gateway
resource "google_cloud_run_v2_service" "gateway" {
  name     = "api_gateway"
  location = var.region
  project  = var.project_id
  
  ingress = "INGRESS_TRAFFIC_ALL"
  

  
  template {
    service_account = google_service_account.gateway_sa.email
    
    containers {
      image = "us-central1-docker.pkg.dev/${var.project_id}/saas-factory/api_gateway:v1.0"
      
      ports {
        container_port = 8000
      }
      
      env {
        name  = "ORCH_ENDPOINT"
        value = var.orchestrator_vertex_endpoint
      }
      
      env {
        name  = "ORCH_TIMEOUT"
        value = "30"
      }
      
      # Enhanced resource configuration
      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }
    
    scaling {
      max_instance_count = 10
      min_instance_count = 0
    }
  }
  
  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

# Allow public access to the gateway service
# Note: Consider implementing more restrictive access controls for production
resource "google_cloud_run_service_iam_member" "gateway_public_access" {
  location = google_cloud_run_v2_service.gateway.location
  project  = google_cloud_run_v2_service.gateway.project
  service  = google_cloud_run_v2_service.gateway.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Output the gateway URL
output "gateway_url" {
  description = "The URL of the API gateway Cloud Run service"
  value       = google_cloud_run_v2_service.gateway.uri
} 