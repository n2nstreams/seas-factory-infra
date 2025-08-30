#!/usr/bin/env python3
"""
ReviewAgent Demo - Night 37 Implementation
Demonstrates the ReviewAgent's capabilities for running pytest in Cloud Build
and providing feedback loops to DevAgent
"""

import asyncio
from review_agent import (
    ReviewAgent, CodeReviewRequest, GeneratedCodeFile, 
    TenantContext
)

async def demo_basic_code_review():
    """Demo: Basic code review with pytest execution"""
    print("🔍 Demo: Basic Code Review with Pytest")
    print("=" * 50)
    
    # Create ReviewAgent instance
    review_agent = ReviewAgent()
    
    # Sample generated code from DevAgent (with intentional issues for demo)
    generated_files = [
        GeneratedCodeFile(
            filename="calculator.py",
            content='''
def add(a, b):
    """Add two numbers"""
    return a + b

def divide(a, b):
    """Divide two numbers"""
    return a / b  # Potential division by zero

def multiply(a, b):
    """Multiply two numbers"""
    return a * b

class Calculator:
    """Simple calculator class"""
    
    def __init__(self):
        self.history = []
    
    def calculate(self, operation, a, b):
        """Perform calculation"""
        if operation == "add":
            result = add(a, b)
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = multiply(a, b)
        elif operation == "divide":
            result = divide(a, b)
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        self.history.append((operation, a, b, result))
        return result
''',
            file_type="source",
            language="python",
            size_bytes=800,
            functions=["add", "divide", "multiply", "Calculator"],
            imports=[]
        ),
        GeneratedCodeFile(
            filename="test_calculator.py",
            content='''
import pytest
from calculator import add, divide, multiply, Calculator

def test_add():
    """Test addition function"""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

def test_multiply():
    """Test multiplication function"""
    assert multiply(2, 3) == 6
    assert multiply(-1, 5) == -5
    assert multiply(0, 10) == 0

def test_divide():
    """Test division function"""
    assert divide(6, 2) == 3
    assert divide(10, 5) == 2
    
    # This test should fail if division by zero handling is missing
    with pytest.raises(ZeroDivisionError):
        divide(5, 0)

def test_calculator_class():
    """Test Calculator class"""
    calc = Calculator()
    
    # Test basic operations
    assert calc.calculate("add", 2, 3) == 5
    assert calc.calculate("multiply", 4, 5) == 20
    
    # Test history tracking
    assert len(calc.history) == 2
    
    # Test invalid operation
    with pytest.raises(ValueError):
        calc.calculate("invalid", 1, 2)

def test_calculator_edge_cases():
    """Test edge cases"""
    calc = Calculator()
    
    # Test with negative numbers
    assert calc.calculate("subtract", 10, 15) == -5
    
    # Test division by zero should be handled
    with pytest.raises(ZeroDivisionError):
        calc.calculate("divide", 10, 0)
''',
            file_type="test",
            language="python",
            size_bytes=1200,
            functions=["test_add", "test_multiply", "test_divide", "test_calculator_class", "test_calculator_edge_cases"],
            imports=["pytest", "calculator"]
        )
    ]
    
    # Create review request
    review_request = CodeReviewRequest(
        project_id="demo-calculator-project",
        module_name="Calculator",
        generated_files=generated_files,
        dev_agent_request_id="dev-req-123",
        review_type="full"
    )
    
    # Create tenant context
    tenant_context = TenantContext(tenant_id="demo-tenant", user_id="demo-user")
    
    try:
        # Perform code review
        print("🔧 Starting code review with pytest execution...")
        result = await review_agent.review_generated_code(review_request, tenant_context)
        
        print("✅ Code review completed!")
        print(f"📊 Review ID: {result.review_id}")
        print(f"📈 Review Status: {result.review_status}")
        print(f"⏱️  Duration: {result.review_duration:.2f} seconds")
        print(f"🎯 Quality Score: {result.feedback.code_quality_score:.1f}/100")
        
        # Display test results
        if result.cloud_build_result and result.cloud_build_result.pytest_results:
            pytest_results = result.cloud_build_result.pytest_results
            print("\n🧪 Test Results:")
            print(f"  Total tests: {pytest_results.total_tests}")
            print(f"  Passed: {pytest_results.passed}")
            print(f"  Failed: {pytest_results.failed}")
            print(f"  Errors: {pytest_results.errors}")
            print(f"  Coverage: {pytest_results.coverage_percentage or 'N/A'}%")
        
        # Display issues found
        if result.feedback.issues_found:
            print(f"\n⚠️  Issues Found ({len(result.feedback.issues_found)}):")
            for i, issue in enumerate(result.feedback.issues_found[:5], 1):
                print(f"  {i}. {issue}")
        
        # Display suggestions
        if result.feedback.suggestions:
            print(f"\n💡 Suggestions ({len(result.feedback.suggestions)}):")
            for i, suggestion in enumerate(result.feedback.suggestions[:3], 1):
                print(f"  {i}. {suggestion}")
        
        # Display failed tests
        if result.feedback.test_failures:
            print(f"\n❌ Failed Tests ({len(result.feedback.test_failures)}):")
            for test in result.feedback.test_failures[:3]:
                print(f"  - {test.test_name}: {test.error_message or 'Unknown error'}")
        
        return result
        
    except Exception as e:
        print(f"❌ Code review failed: {e}")
        return None

