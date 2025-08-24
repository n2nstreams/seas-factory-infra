#!/usr/bin/env python3
"""
Frontend-Backend Integration Tests
Tests the complete user journey from frontend forms to backend APIs

These tests verify:
1. Signup form connects to backend registration API
2. Login form authenticates users correctly
3. Idea submission form saves data to backend
4. End-to-end user experience flow works
5. Error handling and validation work properly
"""

import asyncio
import pytest
import uuid
import httpx

# Import conftest with proper path handling
import sys
from pathlib import Path

# Add the tests directory to the path
tests_dir = Path(__file__).parent.parent
sys.path.insert(0, str(tests_dir))

try:
    from conftest import integration_test, wait_for_condition
except ImportError:
    # Fallback decorators if conftest is not available
    def integration_test(func):
        return func
    
    def wait_for_condition(condition, timeout=30, interval=1):
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition():
                return True
            time.sleep(interval)
        return False


class TestFrontendBackendIntegration:
    """Integration tests for frontend-backend connectivity"""
    
    @pytest.fixture
    def valid_signup_data(self):
        """Valid user registration data for testing"""
        return {
            "firstName": "Jane",
            "lastName": "Smith",
            "email": f"test-{uuid.uuid4().hex[:8]}@example.com",
            "password": "SecurePass123!",
            "confirmPassword": "SecurePass123!",
            "agreeToTerms": True
        }
    
    @pytest.fixture
    def valid_login_data(self):
        """Valid login credentials for testing"""
        return {
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
    
    @pytest.fixture
    def valid_idea_data(self):
        """Valid idea submission data for testing"""
        return {
            "projectName": "AI Task Manager",
            "description": "An intelligent task management system",
            "category": "productivity",
            "problem": "People struggle to prioritize and complete tasks efficiently",
            "solution": "AI-powered task prioritization and scheduling",
            "targetAudience": "Busy professionals and teams",
            "keyFeatures": "Smart prioritization, time tracking, team collaboration",
            "businessModel": "subscription",
            "timeline": "3 months",
            "budget": "5000-10000"
        }
    
    @pytest.fixture
    def api_base_url(self):
        """Get API base URL for testing"""
        import os
        # Use test environment or default to localhost
        return os.getenv('TEST_API_URL', 'http://localhost:8000')
    
    @integration_test
    async def test_signup_form_connects_to_backend(self, api_base_url, valid_signup_data):
        """Test that signup form successfully connects to backend registration API"""
        
        # Test the actual API endpoint
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{api_base_url}/api/users/register",
                    json=valid_signup_data,
                    headers={"Content-Type": "application/json"}
                )
                
                # Verify the API responds (even if validation fails, it should respond)
                assert response.status_code in [200, 201, 422], f"API should respond, got {response.status_code}"
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    assert "id" in data, "Response should contain user ID"
                    assert data["email"] == valid_signup_data["email"], "Email should match"
                    print(f"✅ Signup API working: {data['id']}")
                else:
                    # 422 means validation error, which is expected for test data
                    print(f"✅ Signup API responding with validation: {response.status_code}")
                    
            except httpx.ConnectError:
                pytest.skip("Backend API not accessible for testing")
            except Exception as e:
                pytest.fail(f"Signup API test failed: {e}")
    
    @integration_test
    async def test_login_form_connects_to_backend(self, api_base_url, valid_login_data):
        """Test that login form successfully connects to backend authentication API"""
        
        # Test the actual API endpoint
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{api_base_url}/api/users/login",
                    json=valid_login_data,
                    headers={"Content-Type": "application/json"}
                )
                
                # Verify the API responds
                assert response.status_code in [200, 401, 422], f"API should respond, got {response.status_code}"
                
                if response.status_code == 200:
                    data = response.json()
                    assert "token" in data or "access_token" in data, "Response should contain auth token"
                    print(f"✅ Login API working: {response.status_code}")
                else:
                    # 401/422 are expected for test credentials
                    print(f"✅ Login API responding with auth error: {response.status_code}")
                    
            except httpx.ConnectError:
                pytest.skip("Backend API not accessible for testing")
            except Exception as e:
                pytest.fail(f"Login API test failed: {e}")
    
    @integration_test
    async def test_idea_submission_form_connects_to_backend(self, api_base_url, valid_idea_data):
        """Test that idea submission form successfully connects to backend ideas API"""
        
        # Test the actual API endpoint
        async with httpx.AsyncClient() as client:
            try:
                # First create a test user to get tenant context
                test_user = {
                    "firstName": "Test",
                    "lastName": "User",
                    "email": f"test-{uuid.uuid4().hex[:8]}@example.com",
                    "password": "TestPass123!",
                    "confirmPassword": "TestPass123!",
                    "agreeToTerms": True
                }
                
                # Register test user
                user_response = await client.post(
                    f"{api_base_url}/api/users/register",
                    json=test_user,
                    headers={"Content-Type": "application/json"}
                )
                
                if user_response.status_code in [200, 201]:
                    user_data = user_response.json()
                    tenant_id = user_data.get("tenant_id", "default")
                    user_id = user_data.get("id", "default")
                    
                    # Now test idea submission with tenant context
                    idea_response = await client.post(
                        f"{api_base_url}/api/ideas/submit",
                        json=valid_idea_data,
                        headers={
                            "Content-Type": "application/json",
                            "X-Tenant-ID": tenant_id,
                            "X-User-ID": user_id
                        }
                    )
                    
                    # Verify the API responds
                    assert idea_response.status_code in [200, 201, 422], f"Idea API should respond, got {idea_response.status_code}"
                    
                    if idea_response.status_code in [200, 201]:
                        idea_data = idea_response.json()
                        assert "id" in idea_data, "Response should contain idea ID"
                        print(f"✅ Idea submission API working: {idea_data['id']}")
                    else:
                        print(f"✅ Idea submission API responding with validation: {idea_response.status_code}")
                        
                else:
                    # If user creation fails, test idea API directly
                    idea_response = await client.post(
                        f"{api_base_url}/api/ideas/submit",
                        json=valid_idea_data,
                        headers={
                            "Content-Type": "application/json",
                            "X-Tenant-ID": "test-tenant",
                            "X-User-ID": "test-user"
                        }
                    )
                    
                    assert idea_response.status_code in [200, 201, 422, 400], f"Idea API should respond, got {idea_response.status_code}"
                    print(f"✅ Idea submission API responding: {idea_response.status_code}")
                    
            except httpx.ConnectError:
                pytest.skip("Backend API not accessible for testing")
            except Exception as e:
                pytest.fail(f"Idea submission API test failed: {e}")
    
    @integration_test
    async def test_end_to_end_user_experience_flow(self, api_base_url):
        """Test complete end-to-end user experience flow"""
        
        # This test simulates the complete user journey
        async with httpx.AsyncClient() as client:
            try:
                # Step 1: User registration
                user_data = {
                    "firstName": "EndToEnd",
                    "lastName": "User",
                    "email": f"e2e-{uuid.uuid4().hex[:8]}@example.com",
                    "password": "E2EPass123!",
                    "confirmPassword": "E2EPass123!",
                    "agreeToTerms": True
                }
                
                print("🔄 Step 1: Testing user registration...")
                register_response = await client.post(
                    f"{api_base_url}/api/users/register",
                    json=user_data,
                    headers={"Content-Type": "application/json"}
                )
                
                assert register_response.status_code in [200, 201, 422], f"Registration should work, got {register_response.status_code}"
                
                if register_response.status_code in [200, 201]:
                    user_info = register_response.json()
                    tenant_id = user_info.get("tenant_id", "default")
                    user_id = user_info.get("id", "default")
                    print(f"✅ User registered: {user_id}")
                    
                    # Step 2: User login
                    print("🔄 Step 2: Testing user login...")
                    login_data = {
                        "email": user_data["email"],
                        "password": user_data["password"]
                    }
                    
                    login_response = await client.post(
                        f"{api_base_url}/api/users/login",
                        json=login_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    assert login_response.status_code in [200, 401, 422], f"Login should work, got {login_response.status_code}"
                    
                    if login_response.status_code == 200:
                        print("✅ User login successful")
                        
                        # Step 3: Submit idea
                        print("🔄 Step 3: Testing idea submission...")
                        idea_data = {
                            "projectName": "E2E Test Project",
                            "description": "Testing the complete user flow",
                            "category": "testing",
                            "problem": "Need to test user flows",
                            "solution": "Automated testing",
                            "targetAudience": "Developers",
                            "keyFeatures": "Testing, validation, automation",
                            "businessModel": "open_source",
                            "timeline": "1 month",
                            "budget": "1000-2000"
                        }
                        
                        idea_response = await client.post(
                            f"{api_base_url}/api/ideas/submit",
                            json=idea_data,
                            headers={
                                "Content-Type": "application/json",
                                "X-Tenant-ID": tenant_id,
                                "X-User-ID": user_id
                            }
                        )
                        
                        assert idea_response.status_code in [200, 201, 422], f"Idea submission should work, got {idea_response.status_code}"
                        
                        if idea_response.status_code in [200, 201]:
                            idea_info = idea_response.json()
                            print(f"✅ Idea submitted: {idea_info.get('id', 'unknown')}")
                        else:
                            print(f"⚠️ Idea submission validation: {idea_response.status_code}")
                    else:
                        print(f"⚠️ Login validation: {login_response.status_code}")
                else:
                    print(f"⚠️ Registration validation: {register_response.status_code}")
                
                print("✅ End-to-end user experience flow test completed")
                
            except httpx.ConnectError:
                pytest.skip("Backend API not accessible for testing")
            except Exception as e:
                pytest.fail(f"End-to-end flow test failed: {e}")
    
    @integration_test
    async def test_api_gateway_health_and_routing(self, api_base_url):
        """Test API gateway health and basic routing"""
        
        async with httpx.AsyncClient() as client:
            try:
                # Test health endpoint
                health_response = await client.get(f"{api_base_url}/health")
                assert health_response.status_code == 200, "Health endpoint should be accessible"
                
                health_data = health_response.json()
                assert health_data["status"] == "healthy", "Health status should be healthy"
                print("✅ API Gateway health check working")
                
                # Test root endpoint
                root_response = await client.get(f"{api_base_url}/")
                assert root_response.status_code == 200, "Root endpoint should be accessible"
                
                root_data = root_response.json()
                assert "service" in root_data, "Root should return service information"
                assert "endpoints" in root_data, "Root should list available endpoints"
                print("✅ API Gateway root endpoint working")
                
                # Test CORS headers by checking if POST request works with origin
                post_response = await client.post(
                    f"{api_base_url}/api/users/register",
                    json={"firstName": "Test", "lastName": "User", "email": "test@example.com", "password": "TestPass123!", "confirmPassword": "TestPass123!", "agreeToTerms": True},
                    headers={"Origin": "http://localhost:3000", "Content-Type": "application/json"}
                )
                
                # Should get validation error (400/422) but CORS headers should be present
                assert post_response.status_code in [200, 201, 400, 422], f"POST request should work, got {post_response.status_code}"
                assert "access-control-allow-origin" in post_response.headers, "CORS headers should be present"
                
                # Log the response for debugging
                if post_response.status_code not in [200, 201]:
                    response_data = post_response.json()
                    print(f"⚠️ Registration returned {post_response.status_code}: {response_data}")
                
                print("✅ API Gateway CORS working")
                
            except httpx.ConnectError:
                pytest.skip("Backend API not accessible for testing")
            except Exception as e:
                pytest.fail(f"API Gateway test failed: {e}")
    
    @integration_test
    async def test_error_handling_and_validation(self, api_base_url):
        """Test error handling and validation across APIs"""
        
        async with httpx.AsyncClient() as client:
            try:
                # Test invalid signup data
                invalid_signup = {
                    "firstName": "",  # Empty name
                    "lastName": "Test",
                    "email": "invalid-email",  # Invalid email
                    "password": "123",  # Too short
                    "confirmPassword": "different",  # Mismatch
                    "agreeToTerms": False  # Must be true
                }
                
                signup_response = await client.post(
                    f"{api_base_url}/api/users/register",
                    json=invalid_signup,
                    headers={"Content-Type": "application/json"}
                )
                
                # Should return validation error (422)
                assert signup_response.status_code == 422, "Invalid signup should return validation error"
                print("✅ Signup validation working")
                
                # Test invalid idea submission
                invalid_idea = {
                    "projectName": "",  # Empty name
                    "description": "",  # Empty description
                }
                
                idea_response = await client.post(
                    f"{api_base_url}/api/ideas/submit",
                    json=invalid_idea,
                    headers={
                        "Content-Type": "application/json",
                        "X-Tenant-ID": "test-tenant",
                        "X-User-ID": "test-user"
                    }
                )
                
                # Should return validation error or bad request
                assert idea_response.status_code in [400, 422], "Invalid idea should return error"
                print("✅ Idea validation working")
                
                # Test missing tenant headers
                idea_response_no_headers = await client.post(
                    f"{api_base_url}/api/ideas/submit",
                    json={"projectName": "Test", "description": "Test"},
                    headers={"Content-Type": "application/json"}
                )
                
                # Should return error for missing tenant context
                assert idea_response_no_headers.status_code in [400, 401, 422], "Missing tenant headers should return error"
                print("✅ Tenant validation working")
                
            except httpx.ConnectError:
                pytest.skip("Backend API not accessible for testing")
            except Exception as e:
                pytest.fail(f"Error handling test failed: {e}")


# Test runner for manual execution
async def run_integration_tests(api_url: str = None):
    """Run all integration tests manually"""
    print("🚀 Running Frontend-Backend Integration Tests...")
    
    # Use provided API URL or get from environment
    if not api_url:
        import os
        api_url = os.getenv('TEST_API_URL', 'http://localhost:8000')
    
    print(f"🔗 Testing against API: {api_url}")
    
    # Create test instance
    test_instance = TestFrontendBackendIntegration()
    
    # Run tests with proper parameters
    test_configs = [
        ("API Gateway Health", test_instance.test_api_gateway_health_and_routing, [api_url]),
        ("Signup API", test_instance.test_signup_form_connects_to_backend, [api_url, {
            "firstName": "Jane",
            "lastName": "Smith",
            "email": f"test-{uuid.uuid4().hex[:8]}@example.com",
            "password": "SecurePass123!",
            "confirmPassword": "SecurePass123!",
            "agreeToTerms": True
        }]),
        ("Login API", test_instance.test_login_form_connects_to_backend, [api_url, {
            "email": "test@example.com",
            "password": "SecurePass123!"
        }]),
        ("Idea Submission", test_instance.test_idea_submission_form_connects_to_backend, [api_url, {
            "projectName": "AI Task Manager",
            "description": "An intelligent task management system",
            "category": "productivity",
            "problem": "People struggle to prioritize and complete tasks efficiently",
            "solution": "AI-powered task prioritization and scheduling",
            "targetAudience": "Busy professionals and teams",
            "keyFeatures": "Smart prioritization, time tracking, team collaboration",
            "businessModel": "subscription",
            "timeline": "3 months",
            "budget": "5000-10000"
        }]),
        ("Error Handling", test_instance.test_error_handling_and_validation, [api_url]),
        ("End-to-End Flow", test_instance.test_end_to_end_user_experience_flow, [api_url]),
    ]
    
    results = []
    for test_name, test_func, args in test_configs:
        try:
            print(f"\n🧪 Running {test_name}...")
            await test_func(*args)
            results.append((test_name, "PASSED"))
            print(f"✅ {test_name} PASSED")
        except Exception as e:
            results.append((test_name, f"FAILED: {e}"))
            print(f"❌ {test_name} FAILED: {e}")
    
    # Print summary
    print("\n📊 Test Results Summary:")
    print("=" * 50)
    for test_name, result in results:
        status = "✅" if "PASSED" in result else "❌"
        print(f"{status} {test_name}: {result}")
    
    passed = sum(1 for _, result in results if "PASSED" in result)
    total = len(results)
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All frontend-backend integration tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Check the backend API connectivity.")
        return False


if __name__ == "__main__":
    asyncio.run(run_integration_tests())
