# Night 64: License Scan Agent - OSS Review Toolkit Integration

## Overview

The **License Scan Agent** is a comprehensive solution for automated license compliance checking using the **OSS Review Toolkit (ORT)**. This implementation fulfills the Night 64 requirement from the AI SaaS Factory masterplan: **"License scan agent (OSS Review Toolkit) – fail pipeline on GPL."**

## Features

🔍 **OSS Review Toolkit (ORT) Integration**
- Full ORT CLI integration for comprehensive license scanning
- Support for multiple package managers (npm, pip, maven, gradle)
- Deep license detection with confidence scoring
- Configurable scanning rules and policies

🚨 **GPL License Detection & Pipeline Failure**
- Automatic detection of GPL, AGPL, and other copyleft licenses
- Configurable pipeline failure on GPL violations
- Risk-based license classification (Safe, Low, Medium, High, Critical)
- Detailed violation reporting with actionable recommendations

🏗️ **CI/CD Pipeline Integration**
- Cloud Build configuration for automated scanning
- Pipeline webhook notifications
- Artifact storage in Cloud Storage
- Integration with existing GitHub Actions workflows

🔐 **Multi-tenant Architecture**
- Row-level security for tenant isolation
- Custom license policies per tenant
- Comprehensive audit trails
- Scalable database schema design

📊 **Comprehensive Reporting**
- Detailed scan results with package-level information
- License risk assessment and recommendations
- Historical scan tracking and metrics
- Dashboard-ready data structures

## Architecture

```
License Scan Agent (Night 64)
├── OSS Review Toolkit (ORT) Engine
│   ├── Analyzer (dependency detection)
│   ├── Scanner (license detection)
│   ├── Evaluator (policy enforcement)
│   └── Reporter (result generation)
├── FastAPI REST API
│   ├── Scan endpoints
│   ├── Policy management
│   ├── Webhook handlers
│   └── Metrics collection
├── Cloud Build Integration
│   ├── ORT installation
│   ├── Multi-language support
│   ├── Pipeline decision logic
│   └── Result storage
└── Database Schema
    ├── Scan results storage
    ├── License violations tracking
    ├── Policy configuration
    └── Tenant isolation
```

## Quick Start

### 1. Prerequisites

- Python 3.12+
- Java 11+ (required for ORT)
- PostgreSQL database
- Google Cloud Platform account (for Cloud Build integration)

### 2. Installation

```bash
# Clone the repository
cd agents/qa

# Install Python dependencies
pip install -r requirements.txt

# Install OSS Review Toolkit (ORT)
# Download from: https://github.com/oss-review-toolkit/ort/releases
wget https://github.com/oss-review-toolkit/ort/releases/download/1.5.0/ort-1.5.0.tar.gz
tar -xzf ort-1.5.0.tar.gz
sudo mv ort-1.5.0 /opt/ort
sudo ln -s /opt/ort/bin/ort /usr/local/bin/ort

# Verify installation
ort --version
```

### 3. Database Setup

```bash
# Run the database migration
psql -d factorydb -f ../../dev/migrations/007_create_license_scan_results.sql
```

### 4. Configuration

```bash
# Set environment variables
export GOOGLE_CLOUD_PROJECT="your-project-id"
export DB_HOST="localhost"
export DB_NAME="factorydb"
export DB_USER="factoryadmin"
export DB_PASS="your-password"
export ORT_CLI_PATH="/usr/local/bin/ort"
export LICENSE_SCAN_RESULTS_BUCKET="license-scan-results"
```

### 5. Start the Agent

```bash
# Run the License Scan Agent
python license_main.py
```

The agent will be available at `http://localhost:8087`

## API Endpoints

### Core Scanning

#### `POST /scan`
Scan project dependencies for license compliance.

```json
{
  "project_id": "my-project",
  "repository_url": "https://github.com/user/repo.git",
  "branch": "main",
  "fail_on_gpl": true,
  "package_managers": ["npm", "pip"]
}
```

#### `POST /scan/async`
Start an asynchronous license scan.

#### `GET /scan/{scan_id}/status`
Get the status and results of a license scan.

### Pipeline Integration

#### `POST /pipeline/check`
Pipeline integration endpoint for CI/CD systems.

```bash
# Example CI/CD usage
curl -X POST "http://license-agent:8087/pipeline/check" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: my-tenant" \
  -d '{
    "project_id": "my-project",
    "repository_url": "https://github.com/user/repo.git",
    "branch": "main",
    "fail_build": true
  }'
```

### Policy Management

#### `GET /policy/default`
Get the default license policy.

#### `POST /scan/with-policy`
Scan with a custom license policy.

### Monitoring

#### `GET /health`
Health check endpoint.

#### `GET /metrics`
Get agent performance metrics.

## Cloud Build Integration

### 1. Create Cloud Build Trigger

```bash
# Create a Cloud Build trigger using the license scanning configuration
gcloud builds triggers create github \
  --repo-name="your-repo" \
  --repo-owner="your-org" \
  --branch-pattern="^main$" \
  --build-config="agents/qa/license-cloudbuild.yaml" \
  --substitutions="_PROJECT_NAME=my-project,_FAIL_ON_GPL=true"
```

### 2. Configure Substitution Variables

The Cloud Build configuration supports the following variables:

