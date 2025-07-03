Night 7 — DevOps & AIOps Foundations  ≈ 3 h

Goal:
Automate the first production deployment path (Cloud Run → Cloud SQL), wrap it with monitoring + cost guardrails, and scaffold two “ops” agents (DevOpsAgent & AIOpsAgent) that will later manage roll-outs and log analysis.

⸻

Step-by-Step

#	Task / Command	Why / Result
0	cd saas-factory-infra/infra/envs/prod	Work in prod env.
1	Enable APIs once:	Needed resources.
	bash\ngcloud services enable run.googleapis.com compute.googleapis.com \\\n    clouddeploy.googleapis.com monitoring.googleapis.com \\\n    billingbudgets.googleapis.com pubsub.googleapis.com\n	
2	Service account for Cloud Run:	Least-privilege runtime ID.
	hcl\n# iam-run.tf\nresource \"google_service_account\" \"run_sa\" {\n  account_id   = \"run-sa\"\n  display_name = \"Cloud Run runtime\"\n}\n\nresource \"google_project_iam_member\" \"run_sa_sql\" {\n  project = var.project_id\n  role    = \"roles/cloudsql.client\"\n  member  = \"serviceAccount:${google_service_account.run_sa.email}\"\n}\n	
3	Cloud SQL user for app:	Separate from admin login.
	hcl\nresource \"google_sql_user\" \"app\" {\n  name     = \"appuser\"\n  instance = module.cloudsql_postgres.instance_name\n  password = random_password.appuser.result\n}\nresource \"random_password\" \"appuser\" {\n  length  = 16\n  special = true\n}\n	
4	Build & push a starter container (FastAPI “Hello”):	Gives Cloud Run something to deploy.
	bash\n# in repo root\ncd agents/dev/starter-api\ndocker build -t us-central1-docker.pkg.dev/$PROJECT_ID/saas-factory/api:0.1 .\ndocker push us-central1-docker.pkg.dev/$PROJECT_ID/saas-factory/api:0.1\n	(Create Artifact Registry repo first if prompted.)
5	cloud-run.tf — create the service in us-central1:	Private egress, talks to DB.
	hcl\nresource \"google_cloud_run_v2_service\" \"api_central\" {\n  name     = \"api-backend\"\n  location = var.region            # us-central1\n  ingress  = \"INGRESS_TRAFFIC_ALL\"\n  template {\n    service_account = google_service_account.run_sa.email\n    containers {\n      image = \"us-central1-docker.pkg.dev/${var.project_id}/saas-factory/api:0.1\"\n      env = [\n        { name = \"DB_HOST\",  value = module.cloudsql_postgres.private_ip_address },\n        { name = \"DB_USER\",  value = google_sql_user.app.name },\n        { name = \"DB_PASS\",  value = google_sql_user.app.password },\n        { name = \"DB_NAME\",  value = var.db_name }\n      ]\n    }\n    vpc_access {\n      connector = module.network_base.serverless_connector_name  # auto-created by network module\n    }\n  }\n}\noutput \"api_url\" { value = google_cloud_run_v2_service.api_central.uri }\n	
6	Multi-region (us-east1) clone	For future blue/green + higher SLA.
	Duplicate the resource above as api_east with location=\"us-east1\" and image tag 0.1.	
7	Global HTTP(S) Load Balancer w/ serverless NEGs:	Front door for both regions.
	Use the Google-maintained Cloud Run load-balancer module for brevity:module \"lb\" { source=\"GoogleCloudPlatform/cloud-run-lb/google\" version=\"~>2.0\" project_id=var.project_id domain=\"api.${var.project_id}.com\" backends=[google_cloud_run_v2_service.api_central.name, google_cloud_run_v2_service.api_east.name] }	Issues managed TLS cert + global IP.
8	terraform init && terraform plan -out app.planterraform apply app.plan	Deploy infra (5-8 min inc. cert).
9	Uptime check + Slack alert	Detect outages.
	hcl\nresource \"google_monitoring_uptime_check_config\" \"api\" {\n  display_name = \"API HTTPS\"\n  timeout      = \"10s\"\n  period       = \"60s\"\n  monitored_resource {\n    type = \"uptime_url\"\n    labels = {\n      project_id = var.project_id\n      host       = module.lb.lb_ip_address\n    }\n  }\n  http_check { port = 443 path=\"/health\" tls_config {}}  # ensure /health endpoint exists\n  content_matchers { content = \"OK\" matcher = \"CONTAINS_STRING\" }\n  notification_channels = [google_monitoring_notification_channel.slack.id]\n}\n\nresource \"google_monitoring_notification_channel\" \"slack\" {\n  display_name = \"Slack DevOps\"\n  type         = \"slack\"\n  labels = {\n    channel_name = \"#alerts\"\n  }\n  sensitive_labels = {\n    token = var.slack_webhook_token\n  }\n}\n	Slack Webhook token stored in Secret Manager & passed through terraform.tfvars.
10	Billing Budget + Pub/Sub → CostGuardAgent	Catch runaway spend.
	hcl\nresource \"google_billing_budget\" \"budget\" {\n  billing_account = var.billing_account\n  display_name    = \"Monthly Budget\"\n  amount { specified_amount { units = 200 } }  # $200 cap\n  threshold_rules { threshold_percent = 0.8 }   # 80 %\n  threshold_rules { threshold_percent = 1.0 }   # 100 %\n  pubsub_topic    = google_pubsub_topic.cost_guard.id\n}\n\nresource \"google_pubsub_topic\" \"cost_guard\" { name = \"cost-guard\" }\n	Later, CostGuardAgent (Cloud Run job) subscribes & emails you.
11	Skeleton DevOpsAgent / AIOpsAgent	Placeholders for future logic.
	bash\nmkdir -p agents/ops && touch agents/ops/devops_agent.py agents/ops/aiops_agent.py\n	Commit empty classes + README.
12	git add . && git commit -m \"Night 7 – Cloud Run + LB + monitoring + budget guards\" && git push	Lock in state.


⸻

Night 7 Deliverables
	•	Cloud Run “api-backend” deployed in us-central1 and us-east1.
	•	Global HTTPS Load Balancer (https://api.<PROJECT_ID>.com) fronting both regions, managed TLS.
	•	Private DB connectivity: service account with roles/cloudsql.client; env vars wired.
	•	Uptime Check hitting /health every 60 s + Slack alert channel.
	•	Billing Budget ($200) → Pub/Sub topic cost-guard for future CostGuardAgent.
	•	Place-holder DevOpsAgent & AIOpsAgent code stubs committed.
	•	Terraform state reflects ~30 new resources; repo pushed to GitHub.

Your SaaS factory now has a live, monitored API stack and guardrails—ready for code-gen agents to deploy real apps!
