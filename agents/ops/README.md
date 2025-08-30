# Operations Agents

This directory contains the DevOps and AIOps agents for the SaaS Factory platform.

## DevOps Agent (`devops_agent.py`)

The DevOps Agent handles automated deployment and infrastructure management with **LLM-powered Terraform diff review** capabilities.

### Features

#### ✅ Terraform Diff Review (Night 44)
- **LLM-Powered Analysis**: Uses GPT-4o to provide intelligent review of Terraform infrastructure changes
- **Security Assessment**: Automated detection of security vulnerabilities and misconfigurations
- **Best Practices Validation**: Checks for documentation, tagging, and infrastructure best practices
- **Cost Analysis**: Identifies potential cost implications of infrastructure changes
- **GitHub Integration**: Automatically posts comprehensive review comments to pull requests
- **Scoring System**: Provides 0-100 score based on security findings and best practices
- **Auto-Approval Logic**: Determines when changes are safe to auto-approve

#### 📊 Security Analysis
- **Critical Findings**: Detects high-risk configurations (e.g., 0.0.0.0/0 access, unencrypted connections)
- **Resource-Specific Patterns**: Tailored security checks for different GCP resources
- **Severity Levels**: Categorizes findings as Critical, High, Medium, or Low
- **Actionable Recommendations**: Provides specific guidance for fixing issues

#### 🔍 Supported Resources
- **Google SQL Database**: Connection security, backup configuration, version checks
- **Google Compute Engine**: Network security, IP forwarding, SSH access
- **Google Storage Buckets**: Access controls, encryption, public access prevention
- **Google Cloud Run**: Authentication, container security
- **And more**: Extensible pattern system for additional resources

#### 🚀 Deployment Operations (Existing)
- **Deployment Orchestration**: Automated deployment of services across multiple regions
- **Infrastructure Provisioning**: Dynamic scaling and resource management
- **CI/CD Pipeline Management**: Integration with build and deployment pipelines
- **Environment Management**: Configuration management across environments
- **Rollback Procedures**: Automated rollback capabilities with health checks

### Usage

#### Terraform Diff Review
```python
from agents.ops.devops_agent import DevOpsAgent, DeploymentConfig

# Initialize agent
config = DeploymentConfig(
    project_id="your-project-id",
    environment="production",
    version="1.0.0"
)
agent = DevOpsAgent(config)

# Review a Terraform diff
diff_content = """
+ resource "google_sql_database_instance" "main" {
+   name             = "main-instance"
+   database_version = "POSTGRES_13"
+   settings {
+     tier = "db-f1-micro"
+     ip_configuration {
+       authorized_networks {
+         value = "0.0.0.0/0"
+       }
+     }
+   }
+ }
"""

# Perform review (with optional GitHub PR integration)
review = await agent.review_terraform_diff(
    diff_content, 
    pr_number=123,  # Optional: for GitHub integration
    context={"environment": "production"}
)

print(f"Overall Score: {review.overall_score}/100")
print(f"Approved: {review.approved}")
print(f"Security Findings: {len(review.security_findings)}")
```

#### GitHub Integration
```python
# The agent automatically posts review comments to GitHub PRs
# Example output:
"""
## ✅ Terraform Diff Review

**Overall Score**: 🔴 45.0/100

### 🔒 Security Analysis
- 🚨 **CRITICAL**: SQL instance allows access from any IP
- ⚠️ **HIGH**: SQL instance has no backup configuration

### 📋 Best Practices
- ❌ Resource main lacks proper documentation
- ❌ Resource main missing labels/tags

### 💰 Cost Implications
- 💸 Creating google_sql_database_instance 'main': SQL instances have significant monthly costs

### 📝 Recommendations
- 💡 Restrict SQL instance network access to specific IP ranges
- 💡 Add backup configuration for data protection
- 💡 Implement proper resource tagging for cost tracking
"""
```

#### Traditional Deployment
```python
# Deploy a service
status = agent.deploy_service("api-backend", "1.0.0")
print(f"Deployment status: {status}")

# Check health
health_status = agent.check_deployment_health(status.deployment_id)
print(f"Health check: {health_status}")
```

