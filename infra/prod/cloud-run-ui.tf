# Cloud Run service for the frontend web application
resource "google_cloud_run_v2_service" "frontend" {
  name     = "web-frontend"
  location = var.region
  project  = var.project_id
  
  ingress = "INGRESS_TRAFFIC_ALL"
  
  template {
    containers {
      image = "us-central1-docker.pkg.dev/${var.project_id}/saas-factory-web/ui:latest"
      
      ports {
        container_port = 80
      }
      
      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }
    
    scaling {
      max_instance_count = 5
      min_instance_count = 0
    }
  }
  
  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

# Allow public access to the frontend service
resource "google_cloud_run_service_iam_member" "frontend_public_access" {
  location = google_cloud_run_v2_service.frontend.location
  project  = google_cloud_run_v2_service.frontend.project
  service  = google_cloud_run_v2_service.frontend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Output the frontend URL
output "frontend_url" {
  description = "The URL of the frontend Cloud Run service"
  value       = google_cloud_run_v2_service.frontend.uri
} 