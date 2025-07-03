# Slack notification channel
resource "google_monitoring_notification_channel" "slack" {
  display_name = "Slack DevOps"
  type         = "slack"
  project      = var.project_id
  
  labels = {
    channel_name = "#alerts"
  }
  
  sensitive_labels {
    auth_token = var.slack_webhook_token
  }
}

# Email notification channel
resource "google_monitoring_notification_channel" "email" {
  display_name = "Email DevOps"
  type         = "email"
  project      = var.project_id
  
  labels = {
    email_address = var.owner_email
  }
}

# Uptime check for API health endpoint
resource "google_monitoring_uptime_check_config" "api_health" {
  display_name = "API Health Check"
  timeout      = "10s"
  period       = "60s"
  project      = var.project_id
  
  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = google_compute_global_address.lb_ip.address
    }
  }
  
  http_check {
    port         = 443
    use_ssl      = true
    path         = "/health"
    validate_ssl = true
    
    accepted_response_status_codes {
      status_class = "STATUS_CLASS_2XX"
    }
  }
  
  content_matchers {
    content = "OK"
    matcher = "CONTAINS_STRING"
  }
}

# Alert policy for uptime check failures
resource "google_monitoring_alert_policy" "uptime_alert" {
  display_name = "API Uptime Alert"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "Uptime check failed"
    
    condition_threshold {
      filter          = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND resource.type=\"uptime_url\""
      comparison      = "COMPARISON_EQUAL"
      threshold_value = 0
      duration        = "300s"
      
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_FRACTION_TRUE"
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.slack.id,
    google_monitoring_notification_channel.email.id
  ]
  
  alert_strategy {
    auto_close = "1800s"
  }
}

# Alert policy for high error rate
resource "google_monitoring_alert_policy" "error_rate_alert" {
  display_name = "High Error Rate Alert"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "Error rate too high"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\""
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 0.1
      duration        = "300s"
      
      aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_MEAN"
        group_by_fields      = ["resource.label.service_name"]
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.slack.id,
    google_monitoring_notification_channel.email.id
  ]
}

# Alert policy for high latency
resource "google_monitoring_alert_policy" "latency_alert" {
  display_name = "High Latency Alert"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "Response latency too high"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_latencies\""
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 5000
      duration        = "300s"
      
      aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_DELTA"
        cross_series_reducer = "REDUCE_PERCENTILE_95"
        group_by_fields      = ["resource.label.service_name"]
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.slack.id,
    google_monitoring_notification_channel.email.id
  ]
}

# Custom dashboard for API monitoring
resource "google_monitoring_dashboard" "api_dashboard" {
  project        = var.project_id
  dashboard_json = jsonencode({
    displayName = "SaaS Factory API Dashboard"
    mosaicLayout = {
      tiles = [
        {
          width  = 6
          height = 4
          widget = {
            title = "Request Count"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\""
                    aggregation = {
                      alignmentPeriod    = "60s"
                      perSeriesAligner   = "ALIGN_RATE"
                      crossSeriesReducer = "REDUCE_SUM"
                    }
                  }
                }
              }]
            }
          }
        },
        {
          width  = 6
          height = 4
          widget = {
            title = "Response Latency"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_latencies\""
                    aggregation = {
                      alignmentPeriod    = "60s"
                      perSeriesAligner   = "ALIGN_DELTA"
                      crossSeriesReducer = "REDUCE_PERCENTILE_95"
                    }
                  }
                }
              }]
            }
          }
        }
      ]
    }
  })
} 