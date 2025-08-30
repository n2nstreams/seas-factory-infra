# UI Staging Bucket for build artifacts
resource "google_storage_bucket" "ui_staging" {
  name     = "ui-staging-builds-${var.project_id}"
  location = "US"
  project  = var.project_id
  
  uniform_bucket_level_access = true
  
  # Auto-delete builds after 14 days to save costs
  lifecycle_rule {
    condition {
      age = 14
    }
    action {
      type = "Delete"
    }
  }
  
  # Enable versioning for better tracking
  versioning {
    enabled = true
  }
  
  # CORS configuration to allow web access
  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

# Grant write access to GitHub Actions service account
resource "google_storage_bucket_iam_member" "ui_staging_writer" {
  bucket = google_storage_bucket.ui_staging.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.gha_deployer.email}"
}

# Grant public read access for preview links
resource "google_storage_bucket_iam_member" "ui_staging_public_read" {
  bucket = google_storage_bucket.ui_staging.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
} 