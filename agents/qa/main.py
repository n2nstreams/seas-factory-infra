#!/usr/bin/env python3
"""
QA Agent - Automated Test Generation and Quality Assurance
Automatically generates test cases, performs quality checks, and monitors test coverage.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import json
import os
import requests
import asyncio
import asyncpg
from datetime import datetime
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="QA Agent",
    description="Automated test generation and quality assurance",
    version="1.0.0"
)

# Request/Response Models
class TestGenerationRequest(BaseModel):
    project_id: str = Field(..., description="Project ID to generate tests for")
    test_type: str = Field(default="unit", description="Type of tests to generate (unit, integration, e2e)")
    target_module: Optional[str] = Field(None, description="Specific module to test")
    coverage_threshold: float = Field(default=80.0, description="Minimum coverage threshold")

class TestCaseModel(BaseModel):
    name: str
    description: str
    test_type: str
    module: str
    code: str
    assertions: List[str]
    setup_required: bool = False
    cleanup_required: bool = False

class TestSuiteModel(BaseModel):
    suite_name: str
    project_id: str
    test_cases: List[TestCaseModel]
    estimated_duration: int  # in minutes
    dependencies: List[str] = []

class QualityMetrics(BaseModel):
    coverage_percentage: float
    test_count: int
    passing_tests: int
    failing_tests: int
    critical_issues: int
    code_smells: int
    security_vulnerabilities: int

class QAAgent:
    """Main QA Agent class for automated testing and quality assurance"""
    
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'factorydb'),
            'user': os.getenv('DB_USER', 'factoryadmin'),
            'password': os.getenv('DB_PASSWORD', 'localpass')
        }
        
        # Test generation prompts
        self.test_prompts = {
            'unit': {
                'system': """You are an expert test engineer. Generate comprehensive unit tests for the provided code.
                Focus on:
                - Testing all public methods and functions
                - Edge cases and boundary conditions
                - Error handling and exception cases
                - Input validation
                - Mock external dependencies
                
                Generate pytest-compatible Python test code.""",
                
                'user_template': """Generate unit tests for this code module:
                
                Module: {module}
                Code:
                {code}
                
                Requirements:
                - Use pytest framework
                - Include setup and teardown if needed
                - Test happy path and edge cases
                - Mock external dependencies
                - Include docstrings for test methods
                """
            },
            
            'integration': {
                'system': """You are an expert integration test engineer. Generate integration tests that verify components work together correctly.
                Focus on:
                - API endpoint testing
                - Database integration
                - Service-to-service communication
                - Data flow validation
                - Configuration testing""",
                
                'user_template': """Generate integration tests for:
                
                Project: {project_id}
                Component: {module}
                
                Test the integration between components, APIs, and external services.
                Use appropriate test frameworks and ensure proper test isolation."""
            },
            
            'e2e': {
                'system': """You are an expert end-to-end test engineer. Generate complete user journey tests.
                Focus on:
                - Complete user workflows
                - Browser automation (Playwright/Selenium)
                - Multi-step processes
                - Cross-browser compatibility
                - Performance validation""",
                
                'user_template': """Generate end-to-end tests for:
                
                Project: {project_id}
                User Journey: {module}
                
                Create complete user workflow tests using Playwright or similar tools.
                Include realistic user interactions and validation points."""
            }
        }
    
    async def get_project_info(self, project_id: str) -> Dict[str, Any]:
        """Get project information from database"""
        try:
            conn = await asyncpg.connect(**self.db_config)
            
            project = await conn.fetchrow(
                "SELECT * FROM projects WHERE id = $1",
                project_id
            )
            
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            
            await conn.close()
            return dict(project)
            
        except Exception as e:
            logger.error(f"Error fetching project info: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {e}")
    
    def generate_tenant_test_cases(self, tenant_id: str) -> List[TestCaseModel]:
        """Generate test cases specific to tenant functionality"""
        test_cases = [
            TestCaseModel(
                name="test_tenant_data_isolation",
                description="Verify that tenant data is properly isolated using RLS",
                test_type="integration",
                module="tenant_management",
                code=f"""
import pytest
import asyncpg
import uuid

async def test_tenant_data_isolation():
    \"\"\"Test that Row Level Security properly isolates tenant data\"\"\"
    conn = await asyncpg.connect(**TEST_DB_CONFIG)
    
    # Set tenant context
    await conn.execute("SET app.tenant_id = '{tenant_id}'")
    await conn.execute("SET ROLE application_role")
    
    # Query data - should only see this tenant's data
    projects = await conn.fetch("SELECT * FROM projects")
    users = await conn.fetch("SELECT * FROM users")
    
    # Verify all returned data belongs to this tenant
    for project in projects:
        assert str(project['tenant_id']) == '{tenant_id}'
    
    for user in users:
        assert str(user['tenant_id']) == '{tenant_id}'
    
    await conn.close()
