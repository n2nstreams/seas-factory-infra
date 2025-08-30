# Night 68: Terraform Variables for DevAgent K8s POC
# Configuration variables for GKE Autopilot cluster

# Project Configuration
variable "project_id" {
  description = "The GCP project ID"
  type        = string
  validation {
    condition     = length(var.project_id) > 0
    error_message = "Project ID must not be empty."
  }
}

variable "region" {
  description = "The GCP region for the cluster"
  type        = string
  default     = "us-central1"
  validation {
    condition = can(regex("^[a-z]+-[a-z]+[0-9]$", var.region))
    error_message = "Region must be a valid GCP region format (e.g., us-central1)."
  }
}

# Cluster Configuration
variable "cluster_name" {
  description = "Name of the GKE cluster"
  type        = string
  default     = "devagent-poc-cluster"
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.cluster_name))
    error_message = "Cluster name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "cluster_labels" {
  description = "Labels to apply to the cluster"
  type        = map(string)
  default = {
    purpose     = "devagent-poc"
    environment = "poc"
    night       = "68"
  }
}

# Network Configuration
variable "network_name" {
  description = "Name of the VPC network"
  type        = string
  default     = "default"
}

variable "subnet_name" {
  description = "Name of the subnet"
  type        = string
  default     = "default"
}

variable "pods_range_name" {
  description = "Name of the secondary IP range for pods"
  type        = string
  default     = "gke-pods"
}

variable "services_range_name" {
  description = "Name of the secondary IP range for services"
  type        = string
  default     = "gke-services"
}

variable "master_ipv4_cidr_block" {
  description = "CIDR block for the master nodes"
  type        = string
  default     = "172.16.0.0/28"
  validation {
    condition     = can(cidrhost(var.master_ipv4_cidr_block, 0))
    error_message = "Master CIDR block must be a valid CIDR notation."
  }
}

variable "authorized_networks" {
  description = "List of authorized networks for cluster access"
  type = list(object({
    cidr_block   = string
    display_name = string
  }))
  default = [
    {
      cidr_block   = "0.0.0.0/0"
      display_name = "All networks (POC only - restrict in production)"
    }
  ]
}

# Security Configuration
variable "database_encryption_enabled" {
  description = "Enable Application-layer Secrets Encryption (envelope encryption)"
  type        = bool
  default     = false
}

variable "kms_key_name" {
  description = "The Cloud KMS key to use for database encryption"
  type        = string
  default     = null
}

variable "enable_cloud_armor" {
  description = "Enable Cloud Armor security policy"
  type        = bool
  default     = false
}

variable "enable_ssl_policy" {
  description = "Enable SSL policy for HTTPS load balancer"
  type        = bool
  default     = false
}

variable "blocked_ip_ranges" {
  description = "List of IP ranges to block (for Cloud Armor)"
  type        = list(string)
  default     = []
}

# Maintenance Configuration
variable "maintenance_start_time" {
  description = "Start time for maintenance window (RFC3339 format)"
  type        = string
  default     = "2023-01-01T02:00:00Z"
}

variable "maintenance_end_time" {
  description = "End time for maintenance window (RFC3339 format)"
  type        = string
  default     = "2023-01-01T06:00:00Z"
}

variable "maintenance_recurrence" {
  description = "Recurrence pattern for maintenance window"
  type        = string
  default     = "FREQ=WEEKLY;BYDAY=SA"
}

# Cluster Features
variable "config_connector_enabled" {
  description = "Enable Config Connector addon"
  type        = bool
  default     = false
}

variable "backup_agent_enabled" {
  description = "Enable GKE Backup agent"
  type        = bool
  default     = false
}

variable "release_channel" {
  description = "Release channel for cluster updates"
  type        = string
  default     = "REGULAR"
  validation {
    condition     = contains(["RAPID", "REGULAR", "STABLE", "UNSPECIFIED"], var.release_channel)
    error_message = "Release channel must be one of: RAPID, REGULAR, STABLE, UNSPECIFIED."
  }
}

# Monitoring and Logging
variable "usage_export_dataset_id" {
  description = "BigQuery dataset ID for resource usage export"
  type        = string
  default     = null
}

variable "enable_workload_monitoring" {
  description = "Enable workload monitoring"
  type        = bool
  default     = true
}

variable "enable_system_monitoring" {
  description = "Enable system component monitoring"
  type        = bool
  default     = true
}

# Cost Management
variable "enable_cost_allocation" {
  description = "Enable cost allocation tracking"
  type        = bool
  default     = true
}

# Environment and Tags
variable "environment" {
  description = "Environment name (poc, dev, staging, prod)"
  type        = string
  default     = "poc"
  validation {
    condition     = contains(["poc", "dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: poc, dev, staging, prod."
  }
}

variable "team" {
  description = "Team responsible for the cluster"
  type        = string
  default     = "saas-factory"
}

variable "cost_center" {
  description = "Cost center for billing"
  type        = string
  default     = "engineering"
}

# Advanced Configuration
variable "enable_vertical_pod_autoscaling" {
  description = "Enable Vertical Pod Autoscaling"
  type        = bool
  default     = true
}

variable "enable_network_policy" {
  description = "Enable Kubernetes Network Policy"
  type        = bool
  default     = true
}

variable "enable_binary_authorization" {
  description = "Enable Binary Authorization"
  type        = bool
  default     = false
}

variable "enable_pod_security_policy" {
  description = "Enable Pod Security Policy (deprecated, use Pod Security Standards)"
  type        = bool
  default     = false
}

# DNS Configuration
variable "cluster_dns_provider" {
  description = "DNS provider for the cluster"
  type        = string
  default     = "CLOUD_DNS"
  validation {
    condition     = contains(["PLATFORM_DEFAULT", "CLOUD_DNS"], var.cluster_dns_provider)
    error_message = "DNS provider must be either PLATFORM_DEFAULT or CLOUD_DNS."
  }
}

variable "cluster_dns_scope" {
  description = "DNS scope for the cluster"
  type        = string
  default     = "CLUSTER_SCOPE"
  validation {
    condition     = contains(["CLUSTER_SCOPE", "VPC_SCOPE"], var.cluster_dns_scope)
    error_message = "DNS scope must be either CLUSTER_SCOPE or VPC_SCOPE."
  }
}

# Resource Configuration
variable "initial_node_count" {
  description = "Initial number of nodes (ignored in Autopilot)"
  type        = number
  default     = 1
}

variable "max_node_count" {
  description = "Maximum number of nodes per zone"
  type        = number
  default     = 10
}

# Timeouts
variable "cluster_create_timeout" {
  description = "Timeout for cluster creation"
  type        = string
  default     = "30m"
}

variable "cluster_update_timeout" {
  description = "Timeout for cluster updates"
  type        = string
  default     = "40m"
}

variable "cluster_delete_timeout" {
  description = "Timeout for cluster deletion"
  type        = string
  default     = "30m"
} 