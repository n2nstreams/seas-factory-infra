# ReviewAgent - Intelligent Code Review with Cloud Build Integration

The ReviewAgent is a sophisticated AI-powered code review agent that **runs Pytest in Cloud Build** and **loops back to DevAgent** on test failures. This is the **Night 37** implementation from the AI SaaS Factory masterplan.

## Features

🏗️ **Cloud Build Integration**: Executes pytest in Google Cloud Build for scalable testing  
🔄 **DevAgent Feedback Loop**: Automatically sends feedback to DevAgent when tests fail  
✅ **Comprehensive Testing**: Runs unit tests, integration tests, and coverage analysis  
🔍 **Intelligent Analysis**: Parses test results and provides actionable feedback  
📊 **Quality Metrics**: Calculates code quality scores and coverage percentages  
🏢 **Multi-tenant Support**: Built-in tenant isolation and database integration  
📈 **Performance Monitoring**: Tracks review metrics and success rates  

## Architecture

```bash
ReviewAgent (Night 37)
├── Pytest Execution Engine
│   ├── Local Execution (fallback)
│   └── Cloud Build Integration
├── Test Result Parser
├── Feedback Analysis Engine
├── DevAgent Communication
├── Cloud Build Manager
└── Tenant Database Integration
```

## Night 37 Requirements ✅

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| **Run Pytest in Cloud Build** | ✅ Full Cloud Build API integration with artifact storage | Complete |
| **Loop back to DevAgent on failure** | ✅ HTTP feedback with issue analysis and suggestions | Complete |
| **Test result parsing** | ✅ Comprehensive pytest output parsing and metrics | Complete |
| **Quality analysis** | ✅ Code quality scoring and improvement suggestions | Complete |

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_CLOUD_PROJECT="your-project-id"
export DEV_AGENT_URL="http://dev-agent:8083"
export DB_HOST="localhost"
export DB_NAME="factorydb"
```

### 2. Start the ReviewAgent

```bash
# Start the server
python review_agent.py

# Or with Docker
docker build -t reviewagent .
docker run -p 8084:8084 reviewagent
```

### 3. Review Generated Code

```bash
# Run the demo
python review_demo.py

# Or make HTTP requests
curl -X POST http://localhost:8084/review \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "my-project",
    "module_name": "UserService",
    "generated_files": [...]
  }'