""",
                assertions=[
                    "All returned projects belong to the correct tenant",
                    "All returned users belong to the correct tenant",
                    "No cross-tenant data leakage occurs"
                ],
                setup_required=True,
                cleanup_required=True
            ),
            
            TestCaseModel(
                name="test_tenant_api_access_control",
                description="Verify API endpoints respect tenant boundaries",
                test_type="integration",
                module="api_security",
                code=f"""
import pytest
import requests

async def test_tenant_api_access_control():
    \"\"\"Test that API endpoints enforce tenant access control\"\"\"
    base_url = "http://localhost:8000"
    
    # Test with valid tenant context
    headers = {{"X-Tenant-ID": "{tenant_id}"}}
    
    response = requests.get(f"{{base_url}}/api/projects", headers=headers)
    assert response.status_code == 200
    
    projects = response.json()
    for project in projects:
        assert project['tenant_id'] == '{tenant_id}'
    
    # Test access to another tenant's resources (should fail)
    other_tenant_id = str(uuid.uuid4())
    headers = {{"X-Tenant-ID": other_tenant_id}}
    
    response = requests.get(f"{{base_url}}/api/projects/{tenant_id}", headers=headers)
    assert response.status_code in [403, 404]  # Should be denied
""",
                assertions=[
                    "API returns only tenant-specific data",
                    "Cross-tenant access is denied",
                    "Proper HTTP status codes are returned"
                ]
            ),
            
            TestCaseModel(
                name="test_tenant_isolation_promotion",
                description="Test tenant promotion to isolated infrastructure",
                test_type="integration",
                module="tenant_isolation",
                code=f"""
import pytest
from scripts.tenant_isolation import TenantIsolationManager

async def test_tenant_isolation_promotion():
    \"\"\"Test promoting a tenant to isolated infrastructure\"\"\"
    manager = TenantIsolationManager()
    
    # Create test tenant
    test_tenant_slug = "test-isolation-tenant"
    
    # Perform isolation promotion
    result = await manager.promote_tenant(test_tenant_slug, cleanup_shared=False)
    
    assert result['status'] == 'success'
    assert result['isolated_db_name'].startswith('tenant_')
    
    # Verify tenant status updated
    status = await manager.get_isolation_status(test_tenant_slug)
    assert status['isolation_mode'] == 'isolated'
    
    # Clean up
    # ... cleanup code
""",
                assertions=[
                    "Tenant promotion completes successfully",
                    "Isolated database is created",
                    "Tenant status is updated correctly",
                    "Data migration is complete"
                ],
                setup_required=True,
                cleanup_required=True
            )
        ]
        
        return test_cases
    
    def generate_api_test_cases(self, project_id: str) -> List[TestCaseModel]:
        """Generate API test cases for a project"""
        test_cases = [
            TestCaseModel(
                name="test_api_authentication",
                description="Test API authentication and authorization",
                test_type="integration",
                module="api_auth",
                code="""
import pytest
import requests

def test_api_authentication():
    \"\"\"Test API authentication mechanisms\"\"\"
    base_url = "http://localhost:8000"
    
    # Test unauthenticated request
    response = requests.get(f"{base_url}/api/projects")
    assert response.status_code == 401
    
    # Test with valid authentication
    headers = {"Authorization": "Bearer valid_token"}
    response = requests.get(f"{base_url}/api/projects", headers=headers)
    assert response.status_code == 200
    
    # Test with invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    response = requests.get(f"{base_url}/api/projects", headers=headers)
    assert response.status_code == 401
""",
                assertions=[
                    "Unauthenticated requests are rejected",
                    "Valid tokens are accepted",
                    "Invalid tokens are rejected"
                ]
            ),
            
            TestCaseModel(
                name="test_api_rate_limiting",
                description="Test API rate limiting functionality",
                test_type="integration",
                module="api_limits",
                code="""
import pytest
import requests
import time

def test_api_rate_limiting():
    \"\"\"Test API rate limiting enforcement\"\"\"
    base_url = "http://localhost:8000"
    headers = {"Authorization": "Bearer valid_token"}
    
    # Make rapid requests to trigger rate limit
    responses = []
    for i in range(100):
        response = requests.get(f"{base_url}/api/projects", headers=headers)
        responses.append(response.status_code)
        if response.status_code == 429:  # Rate limited
            break
    
    # Should eventually get rate limited
    assert 429 in responses
    
    # Wait and try again - should work
    time.sleep(60)
    response = requests.get(f"{base_url}/api/projects", headers=headers)
    assert response.status_code == 200
