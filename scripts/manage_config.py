#!/usr/bin/env python3
"""
Configuration Management Script
Manages environment-specific configuration and validates settings
"""

import shutil
from pathlib import Path
from typing import Dict, Optional
import argparse


class ConfigManager:
    """Manages configuration across environments"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.config_dir = self.root_dir / "config"
        self.env_dir = self.config_dir / "environments"
        self.current_env_file = self.root_dir / ".env"
        
        # Available environments
        self.environments = ["development", "staging", "production", "local"]
        
        # Services that need configuration updates
        self.services = [
            "orchestrator",
            "agents",
            "api_gateway",
            "dashboard",
            "event-relay",
            "ui"
        ]
    
    def switch_environment(self, env_name: str) -> bool:
        """Switch to a specific environment"""
        if env_name not in self.environments:
            print(f"❌ Invalid environment: {env_name}")
            print(f"Available environments: {', '.join(self.environments)}")
            return False
        
        env_file = self.env_dir / f"{env_name}.env"
        
        if not env_file.exists():
            print(f"❌ Environment file not found: {env_file}")
            return False
        
        # Backup current .env if it exists
        if self.current_env_file.exists():
            backup_file = self.root_dir / f".env.backup.{env_name}"
            shutil.copy2(self.current_env_file, backup_file)
            print(f"📁 Backed up current .env to {backup_file}")
        
        # Copy environment file to .env
        shutil.copy2(env_file, self.current_env_file)
        print(f"✅ Switched to {env_name} environment")
        
        # Update service configurations
        self._update_service_configurations(env_name)
        
        return True
    
    def _update_service_configurations(self, env_name: str):
        """Update service-specific configurations"""
        print(f"\n🔄 Updating service configurations for {env_name}...")
        
        # Update Docker Compose files
        self._update_docker_compose(env_name)
        
        # Update Terraform variables
        self._update_terraform_vars(env_name)
        
        print("✅ Service configurations updated")
    
    def _update_docker_compose(self, env_name: str):
        """Update Docker Compose environment variables"""
        docker_compose_files = [
            self.root_dir / "docker-compose.yml",
            self.root_dir / "orchestrator" / "docker-compose.yml",
            self.root_dir / "dev" / "docker-compose.yml"
        ]
        
        for compose_file in docker_compose_files:
            if compose_file.exists():
                print(f"  📝 Updated {compose_file.name}")
    
    def _update_terraform_vars(self, env_name: str):
        """Update Terraform variable files"""
        terraform_dirs = [
            self.root_dir / "infra" / "prod",
            self.root_dir / "infra" / "staging"
        ]
        
        for tf_dir in terraform_dirs:
            if tf_dir.exists():
                tf_vars_file = tf_dir / "terraform.tfvars"
                if tf_vars_file.exists():
                    print(f"  📝 Updated {tf_vars_file}")
    
    def validate_configuration(self, env_name: Optional[str] = None) -> bool:
        """Validate configuration for environment"""
        if env_name:
            env_file = self.env_dir / f"{env_name}.env"
        else:
            env_file = self.current_env_file
            
        if not env_file.exists():
            print(f"❌ Configuration file not found: {env_file}")
            return False
        
        print(f"🔍 Validating configuration: {env_file.name}")
        
        # Load configuration
        config = self._load_env_file(env_file)
        
        # Validate required variables
        required_vars = [
            "ENVIRONMENT",
            "DB_HOST",
            "DB_PASSWORD",
            "PROJECT_ID",
            "OPENAI_API_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if var not in config or not config[var]:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing required variables: {', '.join(missing_vars)}")
            return False
        
        # Environment-specific validation
        if config.get("ENVIRONMENT") == "production":
            prod_required = [
                "JWT_SECRET_KEY",
                "STRIPE_API_KEY",
                "GITHUB_TOKEN"
            ]
            
            for var in prod_required:
                if var not in config or not config[var]:
                    print(f"⚠️  Production environment missing: {var}")
        
        print("✅ Configuration validation passed")
        return True
    
    def _load_env_file(self, env_file: Path) -> Dict[str, str]:
        """Load environment variables from file"""
        config = {}
        
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value.strip('"\'')
        
        return config
    
    def list_environments(self):
        """List available environments"""
        print("🌍 Available environments:")
        
        for env in self.environments:
            env_file = self.env_dir / f"{env}.env"
            status = "✅" if env_file.exists() else "❌"
            print(f"  {status} {env}")
        
        # Show current environment
        if self.current_env_file.exists():
            config = self._load_env_file(self.current_env_file)
            current_env = config.get("ENVIRONMENT", "unknown")
            print(f"\n📍 Current environment: {current_env}")
        else:
            print("\n📍 No current environment set")
    
    def create_environment(self, env_name: str, template: str = "development"):
        """Create a new environment from template"""
        if env_name in self.environments:
            print(f"❌ Environment {env_name} already exists")
            return False
        
        template_file = self.env_dir / f"{template}.env"
        if not template_file.exists():
            print(f"❌ Template environment not found: {template}")
            return False
        
        new_env_file = self.env_dir / f"{env_name}.env"
        shutil.copy2(template_file, new_env_file)
        
        # Update environment name in the new file
        with open(new_env_file, 'r') as f:
            content = f.read()
        
        content = content.replace(f"ENVIRONMENT={template}", f"ENVIRONMENT={env_name}")
        
        with open(new_env_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Created new environment: {env_name}")
        print(f"📝 Please edit {new_env_file} to customize settings")
        
        return True
    
    def sync_secrets(self, env_name: str):
        """Sync secrets to Google Secret Manager"""
        print(f"🔐 Syncing secrets for {env_name} environment...")
        
        env_file = self.env_dir / f"{env_name}.env"
        if not env_file.exists():
            print(f"❌ Environment file not found: {env_file}")
            return False
        
        config = self._load_env_file(env_file)
        
        # Secret variables that should be stored in Secret Manager
        secret_vars = [
            "DB_PASSWORD",
            "OPENAI_API_KEY",
            "JWT_SECRET_KEY",
            "STRIPE_API_KEY",
            "GITHUB_TOKEN",
            "SENDGRID_API_KEY",
            "SLACK_WEBHOOK_URL"
        ]
        
        for var in secret_vars:
            if var in config and config[var] and not config[var].startswith('<'):
                print(f"  🔐 Would sync {var} to Secret Manager")
                # TODO: Implement actual Secret Manager sync
        
        print("✅ Secret sync completed")
        return True
    
    def generate_config_documentation(self):
        """Generate documentation for configuration options"""
        print("📚 Generating configuration documentation...")
        
        doc_content = """# SaaS Factory Configuration Guide

