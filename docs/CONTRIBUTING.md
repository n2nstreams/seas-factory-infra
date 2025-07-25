# Contributing to AI SaaS Factory

## 🎯 **Overview**

Welcome to the AI SaaS Factory project! This guide will help you contribute effectively to our **multi-agent AI automation platform** that transforms ideas into fully-deployed SaaS applications.

The SaaS Factory follows a **masterplan-driven development approach** with clear nightly milestones (Night 1-84) and uses a sophisticated **multi-agent architecture** powered by OpenAI GPT-4o and Google Gemini 2.5 Pro.

---

## 🏗️ **Project Architecture**

### Core Components

```
saas-factory/
├── infra/                 # Terraform & IaC modules
├── orchestrator/          # ADK Project Orchestrator agent  
├── agents/                # Worker agents (idea, design, code, qa, ops, etc.)
│   ├── dev/              # DevAgent - Code generation
│   ├── qa/               # ReviewAgent - Testing & QA
│   ├── design/           # DesignAgent - UI/UX generation
│   ├── ops/              # AIOpsAgent & DevOpsAgent - Infrastructure
│   ├── docs/             # DocAgent - Documentation generation
│   └── shared/           # Shared utilities and components
├── ui/                   # React dashboard + marketplace
├── api-gateway/          # FastAPI gateway with tenant routing
└── docs/                 # Generated & manual documentation
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Python 3.12, FastAPI, PostgreSQL | Agent services & API |
| **Frontend** | React 18, TypeScript, Tailwind CSS | Dashboard & marketplace |
| **AI/ML** | OpenAI GPT-4o, Google Gemini 2.5 Pro | Agent intelligence |
| **Cloud** | Google Cloud Platform | Infrastructure & deployment |
| **Database** | PostgreSQL 15 + pgvector | Multi-tenant data storage |
| **CI/CD** | GitHub Actions + Cloud Build | Automated deployment |
| **Orchestration** | Vertex AI Agent Engine + LangGraph | Multi-agent coordination |

---

## 🚀 **Development Setup**

### Prerequisites

1. **Python 3.12+** with pip and virtualenv
2. **Node.js 18+** with npm
3. **Docker** and Docker Compose
4. **gcloud CLI** (for GCP integration)
5. **terraform** (for infrastructure)
6. **Git** with SSH keys configured

### Initial Setup

```bash
# 1. Clone the repository
git clone git@github.com:your-org/saas-factory.git
cd saas-factory

# 2. Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-base.txt

# 3. Set up frontend dependencies
cd ui
npm install
cd ..

# 4. Start local development environment
make dev-up
```

### Environment Configuration

Create a `.env` file in the project root:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Google Cloud Configuration  
GOOGLE_CLOUD_PROJECT=your-gcp-project
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=factorydb
DB_USER=factory_user
DB_PASSWORD=your_secure_password

# Stripe Configuration (for billing agent)
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# GitHub Integration (for DevAgent)
GITHUB_TOKEN=ghp_your_github_token
GITHUB_REPO_OWNER=your-github-username
GITHUB_REPO_NAME=your-repo-name
```

### Local Development Commands

```bash
# Start all services in development mode
make dev-up

# Run specific agent locally
make run-agent AGENT=dev

# Run tests
make test

# Run linting and formatting
make lint
make format

# Build all Docker images
make build

# Clean up development environment
make dev-down
```

---

## 📋 **Coding Standards**

### Python Code Standards

We follow **PEP 8** with these specific guidelines:

#### 1. **Agent Structure Pattern**

All agents must follow this standardized structure:

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import shared components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from tenant_db import TenantDatabase, TenantContext, get_tenant_context_from_headers
from access_control import require_subscription, AccessLevel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentNameAgent:
    """
    Agent description following the Night X implementation
    """
    
    def __init__(self):
        # Initialize OpenAI client, database, etc.
        pass
    
    async def main_function(self, spec: BaseModel, tenant_context: TenantContext):
        """Main agent functionality"""
        try:
            # Implementation
            pass
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

# FastAPI setup
app = FastAPI(title="AgentName API", version="1.0.0")
agent = AgentNameAgent()

@app.post("/process")
@require_subscription(AccessLevel.STARTER)
async def process_request(
    spec: RequestModel,
    tenant_context: TenantContext = Depends(get_tenant_context_from_headers)
):
    return await agent.main_function(spec, tenant_context)
