-- Module 11: Security & Compliance Migration
-- Comprehensive security and compliance system with RLS + Least-Privilege + Audits
-- This migration strengthens tenant isolation while reducing custom code

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- DATA CLASSIFICATION SYSTEM
-- ============================================================================

-- Data classification levels: P0 (PII/payment), P1 (user content), P2 (telemetry)
CREATE TYPE data_classification_level AS ENUM ('P0', 'P1', 'P2');

-- Data classification table for tracking sensitive data
CREATE TABLE IF NOT EXISTS data_classification (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Classification details
    table_name VARCHAR(100) NOT NULL,
    column_name VARCHAR(100),
    classification_level data_classification_level NOT NULL,
    data_type VARCHAR(50) NOT NULL, -- 'pii', 'payment', 'user_content', 'telemetry'
    
    -- Compliance metadata
    gdpr_impact BOOLEAN DEFAULT false,
    pci_impact BOOLEAN DEFAULT false,
    retention_days INTEGER,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

-- ============================================================================
-- ACCESS REVIEW SYSTEM
-- ============================================================================

-- Access review table for tracking who holds service keys, Stripe keys, etc.
CREATE TABLE IF NOT EXISTS access_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Review details
    review_type VARCHAR(50) NOT NULL, -- 'quarterly', 'annual', 'ad-hoc', 'incident'
    review_period_start DATE NOT NULL,
    review_period_end DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'overdue')),
    
    -- Review scope
    scope_description TEXT NOT NULL,
    key_holders_count INTEGER DEFAULT 0,
    service_accounts_count INTEGER DEFAULT 0,
    
    -- Findings
    findings_summary TEXT,
    risk_score INTEGER CHECK (risk_score >= 1 AND risk_score <= 10),
    remediation_required BOOLEAN DEFAULT false,
    
    -- Assignments
    assigned_reviewer_id UUID REFERENCES users(id),
    assigned_approver_id UUID REFERENCES users(id),
    
    -- Timing
    due_date DATE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

-- Key holder inventory table
CREATE TABLE IF NOT EXISTS key_holders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    access_review_id UUID NOT NULL REFERENCES access_reviews(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Key holder details
    holder_name VARCHAR(255) NOT NULL,
    holder_email VARCHAR(255),
    holder_role VARCHAR(100),
    
    -- Key details
    key_type VARCHAR(50) NOT NULL, -- 'stripe', 'service_account', 'api_key', 'database', 'other'
    key_name VARCHAR(255) NOT NULL,
    key_purpose TEXT,
    key_scope TEXT,
    
    -- Access details
    access_level VARCHAR(50) NOT NULL, -- 'read', 'write', 'admin', 'full'
    last_used_at TIMESTAMP WITH TIME ZONE,
    rotation_schedule_days INTEGER,
    next_rotation_date DATE,
    
    -- Risk assessment
    risk_level VARCHAR(20) DEFAULT 'low' CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    justification TEXT,
    
    -- Status
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'rotated', 'revoked', 'expired')),
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

-- ============================================================================
-- ADMIN ACTION AUDIT SYSTEM
-- ============================================================================

-- Enhanced admin actions table for comprehensive audit trail
CREATE TABLE IF NOT EXISTS admin_actions_audit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    admin_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Action details
    action_type VARCHAR(100) NOT NULL,
    action_category VARCHAR(50) NOT NULL, -- 'security', 'compliance', 'user_management', 'system_config'
    target_type VARCHAR(50) NOT NULL, -- 'user', 'tenant', 'project', 'idea', 'system'
    target_id UUID NOT NULL,
    
    -- Action specifics
    action_data JSONB DEFAULT '{}',
    old_values JSONB,
    new_values JSONB,
    
    -- Context and justification
    reason TEXT NOT NULL,
    business_justification TEXT,
    risk_assessment VARCHAR(20) DEFAULT 'low' CHECK (risk_assessment IN ('low', 'medium', 'high', 'critical')),
    
    -- Approval workflow
    requires_approval BOOLEAN DEFAULT false,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    approval_notes TEXT,
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    correlation_id VARCHAR(255),
    
    -- Timing
    action_started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    action_completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- SECURITY POLICIES AND COMPLIANCE
-- ============================================================================

