"""
Multi-cloud secret management providers for SecretsManagerAgent
Supports GCP Secret Manager, AWS Secrets Manager, and Azure Key Vault
"""

import abc
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from google.cloud import secretmanager
import json

logger = logging.getLogger(__name__)

class SecretRotationResult:
    """Result of a secret rotation operation"""
    
    def __init__(
        self,
        success: bool,
        previous_version: Optional[str] = None,
        new_version: Optional[str] = None,
        error_message: Optional[str] = None,
        duration_seconds: Optional[int] = None
    ):
        self.success = success
        self.previous_version = previous_version
        self.new_version = new_version
        self.error_message = error_message
        self.duration_seconds = duration_seconds
        self.timestamp = datetime.utcnow()

class SecretProvider(abc.ABC):
    """Abstract base class for secret management providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_name = self.__class__.__name__.lower().replace('provider', '')
    
    @abc.abstractmethod
    async def create_secret(
        self,
        secret_name: str,
        secret_value: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """Create a new secret"""
        pass
    
    @abc.abstractmethod
    async def get_secret(self, secret_name: str, version: str = "latest") -> Optional[str]:
        """Retrieve a secret value"""
        pass
    
    @abc.abstractmethod
    async def update_secret(
        self,
        secret_name: str,
        new_value: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> SecretRotationResult:
        """Update an existing secret (rotation)"""
        pass
    
    @abc.abstractmethod
    async def delete_secret(self, secret_name: str) -> bool:
        """Delete a secret"""
        pass
    
    @abc.abstractmethod
    async def list_secrets(self) -> List[Dict[str, Any]]:
        """List all secrets managed by this provider"""
        pass
    
    @abc.abstractmethod
    async def get_secret_metadata(self, secret_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata about a secret"""
        pass

    def validate_config(self) -> bool:
        """Validate provider configuration"""
        required_fields = self.get_required_config_fields()
        for field in required_fields:
            if field not in self.config:
                logger.error(f"Missing required config field: {field}")
                return False
        return True
    
    @abc.abstractmethod
    def get_required_config_fields(self) -> List[str]:
        """Return list of required configuration fields"""
        pass

