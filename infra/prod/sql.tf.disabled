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

  # Enhanced backup configuration for primary instance
  backup_configuration = {
    enabled                        = true
    start_time                     = "02:00"
    point_in_time_recovery_enabled = true
    backup_retention_settings = {
      retained_backups = 7
      retention_unit   = "COUNT"
    }
  }

  ip_configuration = {
    ipv4_enabled         = false
    private_network      = module.network_base.network_self_link
    allocated_ip_range   = ""
    authorized_networks  = []
    require_ssl          = false
  }

  # Enable pgvector extension
  database_flags = [
    {
      name  = "shared_preload_libraries"
      value = "pgvector"
    }
  ]

  user_name     = var.db_user
  user_password = var.db_password
  module_depends_on = [google_service_networking_connection.private_vpc_connection]
}

resource "google_sql_database" "factorydb" {
  project  = var.project_id
  name     = var.db_name
  instance = module.cloudsql_postgres.instance_name
}

# Application user for Cloud Run services
resource "google_sql_user" "app" {
  name     = "appuser"
  instance = module.cloudsql_postgres.instance_name
  password = random_password.appuser.result
  project  = var.project_id
}

resource "random_password" "appuser" {
  length  = 16
  special = true
}

# Failover configuration and monitoring
resource "google_monitoring_alert_policy" "database_failover" {
  project      = var.project_id
  display_name = "Database Instance Failover Alert"
  
  conditions {
    display_name = "Database instance is down"
    condition_threshold {
      filter         = "resource.type=\"gce_instance\" AND resource.labels.instance_id=\"${module.cloudsql_postgres.instance_name}\""
      comparison     = "COMPARISON_LESS_THAN"
      threshold_value = 1
      duration       = "60s"
      
      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_MEAN"
        cross_series_reducer = "REDUCE_MEAN"
      }
    }
  }

  notification_channels = []
  
  alert_strategy {
    auto_close = "1800s"
  }
}

# Cloud SQL Read Replica in us-east1 for disaster recovery
resource "google_sql_database_instance" "read_replica_east" {
  project             = var.project_id
  name                = "psql-saas-factory-replica-east"
  region              = "us-east1"
  database_version    = "POSTGRES_15"
  master_instance_name = module.cloudsql_postgres.instance_name

  replica_configuration {
    failover_target = true
  }

  settings {
    tier                        = "db-custom-1-3840"
    disk_size                   = 20
    disk_autoresize            = true
    disk_autoresize_limit      = 100
    availability_type          = "REGIONAL"
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 7
        retention_unit   = "COUNT"
      }
    }
    
    ip_configuration {
      ipv4_enabled         = false
      private_network      = module.network_base.network_self_link
      allocated_ip_range   = ""
      authorized_networks  = []
      require_ssl          = false
    }

    database_flags {
      name  = "shared_preload_libraries"
      value = "pgvector"
    }
  }

  depends_on = [
    module.cloudsql_postgres,
    google_service_networking_connection.private_vpc_connection
  ]
}

# Additional read replica in us-central1 for load distribution
resource "google_sql_database_instance" "read_replica_central" {
  project             = var.project_id
  name                = "psql-saas-factory-replica-central"
  region              = var.region
  database_version    = "POSTGRES_15"
  master_instance_name = module.cloudsql_postgres.instance_name

  replica_configuration {
    failover_target = false  # This is just for read load distribution
  }

  settings {
    tier                        = "db-custom-1-3840"
    disk_size                   = 20
    disk_autoresize            = true
    disk_autoresize_limit      = 100
    availability_type          = "REGIONAL"
    
    ip_configuration {
      ipv4_enabled         = false
      private_network      = module.network_base.network_self_link
      allocated_ip_range   = ""
      authorized_networks  = []
      require_ssl          = false
    }

    database_flags {
      name  = "shared_preload_libraries"
      value = "pgvector"
    }
  }

  depends_on = [
    module.cloudsql_postgres,
    google_service_networking_connection.private_vpc_connection
  ]
}

# Output the replica instances for configuration
output "primary_instance_name" {
  description = "Name of the primary Cloud SQL instance"
  value       = module.cloudsql_postgres.instance_name
}

output "read_replica_east_name" {
  description = "Name of the us-east1 read replica instance"
  value       = google_sql_database_instance.read_replica_east.name
}

output "read_replica_central_name" {
  description = "Name of the us-central1 read replica instance" 
  value       = google_sql_database_instance.read_replica_central.name
}

output "primary_instance_ip" {
  description = "Private IP of the primary instance"
  value       = module.cloudsql_postgres.private_ip_address
}

output "read_replica_east_ip" {
  description = "Private IP of the us-east1 replica"
  value       = google_sql_database_instance.read_replica_east.private_ip_address
} 