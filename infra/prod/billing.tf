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

# Storage bucket for cost guard function source
resource "google_storage_bucket" "cost_guard_source" {
  name          = "${var.project_id}-cost-guard-source"
  location      = var.region
  force_destroy = true
  project       = var.project_id
  
  uniform_bucket_level_access = true
}

# ZIP file for Cost Guard Function source
data "archive_file" "cost_guard_function_zip" {
  type        = "zip"
  output_path = "/tmp/cost-guard-function.zip"
  source {
    content = file("${path.module}/cost-guard-agent.py")
    filename = "main.py"
  }
  source {
    content = file("${path.module}/cost-guard-requirements.txt")
    filename = "requirements.txt"
  }
}

# Upload function source to bucket
resource "google_storage_bucket_object" "cost_guard_function_zip" {
  name   = "cost-guard-function-${data.archive_file.cost_guard_function_zip.output_md5}.zip"
  bucket = google_storage_bucket.cost_guard_source.name
  source = data.archive_file.cost_guard_function_zip.output_path
}

# Cloud Function for cost guard processing
resource "google_cloudfunctions2_function" "cost_guard" {
  name        = "cost-guard-agent"
  location    = var.region
  project     = var.project_id
  description = "CostGuardAgent - Processes budget alerts and sends email notifications"
  
  build_config {
    runtime     = "python311"
    entry_point = "cost_guard_handler"
    
    source {
      storage_source {
        bucket = google_storage_bucket.cost_guard_source.name
        object = google_storage_bucket_object.cost_guard_function_zip.name
      }
    }
  }
  
  service_config {
    max_instance_count = 10
    available_memory   = "512M"
    timeout_seconds    = 540
    
    service_account_email = google_service_account.cost_guard_sa.email
    
    environment_variables = {
      PROJECT_ID       = var.project_id
      ALERT_EMAIL      = var.owner_email
      BILLING_ACCOUNT  = var.billing_account
    }
    
    secret_environment_variables {
      key        = "SENDGRID_API_KEY"
      project_id = var.project_id
      secret     = google_secret_manager_secret.sendgrid_key.secret_id
      version    = "latest"
    }
  }
  
  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.cost_guard.id
  }
}

# Secret Manager secret for SendGrid API key
resource "google_secret_manager_secret" "sendgrid_key" {
  secret_id = "sendgrid-api-key"
  project   = var.project_id
  
  replication {
    auto {}
  }
}

# Grant cost guard service account access to SendGrid secret
resource "google_secret_manager_secret_iam_member" "cost_guard_sendgrid_access" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.sendgrid_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cost_guard_sa.email}"
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

# Enhanced Alert policy for cost threshold with multiple severity levels
resource "google_monitoring_alert_policy" "cost_alert_warning" {
  display_name = "Cost Alert - Warning (50% threshold)"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "Cost threshold 50% exceeded"
    
    condition_threshold {
      filter          = "metric.type=\"logging.googleapis.com/user/cost_threshold_exceeded\""
      comparison      = "COMPARISON_GT"
      threshold_value = 100  # $100 (50% of $200 budget)
      duration        = "300s"
      
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.email.id
  ]
  
  alert_strategy {
    auto_close = "86400s"  # 24 hours
  }
  
  documentation {
    content = "⚠️ **WARNING**: 50% of monthly budget has been consumed. Monitor spending closely."
  }
}

resource "google_monitoring_alert_policy" "cost_alert_critical" {
  display_name = "Cost Alert - Critical (80% threshold)"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "Cost threshold 80% exceeded"
    
    condition_threshold {
      filter          = "metric.type=\"logging.googleapis.com/user/cost_threshold_exceeded\""
      comparison      = "COMPARISON_GT"
      threshold_value = 160  # $160 (80% of $200 budget)
      duration        = "300s"
      
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
    content = "🚨 **CRITICAL**: 80% of monthly budget has been consumed. Immediate cost review required!"
  }
}

