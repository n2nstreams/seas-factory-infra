resource "google_compute_global_address" "private_ip_address" {
  project       = var.project_id
  name          = "private-ip-for-gcp-services"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = module.network_base.network_self_link
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = module.network_base.network_self_link
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
  depends_on              = [google_compute_global_address.private_ip_address]
}

module "cloudsql_postgres" {
  source  = "terraform-google-modules/sql-db/google//modules/postgresql"
  version = "~> 13.0"

  project_id      = var.project_id
  name            = "psql-saas-factory"
  region          = var.region
  zone            = "${var.region}-a"
  tier            = "db-custom-1-3840"
  disk_size       = 20
  disk_autoresize = true

  database_version = "POSTGRES_15"

  ip_configuration = {
    ipv4_enabled         = false
    private_network      = module.network_base.network_self_link
    allocated_ip_range   = ""
    authorized_networks  = []
    require_ssl          = false
  }

  user_name     = var.db_user
  user_password = var.db_password
  module_depends_on = [google_service_networking_connection.private_vpc_connection]
}

resource "google_sql_database" "factorydb" {
  project  = var.project_id
  name     = var.db_name
  instance = module.cloudsql_postgres.instance_name
} 