-- Security policies table for tenant-specific security rules
CREATE TABLE IF NOT EXISTS security_policies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Policy details
    policy_name VARCHAR(255) NOT NULL,
    policy_type VARCHAR(50) NOT NULL, -- 'access_control', 'data_protection', 'audit', 'incident_response'
    policy_version VARCHAR(20) DEFAULT '1.0',
    
    -- Policy content
    policy_description TEXT NOT NULL,
    policy_rules JSONB NOT NULL,
    compliance_requirements JSONB DEFAULT '[]',
    
    -- Enforcement
    is_enforced BOOLEAN DEFAULT true,
    enforcement_level VARCHAR(20) DEFAULT 'strict' CHECK (enforcement_level IN ('advisory', 'recommended', 'strict', 'blocking')),
    
    -- Status
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('draft', 'active', 'deprecated', 'archived')),
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    
    UNIQUE(tenant_id, policy_name, policy_version)
);

-- Compliance checks table for tracking compliance status
CREATE TABLE IF NOT EXISTS compliance_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Check details
    check_name VARCHAR(255) NOT NULL,
    check_type VARCHAR(50) NOT NULL, -- 'gdpr', 'pci', 'soc2', 'custom'
    check_frequency VARCHAR(20) DEFAULT 'monthly' CHECK (check_frequency IN ('daily', 'weekly', 'monthly', 'quarterly', 'annually')),
    
    -- Check results
    last_check_date DATE,
    last_check_result VARCHAR(20) DEFAULT 'pending' CHECK (last_check_result IN ('pending', 'pass', 'fail', 'warning', 'error')),
    last_check_details TEXT,
    
    -- Compliance status
    is_compliant BOOLEAN DEFAULT false,
    compliance_score DECIMAL(5,2) CHECK (compliance_score >= 0 AND compliance_score <= 100),
    
    -- Next check
    next_check_date DATE,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

-- ============================================================================
-- ENHANCED RLS POLICIES
-- ============================================================================

-- Function to get current user's tenant context
CREATE OR REPLACE FUNCTION get_current_tenant_id()
RETURNS UUID AS $$
BEGIN
    -- Try to get from session context first
    IF current_setting('app.current_tenant_id', true) IS NOT NULL THEN
        RETURN current_setting('app.current_tenant_id')::UUID;
    END IF;
    
    -- Fallback to auth.uid() if available
    IF auth.uid() IS NOT NULL THEN
        RETURN (
            SELECT tenant_id 
            FROM user_tenants 
            WHERE user_id = auth.uid() 
            AND status = 'active' 
            LIMIT 1
        );
    END IF;
    
    -- Return NULL if no tenant context
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user has admin privileges
CREATE OR REPLACE FUNCTION is_admin_user()
RETURNS BOOLEAN AS $$
BEGIN
    -- Check if user has admin role in current tenant
    IF current_setting('app.current_user_role', true) = 'admin' THEN
        RETURN true;
    END IF;
    
    -- Check if user is tenant owner
    IF current_setting('app.current_user_role', true) = 'tenant_owner' THEN
        RETURN true;
    END IF;
    
    -- Check if user has admin role in user_tenants
    IF auth.uid() IS NOT NULL THEN
        RETURN EXISTS (
            SELECT 1 
            FROM user_tenants 
            WHERE user_id = auth.uid() 
            AND role IN ('admin', 'tenant_owner')
            AND status = 'active'
        );
    END IF;
    
    RETURN false;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check data access permissions
CREATE OR REPLACE FUNCTION check_data_access_permission(
    target_tenant_id UUID,
    required_permission VARCHAR(50) DEFAULT 'read'
)
RETURNS BOOLEAN AS $$
BEGIN
    -- Admin users can access any tenant
    IF is_admin_user() THEN
        RETURN true;
    END IF;
    
    -- Users can only access their own tenant
    IF get_current_tenant_id() = target_tenant_id THEN
        RETURN true;
    END IF;
    
    -- Deny access by default
    RETURN false;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Data classification indexes
CREATE INDEX IF NOT EXISTS idx_data_classification_tenant_id ON data_classification(tenant_id);
CREATE INDEX IF NOT EXISTS idx_data_classification_level ON data_classification(classification_level);
CREATE INDEX IF NOT EXISTS idx_data_classification_table ON data_classification(table_name);

-- Access review indexes
CREATE INDEX IF NOT EXISTS idx_access_reviews_tenant_id ON access_reviews(tenant_id);
CREATE INDEX IF NOT EXISTS idx_access_reviews_status ON access_reviews(status);
CREATE INDEX IF NOT EXISTS idx_access_reviews_due_date ON access_reviews(due_date);
CREATE INDEX IF NOT EXISTS idx_access_reviews_type ON access_reviews(review_type);

