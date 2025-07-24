# Individual Agent Services using the app-infra module

# Idea Validation Agent
module "idea_agent" {
  source = "../modules/app-infra"
  
  project_id               = var.project_id
  region                   = var.region
  service_name             = "idea-agent"
  container_image          = "${var.region}-docker.pkg.dev/${var.project_id}/saas-factory/lang-dummy:0.1"
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

# Design Agent
module "design_agent" {
  source = "../modules/app-infra"
  
  project_id               = var.project_id
  region                   = var.region
  service_name             = "design-agent"
  container_image          = "${var.region}-docker.pkg.dev/${var.project_id}/saas-factory/lang-dummy:0.1"
  service_account_email    = google_service_account.run_sa.email
  cloud_sql_instance_name  = module.cloudsql_postgres.instance_name
  db_host                  = module.cloudsql_postgres.private_ip_address
  db_name                  = var.db_name
  db_user_name             = "design_agent_user"
  vpc_connector_id         = google_vpc_access_connector.connector.id
  
  env_vars = {
    AGENT_TYPE = "design"
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

# Development Agent
module "dev_agent" {
  source = "../modules/app-infra"
  
  project_id               = var.project_id
  region                   = var.region
  service_name             = "dev-agent"
  container_image          = "${var.region}-docker.pkg.dev/${var.project_id}/saas-factory/lang-dummy:0.1"
  service_account_email    = google_service_account.run_sa.email
  cloud_sql_instance_name  = module.cloudsql_postgres.instance_name
  db_host                  = module.cloudsql_postgres.private_ip_address
  db_name                  = var.db_name
  db_user_name             = "dev_agent_user"
  vpc_connector_id         = google_vpc_access_connector.connector.id
  
  env_vars = {
    AGENT_TYPE = "dev"
    LOG_LEVEL  = "INFO"
  }
  
  secret_env_vars = {
    OPENAI_API_KEY = {
      secret_id = google_secret_manager_secret.openai_key.secret_id
      version   = "latest"
    }
  }
  
  cpu_limit     = "2"
  memory_limit  = "2Gi"
  max_instances = 10
  create_neg    = true
}

# QA Agent
module "qa_agent" {
  source = "../modules/app-infra"
  
  project_id               = var.project_id
  region                   = var.region
  service_name             = "qa-agent"
  container_image          = "${var.region}-docker.pkg.dev/${var.project_id}/saas-factory/lang-dummy:0.1"
  service_account_email    = google_service_account.run_sa.email
  cloud_sql_instance_name  = module.cloudsql_postgres.instance_name
  db_host                  = module.cloudsql_postgres.private_ip_address
  db_name                  = var.db_name
  db_user_name             = "qa_agent_user"
  vpc_connector_id         = google_vpc_access_connector.connector.id
  
  env_vars = {
    AGENT_TYPE = "qa"
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

# Operations Agent
module "ops_agent" {
  source = "../modules/app-infra"
  
  project_id               = var.project_id
  region                   = var.region
  service_name             = "ops-agent"
  container_image          = "${var.region}-docker.pkg.dev/${var.project_id}/saas-factory/lang-dummy:0.1"
  service_account_email    = google_service_account.run_sa.email
  cloud_sql_instance_name  = module.cloudsql_postgres.instance_name
  db_host                  = module.cloudsql_postgres.private_ip_address
  db_name                  = var.db_name
  db_user_name             = "ops_agent_user"
  vpc_connector_id         = google_vpc_access_connector.connector.id
  
  env_vars = {
    AGENT_TYPE = "ops"
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

# TechStack Agent
module "techstack_agent" {
  source = "../modules/app-infra"
  
  project_id               = var.project_id
  region                   = var.region
  service_name             = "techstack-agent"
  container_image          = "${var.region}-docker.pkg.dev/${var.project_id}/saas-factory/lang-dummy:0.1"
  service_account_email    = google_service_account.run_sa.email
  cloud_sql_instance_name  = module.cloudsql_postgres.instance_name
  db_host                  = module.cloudsql_postgres.private_ip_address
  db_name                  = var.db_name
  db_user_name             = "techstack_agent_user"
  vpc_connector_id         = google_vpc_access_connector.connector.id
  
  env_vars = {
    AGENT_TYPE = "techstack"
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

resource "google_cloud_scheduler_job" "marketing_drip_campaign" {
  name        = "marketing-drip-campaign"
  description = "Triggers the daily email drip campaign for inactive users."
  schedule    = "0 9 * * *" # Runs every day at 9:00 AM
  time_zone   = "UTC"

  http_target {
    http_method = "POST"
    uri         = "https://marketing-agent-your-project-id.a.run.app/trigger-drip" # Replace with your actual URL
    
    oidc_token {
      service_account_email = google_service_account.cloud_run_invoker.email
    }
  }

  attempt_deadline = "320s"
} 