""",
                assertions=[
                    "Rate limiting is enforced",
                    "Rate limit resets after time window",
                    "Proper HTTP 429 status is returned"
                ]
            )
        ]
        
        return test_cases
    
    def generate_performance_test_cases(self, project_id: str) -> List[TestCaseModel]:
        """Generate performance test cases"""
        return [
            TestCaseModel(
                name="test_database_query_performance",
                description="Test database query performance under load",
                test_type="performance",
                module="database_performance",
                code="""
import pytest
import asyncpg
import time
import asyncio

async def test_database_query_performance():
    \"\"\"Test database query performance\"\"\"
    conn = await asyncpg.connect(**TEST_DB_CONFIG)
    
    # Test individual query performance
    start_time = time.time()
    result = await conn.fetch("SELECT * FROM projects LIMIT 100")
    query_time = time.time() - start_time
    
    assert query_time < 1.0, f"Query took {query_time}s, should be < 1s"
    
    # Test concurrent query performance
    async def run_query():
        return await conn.fetch("SELECT COUNT(*) FROM users")
    
    start_time = time.time()
    tasks = [run_query() for _ in range(10)]
    await asyncio.gather(*tasks)
    concurrent_time = time.time() - start_time
    
    assert concurrent_time < 5.0, f"Concurrent queries took {concurrent_time}s"
    
    await conn.close()
""",
                assertions=[
                    "Individual queries complete within time limits",
                    "Concurrent queries perform adequately",
                    "No query timeouts occur"
                ]
            )
        ]
    
    async def analyze_code_quality(self, project_id: str) -> QualityMetrics:
        """Analyze code quality metrics for a project"""
        # Mock analysis - in real implementation, integrate with tools like:
        # - SonarQube for code quality
        # - Bandit for security analysis
        # - Coverage.py for test coverage
        
        return QualityMetrics(
            coverage_percentage=85.5,
            test_count=42,
            passing_tests=40,
            failing_tests=2,
            critical_issues=1,
            code_smells=7,
            security_vulnerabilities=0
        )
    
    async def generate_test_suite(self, request: TestGenerationRequest) -> TestSuiteModel:
        """Generate a comprehensive test suite"""
        project_info = await self.get_project_info(request.project_id)
        
        test_cases = []
        
        if request.test_type in ["unit", "all"]:
            # Generate unit tests
            pass
        
        if request.test_type in ["integration", "all"]:
            # Generate integration tests
            tenant_tests = self.generate_tenant_test_cases(project_info['tenant_id'])
            api_tests = self.generate_api_test_cases(request.project_id)
            test_cases.extend(tenant_tests)
            test_cases.extend(api_tests)
        
        if request.test_type in ["performance", "all"]:
            # Generate performance tests
            perf_tests = self.generate_performance_test_cases(request.project_id)
            test_cases.extend(perf_tests)
        
        if request.test_type in ["e2e", "all"]:
            # Generate end-to-end tests
            pass
        
        return TestSuiteModel(
            suite_name=f"{project_info['name']}_test_suite",
            project_id=request.project_id,
            test_cases=test_cases,
            estimated_duration=len(test_cases) * 3,  # 3 minutes per test
            dependencies=["pytest", "asyncpg", "requests"]
        )

# Initialize QA Agent
qa_agent = QAAgent()

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/generate-tests", response_model=TestSuiteModel)
async def generate_tests(request: TestGenerationRequest):
    """Generate test suite for a project"""
    try:
        test_suite = await qa_agent.generate_test_suite(request)
        return test_suite
    except Exception as e:
        logger.error(f"Error generating tests: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/quality-metrics/{project_id}", response_model=QualityMetrics)
async def get_quality_metrics(project_id: str):
    """Get quality metrics for a project"""
    try:
        metrics = await qa_agent.analyze_code_quality(project_id)
        return metrics
    except Exception as e:
        logger.error(f"Error getting quality metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run-tests/{project_id}")
async def run_tests(project_id: str, background_tasks: BackgroundTasks):
    """Run tests for a project"""
    try:
        # Add background task to run tests
        background_tasks.add_task(run_project_tests, project_id)
        return {"message": "Tests started", "project_id": project_id}
    except Exception as e:
        logger.error(f"Error starting tests: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_project_tests(project_id: str):
    """Background task to run project tests"""
    logger.info(f"Running tests for project {project_id}")
    
    # In real implementation:
    # 1. Generate test suite
    # 2. Execute tests using pytest
    # 3. Collect results
    # 4. Update database with results
    # 5. Send notifications
    
    # Mock test execution
    await asyncio.sleep(30)  # Simulate test execution time
    logger.info(f"Tests completed for project {project_id}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083) 