async def demo_feedback_loop():
    """Demo: Complete feedback loop with DevAgent"""
    print("\n🔄 Demo: Feedback Loop with DevAgent")
    print("=" * 50)
    
    # This would normally be triggered by a failed review
    # For demo purposes, we simulate the feedback process
    
    print("📤 Simulating feedback to DevAgent...")
    
    feedback_data = {
        "request_id": "dev-req-123",
        "review_passed": False,
        "issues": [
            "Division by zero not handled in divide function",
            "Missing error handling for edge cases",
            "Test coverage below 70% threshold"
        ],
        "suggestions": [
            "Add proper exception handling for division by zero",
            "Include input validation for numeric types",
            "Add more comprehensive test cases for edge scenarios"
        ],
        "code_quality_score": 65.5,
        "retry_recommended": True
    }
    
    print("📋 Feedback being sent:")
    print(f"  Review Passed: {feedback_data['review_passed']}")
    print(f"  Quality Score: {feedback_data['code_quality_score']}")
    print(f"  Issues: {len(feedback_data['issues'])}")
    print(f"  Suggestions: {len(feedback_data['suggestions'])}")
    
    # In a real implementation, this would make an HTTP request to DevAgent
    print("🔄 DevAgent would receive this feedback and:")
    print("  1. Analyze the issues and suggestions")
    print("  2. Modify the code generation prompts")
    print("  3. Regenerate improved code")
    print("  4. Send back to ReviewAgent for re-review")
    
    print("✅ Feedback loop demonstrated!")

async def demo_cloud_build_integration():
    """Demo: Cloud Build integration (if available)"""
    print("\n☁️  Demo: Cloud Build Integration")
    print("=" * 50)
    
    try:
        from cloud_build_integration import create_cloud_build_manager
        
        cloud_build_manager = create_cloud_build_manager()
        
        if cloud_build_manager:
            print("✅ Google Cloud Build integration available")
            print("🏗️  Cloud Build would:")
            print("  1. Package source code into archive")
            print("  2. Upload to Google Cloud Storage")
            print("  3. Submit build job to Cloud Build")
            print("  4. Execute pytest in containerized environment")
            print("  5. Generate test reports and coverage")
            print("  6. Store artifacts in Cloud Storage")
            print("  7. Stream logs back to ReviewAgent")
        else:
            print("⚠️  Google Cloud Build integration not available")
            print("🔄 Falling back to local pytest execution")
            
    except ImportError:
        print("📦 Cloud Build module not found, using local execution")