### Configuration

#### Environment Variables
```bash
# Required for LLM review functionality
export OPENAI_API_KEY="your-openai-api-key"

# Required for GitHub integration
export GITHUB_TOKEN="your-github-token"
export GITHUB_REPOSITORY="owner/repo"

# Standard deployment configuration
export PROJECT_ID="your-project-id"
export ENVIRONMENT="production"
export MONITORING_ENABLED="true"
```

### Review Output Structure

```python
@dataclass
class TerraformReview:
    diff_id: str                          # Unique review identifier
    pr_number: Optional[int]              # GitHub PR number
    overall_score: float                  # 0-100 score
    security_findings: List[SecurityFinding]  # Security issues found
    best_practices_violations: List[str]  # Best practices violations
    cost_implications: List[str]          # Cost analysis
    recommendations: List[str]            # LLM recommendations
    approved: bool                        # Auto-approval decision
    reviewer_notes: str                   # LLM summary
    reviewed_at: datetime                 # Review timestamp
```

### Testing

Run comprehensive tests:
```bash
# Run all tests
pytest agents/ops/test_terraform_diff_review.py -v

# Run specific test categories
pytest agents/ops/test_terraform_diff_review.py::TestTerraformDiffReview::test_security_analysis_critical_findings -v

# Run with coverage
pytest agents/ops/test_terraform_diff_review.py --cov=agents.ops.devops_agent --cov-report=html
```

### Security Pattern Extension

Add new security patterns:
```python
# In DevOpsAgent._load_security_patterns()
"google_new_resource_type": {
    "critical": [
        {"pattern": r"dangerous_config_pattern", "message": "Description of issue"}
    ],
    "high": [
        {"pattern": r"risky_config_pattern", "message": "Description of issue"}
    ]
}
```

## AIOps Agent (`aiops_agent.py`)

The AIOps Agent provides AI-driven operations and monitoring capabilities.

### Features (Implemented)
- **Log Analysis**: Pattern recognition and anomaly detection in logs
- **Performance Monitoring**: Real-time performance metrics analysis
- **Predictive Scaling**: ML-based resource scaling predictions
- **Incident Response**: Automated incident detection and response
- **Root Cause Analysis**: AI-powered root cause identification

### Usage
```python
from agents.ops.aiops_agent import AIOpsAgent

agent = AIOpsAgent("your-project-id")
metrics = agent.monitor_performance("api-backend")
anomalies = agent.detect_anomalies(metrics)
```

## Integration with Infrastructure

Both agents are designed to integrate with the SaaS Factory infrastructure:

- **Cloud Run**: Deploy and manage containerized services
- **Cloud SQL**: Monitor database performance and connectivity
- **Cloud Monitoring**: Integrate with GCP monitoring and alerting
- **Cloud Load Balancing**: Manage traffic distribution
- **Pub/Sub**: Handle event-driven operations and notifications
- **GitHub Actions**: Trigger reviews on infrastructure PRs

## Future Enhancements

### DevOps Agent
1. **Multi-Cloud Support**: AWS and Azure Terraform review capabilities
2. **Custom Rule Engine**: User-defined security and compliance rules
3. **Integration Testing**: Automated testing of infrastructure changes
4. **Compliance Scanning**: SOC2, HIPAA, PCI-DSS compliance checks
5. **Cost Optimization**: AI-driven cost reduction recommendations

### AIOps Agent
1. **Machine Learning Models**: Train custom models for anomaly detection
2. **Correlation Analysis**: Cross-service impact analysis
3. **Predictive Analytics**: Forecast resource needs and potential issues
4. **Automated Remediation**: Self-healing infrastructure capabilities
5. **Cost Optimization**: AI-driven cost analysis and optimization

## Contributing

When extending these agents:

1. Follow the existing interface patterns
2. Add comprehensive error handling
3. Include logging for all operations
4. Write unit tests for new functionality
5. Update this README with new features
6. Consider security implications of new features

## Security Considerations

- All API keys are stored in environment variables
- GitHub tokens use minimal required permissions
- LLM prompts are sanitized to prevent injection attacks
- Review results are logged for audit trails
- Sensitive data is not included in review comments 