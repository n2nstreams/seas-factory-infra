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

# Load balancer IP addresses
output "api_lb_ip_address" {
  description = "The IP address of the API load balancer (for DNS A record: api.forge95.com)"
  value       = google_compute_global_address.lb_ip.address
}

output "frontend_lb_ip_address" {
  description = "The IP address of the frontend load balancer (for DNS A record: www.forge95.com)"
  value       = google_compute_global_address.frontend_lb_ip.address
}

# Custom domains
output "api_domain" {
  description = "The custom domain for the API"
  value       = "${var.api_subdomain}.${var.domain_name}"
}

output "frontend_domain" {
  description = "The custom domain for the frontend"
  value       = "${var.www_subdomain}.${var.domain_name}"
}

output "apex_domain" {
  description = "The apex domain"
  value       = var.domain_name
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

output "ui_staging_bucket_name" {
  description = "The name of the UI staging bucket"
  value       = google_storage_bucket.ui_staging.name
}

# Orchestrator service account
output "orchestrator_sa_email" {
  description = "The email address of the orchestrator service account"
  value       = google_service_account.orchestrator_sa.email
}

# Orchestrator endpoint
output "orchestrator_endpoint" {
  description = "The endpoint URI for the Project Orchestrator"
  value       = google_cloud_run_v2_service.orchestrator.uri
}

# Agent service endpoints
output "idea_agent_url" {
  description = "The URL of the Idea Agent service"
  value       = module.idea_agent.service_url
}

output "design_agent_url" {
  description = "The URL of the Design Agent service"
  value       = module.design_agent.service_url
}

output "dev_agent_url" {
  description = "The URL of the Dev Agent service"
  value       = module.dev_agent.service_url
}

# SSL Certificate Status (for monitoring certificate provisioning)
output "api_ssl_certificate_id" {
  description = "ID of the API SSL certificate"
  value       = google_compute_managed_ssl_certificate.api_ssl_cert.id
}

output "frontend_ssl_certificate_id" {
  description = "ID of the frontend SSL certificate"
  value       = google_compute_managed_ssl_certificate.frontend_ssl_cert.id
}

# SSL Certificate domains
output "api_ssl_certificate_domains" {
  description = "Domains covered by the API SSL certificate"
  value       = google_compute_managed_ssl_certificate.api_ssl_cert.managed[0].domains
}

output "frontend_ssl_certificate_domains" {
  description = "Domains covered by the frontend SSL certificate"
  value       = google_compute_managed_ssl_certificate.frontend_ssl_cert.managed[0].domains
}

# Custom domain URLs (complete URLs)
output "custom_api_url" {
  description = "Complete HTTPS URL for the custom domain API"
  value       = "https://${var.api_subdomain}.${var.domain_name}"
}

output "custom_frontend_url" {
  description = "Complete HTTPS URL for the custom domain frontend"
  value       = "https://${var.www_subdomain}.${var.domain_name}"
}

output "qa_agent_url" {
  description = "The URL of the QA Agent service"
  value       = module.qa_agent.service_url
}

output "ops_agent_url" {
  description = "The URL of the Ops Agent service"
  value       = module.ops_agent.service_url
}

output "techstack_agent_url" {
  description = "The URL of the TechStack Agent service"
  value       = module.techstack_agent.service_url
} 