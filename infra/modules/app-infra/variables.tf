variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
}

variable "service_name" {
  description = "Name of the Cloud Run service"
  type        = string
}

variable "container_image" {
  description = "Container image for the Cloud Run service"
  type        = string
}

variable "container_port" {
  description = "Port that the container listens on"
  type        = number
  default     = 8080
}

variable "service_account_email" {
  description = "Email of the service account for the Cloud Run service"
  type        = string
}

variable "cloud_sql_instance_name" {
  description = "Name of the Cloud SQL instance"
  type        = string
}

variable "db_host" {
  description = "Database host IP address"
  type        = string
}

variable "db_name" {
  description = "Database name"
  type        = string
}

variable "db_user_name" {
  description = "Database user name for this agent"
  type        = string
}

variable "vpc_connector_id" {
  description = "ID of the VPC connector for private database access"
  type        = string
}

variable "cpu_limit" {
  description = "CPU limit for the container"
  type        = string
  default     = "1"
}

variable "memory_limit" {
  description = "Memory limit for the container"
  type        = string
  default     = "512Mi"
}

variable "min_instances" {
  description = "Minimum number of instances"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of instances"
  type        = number
  default     = 10
}

variable "env_vars" {
  description = "Environment variables for the container"
  type        = map(string)
  default     = {}
}

variable "secret_env_vars" {
  description = "Secret environment variables for the container"
  type = map(object({
    secret_id = string
    version   = string
  }))
  default = {}
}

variable "create_neg" {
  description = "Whether to create a Network Endpoint Group for load balancer"
  type        = bool
  default     = false
} 