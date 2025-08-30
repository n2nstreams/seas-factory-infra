#!/usr/bin/env python3
"""
Test suite for Tenant Isolation CLI (Night 66)
"""

import asyncio
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

# Add the scripts directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from tenant_isolation import TenantIsolationManager, TenantIsolationError


class TestTenantIsolationCLI(unittest.TestCase):
    """Test the tenant isolation CLI functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.manager = TenantIsolationManager()
        self.test_tenant_slug = "test-corp"
        self.test_tenant_id = "12345"
        
    def test_manager_initialization(self):
        """Test that the manager initializes with correct configuration"""
        self.assertIsInstance(self.manager, TenantIsolationManager)
        self.assertIn('host', self.manager.source_db_config)
        self.assertIn('database', self.manager.source_db_config)
        self.assertEqual(self.manager.project_id, 'saas-factory-prod')
        self.assertEqual(self.manager.region, 'us-central1')
        
    @patch('tenant_isolation.subprocess.run')
    async def test_create_cloud_run_service(self, mock_subprocess):
        """Test Cloud Run service creation"""
        # Mock successful gcloud deployment
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Service URL: https://api-test-corp-project.us-central1.run.app\n"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        isolated_db_name = "tenant_test_corp"
        service_url = await self.manager.create_cloud_run_service(
            self.test_tenant_slug, 
            isolated_db_name
        )
        
        # Verify the gcloud command was called correctly
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        
        self.assertIn('gcloud', call_args)
        self.assertIn('run', call_args)
        self.assertIn('deploy', call_args)
        self.assertIn('api-test-corp', call_args)
        self.assertIn('--set-env-vars', call_args)
        
        # Verify service URL is returned
        self.assertTrue(service_url.startswith('https://'))
        self.assertIn('api-test-corp', service_url)
        
    @patch('tenant_isolation.subprocess.run')
    async def test_create_cloud_run_service_failure(self, mock_subprocess):
        """Test Cloud Run service creation failure handling"""
        # Mock failed gcloud deployment
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "ERROR: Deployment failed"
        mock_subprocess.return_value = mock_result
        
        isolated_db_name = "tenant_test_corp"
        
        with self.assertRaises(TenantIsolationError) as context:
            await self.manager.create_cloud_run_service(
                self.test_tenant_slug, 
                isolated_db_name
            )
        
        self.assertIn("Failed to deploy Cloud Run service", str(context.exception))
        
    async def test_create_load_balancer_routing(self):
        """Test load balancer routing configuration creation"""
        service_url = "https://api-test-corp-project.us-central1.run.app"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Temporarily change the config directory
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                await self.manager.create_load_balancer_routing(
                    self.test_tenant_slug, 
                    service_url
                )
                
                # Verify config file was created
                config_file = Path("config/load-balancer/test-corp.json")
                self.assertTrue(config_file.exists())
                
                # Verify config content
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                self.assertEqual(config['tenant_slug'], self.test_tenant_slug)
                self.assertEqual(config['service_url'], service_url)
                self.assertEqual(config['subdomain'], 'app-test-corp')
                
            finally:
                os.chdir(original_cwd)
                
    @patch('tenant_isolation.urllib.request.urlopen')
    async def test_verify_cloud_run_deployment_healthy(self, mock_urlopen):
        """Test Cloud Run deployment health verification - healthy case"""
        # Mock successful health check
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        service_url = "https://api-test-corp-project.us-central1.run.app"
        
        result = await self.manager.verify_cloud_run_deployment(
            self.test_tenant_slug, 
            service_url
        )
        
        self.assertTrue(result)
        mock_urlopen.assert_called_with(f"{service_url}/health", timeout=30)
        
    @patch('tenant_isolation.urllib.request.urlopen')
    async def test_verify_cloud_run_deployment_unhealthy(self, mock_urlopen):
        """Test Cloud Run deployment health verification - unhealthy case"""
        # Mock failed health check
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("Service unavailable")
        
        service_url = "https://api-test-corp-project.us-central1.run.app"
        
        result = await self.manager.verify_cloud_run_deployment(
            self.test_tenant_slug, 
            service_url
        )
        
        self.assertFalse(result)
        
    async def test_create_routing_config_with_cloud_run(self):
        """Test routing configuration creation with Cloud Run info"""
        isolated_db_name = "tenant_test_corp"
        service_url = "https://api-test-corp-project.us-central1.run.app"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                await self.manager.create_routing_config(
                    self.test_tenant_slug, 
                    isolated_db_name, 
                    service_url
                )
                
                # Verify config file was created
                config_file = Path("config/routing/test-corp.json")
                self.assertTrue(config_file.exists())
                
                # Verify config content
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                self.assertEqual(config['tenant_slug'], self.test_tenant_slug)
                self.assertEqual(config['database']['name'], isolated_db_name)
                self.assertEqual(config['cloud_run']['service_url'], service_url)
                self.assertEqual(config['cloud_run']['service_name'], 'api-test-corp')
                self.assertEqual(config['endpoints']['api'], service_url)
                
            finally:
                os.chdir(original_cwd)


class TestTenantIsolationIntegration(unittest.TestCase):
    """Integration tests for the full tenant isolation workflow"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.manager = TenantIsolationManager()
        self.test_tenant_slug = "integration-test"
        
    @patch('tenant_isolation.asyncpg.connect')
    @patch('tenant_isolation.subprocess.run')
    @patch('tenant_isolation.urllib.request.urlopen')
    async def test_promote_tenant_full_workflow(self, mock_urlopen, mock_subprocess, mock_connect):
        """Test the complete tenant promotion workflow"""
        # Mock database operations
        mock_conn = AsyncMock()
        mock_connect.return_value = mock_conn
        
        # Mock tenant info
        mock_tenant_data = {
            'id': '12345',
            'slug': self.test_tenant_slug,
            'isolation_mode': 'shared',
            'plan': 'pro',
            'status': 'active'
        }
        mock_conn.fetchrow.return_value = mock_tenant_data
        mock_conn.fetchval.return_value = None  # Database doesn't exist
        mock_conn.fetch.return_value = []  # No data to migrate initially
        mock_conn.execute.return_value = "UPDATE 1"
        
        # Mock successful Cloud Run deployment
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = f"Service URL: https://api-{self.test_tenant_slug}-project.us-central1.run.app\n"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        # Mock successful health check
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create fake migration file
                os.makedirs('dev/migrations', exist_ok=True)
                with open('dev/migrations/001_create_tenant_model.sql', 'w') as f:
                    f.write('CREATE TABLE tenants (id UUID PRIMARY KEY);')
                
                result = await self.manager.promote_tenant(
                    self.test_tenant_slug,
                    cleanup_shared=False,  # Don't cleanup for test
                    deploy_cloud_run=True
                )
                
                # Verify result
                self.assertEqual(result['status'], 'success')
                self.assertEqual(result['tenant_slug'], self.test_tenant_slug)
                self.assertIsNotNone(result['cloud_run_service_url'])
                self.assertTrue(result['cloud_run_deployed'])
                
                # Verify config files were created
                self.assertTrue(Path(f"config/routing/{self.test_tenant_slug}.json").exists())
                self.assertTrue(Path(f"config/load-balancer/{self.test_tenant_slug}.json").exists())
                
            finally:
                os.chdir(original_cwd)


