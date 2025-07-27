# SecretsManagerAgent Infrastructure - Night 67
# Automated secret rotation across cloud providers

# SecretsManagerAgent Cloud Run Service
module "secrets_manager_agent" {
  source = "../modules/app-infra"
  
  project_id               = var.project_id
  region                   = var.region
  service_name             = "secrets-manager-agent"
  container_image          = "${var.region}-docker.pkg.dev/${var.project_id}/saas-factory/secrets-manager:latest"
  service_account_email    = google_service_account.secrets_manager_sa.email
  cloud_sql_instance_name  = module.cloudsql_postgres.instance_name
  db_host                  = module.cloudsql_postgres.private_ip_address
  db_name                  = var.db_name
  db_user_name             = "secrets_manager_user"
  vpc_connector_id         = google_vpc_access_connector.connector.id
  
  env_vars = {
    AGENT_TYPE = "secrets_manager"
    LOG_LEVEL  = "INFO"
    PROJECT_ID = var.project_id
  }
  
  secret_env_vars = {
    DB_PASSWORD = {
      secret_id = google_secret_manager_secret.db_password.secret_id
      version   = "latest"
    }
  }
  
  cpu_limit     = "1"
  memory_limit  = "1Gi"
  max_instances = 3
  create_neg    = true
}

# Service Account for SecretsManagerAgent
resource "google_service_account" "secrets_manager_sa" {
  account_id   = "secrets-manager-sa"
  display_name = "SecretsManagerAgent Service Account"
  description  = "Service account for SecretsManagerAgent with Secret Manager permissions"
  project      = var.project_id
}

# IAM roles for SecretsManagerAgent
resource "google_project_iam_member" "secrets_manager_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.secrets_manager_sa.email}"
}

resource "google_project_iam_member" "secrets_manager_secret_admin" {
  project = var.project_id
  role    = "roles/secretmanager.admin"
  member  = "serviceAccount:${google_service_account.secrets_manager_sa.email}"
}

resource "google_project_iam_member" "secrets_manager_cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.secrets_manager_sa.email}"
}

resource "google_project_iam_member" "secrets_manager_logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.secrets_manager_sa.email}"
}

resource "google_project_iam_member" "secrets_manager_monitoring_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.secrets_manager_sa.email}"
}

# Cloud Scheduler for monthly secret rotation
resource "google_cloud_scheduler_job" "secrets_monthly_rotation" {
  name        = "secrets-monthly-rotation"
  description = "Triggers monthly secret rotation for all tenants"
  schedule    = "0 2 1 * *" # Runs at 2 AM on the 1st of every month
  time_zone   = "UTC"
  region      = var.region

  http_target {
    http_method = "POST"
    uri         = "https://secrets-manager-agent-${var.project_id}.a.run.app/internal/scheduled-rotation"
    
    headers = {
      "Content-Type" = "application/json"
    }
    
    body = base64encode(jsonencode({
      source = "cloud-scheduler"
      type   = "monthly-rotation"
      timestamp = timestamp()
    }))
    
    oidc_token {
      service_account_email = google_service_account.secrets_manager_scheduler_sa.email
    }
  }

  attempt_deadline = "600s"
  
  retry_config {
    retry_count = 3
    max_retry_duration = "300s"
    min_backoff_duration = "30s"
    max_backoff_duration = "120s"
  }
}

# Service Account for Cloud Scheduler
resource "google_service_account" "secrets_manager_scheduler_sa" {
  account_id   = "secrets-scheduler-sa"
  display_name = "Secrets Manager Scheduler Service Account"
  description  = "Service account for Cloud Scheduler to trigger secret rotations"
  project      = var.project_id
}

# Grant scheduler SA permission to invoke Cloud Run
resource "google_cloud_run_service_iam_member" "secrets_manager_scheduler_invoker" {
  project  = var.project_id
  location = var.region
  service  = module.secrets_manager_agent.service_name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.secrets_manager_scheduler_sa.email}"
}

