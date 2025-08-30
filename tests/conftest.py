#!/usr/bin/env python3
"""
Pytest Configuration and Fixtures
Comprehensive testing setup for SaaS Factory
"""

import asyncio
import os
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch
import asyncpg
import httpx
from datetime import datetime

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "true"
os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["DB_NAME"] = "factorydb_test"
os.environ["DB_PASSWORD"] = "testpass"
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret"

# Import configuration and shared components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.settings import get_settings
from agents.shared.tenant_db import TenantDatabase, TenantContext
# Prevent hard dependency on real Stripe keys during collection
os.environ.setdefault("STRIPE_API_KEY", "test-key")


# Test configuration
TEST_CONFIG = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "factorydb_test",
        "user": "factoryadmin",
        "password": "testpass"
    },
    "tenant_id": "test-tenant",
    "user_id": "test-user",
    "project_id": "test-project-123"
}


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings():
    """Get test settings"""
    return get_settings()


@pytest.fixture(scope="session")
async def test_database():
    """Create test database and clean up after tests"""
    
    # Create test database
    admin_conn = await asyncpg.connect(
        host=TEST_CONFIG["database"]["host"],
        port=TEST_CONFIG["database"]["port"],
        database="postgres",
        user=TEST_CONFIG["database"]["user"],
        password=TEST_CONFIG["database"]["password"]
    )
    
    try:
        # Drop test database if exists
        await admin_conn.execute(f"DROP DATABASE IF EXISTS {TEST_CONFIG['database']['name']}")
        
        # Create test database
        await admin_conn.execute(f"CREATE DATABASE {TEST_CONFIG['database']['name']}")
        
        # Create test connection
        test_conn = await asyncpg.connect(
            host=TEST_CONFIG["database"]["host"],
            port=TEST_CONFIG["database"]["port"],
            database=TEST_CONFIG["database"]["name"],
            user=TEST_CONFIG["database"]["user"],
            password=TEST_CONFIG["database"]["password"]
        )
        
        # Create test schema
        await create_test_schema(test_conn)
        
        yield test_conn
        
    finally:
        await admin_conn.execute(f"DROP DATABASE IF EXISTS {TEST_CONFIG['database']['name']}")
        await admin_conn.close()


@pytest.fixture
def db_connection():
    """Create database connection for testing"""
    # Note: This fixture will be used by async tests that need to await the connection
    # The actual connection will be created in the test methods
    pass


