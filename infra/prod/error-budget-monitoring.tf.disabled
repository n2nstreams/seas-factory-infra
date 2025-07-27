# Error Budget Monitoring - Night 47 Implementation
# SLI/SLO definitions and error budget tracking for auto-rollback strategy

# SLO for API Backend Service - 99% uptime target (1% error budget)
resource "google_monitoring_slo" "api_backend_availability_slo" {
  service      = google_monitoring_service.api_backend_service.service_id
  display_name = "API Backend 99% Availability SLO"
  slo_id       = "api-backend-availability-slo"
  
  goal                = 0.99  # 99% availability target
  calendar_period     = "WEEK"
  rolling_period_days = 7
  
  availability_sli {
    request_based {
      # Distribution cut for request-based SLI
      distribution_cut {
        distribution_filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"api-backend\" AND metric.type=\"run.googleapis.com/request_latencies\""
        
        range {
          max = 5000  # 5 seconds max latency
        }
      }
    }
  }
}

# SLO for Error Rate - Maximum 1% error rate
resource "google_monitoring_slo" "api_backend_error_rate_slo" {
  service      = google_monitoring_service.api_backend_service.service_id
  display_name = "API Backend Error Rate SLO"
  slo_id       = "api-backend-error-rate-slo"
  
  goal                = 0.99  # 99% success rate (1% error budget)
  calendar_period     = "WEEK"
  rolling_period_days = 1      # 1-day rolling window for faster detection
  
  request_based_sli {
    good_total_ratio {
      good_service_filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"api-backend\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.labels.response_code_class=\"2xx\""
      total_service_filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"api-backend\" AND metric.type=\"run.googleapis.com/request_count\""
    }
  }
}

# Service definition for API Backend
resource "google_monitoring_service" "api_backend_service" {
  service_id   = "api-backend-service"
  display_name = "API Backend Service"
  
  cloud_run {
    service_name = google_cloud_run_v2_service.api_central.name
    location     = var.region
  }
}

# Error Budget Alert Policy - Triggers when error budget > 1% in 1 hour
resource "google_monitoring_alert_policy" "error_budget_alert" {
  display_name = "Error Budget Exceeded - Auto Rollback Trigger"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "Error budget consumption > 1% in 1 hour"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"api-backend\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.labels.response_code_class!=\"2xx\""
      comparison      = "COMPARISON_GT"
      threshold_value = 0.01  # 1% error rate threshold
      duration        = "3600s"  # 1 hour window
      
      aggregations {
        alignment_period     = "3600s"  # 1 hour alignment
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_MEAN"
        group_by_fields      = ["resource.label.service_name"]
      }
      
      trigger {
        count = 1
      }
    }
  }
  
  # Critical alert - triggers immediate rollback
  alert_strategy {
    auto_close = "86400s"  # 24 hours
    
    notification_rate_limit {
      period = "3600s"  # Rate limit to 1 per hour
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.slack.id,
    google_monitoring_notification_channel.email.id,
    google_monitoring_notification_channel.error_budget_webhook.id
  ]
  
  documentation {
    content = "🚨 **CRITICAL - AUTO ROLLBACK TRIGGERED**: Error budget exceeded! Error rate > 1% for 1 hour. Automatic rollback initiated via Cloud Deploy. Monitor rollback progress in Cloud Deploy console."
    mime_type = "text/markdown"
  }
}

