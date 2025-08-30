# Blue-Green Deployment Configuration for Multi-Region Setup
# Night 48 - Enhanced support for blue-green deployments

# Local values for blue-green deployment configuration
locals {
  regions = {
    primary   = var.region
    secondary = "us-east1"
  }
  
  services = {
    primary   = google_cloud_run_v2_service.api_central.name
    secondary = google_cloud_run_v2_service.api_east.name
  }
  
  # Blue-green deployment tags
  deployment_tags = ["blue", "green"]
  
  # Traffic split stages for progressive deployment
  traffic_stages = [10, 25, 50, 100]
}

# Cloud Monitoring Alert Policy for Blue-Green Deployment Health
resource "google_monitoring_alert_policy" "blue_green_deployment_health" {
  display_name = "Blue-Green Deployment Health Alert"
  project      = var.project_id
  
  documentation {
    content   = "This alert triggers when health checks fail during blue-green deployment"
    mime_type = "text/markdown"
  }
  
  conditions {
    display_name = "High Error Rate During Deployment"
    
    condition_threshold {
      filter         = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.label.response_code_class=\"5xx\""
      duration       = "300s"
      comparison     = "COMPARISON_GT"
      threshold_value = 10
      
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  conditions {
    display_name = "High Latency During Deployment"
    
    condition_threshold {
      filter         = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_latencies\""
      duration       = "300s"
      comparison     = "COMPARISON_GT"
      threshold_value = 5000  # 5 seconds
      
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_95TH_PERCENTILE"
      }
    }
  }
  
  combiner     = "OR"
  enabled      = true
  
  notification_channels = var.slack_webhook_token != "" ? [google_monitoring_notification_channel.slack[0].id] : []
  
  alert_strategy {
    auto_close = "1800s"  # Auto-close after 30 minutes
  }
}

# Cloud Monitoring Dashboard for Blue-Green Deployments
resource "google_monitoring_dashboard" "blue_green_dashboard" {
  project        = var.project_id
  dashboard_json = jsonencode({
    displayName = "Blue-Green Deployment Dashboard"
    mosaicLayout = {
      tiles = [
        {
          width  = 6
          height = 4
          widget = {
            title = "Request Rate by Revision"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\""
                      aggregation = {
                        alignmentPeriod  = "60s"
                        perSeriesAligner = "ALIGN_RATE"
                        crossSeriesReducer = "REDUCE_SUM"
                        groupByFields = ["resource.label.revision_name"]
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
            }
          }
        },
        {
          width  = 6
          height = 4
          widget = {
            title = "Error Rate by Revision"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.label.response_code_class=\"5xx\""
                      aggregation = {
                        alignmentPeriod  = "60s"
                        perSeriesAligner = "ALIGN_RATE"
                        crossSeriesReducer = "REDUCE_SUM"
                        groupByFields = ["resource.label.revision_name"]
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
            }
          }
        },
        {
          width  = 6
          height = 4
          widget = {
            title = "Latency by Revision (95th percentile)"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_latencies\""
                      aggregation = {
                        alignmentPeriod  = "60s"
                        perSeriesAligner = "ALIGN_95TH_PERCENTILE"
                        crossSeriesReducer = "REDUCE_MEAN"
                        groupByFields = ["resource.label.revision_name"]
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
            }
          }
        },
        {
          width  = 6
          height = 4
          widget = {
            title = "Traffic Split by Region"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/container/cpu/utilizations\""
                      aggregation = {
                        alignmentPeriod  = "60s"
                        perSeriesAligner = "ALIGN_MEAN"
                        crossSeriesReducer = "REDUCE_MEAN"
                        groupByFields = ["resource.label.location"]
                      }
                    }
                  }
                  plotType = "STACKED_BAR"
                }
              ]
            }
          }
        }
      ]
    }
  })
}

# Custom metric for tracking deployment progress
resource "google_logging_metric" "blue_green_deployment_progress" {
  name    = "blue_green_deployment_progress"
  project = var.project_id
  
  filter = "resource.type=\"cloud_run_revision\" AND jsonPayload.deployment_stage!=\"\""
  
  metric_descriptor {
    metric_kind = "GAUGE"
    value_type  = "INT64"
    display_name = "Blue-Green Deployment Progress"
  }
  
  value_extractor = "EXTRACT(jsonPayload.traffic_percentage)"
  
  label_extractors = {
    "region"           = "EXTRACT(resource.labels.location)"
    "service_name"     = "EXTRACT(resource.labels.service_name)"
    "revision_name"    = "EXTRACT(resource.labels.revision_name)"
    "deployment_stage" = "EXTRACT(jsonPayload.deployment_stage)"
  }
}

# Service Level Indicator (SLI) for deployment success rate
resource "google_monitoring_sli" "deployment_success_sli" {
  service      = google_monitoring_service.blue_green_service.service_id
  sli_id       = "deployment-success-rate"
  display_name = "Blue-Green Deployment Success Rate"
  
  request_based_sli {
    good_total_ratio {
      good_service_filter  = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.label.response_code_class!~\"5.*\""
      total_service_filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\""
    }
  }
}

