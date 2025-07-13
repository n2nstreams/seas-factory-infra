# Cloud Run service for the agent
resource "google_cloud_run_v2_service" "agent" {
  name     = var.service_name
  location = var.region
  project  = var.project_id
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = var.service_account_email
    
    containers {
      image = var.container_image
      
      ports {
        container_port = var.container_port
      }
      
      # Database connection environment variables
      env {
        name  = "DB_HOST"
        value = var.db_host
      }
      
      env {
        name  = "DB_USER"
        value = google_sql_user.agent.name
      }
      
      env {
        name  = "DB_PASS"
        value = google_sql_user.agent.password
      }
      
      env {
        name  = "DB_NAME"
        value = var.db_name
      }
      
      env {
        name  = "DB_PORT"
        value = "5432"
      }
      
      # Agent-specific environment variables
      dynamic "env" {
        for_each = var.env_vars
        content {
          name  = env.key
          value = env.value
        }
      }
      
      # Secret environment variables
      dynamic "env" {
        for_each = var.secret_env_vars
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = env.value.secret_id
              version = env.value.version
            }
          }
        }
      }
      
      resources {
        limits = {
          cpu    = var.cpu_limit
          memory = var.memory_limit
        }
      }
    }
    
    # VPC access for private database connectivity
    vpc_access {
      connector = var.vpc_connector_id
      egress    = "PRIVATE_RANGES_ONLY"
    }
    
    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }
  }
  
  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
  
  depends_on = [
    google_sql_user.agent
  ]
}

# Cloud SQL user for the agent
resource "google_sql_user" "agent" {
  name     = var.db_user_name
  instance = var.cloud_sql_instance_name
  password = random_password.agent_db_password.result
  project  = var.project_id
}

# Generate random password for the agent's database user
resource "random_password" "agent_db_password" {
  length  = 16
  special = true
}

# Allow public access to the agent service
resource "google_cloud_run_service_iam_member" "public_access" {
  project  = var.project_id
  location = google_cloud_run_v2_service.agent.location
  service  = google_cloud_run_v2_service.agent.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Serverless NEG for load balancer integration
resource "google_compute_region_network_endpoint_group" "agent_neg" {
  count                 = var.create_neg ? 1 : 0
  name                  = "${var.service_name}-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  project               = var.project_id
  
  cloud_run {
    service = google_cloud_run_v2_service.agent.name
  }
} 