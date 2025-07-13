output "service_url" {
  description = "The URL of the Cloud Run service"
  value       = google_cloud_run_v2_service.agent.uri
}

output "service_name" {
  description = "The name of the Cloud Run service"
  value       = google_cloud_run_v2_service.agent.name
}

output "db_user_name" {
  description = "The database user name for this agent"
  value       = google_sql_user.agent.name
}

output "db_user_password" {
  description = "The database user password for this agent"
  value       = google_sql_user.agent.password
  sensitive   = true
}

output "neg_id" {
  description = "The ID of the Network Endpoint Group (if created)"
  value       = var.create_neg ? google_compute_region_network_endpoint_group.agent_neg[0].id : null
} 