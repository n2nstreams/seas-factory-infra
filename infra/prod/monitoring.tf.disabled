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

# Uptime check for Orchestrator service
resource "google_monitoring_uptime_check_config" "orchestrator_health" {
  display_name = "Orchestrator Health Check"
  timeout      = "10s"
  period       = "60s"
  project      = var.project_id
  
  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = replace(google_cloud_run_v2_service.orchestrator.uri, "https://", "")
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
}

# Uptime check for API Gateway service
resource "google_monitoring_uptime_check_config" "gateway_health" {
  display_name = "Gateway Health Check"
  timeout      = "10s"
  period       = "60s"
  project      = var.project_id
  
  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = replace(google_cloud_run_v2_service.gateway.uri, "https://", "")
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
}

# Uptime check for Frontend service
resource "google_monitoring_uptime_check_config" "frontend_health" {
  display_name = "Frontend Health Check"
  timeout      = "10s"
  period       = "60s"
  project      = var.project_id
  
  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = replace(google_cloud_run_v2_service.frontend.uri, "https://", "")
    }
  }
  
  http_check {
    port         = 443
    use_ssl      = true
    path         = "/"
    validate_ssl = true
    
    accepted_response_status_codes {
      status_class = "STATUS_CLASS_2XX"
    }
  }
}

# Uptime check for Event Relay service
resource "google_monitoring_uptime_check_config" "event_relay_health" {
  display_name = "Event Relay Health Check"
  timeout      = "10s"
  period       = "60s"
  project      = var.project_id
  
  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = replace(google_cloud_run_v2_service.event_relay.uri, "https://", "")
    }
  }
  
  http_check {
    port         = 443
    use_ssl      = true
    path         = "/"
    validate_ssl = true
    
    accepted_response_status_codes {
      status_class = "STATUS_CLASS_2XX"
    }
  }
}

# TODO: Enable agent uptime checks after modules are properly deployed
# Uptime check for Agent services (sample with Idea Agent)
# resource "google_monitoring_uptime_check_config" "idea_agent_health" {
#   display_name = "Idea Agent Health Check"
#   timeout      = "10s"
#   period       = "60s"
#   project      = var.project_id
#   
#   monitored_resource {
#     type = "uptime_url"
#     labels = {
#       project_id = var.project_id
#       host       = replace(module.idea_agent.service_url, "https://", "")
#     }
#   }
#   
#   http_check {
#     port         = 443
#     use_ssl      = true
#     path         = "/health"
#     validate_ssl = true
#     
#     accepted_response_status_codes {
#       status_class = "STATUS_CLASS_2XX"
#     }
#   }
# }

