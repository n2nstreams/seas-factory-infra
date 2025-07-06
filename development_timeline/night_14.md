Night 14 — Staging Build Artifacts to Cloud Storage  ≈ 2 h

Goal:
	1.	Create a staging bucket in GCS.
	2.	Extend the GitHub Actions pipeline so every push to any branch (or PR) uploads the compiled React dist/ directory to that bucket under a unique path (branch/commit-sha/).
	3.	Produce a signed URL (valid 7 days) and print it in the Action logs—useful for quick, no-deploy previews.

⸻

Step-by-Step

#	Action / Command	Why / Result
1	cd infra/envs/prod (or create staging env if you prefer)	Work in Terraform.
2	bucket.tf — add bucket resource	hcl\nresource \"google_storage_bucket\" \"ui_staging\" {\n  name          = \"ui-staging-builds-${var.project_id}\"\n  location      = \"US\"\n  uniform_bucket_level_access = true\n  lifecycle_rule {\n    condition { age = 14 }    # auto-delete after 14 days\n    action    { type = \"Delete\" }\n  }\n}\n
3	Grant write access to GitHub SA	hcl\nresource \"google_storage_bucket_iam_member\" \"ui_staging_writer\" {\n  bucket = google_storage_bucket.ui_staging.name\n  role   = \"roles/storage.objectAdmin\"\n  member = \"serviceAccount:${google_service_account.gha_deployer.email}\"\n}\n
4	terraform apply -target google_storage_bucket.ui_staging	Creates bucket in seconds.
5	GitHub Action Update — add new job (or step) in .github/workflows/deploy.yml before the Cloud Run deploy (so preview even for PRs):	```yaml\n  build-preview:\n    runs-on: ubuntu-latest\n    permissions:\n      id-token: write\n      contents: read\n    if: github.event_name == ‘pull_request’
6	Optional: Add PR comment bot	Use peter-evans/create-or-update-comment action to post the signed URL to the pull-request thread.
7	Commit & push	bash\ngit add infra bucket.tf .github/workflows/deploy.yml \\\n  && git commit -m \"Night 14 – staging build upload to GCS\" && git push\n
8	Test — open a new PR or push to a feature branch. Actions tab → build-preview job prints a signed URL. Click – you should see the React landing page served directly from Cloud Storage.	


⸻

Night 14 Deliverables ✅
	•	GCS bucket ui-staging-builds-<project> with 14-day auto-delete lifecycle.
	•	IAM binding allowing GitHub OIDC service-account to write objects.
	•	CI workflow that:
	•	Builds React dist/ in CI.
	•	gsutil rsync uploads build to bucket under branch/commit.
	•	Generates a 7-day signed URL and logs (or comments) it for quick preview.
	•	Pull-request reviewers (and novices) can now click a link to preview every UI change—no container build, no Cloud Run deploy needed.