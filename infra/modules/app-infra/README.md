# app-infra Terraform Module

This module provisions a Cloud Run service for SaaS Factory agents with database connectivity, IAM permissions, and optional load balancer integration.

## Features

- Deploys a Cloud Run service with configurable resources
- Creates a dedicated Cloud SQL user for the agent
- Configures VPC connectivity for private database access
- Sets up proper IAM permissions
- Optional Network Endpoint Group for load balancer integration
- Supports environment variables and secrets

## Usage

```hcl
module "idea_agent" {
  source = "./modules/app-infra"
  
  project_id               = var.project_id
  region                   = var.region
  service_name             = "idea-agent"
  container_image          = "${var.region}-docker.pkg.dev/${var.project_id}/saas-factory/idea-agent:latest"
  service_account_email    = google_service_account.run_sa.email
  cloud_sql_instance_name  = module.cloudsql_postgres.instance_name
  db_host                  = module.cloudsql_postgres.private_ip_address
  db_name                  = var.db_name
  db_user_name             = "idea_agent_user"
  vpc_connector_id         = google_vpc_access_connector.connector.id
  
  env_vars = {
    AGENT_TYPE = "idea"
    LOG_LEVEL  = "INFO"
  }
  
  secret_env_vars = {
    OPENAI_API_KEY = {
      secret_id = google_secret_manager_secret.openai_key.secret_id
      version   = "latest"
    }
  }
  
  cpu_limit     = "1"
  memory_limit  = "1Gi"
  max_instances = 5
  create_neg    = true
}
```

## Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| project_id | The GCP project ID | `string` | n/a | yes |
| region | The GCP region for resources | `string` | n/a | yes |
| service_name | Name of the Cloud Run service | `string` | n/a | yes |
| container_image | Container image for the Cloud Run service | `string` | n/a | yes |
| service_account_email | Email of the service account for the Cloud Run service | `string` | n/a | yes |
| cloud_sql_instance_name | Name of the Cloud SQL instance | `string` | n/a | yes |
| db_host | Database host IP address | `string` | n/a | yes |
| db_name | Database name | `string` | n/a | yes |
| db_user_name | Database user name for this agent | `string` | n/a | yes |
| vpc_connector_id | ID of the VPC connector for private database access | `string` | n/a | yes |
| container_port | Port that the container listens on | `number` | `8080` | no |
| cpu_limit | CPU limit for the container | `string` | `"1"` | no |
| memory_limit | Memory limit for the container | `string` | `"512Mi"` | no |
| min_instances | Minimum number of instances | `number` | `0` | no |
| max_instances | Maximum number of instances | `number` | `10` | no |
| env_vars | Environment variables for the container | `map(string)` | `{}` | no |
| secret_env_vars | Secret environment variables for the container | `map(object)` | `{}` | no |
| create_neg | Whether to create a Network Endpoint Group for load balancer | `bool` | `false` | no |

## Outputs

| Name | Description |
|------|-------------|
| service_url | The URL of the Cloud Run service |
| service_name | The name of the Cloud Run service |
| db_user_name | The database user name for this agent |
| db_user_password | The database user password for this agent |
| neg_id | The ID of the Network Endpoint Group (if created) |

## Requirements

- Terraform >= 1.0
- Google Cloud Provider >= 4.0
- Existing VPC network with Cloud SQL connectivity
- Existing Cloud SQL instance
- Service account with appropriate permissions 