# Service Level Objective (SLO) for deployment
resource "google_monitoring_slo" "deployment_success_slo" {
  service      = google_monitoring_service.blue_green_service.service_id
  slo_id       = "deployment-99-availability"
  display_name = "99% Availability During Deployments"
  
  request_based_sli {
    good_total_ratio {
      good_service_filter  = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.label.response_code_class!~\"5.*\""
      total_service_filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\""
    }
  }
  
  goal                = 0.99
  rolling_period_days = 30
}

# Monitoring Service for Blue-Green Deployments
resource "google_monitoring_service" "blue_green_service" {
  service_id   = "blue-green-api-service"
  display_name = "Blue-Green API Service"
  project      = var.project_id
  
  telemetry {
    resource_name = "//run.googleapis.com/projects/${var.project_id}/locations/${var.region}/services/${google_cloud_run_v2_service.api_central.name}"
  }
}

# Cloud Function for automated rollback (triggered by alerts)
resource "google_storage_bucket" "rollback_function_source" {
  name     = "rollback-function-source-${var.project_id}"
  location = "US"
  project  = var.project_id
  
  uniform_bucket_level_access = true
  force_destroy              = true
}

# ZIP file for Cloud Function source
data "archive_file" "rollback_function_zip" {
  type        = "zip"
  output_path = "/tmp/rollback-function.zip"
  source {
    content = templatefile("${path.module}/rollback-function.py", {
      project_id       = var.project_id
      primary_region   = var.region
      secondary_region = "us-east1"
    })
    filename = "main.py"
  }
  source {
    content  = "functions-framework==3.*\ngoogle-cloud-run==0.9.*\ngoogle-cloud-logging==3.*"
    filename = "requirements.txt"
  }
}

# Upload function source to bucket
resource "google_storage_bucket_object" "rollback_function_zip" {
  name   = "rollback-function-${data.archive_file.rollback_function_zip.output_md5}.zip"
  bucket = google_storage_bucket.rollback_function_source.name
  source = data.archive_file.rollback_function_zip.output_path
}

# Cloud Function for automated rollback
resource "google_cloudfunctions2_function" "auto_rollback" {
  name        = "auto-rollback-function"
  location    = var.region
  project     = var.project_id
  description = "Automatically rollback failed blue-green deployments"
  
  build_config {
    runtime     = "python39"
    entry_point = "rollback_handler"
    
    source {
      storage_source {
        bucket = google_storage_bucket.rollback_function_source.name
        object = google_storage_bucket_object.rollback_function_zip.name
      }
    }
  }
  
  service_config {
    max_instance_count = 10
    available_memory   = "256M"
    timeout_seconds    = 540
    
    service_account_email = google_service_account.rollback_function_sa.email
    
    environment_variables = {
      PROJECT_ID       = var.project_id
      PRIMARY_REGION   = var.region
      SECONDARY_REGION = "us-east1"
    }
  }
  
  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.rollback_trigger.id
  }
}

# Service account for rollback function
resource "google_service_account" "rollback_function_sa" {
  account_id   = "rollback-function-sa"
  display_name = "Auto Rollback Function Service Account"
  project      = var.project_id
}

# IAM permissions for rollback function
resource "google_project_iam_member" "rollback_function_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.rollback_function_sa.email}"
}

resource "google_project_iam_member" "rollback_function_monitoring_viewer" {
  project = var.project_id
  role    = "roles/monitoring.viewer"
  member  = "serviceAccount:${google_service_account.rollback_function_sa.email}"
}

# Pub/Sub topic for triggering rollbacks
resource "google_pubsub_topic" "rollback_trigger" {
  name    = "rollback-trigger"
  project = var.project_id
}

# Connect monitoring alert to rollback trigger
resource "google_monitoring_alert_policy" "auto_rollback_trigger" {
  display_name = "Auto Rollback Trigger"
  project      = var.project_id
  
  conditions {
    display_name = "Critical Error Rate During Deployment"
    
    condition_threshold {
      filter         = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.label.response_code_class=\"5xx\""
      duration       = "180s"  # Trigger faster for critical issues
      comparison     = "COMPARISON_GT"
      threshold_value = 20
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  notification_channels = [google_monitoring_notification_channel.rollback_pubsub.id]
  
  enabled = true
}

# Notification channel that publishes to Pub/Sub for rollback
resource "google_monitoring_notification_channel" "rollback_pubsub" {
  display_name = "Rollback Pub/Sub Channel"
  type         = "pubsub"
  project      = var.project_id
  
  labels = {
    topic = google_pubsub_topic.rollback_trigger.id
  }
}

# Output values for blue-green configuration
output "blue_green_dashboard_url" {
  description = "URL to the blue-green deployment monitoring dashboard"
  value       = "https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.blue_green_dashboard.id}?project=${var.project_id}"
}

output "rollback_function_name" {
  description = "Name of the auto-rollback Cloud Function"
  value       = google_cloudfunctions2_function.auto_rollback.name
}

output "deployment_slo_name" {
  description = "Name of the deployment SLO"
  value       = google_monitoring_slo.deployment_success_slo.name
} 