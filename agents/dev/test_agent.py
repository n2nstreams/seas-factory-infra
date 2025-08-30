import pytest
from unittest.mock import AsyncMock, patch
from main import DevAgent, ModuleSpec, CodeGenerationRequest, TenantContext

# Test data
SAMPLE_MODULE_SPEC = ModuleSpec(
    name="UserService",
    description="A service for managing user operations",
    module_type="service",
    language="python",
    framework="fastapi",
    dependencies=["fastapi", "pydantic", "sqlalchemy"],
    functions=[
        {
            "name": "create_user",
            "description": "Create a new user in the system",
            "parameters": ["name", "email", "password"]
        },
        {
            "name": "get_user",
            "description": "Get user by ID",
            "parameters": ["user_id"]
        }
    ],
    api_endpoints=[
        {
            "method": "POST",
            "path": "/users",
            "handler_name": "create_user_endpoint",
            "description": "Create a new user"
        },
        {
            "method": "GET",
            "path": "/users/{user_id}",
            "handler_name": "get_user_endpoint",
            "description": "Get user by ID"
        }
    ],
    requirements=[
        "Users must be created with valid email addresses",
        "User passwords must be hashed before storage",
        "User IDs must be unique"
    ]
)

@pytest.fixture
def dev_agent():
    """Create a DevAgent instance for testing"""
    return DevAgent()

@pytest.fixture
def tenant_context():
    """Create a test tenant context"""
    return TenantContext(tenant_id="test-tenant", user_id="test-user")

@pytest.fixture
def code_generation_request():
    """Create a test code generation request"""
    return CodeGenerationRequest(
        project_id="test-project",
        module_spec=SAMPLE_MODULE_SPEC,
        style_preferences={"follow_pep8": True, "use_type_hints": True},
        include_tests=True,
        include_documentation=True
    )

