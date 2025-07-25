"""
Tests for SecretsManagerAgent
"""

import pytest
import asyncio
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import os
import sys

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from secrets_manager import SecretsManagerAgent, SecretGenerator
from providers import GCPSecretProvider, SecretRotationResult, get_provider
from tenant_db import TenantContext

class TestSecretGenerator:
    """Test the SecretGenerator class"""
    
    def test_generate_api_key(self):
        """Test API key generation"""
        key = SecretGenerator.generate_api_key(32)
        assert len(key) == 32
        assert key.isalnum()
    
    def test_generate_token(self):
        """Test token generation"""
        token = SecretGenerator.generate_token(64)
        assert len(token) > 0  # URL-safe tokens may vary in length
    
    def test_generate_password(self):
        """Test password generation"""
        password = SecretGenerator.generate_password(16)
        assert len(password) == 16
        # Check it contains allowed characters
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*")
        assert all(c in allowed_chars for c in password)

class TestGCPSecretProvider:
    """Test GCP Secret Provider"""
    
    @pytest.fixture
    def gcp_provider(self):
        config = {"project_id": "test-project"}
        return GCPSecretProvider(config)
    
    def test_validate_config(self, gcp_provider):
        """Test configuration validation"""
        assert gcp_provider.validate_config() is True
        
        # Test invalid config
        invalid_provider = GCPSecretProvider({})
        assert invalid_provider.validate_config() is False
    
    def test_get_required_config_fields(self, gcp_provider):
        """Test required config fields"""
        fields = gcp_provider.get_required_config_fields()
        assert "project_id" in fields

class TestProviderFactory:
    """Test provider factory function"""
    
    def test_get_gcp_provider(self):
        """Test getting GCP provider"""
        config = {"project_id": "test-project"}
        provider = get_provider("gcp", config)
        assert isinstance(provider, GCPSecretProvider)
    
    def test_get_invalid_provider(self):
        """Test getting invalid provider"""
        with pytest.raises(ValueError):
            get_provider("invalid", {})
    
    def test_get_provider_invalid_config(self):
        """Test getting provider with invalid config"""
        with pytest.raises(ValueError):
            get_provider("gcp", {})  # Missing project_id

@pytest.fixture
def tenant_context():
    """Test tenant context"""
    return TenantContext(
        tenant_id=str(uuid.uuid4()),
        user_id=str(uuid.uuid4()),
        user_role="admin"
    )

@pytest.fixture
def mock_tenant_db():
    """Mock tenant database"""
    with patch('secrets_manager.TenantDatabase') as mock_db:
        mock_instance = Mock()
        mock_db.return_value = mock_instance
        
        # Mock connection context manager
        mock_conn = Mock()
        mock_instance.get_tenant_connection.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_instance.get_tenant_connection.return_value.__aexit__ = AsyncMock(return_value=None)
        
        yield mock_instance

