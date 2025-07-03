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