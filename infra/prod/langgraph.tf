resource "google_cloud_run_v2_service" "lang_echo" {
  name     = "lang-echo"
  location = var.region
  project  = var.project_id
  
  template {
    containers {
      image = "us-central1-docker.pkg.dev/${var.project_id}/saas-factory/lang-dummy:0.1"
      
      ports {
        container_port = 8080
      }
      
      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
      
    }
    
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
    
    vpc_access {
      connector = google_vpc_access_connector.connector.id
    }
  }
  
  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

# IAM policy to allow public access
resource "google_cloud_run_v2_service_iam_member" "lang_echo_public" {
  location = google_cloud_run_v2_service.lang_echo.location
  name     = google_cloud_run_v2_service.lang_echo.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "lang_echo_url" {
  description = "URL of the LangGraph echo service"
  value       = google_cloud_run_v2_service.lang_echo.uri
} 