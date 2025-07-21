-- Migration 003: Create ideas table for admin approval workflow
-- Night 54: Admin console: approve/reject ideas, upgrade tenant to isolated.
-- Created: 2024-01-15

-- Create ideas table for managing submitted ideas
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

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_ideas_tenant_id ON ideas(tenant_id);
CREATE INDEX IF NOT EXISTS idx_ideas_status ON ideas(status);
CREATE INDEX IF NOT EXISTS idx_ideas_submitted_by ON ideas(submitted_by);
CREATE INDEX IF NOT EXISTS idx_ideas_reviewed_by ON ideas(reviewed_by);
CREATE INDEX IF NOT EXISTS idx_ideas_priority ON ideas(priority);
CREATE INDEX IF NOT EXISTS idx_ideas_category ON ideas(category);
CREATE INDEX IF NOT EXISTS idx_ideas_created_at ON ideas(created_at);

-- Create composite indexes for common admin queries
CREATE INDEX IF NOT EXISTS idx_ideas_status_priority_date ON ideas(status, priority, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ideas_tenant_status ON ideas(tenant_id, status);

-- Enable Row Level Security
ALTER TABLE ideas ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for tenant isolation
CREATE POLICY ideas_tenant_isolation ON ideas
    FOR ALL
    TO application_role
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Create admin RLS policy (admins can see all ideas)
CREATE POLICY ideas_admin_access ON ideas
    FOR ALL
    TO application_role
    USING (
        current_setting('app.current_user_role', true) = 'admin'
        OR tenant_id = current_setting('app.current_tenant_id')::UUID
    );

-- Grant permissions to application role
GRANT ALL PRIVILEGES ON TABLE ideas TO application_role;

-- Create trigger for updated_at
CREATE TRIGGER update_ideas_updated_at
    BEFORE UPDATE ON ideas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create admin actions audit table
CREATE TABLE IF NOT EXISTS admin_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    admin_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL,
    target_type VARCHAR(50) NOT NULL, -- 'idea', 'tenant', 'user', etc.
    target_id UUID NOT NULL,
    
    -- Action details
    action_data JSONB DEFAULT '{}',
    reason TEXT,
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    
    -- Timing
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for admin actions
CREATE INDEX IF NOT EXISTS idx_admin_actions_admin_user_id ON admin_actions(admin_user_id);
CREATE INDEX IF NOT EXISTS idx_admin_actions_action_type ON admin_actions(action_type);
CREATE INDEX IF NOT EXISTS idx_admin_actions_target_type ON admin_actions(target_type);
CREATE INDEX IF NOT EXISTS idx_admin_actions_target_id ON admin_actions(target_id);
CREATE INDEX IF NOT EXISTS idx_admin_actions_created_at ON admin_actions(created_at);

-- Enable RLS for admin actions
ALTER TABLE admin_actions ENABLE ROW LEVEL SECURITY;

-- Create admin actions RLS policy (only admins can access)
CREATE POLICY admin_actions_admin_only ON admin_actions
    FOR ALL
    TO application_role
    USING (current_setting('app.current_user_role', true) = 'admin');

-- Grant permissions
GRANT ALL PRIVILEGES ON TABLE admin_actions TO application_role;

-- Create view for idea summary statistics
CREATE OR REPLACE VIEW idea_statistics AS
SELECT 
    COUNT(*) as total_ideas,
    COUNT(*) FILTER (WHERE status = 'pending') as pending_ideas,
    COUNT(*) FILTER (WHERE status = 'approved') as approved_ideas,
    COUNT(*) FILTER (WHERE status = 'rejected') as rejected_ideas,
    COUNT(*) FILTER (WHERE status = 'in_review') as in_review_ideas,
    COUNT(*) FILTER (WHERE priority = 'high') as high_priority_ideas,
    COUNT(*) FILTER (WHERE priority = 'medium') as medium_priority_ideas,
    COUNT(*) FILTER (WHERE priority = 'low') as low_priority_ideas,
    AVG(EXTRACT(days FROM (COALESCE(reviewed_at, NOW()) - created_at))) as avg_review_time_days
FROM ideas;

-- Grant view access
GRANT SELECT ON idea_statistics TO application_role;

COMMENT ON TABLE ideas IS 'Submitted ideas awaiting admin approval before becoming projects';
COMMENT ON TABLE admin_actions IS 'Audit trail for admin actions performed in the system';
COMMENT ON VIEW idea_statistics IS 'Summary statistics for idea submission and approval metrics'; 