# Night 66: Tenant Isolation CLI

## Overview

The tenant isolation CLI enables promoting tenants from shared infrastructure to dedicated isolated resources. This includes creating dedicated databases and optionally deploying isolated Cloud Run services.

## Features

- **Database Isolation**: Creates dedicated PostgreSQL database for tenant data
- **Cloud Run Deployment**: Deploys isolated Cloud Run service with tenant-specific configuration
- **Data Migration**: Safely migrates tenant data from shared to isolated infrastructure
- **Routing Configuration**: Sets up load balancer routing for tenant-specific subdomains
- **Rollback Safety**: Preserves shared data during migration (optional cleanup)

## Quick Start

### Prerequisites

1. **Environment Setup**:
   ```bash
   # Copy and customize environment configuration
   cp config/environments/tenant-isolation.env.example config/environments/tenant-isolation.env
   
   # Edit the configuration
   vim config/environments/tenant-isolation.env
   
   # Load environment variables
   source config/environments/tenant-isolation.env
   ```

2. **Google Cloud Authentication**:
   ```bash
   # Authenticate with Google Cloud
   gcloud auth login
   
   # Set default project
   gcloud config set project $GOOGLE_CLOUD_PROJECT
   
   # Verify permissions
   gcloud projects get-iam-policy $GOOGLE_CLOUD_PROJECT
   ```

3. **Required Permissions**:
   - Cloud Run Admin (`roles/run.admin`)
   - Cloud SQL Admin (`roles/cloudsql.admin`)
   - Service Account User (`roles/iam.serviceAccountUser`)

### Basic Usage

#### Promote Tenant (Full Isolation)

Promotes a tenant to both isolated database and Cloud Run service:

```bash
# Interactive promotion with confirmation
make isolate TENANT_ID=acme-corp

# Skip confirmation in scripts
python3 scripts/tenant_isolation.py promote --tenant-slug=acme-corp --confirm
```

#### Database-Only Isolation

Promotes tenant to isolated database without deploying Cloud Run:

```bash
# Database isolation only
make isolate-db-only TENANT_ID=acme-corp

# Via direct script
python3 scripts/tenant_isolation.py promote --tenant-slug=acme-corp --confirm --no-cloud-run
```

#### Check Tenant Status

View current isolation status of a tenant:

```bash
# Check isolation status
make tenant-status TENANT_ID=acme-corp

# Detailed JSON output
python3 scripts/tenant_isolation.py status --tenant-slug=acme-corp
```

## Advanced Usage

### Command Options

#### Makefile Options

```bash
# Keep data in shared database (don't cleanup)
make isolate TENANT_ID=acme-corp KEEP_SHARED_DATA=true

# Skip Cloud Run deployment  
make isolate TENANT_ID=acme-corp SKIP_CLOUD_RUN=true

# Combine options
make isolate TENANT_ID=acme-corp KEEP_SHARED_DATA=true SKIP_CLOUD_RUN=true
```

#### Direct Script Options

```bash
# Full options example
python3 scripts/tenant_isolation.py promote \
  --tenant-slug=acme-corp \
  --confirm \
  --keep-shared-data \
  --no-cloud-run
```

### Environment Variables

Key environment variables for customization:

```bash
# Cloud configuration
export GOOGLE_CLOUD_PROJECT=your-project-id
export CLOUD_RUN_REGION=us-central1
export CONTAINER_IMAGE=your-registry/api:latest

# Database configuration  
export DB_HOST=your-db-host
export DB_NAME=your-database
export DB_USER=your-user
export DB_PASSWORD=your-password
```

## What Happens During Isolation

### Step-by-Step Process

1. **Validation**: Verify tenant exists and is not already isolated
2. **Database Creation**: Create new database `tenant_<slug>`
3. **Schema Cloning**: Copy database schema to isolated instance
4. **Data Migration**: Migrate tenant-specific data safely
5. **Cloud Run Deployment**: Deploy isolated service (if enabled)
6. **Health Verification**: Verify deployment is healthy
7. **Routing Setup**: Configure load balancer routing
8. **Status Update**: Mark tenant as isolated in database
9. **Cleanup**: Remove data from shared database (optional)

