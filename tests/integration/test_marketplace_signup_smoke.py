#!/usr/bin/env python3
"""
Marketplace Signup Flow Smoke Tests - Night 76
Fast, essential tests for the critical path of user registration and marketplace onboarding

These tests verify:
1. User registration API functionality
2. Form validation and error handling
3. Database user creation
4. Authentication flow
5. Email service integration
6. GDPR compliance tracking
"""

import asyncio
import pytest
import uuid
import json
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from conftest import integration_test, wait_for_condition


class TestMarketplaceSignupFlow:
    """Smoke tests for marketplace signup flow"""
    
    @pytest.fixture
    def valid_user_data(self):
        """Valid user registration data for testing"""
        return {
            "firstName": "John",
            "lastName": "Doe", 
            "email": f"test-{uuid.uuid4().hex[:8]}@example.com",
            "password": "TestPassword123!",
            "confirmPassword": "TestPassword123!",
            "agreeToTerms": True,
            "gdprConsent": True
        }
    
    @pytest.fixture
    def invalid_user_data(self):
        """Invalid user registration data for testing validation"""
        return {
            "firstName": "",  # Invalid: empty
            "lastName": "Doe",
            "email": "invalid-email",  # Invalid: malformed
            "password": "weak",  # Invalid: too short
            "confirmPassword": "different",  # Invalid: doesn't match
            "agreeToTerms": False,  # Invalid: must be true
            "gdprConsent": False  # Invalid: must be true
        }
    
    @integration_test
    async def test_successful_user_registration(self, tenant_db, valid_user_data):
        """Test successful user registration flow"""
        
        # Import the registration function
        from api_gateway.user_routes import register_user, UserRegistrationRequest
        from fastapi import Request
        
        # Create mock request object
        mock_request = Mock(spec=Request)
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {"user-agent": "test-agent"}
        
        # Mock email service to avoid sending real emails
        with patch('api_gateway.user_routes.get_email_service') as mock_email_service:
            mock_email_instance = Mock()
            mock_email_instance.send_welcome_email = AsyncMock(return_value={"status": "sent"})
            mock_email_service.return_value = mock_email_instance
            
            # Execute registration
            registration_request = UserRegistrationRequest(**valid_user_data)
            result = await register_user(registration_request, mock_request)
            
            # Verify response structure
            assert result.email == valid_user_data["email"]
            assert result.name == f"{valid_user_data['firstName']} {valid_user_data['lastName']}"
            assert result.role == "user"
            assert result.status == "active"
            assert result.id is not None
            assert result.tenant_id is not None
            
            # Verify email service was called
            mock_email_instance.send_welcome_email.assert_called_once()
            
            print(f"✅ User registration successful: {result.id}")
    
    @integration_test
    async def test_registration_validation_errors(self, tenant_db, invalid_user_data):
        """Test registration validation catches invalid data"""
        
        from api_gateway.user_routes import UserRegistrationRequest
        from pydantic import ValidationError
        
        # Test individual validation failures
        with pytest.raises(ValidationError) as exc_info:
            UserRegistrationRequest(**invalid_user_data)
        
        errors = exc_info.value.errors()
        error_fields = [error['loc'][0] for error in errors]
        
        # Check that all expected validation errors are present
        expected_errors = ['firstName', 'email', 'password', 'confirmPassword', 'agreeToTerms', 'gdprConsent']
        
        for expected_field in expected_errors:
            assert expected_field in error_fields, f"Expected validation error for {expected_field}"
        
        print(f"✅ Validation errors caught correctly: {len(errors)} errors")
    
    @integration_test
    async def test_duplicate_email_registration(self, tenant_db, valid_user_data):
        """Test that duplicate email registration is rejected"""
        
        from api_gateway.user_routes import register_user, UserRegistrationRequest
        from fastapi import Request, HTTPException
        
        # Create mock request
        mock_request = Mock(spec=Request)
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {"user-agent": "test-agent"}
        
        with patch('api_gateway.user_routes.get_email_service') as mock_email_service:
            mock_email_instance = Mock()
            mock_email_instance.send_welcome_email = AsyncMock(return_value={"status": "sent"})
            mock_email_service.return_value = mock_email_instance
            
            # Register user first time
            registration_request = UserRegistrationRequest(**valid_user_data)
            first_result = await register_user(registration_request, mock_request)
            assert first_result is not None
            
            # Try to register same email again
            with pytest.raises(HTTPException) as exc_info:
                await register_user(registration_request, mock_request)
            
            assert exc_info.value.status_code == 400
            assert "already exists" in str(exc_info.value.detail)
            
            print("✅ Duplicate email registration correctly rejected")
    
    @integration_test
    async def test_user_login_after_registration(self, tenant_db, valid_user_data):
        """Test user can login after successful registration"""
        
        from api_gateway.user_routes import register_user, login_user, UserRegistrationRequest, UserLoginRequest
        from fastapi import Request
        
        # Register user first
        mock_request = Mock(spec=Request)
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {"user-agent": "test-agent"}
        
        with patch('api_gateway.user_routes.get_email_service') as mock_email_service:
            mock_email_instance = Mock()
            mock_email_instance.send_welcome_email = AsyncMock(return_value={"status": "sent"})
            mock_email_service.return_value = mock_email_instance
            
            # Register user
            registration_request = UserRegistrationRequest(**valid_user_data)
            registration_result = await register_user(registration_request, mock_request)
            
            # Login user
            login_request = UserLoginRequest(
                email=valid_user_data["email"],
                password=valid_user_data["password"]
            )
            
            login_result = await login_user(login_request)
            
            # Verify login response
            assert login_result["message"] == "Login successful"
            assert login_result["user"]["email"] == valid_user_data["email"]
            assert login_result["user"]["id"] == registration_result.id
            
            print("✅ User login after registration successful")
    
    @integration_test
    async def test_invalid_login_credentials(self, tenant_db, valid_user_data):
        """Test login with invalid credentials is rejected"""
        
        from api_gateway.user_routes import register_user, login_user, UserRegistrationRequest, UserLoginRequest
        from fastapi import Request, HTTPException
        
        # Register user first
        mock_request = Mock(spec=Request)
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {"user-agent": "test-agent"}
        
        with patch('api_gateway.user_routes.get_email_service') as mock_email_service:
            mock_email_instance = Mock()
            mock_email_instance.send_welcome_email = AsyncMock(return_value={"status": "sent"})
            mock_email_service.return_value = mock_email_instance
            
            # Register user
            registration_request = UserRegistrationRequest(**valid_user_data)
            await register_user(registration_request, mock_request)
            
            # Try login with wrong password
            login_request = UserLoginRequest(
                email=valid_user_data["email"],
                password="WrongPassword123!"
            )
            
            with pytest.raises(HTTPException) as exc_info:
                await login_user(login_request)
            
            assert exc_info.value.status_code == 401
            assert "Invalid email or password" in str(exc_info.value.detail)
            
            print("✅ Invalid login credentials correctly rejected")
    
    @integration_test
    async def test_gdpr_compliance_tracking(self, tenant_db, valid_user_data):
        """Test GDPR compliance data is properly tracked"""
        
        from api_gateway.user_routes import register_user, UserRegistrationRequest
        from fastapi import Request
        
        mock_request = Mock(spec=Request)
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {"user-agent": "test-agent"}
        
        with patch('api_gateway.user_routes.get_email_service') as mock_email_service:
            mock_email_instance = Mock()
            mock_email_instance.send_welcome_email = AsyncMock(return_value={"status": "sent"})
            mock_email_service.return_value = mock_email_instance
            
            # Register user
            registration_request = UserRegistrationRequest(**valid_user_data)
            result = await register_user(registration_request, mock_request)
            
            # Verify GDPR compliance data was stored
            await tenant_db.init_pool()
            
            from agents.shared.tenant_db import TenantContext
            tenant_context = TenantContext(result.tenant_id)
            
            async with tenant_db.get_tenant_connection(tenant_context) as conn:
                # Check user record has GDPR data
                user = await conn.fetchrow(
                    "SELECT * FROM users WHERE id = $1",
                    result.id
                )
                
                assert user is not None
                assert user['gdpr_consent_given'] is True
                assert user['gdpr_consent_date'] is not None
                assert user['gdpr_consent_ip'] == "127.0.0.1"
                assert user['privacy_policy_version'] == "1.0"
                
                # Check consent audit records exist
                consent_records = await conn.fetch(
                    "SELECT * FROM privacy_consent_audit WHERE user_id = $1",
                    result.id
                )
                
                assert len(consent_records) == 2  # GDPR + Terms
                consent_types = [record['consent_type'] for record in consent_records]
                assert 'gdpr' in consent_types
                assert 'terms' in consent_types
                
                print("✅ GDPR compliance tracking verified")
    
    @integration_test
    async def test_password_hashing_security(self, tenant_db, valid_user_data):
        """Test passwords are properly hashed and not stored in plaintext"""
        
        from api_gateway.user_routes import register_user, UserRegistrationRequest, verify_password
        from fastapi import Request
        
        mock_request = Mock(spec=Request)
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {"user-agent": "test-agent"}
        
        with patch('api_gateway.user_routes.get_email_service') as mock_email_service:
            mock_email_instance = Mock()
            mock_email_instance.send_welcome_email = AsyncMock(return_value={"status": "sent"})
            mock_email_service.return_value = mock_email_instance
            
            # Register user
            registration_request = UserRegistrationRequest(**valid_user_data)
            result = await register_user(registration_request, mock_request)
            
            # Check password hash in database
            await tenant_db.init_pool()
            
            from agents.shared.tenant_db import TenantContext
            tenant_context = TenantContext(result.tenant_id)
            
            async with tenant_db.get_tenant_connection(tenant_context) as conn:
                user = await conn.fetchrow(
                    "SELECT password_hash FROM users WHERE id = $1",
                    result.id
                )
                
                password_hash = user['password_hash']
                
                # Verify password is hashed (not plaintext)
                assert password_hash != valid_user_data["password"]
                assert len(password_hash) > 50  # bcrypt hashes are long
                assert password_hash.startswith('$2b$')  # bcrypt format
                
                # Verify password can be verified
                assert verify_password(valid_user_data["password"], password_hash)
                assert not verify_password("wrong-password", password_hash)
                
                print("✅ Password hashing security verified")
    
    @integration_test
    async def test_email_service_integration(self, tenant_db, valid_user_data):
        """Test email service integration for welcome emails"""
        
        from api_gateway.user_routes import register_user, UserRegistrationRequest
        from fastapi import Request
        
        mock_request = Mock(spec=Request)
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {"user-agent": "test-agent"}
        
        # Mock email service with detailed tracking
        email_calls = []
        
        with patch('api_gateway.user_routes.get_email_service') as mock_email_service:
            mock_email_instance = Mock()
            
            async def track_email_call(recipient, welcome_data):
                email_calls.append({
                    "recipient": recipient,
                    "welcome_data": welcome_data,
                    "timestamp": datetime.utcnow()
                })
                return {"status": "sent", "message_id": f"msg_{uuid.uuid4().hex[:8]}"}
            
            mock_email_instance.send_welcome_email = AsyncMock(side_effect=track_email_call)
            mock_email_service.return_value = mock_email_instance
            
            # Register user
            registration_request = UserRegistrationRequest(**valid_user_data)
            result = await register_user(registration_request, mock_request)
            
            # Verify email was sent
            assert len(email_calls) == 1
            
            email_call = email_calls[0]
            recipient = email_call["recipient"]
            welcome_data = email_call["welcome_data"]
            
            # Verify email content
            assert recipient.email == valid_user_data["email"]
            assert recipient.name == f"{valid_user_data['firstName']} {valid_user_data['lastName']}"
            assert welcome_data.user_name == valid_user_data["firstName"]
            assert welcome_data.user_email == valid_user_data["email"]
            assert "dashboard" in welcome_data.dashboard_url.lower()
            
            print("✅ Email service integration verified")
    
    @integration_test
    async def test_tenant_assignment(self, tenant_db, valid_user_data):
        """Test user is properly assigned to a tenant"""
        
        from api_gateway.user_routes import register_user, UserRegistrationRequest
        from fastapi import Request
        
        mock_request = Mock(spec=Request)
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {"user-agent": "test-agent"}
        
        with patch('api_gateway.user_routes.get_email_service') as mock_email_service:
            mock_email_instance = Mock()
            mock_email_instance.send_welcome_email = AsyncMock(return_value={"status": "sent"})
            mock_email_service.return_value = mock_email_instance
            
            # Register user
            registration_request = UserRegistrationRequest(**valid_user_data)
            result = await register_user(registration_request, mock_request)
            
            # Verify tenant assignment
            assert result.tenant_id is not None
            assert len(result.tenant_id) > 10  # Should be a UUID or similar
            
            # Verify user can access tenant data
            await tenant_db.init_pool()
            
            from agents.shared.tenant_db import TenantContext
            tenant_context = TenantContext(result.tenant_id)
            
            async with tenant_db.get_tenant_connection(tenant_context) as conn:
                tenant = await conn.fetchrow(
                    "SELECT * FROM tenants WHERE id = $1",
                    result.tenant_id
                )
                
                assert tenant is not None
                assert tenant['plan'] is not None  # Should have a plan assigned
                
                print(f"✅ Tenant assignment verified: {result.tenant_id}")
    
    @integration_test
    async def test_registration_error_handling(self, tenant_db, valid_user_data):
        """Test registration handles database errors gracefully"""
        
        from api_gateway.user_routes import register_user, UserRegistrationRequest
        from fastapi import Request, HTTPException
        
        mock_request = Mock(spec=Request)
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {"user-agent": "test-agent"}
        
        # Mock database connection failure
        with patch('agents.shared.tenant_db.TenantDatabase.get_tenant_connection') as mock_conn:
            mock_conn.side_effect = Exception("Database connection failed")
            
            registration_request = UserRegistrationRequest(**valid_user_data)
            
            with pytest.raises(HTTPException) as exc_info:
                await register_user(registration_request, mock_request)
            
            assert exc_info.value.status_code == 500
            assert "Internal server error" in str(exc_info.value.detail)
            
            print("✅ Database error handling verified")
    
    @integration_test
    async def test_signup_flow_performance(self, tenant_db):
        """Test signup flow performance with multiple concurrent registrations"""
        
        from api_gateway.user_routes import register_user, UserRegistrationRequest
        from fastapi import Request
        import time
        
        # Create multiple user registration tasks
        tasks = []
        start_time = time.time()
        
        for i in range(5):
            user_data = {
                "firstName": f"User{i}",
                "lastName": "Test",
                "email": f"perf-test-{i}-{uuid.uuid4().hex[:8]}@example.com",
                "password": "TestPassword123!",
                "confirmPassword": "TestPassword123!",
                "agreeToTerms": True,
                "gdprConsent": True
            }
            
            mock_request = Mock(spec=Request)
            mock_request.client.host = "127.0.0.1"
            mock_request.headers = {"user-agent": "test-agent"}
            
            with patch('api_gateway.user_routes.get_email_service') as mock_email_service:
                mock_email_instance = Mock()
                mock_email_instance.send_welcome_email = AsyncMock(return_value={"status": "sent"})
                mock_email_service.return_value = mock_email_instance
                
                registration_request = UserRegistrationRequest(**user_data)
                task = register_user(registration_request, mock_request)
                tasks.append(task)
        
        # Execute all registrations concurrently
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Verify all registrations succeeded
        assert len(results) == 5
        assert all(result.status == "active" for result in results)
        
        total_time = end_time - start_time
        avg_time_per_registration = total_time / len(results)
        
        # Performance assertion (should be reasonably fast)
        assert total_time < 30.0, f"Registration took too long: {total_time}s"
        assert avg_time_per_registration < 10.0, f"Average registration time too slow: {avg_time_per_registration}s"
        
        print(f"✅ Performance test passed: {len(results)} registrations in {total_time:.2f}s")


