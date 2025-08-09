# Night 38: Auto-Commit Workflow Implementation

**DevAgent opens PR; ReviewAgent comments; Orchestrator merges on green**

## Overview

Night 38 completes the automated CI/CD pipeline by implementing a fully automated workflow where:

1. **DevAgent** generates code and automatically creates GitHub pull requests
2. **ReviewAgent** runs tests, analyzes code quality, and comments on pull requests
3. **Orchestrator** automatically merges pull requests when all checks pass

This creates a complete automated development pipeline that can generate, test, review, and deploy code with minimal human intervention.

## Architecture

```bash
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌──────────────┐
│  DevAgent   │───▶│   GitHub    │───▶│ ReviewAgent │───▶│ Orchestrator │
│             │    │     PR      │    │             │    │              │
│ - Generate  │    │ - Create PR │    │ - Run Tests │    │ - Check PR   │
│   Code      │    │ - Add Files │    │ - Quality   │    │ - Auto-Merge │
│ - Create PR │    │ - Add Labels│    │ - Comment   │    │ - Monitor    │
└─────────────┘    └─────────────┘    └─────────────┘    └──────────────┘
```

## Components Implemented

### 1. GitHub Integration Module (`agents/shared/github_integration.py`)

**Features:**

- ✅ Complete GitHub API integration
- ✅ PR creation and management
- ✅ Branch operations
- ✅ PR status checking and merging
- ✅ Comment management (general and inline)
- ✅ Auto-merge capabilities

**Key Classes:**

- `GitHubIntegration`: Main GitHub API client
- `PullRequestConfig`: PR configuration model
- `ReviewComment`: PR review comment model

### 2. Enhanced DevAgent (`agents/dev/main.py`)

**New Features:**

- ✅ GitHub integration initialization
- ✅ `create_github_pull_request()` method
- ✅ Auto-PR creation option in `/generate` endpoint
- ✅ `/create-pr` endpoint for manual PR creation
- ✅ Environment-based configuration

**Usage:**

```python
# Generate code with automatic PR creation
POST /generate?create_pr=true
{
  "module_spec": {
    "name": "UserService",
    "description": "User management service",
    "language": "python"
  }
}
```

### 3. Enhanced ReviewAgent (`agents/qa/review_agent.py`)

**New Features:**

- ✅ GitHub integration initialization
- ✅ `add_github_pr_comment()` method
- ✅ `add_inline_pr_comments()` method
- ✅ `/pr-comment` endpoint
- ✅ Comprehensive review comment generation
- ✅ Test result integration

**Features:**

- 🧪 Test execution and result parsing
- 📊 Quality score calculation
- 💬 Automated PR commenting
- 🔍 Issue analysis and suggestions
- 📈 Coverage reporting

### 4. Enhanced Orchestrator (`orchestrator/project_orchestrator.py`)

**New Features:**

- ✅ GitHub integration
- ✅ `GitHubMergeAgent` for PR management
- ✅ `check_pr_merge_status()` function
- ✅ `monitor_pr_for_auto_merge()` function
- ✅ `orchestrate_full_workflow()` function

**Capabilities:**

- 🔄 PR status monitoring
- ⚖️ Merge eligibility checking
- 🤖 Automated merging
- 🚀 Full workflow orchestration

### 5. GitHub Actions Workflow (`.github/workflows/auto-commit.yml`)

**Features:**

- ✅ Auto-generated PR detection
- ✅ Test execution
- ✅ ReviewAgent integration
- ✅ Auto-merge logic
- ✅ Status monitoring

**Triggers:**

- PR opened/updated
- PR review submitted
- Status checks completed

## Configuration

### Environment Variables

```bash
# GitHub Integration
GITHUB_TOKEN=your_github_token
GITHUB_REPOSITORY=owner/repo

# Agent URLs
DEV_AGENT_URL=http://dev-agent:8083
REVIEW_AGENT_URL=http://review-agent:8084

# Feature Flags
ENABLE_AUTO_COMMIT=true
ENABLE_AUTO_PR=true
ENABLE_AUTO_COMMENT=true

# Google Cloud (for ReviewAgent)
GOOGLE_CLOUD_PROJECT=your-project-id
CLOUD_BUILD_REGION=us-central1
```

### GitHub Repository Setup

1. **Create GitHub Token:**

   ```bash
   # Create a personal access token with these permissions:
   # - repo (full access)
   # - pull_requests (read/write)
   # - actions (read/write)
   ```