```

#### 2. **Naming Conventions**

- **Classes**: `PascalCase` (e.g., `DevAgent`, `TenantContext`)
- **Functions/Variables**: `snake_case` (e.g., `generate_code`, `tenant_id`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- **Private methods**: `_snake_case` (e.g., `_build_prompt`, `_validate_input`)

#### 3. **Error Handling**

```python
# Standard error handling pattern
try:
    result = await some_operation()
    logger.info(f"Operation completed successfully: {result.id}")
    return result
except ValidationError as e:
    logger.error(f"Validation error: {str(e)}")
    raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
except Exception as e:
    logger.error(f"Unexpected error in {operation_name}: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
```

#### 4. **Documentation Standards**

```python
async def generate_code(self, spec: ModuleSpec, tenant_context: TenantContext) -> GeneratedCode:
    """
    Generate code based on module specification
    
    Args:
        spec: Module specification with requirements and constraints
        tenant_context: Tenant context for multi-tenant isolation
        
    Returns:
        GeneratedCode: Generated code with metadata and validation results
        
    Raises:
        HTTPException: If generation fails or quota exceeded
        ValidationError: If specification is invalid
        
    Example:
        >>> spec = ModuleSpec(name="UserService", module_type="api")
        >>> result = await agent.generate_code(spec, tenant_context)
        >>> print(result.code)
    """
```

### React/TypeScript Standards

#### 1. **Component Structure**

```typescript
// components/ComponentName.tsx
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface ComponentNameProps {
  data: DataType;
  onAction: (id: string) => void;
  className?: string;
}

export const ComponentName: React.FC<ComponentNameProps> = ({
  data,
  onAction,
  className = ''
}) => {
  const [state, setState] = useState<StateType>(initialState);

  useEffect(() => {
    // Effect logic
  }, [dependency]);

  const handleAction = (id: string) => {
    // Handler logic
    onAction(id);
  };

  return (
    <Card className={`component-base-styles ${className}`}>
      <CardHeader>
        <CardTitle>{data.title}</CardTitle>
      </CardHeader>
      <CardContent>
        {/* Component content */}
      </CardContent>
    </Card>
  );
};
```

#### 2. **Styling Guidelines**

- Use **Tailwind CSS** for styling with the glassmorphism design theme
- Follow the **natural olive green** color palette: [[memory:2392994]]
- Use **shadcn/ui** components for consistency
- Implement responsive design with mobile-first approach

```typescript
// Example glassmorphism styling
const glassmorphismClasses = `
  bg-white/10 backdrop-blur-lg rounded-xl border border-white/20
  shadow-xl hover:bg-white/20 transition-all duration-200
  text-emerald-800 dark:text-emerald-100
`;
```

---

## ✅ **Testing Requirements**

### Test Structure

All code changes must include comprehensive tests. [[memory:3487784]]

#### 1. **Agent Testing Pattern**

```python
# tests/test_agent_name.py
import pytest
import asyncio
from unittest.mock import Mock, patch
from agents.agent_name.main import AgentNameAgent
from agents.shared.tenant_db import TenantContext

@pytest.fixture
def agent():
    return AgentNameAgent()

@pytest.fixture  
def tenant_context():
    return TenantContext(
        tenant_id="test-tenant",
        subscription_tier="STARTER",
        database_url="postgresql://test:test@localhost/test"
    )

class TestAgentName:
    @pytest.mark.asyncio
    async def test_main_function_success(self, agent, tenant_context):
        """Test successful execution of main function"""
        # Test implementation
        pass
    
    @pytest.mark.asyncio
    async def test_main_function_validation_error(self, agent, tenant_context):
        """Test validation error handling"""
        # Test implementation
        pass
    
    @pytest.mark.asyncio
    async def test_tenant_isolation(self, agent, tenant_context):
        """Test tenant isolation enforcement"""
        # Test implementation
        pass
```

#### 2. **Frontend Testing**

```typescript
// components/__tests__/ComponentName.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ComponentName } from '../ComponentName';

describe('ComponentName', () => {
  const mockProps = {
    data: { title: 'Test Title' },
    onAction: jest.fn()
  };

  test('renders correctly', () => {
    render(<ComponentName {...mockProps} />);
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });

  test('handles user interaction', () => {
    render(<ComponentName {...mockProps} />);
    fireEvent.click(screen.getByRole('button'));
    expect(mockProps.onAction).toHaveBeenCalled();
  });
});
```

#### 3. **Running Tests**

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_dev_agent.py -v

# Run tests with coverage
pytest --cov=agents tests/

# Run frontend tests
cd ui && npm test

# Run integration tests
pytest tests/integration/ -v
```

### Test Coverage Requirements

- **Unit tests**: Minimum 80% coverage for all agents
- **Integration tests**: Critical paths and agent interactions
- **End-to-end tests**: Complete user journeys (Night 56 implementation)

---

## 🔄 **Pull Request Process**

### 1. **Branch Naming Convention**

```bash
# Feature branches
feature/night-71-docagent-implementation
feature/ui-glassmorphism-theme

# Bugfix branches  
bugfix/tenant-isolation-leak
bugfix/stripe-webhook-validation

# Agent-specific branches
agent/dev-agent-function-calling
agent/qa-playwright-integration
```

### 2. **Commit Message Format**

```bash
# Format: [Night X] Component: Brief description
git commit -m "[Night 71] DocAgent: Implement AI-powered documentation generation"
git commit -m "[Bugfix] TenantDB: Fix row-level security policy"
git commit -m "[UI] Dashboard: Add glassmorphism design theme"
```

### 3. **Pull Request Template**

When creating a PR, include:

```markdown
## Night X Implementation: [Feature Name]

### 🎯 Objective
Brief description of what this PR accomplishes

### ✅ Changes Made
- [ ] Implemented core functionality
- [ ] Added comprehensive tests  
- [ ] Updated documentation
- [ ] Verified tenant isolation
- [ ] Tested with multiple agents

### 🧪 Testing
- Unit tests: [coverage %]
- Integration tests: [status]
- Manual testing: [scenarios tested]

### 📝 Documentation
- [ ] Code comments added
- [ ] API documentation updated
- [ ] README updated if needed

### 🔒 Security Considerations
- [ ] Tenant isolation verified
- [ ] Input validation added
- [ ] Access controls implemented

### 🎨 UI/UX (if applicable)
- [ ] Follows glassmorphism design theme
- [ ] Natural olive green color palette applied
- [ ] Responsive design tested
- [ ] Accessibility considerations

### 📋 Checklist
- [ ] Code follows project standards
- [ ] Tests pass locally
- [ ] No linting errors
- [ ] Database migrations included (if needed)
- [ ] Breaking changes documented
```

### 4. **Review Process**

1. **Automated Checks**: GitHub Actions run tests, linting, and security scans
2. **ReviewAgent Analysis**: AI-powered code review with quality scoring
3. **Human Review**: At least one maintainer review required
4. **Auto-merge**: PRs with passing tests and approval can be auto-merged (Night 38 implementation)

---

## 🤖 **Agent Development Guidelines**

### Creating a New Agent

1. **Follow the Night Pattern**: Each agent implements a specific "Night" from the masterplan
2. **Use Standard Structure**: Follow the agent template pattern
3. **Implement Multi-tenancy**: All agents must support tenant isolation
4. **Add Access Control**: Use `@require_subscription` decorators appropriately

### Agent Communication

Agents communicate through:

- **Database**: Shared PostgreSQL with tenant isolation
- **Pub/Sub**: Google Cloud Pub/Sub for async events
- **HTTP APIs**: Direct agent-to-agent communication
- **Orchestrator**: Central coordination through Vertex AI Agent Engine

### Agent Lifecycle

```python
# Standard agent lifecycle
class AgentTemplate:
    def __init__(self):
        # Initialize connections, load configs
        pass
    
    async def process(self, request, tenant_context):
        # 1. Validate input
        # 2. Check permissions
        # 3. Execute main logic
        # 4. Store results
        # 5. Notify other agents if needed
        pass
    
    async def cleanup(self):
        # Clean up resources
        pass
```

---

## 📚 **Documentation Standards**

### 1. **Code Documentation**

- **Docstrings**: All public methods must have comprehensive docstrings
- **Type hints**: Use strict typing for all function signatures
- **Comments**: Complex logic requires inline comments

### 2. **API Documentation**

FastAPI automatically generates OpenAPI documentation. Ensure:

- Clear endpoint descriptions
- Comprehensive request/response models
- Example requests and responses
- Error code documentation

### 3. **README Files**

Each agent should have a detailed README following this structure:

```markdown
# AgentName - Brief Description

## Features
[List of key features with checkboxes]

## Architecture  
[System diagram and component description]

## Night X Requirements ✅
[Masterplan requirements tracking]

## Quick Start
[Installation and usage instructions]

## API Reference
[Endpoint documentation]

## Testing
[How to run tests]

## Configuration
[Environment variables and settings]
```

---

## 🆘 **Getting Help**

### 1. **Documentation Resources**

- **Masterplan**: `masterplan.md` - Complete project roadmap
- **Architecture Docs**: `docs/` directory
- **Agent READMEs**: Individual agent documentation
- **API Documentation**: Auto-generated at `/docs` endpoints

### 2. **Communication Channels**

- **GitHub Issues**: Bug reports and feature requests  
- **GitHub Discussions**: Questions and community support
- **Code Reviews**: Pull request discussions
- **Documentation**: In-code comments and docstrings

### 3. **Development Support**

- **Local Setup Issues**: Check `dev/README.md`
- **Agent Development**: See agent template patterns
- **Infrastructure Questions**: Review `infra/` Terraform modules
- **UI/UX Guidelines**: Follow glassmorphism design patterns

### 4. **Troubleshooting Common Issues**

```bash
# Database connection issues
make dev-restart-db

# Agent communication failures  
docker-compose logs [service-name]

# Build failures
make clean && make build

# Test failures
pytest tests/ -v --tb=short
```

---

## 🔒 **Security Guidelines**

### 1. **Tenant Isolation**

- Always use `TenantContext` for database operations
- Implement Row Level Security (RLS) policies
- Validate tenant access in all endpoints
- Never expose cross-tenant data

### 2. **Input Validation**

- Use Pydantic models for all API inputs
- Sanitize user inputs for LLM prompts
- Validate file uploads and sizes
- Implement rate limiting

### 3. **Secrets Management**

- Store all secrets in Google Secret Manager
- Use environment variables for configuration
- Never commit API keys or credentials
- Rotate secrets regularly (Night 67 implementation)

### 4. **API Security**

- Implement proper authentication and authorization
- Use HTTPS for all external communications
- Validate webhook signatures (Stripe, GitHub)
- Monitor for unusual access patterns

---

## 🚀 **Deployment & Infrastructure**

### 1. **Cloud Deployment**

The project uses Google Cloud Platform with:

- **Cloud Run**: Containerized agent services
- **Cloud SQL**: PostgreSQL with pgvector
- **Vertex AI**: Agent Engine orchestration
- **Cloud Build**: CI/CD pipelines
- **Terraform**: Infrastructure as Code

### 2. **Multi-Region Strategy**

- Primary region: `us-central1`
- Failover region: `us-east1`  
- Blue-green deployments (Night 48 implementation)
- Automated rollback on errors (Night 47 implementation)

### 3. **Monitoring & Observability**

- **Cloud Logging**: Structured logging across all services
- **Cloud Monitoring**: Custom metrics and alerting
- **Error Reporting**: Automatic error aggregation
- **AIOpsAgent**: Intelligent anomaly detection (Night 46)

---

## 📈 **Performance Guidelines**

### 1. **Agent Performance**

- **Response Times**: Target < 30s for complex operations
- **Concurrency**: Support multiple tenant requests
- **Caching**: Implement Redis caching where appropriate
- **Rate Limiting**: Protect against abuse

### 2. **Database Optimization**

- Use proper indexing strategies
- Implement connection pooling
- Monitor query performance
- Regular maintenance tasks

### 3. **Frontend Performance**

- Code splitting for large components
- Lazy loading for non-critical features
- Image optimization
- Bundle size monitoring

---

## 🎯 **Contributing Workflow Summary**

1. **Choose a Night**: Pick an unimplemented night from the masterplan
2. **Create Branch**: Use proper naming convention
3. **Implement Feature**: Follow coding standards and patterns
4. **Write Tests**: Comprehensive test coverage required [[memory:3487784]]
5. **Update Documentation**: Keep docs current
6. **Submit PR**: Use the PR template
7. **Code Review**: Address feedback promptly
8. **Merge**: Auto-merge on approval

---

## 📄 **License & Legal**

This project is licensed under the MIT License. By contributing, you agree that your contributions will be licensed under the same license.

### Contributor License Agreement

All contributors must agree to:

- Grant necessary rights for code distribution
- Ensure original work or proper attribution
- Follow the project's code of conduct
- Respect intellectual property rights

---

**Generated by DocAgent** | AI SaaS Factory v1.0  
*Last updated: 2024-12-22* 