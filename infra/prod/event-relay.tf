# Event Relay Cloud Run Service
resource "google_cloud_run_v2_service" "event_relay" {
  name     = "event-relay"
  location = var.region
  project  = var.project_id
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.run_sa.email
    
    containers {
      image = "${google_artifact_registry_repository.saas_factory.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.saas_factory.name}/event-relay:v1.0"
      
      ports {
        container_port = 8080
      }
      
      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      
      resources {
        limits = {
          cpu    = "1000m"
          memory = "1Gi"
        }
        cpu_idle = true
      }
      
      startup_probe {
        initial_delay_seconds = 10
        timeout_seconds       = 5
        period_seconds        = 10
        failure_threshold     = 3
        
        http_get {
          path = "/"
          port = 8080
        }
      }
      
      liveness_probe {
        initial_delay_seconds = 30
        timeout_seconds       = 5
        period_seconds        = 30
        failure_threshold     = 3
        
        http_get {
          path = "/"
          port = 8080
        }
      }
    }
    
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
  }
  
  depends_on = [
    google_artifact_registry_repository.saas_factory,
    google_service_account.run_sa
  ]
}

# IAM policy for invoking Event Relay (needed for Pub/Sub push)
resource "google_cloud_run_service_iam_member" "event_relay_invoker" {
  service  = google_cloud_run_v2_service.event_relay.name
  location = google_cloud_run_v2_service.event_relay.location
  project  = var.project_id
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.run_sa.email}"
}

# Allow unauthenticated access for Pub/Sub push subscriptions
resource "google_cloud_run_service_iam_member" "event_relay_public" {
  service  = google_cloud_run_v2_service.event_relay.name
  location = google_cloud_run_v2_service.event_relay.location
  project  = var.project_id
  role     = "roles/run.invoker"
  member   = "allUsers"
} 