```

## API Endpoints

### `POST /review`

Review generated code using pytest in Cloud Build.

**Request Body:**

```json
{
  "project_id": "string",
  "module_name": "string", 
  "generated_files": [
    {
      "filename": "main.py",
      "content": "def hello(): return 'world'",
      "file_type": "source",
      "language": "python",
      "size_bytes": 1024,
      "functions": ["hello"],
      "imports": []
    }
  ],
  "dev_agent_request_id": "optional-for-feedback-loop",
  "review_type": "full|syntax|tests_only",
  "cloud_build_config": {...}
}
```

**Response:**

```json
{
  "review_id": "uuid",
  "project_id": "my-project",
  "module_name": "UserService",
  "review_status": "passed|failed|error",
  "cloud_build_result": {
    "build_id": "cloud-build-uuid",
    "status": "success|failure",
    "duration": 45.2,
    "log_url": "https://console.cloud.google.com/...",
    "pytest_results": {
      "total_tests": 15,
      "passed": 13,
      "failed": 2,
      "errors": 0,
      "coverage_percentage": 78.5,
      "test_results": [...]
    }
  },
  "feedback": {
    "review_passed": false,
    "issues_found": [
      "Division by zero not handled in calculate function",
      "Missing type hints for user_id parameter"
    ],
    "suggestions": [
      "Add input validation for numeric operations", 
      "Include comprehensive type annotations"
    ],
    "code_quality_score": 72.5,
    "retry_recommended": true
  },
  "review_duration": 42.1,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### `GET /review-history/{project_id}`

Get review history for a project.

### `POST /review-feedback`

Submit manual review feedback.

### `GET /health`

Health check endpoint.

## Cloud Build Integration

The ReviewAgent uses Google Cloud Build to execute tests in a clean, containerized environment:

### Cloud Build Process

1. **Source Packaging**: Creates ZIP archive of generated code
2. **GCS Upload**: Uploads source to Google Cloud Storage  
3. **Build Submission**: Submits build job to Cloud Build
4. **Test Execution**: Runs pytest with comprehensive options
5. **Artifact Collection**: Stores test results, coverage reports
6. **Result Processing**: Downloads and parses test artifacts

### Cloud Build Configuration

```yaml
steps:
  - name: 'python:3.11-slim'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        pip install pytest pytest-cov pytest-xdist
        python -m pytest --cov=src --junit-xml=results.xml tests/

artifacts:
  objects:
    location: 'gs://project-artifacts/reviews/$BUILD_ID'
    paths: ['results.xml', 'coverage.xml']

timeout: '600s'
```

## DevAgent Feedback Loop

The core **Night 37** feature - when tests fail, ReviewAgent automatically sends feedback to DevAgent:

### Feedback Process

1. **Test Analysis**: Parse pytest results and identify failure patterns
2. **Issue Classification**: Categorize errors (syntax, import, assertion, type)
3. **Suggestion Generation**: Create actionable improvement recommendations
4. **Feedback Transmission**: Send structured feedback to DevAgent via HTTP
5. **Loop Completion**: DevAgent can regenerate improved code

### Feedback Structure

```python
{
  "request_id": "original-dev-request-id",
  "review_passed": false,
  "issues": [
    "Assertion failure in test_calculate: Expected 10 but got 8",
    "Import error in test_module: Missing dependency 'requests'"
  ],
  "suggestions": [
    "Review calculation logic and expected values",
    "Add 'requests' to requirements.txt dependencies"
  ],
  "code_quality_score": 65.5,
  "retry_recommended": true
}
```

## Test Types Supported

| Test Type | Description | Cloud Build | Local Fallback |
|-----------|-------------|-------------|----------------|
| **Unit Tests** | Individual function/method testing | ✅ | ✅ |
| **Integration Tests** | Component interaction testing | ✅ | ✅ |
| **Coverage Analysis** | Code coverage measurement | ✅ | ✅ |
| **Syntax Validation** | Python syntax checking | ✅ | ✅ |
| **Performance Tests** | Execution time validation | 🔄 | 🔄 |
| **Security Scans** | Vulnerability detection | 🔄 | 🔄 |

Legend: ✅ Implemented, 🔄 Planned

## Quality Metrics

The ReviewAgent calculates comprehensive quality scores:

### Score Components

- **Test Pass Rate** (40%): Percentage of tests passing
- **Code Coverage** (30%): Percentage of code covered by tests  
- **Issue Severity** (20%): Weight of critical vs minor issues
- **Best Practices** (10%): Code style and documentation quality

### Quality Thresholds

- **Excellent**: 90-100 points
- **Good**: 75-89 points  
- **Acceptable**: 60-74 points
- **Needs Improvement**: < 60 points

## Issue Detection

The ReviewAgent identifies common code issues:

### Failure Analysis

```python
# Assertion failures
"Assertion failure in test_calculate: Expected 10 but got 8"
→ "Review assertion logic and expected vs actual values"

# Import errors  
"Import error in test_module: Missing dependency"
→ "Check import statements and ensure all dependencies are included"

# Type errors
"Type error in test_function: Incorrect argument types" 
→ "Add proper type hints and validate function signatures"

# Syntax errors
"Syntax error in module: Invalid Python syntax"
→ "Review code syntax, indentation, and Python grammar"
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | saas-factory-prod |
| `CLOUD_BUILD_REGION` | Cloud Build region | us-central1 |
| `DEV_AGENT_URL` | DevAgent base URL | http://dev-agent:8083 |
| `MAX_REVIEW_RETRIES` | Maximum retry attempts | 3 |
| `DB_HOST` | Database host | localhost |
| `DB_NAME` | Database name | factorydb |
| `DB_USER` | Database user | factoryadmin |
| `DB_PASSWORD` | Database password | - |

## Local vs Cloud Build

### Local Execution (Fallback)

- Fast execution for development
- Limited to single machine resources
- Uses local Python environment
- Immediate results

### Cloud Build Execution (Production)

- Scalable containerized testing
- Consistent clean environments
- Artifact storage and retrieval
- Detailed logging and monitoring
- Better isolation between tests

## Performance

- **Local Pytest**: ~5-15 seconds per review
- **Cloud Build**: ~30-60 seconds per review  
- **Concurrent Reviews**: Up to 10 simultaneous
- **Memory Usage**: ~150MB baseline, +100MB per review
- **Throughput**: ~100 reviews per hour

## Integration Examples

### With DevAgent

```python
# DevAgent generates code
code_result = await dev_agent.generate_code(module_spec)

# ReviewAgent reviews the code
review_request = CodeReviewRequest(
    project_id=project_id,
    module_name=code_result.module_name,
    generated_files=code_result.files,
    dev_agent_request_id=code_result.request_id
)

review_result = await review_agent.review_generated_code(review_request)

# Automatic feedback loop if tests fail
if not review_result.feedback.review_passed:
    # ReviewAgent automatically sends feedback to DevAgent
    # DevAgent can regenerate improved code
    pass
```

### With Orchestrator

```python
# In orchestrator/project_orchestrator.py
class ReviewAgentIntegration(Agent):
    async def review_generated_code(self, code_generation_result):
        response = await httpx.post(
            "http://review-agent:8084/review",
            json={
                "project_id": code_generation_result.project_id,
                "module_name": code_generation_result.module_name,
                "generated_files": code_generation_result.files
            }
        )
        return response.json()
```

## Testing

```bash
# Run unit tests
pytest test_review_agent.py -v

# Run with coverage
pytest test_review_agent.py --cov=review_agent --cov-report=html

# Run integration tests
pytest test_review_agent.py::TestReviewAgent::test_cloud_build_integration -v

# Run demo
python review_demo.py
```

## Monitoring

### Key Metrics

- Review success rate
- Average review duration  
- Test failure patterns
- Cloud Build usage
- Feedback loop effectiveness

### Health Checks

- Database connectivity
- Cloud Build API availability
- DevAgent communication
- Storage bucket access

## Troubleshooting

### Common Issues

1. **Cloud Build Failures**
   - Check GCP credentials and permissions
   - Verify project ID and region settings
   - Ensure Cloud Build API is enabled

2. **DevAgent Communication**  
   - Verify DEV_AGENT_URL configuration
   - Check network connectivity
   - Ensure DevAgent is running

3. **Pytest Execution**
   - Check Python syntax in generated code
   - Verify test file structure
   - Ensure required dependencies are included

## Future Enhancements

- **Multi-language Support**: JavaScript/TypeScript testing with Jest
- **Security Scanning**: Integration with security vulnerability scanners  
- **Performance Benchmarking**: Automated performance regression testing
- **Visual Testing**: UI component screenshot comparison
- **AI-Powered Suggestions**: ML-based code improvement recommendations

---

## Night 37 Implementation Status ✅

This ReviewAgent implementation fully satisfies the **Night 37** requirements:

- ✅ **Runs Pytest in Cloud Build**: Complete Google Cloud Build integration with artifact management
- ✅ **Loops back to DevAgent on failure**: Automatic feedback transmission with detailed issue analysis  
- ✅ **Comprehensive testing**: Unit tests, integration tests, coverage analysis
- ✅ **Production-ready**: Error handling, logging, monitoring, tenant support
- ✅ **Scalable architecture**: Handles concurrent reviews and integrates with orchestrator

The ReviewAgent is now ready to provide intelligent code review capabilities as part of the complete AI SaaS Factory pipeline, ensuring code quality through automated testing and continuous improvement feedback loops.