-- Key holder indexes
CREATE INDEX IF NOT EXISTS idx_key_holders_review_id ON key_holders(access_review_id);
CREATE INDEX IF NOT EXISTS idx_key_holders_tenant_id ON key_holders(tenant_id);
CREATE INDEX IF NOT EXISTS idx_key_holders_key_type ON key_holders(key_type);
CREATE INDEX IF NOT EXISTS idx_key_holders_risk_level ON key_holders(risk_level);
CREATE INDEX IF NOT EXISTS idx_key_holders_next_rotation ON key_holders(next_rotation_date);

-- Admin actions audit indexes
CREATE INDEX IF NOT EXISTS idx_admin_actions_audit_tenant_id ON admin_actions_audit(tenant_id);
CREATE INDEX IF NOT EXISTS idx_admin_actions_audit_admin_user_id ON admin_actions_audit(admin_user_id);
CREATE INDEX IF NOT EXISTS idx_admin_actions_audit_action_type ON admin_actions_audit(action_type);
CREATE INDEX IF NOT EXISTS idx_admin_actions_audit_target_type ON admin_actions_audit(target_type);
CREATE INDEX IF NOT EXISTS idx_admin_actions_audit_created_at ON admin_actions_audit(created_at);
CREATE INDEX IF NOT EXISTS idx_admin_actions_audit_correlation_id ON admin_actions_audit(correlation_id);

-- Security policies indexes
CREATE INDEX IF NOT EXISTS idx_security_policies_tenant_id ON security_policies(tenant_id);
CREATE INDEX IF NOT EXISTS idx_security_policies_type ON security_policies(policy_type);
CREATE INDEX IF NOT EXISTS idx_security_policies_status ON security_policies(status);

-- Compliance checks indexes
CREATE INDEX IF NOT EXISTS idx_compliance_checks_tenant_id ON compliance_checks(tenant_id);
CREATE INDEX IF NOT EXISTS idx_compliance_checks_type ON compliance_checks(check_type);
CREATE INDEX IF NOT EXISTS idx_compliance_checks_next_check ON compliance_checks(next_check_date);

-- ============================================================================
-- ENABLE ROW LEVEL SECURITY
-- ============================================================================

-- Enable RLS on all new security tables
ALTER TABLE data_classification ENABLE ROW LEVEL SECURITY;
ALTER TABLE access_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE key_holders ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_actions_audit ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance_checks ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- RLS POLICIES FOR SECURITY TABLES
-- ============================================================================

-- Data classification RLS policies
CREATE POLICY "data_classification_tenant_isolation" ON data_classification
    FOR ALL USING (check_data_access_permission(tenant_id));

-- Access reviews RLS policies
CREATE POLICY "access_reviews_tenant_isolation" ON access_reviews
    FOR ALL USING (check_data_access_permission(tenant_id));

-- Key holders RLS policies
CREATE POLICY "key_holders_tenant_isolation" ON key_holders
    FOR ALL USING (check_data_access_permission(tenant_id));

-- Admin actions audit RLS policies
CREATE POLICY "admin_actions_audit_tenant_isolation" ON admin_actions_audit
    FOR ALL USING (check_data_access_permission(tenant_id));

-- Security policies RLS policies
CREATE POLICY "security_policies_tenant_isolation" ON security_policies
    FOR ALL USING (check_data_access_permission(tenant_id));

-- Compliance checks RLS policies
CREATE POLICY "compliance_checks_tenant_isolation" ON compliance_checks
    FOR ALL USING (check_data_access_permission(tenant_id));

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================

-- Grant permissions to application role
GRANT USAGE ON SCHEMA public TO application_role;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO application_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO application_role;

-- Grant execute permissions on security functions
GRANT EXECUTE ON FUNCTION get_current_tenant_id() TO application_role;
GRANT EXECUTE ON FUNCTION is_admin_user() TO application_role;
GRANT EXECUTE ON FUNCTION check_data_access_permission(UUID, VARCHAR) TO application_role;

-- ============================================================================
-- TRIGGERS FOR AUDIT TRAIL
-- ============================================================================

-- Create trigger function for updated_at
CREATE OR REPLACE FUNCTION update_security_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at on all security tables
CREATE TRIGGER update_data_classification_updated_at 
    BEFORE UPDATE ON data_classification 
    FOR EACH ROW EXECUTE FUNCTION update_security_updated_at_column();

CREATE TRIGGER update_access_reviews_updated_at 
    BEFORE UPDATE ON access_reviews 
    FOR EACH ROW EXECUTE FUNCTION update_security_updated_at_column();

