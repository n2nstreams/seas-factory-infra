variable "project_id" {
  description = "The GCP project ID."
  type        = string
  default     = "summer-nexus-463503-e1"
}

variable "region" {
  description = "The GCP region for resources."
  type        = string
  default     = "us-central1"
}

variable "owner_email" {
  description = "The email address of the project owner."
  type        = string
}

variable "devops_group" {
  description = "The email address of the DevOps Google Group."
  type        = string
}

variable "viewer_group" {
  description = "The email address of the Viewer Google Group."
  type        = string
}

variable "db_name" {
  description = "The name of the main database."
  type        = string
  default     = "factorydb"
}

variable "db_user" {
  description = "The default user for the database."
  type        = string
  default     = "factoryadmin"
}

variable "db_password" {
  description = "The password for the default database user."
  type        = string
  sensitive   = true
}

variable "billing_account" {
  description = "The billing account ID for budget alerts."
  type        = string
}

variable "slack_webhook_token" {
  description = "The Slack webhook token for notifications."
  type        = string
  sensitive   = true
}

variable "workload_pool_id" {
  description = "The workload identity pool ID for GitHub Actions"
  type        = string
  default     = "gh-pool"
}

variable "github_repo" {
  description = "The GitHub repository in the format 'owner/repo'"
  type        = string
}

variable "openai_api_key" {
  description = "The OpenAI API key for GPT-4o model access"
  type        = string
  sensitive   = true
}

variable "use_separate_cloud_run_sa" {
  description = "Whether to use a separate service account for Cloud Run"
  type        = bool
  default     = false
}

variable "orchestrator_vertex_endpoint" {
  description = "The Vertex AI Agent Engine endpoint URL for the Project Orchestrator"
  type        = string
}

# Custom domain configuration
variable "domain_name" {
  description = "The custom domain name for the SaaS Factory (e.g., forge95.com)"
  type        = string
  default     = "forge95.com"
}

variable "api_subdomain" {
  description = "The subdomain for API services"
  type        = string
  default     = "api"
}

variable "www_subdomain" {
  description = "The subdomain for the frontend web application"
  type        = string
  default     = "www"
} 