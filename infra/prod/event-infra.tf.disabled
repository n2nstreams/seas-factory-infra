# Event Infrastructure for Live Dashboard
# Pub/Sub topic for agent events
resource "google_pubsub_topic" "agent_events" {
  name    = "agent-events"
  project = var.project_id
}

# Firestore Native mode database (if not yet created)
resource "google_firestore_database" "default" {
  name        = "(default)"
  location_id = "us-central1"
  type        = "FIRESTORE_NATIVE"
  project     = var.project_id
}

# IAM binding for Event Relay service account to access Firestore
resource "google_project_iam_member" "event_relay_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

# IAM binding for Event Relay service account to access Pub/Sub
resource "google_project_iam_member" "event_relay_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

# IAM binding for Orchestrator service account to publish to Pub/Sub
resource "google_project_iam_member" "orchestrator_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.orchestrator_sa.email}"
}

# Pub/Sub push subscription for Event Relay
resource "google_pubsub_subscription" "relay" {
  name    = "event-relay-push"
  topic   = google_pubsub_topic.agent_events.name
  project = var.project_id

  push_config {
    push_endpoint = google_cloud_run_v2_service.event_relay.uri
    oidc_token {
      service_account_email = google_service_account.run_sa.email
    }
  }

  depends_on = [
    google_cloud_run_v2_service.event_relay,
    google_pubsub_topic.agent_events
  ]
} 