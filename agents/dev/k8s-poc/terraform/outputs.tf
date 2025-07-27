# Night 68: Terraform Outputs for DevAgent K8s POC
# Outputs for GKE Autopilot cluster and related resources

# Cluster Information
output "cluster_name" {
  description = "Name of the GKE cluster"
  value       = google_container_cluster.devagent_poc.name
}

output "cluster_location" {
  description = "Location of the GKE cluster"
  value       = google_container_cluster.devagent_poc.location
}

output "cluster_endpoint" {
  description = "Endpoint for the GKE cluster"
  value       = google_container_cluster.devagent_poc.endpoint
  sensitive   = true
}

output "cluster_ca_certificate" {
  description = "Base64 encoded CA certificate for the cluster"
  value       = google_container_cluster.devagent_poc.master_auth.0.cluster_ca_certificate
  sensitive   = true
}

output "cluster_master_version" {
  description = "Current master version of the cluster"
  value       = google_container_cluster.devagent_poc.master_version
}

output "cluster_node_version" {
  description = "Current node version of the cluster"
  value       = google_container_cluster.devagent_poc.node_version
}

output "cluster_status" {
  description = "Status of the cluster"
  value       = google_container_cluster.devagent_poc.status
}

# Service Account Information
output "devagent_service_account_email" {
  description = "Email of the DevAgent service account"
  value       = google_service_account.devagent_k8s.email
}

output "devagent_service_account_name" {
  description = "Name of the DevAgent service account"
  value       = google_service_account.devagent_k8s.name
}

output "devagent_service_account_unique_id" {
  description = "Unique ID of the DevAgent service account"
  value       = google_service_account.devagent_k8s.unique_id
}

# Network Information
output "cluster_network" {
  description = "Network used by the cluster"
  value       = google_container_cluster.devagent_poc.network
}

output "cluster_subnetwork" {
  description = "Subnetwork used by the cluster"
  value       = google_container_cluster.devagent_poc.subnetwork
}

output "cluster_private_endpoint" {
  description = "Private endpoint for the cluster"
  value       = google_container_cluster.devagent_poc.private_cluster_config.0.private_endpoint
  sensitive   = true
}

output "cluster_public_endpoint" {
  description = "Public endpoint for the cluster"
  value       = google_container_cluster.devagent_poc.endpoint
  sensitive   = true
}

# Security Information
output "workload_identity_pool" {
  description = "Workload Identity pool for the cluster"
  value       = google_container_cluster.devagent_poc.workload_identity_config.0.workload_pool
}

output "security_policy_name" {
  description = "Name of the Cloud Armor security policy (if enabled)"
  value       = var.enable_cloud_armor ? google_compute_security_policy.devagent_security_policy[0].name : null
}

output "ssl_policy_name" {
  description = "Name of the SSL policy (if enabled)"
  value       = var.enable_ssl_policy ? google_compute_ssl_policy.devagent_ssl_policy[0].name : null
}

# Cluster Configuration
output "cluster_autopilot_enabled" {
  description = "Whether Autopilot is enabled"
  value       = google_container_cluster.devagent_poc.enable_autopilot
}

output "cluster_release_channel" {
  description = "Release channel configuration"
  value       = google_container_cluster.devagent_poc.release_channel.0.channel
}

output "cluster_monitoring_enabled_components" {
  description = "Enabled monitoring components"
  value       = google_container_cluster.devagent_poc.monitoring_config.0.enable_components
}

output "cluster_logging_enabled_components" {
  description = "Enabled logging components"
  value       = google_container_cluster.devagent_poc.logging_config.0.enable_components
}

# Connection Information
output "kubectl_connection_command" {
  description = "Command to connect kubectl to this cluster"
  value       = "gcloud container clusters get-credentials ${google_container_cluster.devagent_poc.name} --region=${google_container_cluster.devagent_poc.location} --project=${var.project_id}"
}

output "cluster_dashboard_url" {
  description = "URL to the GKE cluster dashboard"
  value       = "https://console.cloud.google.com/kubernetes/clusters/details/${google_container_cluster.devagent_poc.location}/${google_container_cluster.devagent_poc.name}/details?project=${var.project_id}"
}

# Deployment Commands
output "deployment_commands" {
  description = "Commands to deploy DevAgent to this cluster"
  value = {
    set_project     = "export PROJECT_ID=${var.project_id}"
    set_cluster     = "export CLUSTER_NAME=${google_container_cluster.devagent_poc.name}"
    set_region      = "export REGION=${google_container_cluster.devagent_poc.location}"
    get_credentials = "gcloud container clusters get-credentials ${google_container_cluster.devagent_poc.name} --region=${google_container_cluster.devagent_poc.location} --project=${var.project_id}"
    deploy_devagent = "./scripts/deploy.sh"
    check_health    = "./scripts/health-check.sh"
  }
}

# Resource Tags and Labels
output "cluster_labels" {
  description = "Labels applied to the cluster"
  value       = google_container_cluster.devagent_poc.resource_labels
}

# Cost Information
output "cluster_cost_allocation_enabled" {
  description = "Whether cost allocation is enabled"
  value       = google_container_cluster.devagent_poc.cost_management_config.0.enabled
}

output "resource_usage_export_enabled" {
  description = "Whether resource usage export is enabled"
  value       = google_container_cluster.devagent_poc.resource_usage_export_config != null
}

# Maintenance Information
output "maintenance_window" {
  description = "Maintenance window configuration"
  value = {
    start_time  = var.maintenance_start_time
    end_time    = var.maintenance_end_time
    recurrence  = var.maintenance_recurrence
  }
}

# Security Configuration Summary
output "security_configuration" {
  description = "Summary of security configuration"
  value = {
    network_policy_enabled      = google_container_cluster.devagent_poc.network_policy.0.enabled
    private_nodes_enabled       = google_container_cluster.devagent_poc.private_cluster_config.0.enable_private_nodes
    workload_identity_enabled   = google_container_cluster.devagent_poc.workload_identity_config != null
    database_encryption_enabled = var.database_encryption_enabled
    binary_authorization_mode   = google_container_cluster.devagent_poc.binary_authorization.0.evaluation_mode
    cloud_armor_enabled         = var.enable_cloud_armor
  }
}

# Quick Start Guide
output "quick_start_guide" {
  description = "Quick start guide for using this cluster"
  value = <<-EOT
    Night 68: DevAgent K8s POC Quick Start
    =====================================
    
    1. Connect to cluster:
       ${format("gcloud container clusters get-credentials %s --region=%s --project=%s", google_container_cluster.devagent_poc.name, google_container_cluster.devagent_poc.location, var.project_id)}
    
    2. Verify cluster:
       kubectl cluster-info
       kubectl get nodes
    
    3. Deploy DevAgent:
       cd agents/dev/k8s-poc/
       ./scripts/deploy.sh
    
    4. Check deployment:
       ./scripts/health-check.sh
    
    5. Access DevAgent:
       kubectl port-forward -n devagent-poc service/devagent 8083:8083
       curl http://localhost:8083/health
    
    6. View logs:
       kubectl logs -f deployment/devagent -n devagent-poc
    
    7. Cleanup:
       ./scripts/cleanup.sh
       terraform destroy
    
    Dashboard: ${format("https://console.cloud.google.com/kubernetes/clusters/details/%s/%s/details?project=%s", google_container_cluster.devagent_poc.location, google_container_cluster.devagent_poc.name, var.project_id)}
  EOT
} 