class TestDevAgent:
    """Test suite for DevAgent functionality"""

    def test_dev_agent_initialization(self, dev_agent):
        """Test DevAgent initialization"""
        assert dev_agent is not None
        assert hasattr(dev_agent, 'openai_client')
        assert hasattr(dev_agent, 'tenant_db')
        assert hasattr(dev_agent, 'code_templates')
        assert len(dev_agent.code_templates) > 0

    def test_module_spec_validation(self):
        """Test ModuleSpec validation"""
        # Valid module spec
        valid_spec = ModuleSpec(
            name="TestModule",
            description="A test module",
            module_type="service",
            language="python"
        )
        assert valid_spec.name == "TestModule"
        assert valid_spec.module_type == "service"
        assert valid_spec.language == "python"

        # Test with invalid module type
        with pytest.raises(Exception):
            ModuleSpec(
                name="TestModule",
                description="A test module",
                module_type="invalid_type",
                language="python"
            )

    def test_code_generation_functions(self, dev_agent):
        """Test GPT-4o function definitions"""
        functions = dev_agent._get_code_generation_functions()
        
        assert len(functions) == 3
        
        # Check function names
        function_names = [func["name"] for func in functions]
        assert "generate_python_module" in function_names
        assert "generate_react_component" in function_names
        assert "generate_api_endpoint" in function_names
        
        # Check function structure
        for func in functions:
            assert "name" in func
            assert "description" in func
            assert "parameters" in func

    def test_file_extension_mapping(self, dev_agent):
        """Test file extension mapping for different languages"""
        assert dev_agent._get_file_extension("python") == "py"
        assert dev_agent._get_file_extension("javascript") == "js"
        assert dev_agent._get_file_extension("typescript") == "ts"
        assert dev_agent._get_file_extension("html") == "html"
        assert dev_agent._get_file_extension("css") == "css"
        assert dev_agent._get_file_extension("unknown") == "txt"

    def test_python_code_generation(self, dev_agent):
        """Test Python code generation from specification"""
        spec = {
            "module_name": "TestService",
            "imports": ["from typing import Optional", "import logging"],
            "classes": [
                {
                    "name": "UserService",
                    "description": "Service for user operations",
                    "methods": [
                        {
                            "name": "create_user",
                            "description": "Create a new user",
                            "parameters": ["name", "email"]
                        }
                    ]
                }
            ],
            "functions": [
                {
                    "name": "validate_email",
                    "description": "Validate email address",
                    "parameters": ["email"]
                }
            ]
        }
        
        code = dev_agent._generate_python_from_spec(spec, SAMPLE_MODULE_SPEC)
        
        assert "class UserService:" in code
        assert "def create_user(self, name, email):" in code
        assert "def validate_email(email):" in code
        assert "from typing import Optional" in code
        assert "import logging" in code

    def test_react_component_generation(self, dev_agent):
        """Test React component generation from specification"""
        spec = {
            "component_name": "UserProfile",
            "props": [
                {"name": "userId", "type": "string", "required": True},
                {"name": "showEmail", "type": "boolean", "required": False}
            ],
            "state_variables": [
                {"name": "user", "type": "User | null", "initial_value": "null"}
            ],
            "methods": [
                {"name": "fetchUser", "description": "Fetch user data"}
            ]
        }
        
        code = dev_agent._generate_react_from_spec(spec, SAMPLE_MODULE_SPEC)
        
        assert "interface UserProfileProps {" in code
        assert "userId: string;" in code
        assert "showEmail?: boolean;" in code
        assert "const [user, setUser] = useState<User | null>(null);" in code
        assert "const fetchUser = () => {" in code
        assert "export default UserProfile;" in code

    def test_api_endpoint_generation(self, dev_agent):
        """Test API endpoint generation from specification"""
        spec = {
            "endpoints": [
                {
                    "method": "GET",
                    "path": "/users",
                    "handler_name": "get_users",
                    "description": "Get all users"
                },
                {
                    "method": "POST",
                    "path": "/users",
                    "handler_name": "create_user",
                    "description": "Create a new user"
                }
            ]
        }
        
        code = dev_agent._generate_api_from_spec(spec, SAMPLE_MODULE_SPEC)
        
        assert "@app.get('/users')" in code
        assert "@app.post('/users')" in code
        assert "async def get_users(" in code
        assert "async def create_user(" in code
        assert "from fastapi import FastAPI" in code

    def test_code_validation(self, dev_agent):
        """Test code validation functionality"""
        from main import GeneratedFile
        
        # Valid Python code
        valid_file = GeneratedFile(
            filename="test.py",
            content="def hello():\n    return 'Hello, World!'",
            file_type="source",
            language="python",
            size_bytes=100
        )
        
        # Invalid Python code
        invalid_file = GeneratedFile(
            filename="test_invalid.py",
            content="def hello(\n    return 'Hello, World!'",  # Missing closing parenthesis
            file_type="source",
            language="python",
            size_bytes=100
        )
        
        results = dev_agent._validate_generated_code([valid_file, invalid_file])
        
        assert results["test.py"]["valid"] is True
        assert len(results["test.py"]["errors"]) == 0
        assert results["test_invalid.py"]["valid"] is False
        assert len(results["test_invalid.py"]["errors"]) > 0

    def test_test_file_generation(self, dev_agent):
        """Test unit test file generation"""
        from main import GeneratedFile
        
        files = [
            GeneratedFile(
                filename="user_service.py",
                content="class UserService: pass",
                file_type="source",
                language="python",
                size_bytes=100
            )
        ]
        
        test_file = dev_agent._generate_test_file(SAMPLE_MODULE_SPEC, files)
        
        assert test_file is not None
        assert test_file.filename == "test_userservice.py"
        assert "import pytest" in test_file.content
        assert "class TestUserservice:" in test_file.content
        assert test_file.file_type == "test"
        assert test_file.language == "python"

    def test_documentation_generation(self, dev_agent):
        """Test documentation file generation"""
        from main import GeneratedFile
        
        files = [
            GeneratedFile(
                filename="user_service.py",
                content="class UserService: pass",
                file_type="source",
                language="python",
                size_bytes=100
            )
        ]
        
        doc_file = dev_agent._generate_documentation(SAMPLE_MODULE_SPEC, files)
        
        assert doc_file is not None
        assert doc_file.filename == "userservice_README.md"
        assert "# Userservice Module" in doc_file.content
        assert SAMPLE_MODULE_SPEC.description in doc_file.content
        assert doc_file.file_type == "documentation"
        assert doc_file.language == "markdown"

    def test_setup_instructions_generation(self, dev_agent):
        """Test setup instructions generation"""
        from main import GeneratedFile
        
        files = [
            GeneratedFile(
                filename="user_service.py",
                content="class UserService: pass",
                file_type="source",
                language="python",
                size_bytes=100
            )
        ]
        
        instructions = dev_agent._generate_setup_instructions(SAMPLE_MODULE_SPEC, files)
        
        assert len(instructions) > 0
        assert any("pip install" in instruction for instruction in instructions)
        assert any("pytest" in instruction for instruction in instructions)

    @patch('main.DevAgent._call_gpt4o_function')
    async def test_generate_code_with_gpt4o(self, mock_gpt4o, dev_agent):
        """Test code generation with GPT-4o mocking"""
        # Mock GPT-4o response
        mock_gpt4o.return_value = {
            "status": "success",
            "function_call": {
                "name": "generate_python_module",
                "arguments": '{"module_name": "TestService", "classes": [{"name": "TestService", "description": "A test service", "methods": []}], "functions": [], "imports": []}'
            }
        }
        
        response = await dev_agent.generate_code_with_gpt4o(
            SAMPLE_MODULE_SPEC,
            {"follow_pep8": True}
        )
        
        assert response["status"] == "success"
        assert response["function_call"]["name"] == "generate_python_module"
        mock_gpt4o.assert_called_once()

    @patch('main.DevAgent._call_gpt4o_function')
    @patch('main.DevAgent.tenant_db')
    async def test_full_code_generation(self, mock_db, mock_gpt4o, dev_agent, tenant_context, code_generation_request):
        """Test full code generation flow"""
        # Mock database
        mock_db.log_agent_event = AsyncMock()
        
        # Mock GPT-4o response
        mock_gpt4o.return_value = {
            "status": "success",
            "function_call": {
                "name": "generate_python_module",
                "arguments": '{"module_name": "UserService", "classes": [{"name": "UserService", "description": "Service for user operations", "methods": [{"name": "create_user", "description": "Create a new user", "parameters": ["name", "email"]}]}], "functions": [], "imports": ["from typing import Optional"]}'
            }
        }
        
        result = await dev_agent.generate_code(code_generation_request, tenant_context)
        
        assert result.module_name == "UserService"
        assert result.total_files >= 1  # At least the main file
        assert result.total_lines > 0
        assert len(result.files) > 0
        assert result.validation_results is not None
        assert len(result.setup_instructions) > 0
        assert len(result.next_steps) > 0
        
        # Check that database logging was called
        assert mock_db.log_agent_event.call_count >= 2  # Start and completion events

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 