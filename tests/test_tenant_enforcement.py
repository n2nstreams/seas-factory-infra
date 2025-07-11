#!/usr/bin/env python3
"""
Unit Tests for Tenant Enforcement
Tests Row Level Security, data isolation, and multi-tenant functionality.
"""

import pytest
import pytest_asyncio
import asyncio
import asyncpg
import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List

# Mark all async tests
pytestmark = pytest.mark.asyncio

# Test configuration
TEST_DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'factorydb'),
    'user': os.getenv('DB_USER', 'factoryadmin'),
    'password': os.getenv('DB_PASSWORD', 'localpass')
}

class TenantTestCase:
    """Base class for tenant-related test cases"""
    
    def __init__(self):
        self.test_tenants = []
        self.test_users = []
        self.test_projects = []
        
    async def setup_test_data(self, conn):
        """Set up test data for tenant tests"""
        # Disable RLS for setup
        await conn.execute("SET row_security = off")
        
        # Create test tenants
        tenant1_id = str(uuid.uuid4())
        tenant2_id = str(uuid.uuid4())
        
        test_tenants = [
            {
                'id': tenant1_id,
                'name': 'Test Tenant 1',
                'slug': 'test-tenant-1',
                'plan': 'starter',
                'status': 'active',
                'isolation_mode': 'shared'
            },
            {
                'id': tenant2_id,
                'name': 'Test Tenant 2', 
                'slug': 'test-tenant-2',
                'plan': 'pro',
                'status': 'active',
                'isolation_mode': 'shared'
            }
        ]
        
        for tenant in test_tenants:
            await conn.execute(
                """
                INSERT INTO tenants (id, name, slug, plan, status, isolation_mode)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (id) DO NOTHING
                """,
                tenant['id'], tenant['name'], tenant['slug'], 
                tenant['plan'], tenant['status'], tenant['isolation_mode']
            )
            self.test_tenants.append(tenant)
        
        # Create test users for each tenant
        test_users = [
            {
                'id': str(uuid.uuid4()),
                'tenant_id': tenant1_id,
                'email': 'user1@tenant1.com',
                'name': 'User 1',
                'role': 'admin'
            },
            {
                'id': str(uuid.uuid4()),
                'tenant_id': tenant1_id,
                'email': 'user2@tenant1.com',
                'name': 'User 2',
                'role': 'member'
            },
            {
                'id': str(uuid.uuid4()),
                'tenant_id': tenant2_id,
                'email': 'user1@tenant2.com',
                'name': 'User 1 T2',
                'role': 'admin'
            }
        ]
        
        for user in test_users:
            await conn.execute(
                """
                INSERT INTO users (id, tenant_id, email, name, role)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (id) DO NOTHING
                """,
                user['id'], user['tenant_id'], user['email'], 
                user['name'], user['role']
            )
            self.test_users.append(user)
        
        # Create test projects
        test_projects = [
            {
                'id': str(uuid.uuid4()),
                'tenant_id': tenant1_id,
                'name': 'Project A',
                'description': 'Test project for tenant 1',
                'status': 'active'
            },
            {
                'id': str(uuid.uuid4()),
                'tenant_id': tenant2_id,
                'name': 'Project B',
                'description': 'Test project for tenant 2',
                'status': 'active'
            }
        ]
        
        for project in test_projects:
            await conn.execute(
                """
                INSERT INTO projects (id, tenant_id, name, description, status)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (id) DO NOTHING
                """,
                project['id'], project['tenant_id'], project['name'],
                project['description'], project['status']
            )
            self.test_projects.append(project)
        
        # Re-enable RLS
        await conn.execute("SET row_security = on")
        
    async def cleanup_test_data(self, conn):
        """Clean up test data"""
        await conn.execute("SET row_security = off")
        
        # Clean up in reverse order of creation
        for project in self.test_projects:
            await conn.execute("DELETE FROM projects WHERE id = $1", project['id'])
        
        for user in self.test_users:
            await conn.execute("DELETE FROM users WHERE id = $1", user['id'])
        
        for tenant in self.test_tenants:
            await conn.execute("DELETE FROM tenants WHERE id = $1", tenant['id'])
        
        # Clear lists
        self.test_tenants.clear()
        self.test_users.clear()
        self.test_projects.clear()