def run_tests():
    """Run all tenant isolation CLI tests"""
    print("🧪 Running Tenant Isolation CLI Tests...")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestTenantIsolationCLI))
    suite.addTests(loader.loadTestsFromTestCase(TestTenantIsolationIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("✅ All tenant isolation CLI tests passed!")
        return True
    else:
        print("❌ Some tenant isolation CLI tests failed!")
        return False


async def run_async_tests():
    """Run async tests"""
    test_cases = [
        TestTenantIsolationCLI(),
        TestTenantIsolationIntegration()
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        test_case.setUp()
        
        # Get all async test methods
        async_methods = [
            method for method in dir(test_case) 
            if method.startswith('test_') and asyncio.iscoroutinefunction(getattr(test_case, method))
        ]
        
        for method_name in async_methods:
            try:
                print(f"Running {test_case.__class__.__name__}.{method_name}...")
                await getattr(test_case, method_name)()
                print(f"✅ {method_name} passed")
            except Exception as e:
                print(f"❌ {method_name} failed: {e}")
                all_passed = False
    
    return all_passed


if __name__ == '__main__':
    print("🚀 Night 66: Tenant Isolation CLI Tests")
    print("=" * 50)
    
    # Run async tests
    async_result = asyncio.run(run_async_tests())
    
    print("\n" + "=" * 50)
    if async_result:
        print("✅ All Night 66 tenant isolation tests completed successfully!")
        sys.exit(0)
    else:
        print("❌ Some Night 66 tenant isolation tests failed!")
        sys.exit(1) 