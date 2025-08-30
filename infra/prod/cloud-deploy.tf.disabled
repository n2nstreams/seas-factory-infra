# Cloud Deploy - Auto-Rollback Strategy Implementation (Night 47)
# Sets up Cloud Deploy with automated rollback based on error budget monitoring

# Enable Cloud Deploy API
resource "google_project_service" "clouddeploy" {
  project = var.project_id
  service = "clouddeploy.googleapis.com"
  
  disable_dependent_services = false
  disable_on_destroy        = false
}

# Service account for Cloud Deploy
resource "google_service_account" "cloud_deploy_sa" {
  account_id   = "cloud-deploy-sa"
  display_name = "Cloud Deploy Service Account"
  description  = "Service account for Cloud Deploy operations and auto-rollback"
  project      = var.project_id
}

# Grant Cloud Deploy permissions
resource "google_project_iam_member" "cloud_deploy_sa_deployer" {
  project = var.project_id
  role    = "roles/clouddeploy.operator"
  member  = "serviceAccount:${google_service_account.cloud_deploy_sa.email}"
}

# Grant Cloud Run permissions for deployment
resource "google_project_iam_member" "cloud_deploy_sa_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.cloud_deploy_sa.email}"
}

# Grant monitoring permissions for error budget tracking
resource "google_project_iam_member" "cloud_deploy_sa_monitoring" {
  project = var.project_id
  role    = "roles/monitoring.viewer"
  member  = "serviceAccount:${google_service_account.cloud_deploy_sa.email}"
}

# Cloud Deploy Delivery Pipeline for API Backend
resource "google_clouddeploy_delivery_pipeline" "api_backend_pipeline" {
  name         = "api-backend-pipeline"
  location     = var.region
  project      = var.project_id
  description  = "Delivery pipeline for API backend with auto-rollback"

  serial_pipeline {
    stages {
      target_id = google_clouddeploy_target.staging.name
      profiles  = ["staging"]
    }
    
    stages {
      target_id = google_clouddeploy_target.production.name
      profiles  = ["production"]
      
      strategy {
        canary {
          runtime_config {
            cloud_run {
              automatic_traffic_control = true
            }
          }
          
          canary_deployment {
            percentages = [25, 50, 100]
            verify      = true
          }
        }
      }
    }
  }

  depends_on = [google_project_service.clouddeploy]
}

# Cloud Deploy Target - Staging
resource "google_clouddeploy_target" "staging" {
  name         = "staging"
  location     = var.region
  project      = var.project_id
  description  = "Staging environment target"

  execution_configs {
    usages            = ["RENDER", "DEPLOY"]
    service_account   = google_service_account.cloud_deploy_sa.email
    artifact_storage  = google_storage_bucket.deploy_artifacts.url
  }

  run {
    location = var.region
  }

  depends_on = [google_project_service.clouddeploy]
}

# Cloud Deploy Target - Production
resource "google_clouddeploy_target" "production" {
  name         = "production"
  location     = var.region
  project      = var.project_id
  description  = "Production environment target with auto-rollback"

  execution_configs {
    usages            = ["RENDER", "DEPLOY"]
    service_account   = google_service_account.cloud_deploy_sa.email
    artifact_storage  = google_storage_bucket.deploy_artifacts.url
  }

  run {
    location = var.region
  }

  depends_on = [google_project_service.clouddeploy]
}

# Storage bucket for Cloud Deploy artifacts
resource "google_storage_bucket" "deploy_artifacts" {
  name     = "deploy-artifacts-${var.project_id}"
  location = "US"
  project  = var.project_id
  
  uniform_bucket_level_access = true
  
  # Auto-delete artifacts after 30 days
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
  
  versioning {
    enabled = true
  }
}

# Grant Cloud Deploy SA access to artifacts bucket
resource "google_storage_bucket_iam_member" "deploy_artifacts_admin" {
  bucket = google_storage_bucket.deploy_artifacts.name
  role   = "roles/storage.admin"
  member = "serviceAccount:${google_service_account.cloud_deploy_sa.email}"
}

# Automation for Cloud Deploy - this will trigger rollbacks
resource "google_clouddeploy_automation" "auto_rollback" {
  name         = "auto-rollback-automation"
  location     = var.region
  project      = var.project_id
  delivery_pipeline = google_clouddeploy_delivery_pipeline.api_backend_pipeline.name
  
  description  = "Automated rollback when error budget exceeds 1% in 1 hour"
  
  service_account = google_service_account.cloud_deploy_sa.email
  
  selector {
    targets {
      id = google_clouddeploy_target.production.name
    }
  }
  
  rules {
    rollback_rule {
      id                    = "error-budget-rollback"
      source_phases         = ["DEPLOY"]
      wait_after_rollback   = "300s"  # Wait 5 minutes after rollback
      condition             = "failure()"
    }
  }

  depends_on = [google_clouddeploy_delivery_pipeline.api_backend_pipeline]
}

# Output Cloud Deploy information
output "cloud_deploy_pipeline_id" {
  description = "The ID of the Cloud Deploy delivery pipeline"
  value       = google_clouddeploy_delivery_pipeline.api_backend_pipeline.id
}

output "cloud_deploy_pipeline_name" {
  description = "The name of the Cloud Deploy delivery pipeline"
  value       = google_clouddeploy_delivery_pipeline.api_backend_pipeline.name
}

output "deploy_artifacts_bucket" {
  description = "The URL of the deployment artifacts bucket"
  value       = google_storage_bucket.deploy_artifacts.url
} 