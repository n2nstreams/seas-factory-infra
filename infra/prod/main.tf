# Common labels for all resources
locals {
  common_labels = {
    project     = var.project_id
    environment = "production"
    managed_by  = "terraform"
    owner       = var.owner_email
    cost_center = "saas-factory"
  }
}

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
      log_config = {
        aggregation_interval = "INTERVAL_5_SEC"
        flow_sampling       = 0.5
        metadata            = "INCLUDE_ALL_METADATA"
      }
    },
    {
      subnet_name           = "private-subnet"
      subnet_ip             = "10.10.20.0/24"
      subnet_region         = var.region
      subnet_private_access = "true"
      subnet_flow_logs      = "true"
      log_config = {
        aggregation_interval = "INTERVAL_5_SEC"
        flow_sampling       = 0.5
        metadata            = "INCLUDE_ALL_METADATA"
      }
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
  
  # Enhanced NAT configuration
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  nat_ips = []
} 