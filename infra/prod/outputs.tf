output "cloudsql_postgres_instance_connection_name" {
  description = "The connection name of the Cloud SQL instance."
  value       = module.cloudsql_postgres.instance_connection_name
}

output "cloudsql_postgres_user" {
  description = "The name of the default user."
  value       = var.db_user
}

output "cloudsql_postgres_password" {
  description = "The password for the default user."
  value       = var.db_password
  sensitive   = true
}

output "cloudsql_instance_name" {
  description = "The name of the Cloud SQL instance"
  value       = module.cloudsql_postgres.instance_name
}

# Cloud Run service URLs
output "api_central_url" {
  description = "The URL of the central Cloud Run service"
  value       = google_cloud_run_v2_service.api_central.uri
}

output "api_east_url" {
  description = "The URL of the east Cloud Run service"
  value       = google_cloud_run_v2_service.api_east.uri
}

# Load balancer IP
output "lb_ip_address" {
  description = "The IP address of the load balancer"
  value       = google_compute_global_address.lb_ip.address
}

# API domain
output "api_domain" {
  description = "The domain for the API"
  value       = "api.${var.project_id}.com"
}

# Artifact Registry repository
output "artifact_registry_repository" {
  description = "The Artifact Registry repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/saas-factory"
}

# Monitoring dashboard
output "monitoring_dashboard_url" {
  description = "The URL of the monitoring dashboard"
  value       = "https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.api_dashboard.id}?project=${var.project_id}"
}

# Workload Identity outputs for GitHub Actions
output "gh_provider_name" {
  description = "The full name of the GitHub OIDC provider"
  value       = google_iam_workload_identity_pool_provider.gh_provider.name
}

output "gha_deployer_email" {
  description = "The email address of the GitHub Actions deployer service account"
  value       = google_service_account.gha_deployer.email
}

output "workload_identity_pool_id" {
  description = "The ID of the workload identity pool"
  value       = google_iam_workload_identity_pool.gh_pool.workload_identity_pool_id
} 