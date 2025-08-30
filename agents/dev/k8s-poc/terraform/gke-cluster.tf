# Night 68: GKE Autopilot Cluster for DevAgent POC
# This creates a managed Kubernetes cluster optimized for the DevAgent deployment

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

# GKE Autopilot cluster
resource "google_container_cluster" "devagent_poc" {
  name     = var.cluster_name
  location = var.region
  project  = var.project_id

  # Enable Autopilot mode
  enable_autopilot = true

  # Network configuration
  network    = var.network_name
  subnetwork = var.subnet_name

  # IP allocation policy for VPC-native networking
  ip_allocation_policy {
    cluster_secondary_range_name  = var.pods_range_name
    services_secondary_range_name = var.services_range_name
  }

  # Private cluster configuration
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = var.master_ipv4_cidr_block
  }

  # Master authorized networks
  master_authorized_networks_config {
    dynamic "cidr_blocks" {
      for_each = var.authorized_networks
      content {
        cidr_block   = cidr_blocks.value.cidr_block
        display_name = cidr_blocks.value.display_name
      }
    }
  }

  # Workload Identity configuration
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Network policy (Autopilot enables this by default)
  network_policy {
    enabled = true
  }

  # Binary authorization (for enhanced security)
  binary_authorization {
    evaluation_mode = "PROJECT_SINGLETON_POLICY_ENFORCE"
  }

  # Database encryption (optional, for enhanced security)
  database_encryption {
    state    = var.database_encryption_enabled ? "ENCRYPTED" : "DECRYPTED"
    key_name = var.database_encryption_enabled ? var.kms_key_name : null
  }

  # Monitoring configuration
  monitoring_config {
    enable_components = [
      "SYSTEM_COMPONENTS",
      "WORKLOADS",
      "APISERVER",
      "SCHEDULER",
      "CONTROLLER_MANAGER"
    ]

    managed_prometheus {
      enabled = true
    }
  }

  # Logging configuration
  logging_config {
    enable_components = [
      "SYSTEM_COMPONENTS",
      "WORKLOADS",
      "APISERVER"
    ]
  }

  # Maintenance policy
  maintenance_policy {
    recurring_window {
      start_time = var.maintenance_start_time
      end_time   = var.maintenance_end_time
      recurrence = var.maintenance_recurrence
    }
  }

  # Addons configuration
  addons_config {
    horizontal_pod_autoscaling {
      disabled = false
    }

    http_load_balancing {
      disabled = false
    }

    network_policy_config {
      disabled = false
    }

    gcp_filestore_csi_driver_config {
      enabled = false # Not needed for DevAgent POC
    }

    gce_persistent_disk_csi_driver_config {
      enabled = true
    }

    config_connector_config {
      enabled = var.config_connector_enabled
    }

    gke_backup_agent_config {
      enabled = var.backup_agent_enabled
    }
  }

  # Resource usage export (for cost monitoring)
  resource_usage_export_config {
    enable_network_egress_metering       = true
    enable_resource_consumption_metering = true
    
    bigquery_destination {
      dataset_id = var.usage_export_dataset_id
    }
  }

  # Release channel for automatic updates
  release_channel {
    channel = var.release_channel
  }

  # Security configuration
  security_posture_config {
    mode               = "BASIC"
    vulnerability_mode = "VULNERABILITY_BASIC"
  }

  # Cost optimization
  cost_management_config {
    enabled = true
  }

  # Labels for resource management
  resource_labels = merge(var.cluster_labels, {
    purpose     = "devagent-poc"
    night       = "68"
    environment = "poc"
    managed-by  = "terraform"
  })

  # Timeouts
  timeouts {
    create = "30m"
    update = "40m"
    delete = "30m"
  }

  # Lifecycle management
  lifecycle {
    ignore_changes = [
      # Ignore node pool changes since Autopilot manages them
      node_pool,
      initial_node_count,
      remove_default_node_pool,
    ]
  }
}

# Node pool configuration (for reference, Autopilot manages this automatically)
# This is here for documentation purposes - Autopilot creates and manages node pools automatically
data "google_container_cluster" "devagent_poc" {
  name     = google_container_cluster.devagent_poc.name
  location = google_container_cluster.devagent_poc.location
  project  = var.project_id

  depends_on = [google_container_cluster.devagent_poc]
}

# Service account for Workload Identity
resource "google_service_account" "devagent_k8s" {
  account_id   = "devagent-k8s"
  display_name = "DevAgent Kubernetes Service Account"
  description  = "Service account for DevAgent running on GKE Autopilot"
  project      = var.project_id
}

# IAM bindings for the service account
resource "google_project_iam_member" "devagent_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.devagent_k8s.email}"
}

resource "google_project_iam_member" "devagent_cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.devagent_k8s.email}"
}

resource "google_project_iam_member" "devagent_monitoring_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.devagent_k8s.email}"
}

resource "google_project_iam_member" "devagent_logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.devagent_k8s.email}"
}

# Workload Identity binding
resource "google_service_account_iam_member" "devagent_workload_identity" {
  service_account_id = google_service_account.devagent_k8s.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[devagent-poc/devagent-service-account]"
}

# Optional: Cloud Armor security policy for ingress
resource "google_compute_security_policy" "devagent_security_policy" {
  count = var.enable_cloud_armor ? 1 : 0

  name        = "devagent-security-policy"
  description = "Security policy for DevAgent POC"
  project     = var.project_id

  # Default rule (allow all traffic by default)
  rule {
    action   = "allow"
    priority = "2147483647"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default allow rule"
  }

  # Rate limiting rule
  rule {
    action   = "rate_based_ban"
    priority = "1000"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      enforce_on_key = "IP"
      rate_limit_threshold {
        count        = 100
        interval_sec = 60
      }
      ban_duration_sec = 300
    }
    description = "Rate limit 100 requests per minute per IP"
  }

  # Block known malicious IPs (example)
  dynamic "rule" {
    for_each = var.blocked_ip_ranges
    content {
      action   = "deny(403)"
      priority = rule.key + 100
      match {
        versioned_expr = "SRC_IPS_V1"
        config {
          src_ip_ranges = [rule.value]
        }
      }
      description = "Block malicious IP range"
    }
  }
}

# Optional: SSL policy for HTTPS load balancer
resource "google_compute_ssl_policy" "devagent_ssl_policy" {
  count = var.enable_ssl_policy ? 1 : 0

  name            = "devagent-ssl-policy"
  description     = "SSL policy for DevAgent POC"
  project         = var.project_id
  profile         = "MODERN"
  min_tls_version = "TLS_1_2"
} 