Night 6 — Cloud SQL for Postgres + pgvector ≈ 90 min

Goal: Provision a private-IP Cloud SQL Postgres 15 instance in the same VPC, then enable the pgvector extension so agents can store embeddings.

⸻

Prerequisites
	•	VPC vpc-saas-factory exists with private-service-access automatically set up by the network module (needed for private IP).
	•	Cloud SQL Admin API is enabled (gcloud services enable sqladmin.googleapis.com)—the module will do this on terraform apply, but enabling early removes a wait.

⸻

Step-by-Step

#	Command / Action	Why / Result
1	cd saas-factory-infra/infra/envs/prod	Work in prod env.
2	variables.tf → append DB vars:	Keeps secrets out of code.
	hcl<br>variable \"db_name\"        { type = string default = \"factorydb\" }\nvariable \"db_user\"        { type = string default = \"factoryadmin\" }\nvariable \"db_password\"    { type = string sensitive = true }\n	
3	terraform.tfvars — add password:	Use a strong one; later you’ll rotate via Secret Manager.
	hcl\n# …existing vars…\ndb_password = \"changeMe-9viY2!\"\n	
4	sql.tf — new file for Cloud SQL module:	Uses official module for best practices.
	hcl\nmodule \"cloudsql_postgres\" {\n  source  = \"terraform-google-modules/sql-db/google//modules/postgresql\"\n  version = \"~> 13.0\"\n\n  project_id  = var.project_id\n  name        = \"psql-saas-factory\"\n  region      = var.region\n  tier        = \"db-custom-1-3840\"          # 1 vCPU / 3.75 GB RAM\n  disk_size   = 20                           # GB SSD\n  disk_autoresize = true\n\n  database_version = \"POSTGRES_15\"\n\n  # Private IP in our VPC\n  network           = module.network_base.network_self_link\n  ip_configuration  = {\n    ipv4_enabled    = false\n    private_network = module.network_base.network_self_link\n  }\n\n  # Auth & users\n  user_name     = var.db_user\n  user_password = var.db_password\n\n  # Flags (pgvector preloaded)\n  database_flags = [\n    {\n      name  = \"shared_preload_libraries\"\n      value = \"pgvector\"\n    }\n  ]\n}\n\n# create the logical DB\nresource \"google_sql_database\" \"factorydb\" {\n  name     = var.db_name\n  instance = module.cloudsql_postgres.instance_name\n}\n	• Private-IP only (no public IP).• shared_preload_libraries loads pgvector at startup.
5	terraform init	Downloads module + provider updates.
6	terraform plan -out sql.plan	Should show ≈ 8 resources (instance, db, IAM, connection).
7	Review plan → confirm tier & region are okay; monthly cost ~$35 (can downsize later).	
8	terraform apply sql.plan	Instance creation ≈ 3-5 min.
9	Create pgvector extension (one-time SQL):	Module can’t enable per-DB extension, so do it manually once.
	bash\n# Install Cloud SQL Auth Proxy if you haven’t\nbrew install cloud-sql-proxy   # or curl download\n\n# In another terminal start the proxy\ncloud-sql-proxy $(terraform output -raw cloudsql_postgres_instance_connection_name) \\\n               --private-ip \\\n               --port 5432 &\n\n# Connect and enable pgvector\nPGPASSWORD=\"$(terraform output -raw cloudsql_postgres_password)\" \\\npsql -h localhost -U $(terraform output -raw cloudsql_postgres_user) -d factorydb -c \"CREATE EXTENSION IF NOT EXISTS vector;\"\n	vector is the extension name for pgvector ≥ 0.5.
10	Verify: \dx inside psql should list vector.	
11	git add sql.tf variables.tf terraform.tfvars && git commit -m "Night 6 – Cloud SQL Postgres (private IP) with pgvector"git push origin main	Persist code & state.


⸻

Night 6 Deliverables
	1.	Cloud SQL instance psql-saas-factory (Postgres 15) in us-central1 using private IP only.
	2.	Database factorydb created with pgvector extension enabled.
	3.	Outputs you’ll reuse later:
	•	instance_connection_name
	•	private_ip_address
	4.	Terraform code (sql.tf, updated vars) committed and remote state updated.
