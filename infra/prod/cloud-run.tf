# Artifact Registry repository for container images
resource "google_artifact_registry_repository" "saas_factory" {
  location      = var.region
  repository_id = "saas-factory"
  description   = "SaaS Factory container registry"
  format        = "DOCKER"
  project       = var.project_id
}

# VPC Connector for private database access
resource "google_vpc_access_connector" "connector" {
  name          = "vpc-connector"
  ip_cidr_range = "10.8.0.0/28"
  network       = module.network_base.network_name
  region        = var.region
  project       = var.project_id
}

# Cloud Run service in us-central1
resource "google_cloud_run_v2_service" "api_central" {
  name     = "api-backend"
  location = var.region
  project  = var.project_id
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.run_sa.email
    
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/saas-factory/api:0.1"
      
      ports {
        container_port = 8080
      }
      
      env {
        name  = "DB_HOST"
        value = module.cloudsql_postgres.private_ip_address
      }
      
      env {
        name  = "DB_USER"
        value = google_sql_user.app.name
      }
      
      env {
        name  = "DB_PASS"
        value = google_sql_user.app.password
      }
      
      env {
        name  = "DB_NAME"
        value = var.db_name
      }
      
      env {
        name  = "DB_PORT"
        value = "5432"
      }
      
      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
      }
    }
    
    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }
    
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
  }
  
  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
  
  depends_on = [
    google_artifact_registry_repository.saas_factory,
    google_service_account.run_sa,
    google_sql_user.app
  ]
}

# Cloud Run service in us-east1 (multi-region)
resource "google_cloud_run_v2_service" "api_east" {
  name     = "api-backend-east"
  location = "us-east1"
  project  = var.project_id
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.run_sa.email
    
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/saas-factory/api:0.1"
      
      ports {
        container_port = 8080
      }
      
      env {
        name  = "DB_HOST"
        value = module.cloudsql_postgres.private_ip_address
      }
      
      env {
        name  = "DB_USER"
        value = google_sql_user.app.name
      }
      
      env {
        name  = "DB_PASS"
        value = google_sql_user.app.password
      }
      
      env {
        name  = "DB_NAME"
        value = var.db_name
      }
      
      env {
        name  = "DB_PORT"
        value = "5432"
      }
      
      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
      }
    }
    
    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }
    
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
  }
  
  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
  
  depends_on = [
    google_artifact_registry_repository.saas_factory,
    google_service_account.run_sa,
    google_sql_user.app
  ]
}

# Allow unauthenticated access to Cloud Run services
resource "google_cloud_run_service_iam_member" "public_access_central" {
  project  = var.project_id
  location = google_cloud_run_v2_service.api_central.location
  service  = google_cloud_run_v2_service.api_central.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "public_access_east" {
  project  = var.project_id
  location = google_cloud_run_v2_service.api_east.location
  service  = google_cloud_run_v2_service.api_east.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Cloud Run service for the Project Orchestrator
resource "google_cloud_run_v2_service" "orchestrator" {
  name     = "project-orchestrator"
  location = var.region
  project  = var.project_id
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.orchestrator_sa.email
    
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/saas-factory/orchestrator:0.6"
      
      ports {
        container_port = 8080
      }
      
      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      
      env {
        name  = "ENVIRONMENT"
        value = "production"
      }
      
      env {
        name  = "LOG_LEVEL"
        value = "INFO"
      }
      
      env {
        name  = "MODEL_PROVIDER"
        value = "gpt4o"
      }
      
      env {
        name = "OPENAI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.openai_key.secret_id
            version = "latest"
          }
        }
      }
      
      env {
        name  = "LANG_ECHO_URL"
        value = google_cloud_run_v2_service.lang_echo.uri
      }
      
      resources {
        limits = {
          cpu    = "1"
          memory = "1Gi"
        }
      }
    }
    
    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }
  }
  
  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
  
  depends_on = [
    google_artifact_registry_repository.saas_factory,
    google_service_account.orchestrator_sa,
    google_cloud_run_v2_service.lang_echo
  ]
}

# Allow public access to the orchestrator service
resource "google_cloud_run_service_iam_member" "orchestrator_public_access" {
  project  = var.project_id
  location = google_cloud_run_v2_service.orchestrator.location
  service  = google_cloud_run_v2_service.orchestrator.name
  role     = "roles/run.invoker"
  member   = "allUsers"
} 