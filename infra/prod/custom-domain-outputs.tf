# Custom Domain Outputs Only

# Load balancer IP addresses for DNS configuration
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

# Custom domain URLs (complete URLs)
output "custom_api_url" {
  description = "Complete HTTPS URL for the custom domain API"
  value       = "https://${var.api_subdomain}.${var.domain_name}"
}

output "custom_frontend_url" {
  description = "Complete HTTPS URL for the custom domain frontend"
  value       = "https://${var.www_subdomain}.${var.domain_name}"
}

# SSL Certificate IDs
output "api_ssl_certificate_id" {
  description = "ID of the API SSL certificate"
  value       = google_compute_managed_ssl_certificate.api_ssl_cert.id
}

output "frontend_ssl_certificate_id" {
  description = "ID of the frontend SSL certificate"
  value       = google_compute_managed_ssl_certificate.frontend_ssl_cert.id
} 