### Created Resources

After successful isolation:

```
tenant_acme_corp (Database)
├── All migrated tenant data
├── Row-level security policies
└── Isolated user permissions

api-acme-corp (Cloud Run Service)
├── Service URL: https://api-acme-corp-PROJECT.REGION.run.app
├── Environment: TENANT_ID=acme-corp, ISOLATION_MODE=isolated
├── Database: Connected to tenant_acme_corp
└── Scaling: 0-10 instances

config/routing/acme-corp.json (Routing Config)
├── Database connection details
├── Cloud Run service information
└── Load balancer routing rules

config/load-balancer/acme-corp.json (LB Config)
├── Subdomain: app-acme-corp
├── Backend service mapping
└── SSL certificate requirements
```

## Monitoring and Verification

### Health Checks

The CLI performs several health checks:

```bash
# Database connectivity
psql "postgresql://user:pass@host:5432/tenant_acme_corp" -c "SELECT 1;"

# Cloud Run service health
curl https://api-acme-corp-PROJECT.REGION.run.app/health

# Data integrity verification
python3 scripts/tenant_isolation.py status --tenant-slug=acme-corp
```

### Logs and Monitoring

```bash
# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=api-acme-corp" --limit=50

# Database connection monitoring
gcloud sql operations list --instance=INSTANCE_NAME --filter="operationType=IMPORT"
```

## Troubleshooting

### Common Issues

#### 1. gcloud CLI Not Found
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

#### 2. Insufficient Permissions
```bash
# Check current permissions
gcloud projects get-iam-policy $GOOGLE_CLOUD_PROJECT --flatten="bindings[].members" --filter="bindings.members:user:$(gcloud config get-value account)"

# Grant necessary roles
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
  --member="user:your-email@domain.com" \
  --role="roles/run.admin"
```

#### 3. VPC Connector Issues
```bash
# Verify VPC connector exists
gcloud compute networks vpc-access connectors list --region=$CLOUD_RUN_REGION

# Create if missing (refer to infrastructure setup)
```

#### 4. Container Image Not Found
```bash
# Verify image exists
gcloud container images list --repository=$CONTAINER_IMAGE

# Build and push if needed
cd api_gateway && docker build -t $CONTAINER_IMAGE .
docker push $CONTAINER_IMAGE
```

### Recovery Procedures

#### Rollback Failed Isolation

If isolation fails partway through:

```bash
# 1. Check what was created
make tenant-status TENANT_ID=acme-corp

# 2. Manual cleanup if needed
# Delete Cloud Run service
gcloud run services delete api-acme-corp --region=$CLOUD_RUN_REGION

# Drop isolated database
psql -h $DB_HOST -U $DB_USER -c "DROP DATABASE IF EXISTS tenant_acme_corp;"

# Reset tenant status in shared database
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "UPDATE tenants SET isolation_mode='shared' WHERE slug='acme-corp';"
```

## Security Considerations

- **Credentials**: Environment variables contain sensitive database passwords
- **Network**: Cloud Run services use VPC connectors for database access
- **Access Control**: Each isolated tenant gets dedicated database user
- **Audit Trail**: All isolation operations are logged with timestamps

## Performance Impact

- **Database**: Each isolated database has its own connection pool
- **Cloud Run**: Independent scaling and resource allocation per tenant
- **Cost**: Linear cost increase per isolated tenant
- **Monitoring**: Separate metrics and alerting per isolated service

## Integration with Factory Pipeline

Isolated tenants maintain full factory functionality:

- **Agent Communication**: Uses tenant-specific database and routing
- **Event Processing**: Isolated event streams and processing
- **Monitoring**: Dedicated dashboards and alerting
- **Billing**: Accurate cost attribution per tenant

## Next Steps

After implementing Night 66:

- **Night 67**: Secrets rotation automation
- **Night 68**: Kubernetes migration path
- **Night 69**: Load testing isolated infrastructure
- **Night 70**: Multi-region failover testing 