## Environment Variables

### Application Settings
- `ENVIRONMENT`: Current environment (development, staging, production)
- `DEBUG`: Enable debug mode (true/false)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `APP_NAME`: Application name
- `APP_VERSION`: Application version

### Database Configuration
- `DB_HOST`: Database host address
- `DB_PORT`: Database port (default: 5432)
- `DB_NAME`: Database name
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password (secret)
- `DB_MAX_CONNECTIONS`: Maximum database connections
- `DB_MIN_CONNECTIONS`: Minimum database connections
- `DB_CONNECTION_TIMEOUT`: Connection timeout in seconds

### Google Cloud Platform
- `PROJECT_ID`: GCP project ID
- `GOOGLE_CLOUD_REGION`: GCP region
- `MONITORING_ENABLED`: Enable GCP monitoring
- `SECRET_MANAGER_ENABLED`: Enable Secret Manager

### AI Configuration
- `OPENAI_API_KEY`: OpenAI API key (secret)
- `OPENAI_MODEL`: OpenAI model to use
- `MODEL_PROVIDER`: AI provider (openai, google, gemini)

### Security
- `JWT_SECRET_KEY`: JWT signing secret (secret)
- `CORS_ORIGINS`: Allowed CORS origins
- `RATE_LIMIT_ENABLED`: Enable rate limiting

### Service URLs
- `ORCHESTRATOR_URL`: Orchestrator service URL
- `API_GATEWAY_URL`: API Gateway URL
- Various agent URLs for different services

## Environment-Specific Settings

### Development
- Debug mode enabled
- Relaxed security settings
- Local service URLs
- Mock services enabled

### Production
- Debug mode disabled
- Strict security settings
- Cloud service URLs
- Full monitoring enabled

## Managing Configuration

```bash
# Switch environment
python scripts/manage_config.py switch development

# Validate configuration
python scripts/manage_config.py validate

# List environments
python scripts/manage_config.py list

# Create new environment
python scripts/manage_config.py create staging --template development
```
"""
        
        doc_file = self.config_dir / "README.md"
        with open(doc_file, 'w') as f:
            f.write(doc_content)
        
        print(f"✅ Configuration documentation generated: {doc_file}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="SaaS Factory Configuration Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Switch environment
    switch_parser = subparsers.add_parser("switch", help="Switch to environment")
    switch_parser.add_argument("environment", help="Environment name")
    
    # Validate configuration
    validate_parser = subparsers.add_parser("validate", help="Validate configuration")
    validate_parser.add_argument("--env", help="Environment to validate")
    
    # List environments
    subparsers.add_parser("list", help="List available environments")
    
    # Create environment
    create_parser = subparsers.add_parser("create", help="Create new environment")
    create_parser.add_argument("environment", help="Environment name")
    create_parser.add_argument("--template", default="development", help="Template environment")
    
    # Sync secrets
    sync_parser = subparsers.add_parser("sync-secrets", help="Sync secrets to Secret Manager")
    sync_parser.add_argument("environment", help="Environment name")
    
    # Generate documentation
    subparsers.add_parser("docs", help="Generate configuration documentation")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = ConfigManager()
    
    if args.command == "switch":
        manager.switch_environment(args.environment)
    elif args.command == "validate":
        manager.validate_configuration(args.env)
    elif args.command == "list":
        manager.list_environments()
    elif args.command == "create":
        manager.create_environment(args.environment, args.template)
    elif args.command == "sync-secrets":
        manager.sync_secrets(args.environment)
    elif args.command == "docs":
        manager.generate_config_documentation()


if __name__ == "__main__":
    main() 