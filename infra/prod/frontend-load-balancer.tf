# Frontend Load Balancer Configuration for www.launch84.com

# Global IP address for frontend load balancer
resource "google_compute_global_address" "frontend_lb_ip" {
  name         = "frontend-lb-ip"
  address_type = "EXTERNAL"
  project      = var.project_id
}

# Serverless NEG for frontend Cloud Run service
resource "google_compute_region_network_endpoint_group" "frontend_neg" {
  name                  = "frontend-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  project               = var.project_id
  
  cloud_run {
    service = google_cloud_run_v2_service.frontend.name
  }
}

# Backend service for frontend
resource "google_compute_backend_service" "frontend_backend" {
  name                  = "frontend-backend-service"
  project               = var.project_id
  protocol              = "HTTP"
  timeout_sec           = 30
  load_balancing_scheme = "EXTERNAL_MANAGED"
  
  backend {
    group = google_compute_region_network_endpoint_group.frontend_neg.id
  }
  
  health_checks = [google_compute_health_check.frontend_health_check.id]
}

# Health check for frontend
resource "google_compute_health_check" "frontend_health_check" {
  name               = "frontend-health-check"
  project            = var.project_id
  check_interval_sec = 30
  timeout_sec        = 5
  
  http_health_check {
    port         = 80
    request_path = "/"
  }
}

# URL map for frontend
resource "google_compute_url_map" "frontend_url_map" {
  name            = "frontend-url-map"
  project         = var.project_id
  default_service = google_compute_backend_service.frontend_backend.id
}

# Managed SSL certificate for frontend
resource "google_compute_managed_ssl_certificate" "frontend_ssl_cert" {
  name    = "frontend-ssl-cert"
  project = var.project_id
  
  managed {
    domains = ["${var.www_subdomain}.${var.domain_name}"]
  }
}

# HTTPS proxy for frontend
resource "google_compute_target_https_proxy" "frontend_https_proxy" {
  name             = "frontend-https-proxy"
  project          = var.project_id
  url_map          = google_compute_url_map.frontend_url_map.id
  ssl_certificates = [google_compute_managed_ssl_certificate.frontend_ssl_cert.id]
}

# Global forwarding rule for frontend HTTPS
resource "google_compute_global_forwarding_rule" "frontend_https_forwarding_rule" {
  name       = "frontend-https-forwarding-rule"
  project    = var.project_id
  target     = google_compute_target_https_proxy.frontend_https_proxy.id
  port_range = "443"
  ip_address = google_compute_global_address.frontend_lb_ip.address
}

# HTTP to HTTPS redirect for frontend
resource "google_compute_url_map" "frontend_http_redirect" {
  name    = "frontend-http-redirect"
  project = var.project_id
  
  default_url_redirect {
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    https_redirect         = true
    strip_query            = false
  }
}

resource "google_compute_target_http_proxy" "frontend_http_proxy" {
  name    = "frontend-http-proxy"
  project = var.project_id
  url_map = google_compute_url_map.frontend_http_redirect.id
}

resource "google_compute_global_forwarding_rule" "frontend_http_forwarding_rule" {
  name       = "frontend-http-forwarding-rule"
  project    = var.project_id
  target     = google_compute_target_http_proxy.frontend_http_proxy.id
  port_range = "80"
  ip_address = google_compute_global_address.frontend_lb_ip.address
} 