class GCPSecretProvider(SecretProvider):
    """Google Cloud Secret Manager provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.project_id = config.get("project_id")
        self.client = None
    
    def get_required_config_fields(self) -> List[str]:
        return ["project_id"]
    
    async def _get_client(self):
        """Initialize GCP Secret Manager client"""
        if self.client is None:
            self.client = secretmanager.SecretManagerServiceClient()
        return self.client
    
    async def create_secret(
        self,
        secret_name: str,
        secret_value: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """Create a new secret in GCP Secret Manager"""
        try:
            client = await self._get_client()
            parent = f"projects/{self.project_id}"
            
            # Create the secret
            secret = {
                "replication": {"automatic": {}},
            }
            
            if metadata:
                secret["labels"] = metadata
            
            secret_id = secret_name
            response = client.create_secret(
                parent=parent,
                secret_id=secret_id,
                secret=secret
            )
            
            # Add the secret version
            secret_name_path = response.name
            payload = {"data": secret_value.encode("UTF-8")}
            
            client.add_secret_version(
                parent=secret_name_path,
                payload=payload
            )
            
            logger.info(f"Created secret {secret_name} in GCP")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create secret {secret_name} in GCP: {e}")
            return False
    
    async def get_secret(self, secret_name: str, version: str = "latest") -> Optional[str]:
        """Retrieve a secret value from GCP Secret Manager"""
        try:
            client = await self._get_client()
            name = f"projects/{self.project_id}/secrets/{secret_name}/versions/{version}"
            
            response = client.access_secret_version(name=name)
            secret_value = response.payload.data.decode("UTF-8")
            
            return secret_value
            
        except Exception as e:
            logger.error(f"Failed to get secret {secret_name} from GCP: {e}")
            return None
    
    async def update_secret(
        self,
        secret_name: str,
        new_value: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> SecretRotationResult:
        """Update a secret in GCP Secret Manager"""
        start_time = datetime.utcnow()
        
        try:
            client = await self._get_client()
            
            # Get current version before rotation
            current_value = await self.get_secret(secret_name)
            if current_value is None:
                return SecretRotationResult(
                    success=False,
                    error_message="Secret not found or access denied"
                )
            
            # Add new version
            parent = f"projects/{self.project_id}/secrets/{secret_name}"
            payload = {"data": new_value.encode("UTF-8")}
            
            response = client.add_secret_version(
                parent=parent,
                payload=payload
            )
            
            # Extract version number from response name
            new_version = response.name.split("/")[-1]
            
            # Update labels if provided
            if metadata:
                secret_path = f"projects/{self.project_id}/secrets/{secret_name}"
                secret = client.get_secret(name=secret_path)
                
                update_mask = {"paths": ["labels"]}
                secret.labels.update(metadata)
                
                client.update_secret(
                    secret=secret,
                    update_mask=update_mask
                )
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(f"Successfully rotated secret {secret_name} in GCP, new version: {new_version}")
            
            return SecretRotationResult(
                success=True,
                previous_version="previous",  # GCP doesn't provide previous version info easily
                new_version=new_version,
                duration_seconds=int(duration)
            )
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Failed to rotate secret {secret_name} in GCP: {e}")
            
            return SecretRotationResult(
                success=False,
                error_message=str(e),
                duration_seconds=int(duration)
            )
    
    async def delete_secret(self, secret_name: str) -> bool:
        """Delete a secret from GCP Secret Manager"""
        try:
            client = await self._get_client()
            name = f"projects/{self.project_id}/secrets/{secret_name}"
            
            client.delete_secret(name=name)
            logger.info(f"Deleted secret {secret_name} from GCP")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete secret {secret_name} from GCP: {e}")
            return False
    
    async def list_secrets(self) -> List[Dict[str, Any]]:
        """List all secrets in GCP Secret Manager"""
        try:
            client = await self._get_client()
            parent = f"projects/{self.project_id}"
            
            secrets = []
            for secret in client.list_secrets(parent=parent):
                secret_info = {
                    "name": secret.name.split("/")[-1],
                    "full_name": secret.name,
                    "labels": dict(secret.labels) if secret.labels else {},
                    "created_time": secret.create_time,
                    "replication": str(secret.replication)
                }
                secrets.append(secret_info)
            
            return secrets
            
        except Exception as e:
            logger.error(f"Failed to list secrets from GCP: {e}")
            return []
    
    async def get_secret_metadata(self, secret_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata about a secret in GCP Secret Manager"""
        try:
            client = await self._get_client()
            name = f"projects/{self.project_id}/secrets/{secret_name}"
            
            secret = client.get_secret(name=name)
            
            metadata = {
                "name": secret.name.split("/")[-1],
                "labels": dict(secret.labels) if secret.labels else {},
                "created_time": secret.create_time,
                "replication": str(secret.replication)
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to get metadata for secret {secret_name} from GCP: {e}")
            return None

class AWSSecretProvider(SecretProvider):
    """AWS Secrets Manager provider (future implementation)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.region = config.get("region", "us-east-1")
        # TODO: Initialize boto3 client when AWS support is added
    
    def get_required_config_fields(self) -> List[str]:
        return ["region", "access_key_id", "secret_access_key"]
    
    async def create_secret(self, secret_name: str, secret_value: str, metadata: Optional[Dict[str, str]] = None) -> bool:
        logger.warning("AWS Secrets Manager not yet implemented")
        return False
    
    async def get_secret(self, secret_name: str, version: str = "latest") -> Optional[str]:
        logger.warning("AWS Secrets Manager not yet implemented")
        return None
    
    async def update_secret(self, secret_name: str, new_value: str, metadata: Optional[Dict[str, str]] = None) -> SecretRotationResult:
        logger.warning("AWS Secrets Manager not yet implemented")
        return SecretRotationResult(success=False, error_message="AWS support not implemented")
    
    async def delete_secret(self, secret_name: str) -> bool:
        logger.warning("AWS Secrets Manager not yet implemented")
        return False
    
    async def list_secrets(self) -> List[Dict[str, Any]]:
        logger.warning("AWS Secrets Manager not yet implemented")
        return []
    
    async def get_secret_metadata(self, secret_name: str) -> Optional[Dict[str, Any]]:
        logger.warning("AWS Secrets Manager not yet implemented")
        return None

class AzureSecretProvider(SecretProvider):
    """Azure Key Vault provider (future implementation)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.vault_url = config.get("vault_url")
        # TODO: Initialize Azure Key Vault client when Azure support is added
    
    def get_required_config_fields(self) -> List[str]:
        return ["vault_url", "client_id", "client_secret", "tenant_id"]
    
    async def create_secret(self, secret_name: str, secret_value: str, metadata: Optional[Dict[str, str]] = None) -> bool:
        logger.warning("Azure Key Vault not yet implemented")
        return False
    
    async def get_secret(self, secret_name: str, version: str = "latest") -> Optional[str]:
        logger.warning("Azure Key Vault not yet implemented")
        return None
    
    async def update_secret(self, secret_name: str, new_value: str, metadata: Optional[Dict[str, str]] = None) -> SecretRotationResult:
        logger.warning("Azure Key Vault not yet implemented")
        return SecretRotationResult(success=False, error_message="Azure support not implemented")
    
    async def delete_secret(self, secret_name: str) -> bool:
        logger.warning("Azure Key Vault not yet implemented")
        return False
    
    async def list_secrets(self) -> List[Dict[str, Any]]:
        logger.warning("Azure Key Vault not yet implemented")
        return []
    
    async def get_secret_metadata(self, secret_name: str) -> Optional[Dict[str, Any]]:
        logger.warning("Azure Key Vault not yet implemented")
        return None

def get_provider(provider_name: str, config: Dict[str, Any]) -> SecretProvider:
    """Factory function to get the appropriate secret provider"""
    providers = {
        "gcp": GCPSecretProvider,
        "aws": AWSSecretProvider,
        "azure": AzureSecretProvider
    }
    
    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unsupported provider: {provider_name}")
    
    provider = provider_class(config)
    if not provider.validate_config():
        raise ValueError(f"Invalid configuration for provider: {provider_name}")
    
    return provider 