resource "google_monitoring_alert_policy" "cost_alert_emergency" {
  display_name = "Cost Alert - Emergency (100% threshold)"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "Budget completely exhausted"
    
    condition_threshold {
      filter          = "metric.type=\"logging.googleapis.com/user/cost_threshold_exceeded\""
      comparison      = "COMPARISON_GT"
      threshold_value = 200  # $200 (100% of budget)
      duration        = "0s"  # Immediate alert
      
      aggregations {
        alignment_period   = "60s"
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
    content = "🚨 **EMERGENCY**: Monthly budget completely exhausted! Automatic cost reduction measures may be triggered."
  }
}

# Custom log-based metrics for detailed cost tracking
resource "google_logging_metric" "daily_spend_metric" {
  name   = "daily_spend_amount"
  filter = "resource.type=\"billing_account\" AND jsonPayload.cost_amount>0"
  project = var.project_id
  
  metric_descriptor {
    metric_kind = "GAUGE"
    value_type  = "DOUBLE"
    display_name = "Daily Spend Amount"
  }
  
  value_extractor = "EXTRACT(jsonPayload.cost_amount)"
}

resource "google_logging_metric" "service_cost_metric" {
  name   = "cost_by_service"
  filter = "resource.type=\"billing_account\" AND jsonPayload.service_name!=\"\""
  project = var.project_id
  
  metric_descriptor {
    metric_kind = "GAUGE"
    value_type  = "DOUBLE"
    display_name = "Cost by Service"
  }
  
  value_extractor = "EXTRACT(jsonPayload.cost_amount)"
  label_extractors = {
    service_name = "EXTRACT(jsonPayload.service_name)"
  }
}

# Comprehensive Cost Monitoring Dashboard
resource "google_monitoring_dashboard" "cost_monitoring_dashboard" {
  project        = var.project_id
  dashboard_json = jsonencode({
    displayName = "SaaS Factory - Cost Monitoring Dashboard"
    mosaicLayout = {
      tiles = [
        # Budget utilization gauge
        {
          width  = 6
          height = 4
          widget = {
            title = "Budget Utilization"
            scorecard = {
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "metric.type=\"logging.googleapis.com/user/cost_threshold_exceeded\""
                  aggregation = {
                    alignmentPeriod  = "3600s"
                    perSeriesAligner = "ALIGN_MEAN"
                  }
                }
              }
              gaugeView = {
                lowerBound = 0.0
                upperBound = 200.0
              }
              sparkChartView = {
                sparkChartType = "SPARK_LINE"
              }
            }
          }
        },
        
        # Daily spending trend
        {
          width  = 6
          height = 4
          xPos   = 6
          widget = {
            title = "Daily Spending Trend"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "metric.type=\"logging.googleapis.com/user/daily_spend_amount\""
                      aggregation = {
                        alignmentPeriod  = "86400s"
                        perSeriesAligner = "ALIGN_MAX"
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
              timeshiftDuration = "0s"
              yAxis = {
                label = "USD"
                scale = "LINEAR"
              }
            }
          }
        },
        
        # Budget progress bar
        {
          width  = 12
          height = 2
          yPos   = 4
          widget = {
            title = "Monthly Budget Progress"
            scorecard = {
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "metric.type=\"logging.googleapis.com/user/cost_threshold_exceeded\""
                  aggregation = {
                    alignmentPeriod  = "3600s"
                    perSeriesAligner = "ALIGN_MEAN"
                  }
                }
              }
              sparkChartView = {
                sparkChartType = "SPARK_BAR"
              }
            }
          }
        },
        
        # Cost by service breakdown
        {
          width  = 8
          height = 6
          yPos   = 6
          widget = {
            title = "Cost Breakdown by Service"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "metric.type=\"logging.googleapis.com/user/cost_by_service\""
                      aggregation = {
                        alignmentPeriod    = "3600s"
                        perSeriesAligner   = "ALIGN_MEAN"
                        crossSeriesReducer = "REDUCE_SUM"
                        groupByFields      = ["metric.label.service_name"]
                      }
                    }
                  }
                  plotType = "STACKED_AREA"
                }
              ]
              yAxis = {
                label = "USD"
                scale = "LINEAR"
              }
            }
          }
        },
        
        # Active alerts panel
        {
          width  = 4
          height = 6
          xPos   = 8
          yPos   = 6
          widget = {
            title = "Active Cost Alerts"
            alertChart = {
              name = google_monitoring_alert_policy.cost_alert_critical.name
            }
          }
        },
        
        # Cost optimization recommendations
        {
          width  = 6
          height = 4
          yPos   = 12
          widget = {
            title = "Cost Optimization Insights"
            text = {
              content = "💡 **Cost Optimization Tips:**\n\n• **Cloud Run**: Scale to zero during idle periods\n• **Cloud SQL**: Use connection pooling to reduce instances\n• **Storage**: Clean up old artifacts and logs regularly\n• **Monitoring**: Set granular budget alerts for early warnings\n• **Scheduling**: Use Cloud Scheduler for batch operations\n\n📊 **Current Month Trend**: Monitor daily spending patterns\n🎯 **Target**: Stay under $200/month budget\n⚡ **Quick Actions**: Review high-cost services weekly"
              format = "MARKDOWN"
            }
          }
        },
        
        # Budget forecast
        {
          width  = 6
          height = 4
          xPos   = 6
          yPos   = 12
          widget = {
            title = "Budget Forecast"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "metric.type=\"logging.googleapis.com/user/daily_spend_amount\""
                      aggregation = {
                        alignmentPeriod    = "86400s"
                        perSeriesAligner   = "ALIGN_MEAN"
                        crossSeriesReducer = "REDUCE_SUM"
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
              yAxis = {
                label = "USD (Projected)"
                scale = "LINEAR"
              }
            }
          }
        }
      ]
    }
    labels = {
      team        = "devops"
      environment = "production"
      purpose     = "cost-monitoring"
    }
  })
}

# Output dashboard URL
output "cost_dashboard_url" {
  description = "URL to the cost monitoring dashboard"
  value       = "https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.cost_monitoring_dashboard.id}?project=${var.project_id}"
} 