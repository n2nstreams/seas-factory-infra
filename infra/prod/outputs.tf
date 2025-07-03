output "cloudsql_postgres_instance_connection_name" {
  description = "The connection name of the Cloud SQL instance."
  value       = module.cloudsql_postgres.instance_connection_name
}

output "cloudsql_postgres_user" {
  description = "The name of the default user."
  value       = var.db_user
}

output "cloudsql_postgres_password" {
  description = "The password for the default user."
  value       = var.db_password
  sensitive   = true
} 