# Alert policy for uptime check failures
resource "google_monitoring_alert_policy" "uptime_alert" {
  display_name = "API Uptime Alert"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "Uptime check failed"
    
    condition_threshold {
      filter          = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND resource.type=\"uptime_url\""
      comparison      = "COMPARISON_EQ"
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

# Alert policy for Orchestrator service failures
resource "google_monitoring_alert_policy" "orchestrator_uptime_alert" {
  display_name = "Orchestrator Service Down"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "Orchestrator uptime check failed"
    
    condition_threshold {
      filter          = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND resource.type=\"uptime_url\" AND metric.labels.check_id=\"${google_monitoring_uptime_check_config.orchestrator_health.uptime_check_id}\""
      comparison      = "COMPARISON_EQ"
      threshold_value = 0
      duration        = "180s"
      
      aggregations {
        alignment_period   = "180s"
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
  
  documentation {
    content = "🚨 **CRITICAL**: Orchestrator service is down! This affects all agent operations. Check Cloud Run logs and service status immediately."
  }
}

# Alert policy for Gateway service failures
resource "google_monitoring_alert_policy" "gateway_uptime_alert" {
  display_name = "Gateway Service Down"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "Gateway uptime check failed"
    
    condition_threshold {
      filter          = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND resource.type=\"uptime_url\" AND metric.labels.check_id=\"${google_monitoring_uptime_check_config.gateway_health.uptime_check_id}\""
      comparison      = "COMPARISON_EQ"
      threshold_value = 0
      duration        = "180s"
      
      aggregations {
        alignment_period   = "180s"
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
  
  documentation {
    content = "⚠️ **HIGH**: API Gateway service is down! This affects API routing to the orchestrator. Check Cloud Run logs and service status."
  }
}

# Alert policy for Frontend service failures
resource "google_monitoring_alert_policy" "frontend_uptime_alert" {
  display_name = "Frontend Service Down"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "Frontend uptime check failed"
    
    condition_threshold {
      filter          = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND resource.type=\"uptime_url\" AND metric.labels.check_id=\"${google_monitoring_uptime_check_config.frontend_health.uptime_check_id}\""
      comparison      = "COMPARISON_EQ"
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
  
  documentation {
    content = "📱 **MEDIUM**: Frontend service is down! Users cannot access the web interface. Check Cloud Run logs and service status."
  }
}

# Alert policy for Event Relay service failures
resource "google_monitoring_alert_policy" "event_relay_uptime_alert" {
  display_name = "Event Relay Service Down"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "Event Relay uptime check failed"
    
    condition_threshold {
      filter          = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND resource.type=\"uptime_url\" AND metric.labels.check_id=\"${google_monitoring_uptime_check_config.event_relay_health.uptime_check_id}\""
      comparison      = "COMPARISON_EQ"
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
  
  documentation {
    content = "🔄 **MEDIUM**: Event Relay service is down! This affects real-time dashboard updates. Check Cloud Run logs and Pub/Sub connectivity."
  }
}

# Alert policy for Agent services failures
# resource "google_monitoring_alert_policy" "agent_services_uptime_alert" {
#   display_name = "Agent Services Down"
#   project      = var.project_id
#   combiner     = "OR"
#   
#   conditions {
#     display_name = "Agent services uptime check failed"
#     
#     condition_threshold {
#       filter          = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND resource.type=\"uptime_url\" AND metric.labels.check_id=\"${google_monitoring_uptime_check_config.idea_agent_health.uptime_check_id}\""
#       comparison      = "COMPARISON_EQ"
#       threshold_value = 0
#       duration        = "300s"
#       
#       aggregations {
#         alignment_period   = "300s"
#         per_series_aligner = "ALIGN_FRACTION_TRUE"
#       }
#     }
#   }
#   
#   notification_channels = [
#     google_monitoring_notification_channel.slack.id,
#     google_monitoring_notification_channel.email.id
#   ]
#   
#   alert_strategy {
#     auto_close = "1800s"
#   }
#   
#   documentation {
#     content = "🤖 **MEDIUM**: One or more Agent services are down! This affects project processing capabilities. Check Cloud Run logs and database connectivity."
#   }
# }

# Alert policy for high error rate
resource "google_monitoring_alert_policy" "error_rate_alert" {
  display_name = "High Error Rate Alert"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "Error rate too high"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\""
      comparison      = "COMPARISON_GT"
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
      comparison      = "COMPARISON_GT"
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
      columns = 12
      tiles = [
        {
          width  = 6
          height = 4
          xPos   = 0
          yPos   = 0
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
          xPos   = 6
          yPos   = 0
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
        },
        {
          width  = 12
          height = 4
          xPos   = 0
          yPos   = 4
          widget = {
            title = "Service Uptime Status"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\""
                    aggregation = {
                      alignmentPeriod    = "60s"
                      perSeriesAligner   = "ALIGN_MEAN"
                      crossSeriesReducer = "REDUCE_MEAN"
                      groupByFields      = ["resource.label.uptime_check_id"]
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
          xPos   = 0
          yPos   = 8
          widget = {
            title = "Error Rate"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\""
                    aggregation = {
                      alignmentPeriod    = "60s"
                      perSeriesAligner   = "ALIGN_RATE"
                      crossSeriesReducer = "REDUCE_SUM"
                      groupByFields      = ["resource.label.service_name"]
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
          xPos   = 6
          yPos   = 8
          widget = {
            title = "Active Alerts"
            scorecard = {
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"global\" AND metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\""
                  aggregation = {
                    alignmentPeriod    = "60s"
                    perSeriesAligner   = "ALIGN_MEAN"
                    crossSeriesReducer = "REDUCE_COUNT"
                  }
                }
              }
            }
          }
        }
      ]
    }
  })
} 