async def create_test_schema(conn):
    """Create test database schema"""
    
    # Create tenants table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            slug VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            subscription_status VARCHAR(50) DEFAULT 'trial',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create projects table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID REFERENCES tenants(id),
            name VARCHAR(255) NOT NULL,
            description TEXT,
            status VARCHAR(50) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create events table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID REFERENCES tenants(id),
            project_id UUID REFERENCES projects(id),
            agent_name VARCHAR(255) NOT NULL,
            event_type VARCHAR(255) NOT NULL,
            status VARCHAR(50) NOT NULL,
            data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create designs table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS designs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID REFERENCES tenants(id),
            project_id UUID REFERENCES projects(id),
            name VARCHAR(255) NOT NULL,
            figma_url VARCHAR(500),
            preview_url VARCHAR(500),
            design_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create security_scan_results table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS security_scan_results (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID REFERENCES tenants(id),
            project_id UUID REFERENCES projects(id),
            scan_type VARCHAR(100) NOT NULL,
            severity VARCHAR(50) NOT NULL,
            vulnerability_type VARCHAR(255),
            file_path VARCHAR(500),
            details JSONB,
            status VARCHAR(50) DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Enable Row Level Security
    await conn.execute("ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;")
    await conn.execute("ALTER TABLE projects ENABLE ROW LEVEL SECURITY;")
    await conn.execute("ALTER TABLE events ENABLE ROW LEVEL SECURITY;")
    await conn.execute("ALTER TABLE designs ENABLE ROW LEVEL SECURITY;")
    await conn.execute("ALTER TABLE security_scan_results ENABLE ROW LEVEL SECURITY;")
    
    # Create RLS policies
    await conn.execute("""
        CREATE POLICY tenant_isolation_policy ON projects
        FOR ALL USING (tenant_id = current_setting('app.tenant_id')::UUID);
    """)
    
    await conn.execute("""
        CREATE POLICY tenant_isolation_policy ON events
        FOR ALL USING (tenant_id = current_setting('app.tenant_id')::UUID);
    """)
    
    await conn.execute("""
        CREATE POLICY tenant_isolation_policy ON designs
        FOR ALL USING (tenant_id = current_setting('app.tenant_id')::UUID);
    """)
    
    await conn.execute("""
        CREATE POLICY tenant_isolation_policy ON security_scan_results
        FOR ALL USING (tenant_id = current_setting('app.tenant_id')::UUID);
    """)


@pytest.fixture
async def tenant_context():
    """Create test tenant context"""
    return TenantContext(
        tenant_id=TEST_CONFIG["tenant_id"],
        user_id=TEST_CONFIG["user_id"]
    )


@pytest.fixture
async def tenant_db(test_database, tenant_context):
    """Create tenant database instance"""
    db = TenantDatabase()
    await db.init_pool()
    
    # Create test tenant
    await db.create_tenant(
        tenant_context,
        slug="test-tenant",
        name="Test Tenant",
        email="test@example.com"
    )
    
    yield db
    
    await db.close_pool()


@pytest.fixture
def mock_openai():
    """Mock OpenAI API"""
    with patch('openai.AsyncOpenAI') as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        
        # Mock chat completions
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message = Mock()
        mock_completion.choices[0].message.content = "Test response"
        
        mock_instance.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        yield mock_instance


@pytest.fixture
def mock_stripe():
    """Mock Stripe API"""
    with patch('stripe.Customer') as mock_customer, \
         patch('stripe.Subscription') as mock_subscription, \
         patch('stripe.PaymentIntent') as mock_payment_intent, \
         patch('stripe.checkout.Session') as mock_checkout:
        
        # Mock customer
        mock_customer.create.return_value = Mock(
            id="cus_test123",
            email="test@example.com",
            name="Test User",
            created=1234567890,
            metadata={"tenant_id": "test-tenant"}
        )
        
        # Mock subscription
        mock_subscription.create.return_value = Mock(
            id="sub_test123",
            customer="cus_test123",
            status="active",
            current_period_start=1234567890,
            current_period_end=1234567890 + 86400 * 30,
            cancel_at_period_end=False,
            items=Mock(data=[Mock(price=Mock(id="price_test123"))]),
            metadata={"tier": "starter"}
        )
        
        # Mock checkout session
        mock_checkout.create.return_value = Mock(
            id="cs_test123",
            url="https://checkout.stripe.com/pay/cs_test123",
            metadata={"tier": "starter"}
        )
        
        yield {
            "customer": mock_customer,
            "subscription": mock_subscription,
            "payment_intent": mock_payment_intent,
            "checkout": mock_checkout
        }


@pytest.fixture
def mock_slack():
    """Mock Slack API"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True, "ts": "1234567890.123"}
        
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        yield mock_client


@pytest.fixture
def mock_github():
    """Mock GitHub API"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 1,
            "number": 1,
            "title": "Test PR",
            "body": "Test PR body",
            "html_url": "https://github.com/test/repo/pull/1",
            "state": "open",
            "head": {"ref": "test-branch"},
            "base": {"ref": "main"}
        }
        
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        yield mock_client


@pytest.fixture
def mock_figma():
    """Mock Figma API"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "key": "test-file-key",
            "name": "Test Design",
            "document": {
                "id": "0:0",
                "name": "Document",
                "type": "DOCUMENT",
                "children": [
                    {
                        "id": "0:1",
                        "name": "Page 1",
                        "type": "CANVAS",
                        "children": [
                            {
                                "id": "0:2",
                                "name": "Frame 1",
                                "type": "FRAME",
                                "absoluteBoundingBox": {
                                    "x": 0,
                                    "y": 0,
                                    "width": 375,
                                    "height": 812
                                }
                            }
                        ]
                    }
                ]
            }
        }
        
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        yield mock_client


@pytest.fixture
def temp_directory():
    """Create temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_project_data():
    """Sample project data for testing"""
    return {
        "id": TEST_CONFIG["project_id"],
        "name": "Test Project",
        "description": "A test project for unit testing",
        "project_type": "web_app",
        "pages": ["home", "about", "contact", "dashboard"],
        "style_preferences": {
            "theme": "glassmorphism",
            "primary_color": "#6B7280",
            "secondary_color": "#84CC16"
        },
        "tech_stack": {
            "frontend": "React",
            "backend": "FastAPI",
            "database": "PostgreSQL",
            "deployment": "Cloud Run"
        }
    }