2. **Set Repository Secrets:**

   ```bash
   # Add these secrets to your repository:
   GITHUB_TOKEN=your_token_here
   ```

3. **Configure Branch Protection:**

   ```yaml
   # Enable branch protection on main branch
   # Require status checks to pass
   # Enable auto-merge for admin users
   ```

## Usage Examples

### 1. Basic Auto-Commit Workflow

```python
# 1. Generate code with auto-PR
import requests

response = requests.post(
    "http://dev-agent:8083/generate?create_pr=true",
    json={
        "module_spec": {
            "name": "PaymentService",
            "description": "Payment processing service",
            "language": "python",
            "framework": "fastapi"
        }
    }
)

# 2. PR is automatically created
pr_info = response.json()["github_pr"]
print(f"PR created: {pr_info['pr_url']}")

# 3. ReviewAgent automatically comments
# 4. Orchestrator merges when tests pass
```

### 2. Manual PR Creation

```python
# Create PR for existing generated code
requests.post(
    "http://dev-agent:8083/create-pr",
    json={
        "module_name": "UserService",
        "files": [
            {
                "filename": "user_service.py",
                "content": "# Generated code here...",
                "language": "python"
            }
        ]
    }
)
```

### 3. Review Agent PR Comments

```python
# Add review comment to PR
requests.post(
    "http://review-agent:8084/pr-comment",
    json={
        "pr_number": 123,
        "review_result": {
            "review_status": "passed",
            "feedback": {
                "code_quality_score": 85.5,
                "suggestions": ["Add error handling"]
            }
        }
    }
)
```

### 4. Orchestrator Auto-Merge

```python
# Check and merge PR
from orchestrator.project_orchestrator import check_pr_merge_status

result = check_pr_merge_status(123)
print(result)  # "✅ PR #123 merged successfully!"
```

## Complete Workflow Example

```python
#!/usr/bin/env python3
"""
Complete Night 38 workflow example
"""

import asyncio
import requests

async def run_auto_commit_workflow():
    # Step 1: DevAgent generates code and creates PR
    print("🚀 Starting auto-commit workflow...")
    
    dev_response = requests.post(
        "http://dev-agent:8083/generate?create_pr=true",
        json={
            "project_id": "my-project",
            "module_spec": {
                "name": "NotificationService",
                "description": "Service for sending notifications",
                "language": "python",
                "framework": "fastapi",
                "requirements": [
                    "Send email notifications",
                    "Handle SMS notifications",
                    "Queue management"
                ]
            }
        }
    )
    
    if dev_response.status_code == 200:
        result = dev_response.json()
        pr_info = result.get("github_pr")
        
        if pr_info:
            print(f"✅ PR #{pr_info['pr_number']} created")
            
            # Step 2: ReviewAgent automatically reviews and comments
            # (This happens automatically via GitHub webhooks)
            
            # Step 3: Orchestrator merges when ready
            # (This happens automatically when all checks pass)
            
            print("🔄 Auto-commit workflow in progress...")
            print(f"📋 Monitor PR: {pr_info['pr_url']}")
            
        else:
            print("❌ No PR created")
    else:
        print(f"❌ DevAgent failed: {dev_response.status_code}")

if __name__ == "__main__":
    asyncio.run(run_auto_commit_workflow())
```

## Demo Script

Run the comprehensive demo:

```bash
python examples/night-demos/night38_demo.py
```

This demonstrates:

- ✅ Complete workflow with successful merge
- ❌ Failure scenario with feedback loop
- 🔄 Retry mechanism simulation

## Testing

### Unit Tests

```bash
# Test GitHub integration
python -m pytest agents/shared/test_github_integration.py

# Test DevAgent PR creation
python -m pytest agents/dev/test_main.py::test_create_github_pull_request

# Test ReviewAgent PR comments
python -m pytest agents/qa/test_review_agent.py::test_add_github_pr_comment

# Test Orchestrator auto-merge
python -m pytest orchestrator/test_project_orchestrator.py::test_check_pr_merge_status
```

### Integration Tests

```bash
# Run complete workflow test
python -m pytest test_night38_integration.py

# Test with actual GitHub API (requires token)
GITHUB_TOKEN=your_token python -m pytest test_github_integration.py
```

## Monitoring and Observability

### Key Metrics

- **PR Creation Rate**: PRs created per hour
- **Review Success Rate**: Percentage of PRs passing review
- **Auto-Merge Rate**: Percentage of PRs auto-merged
- **Workflow Duration**: Time from code generation to merge
- **Failure Rate**: Percentage of failed workflows

