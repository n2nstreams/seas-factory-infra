terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.85"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 4.85"
    }
  }
} 