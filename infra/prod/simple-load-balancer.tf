# Simplified Load Balancer for API Gateway Custom Domain

# Global IP address for API load balancer
resource "google_compute_global_address" "lb_ip" {
  name         = "api-lb-ip"
  address_type = "EXTERNAL"
  project      = var.project_id
}

# Serverless NEG for API Gateway
resource "google_compute_region_network_endpoint_group" "api_neg" {
  name                  = "api-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  project               = var.project_id
  
  cloud_run {
    service = google_cloud_run_v2_service.gateway.name
  }
}

# Backend service for API Gateway
resource "google_compute_backend_service" "api_backend" {
  name                  = "api-backend-service"
  project               = var.project_id
  protocol              = "HTTP"
  timeout_sec           = 30
  load_balancing_scheme = "EXTERNAL_MANAGED"
  
  backend {
    group = google_compute_region_network_endpoint_group.api_neg.id
  }
  
  # Note: Health checks are not compatible with serverless NEGs
}

# URL map for API
resource "google_compute_url_map" "api_url_map" {
  name            = "api-url-map"
  project         = var.project_id
  default_service = google_compute_backend_service.api_backend.id
}

# Managed SSL certificate for API
resource "google_compute_managed_ssl_certificate" "api_ssl_cert" {
  name    = "api-ssl-cert"
  project = var.project_id
  
  managed {
    domains = ["${var.api_subdomain}.${var.domain_name}"]
  }
}

# HTTPS proxy for API
resource "google_compute_target_https_proxy" "api_https_proxy" {
  name             = "api-https-proxy"
  project          = var.project_id
  url_map          = google_compute_url_map.api_url_map.id
  ssl_certificates = [google_compute_managed_ssl_certificate.api_ssl_cert.id]
}

# Global forwarding rule for API HTTPS
resource "google_compute_global_forwarding_rule" "api_https_forwarding_rule" {
  name       = "api-https-forwarding-rule"
  project    = var.project_id
  target     = google_compute_target_https_proxy.api_https_proxy.id
  port_range = "443"
  ip_address = google_compute_global_address.lb_ip.address
}

# HTTP to HTTPS redirect for API
resource "google_compute_url_map" "api_http_redirect" {
  name    = "api-http-redirect"
  project = var.project_id
  
  default_url_redirect {
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    https_redirect         = true
    strip_query            = false
  }
}

resource "google_compute_target_http_proxy" "api_http_proxy" {
  name    = "api-http-proxy"
  project = var.project_id
  url_map = google_compute_url_map.api_http_redirect.id
}

resource "google_compute_global_forwarding_rule" "api_http_forwarding_rule" {
  name       = "api-http-forwarding-rule"
  project    = var.project_id
  target     = google_compute_target_http_proxy.api_http_proxy.id
  port_range = "80"
  ip_address = google_compute_global_address.lb_ip.address
} 