# Emergency rotation Cloud Scheduler (daily check for critical secrets)
resource "google_cloud_scheduler_job" "secrets_critical_rotation_check" {
  name        = "secrets-critical-rotation-check"
  description = "Daily check for critical secrets that need immediate rotation"
  schedule    = "0 */6 * * *" # Every 6 hours
  time_zone   = "UTC"
  region      = var.region

  http_target {
    http_method = "POST"
    uri         = "https://secrets-manager-agent-${var.project_id}.a.run.app/internal/scheduled-rotation"
    
    headers = {
      "Content-Type" = "application/json"
    }
    
    body = base64encode(jsonencode({
      source = "cloud-scheduler"
      type   = "critical-check"
      criticality_filter = "critical"
    }))
    
    oidc_token {
      service_account_email = google_service_account.secrets_manager_scheduler_sa.email
    }
  }

  attempt_deadline = "300s"
  
  retry_config {
    retry_count = 2
    max_retry_duration = "180s"
    min_backoff_duration = "15s"
    max_backoff_duration = "60s"
  }
}

# Pub/Sub topic for secret rotation events
resource "google_pubsub_topic" "secret_rotation_events" {
  name    = "secret-rotation-events"
  project = var.project_id
  
  labels = {
    component = "secrets-manager"
    purpose   = "event-tracking"
  }
}

# Pub/Sub subscription for monitoring
resource "google_pubsub_subscription" "secret_rotation_monitoring" {
  name    = "secret-rotation-monitoring"
  topic   = google_pubsub_topic.secret_rotation_events.name
  project = var.project_id
  
  # Retain messages for 7 days
  message_retention_duration = "604800s"
  
  # Dead letter queue after 5 retries
  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.secret_rotation_dlq.id
    max_delivery_attempts = 5
  }
  
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "300s"
  }
}

# Dead letter queue for failed rotation events
resource "google_pubsub_topic" "secret_rotation_dlq" {
  name    = "secret-rotation-dlq"
  project = var.project_id
  
  labels = {
    component = "secrets-manager"
    purpose   = "dead-letter-queue"
  }
}

# Grant SecretsManagerAgent permission to publish to Pub/Sub
resource "google_pubsub_topic_iam_member" "secrets_manager_publisher" {
  topic   = google_pubsub_topic.secret_rotation_events.name
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.secrets_manager_sa.email}"
  project = var.project_id
}

# Monitoring alerts for secret rotation failures
resource "google_monitoring_alert_policy" "secret_rotation_failures" {
  display_name = "Secret Rotation Failures"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "Secret rotation failure rate"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"secrets-manager-agent\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 5
      
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields = ["resource.labels.service_name"]
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.email_alert.name
  ]
  
  alert_strategy {
    auto_close = "1800s"
  }
}

# Cloud Function for handling secret rotation alerts (optional)
resource "google_cloudfunctions2_function" "secret_rotation_alert_handler" {
  name        = "secret-rotation-alert-handler"
  location    = var.region
  project     = var.project_id
  description = "Handles alerts for failed secret rotations"
  
  build_config {
    runtime     = "python311"
    entry_point = "handle_rotation_alert"
    
    source {
      storage_source {
        bucket = google_storage_bucket.functions_source.name
        object = "secret-rotation-alert-handler.zip"
      }
    }
  }
  
  service_config {
    max_instance_count = 5
    available_memory   = "256M"
    timeout_seconds    = 300
    
    service_account_email = google_service_account.secrets_manager_sa.email
    
    environment_variables = {
      PROJECT_ID = var.project_id
      TOPIC_NAME = google_pubsub_topic.secret_rotation_events.name
    }
  }
  
  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.secret_rotation_dlq.id
  }
}

# Storage bucket for Cloud Functions source code
resource "google_storage_bucket" "functions_source" {
  name     = "${var.project_id}-secrets-functions-source"
  location = var.region
  project  = var.project_id
  
  uniform_bucket_level_access = true
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

# Output the SecretsManagerAgent service URL
output "secrets_manager_agent_url" {
  description = "URL of the SecretsManagerAgent service"
  value       = module.secrets_manager_agent.service_url
}

output "secret_rotation_topic" {
  description = "Pub/Sub topic for secret rotation events"
  value       = google_pubsub_topic.secret_rotation_events.name
} 