@pytest.fixture
def sample_tenant_data():
    """Sample tenant data for testing"""
    return {
        "id": TEST_CONFIG["tenant_id"],
        "slug": "test-tenant",
        "name": "Test Tenant",
        "email": "test@example.com",
        "subscription_status": "active",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def sample_design_data():
    """Sample design data for testing"""
    return {
        "project_id": TEST_CONFIG["project_id"],
        "project_type": "web_app",
        "pages": ["home", "about", "contact"],
        "color_scheme": "natural",
        "layout_type": "clean",
        "style_preferences": {
            "theme": "glassmorphism",
            "primary_color": "#6B7280"
        },
        "target_audience": "business users"
    }


@pytest.fixture
def sample_code_generation_data():
    """Sample code generation data for testing"""
    return {
        "project_id": TEST_CONFIG["project_id"],
        "module_spec": {
            "name": "UserService",
            "type": "service",
            "description": "User management service with CRUD operations",
            "functions": [
                {
                    "name": "create_user",
                    "parameters": ["email", "name", "password"],
                    "return_type": "User",
                    "description": "Create a new user"
                },
                {
                    "name": "get_user",
                    "parameters": ["user_id"],
                    "return_type": "User",
                    "description": "Get user by ID"
                }
            ]
        },
        "requirements": [
            "Use FastAPI for API endpoints",
            "Use Pydantic for data validation",
            "Include proper error handling",
            "Add docstrings and type hints"
        ]
    }


@pytest.fixture
def sample_security_scan_data():
    """Sample security scan data for testing"""
    return {
        "project_id": TEST_CONFIG["project_id"],
        "scan_type": "dependencies",
        "severity_threshold": "medium",
        "files": [
            "requirements.txt",
            "package.json",
            "Dockerfile"
        ]
    }


@pytest.fixture
async def http_client():
    """Create HTTP client for API testing"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client


@pytest.fixture
def mock_cloud_services():
    """Mock Google Cloud services"""
    with patch('google.cloud.logging.Client') as mock_logging, \
         patch('google.cloud.monitoring_v3.MetricServiceClient') as mock_monitoring, \
         patch('google.cloud.error_reporting.Client') as mock_error_reporting:
        
        yield {
            "logging": mock_logging,
            "monitoring": mock_monitoring,
            "error_reporting": mock_error_reporting
        }


# Test utilities
class AsyncContextManager:
    """Async context manager for testing"""
    
    def __init__(self, value):
        self.value = value
    
    async def __aenter__(self):
        return self.value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


def create_mock_response(status_code: int, json_data: Dict[str, Any]) -> Mock:
    """Create mock HTTP response"""
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json_data
    mock_response.text = str(json_data)
    return mock_response


async def wait_for_condition(condition, timeout: float = 5.0, interval: float = 0.1):
    """Wait for condition to be true with timeout"""
    start_time = asyncio.get_event_loop().time()
    
    while True:
        if condition():
            return True
        
        if asyncio.get_event_loop().time() - start_time > timeout:
            raise TimeoutError("Condition not met within timeout")
        
        await asyncio.sleep(interval)


# Test markers
def integration_test(func):
    """Mark test as integration test"""
    return pytest.mark.integration(func)


def slow_test(func):
    """Mark test as slow"""
    return pytest.mark.slow(func)


def requires_docker(func):
    """Mark test as requiring Docker"""
    return pytest.mark.docker(func)


def requires_network(func):
    """Mark test as requiring network access"""
    return pytest.mark.network(func)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "docker: mark test as requiring Docker"
    )
    config.addinivalue_line(
        "markers", "network: mark test as requiring network access"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        # Add integration marker to tests in integration directory
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add slow marker to tests that might be slow
        if any(keyword in item.name for keyword in ["test_full_", "test_end_to_end_", "test_load_"]):
            item.add_marker(pytest.mark.slow) 