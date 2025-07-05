Night 9 — GitHub OIDC ⇄ GCP Workload Identity ≈ 90 min

Goal: Let GitHub Actions obtain short-lived, key-less GCP creds via OpenID Connect.
From now on your CI/CD jobs can run gcloud, deploy to Cloud Run, push to Artifact Registry—without JSON key files.

⸻

Step-by-Step

#	Command / Action	Why / Result
1	cd saas-factory-infra/infra/envs/prod	Work in prod env.
2	variables.tf → append:	Centralise IDs.
	hcl\nvariable \"workload_pool_id\"        { type = string default = \"gh-pool\" }\nvariable \"github_repo\"            { type = string }   # e.g. \"your-org/saas-factory\"\n	
3	terraform.tfvars — add real repo path:	
	hcl\ngithub_repo = \"your-org/saas-factory\"\n	
4	identity.tf — new file:	Creates pool + provider.
	hcl\n# Workload Identity Pool\nresource \"google_iam_workload_identity_pool\" \"gh_pool\" {\n  provider = google-beta\n  workload_identity_pool_id = var.workload_pool_id\n  display_name               = \"GitHub Pool\"\n}\n\n# OIDC Provider for GitHub\nresource \"google_iam_workload_identity_pool_provider\" \"gh_provider\" {\n  provider                           = google-beta\n  workload_identity_pool_id         = google_iam_workload_identity_pool.gh_pool.workload_identity_pool_id\n  workload_identity_pool_provider_id = \"github\"\n  display_name                      = \"GitHub OIDC\"\n  oidc {\n    issuer_uri = \"https://token.actions.githubusercontent.com\"\n  }\n  attribute_mapping = {\n    \"google.subject\"               = \"assertion.sub\"\n    \"attribute.repository\"         = \"assertion.repository\"\n  }\n  attribute_condition = \"assertion.repository == \\\"${var.github_repo}\\\"\"\n}\n	
5	Service account for CI/CD:	IAM least privilege.
	hcl\nresource \"google_service_account\" \"gha_deployer\" {\n  account_id   = \"gha-deployer\"\n  display_name = \"GitHub Actions Deployer\"\n}\n\n# Allow OIDC principals to impersonate SA\nresource \"google_service_account_iam_member\" \"gha_impersonation\" {\n  service_account_id = google_service_account.gha_deployer.name\n  role               = \"roles/iam.workloadIdentityUser\"\n  member             = \"principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.gh_pool.name}/attribute.repository/${var.github_repo}\"\n}\n\n# Attach deploy-time roles\nresource \"google_project_iam_member\" \"gha_run\" {\n  project = var.project_id\n  role    = \"roles/run.admin\"            # Deploy Cloud Run\n  member  = \"serviceAccount:${google_service_account.gha_deployer.email}\"\n}\nresource \"google_project_iam_member\" \"gha_artifact\" {\n  project = var.project_id\n  role    = \"roles/artifactregistry.writer\"\n  member  = \"serviceAccount:${google_service_account.gha_deployer.email}\"\n}\nresource \"google_project_iam_member\" \"gha_sql\" {\n  project = var.project_id\n  role    = \"roles/cloudsql.client\"\n  member  = \"serviceAccount:${google_service_account.gha_deployer.email}\"\n}\n	
6	terraform init (with google-beta provider auto-added)	Pulls beta provider for identity pool.
7	terraform plan -out oidc.plan → terraform apply oidc.plan	Creates pool, provider, SA, bindings.
8	Grab IDs for GitHub:	Needed by workflow.
	bash\nexport WIF_PROVIDER=\"$(terraform output -raw gh_provider_name)\"   # long URI\nexport GCP_SA=\"$(terraform output -raw gha_deployer_email)\"\n	
9	GitHub → repo settings → Secrets & Variables > Actions	Add:GCP_PROJECT_ID = <your-project>WIF_PROVIDER   = $WIF_PROVIDERGCP_SA_EMAIL   = $GCP_SA
10	Deploy workflow .github/workflows/deploy.yml:	Uses OIDC creds.
	```yaml\nname: Deploy\non:\n  push:\n    branches: [ main ]\njobs:\n  deploy:\n    runs-on: ubuntu-latest\n    permissions:\n      id-token: write      # required for OIDC\n      contents: read\n    steps:\n      - uses: actions/checkout@v4\n      - id: auth\n        uses: google-github-actions/auth@v2\n        with:\n          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}\n          service_account:           ${{ secrets.GCP_SA_EMAIL }}\n      - uses: google-github-actions/setup-gcloud@v2\n      - run: gcloud run services list	head -n 5\n```
11	Commit & push:	Test auth works.
	bash\ngit add identity.tf .github/workflows/deploy.yml && \\\n  git commit -m \"Night 9 – GitHub OIDC federation\" && git push\n	
12	Verify in GitHub Actions UI → Deploy job prints Cloud Run service list w/o any JSON key.	Proves OIDC → SA impersonation is live.


⸻

Night 9 Deliverables
	•	Workload Identity Pool gh-pool and OIDC Provider bound only to your repo (assertion.repository == your-org/saas-factory).
	•	Service Account gha-deployer@… with roles:
	•	iam.workloadIdentityUser (impersonatable by GitHub)
	•	run.admin, artifactregistry.writer, cloudsql.client (deployment capabilities)
	•	GitHub repository configured with secrets/vars: GCP_PROJECT_ID, WIF_PROVIDER, GCP_SA_EMAIL.
	•	deploy.yml workflow authenticates via google-github-actions/auth@v2 and can run gcloud commands key-less.

CI/CD is now securely wired—ready for Night 10’s Cloud Build trigger that’ll auto-build and deploy your containers on each merge!
