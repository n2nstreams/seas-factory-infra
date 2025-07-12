#!/usr/bin/env python3
"""
Unit tests for ReviewAgent - Night 37 Implementation
Tests the ReviewAgent's capability to run pytest and provide feedback loops
"""

import pytest
import asyncio
import tempfile
import shutil
import os
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from review_agent import (
    ReviewAgent, CodeReviewRequest, GeneratedCodeFile, 
    TenantContext, CodeReviewResult, PyTestResults, TestResult,
    CloudBuildResult, ReviewFeedback
)

# Test data
SAMPLE_PYTHON_CODE = '''
def add(a, b):
    """Add two numbers"""
    return a + b

def divide(a, b):
    """Divide two numbers"""
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b
'''

SAMPLE_TEST_CODE = '''
import pytest
from main import add, divide

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_divide():
    assert divide(6, 2) == 3
    with pytest.raises(ZeroDivisionError):
        divide(5, 0)
'''

SAMPLE_BAD_CODE = '''
def broken_function(:  # Syntax error
    return "broken"
'''

class TestReviewAgent:
    """Test suite for ReviewAgent functionality"""

    @pytest.fixture
    def review_agent(self):
        """Create ReviewAgent instance for testing"""
        return ReviewAgent()

    @pytest.fixture
    def tenant_context(self):
        """Create test tenant context"""
        return TenantContext(tenant_id="test-tenant", user_id="test-user")

    @pytest.fixture
    def sample_generated_files(self):
        """Create sample generated files for testing"""
        return [
            GeneratedCodeFile(
                filename="main.py",
                content=SAMPLE_PYTHON_CODE,
                file_type="source",
                language="python",
                size_bytes=len(SAMPLE_PYTHON_CODE),
                functions=["add", "divide"],
                imports=[]
            ),
            GeneratedCodeFile(
                filename="test_main.py",
                content=SAMPLE_TEST_CODE,
                file_type="test",
                language="python",
                size_bytes=len(SAMPLE_TEST_CODE),
                functions=["test_add", "test_divide"],
                imports=["pytest", "main"]
            )
        ]

    @pytest.fixture
    def code_review_request(self, sample_generated_files):
        """Create code review request for testing"""
        return CodeReviewRequest(
            project_id="test-project",
            module_name="TestModule",
            generated_files=sample_generated_files,
            dev_agent_request_id="test-request-123",
            review_type="full"
        )

    def test_review_agent_initialization(self, review_agent):
        """Test ReviewAgent initialization"""
        assert review_agent is not None
        assert hasattr(review_agent, 'tenant_db')
        assert hasattr(review_agent, 'dev_agent_url')
        assert hasattr(review_agent, 'max_retry_attempts')

    @pytest.mark.asyncio
    async def test_setup_test_workspace(self, review_agent, sample_generated_files):
        """Test test workspace setup"""
        workspace_dir = await review_agent.setup_test_workspace(sample_generated_files)
        
        try:
            workspace_path = Path(workspace_dir)
            assert workspace_path.exists()
            assert (workspace_path / "src").exists()
            assert (workspace_path / "tests").exists()
            assert (workspace_path / "src" / "main.py").exists()
            assert (workspace_path / "tests" / "test_main.py").exists()
            assert (workspace_path / "requirements.txt").exists()
            assert (workspace_path / "pytest.ini").exists()
            
            # Verify file contents
            with open(workspace_path / "src" / "main.py") as f:
                content = f.read()
                assert "def add(a, b):" in content
                assert "def divide(a, b):" in content
                
        finally:
            shutil.rmtree(workspace_dir, ignore_errors=True)

    def test_parse_pytest_output(self, review_agent):
        """Test pytest output parsing"""
        # Sample pytest output
        output = """
======================== test session starts ========================
collected 2 items

test_main.py::test_add PASSED                                    [ 50%]
test_main.py::test_divide FAILED                                 [100%]

======================== FAILURES ========================
FAILED test_main.py::test_divide - assert divide(10, 0) == 5
E       ZeroDivisionError: Cannot divide by zero

======================== short test summary info ========================
FAILED test_main.py::test_divide - ZeroDivisionError: Cannot divide by zero
======================== 1 failed, 1 passed in 0.12s ========================
"""
        
        error_output = ""
        exit_code = 1
        
        results = review_agent.parse_pytest_output(output, error_output, exit_code)
        
        assert results.total_tests == 2
        assert results.passed == 1
        assert results.failed == 1
        assert results.exit_code == 1
        assert len(results.test_results) == 2
        
        # Check individual test results
        passed_test = next(t for t in results.test_results if t.status == "passed")
        assert passed_test.test_name == "test_add"
        
        failed_test = next(t for t in results.test_results if t.status == "failed")
        assert failed_test.test_name == "test_divide"

    @pytest.mark.asyncio
    async def test_run_pytest_locally_success(self, review_agent):
        """Test successful local pytest execution"""
        # Create temporary workspace with valid code
        workspace_dir = tempfile.mkdtemp()
        try:
            # Create valid Python files
            src_dir = Path(workspace_dir) / "src"
            tests_dir = Path(workspace_dir) / "tests"
            src_dir.mkdir()
            tests_dir.mkdir()
            
            # Write main module
            with open(src_dir / "main.py", "w") as f:
                f.write(SAMPLE_PYTHON_CODE)
            
            # Write test file
            with open(tests_dir / "test_main.py", "w") as f:
                f.write(SAMPLE_TEST_CODE)
            
            # Write requirements
            with open(Path(workspace_dir) / "requirements.txt", "w") as f:
                f.write("pytest>=7.0.0\n")
            
            # Mock subprocess.run to simulate successful pytest
            with patch('review_agent.subprocess.run') as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "2 passed in 0.12s"
                mock_run.return_value.stderr = ""
                
                results = await review_agent.run_pytest_locally(workspace_dir)
                
                assert results.exit_code == 0
                mock_run.assert_called()
                
        finally:
            shutil.rmtree(workspace_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_run_pytest_locally_failure(self, review_agent):
        """Test local pytest execution with failures"""
        workspace_dir = tempfile.mkdtemp()
        try:
            # Create workspace with syntax error
            src_dir = Path(workspace_dir) / "src"
            src_dir.mkdir()
            
            # Write file with syntax error
            with open(src_dir / "broken.py", "w") as f:
                f.write(SAMPLE_BAD_CODE)
            
            # Write requirements
            with open(Path(workspace_dir) / "requirements.txt", "w") as f:
                f.write("pytest>=7.0.0\n")
            
            # Mock subprocess.run to simulate pytest failure
            with patch('review_agent.subprocess.run') as mock_run:
                mock_run.side_effect = [
                    MagicMock(returncode=0),  # pip install
                    MagicMock(returncode=1, stdout="", stderr="SyntaxError")  # pytest
                ]
                
                results = await review_agent.run_pytest_locally(workspace_dir)
                
                assert results.exit_code == 1
                assert results.errors > 0
                
        finally:
            shutil.rmtree(workspace_dir, ignore_errors=True)

    def test_analyze_test_failures(self, review_agent):
        """Test test failure analysis"""
        pytest_results = PyTestResults(
            total_tests=3,
            passed=1,
            failed=2,
            skipped=0,
            errors=0,
            coverage_percentage=60.0,
            duration=5.0,
            test_results=[
                TestResult(
                    test_name="test_add",
                    status="passed",
                    duration=1.0
                ),
                TestResult(
                    test_name="test_divide",
                    status="failed",
                    duration=2.0,
                    error_message="AssertionError: Expected 5 but got 3"
                ),
                TestResult(
                    test_name="test_import",
                    status="failed",
                    duration=1.0,
                    error_message="ImportError: No module named 'missing_module'"
                )
            ],
            exit_code=1,
            output="",
            error_output=""
        )
        
        issues = review_agent.analyze_test_failures(pytest_results)
        
        assert len(issues) == 3  # 2 test failures + 1 coverage issue
        assert any("assertion failure" in issue.lower() for issue in issues)
        assert any("import error" in issue.lower() for issue in issues)
        assert any("low test coverage" in issue.lower() for issue in issues)

    def test_generate_improvement_suggestions(self, review_agent):
        """Test improvement suggestion generation"""
        issues = [
            "Assertion failure in test_calculate: Expected 10 but got 8",
            "Import error in test_module: Missing dependency",
            "Type error in test_function: Incorrect argument types",
            "Low test coverage: 45% (target: 70%+)"
        ]
        
        pytest_results = PyTestResults(
            total_tests=4,
            passed=1,
            failed=3,
            skipped=0,
            errors=0,
            coverage_percentage=45.0,
            duration=30.0,
            test_results=[],
            exit_code=1,
            output="",
            error_output=""
        )
        
        suggestions = review_agent.generate_improvement_suggestions(issues, pytest_results)
        
        assert len(suggestions) > 0
        assert any("assertion logic" in suggestion.lower() for suggestion in suggestions)
        assert any("import statements" in suggestion.lower() for suggestion in suggestions)
        assert any("type hints" in suggestion.lower() for suggestion in suggestions)
        assert any("test coverage" in suggestion.lower() for suggestion in suggestions)

    @pytest.mark.asyncio
    async def test_send_feedback_to_dev_agent(self, review_agent):
        """Test feedback sending to DevAgent"""
        feedback = ReviewFeedback(
            review_passed=False,
            issues_found=["Test failure in calculator"],
            test_failures=[],
            suggestions=["Add error handling"],
            code_quality_score=65.0,
            retry_recommended=True
        )
        
        # Mock httpx client
        with patch('review_agent.httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            result = await review_agent.send_feedback_to_dev_agent(feedback, "test-request-123")
            
            assert result is True
            mock_client.return_value.__aenter__.return_value.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_feedback_failure(self, review_agent):
        """Test feedback sending failure handling"""
        feedback = ReviewFeedback(
            review_passed=False,
            issues_found=["Test failure"],
            test_failures=[],
            suggestions=["Fix issues"],
            code_quality_score=50.0,
            retry_recommended=True
        )
        
        # Mock httpx client with failure
        with patch('review_agent.httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            result = await review_agent.send_feedback_to_dev_agent(feedback, "test-request-123")
            
            assert result is False

    @pytest.mark.asyncio
    @patch('review_agent.ReviewAgent.tenant_db')
    async def test_review_generated_code_success(self, mock_db, review_agent, code_review_request, tenant_context):
        """Test successful code review flow"""
        # Mock database operations
        mock_db.log_agent_event = AsyncMock()
        
        # Mock pytest execution
        with patch.object(review_agent, 'run_pytest_locally') as mock_pytest:
            mock_pytest.return_value = PyTestResults(
                total_tests=2,
                passed=2,
                failed=0,
                skipped=0,
                errors=0,
                coverage_percentage=85.0,
                duration=3.0,
                test_results=[
                    TestResult(test_name="test_add", status="passed", duration=1.0),
                    TestResult(test_name="test_divide", status="passed", duration=2.0)
                ],
                exit_code=0,
                output="2 passed",
                error_output=""
            )
            
            result = await review_agent.review_generated_code(code_review_request, tenant_context)
            
            assert result.review_status == "passed"
            assert result.feedback.review_passed is True
            assert result.feedback.code_quality_score > 70
            assert len(result.feedback.issues_found) == 0
            
            # Verify database logging
            assert mock_db.log_agent_event.call_count >= 2

    @pytest.mark.asyncio
    @patch('review_agent.ReviewAgent.tenant_db')
    async def test_review_generated_code_failure(self, mock_db, review_agent, code_review_request, tenant_context):
        """Test code review with test failures"""
        # Mock database operations
        mock_db.log_agent_event = AsyncMock()
        
        # Mock pytest execution with failures
        with patch.object(review_agent, 'run_pytest_locally') as mock_pytest:
            mock_pytest.return_value = PyTestResults(
                total_tests=2,
                passed=1,
                failed=1,
                skipped=0,
                errors=0,
                coverage_percentage=45.0,
                duration=5.0,
                test_results=[
                    TestResult(test_name="test_add", status="passed", duration=1.0),
                    TestResult(test_name="test_divide", status="failed", duration=2.0, 
                              error_message="AssertionError: Test failed")
                ],
                exit_code=1,
                output="1 passed, 1 failed",
                error_output=""
            )
            
            # Mock feedback sending
            with patch.object(review_agent, 'send_feedback_to_dev_agent') as mock_feedback:
                mock_feedback.return_value = True
                
                result = await review_agent.review_generated_code(code_review_request, tenant_context)
                
                assert result.review_status == "failed"
                assert result.feedback.review_passed is False
                assert result.feedback.code_quality_score < 70
                assert len(result.feedback.issues_found) > 0
                assert len(result.feedback.test_failures) > 0
                
                # Verify feedback was sent
                mock_feedback.assert_called_once()

    @pytest.mark.asyncio
    async def test_cloud_build_integration_available(self, review_agent):
        """Test Cloud Build integration when available"""
        try:
            from cloud_build_integration import create_cloud_build_manager
            
            manager = create_cloud_build_manager()
            
            if manager:
                # Test manager initialization
                assert hasattr(manager, 'project_id')
                assert hasattr(manager, 'build_client')
                assert hasattr(manager, 'storage_client')
                
                # Test source archive creation
                workspace_dir = tempfile.mkdtemp()
                try:
                    # Create test files
                    (Path(workspace_dir) / "test.py").write_text("print('test')")
                    
                    archive_path = manager.create_source_archive(workspace_dir)
                    assert os.path.exists(archive_path)
                    assert archive_path.endswith('.zip')
                    
                    os.unlink(archive_path)
                    
                finally:
                    shutil.rmtree(workspace_dir, ignore_errors=True)
            else:
                pytest.skip("Google Cloud Build not available")
                
        except ImportError:
            pytest.skip("Cloud Build integration module not available")

    def test_model_validation(self):
        """Test pydantic model validation"""
        # Test CodeReviewRequest validation
        with pytest.raises(Exception):
            CodeReviewRequest(
                project_id="",  # Empty project ID should fail
                module_name="Test",
                generated_files=[]
            )
        
        # Test valid request
        valid_request = CodeReviewRequest(
            project_id="valid-project",
            module_name="TestModule",
            generated_files=[
                GeneratedCodeFile(
                    filename="test.py",
                    content="def test(): pass",
                    file_type="source",
                    language="python",
                    size_bytes=20
                )
            ]
        )
        assert valid_request.project_id == "valid-project"

    @pytest.mark.asyncio
    async def test_concurrent_reviews(self, review_agent, tenant_context):
        """Test handling of concurrent review requests"""
        # Create multiple review requests
        requests = []
        for i in range(3):
            files = [
                GeneratedCodeFile(
                    filename=f"module_{i}.py",
                    content=f"def function_{i}(): return {i}",
                    file_type="source",
                    language="python",
                    size_bytes=50
                )
            ]
            requests.append(CodeReviewRequest(
                project_id=f"project-{i}",
                module_name=f"Module{i}",
                generated_files=files
            ))
        
        # Mock pytest to return quickly
        with patch.object(review_agent, 'run_pytest_locally') as mock_pytest:
            mock_pytest.return_value = PyTestResults(
                total_tests=1, passed=1, failed=0, skipped=0, errors=0,
                coverage_percentage=80.0, duration=1.0, test_results=[],
                exit_code=0, output="", error_output=""
            )
            
            # Run reviews concurrently
            tasks = [
                review_agent.review_generated_code(req, tenant_context)
                for req in requests
            ]
            
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 3
            for result in results:
                assert isinstance(result, CodeReviewResult)
                assert result.review_status in ["passed", "failed", "error"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 