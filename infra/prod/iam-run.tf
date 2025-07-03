# Cloud Run service account with least privilege
resource "google_service_account" "run_sa" {
  account_id   = "run-sa"
  display_name = "Cloud Run runtime"
  description  = "Service account for Cloud Run instances"
  project      = var.project_id
}

# Grant Cloud SQL client access to Cloud Run service account
resource "google_project_iam_member" "run_sa_sql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

# Grant logging permissions
resource "google_project_iam_member" "run_sa_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

# Grant monitoring permissions
resource "google_project_iam_member" "run_sa_monitoring" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
} 