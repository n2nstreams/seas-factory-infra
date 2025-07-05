# Pub/Sub topic for cost guard notifications
resource "google_pubsub_topic" "cost_guard" {
  name    = "cost-guard"
  project = var.project_id
}

# Pub/Sub subscription for cost guard
resource "google_pubsub_subscription" "cost_guard_subscription" {
  name    = "cost-guard-subscription"
  topic   = google_pubsub_topic.cost_guard.name
  project = var.project_id
  
  message_retention_duration = "604800s"  # 7 days
  retain_acked_messages      = false
  ack_deadline_seconds       = 20
  
  expiration_policy {
    ttl = "300000.5s"
  }
}

# Billing budget with thresholds
resource "google_billing_budget" "budget" {
  billing_account = var.billing_account
  display_name    = "Monthly SaaS Factory Budget"
  
  budget_filter {
    projects = ["projects/${var.project_id}"]
  }
  
  amount {
    specified_amount {
      currency_code = "USD"
      units         = "200"
    }
  }
  
  threshold_rules {
    threshold_percent = 0.5   # 50% warning
    spend_basis       = "CURRENT_SPEND"
  }
  
  threshold_rules {
    threshold_percent = 0.8   # 80% warning
    spend_basis       = "CURRENT_SPEND"
  }
  
  threshold_rules {
    threshold_percent = 1.0   # 100% critical
    spend_basis       = "CURRENT_SPEND"
  }
  
  all_updates_rule {
    pubsub_topic                     = google_pubsub_topic.cost_guard.id
    schema_version                   = "1.0"
    monitoring_notification_channels = [
      google_monitoring_notification_channel.email.id
    ]
  }
}

# Service account for cost guard function
resource "google_service_account" "cost_guard_sa" {
  account_id   = "cost-guard-sa"
  display_name = "Cost Guard Service Account"
  description  = "Service account for cost monitoring and alerts"
  project      = var.project_id
}

# Grant necessary permissions to cost guard service account
resource "google_project_iam_member" "cost_guard_billing" {
  project = var.project_id
  role    = "roles/billing.viewer"
  member  = "serviceAccount:${google_service_account.cost_guard_sa.email}"
}

resource "google_project_iam_member" "cost_guard_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.cost_guard_sa.email}"
}

resource "google_project_iam_member" "cost_guard_monitoring" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.cost_guard_sa.email}"
}

# Cloud Function for cost guard processing (placeholder)
resource "google_storage_bucket" "cost_guard_source" {
  name          = "${var.project_id}-cost-guard-source"
  location      = var.region
  force_destroy = true
  project       = var.project_id
  
  uniform_bucket_level_access = true
}

# Log-based metric for cost alerts
resource "google_logging_metric" "cost_threshold_metric" {
  name   = "cost_threshold_exceeded"
  filter = "resource.type=\"billing_account\" AND protoPayload.methodName=\"google.cloud.billing.budgets.v1.BudgetService.UpdateBudget\""
  project = var.project_id
  
  metric_descriptor {
    metric_kind = "GAUGE"
    value_type  = "INT64"
    display_name = "Cost Threshold Exceeded"
  }
  
  value_extractor = "EXTRACT(jsonPayload.costAmount)"
}

# Alert policy for cost threshold
resource "google_monitoring_alert_policy" "cost_alert" {
  display_name = "Cost Threshold Alert"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "Cost threshold exceeded"
    
    condition_threshold {
      filter          = "metric.type=\"logging.googleapis.com/user/cost_threshold_exceeded\""
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      duration        = "0s"
      
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.slack.id,
    google_monitoring_notification_channel.email.id
  ]
  
  alert_strategy {
    auto_close = "86400s"  # 24 hours
  }
  
  documentation {
    content = "Cost threshold has been exceeded. Review spending and consider scaling down resources."
  }
} 