@integration_test
async def test_end_to_end_marketplace_signup():
    """End-to-end test simulating complete marketplace signup journey"""
    
    # This test simulates a user's complete journey:
    # 1. Visit signup page
    # 2. Fill out form
    # 3. Submit registration
    # 4. Receive welcome email
    # 5. Login to dashboard
    # 6. Access marketplace features
    
    from api_gateway.user_routes import register_user, login_user, UserRegistrationRequest, UserLoginRequest
    from fastapi import Request
    
    user_data = {
        "firstName": "Alice",
        "lastName": "Johnson",
        "email": f"e2e-test-{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123!",
        "confirmPassword": "SecurePassword123!",
        "agreeToTerms": True,
        "gdprConsent": True
    }
    
    # Step 1: User registration
    mock_request = Mock(spec=Request)
    mock_request.client.host = "192.168.1.100"
    mock_request.headers = {"user-agent": "Mozilla/5.0 (test browser)"}
    
    email_sent = False
    
    with patch('api_gateway.user_routes.get_email_service') as mock_email_service:
        mock_email_instance = Mock()
        
        async def track_email(*args, **kwargs):
            nonlocal email_sent
            email_sent = True
            return {"status": "sent", "message_id": "welcome_123"}
        
        mock_email_instance.send_welcome_email = AsyncMock(side_effect=track_email)
        mock_email_service.return_value = mock_email_instance
        
        # Register user
        registration_request = UserRegistrationRequest(**user_data)
        registration_result = await register_user(registration_request, mock_request)
        
        # Verify registration
        assert registration_result.email == user_data["email"]
        assert registration_result.status == "active"
        assert email_sent, "Welcome email should have been sent"
    
    # Step 2: User login
    login_request = UserLoginRequest(
        email=user_data["email"],
        password=user_data["password"]
    )
    
    login_result = await login_user(login_request)
    
    # Verify login
    assert login_result["message"] == "Login successful"
    assert login_result["user"]["email"] == user_data["email"]
    
    # Step 3: Verify user can access marketplace features
    user_id = login_result["user"]["id"]
    tenant_id = login_result["user"]["tenant_id"]
    
    # Simulate accessing user profile (marketplace feature)
    from api_gateway.user_routes import get_user_profile
    
    profile_result = await get_user_profile(
        x_user_id=user_id,
        x_tenant_id=tenant_id
    )
    
    assert profile_result.id == user_id
    assert profile_result.email == user_data["email"]
    assert profile_result.plan is not None  # Should have a plan assigned
    
    print("🎉 End-to-end marketplace signup test completed successfully!")
    print(f"   User: {profile_result.name}")
    print(f"   Email: {profile_result.email}")
    print(f"   Plan: {profile_result.plan}")
    print(f"   Tenant: {profile_result.tenant_id}")


if __name__ == "__main__":
    # Run smoke tests with: python -m pytest tests/integration/test_marketplace_signup_smoke.py -v
    print("Marketplace Signup Smoke Tests - Night 76")
    print("Run with: pytest tests/integration/test_marketplace_signup_smoke.py -v") 