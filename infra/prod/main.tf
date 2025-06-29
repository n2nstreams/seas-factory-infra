module "network_base" {
  source  = "terraform-google-modules/network/google"
  version = "~> 7.0"

  project_id   = var.project_id
  network_name = "vpc-saas-factory"
  routing_mode = "GLOBAL"

  subnets = [
    {
      subnet_name           = "public-subnet"
      subnet_ip             = "10.10.10.0/24"
      subnet_region         = var.region
      subnet_private_access = "true"
      subnet_flow_logs      = "true"
    },
    {
      subnet_name           = "private-subnet"
      subnet_ip             = "10.10.20.0/24"
      subnet_region         = var.region
      subnet_private_access = "true"
      subnet_flow_logs      = "true"
    }
  ]
}

resource "google_compute_router" "router" {
  name    = "cr-vpc-saas-factory"
  network = module.network_base.network_name
  region  = var.region
  project = var.project_id
}

module "cloud-nat" {
  source  = "terraform-google-modules/cloud-nat/google"
  version = "~> 5.0"

  project_id = var.project_id
  region     = var.region
  router     = google_compute_router.router.name
  name       = "nat-gateway"

  log_config_enable = true
  log_config_filter = "ERRORS_ONLY"
} 