class TestSecretsManagerAgent:
    """Test the main SecretsManagerAgent class"""
    
    @pytest.fixture
    def agent(self, tenant_context, mock_tenant_db):
        """Create test agent"""
        return SecretsManagerAgent(tenant_context)
    
    @pytest.mark.asyncio
    async def test_initialization(self, agent, mock_tenant_db):
        """Test agent initialization"""
        await agent.initialize()
        mock_tenant_db.init_pool.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_provider(self, agent):
        """Test adding a provider"""
        await agent.initialize()
        
        config = {"project_id": "test-project"}
        await agent.add_provider("gcp", config)
        
        assert "gcp" in agent.providers
        assert isinstance(agent.providers["gcp"], GCPSecretProvider)
    
    @pytest.mark.asyncio
    async def test_add_invalid_provider(self, agent):
        """Test adding invalid provider"""
        await agent.initialize()
        
        with pytest.raises(ValueError):
            await agent.add_provider("invalid", {})
    
    @pytest.mark.asyncio
    async def test_register_secret(self, agent, mock_tenant_db):
        """Test registering a secret for rotation"""
        await agent.initialize()
        
        # Add provider
        config = {"project_id": "test-project"}
        await agent.add_provider("gcp", config)
        
        # Mock database response
        mock_conn = Mock()
        mock_conn.fetchrow = AsyncMock(return_value={"id": uuid.uuid4()})
        mock_tenant_db.get_tenant_connection.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        
        schedule_id = await agent.register_secret(
            secret_name="test-secret",
            provider_name="gcp",
            secret_type="api_key",
            rotation_interval_days=30
        )
        
        assert schedule_id is not None
        mock_conn.fetchrow.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_secret_invalid_provider(self, agent):
        """Test registering secret with invalid provider"""
        await agent.initialize()
        
        with pytest.raises(ValueError):
            await agent.register_secret(
                secret_name="test-secret",
                provider_name="invalid",
                secret_type="api_key"
            )
    
    @pytest.mark.asyncio
    async def test_rotate_secret_success(self, agent, mock_tenant_db):
        """Test successful secret rotation"""
        await agent.initialize()
        
        # Add mock provider
        mock_provider = Mock()
        mock_provider.update_secret = AsyncMock(return_value=SecretRotationResult(
            success=True,
            previous_version="v1",
            new_version="v2",
            duration_seconds=2
        ))
        agent.providers["gcp"] = mock_provider
        
        # Mock database responses
        mock_conn = Mock()
        mock_conn.fetchrow = AsyncMock(return_value={
            "id": uuid.uuid4(),
            "secret_provider": "gcp",
            "secret_type": "api_key",
            "provider_config": {},
            "criticality": "medium"
        })
        mock_conn.execute = AsyncMock()
        mock_tenant_db.get_tenant_connection.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        
        result = await agent.rotate_secret("test-secret")
        
        assert result.success is True
        assert result.new_version == "v2"
        mock_provider.update_secret.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_rotate_secret_not_found(self, agent, mock_tenant_db):
        """Test rotating non-existent secret"""
        await agent.initialize()
        
        # Mock database response - no secret found
        mock_conn = Mock()
        mock_conn.fetchrow = AsyncMock(return_value=None)
        mock_tenant_db.get_tenant_connection.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        
        result = await agent.rotate_secret("non-existent-secret")
        
        assert result.success is False
        assert "not found" in result.error_message
    
    @pytest.mark.asyncio
    async def test_check_due_rotations(self, agent, mock_tenant_db):
        """Test checking for due rotations"""
        await agent.initialize()
        
        # Mock database response
        mock_conn = Mock()
        due_secret = {
            "id": uuid.uuid4(),
            "secret_name": "due-secret",
            "secret_provider": "gcp",
            "secret_type": "api_key",
            "next_rotation_date": datetime.utcnow() - timedelta(days=1),
            "criticality": "high",
            "auto_rotation_enabled": True
        }
        mock_conn.fetch = AsyncMock(return_value=[due_secret])
        mock_tenant_db.get_tenant_connection.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        
        due_secrets = await agent.check_due_rotations()
        
        assert len(due_secrets) == 1
        assert due_secrets[0]["secret_name"] == "due-secret"
    
    @pytest.mark.asyncio
    async def test_update_secret_schedule(self, agent, mock_tenant_db):
        """Test updating secret schedule"""
        await agent.initialize()
        
        # Mock database response
        mock_conn = Mock()
        mock_conn.execute = AsyncMock(return_value="UPDATE 1")
        mock_tenant_db.get_tenant_connection.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        
        success = await agent.update_secret_schedule(
            secret_name="test-secret",
            rotation_interval_days=45,
            criticality="high"
        )
        
        assert success is True
        mock_conn.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_emergency_rotate(self, agent, mock_tenant_db):
        """Test emergency rotation"""
        await agent.initialize()
        
        # Add mock provider
        mock_provider = Mock()
        mock_provider.update_secret = AsyncMock(return_value=SecretRotationResult(
            success=True,
            new_version="emergency-v1"
        ))
        agent.providers["gcp"] = mock_provider
        
        # Mock database responses
        mock_conn = Mock()
        mock_conn.fetchrow = AsyncMock(return_value={
            "id": uuid.uuid4(),
            "secret_provider": "gcp",
            "secret_type": "api_key",
            "provider_config": {},
            "criticality": "critical"
        })
        mock_conn.execute = AsyncMock()
        mock_tenant_db.get_tenant_connection.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        
        result = await agent.emergency_rotate("test-secret", "new-emergency-value")
        
        assert result.success is True
        mock_provider.update_secret.assert_called_with(
            "test-secret",
            "new-emergency-value",
            metadata={
                "rotated_at": result.timestamp.isoformat(),
                "tenant_id": agent.tenant_context.tenant_id,
                "rotation_method": "emergency"
            }
        )

# Integration tests that require more setup
@pytest.mark.integration
class TestSecretsManagerIntegration:
    """Integration tests for SecretsManagerAgent"""
    
    @pytest.mark.asyncio
    async def test_full_rotation_workflow(self):
        """Test complete rotation workflow"""
        # This would require actual database and GCP setup
        # For now, just ensure the structure is in place
        assert True  # Placeholder for integration tests

if __name__ == "__main__":
    pytest.main([__file__]) 