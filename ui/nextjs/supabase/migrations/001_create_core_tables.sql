-- Supabase Database Migration for Module 3: Database On-Ramp
-- This script creates the core tables with Row Level Security (RLS) policies
-- Run this in your Supabase SQL editor to set up the database foundation

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create tenants table
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    domain VARCHAR(255),
    plan VARCHAR(50) DEFAULT 'starter' CHECK (plan IN ('starter', 'pro', 'growth')),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'cancelled')),
    isolation_mode VARCHAR(50) DEFAULT 'shared' CHECK (isolation_mode IN ('shared', 'isolated')),
    
    -- Metadata
    settings JSONB DEFAULT '{}',
    limits JSONB DEFAULT '{"max_users": 10, "max_projects": 5, "max_storage_gb": 1}',
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);

-- Create users table with tenant association
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'viewer')),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'pending')),
    
    -- Authentication
    password_hash VARCHAR(255),
    last_login_at TIMESTAMP WITH TIME ZONE,
    
    -- GDPR compliance
    gdpr_consent_given BOOLEAN DEFAULT FALSE,
    gdpr_consent_date TIMESTAMP WITH TIME ZONE,
    gdpr_consent_ip VARCHAR(45),
    privacy_policy_version VARCHAR(50) DEFAULT '1.0',
    dpa_version VARCHAR(50) DEFAULT '1.0',
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(tenant_id, email)
);

-- Create projects table (tenant-aware)
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    project_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    
    -- Project configuration
    config JSONB DEFAULT '{}',
    tech_stack JSONB DEFAULT '{}',
    design_config JSONB DEFAULT '{}',
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    UNIQUE(tenant_id, name)
);

-- Create ideas table for admin approval workflow
CREATE TABLE IF NOT EXISTS ideas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    submitted_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Idea details
    project_name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    problem TEXT NOT NULL,
    solution TEXT NOT NULL,
    target_audience TEXT,
    key_features TEXT,
    business_model VARCHAR(100),
    category VARCHAR(100),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    
    -- Approval workflow
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'in_review')),
    admin_notes TEXT,
    reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    
    -- Timeline and budget estimates
    timeline VARCHAR(100),
    budget VARCHAR(100),
    
    -- Metadata
    submission_data JSONB DEFAULT '{}',
    approval_data JSONB DEFAULT '{}',
    
    -- Auto-promotion to project
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    promoted_at TIMESTAMP WITH TIME ZONE,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create design_recommendations table (tenant-aware)
CREATE TABLE IF NOT EXISTS design_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    project_type VARCHAR(50) NOT NULL,
    
    -- Design data
    wireframes JSONB NOT NULL DEFAULT '[]',
    style_guide JSONB NOT NULL DEFAULT '{}',
    figma_project_url VARCHAR(500),
    design_system JSONB DEFAULT '{}',
    reasoning TEXT,
    estimated_dev_time VARCHAR(50),
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

-- Create tech_stack_recommendations table (tenant-aware)
CREATE TABLE IF NOT EXISTS tech_stack_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    project_type VARCHAR(50) NOT NULL,
    
    -- Tech stack data
    frontend JSONB DEFAULT '[]',
    backend JSONB DEFAULT '[]',
    database JSONB DEFAULT '[]',
    deployment JSONB DEFAULT '[]',
    testing JSONB DEFAULT '[]',
    overall_score DECIMAL(3,1),
    reasoning TEXT,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

-- Create agent_events table (tenant-aware for event tracking)
CREATE TABLE IF NOT EXISTS agent_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    
    -- Event data
    event_type VARCHAR(50) NOT NULL,
    agent_name VARCHAR(100),
    stage VARCHAR(50),
    status VARCHAR(50),
    request_id VARCHAR(100),
    
    -- Event payload and results
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create audit_logs table for comprehensive audit trail
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Audit data
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    operation VARCHAR(20) NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    old_values JSONB,
    new_values JSONB,
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    
    -- Timing
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create privacy_consent_audit table for GDPR compliance
CREATE TABLE IF NOT EXISTS privacy_consent_audit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    consent_type VARCHAR(50) NOT NULL, -- 'gdpr', 'terms', 'privacy_policy', 'dpa'
    consent_given BOOLEAN NOT NULL,
    consent_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    consent_ip VARCHAR(45),
    document_version VARCHAR(50),
    user_agent TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_tenants_slug ON tenants(slug);