### Logging

Each component logs structured events:

```python
{
    "timestamp": "2024-01-01T12:00:00Z",
    "agent": "DevAgent",
    "event": "pr_created",
    "pr_number": 123,
    "module_name": "UserService",
    "tenant_id": "tenant-123"
}
```

### Alerts

Set up alerts for:

- PR creation failures
- Review process failures
- Merge conflicts
- Test failures
- Security issues

## Security Considerations

### GitHub Token Security

```bash
# Use fine-grained personal access tokens
# Limit scope to specific repositories
# Rotate tokens regularly
# Store in secure secret management
```

### Code Review Security

```python
# Automated security scanning
# Dependency vulnerability checks
# Code quality gates
# Branch protection rules
```

## Production Deployment

### Prerequisites

1. **GitHub Repository Setup**
   - Branch protection enabled
   - Required status checks configured
   - Auto-merge permissions granted

2. **Agent Infrastructure**
   - DevAgent deployed and accessible
   - ReviewAgent with Cloud Build access
   - Orchestrator with GitHub permissions

3. **Environment Variables**
   - All required tokens and URLs configured
   - Feature flags set appropriately

### Deployment Steps

```bash
# 1. Deploy updated agents
kubectl apply -f agents/dev/deployment.yaml
kubectl apply -f agents/qa/deployment.yaml
kubectl apply -f orchestrator/deployment.yaml

# 2. Update GitHub secrets
gh secret set GITHUB_TOKEN --body "your_token"

# 3. Test the workflow
python examples/night-demos/night38_demo.py

# 4. Monitor metrics
kubectl logs -f deployment/dev-agent
kubectl logs -f deployment/review-agent
kubectl logs -f deployment/orchestrator
```

## Troubleshooting

### Common Issues

1. **PR Not Created**
   - Check `ENABLE_AUTO_PR` environment variable
   - Verify GitHub token permissions
   - Check DevAgent logs for errors

2. **Review Comments Missing**
   - Verify `ENABLE_AUTO_COMMENT` is true
   - Check ReviewAgent connectivity
   - Verify PR has correct labels

3. **Auto-Merge Not Working**
   - Check PR status checks
   - Verify branch protection settings
   - Check orchestrator permissions

### Debug Commands

```bash
# Check agent health
curl http://dev-agent:8083/health
curl http://review-agent:8084/health

# Test GitHub integration
python -c "from agents.shared.github_integration import create_github_integration; print(create_github_integration())"

# Monitor workflow
kubectl logs -f deployment/orchestrator | grep "auto-commit"
```

## Future Enhancements

### Planned Features

- 🔄 **Advanced Retry Logic**: Smarter retry mechanisms with exponential backoff
- 📊 **Enhanced Metrics**: Detailed workflow analytics and performance metrics
- 🔐 **Security Scanning**: Automated security vulnerability detection
- 🎯 **Smart Merging**: ML-based merge conflict resolution
- 📱 **Slack Integration**: Real-time notifications for workflow events

### Extensibility

The Night 38 implementation is designed for easy extension:

```python
# Add custom PR checks
class CustomPRChecker:
    async def check_pr_readiness(self, pr_number):
        # Custom logic here
        return {"ready": True, "reason": "Custom check passed"}

# Add custom review criteria
class CustomReviewCriteria:
    def analyze_code_quality(self, files):
        # Custom analysis logic
        return {"score": 95.0, "issues": []}

# Add custom merge strategies
class CustomMergeStrategy:
    async def merge_pr(self, pr_number, strategy="smart"):
        # Custom merge logic
        return {"merged": True, "strategy": strategy}
```

## Summary

Night 38 successfully implements the complete auto-commit workflow:

✅ **DevAgent** - Generates code and creates PRs automatically  
✅ **ReviewAgent** - Reviews code and adds comprehensive PR comments  
✅ **Orchestrator** - Monitors PRs and merges when all checks pass  
✅ **GitHub Integration** - Full GitHub API integration with all features  
✅ **Automated Testing** - Complete test execution and result analysis  
✅ **Monitoring** - Comprehensive logging and metrics  
✅ **Security** - Proper token management and permissions  

The AI SaaS Factory now has a complete automated development pipeline that can generate, test, review, and deploy code with minimal human intervention, fulfilling the Night 38 masterplan requirements.

**🎉 Night 38 Implementation Complete!**
