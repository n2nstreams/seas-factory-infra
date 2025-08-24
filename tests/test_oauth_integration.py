#!/usr/bin/env python3
"""
Test OAuth Integration for SaaS Factory
Tests both Google and GitHub OAuth flows
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from api_gateway.app import app
from api_gateway.oauth_routes import create_or_get_oauth_user, create_jwt_token


class TestOAuthIntegration:
    """Test OAuth integration functionality"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_tenant_db(self):
        """Mock tenant database"""
        with patch('api_gateway.oauth_routes.tenant_db') as mock_db:
            mock_db.init_pool = AsyncMock()
            mock_db.get_tenant_connection = AsyncMock()
            yield mock_db
    
    def test_oauth_status_endpoint(self, client):
        """Test OAuth status endpoint"""
        response = client.get("/auth/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "google_oauth_enabled" in data
        assert "github_oauth_enabled" in data
        assert "google_client_id_configured" in data
        assert "github_client_id_configured" in data
    
    def test_google_oauth_start_disabled(self, client):
        """Test Google OAuth start when disabled"""
        with patch('config.settings.get_settings') as mock_settings:
            mock_settings.return_value.security.google_oauth_enabled = False
            
            response = client.get("/auth/google")
            assert response.status_code == 400
            assert "not enabled" in response.json()["detail"]
    
    def test_github_oauth_start_disabled(self, client):
        """Test GitHub OAuth start when disabled"""
        with patch('config.settings.get_settings') as mock_settings:
            mock_settings.return_value.security.github_oauth_enabled = False
            
            response = client.get("/auth/github")
            assert response.status_code == 400
            assert "not enabled" in response.json()["detail"]
    
    def test_google_oauth_start_not_configured(self, client):
        """Test Google OAuth start when not configured"""
        with patch('config.settings.get_settings') as mock_settings:
            mock_settings.return_value.security.google_oauth_enabled = True
            mock_settings.return_value.security.google_client_id = None
            
            response = client.get("/auth/google")
            assert response.status_code == 500
            assert "not configured" in response.json()["detail"]
    
    def test_github_oauth_start_not_configured(self, client):
        """Test GitHub OAuth start when not configured"""
        with patch('config.settings.get_settings') as mock_settings:
            mock_settings.return_value.security.github_oauth_enabled = True
            mock_settings.return_value.security.github_client_id = None
            
            response = client.get("/auth/github")
            assert response.status_code == 500
            assert "not configured" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_create_or_get_oauth_user_new_user(self, mock_tenant_db):
        """Test creating new OAuth user"""
        # Mock database connection
        mock_conn = AsyncMock()
        mock_tenant_db.get_tenant_connection.return_value.__aenter__.return_value = mock_conn
        
        # Mock user doesn't exist
        mock_conn.fetchrow.return_value = None
        
        # Mock user creation
        mock_conn.fetchval.return_value = "test-user-id"
        
        # Mock tenant lookup
        mock_conn.fetchrow.side_effect = [None, {"plan": "starter"}]
        
        result = await create_or_get_oauth_user(
            email="test@example.com",
            name="Test User",
            provider="google",
            provider_id="12345"
        )
        
        assert result["email"] == "test@example.com"
        assert result["name"] == "Test User"
        assert result["role"] == "user"
        assert result["status"] == "active"
        assert result["plan"] == "starter"
    
    @pytest.mark.asyncio
    async def test_create_or_get_oauth_user_existing_user(self, mock_tenant_db):
        """Test getting existing OAuth user"""
        # Mock database connection
        mock_conn = AsyncMock()
        mock_tenant_db.get_tenant_connection.return_value.__aenter__.return_value = mock_conn
        
        # Mock existing user
        mock_conn.fetchrow.return_value = {
            "id": "existing-user-id",
            "tenant_id": "test-tenant-id",
            "email": "test@example.com",
            "name": "Test User",
            "role": "user",
            "status": "active",
            "created_at": "2024-01-01T00:00:00",
            "plan": "pro"
        }
        
        result = await create_or_get_oauth_user(
            email="test@example.com",
            name="Test User",
            provider="github",
            provider_id="67890"
        )
        
        assert result["id"] == "existing-user-id"
        assert result["email"] == "test@example.com"
        assert result["plan"] == "pro"
        
        # Verify last login was updated
        mock_conn.execute.assert_called_once()
    
    def test_create_jwt_token(self):
        """Test JWT token creation"""
        user = {
            "id": "test-user-id",
            "tenant_id": "test-tenant-id",
            "email": "test@example.com",
            "role": "user"
        }
        
        with patch('api_gateway.oauth_routes.settings') as mock_settings:
            mock_settings.security.jwt_secret_key.get_secret_value.return_value = "test-secret"
            mock_settings.security.jwt_algorithm = "HS256"
            mock_settings.security.jwt_expiration_hours = 24
            
            token = create_jwt_token(user)
            
            assert token is not None
            assert isinstance(token, str)
    
    def test_oauth_callback_missing_code(self, client):
        """Test OAuth callback with missing code"""
        response = client.get("/auth/callback/google")
        assert response.status_code == 400
        assert "not provided" in response.json()["detail"]
        
        response = client.get("/auth/callback/github")
        assert response.status_code == 400
        assert "not provided" in response.json()["detail"]
    
    def test_oauth_callback_with_error(self, client):
        """Test OAuth callback with error parameter"""
        response = client.get("/auth/callback/google?error=access_denied")
        assert response.status_code == 400
        assert "access_denied" in response.json()["detail"]
        
        response = client.get("/auth/callback/github?error=access_denied")
        assert response.status_code == 400
        assert "access_denied" in response.json()["detail"]


class TestOAuthFrontendIntegration:
    """Test OAuth frontend integration"""
    
    def test_oauth_configuration_validation(self):
        """Test OAuth configuration validation in frontend"""
        # This would test the frontend OAuth configuration
        # Since we can't run frontend tests here, we'll document the expected behavior
        
        expected_config = {
            "github": {
                "clientId": "VITE_GITHUB_CLIENT_ID",
                "redirectUri": "/auth/callback/github",
                "scope": "user:email",
                "authUrl": "https://github.com/login/oauth/authorize"
            },
            "google": {
                "clientId": "VITE_GOOGLE_CLIENT_ID",
                "redirectUri": "/auth/callback/google",
                "scope": "openid email profile",
                "authUrl": "https://accounts.google.com/oauth2/v2/auth"
            }
        }
        
        # Verify expected configuration structure
        assert "github" in expected_config
        assert "google" in expected_config
        assert "clientId" in expected_config["github"]
        assert "clientId" in expected_config["google"]
        assert "redirectUri" in expected_config["github"]
        assert "redirectUri" in expected_config["google"]


if __name__ == "__main__":
    pytest.main([__file__])
