-- Migration 007: Create license scan results table
-- Night 64: License scan agent (OSS Review Toolkit) - fail pipeline on GPL

-- Create license scan results table
CREATE TABLE IF NOT EXISTS license_scan_results (
    id SERIAL PRIMARY KEY,
    scan_id VARCHAR(255) UNIQUE NOT NULL,
    tenant_id VARCHAR(255) NOT NULL,
    project_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    passed BOOLEAN NOT NULL DEFAULT false,
    pipeline_should_fail BOOLEAN NOT NULL DEFAULT false,
    failure_reason TEXT,
    scan_start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    scan_end_time TIMESTAMP WITH TIME ZONE,
    ort_result JSONB,
    recommendations JSONB DEFAULT '[]',
    action_items JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for performance
CREATE INDEX idx_license_scan_results_tenant_id ON license_scan_results(tenant_id);
CREATE INDEX idx_license_scan_results_project_id ON license_scan_results(project_id);
CREATE INDEX idx_license_scan_results_scan_start_time ON license_scan_results(scan_start_time DESC);
CREATE INDEX idx_license_scan_results_status ON license_scan_results(status);
CREATE INDEX idx_license_scan_results_passed ON license_scan_results(passed);

-- Create composite index for common queries
CREATE INDEX idx_license_scan_results_tenant_project ON license_scan_results(tenant_id, project_id, scan_start_time DESC);

-- Add row-level security for tenant isolation
ALTER TABLE license_scan_results ENABLE ROW LEVEL SECURITY;

-- Create policy for tenant isolation
CREATE POLICY license_scan_results_tenant_isolation ON license_scan_results
    USING (tenant_id = current_setting('app.tenant_id', true));

-- Grant permissions to the application role
GRANT SELECT, INSERT, UPDATE, DELETE ON license_scan_results TO factoryadmin;
GRANT USAGE, SELECT ON SEQUENCE license_scan_results_id_seq TO factoryadmin;

-- Create license violations table for detailed violation tracking
CREATE TABLE IF NOT EXISTS license_violations (
    id SERIAL PRIMARY KEY,
    scan_id VARCHAR(255) NOT NULL REFERENCES license_scan_results(scan_id) ON DELETE CASCADE,
    tenant_id VARCHAR(255) NOT NULL,
    package_name VARCHAR(255) NOT NULL,
    package_version VARCHAR(255),
    package_manager VARCHAR(50),
    license_name VARCHAR(255) NOT NULL,
    license_type VARCHAR(100),
    risk_level VARCHAR(50) NOT NULL DEFAULT 'low',
    violation_type VARCHAR(50) NOT NULL, -- 'gpl', 'copyleft', 'unknown', 'denied'
    is_gpl BOOLEAN NOT NULL DEFAULT false,
    is_copyleft BOOLEAN NOT NULL DEFAULT false,
    file_path TEXT,
    confidence DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for license violations
CREATE INDEX idx_license_violations_scan_id ON license_violations(scan_id);
CREATE INDEX idx_license_violations_tenant_id ON license_violations(tenant_id);
CREATE INDEX idx_license_violations_package_name ON license_violations(package_name);
CREATE INDEX idx_license_violations_license_name ON license_violations(license_name);
CREATE INDEX idx_license_violations_risk_level ON license_violations(risk_level);
CREATE INDEX idx_license_violations_violation_type ON license_violations(violation_type);
CREATE INDEX idx_license_violations_is_gpl ON license_violations(is_gpl);

-- Add row-level security for license violations
ALTER TABLE license_violations ENABLE ROW LEVEL SECURITY;

-- Create policy for tenant isolation on violations
CREATE POLICY license_violations_tenant_isolation ON license_violations
    USING (tenant_id = current_setting('app.tenant_id', true));

-- Grant permissions to the application role
GRANT SELECT, INSERT, UPDATE, DELETE ON license_violations TO factoryadmin;
GRANT USAGE, SELECT ON SEQUENCE license_violations_id_seq TO factoryadmin;

-- Create license policies table for custom tenant policies
CREATE TABLE IF NOT EXISTS license_policies (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    policy_name VARCHAR(255) NOT NULL,
    is_default BOOLEAN NOT NULL DEFAULT false,
    allowed_licenses JSONB DEFAULT '[]',
    denied_licenses JSONB DEFAULT '[]',
    gpl_policy VARCHAR(20) NOT NULL DEFAULT 'deny', -- 'deny', 'allow', 'warn'
    copyleft_policy VARCHAR(20) NOT NULL DEFAULT 'warn', -- 'deny', 'allow', 'warn'
    unknown_license_policy VARCHAR(20) NOT NULL DEFAULT 'warn', -- 'deny', 'allow', 'warn'
    risk_threshold VARCHAR(20) NOT NULL DEFAULT 'high', -- 'safe', 'low', 'medium', 'high', 'critical'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, policy_name)
);

-- Add indexes for license policies
CREATE INDEX idx_license_policies_tenant_id ON license_policies(tenant_id);
CREATE INDEX idx_license_policies_is_default ON license_policies(is_default);

-- Add row-level security for license policies
ALTER TABLE license_policies ENABLE ROW LEVEL SECURITY;

-- Create policy for tenant isolation on policies
CREATE POLICY license_policies_tenant_isolation ON license_policies
    USING (tenant_id = current_setting('app.tenant_id', true));

-- Grant permissions to the application role
GRANT SELECT, INSERT, UPDATE, DELETE ON license_policies TO factoryadmin;
GRANT USAGE, SELECT ON SEQUENCE license_policies_id_seq TO factoryadmin;

-- Create a view for license scan summaries
CREATE OR REPLACE VIEW license_scan_summary AS
SELECT 
    lsr.tenant_id,
    lsr.project_id,
    COUNT(*) as total_scans,
    COUNT(*) FILTER (WHERE lsr.passed = true) as passed_scans,
    COUNT(*) FILTER (WHERE lsr.passed = false) as failed_scans,
    COUNT(*) FILTER (WHERE lsr.pipeline_should_fail = true) as pipeline_failures,
    MAX(lsr.scan_start_time) as last_scan_time,
    COUNT(DISTINCT lv.package_name) FILTER (WHERE lv.is_gpl = true) as gpl_packages_found,
    COUNT(DISTINCT lv.package_name) FILTER (WHERE lv.is_copyleft = true) as copyleft_packages_found,
    ARRAY_AGG(DISTINCT lv.license_name) FILTER (WHERE lv.is_gpl = true) as gpl_licenses_found
FROM license_scan_results lsr
LEFT JOIN license_violations lv ON lsr.scan_id = lv.scan_id
GROUP BY lsr.tenant_id, lsr.project_id;

-- Grant permissions on the view
GRANT SELECT ON license_scan_summary TO factoryadmin;

-- Create function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_license_scan_results_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updated_at
CREATE TRIGGER trigger_license_scan_results_updated_at
    BEFORE UPDATE ON license_scan_results
    FOR EACH ROW
    EXECUTE FUNCTION update_license_scan_results_updated_at();

-- Create function to update license policies updated_at timestamp
CREATE OR REPLACE FUNCTION update_license_policies_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for license policies updated_at
CREATE TRIGGER trigger_license_policies_updated_at
    BEFORE UPDATE ON license_policies
    FOR EACH ROW
    EXECUTE FUNCTION update_license_policies_updated_at();

-- Insert default license policy for each tenant
INSERT INTO license_policies (
    tenant_id, 
    policy_name, 
    is_default, 
    allowed_licenses, 
    denied_licenses, 
    gpl_policy, 
    copyleft_policy, 
    unknown_license_policy,
    risk_threshold
) VALUES (
    'default',
    'Default Policy',
    true,
    '["MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause", "ISC", "Unlicense", "CC0-1.0"]',
    '["GPL-2.0", "GPL-3.0", "AGPL-3.0", "GPL-2.0+", "GPL-3.0+"]',
    'deny',
    'warn',
    'warn',
    'high'
) ON CONFLICT (tenant_id, policy_name) DO NOTHING;

-- Create function to get license scan metrics for a tenant
CREATE OR REPLACE FUNCTION get_license_scan_metrics(p_tenant_id VARCHAR(255))
RETURNS TABLE (
    total_scans BIGINT,
    passed_scans BIGINT,
    failed_scans BIGINT,
    gpl_violations BIGINT,
    avg_scan_duration NUMERIC,
    last_scan_time TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_scans,
        COUNT(*) FILTER (WHERE passed = true) as passed_scans,
        COUNT(*) FILTER (WHERE passed = false) as failed_scans,
        COUNT(*) FILTER (WHERE pipeline_should_fail = true AND failure_reason LIKE '%GPL%') as gpl_violations,
        AVG(EXTRACT(EPOCH FROM (scan_end_time - scan_start_time))) as avg_scan_duration,
        MAX(scan_start_time) as last_scan_time
    FROM license_scan_results
    WHERE tenant_id = p_tenant_id;
END;
$$ LANGUAGE plpgsql;

-- Grant execute permission on the function
GRANT EXECUTE ON FUNCTION get_license_scan_metrics TO factoryadmin;

-- Create function to clean up old scan results (for maintenance)
CREATE OR REPLACE FUNCTION cleanup_old_license_scans(p_days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete scan results older than specified days
    DELETE FROM license_scan_results
    WHERE scan_start_time < NOW() - INTERVAL '1 day' * p_days_to_keep;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Grant execute permission on the cleanup function
GRANT EXECUTE ON FUNCTION cleanup_old_license_scans TO factoryadmin;

-- Add comments for documentation
COMMENT ON TABLE license_scan_results IS 'Stores results from OSS Review Toolkit (ORT) license scans for Night 64 implementation';
COMMENT ON TABLE license_violations IS 'Detailed license violations found during scans';
COMMENT ON TABLE license_policies IS 'Custom license policies per tenant';
COMMENT ON VIEW license_scan_summary IS 'Summary view of license scan results by tenant and project';
COMMENT ON FUNCTION get_license_scan_metrics IS 'Returns aggregated license scan metrics for a tenant';
COMMENT ON FUNCTION cleanup_old_license_scans IS 'Maintenance function to clean up old license scan results';

-- Log the migration
INSERT INTO schema_migrations (version, description, applied_at) 
VALUES ('007', 'Create license scan results table for Night 64', NOW())
ON CONFLICT (version) DO NOTHING; 