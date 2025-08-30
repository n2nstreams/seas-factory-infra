resource "google_project_iam_member" "owner" {
  project = var.project_id
  role    = "roles/owner"
  member  = "user:${var.owner_email}"
}

# resource "google_project_iam_binding" "devops" {
#   project = var.project_id
#   role    = "roles/editor"
#   members = ["group:${var.devops_group}"]
# }

# resource "google_project_iam_binding" "viewer" {
#   project = var.project_id
#   role    = "roles/viewer"
#   members = ["group:${var.viewer_group}"]
# } 