class TestRowLevelSecurity:
    """Test Row Level Security enforcement"""
    
    @pytest.fixture
    async def db_connection(self):
        """Create database connection for testing"""
        conn = await asyncpg.connect(**TEST_DB_CONFIG)
        yield conn
        await conn.close()
    
    @pytest.fixture
    async def test_case(self, db_connection):
        """Set up test case with test data"""
        test_case = TenantTestCase()
        await test_case.setup_test_data(db_connection)
        yield test_case
        await test_case.cleanup_test_data(db_connection)
    
    async def test_rls_tenant_isolation(self, db_connection, test_case):
        """Test that RLS properly isolates tenant data"""
        tenant1_id = test_case.test_tenants[0]['id']
        tenant2_id = test_case.test_tenants[1]['id']
        
        # Set tenant context for tenant 1
        await db_connection.execute("SET application_name = 'test_app'")
        await db_connection.execute(f"SET app.tenant_id = '{tenant1_id}'")
        await db_connection.execute("SET ROLE application_role")
        
        # Query users - should only see tenant 1 users
        users = await db_connection.fetch("SELECT * FROM users")
        user_tenant_ids = [str(user['tenant_id']) for user in users]
        
        assert all(tid == tenant1_id for tid in user_tenant_ids), \
            f"Expected only tenant {tenant1_id} users, but got: {user_tenant_ids}"
        
        # Query projects - should only see tenant 1 projects
        projects = await db_connection.fetch("SELECT * FROM projects")
        project_tenant_ids = [str(project['tenant_id']) for project in projects]
        
        assert all(tid == tenant1_id for tid in project_tenant_ids), \
            f"Expected only tenant {tenant1_id} projects, but got: {project_tenant_ids}"
        
        # Switch to tenant 2 context
        await db_connection.execute(f"SET app.tenant_id = '{tenant2_id}'")
        
        # Query users - should only see tenant 2 users
        users = await db_connection.fetch("SELECT * FROM users")
        user_tenant_ids = [str(user['tenant_id']) for user in users]
        
        assert all(tid == tenant2_id for tid in user_tenant_ids), \
            f"Expected only tenant {tenant2_id} users, but got: {user_tenant_ids}"
    
    async def test_cross_tenant_data_access_denied(self, db_connection, test_case):
        """Test that cross-tenant data access is denied"""
        tenant1_id = test_case.test_tenants[0]['id']
        tenant2_id = test_case.test_tenants[1]['id']
        
        # Get a project from tenant 2
        tenant2_project = next(p for p in test_case.test_projects if p['tenant_id'] == tenant2_id)
        
        # Set tenant context for tenant 1
        await db_connection.execute(f"SET app.tenant_id = '{tenant1_id}'")
        await db_connection.execute("SET ROLE application_role")
        
        # Try to access tenant 2's project by ID - should return no results
        project = await db_connection.fetchrow(
            "SELECT * FROM projects WHERE id = $1", 
            tenant2_project['id']
        )
        
        assert project is None, "Cross-tenant data access should be denied by RLS"
    
    async def test_tenant_data_modification_isolation(self, db_connection, test_case):
        """Test that data modifications are properly isolated by tenant"""
        tenant1_id = test_case.test_tenants[0]['id']
        tenant2_id = test_case.test_tenants[1]['id']
        
        # Set tenant context for tenant 1
        await db_connection.execute(f"SET app.tenant_id = '{tenant1_id}'")
        await db_connection.execute("SET ROLE application_role")
        
        # Create a new project for tenant 1
        new_project_id = str(uuid.uuid4())
        await db_connection.execute(
            """
            INSERT INTO projects (id, tenant_id, name, description, status)
            VALUES ($1, $2, $3, $4, $5)
            """,
            new_project_id, tenant1_id, "Test Project", "Test Description", "active"
        )
        
        # Verify project was created for tenant 1
        project = await db_connection.fetchrow(
            "SELECT * FROM projects WHERE id = $1", new_project_id
        )
        assert project is not None
        assert str(project['tenant_id']) == tenant1_id
        
        # Switch to tenant 2 context
        await db_connection.execute(f"SET app.tenant_id = '{tenant2_id}'")
        
        # Try to access the project created by tenant 1 - should not be visible
        project = await db_connection.fetchrow(
            "SELECT * FROM projects WHERE id = $1", new_project_id
        )
        assert project is None, "Project created by tenant 1 should not be visible to tenant 2"
        
        # Clean up
        await db_connection.execute("SET row_security = off")
        await db_connection.execute("DELETE FROM projects WHERE id = $1", new_project_id)
        await db_connection.execute("SET row_security = on")

class TestTenantIsolation:
    """Test tenant isolation functionality"""
    
    @pytest.fixture
    async def db_connection(self):
        conn = await asyncpg.connect(**TEST_DB_CONFIG)
        yield conn
        await conn.close()
    
    async def test_tenant_context_setting(self, db_connection):
        """Test setting and retrieving tenant context"""
        test_tenant_id = str(uuid.uuid4())
        
        # Set tenant context
        await db_connection.execute(f"SET app.tenant_id = '{test_tenant_id}'")
        
        # Retrieve tenant context
        result = await db_connection.fetchval("SELECT current_setting('app.tenant_id')")
        
        assert result == test_tenant_id, f"Expected {test_tenant_id}, got {result}"
    
    async def test_application_role_permissions(self, db_connection):
        """Test that application_role has correct permissions"""
        # Switch to application role
        await db_connection.execute("SET ROLE application_role")
        
        # Test SELECT permission on tenants table
        try:
            await db_connection.fetch("SELECT 1 FROM tenants LIMIT 1")
        except Exception as e:
            pytest.fail(f"application_role should have SELECT permission on tenants: {e}")
        
        # Test that we can't disable RLS as application_role
        with pytest.raises(asyncpg.InsufficientPrivilegeError):
            await db_connection.execute("SET row_security = off")

