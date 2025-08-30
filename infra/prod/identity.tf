# Workload Identity Pool
resource "google_iam_workload_identity_pool" "gh_pool" {
  provider                  = google-beta
  workload_identity_pool_id = var.workload_pool_id
  display_name              = "GitHub Pool"
  description               = "Pool for GitHub Actions OIDC authentication"
  project                   = var.project_id
}

# OIDC Provider for GitHub
resource "google_iam_workload_identity_pool_provider" "gh_provider" {
  provider                           = google-beta
  workload_identity_pool_id          = google_iam_workload_identity_pool.gh_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "github"
  display_name                       = "GitHub OIDC"
  description                        = "OIDC provider for GitHub Actions"
  project                            = var.project_id
  
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
  
  attribute_mapping = {
    "google.subject"         = "assertion.sub"
    "attribute.repository"   = "assertion.repository"
    "attribute.actor"        = "assertion.actor"
    "attribute.ref"          = "assertion.ref"
  }
  
  attribute_condition = "assertion.repository == \"${var.github_repo}\""
}

# Service account for GitHub Actions deployment
resource "google_service_account" "gha_deployer" {
  account_id   = "gha-deployer"
  display_name = "GitHub Actions Deployer"
  description  = "Service account for GitHub Actions CI/CD deployments"
  project      = var.project_id
}

# Allow OIDC principals to impersonate the service account
resource "google_service_account_iam_member" "gha_impersonation" {
  service_account_id = google_service_account.gha_deployer.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.gh_pool.name}/attribute.repository/${var.github_repo}"
}

# Grant necessary permissions to the service account
resource "google_project_iam_member" "gha_run" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.gha_deployer.email}"
}

resource "google_project_iam_member" "gha_artifact" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.gha_deployer.email}"
}

resource "google_project_iam_member" "gha_sql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.gha_deployer.email}"
}

resource "google_project_iam_member" "gha_storage" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.gha_deployer.email}"
}

resource "google_project_iam_member" "gha_iam" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.gha_deployer.email}"
} 