- `_PROJECT_NAME`: Project name for reporting
- `_PACKAGE_MANAGERS`: Comma-separated list of package managers (default: npm,pip,maven,gradle)
- `_ENABLE_SCANNER`: Enable deep license scanning (default: false)
- `_FAIL_ON_GPL`: Fail pipeline on GPL licenses (default: true)
- `_FAIL_ON_COPYLEFT`: Fail pipeline on any copyleft licenses (default: false)
- `_LICENSE_SCAN_RESULTS_BUCKET`: Cloud Storage bucket for results
- `_LICENSE_AGENT_URL`: URL for webhook notifications
- `_TENANT_ID`: Tenant ID for multi-tenant deployments

### 3. Pipeline Usage Example

```yaml
# .github/workflows/license-check.yml
name: License Compliance Check

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  license-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger License Scan
        run: |
          gcloud builds submit \
            --config=agents/qa/license-cloudbuild.yaml \
            --substitutions="_PROJECT_NAME=${{ github.repository }},_FAIL_ON_GPL=true" \
            .
```

## License Policies

### Default Policy

The agent comes with a sensible default license policy:

```json
{
  "allowed_licenses": [
    "MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause", 
    "ISC", "Unlicense", "CC0-1.0"
  ],
  "denied_licenses": [
    "GPL-2.0", "GPL-3.0", "AGPL-3.0", "GPL-2.0+", "GPL-3.0+"
  ],
  "gpl_policy": "deny",
  "copyleft_policy": "warn",
  "unknown_license_policy": "warn",
  "risk_threshold": "high"
}
```

### Custom Policies

You can create custom policies per tenant:

```python
custom_policy = LicensePolicy(
    allowed_licenses=["MIT", "Apache-2.0"],
    denied_licenses=["GPL-2.0", "GPL-3.0"],
    gpl_policy="deny",
    copyleft_policy="allow",
    unknown_license_policy="warn"
)
```

## Database Schema

The agent uses three main tables:

### `license_scan_results`
Stores high-level scan results and metadata.

### `license_violations`
Stores detailed information about specific license violations.

### `license_policies`
Stores custom license policies per tenant.

## Testing

### Run Unit Tests

```bash
# Run the comprehensive test suite
python -m pytest test_license_scan_agent.py -v

# Run with coverage
python -m pytest test_license_scan_agent.py --cov=license_scan_agent --cov-report=html
```

### Test GPL Detection

```python
# Example test for GPL detection
def test_gpl_detection():
    agent = LicenseScanAgent()
    
    # Should detect GPL
    assert agent._is_gpl_license("GPL-2.0") == True
    assert agent._is_gpl_license("GNU General Public License") == True
    
    # Should not detect as GPL
    assert agent._is_gpl_license("MIT") == False
    assert agent._is_gpl_license("Apache-2.0") == False
```

## Deployment

### Docker Deployment

```bash
# Build the container
docker build -f Dockerfile.license -t license-scan-agent .

# Run the container
docker run -p 8087:8087 \
  -e GOOGLE_CLOUD_PROJECT="your-project" \
  -e DB_HOST="your-db-host" \
  license-scan-agent
```

### Cloud Run Deployment

```bash
# Deploy to Cloud Run
gcloud run deploy license-scan-agent \
  --image=gcr.io/your-project/license-scan-agent \
  --platform=managed \
  --region=us-central1 \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=your-project"
```

## Monitoring and Metrics

### Key Metrics

The agent tracks the following metrics:

- `scans_completed`: Total number of scans performed
- `gpl_violations_found`: Number of GPL violations detected
- `pipelines_failed`: Number of pipelines that failed due to license violations
- `average_scan_time`: Average scan duration in seconds

### Alerts

Set up monitoring alerts for:

- High GPL violation rates
- Scan failures
- Long scan durations
- Agent availability

## Troubleshooting

### Common Issues

#### ORT Not Found
```bash
# Verify ORT installation
ort --version

# Check PATH
echo $PATH

# Reinstall if needed
sudo ln -sf /opt/ort/bin/ort /usr/local/bin/ort
```

#### Database Connection Issues
```bash
# Check database connectivity
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1;"

# Verify migration
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT * FROM license_scan_results LIMIT 1;"
```

#### Cloud Build Timeouts
- Increase timeout in `license-cloudbuild.yaml`
- Disable scanner phase for faster scans
- Use more powerful machine types

### Debug Mode

```bash
# Run with debug logging
export LOG_LEVEL=DEBUG
python license_main.py
```

## Night 64 Requirements Checklist

✅ **OSS Review Toolkit (ORT) Integration**
- Full ORT CLI integration with configurable paths
- Support for analyzer, scanner, and evaluator phases
- Comprehensive package manager support

✅ **GPL License Detection**
- Robust GPL pattern matching
- AGPL and GPL variant detection
- Configurable GPL policy enforcement

✅ **Pipeline Failure on GPL**
- Automatic pipeline failure when GPL detected
- Configurable failure policies
- Clear failure reasons and action items

✅ **Cloud Build Integration**
- Complete Cloud Build configuration
- Substitution variables for customization
- Artifact storage and webhook notifications

✅ **Multi-tenant Support**
- Row-level security for tenant isolation
- Custom policies per tenant
- Comprehensive audit trails

✅ **Comprehensive Testing**
- Unit tests for all core functionality
- Integration tests for full workflows
- Mocked tests for CI/CD environments

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is part of the AI SaaS Factory and follows the project's licensing terms.

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the test suite for examples
3. Open an issue with detailed information
4. Contact the development team

---

🎯 **Night 64 Complete**: License scan agent with OSS Review Toolkit integration successfully implemented with GPL detection and pipeline failure capabilities! 