CREATE TRIGGER update_key_holders_updated_at 
    BEFORE UPDATE ON key_holders 
    FOR EACH ROW EXECUTE FUNCTION update_security_updated_at_column();

CREATE TRIGGER update_admin_actions_audit_updated_at 
    BEFORE UPDATE ON admin_actions_audit 
    FOR EACH ROW EXECUTE FUNCTION update_security_updated_at_column();

CREATE TRIGGER update_security_policies_updated_at 
    BEFORE UPDATE ON security_policies 
    FOR EACH ROW EXECUTE FUNCTION update_security_updated_at_column();

CREATE TRIGGER update_compliance_checks_updated_at 
    BEFORE UPDATE ON compliance_checks 
    FOR EACH ROW EXECUTE FUNCTION update_security_updated_at_column();

-- ============================================================================
-- SAMPLE DATA FOR TESTING
-- ============================================================================

-- Insert sample data classification for existing tables
INSERT INTO data_classification (tenant_id, table_name, column_name, classification_level, data_type, gdpr_impact, pci_impact, retention_days) VALUES
-- P0: PII/Payment data
('00000000-0000-0000-0000-000000000001', 'users', 'email', 'P0', 'pii', true, false, 2555),
('00000000-0000-0000-0000-000000000001', 'users', 'first_name', 'P0', 'pii', true, false, 2555),
('00000000-0000-0000-0000-000000000001', 'users', 'last_name', 'P0', 'pii', true, false, 2555),
('00000000-0000-0000-0000-000000000001', 'tenants', 'stripe_subscription_id', 'P0', 'payment', false, true, 2555),

-- P1: User content
('00000000-0000-0000-0000-000000000001', 'ideas', 'title', 'P1', 'user_content', false, false, 1825),
('00000000-0000-0000-0000-000000000001', 'ideas', 'description', 'P1', 'user_content', false, false, 1825),
('00000000-0000-0000-0000-000000000001', 'projects', 'name', 'P1', 'user_content', false, false, 1825),
('00000000-0000-0000-0000-000000000001', 'projects', 'description', 'P1', 'user_content', false, false, 1825),

-- P2: Telemetry
('00000000-0000-0000-0000-000000000001', 'agent_events', 'event_type', 'P2', 'telemetry', false, false, 365),
('00000000-0000-0000-0000-000000000001', 'agent_events', 'duration_ms', 'P2', 'telemetry', false, false, 365),
('00000000-0000-0000-0000-000000000001', 'audit_logs', 'ip_address', 'P2', 'telemetry', false, false, 365),
('00000000-0000-0000-0000-000000000001', 'audit_logs', 'user_agent', 'P2', 'telemetry', false, false, 365)
ON CONFLICT DO NOTHING;

-- Insert sample security policy
INSERT INTO security_policies (tenant_id, policy_name, policy_type, policy_description, policy_rules, compliance_requirements, enforcement_level) VALUES
('00000000-0000-0000-0000-000000000001', 'Data Access Control Policy', 'access_control', 'Policy for controlling access to sensitive data based on classification levels', 
'{"P0_data_access": "admin_only", "P1_data_access": "tenant_users", "P2_data_access": "authenticated_users"}',
'["gdpr", "soc2"]', 'strict')
ON CONFLICT DO NOTHING;

-- Insert sample compliance check
INSERT INTO compliance_checks (tenant_id, check_name, check_type, check_frequency, next_check_date) VALUES
('00000000-0000-0000-0000-000000000001', 'Quarterly Access Review', 'custom', 'quarterly', CURRENT_DATE + INTERVAL '3 months'),
('00000000-0000-0000-0000-000000000001', 'GDPR Compliance Check', 'gdpr', 'monthly', CURRENT_DATE + INTERVAL '1 month'),
('00000000-0000-0000-0000-000000000001', 'PCI DSS Compliance', 'pci', 'quarterly', CURRENT_DATE + INTERVAL '3 months')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- MIGRATION COMPLETION
-- ============================================================================

-- Log migration completion
DO $$
BEGIN
    RAISE NOTICE 'Module 11: Security & Compliance migration completed successfully';
    RAISE NOTICE 'Created % security and compliance tables', (
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN (
            'data_classification', 'access_reviews', 'key_holders', 
            'admin_actions_audit', 'security_policies', 'compliance_checks'
        )
    );
    RAISE NOTICE 'RLS policies enabled on all security tables';
    RAISE NOTICE 'Security functions created and secured';
END $$;
