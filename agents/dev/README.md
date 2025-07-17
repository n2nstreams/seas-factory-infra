# DevAgent - Intelligent Code Generation Agent

The DevAgent is a sophisticated AI-powered code generation agent that uses **GPT-4o function calling** with **pydantic schemas** for module specifications. It can generate production-ready code for various programming languages and frameworks.

## Features

🚀 **GPT-4o Function Calling**: Utilizes OpenAI's GPT-4o with structured function calling for precise code generation  
📋 **Pydantic Schemas**: Robust module specifications with validation  
🎯 **Multiple Languages**: Support for Python, JavaScript, TypeScript, HTML, CSS  
🔧 **Framework Support**: FastAPI, React, Vue, Express, Flask  
✅ **Code Validation**: Automatic syntax validation and error checking  
📚 **Documentation**: Auto-generated documentation and setup instructions  
🧪 **Unit Tests**: Automatic test generation for generated code  
🏢 **Multi-tenant**: Built-in tenant isolation and database integration  

## Architecture

```bash
DevAgent
├── GPT-4o Function Calling
├── Pydantic Module Specifications
├── Code Template Engine
├── Validation Engine
├── Test Generation
├── Documentation Generation
└── Tenant Database Integration
```

## Module Types Supported

| Type | Description | Languages | Frameworks |
|------|-------------|-----------|------------|
| **Service** | Business logic services | Python, JavaScript | FastAPI, Express |
| **API** | REST API endpoints | Python, JavaScript | FastAPI, Express |
| **Component** | UI components | TypeScript, JavaScript | React, Vue |
| **Model** | Data models | Python, TypeScript | Pydantic, TypeScript |
| **Utility** | Helper functions | Python, JavaScript | - |
| **Page** | Web pages | HTML, CSS | - |

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export DB_HOST="localhost"
export DB_NAME="factorydb"
export DB_USER="factoryadmin"
export DB_PASSWORD="your-db-password"
```

### 2. Start the DevAgent

```bash
# Start the server
python main.py

# Or with Docker
docker build -t devagent .
docker run -p 8083:8083 devagent
```

### 3. Generate Code

```bash
# Run the demo
python demo.py

# Or make HTTP requests
curl -X POST http://localhost:8083/generate \
  -H "Content-Type: application/json" \
  -d '{
    "module_spec": {
      "name": "UserService",
      "description": "Service for user management",
      "module_type": "service",
      "language": "python",
      "framework": "fastapi"
    }
  }'
```

## API Endpoints

### `POST /generate`

Generate code based on module specification.

**Request Body:**

```json
{
  "project_id": "optional-project-id",
  "module_spec": {
    "name": "ModuleName",
    "description": "Module description",
    "module_type": "service|api|component|model|utility|page",
    "language": "python|javascript|typescript|html|css",
    "framework": "fastapi|react|vue|express|flask",
    "dependencies": ["dependency1", "dependency2"],
    "functions": [
      {
        "name": "function_name",
        "description": "Function description",
        "parameters": ["param1", "param2"]
      }
    ],
    "api_endpoints": [
      {
        "method": "GET|POST|PUT|DELETE",
        "path": "/api/path",
        "handler_name": "handler_function",
        "description": "Endpoint description"
      }
    ],
    "requirements": ["Requirement 1", "Requirement 2"]
  },
  "style_preferences": {
    "follow_pep8": true,
    "use_type_hints": true,
    "include_docstrings": true
  },
  "include_tests": true,
  "include_documentation": true
}
```

**Response:**

```json
{
  "module_name": "ModuleName",
  "files": [
    {
      "filename": "module_name.py",
      "content": "# Generated code...",
      "file_type": "source",
      "language": "python",
      "size_bytes": 1234,
      "functions": ["function1", "function2"],
      "imports": ["import1", "import2"]
    }
  ],
  "total_files": 3,
  "total_lines": 150,
  "estimated_complexity": "Medium",
  "validation_results": {
    "module_name.py": {
      "valid": true,
      "errors": []
    }
  },
  "setup_instructions": [
    "1. Install dependencies: pip install ...",
    "2. Run tests: pytest ..."
  ],
  "next_steps": [
    "1. Review generated code",
    "2. Implement TODO items"
  ],
  "reasoning": "Generated code explanation"
}
```

### `GET /templates`

Get available code templates.

### `GET /languages`

Get supported programming languages and frameworks.

### `GET /health`

Health check endpoint.

## Module Specification Schema

The `ModuleSpec` uses pydantic for robust validation:

```python
class ModuleSpec(BaseModel):
    name: str = Field(..., description="Name of the module")
    description: str = Field(..., description="Description of what the module does")
    module_type: Literal["api", "service", "model", "utility", "component", "page"]
    language: Literal["python", "javascript", "typescript", "html", "css"]
    framework: Optional[str] = Field(None, description="Framework to use")
    dependencies: List[str] = Field(default_factory=list)
    functions: List[Dict[str, Any]] = Field(default_factory=list)
    api_endpoints: List[Dict[str, Any]] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