class TestDataIntegrity:
    """Test data integrity and constraints"""
    
    @pytest.fixture
    async def db_connection(self):
        conn = await asyncpg.connect(**TEST_DB_CONFIG)
        yield conn
        await conn.close()
    
    async def test_tenant_slug_uniqueness(self, db_connection):
        """Test that tenant slugs must be unique"""
        await db_connection.execute("SET row_security = off")
        
        tenant_id1 = str(uuid.uuid4())
        tenant_id2 = str(uuid.uuid4())
        
        # Create first tenant
        await db_connection.execute(
            """
            INSERT INTO tenants (id, name, slug, plan, status, isolation_mode)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            tenant_id1, "Test Tenant", "unique-slug", "starter", "active", "shared"
        )
        
        # Try to create second tenant with same slug - should fail
        with pytest.raises(asyncpg.UniqueViolationError):
            await db_connection.execute(
                """
                INSERT INTO tenants (id, name, slug, plan, status, isolation_mode)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                tenant_id2, "Another Tenant", "unique-slug", "pro", "active", "shared"
            )
        
        # Clean up
        await db_connection.execute("DELETE FROM tenants WHERE id = $1", tenant_id1)
    
    async def test_foreign_key_constraints(self, db_connection):
        """Test that foreign key constraints are enforced"""
        await db_connection.execute("SET row_security = off")
        
        fake_tenant_id = str(uuid.uuid4())
        
        # Try to create user with non-existent tenant_id - should fail
        with pytest.raises(asyncpg.ForeignKeyViolationError):
            await db_connection.execute(
                """
                INSERT INTO users (id, tenant_id, email, name, role)
                VALUES ($1, $2, $3, $4, $5)
                """,
                str(uuid.uuid4()), fake_tenant_id, "test@test.com", "Test User", "member"
            )

class TestAuditTrail:
    """Test audit trail functionality"""
    
    @pytest.fixture
    async def db_connection(self):
        conn = await asyncpg.connect(**TEST_DB_CONFIG)
        yield conn
        await conn.close()
    
    @pytest.fixture
    async def test_case(self, db_connection):
        test_case = TenantTestCase()
        await test_case.setup_test_data(db_connection)
        yield test_case
        await test_case.cleanup_test_data(db_connection)
    
    async def test_audit_log_creation(self, db_connection, test_case):
        """Test that audit logs are created for data changes"""
        tenant_id = test_case.test_tenants[0]['id']
        
        # Set tenant context
        await db_connection.execute(f"SET app.tenant_id = '{tenant_id}'")
        await db_connection.execute("SET ROLE application_role")
        
        # Create a new project (should trigger audit log)
        project_id = str(uuid.uuid4())
        await db_connection.execute(
            """
            INSERT INTO projects (id, tenant_id, name, description, status)
            VALUES ($1, $2, $3, $4, $5)
            """,
            project_id, tenant_id, "Audit Test Project", "Testing audit trail", "active"
        )
        
        # Check that audit log was created
        await db_connection.execute("SET row_security = off")
        audit_logs = await db_connection.fetch(
            """
            SELECT * FROM audit_logs 
            WHERE tenant_id = $1 AND table_name = 'projects' AND record_id = $2
            """,
            tenant_id, project_id
        )
        
        assert len(audit_logs) > 0, "Audit log should be created for project creation"
        
        audit_log = audit_logs[0]
        assert audit_log['operation'] == 'INSERT'
        assert audit_log['table_name'] == 'projects'
        
        # Clean up
        await db_connection.execute("DELETE FROM projects WHERE id = $1", project_id)
        await db_connection.execute("DELETE FROM audit_logs WHERE record_id = $1", project_id)

# Test runner
async def run_tests():
    """Run all tenant enforcement tests"""
    print("🧪 Running Tenant Enforcement Tests...")
    
    # Import pytest and run tests
    try:
        import pytest
        
        # Run specific test file
        result = pytest.main([
            __file__,
            "-v",
            "--tb=short"
        ])
        
        if result == 0:
            print("✅ All tenant enforcement tests passed!")
        else:
            print("❌ Some tests failed!")
            
        return result == 0
        
    except ImportError:
        print("⚠️  pytest not installed. Running basic tests...")
        
        # Basic test without pytest
        try:
            conn = await asyncpg.connect(**TEST_DB_CONFIG)
            
            # Test basic connectivity and RLS
            await conn.execute("SET app.tenant_id = 'test-tenant'")
            await conn.execute("SET ROLE application_role")
            
            # Try to query tenants table
            result = await conn.fetchval("SELECT COUNT(*) FROM tenants")
            print(f"✅ Basic connectivity test passed. Found {result} tenants.")
            
            await conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Basic test failed: {e}")
            return False

if __name__ == "__main__":
    asyncio.run(run_tests()) 