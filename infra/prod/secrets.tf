# OpenAI API Key Secret Management
resource "google_secret_manager_secret" "openai_key" {
  secret_id = "openai-api-key"
  
  replication {
    automatic = true
  }
  
  labels = {
    environment = "production"
    purpose     = "llm-provider"
    created_by  = "terraform"
  }
}

resource "google_secret_manager_secret_version" "openai_key_v1" {
  secret      = google_secret_manager_secret.openai_key.id
  secret_data = var.openai_api_key
}

# Grant orchestrator service account access to the secret
resource "google_secret_manager_secret_iam_member" "orchestrator_openai_reader" {
  secret_id = google_secret_manager_secret.openai_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.orchestrator_sa.email}"
}

# Optional: Grant Cloud Run service account access if different from orchestrator SA
resource "google_secret_manager_secret_iam_member" "cloud_run_openai_reader" {
  count     = var.use_separate_cloud_run_sa ? 1 : 0
  secret_id = google_secret_manager_secret.openai_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run_sa[0].email}"
} 