async def demo_advanced_scenarios():
    """Demo: Advanced review scenarios"""
    print("\n🎯 Demo: Advanced Review Scenarios")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "Syntax Error Detection",
            "description": "Code with Python syntax errors",
            "expected": "Should catch syntax errors before test execution"
        },
        {
            "name": "Import Error Handling", 
            "description": "Missing dependencies or incorrect imports",
            "expected": "Should identify missing packages and suggest fixes"
        },
        {
            "name": "Performance Test Integration",
            "description": "Code with performance benchmarks",
            "expected": "Should run performance tests and validate against thresholds"
        },
        {
            "name": "Security Vulnerability Scan",
            "description": "Code with potential security issues",
            "expected": "Should identify security vulnerabilities (future enhancement)"
        },
        {
            "name": "Multi-Language Support",
            "description": "JavaScript/TypeScript code review",
            "expected": "Should support Jest/Vitest for JS testing (future enhancement)"
        }
    ]
    
    print("🔮 Advanced scenarios (roadmap):")
    for i, scenario in enumerate(scenarios, 1):
        print(f"  {i}. {scenario['name']}")
        print(f"     {scenario['description']}")
        print(f"     Expected: {scenario['expected']}")
        print()

async def demo_metrics_and_reporting():
    """Demo: Metrics and reporting capabilities"""
    print("\n📊 Demo: Metrics and Reporting")
    print("=" * 50)
    
    # Sample metrics that ReviewAgent would track
    metrics = {
        "reviews_completed": 42,
        "average_quality_score": 78.5,
        "pass_rate": 0.73,
        "average_review_duration": 45.2,
        "total_issues_found": 156,
        "most_common_issues": [
            "Missing type hints (23%)",
            "Insufficient test coverage (18%)",
            "Import errors (15%)",
            "Assertion failures (12%)",
            "Performance issues (8%)"
        ],
        "retry_rate": 0.27,
        "cloud_build_usage": 0.85
    }
    
    print("📈 ReviewAgent Metrics (sample):")
    print(f"  Total Reviews: {metrics['reviews_completed']}")
    print(f"  Average Quality Score: {metrics['average_quality_score']}/100")
    print(f"  Pass Rate: {metrics['pass_rate']:.1%}")
    print(f"  Average Duration: {metrics['average_review_duration']}s")
    print(f"  Retry Rate: {metrics['retry_rate']:.1%}")
    
    print("\n🔍 Most Common Issues:")
    for issue in metrics['most_common_issues']:
        print(f"    - {issue}")
    
    print(f"\n☁️  Cloud Build Usage: {metrics['cloud_build_usage']:.1%}")

async def main():
    """Run all ReviewAgent demos"""
    print("🎯 ReviewAgent Demo - Night 37 Implementation")
    print("=" * 60)
    print("This demo shows the ReviewAgent's capability to run pytest in Cloud Build")
    print("and provide feedback loops back to DevAgent on test failures.")
    print()
    
    # Run demos
    result = await demo_basic_code_review()
    await demo_feedback_loop()
    await demo_cloud_build_integration()
    await demo_advanced_scenarios()
    await demo_metrics_and_reporting()
    
    print("\n🎉 Demo completed!")
    print("📚 The ReviewAgent can:")
    print("  ✅ Execute pytest in Cloud Build or locally")
    print("  ✅ Parse test results and generate quality metrics")
    print("  ✅ Identify common code issues and failures")
    print("  ✅ Provide actionable feedback and suggestions")
    print("  ✅ Loop back to DevAgent for code improvements")
    print("  ✅ Track review history and metrics")
    print("  ✅ Integrate with tenant database for multi-tenancy")
    print()
    print("💡 Next steps:")
    print("  1. Start the ReviewAgent server: python review_agent.py")
    print("  2. Configure Google Cloud Build credentials")
    print("  3. Integrate with orchestrator for complete workflow")
    print("  4. Set up monitoring and alerting for review failures")

if __name__ == "__main__":
    asyncio.run(main()) 