CREATE INDEX IF NOT EXISTS idx_tenants_status ON tenants(status);
CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_projects_tenant_id ON projects(tenant_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_ideas_tenant_id ON ideas(tenant_id);
CREATE INDEX IF NOT EXISTS idx_ideas_status ON ideas(status);
CREATE INDEX IF NOT EXISTS idx_ideas_submitted_by ON ideas(submitted_by);
CREATE INDEX IF NOT EXISTS idx_ideas_priority ON ideas(priority);
CREATE INDEX IF NOT EXISTS idx_ideas_category ON ideas(category);
CREATE INDEX IF NOT EXISTS idx_design_recommendations_tenant_id ON design_recommendations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_design_recommendations_project_id ON design_recommendations(project_id);
CREATE INDEX IF NOT EXISTS idx_tech_stack_recommendations_tenant_id ON tech_stack_recommendations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tech_stack_recommendations_project_id ON tech_stack_recommendations(project_id);
CREATE INDEX IF NOT EXISTS idx_agent_events_tenant_id ON agent_events(tenant_id);
CREATE INDEX IF NOT EXISTS idx_agent_events_project_id ON agent_events(project_id);
CREATE INDEX IF NOT EXISTS idx_agent_events_event_type ON agent_events(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant_id ON audit_logs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_privacy_consent_audit_user_id ON privacy_consent_audit(user_id);
CREATE INDEX IF NOT EXISTS idx_privacy_consent_audit_tenant_id ON privacy_consent_audit(tenant_id);
CREATE INDEX IF NOT EXISTS idx_privacy_consent_audit_consent_type ON privacy_consent_audit(consent_type);

-- Create application role for RLS
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'application_role') THEN
        CREATE ROLE application_role;
    END IF;
END
$$;

-- Enable Row Level Security
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE ideas ENABLE ROW LEVEL SECURITY;
ALTER TABLE design_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE tech_stack_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE privacy_consent_audit ENABLE ROW LEVEL SECURITY;

-- Create Row Level Security Policies

-- Tenants: Can only see own tenant
CREATE POLICY tenant_isolation ON tenants
    FOR ALL
    TO application_role
    USING (id = current_setting('app.current_tenant_id')::UUID);

-- Users: Can only see users in same tenant
CREATE POLICY user_tenant_isolation ON users
    FOR ALL  
    TO application_role
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Projects: Can only see projects in same tenant
CREATE POLICY project_tenant_isolation ON projects
    FOR ALL
    TO application_role
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Ideas: Can only see own tenant's ideas
CREATE POLICY ideas_tenant_isolation ON ideas
    FOR ALL
    TO application_role
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Design recommendations: Can only see own tenant's designs
CREATE POLICY design_tenant_isolation ON design_recommendations
    FOR ALL
    TO application_role
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Tech stack recommendations: Can only see own tenant's tech stacks
CREATE POLICY techstack_tenant_isolation ON tech_stack_recommendations
    FOR ALL
    TO application_role
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Agent events: Can only see own tenant's events
CREATE POLICY events_tenant_isolation ON agent_events
    FOR ALL
    TO application_role
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Audit logs: Can only see own tenant's audit logs
CREATE POLICY audit_tenant_isolation ON audit_logs
    FOR ALL
    TO application_role
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Privacy consent audit: Can only see own tenant's consent records
CREATE POLICY privacy_consent_tenant_isolation ON privacy_consent_audit
    FOR ALL
    TO application_role
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Grant necessary permissions to application role
GRANT USAGE ON SCHEMA public TO application_role;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO application_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO application_role;

-- Create trigger function for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ideas_updated_at BEFORE UPDATE ON ideas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_design_recommendations_updated_at BEFORE UPDATE ON design_recommendations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tech_stack_recommendations_updated_at BEFORE UPDATE ON tech_stack_recommendations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing (optional)
-- Uncomment the following lines if you want to insert test data

/*
INSERT INTO tenants (id, name, slug, plan, status) VALUES 
    ('550e8400-e29b-41d4-a716-446655440000', 'Test Tenant', 'test-tenant', 'growth', 'active');

INSERT INTO users (id, tenant_id, email, name, role, status) VALUES 
    ('550e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440000', 'admin@test.com', 'Test Admin', 'admin', 'active');
*/
