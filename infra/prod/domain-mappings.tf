# Cloud Run Domain Mappings for Custom Domains
# TEMPORARILY DISABLED - Frontend service needs to be healthy first

# Domain mapping for API Gateway
# resource "google_cloud_run_domain_mapping" "api_domain_mapping" {
#   location = var.region
#   name     = "${var.api_subdomain}.${var.domain_name}"
#   project  = var.project_id

#   metadata {
#     namespace = var.project_id
#   }

#   spec {
#     route_name = google_cloud_run_v2_service.gateway.name
#   }

#   depends_on = [
#     google_cloud_run_v2_service.gateway,
#     google_compute_managed_ssl_certificate.api_ssl_cert
#   ]
# }

# Domain mapping for Frontend
# resource "google_cloud_run_domain_mapping" "frontend_domain_mapping" {
#   location = var.region
#   name     = "${var.www_subdomain}.${var.domain_name}"
#   project  = var.project_id

#   metadata {
#     namespace = var.project_id
#   }

#   spec {
#     route_name = google_cloud_run_v2_service.frontend.name
#   }

#   depends_on = [
#     google_cloud_run_v2_service.frontend,
#     google_compute_managed_ssl_certificate.frontend_ssl_cert
#   ]
# }

# Optional: Domain mapping for bare domain (forge95.com -> www.forge95.com)
# resource "google_cloud_run_domain_mapping" "apex_domain_mapping" {
#   location = var.region
#   name     = var.domain_name
#   project  = var.project_id

#   metadata {
#     namespace = var.project_id
#   }

#   spec {
#     route_name = google_cloud_run_v2_service.frontend.name
#   }

#   depends_on = [
#     google_cloud_run_v2_service.frontend
#   ]
# }

# ⚠️  DOMAIN MAPPINGS TEMPORARILY DISABLED
# Frontend service needs to be healthy before domain mappings can be created
# Once the service is running properly, re-enable these resources 