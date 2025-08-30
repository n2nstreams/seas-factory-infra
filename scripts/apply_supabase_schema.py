#!/usr/bin/env python3
"""
Apply Supabase Schema Migrations Script
Applies the core table schema to Supabase for Module 3 completion
"""

import os
import sys
import logging
import asyncio
import psycopg2
from psycopg2.extras import RealDictCursor

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SupabaseSchemaApplier:
    """Applies the core schema to Supabase"""
    
    def __init__(self):
        self.settings = get_settings()
        self.supabase_conn = None
        
    async def initialize_supabase_connection(self):
        """Initialize Supabase database connection"""
        try:
            logger.info("🔌 Initializing Supabase database connection...")
            
            self.supabase_conn = psycopg2.connect(
                host=self.settings.supabase.db_host,
                port=self.settings.supabase.db_port,
                database=self.settings.supabase.db_name,
                user=self.settings.supabase.db_user,
                password=self.settings.supabase.db_password.get_secret_value()
            )
            
            logger.info("✅ Supabase database connection established successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to establish Supabase connection: {str(e)}")
            return False
    
    async def create_extensions(self):
        """Create necessary extensions"""
        try:
            logger.info("🔧 Creating extensions...")
            
            with self.supabase_conn.cursor() as cursor:
                cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
                cursor.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
                cursor.execute('CREATE EXTENSION IF NOT EXISTS "vector"')
                
            self.supabase_conn.commit()
            logger.info("✅ Extensions created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create extensions: {str(e)}")
            return False
    
    async def create_tenants_table(self):
        """Create tenants table"""
        try:
            logger.info("🏢 Creating tenants table...")
            
            with self.supabase_conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tenants (
                        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        name VARCHAR(255) NOT NULL,
                        slug VARCHAR(100) UNIQUE NOT NULL,
                        domain VARCHAR(255),
                        plan VARCHAR(50) DEFAULT 'starter' CHECK (plan IN ('starter', 'pro', 'growth')),
                        status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'cancelled')),
                        isolation_mode VARCHAR(50) DEFAULT 'shared' CHECK (isolation_mode IN ('shared', 'isolated')),
                        settings JSONB DEFAULT '{}',
                        limits JSONB DEFAULT '{"max_users": 10, "max_projects": 5, "max_storage_gb": 1}',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        created_by UUID,
                        updated_by UUID
                    )
                """)
                
                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_tenants_slug ON tenants(slug)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_tenants_status ON tenants(status)')
                
            self.supabase_conn.commit()
            logger.info("✅ Tenants table created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create tenants table: {str(e)}")
            return False
    
    async def create_users_table(self):
        """Create users table"""
        try:
            logger.info("👥 Creating users table...")
            
            with self.supabase_conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                        email VARCHAR(255) NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'viewer')),
                        status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'pending')),
                        password_hash VARCHAR(255),
                        last_login_at TIMESTAMP WITH TIME ZONE,
                        gdpr_consent_given BOOLEAN DEFAULT FALSE,
                        gdpr_consent_date TIMESTAMP WITH TIME ZONE,
                        gdpr_consent_ip VARCHAR(45),
                        privacy_policy_version VARCHAR(50) DEFAULT '1.0',
                        dpa_version VARCHAR(50) DEFAULT '1.0',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        UNIQUE(tenant_id, email)
                    )
                """)
                
                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
                
            self.supabase_conn.commit()
            logger.info("✅ Users table created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create users table: {str(e)}")
            return False
    
    async def create_projects_table(self):
        """Create projects table"""
        try:
            logger.info("🚀 Creating projects table...")
            
            with self.supabase_conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS projects (
                        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        project_type VARCHAR(50) NOT NULL,
                        status VARCHAR(50) DEFAULT 'active',
                        config JSONB DEFAULT '{}',
                        tech_stack JSONB DEFAULT '{}',
                        design_config JSONB DEFAULT '{}',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        created_by UUID REFERENCES users(id),
                        UNIQUE(tenant_id, name)
                    )
                """)
                
                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_tenant_id ON projects(tenant_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)')
                
            self.supabase_conn.commit()
            logger.info("✅ Projects table created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create projects table: {str(e)}")
            return False
    
    async def create_ideas_table(self):
        """Create ideas table"""
        try:
            logger.info("💡 Creating ideas table...")
            
            with self.supabase_conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ideas (
                        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                        submitted_by UUID REFERENCES users(id) ON DELETE SET NULL,
                        project_name VARCHAR(255) NOT NULL,
                        description TEXT NOT NULL,
                        problem TEXT NOT NULL,
                        solution TEXT NOT NULL,
                        target_audience TEXT,
                        key_features TEXT,
                        business_model VARCHAR(100),
                        category VARCHAR(100),
                        priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
                        status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'in_review')),
                        admin_notes TEXT,
                        reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL,
                        reviewed_at TIMESTAMP WITH TIME ZONE,
                        timeline VARCHAR(100),
                        budget VARCHAR(100),
                        submission_data JSONB DEFAULT '{}',
                        approval_data JSONB DEFAULT '{}',
                        project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
                        promoted_at TIMESTAMP WITH TIME ZONE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_ideas_tenant_id ON ideas(tenant_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_ideas_status ON ideas(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_ideas_submitted_by ON ideas(submitted_by)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_ideas_priority ON ideas(priority)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_ideas_category ON ideas(category)')
                
            self.supabase_conn.commit()
            logger.info("✅ Ideas table created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create ideas table: {str(e)}")
            return False
    
    async def create_design_recommendations_table(self):
        """Create design recommendations table"""
        try:
            logger.info("🎨 Creating design recommendations table...")
            
            with self.supabase_conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS design_recommendations (
                        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                        project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
                        recommendation_type VARCHAR(100) NOT NULL,
                        content TEXT NOT NULL,
                        priority VARCHAR(20) DEFAULT 'medium',
                        category VARCHAR(100),
                        tags TEXT[],
                        metadata JSONB DEFAULT '{}',
                        status VARCHAR(50) DEFAULT 'active',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_design_recommendations_tenant_id ON design_recommendations(tenant_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_design_recommendations_project_id ON design_recommendations(project_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_design_recommendations_status ON design_recommendations(status)')
                
            self.supabase_conn.commit()
            logger.info("✅ Design recommendations table created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create design recommendations table: {str(e)}")
            return False
    
    async def create_tech_stack_recommendations_table(self):
        """Create tech stack recommendations table"""
        try:
            logger.info("⚙️ Creating tech stack recommendations table...")
            
            with self.supabase_conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tech_stack_recommendations (
                        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                        project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
                        tech_stack JSONB NOT NULL,
                        priority VARCHAR(20) DEFAULT 'medium',
                        category VARCHAR(100),
                        tags TEXT[],
                        metadata JSONB DEFAULT '{}',
                        status VARCHAR(50) DEFAULT 'active',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_tech_stack_recommendations_tenant_id ON tech_stack_recommendations(tenant_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_tech_stack_recommendations_project_id ON tech_stack_recommendations(project_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_tech_stack_recommendations_status ON tech_stack_recommendations(status)')
                
            self.supabase_conn.commit()
            logger.info("✅ Tech stack recommendations table created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create tech stack recommendations table: {str(e)}")
            return False
    
    async def create_agent_events_table(self):
        """Create agent events table"""
        try:
            logger.info("🤖 Creating agent events table...")
            
            with self.supabase_conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS agent_events (
                        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                        project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
                        user_id UUID REFERENCES users(id) ON DELETE SET NULL,
                        agent_type VARCHAR(100) NOT NULL,
                        event_type VARCHAR(100) NOT NULL,
                        status VARCHAR(50) DEFAULT 'pending',
                        metadata JSONB DEFAULT '{}',
                        result JSONB DEFAULT '{}',
                        error_message TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_events_tenant_id ON agent_events(tenant_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_events_agent_type ON agent_events(agent_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_events_event_type ON agent_events(event_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_events_status ON agent_events(status)')
                
            self.supabase_conn.commit()
            logger.info("✅ Agent events table created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create agent events table: {str(e)}")
            return False
    
    async def verify_schema(self):
        """Verify that the schema was applied correctly"""
        try:
            logger.info("🔍 Verifying schema application...")
            
            expected_tables = [
                'tenants', 'users', 'projects', 'ideas', 
                'design_recommendations', 'tech_stack_recommendations', 'agent_events'
            ]
            
            with self.supabase_conn.cursor() as cursor:
                for table in expected_tables:
                    cursor.execute(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = %s
                        )
                    """, (table,))
                    
                    exists = cursor.fetchone()[0]
                    if exists:
                        logger.info(f"✅ Table {table} exists")
                    else:
                        logger.error(f"❌ Table {table} missing")
                        return False
            
            logger.info("✅ All expected tables verified")
            return True
            
        except Exception as e:
            logger.error(f"❌ Schema verification failed: {str(e)}")
            return False
    
    async def run_schema_application(self):
        """Run the complete schema application process"""
        try:
            logger.info("🚀 Starting Supabase Schema Application")
            logger.info("=" * 50)
            
            # Step 1: Initialize connection
            if not await self.initialize_supabase_connection():
                return False
            
            # Step 2: Create extensions
            if not await self.create_extensions():
                return False
            
            # Step 3: Create tables in dependency order
            if not await self.create_tenants_table():
                return False
            
            if not await self.create_users_table():
                return False
            
            if not await self.create_projects_table():
                return False
            
            if not await self.create_ideas_table():
                return False
            
            if not await self.create_design_recommendations_table():
                return False
            
            if not await self.create_tech_stack_recommendations_table():
                return False
            
            if not await self.create_agent_events_table():
                return False
            
            # Step 4: Verify schema
            if not await self.verify_schema():
                return False
            
            logger.info("🎉 Schema application completed successfully!")
            logger.info("✅ All core tables created")
            logger.info("✅ Indexes created")
            logger.info("🚀 Ready for data migration")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Schema application failed: {str(e)}")
            return False
        
        finally:
            if self.supabase_conn:
                self.supabase_conn.close()
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.supabase_conn:
                self.supabase_conn.close()
                logger.info("🧹 Cleanup completed")
        except Exception as e:
            logger.warning(f"⚠️ Cleanup warning: {str(e)}")

async def main():
    """Main schema application execution"""
    applier = SupabaseSchemaApplier()
    
    try:
        success = await applier.run_schema_application()
        
        if success:
            logger.info("🎉 Supabase Schema Application - SUCCESSFUL")
            logger.info("✅ Core tables created with proper structure")
            logger.info("✅ Ready to proceed with data migration")
        else:
            logger.error("❌ Supabase Schema Application - FAILED")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Schema application execution failed: {str(e)}")
        sys.exit(1)
    
    finally:
        await applier.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
