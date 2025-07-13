# Global HTTP(S) Load Balancer with serverless NEGs
resource "google_compute_global_address" "lb_ip" {
  name         = "lb-ip"
  address_type = "EXTERNAL"
  project      = var.project_id
}

# Serverless NEG for us-central1
resource "google_compute_region_network_endpoint_group" "neg_central" {
  name                  = "neg-central"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  project               = var.project_id
  
  cloud_run {
    service = google_cloud_run_v2_service.api_central.name
  }
}

# Serverless NEG for us-east1
resource "google_compute_region_network_endpoint_group" "neg_east" {
  name                  = "neg-east"
  network_endpoint_type = "SERVERLESS"
  region                = "us-east1"
  project               = var.project_id
  
  cloud_run {
    service = google_cloud_run_v2_service.api_east.name
  }
}

# Backend service
resource "google_compute_backend_service" "backend" {
  name                  = "api-backend-service"
  project               = var.project_id
  protocol              = "HTTP"
  timeout_sec           = 30
  load_balancing_scheme = "EXTERNAL_MANAGED"
  
  backend {
    group = google_compute_region_network_endpoint_group.neg_central.id
  }
  
  backend {
    group = google_compute_region_network_endpoint_group.neg_east.id
  }
  
  health_checks = [google_compute_health_check.health_check.id]
}

# Backend service for agent services
resource "google_compute_backend_service" "agents_backend" {
  name                  = "agents-backend-service"
  project               = var.project_id
  protocol              = "HTTP"
  timeout_sec           = 30
  load_balancing_scheme = "EXTERNAL_MANAGED"
  
  backend {
    group = module.idea_agent.neg_id
  }
  
  backend {
    group = module.design_agent.neg_id
  }
  
  backend {
    group = module.dev_agent.neg_id
  }
  
  backend {
    group = module.qa_agent.neg_id
  }
  
  backend {
    group = module.ops_agent.neg_id
  }
  
  backend {
    group = module.techstack_agent.neg_id
  }
  
  health_checks = [google_compute_health_check.agents_health_check.id]
}

# Health check for agent services
resource "google_compute_health_check" "agents_health_check" {
  name               = "agents-health-check"
  project            = var.project_id
  check_interval_sec = 30
  timeout_sec        = 5
  
  http_health_check {
    port         = 8080
    request_path = "/health"
  }
}

# Health check
resource "google_compute_health_check" "health_check" {
  name               = "api-health-check"
  project            = var.project_id
  check_interval_sec = 30
  timeout_sec        = 5
  
  http_health_check {
    port         = 8080
    request_path = "/health"
  }
}

# URL map with path-based routing
resource "google_compute_url_map" "url_map" {
  name            = "api-url-map"
  project         = var.project_id
  default_service = google_compute_backend_service.backend.id
  
  path_matcher {
    name            = "agents-matcher"
    default_service = google_compute_backend_service.backend.id
    
    path_rule {
      paths   = ["/agents/*"]
      service = google_compute_backend_service.agents_backend.id
    }
    
    path_rule {
      paths   = ["/idea/*"]
      service = google_compute_backend_service.agents_backend.id
    }
    
    path_rule {
      paths   = ["/design/*"]
      service = google_compute_backend_service.agents_backend.id
    }
    
    path_rule {
      paths   = ["/dev/*"]
      service = google_compute_backend_service.agents_backend.id
    }
    
    path_rule {
      paths   = ["/qa/*"]
      service = google_compute_backend_service.agents_backend.id
    }
    
    path_rule {
      paths   = ["/ops/*"]
      service = google_compute_backend_service.agents_backend.id
    }
    
    path_rule {
      paths   = ["/techstack/*"]
      service = google_compute_backend_service.agents_backend.id
    }
  }
  
  host_rule {
    hosts        = ["*"]
    path_matcher = "agents-matcher"
  }
}

# Managed SSL certificate
resource "google_compute_managed_ssl_certificate" "ssl_cert" {
  name    = "api-ssl-cert"
  project = var.project_id
  
  managed {
    domains = ["api.${var.project_id}.com"]
  }
}

# HTTPS proxy
resource "google_compute_target_https_proxy" "https_proxy" {
  name             = "api-https-proxy"
  project          = var.project_id
  url_map          = google_compute_url_map.url_map.id
  ssl_certificates = [google_compute_managed_ssl_certificate.ssl_cert.id]
}

# Global forwarding rule
resource "google_compute_global_forwarding_rule" "forwarding_rule" {
  name       = "api-forwarding-rule"
  project    = var.project_id
  target     = google_compute_target_https_proxy.https_proxy.id
  port_range = "443"
  ip_address = google_compute_global_address.lb_ip.address
}

# HTTP to HTTPS redirect
resource "google_compute_url_map" "http_redirect" {
  name    = "api-http-redirect"
  project = var.project_id
  
  default_url_redirect {
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    https_redirect         = true
    strip_query            = false
  }
}

resource "google_compute_target_http_proxy" "http_proxy" {
  name    = "api-http-proxy"
  project = var.project_id
  url_map = google_compute_url_map.http_redirect.id
}

resource "google_compute_global_forwarding_rule" "http_forwarding_rule" {
  name       = "api-http-forwarding-rule"
  project    = var.project_id
  target     = google_compute_target_http_proxy.http_proxy.id
  port_range = "80"
  ip_address = google_compute_global_address.lb_ip.address
} 