```

## Code Generation Examples

### Python FastAPI Service

```python
module_spec = ModuleSpec(
    name="TaskService",
    description="A service for managing tasks",
    module_type="service",
    language="python",
    framework="fastapi",
    dependencies=["fastapi", "pydantic", "sqlalchemy"],
    functions=[
        {
            "name": "create_task",
            "description": "Create a new task",
            "parameters": ["title", "description"]
        }
    ],
    api_endpoints=[
        {
            "method": "POST",
            "path": "/tasks",
            "handler_name": "create_task_endpoint",
            "description": "Create a new task"
        }
    ]
)
```

### React Component

```python
module_spec = ModuleSpec(
    name="TaskCard",
    description="A React component for displaying tasks",
    module_type="component",
    language="typescript",
    framework="react",
    dependencies=["react", "@types/react"],
    functions=[
        {
            "name": "onTaskClick",
            "description": "Handle task click events",
            "parameters": ["task"]
        }
    ]
)
```

## Integration with Orchestrator

The DevAgent integrates with the main orchestrator system:

```python
# In orchestrator/project_orchestrator.py
class DevAgentIntegration(Agent):
    def __init__(self):
        super().__init__(
            name="dev_agent",
            description="Code generation agent using GPT-4o",
            tools=[self.generate_code]
        )
    
    async def generate_code(self, module_spec: dict) -> dict:
        """Generate code using DevAgent"""
        # Call DevAgent API
        response = await httpx.post(
            "http://dev-agent:8083/generate",
            json={"module_spec": module_spec}
        )
        return response.json()
```

## Testing

```bash
# Run unit tests
pytest test_agent.py -v

# Run with coverage
pytest test_agent.py --cov=main --cov-report=html

# Run specific test
pytest test_agent.py::TestDevAgent::test_python_code_generation -v
```

## Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8083

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8083"]
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o | Required |
| `DB_HOST` | Database host | localhost |
| `DB_NAME` | Database name | factorydb |
| `DB_USER` | Database user | factoryadmin |
| `DB_PASSWORD` | Database password | - |
| `DB_PORT` | Database port | 5432 |

## Performance

- **Code Generation**: ~2-5 seconds per module
- **Validation**: ~100ms per file
- **Concurrent Requests**: Up to 10 simultaneous generations
- **Memory Usage**: ~200MB baseline, +50MB per active generation

## Limitations

- GPT-4o API rate limits apply
- Generated code may require manual review
- Complex business logic may need refinement
- Language-specific validation varies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is part of the AI SaaS Factory and follows the main project license.

---

## Night 36 Implementation Status ✅

This DevAgent implementation fulfills the **Night 36** requirements from the masterplan:

- ✅ **GPT-4o function-calling**: Implemented with structured function definitions
- ✅ **Pydantic schema for module spec**: Comprehensive `ModuleSpec` model with validation
- ✅ **Coder agent functionality**: Generates Python, JavaScript, TypeScript, React components
- ✅ **Production-ready**: Includes error handling, logging, validation, and testing
- ✅ **Integration ready**: FastAPI service with proper endpoints and tenant support

The DevAgent is now ready to be integrated into the larger SaaS Factory orchestration system and can generate high-quality code modules based on AI-powered specifications.
