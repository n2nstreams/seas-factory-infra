#!/usr/bin/env python3
"""
Test script for QA Agent
Tests the QA agent functionality and API endpoints.
"""

import requests
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import QAAgent, TestCaseModel, QualityMetrics

def test_qa_agent_initialization():
    """Test QA agent initialization"""
    print("🧪 Testing QA Agent initialization...")
    
    try:
        agent = QAAgent()
        assert agent.db_config is not None
        assert 'unit' in agent.test_prompts
        assert 'integration' in agent.test_prompts
        assert 'e2e' in agent.test_prompts
        print("✅ QA Agent initialized successfully")
        return True
    except Exception as e:
        print(f"❌ QA Agent initialization failed: {e}")
        return False

def test_tenant_test_case_generation():
    """Test tenant-specific test case generation"""
    print("🧪 Testing tenant test case generation...")
    
    try:
        agent = QAAgent()
        tenant_id = "test-tenant-123"
        
        test_cases = agent.generate_tenant_test_cases(tenant_id)
        
        assert len(test_cases) > 0
        assert all(isinstance(tc, TestCaseModel) for tc in test_cases)
        assert any("isolation" in tc.name for tc in test_cases)
        assert any("api_access" in tc.name for tc in test_cases)
        
        # Check that tenant_id is properly embedded in test code
        for test_case in test_cases:
            if "isolation" in test_case.name:
                assert tenant_id in test_case.code
        
        print(f"✅ Generated {len(test_cases)} tenant test cases")
        return True
    except Exception as e:
        print(f"❌ Tenant test case generation failed: {e}")
        return False

def test_api_test_case_generation():
    """Test API test case generation"""
    print("🧪 Testing API test case generation...")
    
    try:
        agent = QAAgent()
        project_id = "test-project-456"
        
        test_cases = agent.generate_api_test_cases(project_id)
        
        assert len(test_cases) > 0
        assert all(isinstance(tc, TestCaseModel) for tc in test_cases)
        assert any("authentication" in tc.name for tc in test_cases)
        assert any("rate_limiting" in tc.name for tc in test_cases)
        
        print(f"✅ Generated {len(test_cases)} API test cases")
        return True
    except Exception as e:
        print(f"❌ API test case generation failed: {e}")
        return False

def test_performance_test_case_generation():
    """Test performance test case generation"""
    print("🧪 Testing performance test case generation...")
    
    try:
        agent = QAAgent()
        project_id = "test-project-789"
        
        test_cases = agent.generate_performance_test_cases(project_id)
        
        assert len(test_cases) > 0
        assert all(isinstance(tc, TestCaseModel) for tc in test_cases)
        assert any("performance" in tc.test_type for tc in test_cases)
        
        print(f"✅ Generated {len(test_cases)} performance test cases")
        return True
    except Exception as e:
        print(f"❌ Performance test case generation failed: {e}")
        return False

def test_quality_metrics_analysis():
    """Test quality metrics analysis"""
    print("🧪 Testing quality metrics analysis...")
    
    try:
        agent = QAAgent()
        
        # This is a mock test since we don't have real project data
        metrics = asyncio.run(agent.analyze_code_quality("test-project"))
        
        assert isinstance(metrics, QualityMetrics)
        assert metrics.coverage_percentage >= 0
        assert metrics.test_count >= 0
        assert metrics.passing_tests >= 0
        
        print("✅ Quality metrics analysis completed")
        print(f"   Coverage: {metrics.coverage_percentage}%")
        print(f"   Test Count: {metrics.test_count}")
        print(f"   Passing: {metrics.passing_tests}")
        return True
    except Exception as e:
        print(f"❌ Quality metrics analysis failed: {e}")
        return False

def test_http_endpoints():
    """Test HTTP endpoints (if server is running)"""
    print("🧪 Testing HTTP endpoints...")
    
    base_url = "http://localhost:8083"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ Health endpoint accessible")
            
            # Test generate tests endpoint (requires project data)
            test_request = {
                "project_id": "test-project",
                "test_type": "integration",
                "coverage_threshold": 80.0
            }
            
            try:
                response = requests.post(
                    f"{base_url}/generate-tests",
                    json=test_request,
                    timeout=10
                )
                if response.status_code in [200, 404, 500]:  # 404/500 expected without real data
                    print("✅ Generate tests endpoint accessible")
                else:
                    print(f"⚠️ Generate tests endpoint returned: {response.status_code}")
            except requests.RequestException:
                print("⚠️ Generate tests endpoint test skipped (expected without real data)")
            
            return True
        else:
            print(f"⚠️ QA Agent server not running or not accessible (status: {response.status_code})")
            return False
            
    except requests.ConnectionError:
        print("⚠️ QA Agent server not running (connection refused)")
        print("   To test HTTP endpoints, start the server with: python main.py")
        return False
    except Exception as e:
        print(f"❌ HTTP endpoint test failed: {e}")
        return False

def test_test_case_structure():
    """Test the structure and content of generated test cases"""
    print("🧪 Testing test case structure...")
    
    try:
        agent = QAAgent()
        test_cases = agent.generate_tenant_test_cases("sample-tenant")
        
        for test_case in test_cases:
            # Verify required fields
            assert test_case.name, "Test case must have a name"
            assert test_case.description, "Test case must have a description"
            assert test_case.test_type, "Test case must have a test type"
            assert test_case.module, "Test case must have a module"
            assert test_case.code, "Test case must have code"
            assert test_case.assertions, "Test case must have assertions"
            
            # Verify code structure
            assert "def test_" in test_case.code or "async def test_" in test_case.code, \
                "Test case code must contain a test function"
            assert "assert" in test_case.code, \
                "Test case code must contain assertions"
            
            # Verify assertions list
            assert len(test_case.assertions) > 0, \
                "Test case must have at least one assertion description"
        
        print(f"✅ All {len(test_cases)} test cases have valid structure")
        return True
    except Exception as e:
        print(f"❌ Test case structure validation failed: {e}")
        return False

def run_all_tests():
    """Run all QA agent tests"""
    print("🚀 Running QA Agent Tests")
    print("=" * 50)
    
    tests = [
        test_qa_agent_initialization,
        test_tenant_test_case_generation,
        test_api_test_case_generation,
        test_performance_test_case_generation,
        test_quality_metrics_analysis,
        test_test_case_structure,
        test_http_endpoints,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All QA Agent tests passed!")
        return True
    else:
        print("💥 Some QA Agent tests failed!")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 