# SLO Burn Rate Alert - Early warning system
resource "google_monitoring_alert_policy" "slo_burn_rate_alert" {
  display_name = "SLO Burn Rate Alert - Fast Burn Detection"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "Fast burn rate detected"
    
    condition_threshold {
      filter          = "select_slo_burn_rate(\"${google_monitoring_slo.api_backend_error_rate_slo.name}\", \"3600s\")"
      comparison      = "COMPARISON_GT"
      threshold_value = 14.4  # Fast burn rate threshold (consumes 1% budget in 1 hour)
      duration        = "600s"  # 10 minute window
      
      aggregations {
        alignment_period     = "600s"
        per_series_aligner   = "ALIGN_MEAN"
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.slack.id,
    google_monitoring_notification_channel.email.id
  ]
  
  documentation {
    content = "⚠️ **WARNING**: Fast SLO burn rate detected! Error budget being consumed rapidly. Consider manual intervention before auto-rollback triggers."
    mime_type = "text/markdown"
  }
}

# Webhook notification channel for triggering auto-rollback
resource "google_monitoring_notification_channel" "error_budget_webhook" {
  display_name = "Error Budget Webhook"
  type         = "webhook_tokenauth"
  project      = var.project_id
  
  labels = {
    url = "https://aiops-agent-4riidj3biq-uc.a.run.app/webhook/error-budget-alert"
  }
  
  sensitive_labels {
    auth_token = random_password.webhook_token.result
  }
  
  description = "Webhook to trigger auto-rollback when error budget is exceeded"
}

# Random token for webhook authentication
resource "random_password" "webhook_token" {
  length  = 32
  special = true
}

# Store webhook token in Secret Manager
resource "google_secret_manager_secret" "webhook_token" {
  secret_id = "error-budget-webhook-token"
  project   = var.project_id
  
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "webhook_token" {
  secret      = google_secret_manager_secret.webhook_token.id
  secret_data = random_password.webhook_token.result
}

# SLO Dashboard for monitoring error budget consumption
resource "google_monitoring_dashboard" "slo_dashboard" {
  project        = var.project_id
  dashboard_json = jsonencode({
    displayName = "SLO & Error Budget Monitoring"
    mosaicLayout = {
      columns = 12
      tiles = [
        {
          width  = 6
          height = 4
          xPos   = 0
          yPos   = 0
          widget = {
            title = "API Backend Availability SLO"
            scorecard = {
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "select_slo_health(\"${google_monitoring_slo.api_backend_availability_slo.name}\")"
                }
              }
              sparkChartView = {
                sparkChartType = "SPARK_LINE"
              }
              gaugeView = {
                lowerBound = 0.0
                upperBound = 1.0
              }
            }
          }
        },
        {
          width  = 6
          height = 4
          xPos   = 6
          yPos   = 0
          widget = {
            title = "Error Rate SLO"
            scorecard = {
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "select_slo_health(\"${google_monitoring_slo.api_backend_error_rate_slo.name}\")"
                }
              }
              sparkChartView = {
                sparkChartType = "SPARK_LINE"
              }
              gaugeView = {
                lowerBound = 0.0
                upperBound = 1.0
              }
            }
          }
        },
        {
          width  = 12
          height = 4
          xPos   = 0
          yPos   = 4
          widget = {
            title = "Error Budget Burn Rate"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "select_slo_burn_rate(\"${google_monitoring_slo.api_backend_error_rate_slo.name}\", \"3600s\")"
                  }
                }
                plotType = "LINE"
              }]
              yAxis = {
                label = "Burn Rate"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          width  = 12
          height = 4
          xPos   = 0
          yPos   = 8
          widget = {
            title = "Recent Rollback Events"
            logsPanel = {
              filter = "resource.type=\"cloud_run_revision\" AND \"rollback\" AND \"auto-rollback\""
            }
          }
        }
      ]
    }
  })
}

# Outputs for error budget monitoring
output "api_backend_availability_slo_name" {
  description = "The name of the API backend availability SLO"
  value       = google_monitoring_slo.api_backend_availability_slo.name
}

output "api_backend_error_rate_slo_name" {
  description = "The name of the API backend error rate SLO"
  value       = google_monitoring_slo.api_backend_error_rate_slo.name
}

output "error_budget_webhook_url" {
  description = "The webhook URL for error budget alerts"
  value       = "https://aiops-agent-4riidj3biq-uc.a.run.app/webhook/error-budget-alert"
  sensitive   = true
}

output "slo_dashboard_url" {
  description = "The URL of the SLO monitoring dashboard"
  value       = "https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.slo_dashboard.id}?project=${var.project_id}"
} 