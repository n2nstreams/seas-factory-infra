terraform {
  backend "gcs" {
    bucket = "tfstate-saas-factory-prod"
    prefix = "terraform/state"
  }
} 