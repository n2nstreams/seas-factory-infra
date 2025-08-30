-- Migration: Create security scan results table
-- Night 41: Security scan step: Snyk CLI in pipeline; SecurityAgent parses report.
-- Created: 2024-01-01

-- Create security_scan_results table
CREATE TABLE IF NOT EXISTS security_scan_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    project_id UUID,
    scan_type VARCHAR(50) NOT NULL DEFAULT 'dependencies',
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    risk_score DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    total_vulnerabilities INTEGER NOT NULL DEFAULT 0,
    vulnerabilities_by_severity JSONB DEFAULT '{}',
    recommendations JSONB DEFAULT '[]',
    remediation_steps JSONB DEFAULT '[]',
    snyk_report JSONB DEFAULT '{}',
    scan_duration_ms INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_security_scan_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    CONSTRAINT fk_security_scan_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_security_scan_results_tenant_id ON security_scan_results(tenant_id);
CREATE INDEX IF NOT EXISTS idx_security_scan_results_project_id ON security_scan_results(project_id);
CREATE INDEX IF NOT EXISTS idx_security_scan_results_scan_type ON security_scan_results(scan_type);
CREATE INDEX IF NOT EXISTS idx_security_scan_results_status ON security_scan_results(status);
CREATE INDEX IF NOT EXISTS idx_security_scan_results_risk_score ON security_scan_results(risk_score);
CREATE INDEX IF NOT EXISTS idx_security_scan_results_created_at ON security_scan_results(created_at);

-- Create composite index for common queries
CREATE INDEX IF NOT EXISTS idx_security_scan_results_tenant_project_date ON security_scan_results(tenant_id, project_id, created_at DESC);

-- Create security_vulnerabilities table for detailed vulnerability tracking
CREATE TABLE IF NOT EXISTS security_vulnerabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    scan_result_id UUID NOT NULL,
    snyk_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    severity VARCHAR(20) NOT NULL,
    language VARCHAR(50),
    package_name VARCHAR(255) NOT NULL,
    package_version VARCHAR(100),
    vulnerable_versions JSONB DEFAULT '[]',
    patched_versions JSONB DEFAULT '[]',
    cve VARCHAR(50),
    cvss_score DECIMAL(3,1),
    exploit_maturity VARCHAR(50),
    is_patchable BOOLEAN DEFAULT FALSE,
    is_upgradable BOOLEAN DEFAULT FALSE,
    upgrade_path JSONB DEFAULT '[]',
    patch_set VARCHAR(255),
    disclosure_time TIMESTAMP WITH TIME ZONE,
    publication_time TIMESTAMP WITH TIME ZONE,
    credit JSONB DEFAULT '[]',
    semver VARCHAR(255),
    functions JSONB DEFAULT '[]',
    from_path JSONB DEFAULT '[]',
    identifiers JSONB DEFAULT '{}',
    references JSONB DEFAULT '[]',
    status VARCHAR(50) DEFAULT 'open',
    remediation_status VARCHAR(50) DEFAULT 'pending',
    remediation_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_security_vuln_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    CONSTRAINT fk_security_vuln_scan_result FOREIGN KEY (scan_result_id) REFERENCES security_scan_results(id) ON DELETE CASCADE
);

-- Create indexes for security_vulnerabilities
CREATE INDEX IF NOT EXISTS idx_security_vulnerabilities_tenant_id ON security_vulnerabilities(tenant_id);
CREATE INDEX IF NOT EXISTS idx_security_vulnerabilities_scan_result_id ON security_vulnerabilities(scan_result_id);
CREATE INDEX IF NOT EXISTS idx_security_vulnerabilities_snyk_id ON security_vulnerabilities(snyk_id);
CREATE INDEX IF NOT EXISTS idx_security_vulnerabilities_severity ON security_vulnerabilities(severity);
CREATE INDEX IF NOT EXISTS idx_security_vulnerabilities_package_name ON security_vulnerabilities(package_name);
CREATE INDEX IF NOT EXISTS idx_security_vulnerabilities_status ON security_vulnerabilities(status);
CREATE INDEX IF NOT EXISTS idx_security_vulnerabilities_cve ON security_vulnerabilities(cve);
CREATE INDEX IF NOT EXISTS idx_security_vulnerabilities_is_patchable ON security_vulnerabilities(is_patchable);
CREATE INDEX IF NOT EXISTS idx_security_vulnerabilities_is_upgradable ON security_vulnerabilities(is_upgradable);

-- Create security_recommendations table
CREATE TABLE IF NOT EXISTS security_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    scan_result_id UUID NOT NULL,
    vulnerability_id UUID NOT NULL,
    recommendation_type VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    impact TEXT,
    effort VARCHAR(20) NOT NULL,
    priority INTEGER NOT NULL DEFAULT 1,
    automated BOOLEAN DEFAULT FALSE,
    remediation_command TEXT,
    additional_info TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    applied_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_security_rec_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    CONSTRAINT fk_security_rec_scan_result FOREIGN KEY (scan_result_id) REFERENCES security_scan_results(id) ON DELETE CASCADE,
    CONSTRAINT fk_security_rec_vulnerability FOREIGN KEY (vulnerability_id) REFERENCES security_vulnerabilities(id) ON DELETE CASCADE
);

-- Create indexes for security_recommendations
CREATE INDEX IF NOT EXISTS idx_security_recommendations_tenant_id ON security_recommendations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_security_recommendations_scan_result_id ON security_recommendations(scan_result_id);
CREATE INDEX IF NOT EXISTS idx_security_recommendations_vulnerability_id ON security_recommendations(vulnerability_id);
CREATE INDEX IF NOT EXISTS idx_security_recommendations_type ON security_recommendations(recommendation_type);
CREATE INDEX IF NOT EXISTS idx_security_recommendations_priority ON security_recommendations(priority);
CREATE INDEX IF NOT EXISTS idx_security_recommendations_automated ON security_recommendations(automated);
CREATE INDEX IF NOT EXISTS idx_security_recommendations_status ON security_recommendations(status);

-- Create security_scan_history table for tracking scan trends
CREATE TABLE IF NOT EXISTS security_scan_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    project_id UUID,
    scan_date DATE NOT NULL,
    scan_count INTEGER NOT NULL DEFAULT 0,
    total_vulnerabilities INTEGER NOT NULL DEFAULT 0,
    critical_vulnerabilities INTEGER NOT NULL DEFAULT 0,
    high_vulnerabilities INTEGER NOT NULL DEFAULT 0,
    medium_vulnerabilities INTEGER NOT NULL DEFAULT 0,
    low_vulnerabilities INTEGER NOT NULL DEFAULT 0,
    avg_risk_score DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    fixed_vulnerabilities INTEGER NOT NULL DEFAULT 0,
    new_vulnerabilities INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_security_history_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    CONSTRAINT fk_security_history_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(tenant_id, project_id, scan_date)
);

-- Create indexes for security_scan_history
CREATE INDEX IF NOT EXISTS idx_security_scan_history_tenant_id ON security_scan_history(tenant_id);
CREATE INDEX IF NOT EXISTS idx_security_scan_history_project_id ON security_scan_history(project_id);
CREATE INDEX IF NOT EXISTS idx_security_scan_history_scan_date ON security_scan_history(scan_date);
CREATE INDEX IF NOT EXISTS idx_security_scan_history_tenant_project_date ON security_scan_history(tenant_id, project_id, scan_date DESC);

-- Enable Row Level Security (RLS) for all security tables
ALTER TABLE security_scan_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_vulnerabilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_scan_history ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for security_scan_results
CREATE POLICY security_scan_results_tenant_policy ON security_scan_results
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Create RLS policies for security_vulnerabilities
CREATE POLICY security_vulnerabilities_tenant_policy ON security_vulnerabilities
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Create RLS policies for security_recommendations
CREATE POLICY security_recommendations_tenant_policy ON security_recommendations
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Create RLS policies for security_scan_history
CREATE POLICY security_scan_history_tenant_policy ON security_scan_history
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Create function to update security_scan_history
CREATE OR REPLACE FUNCTION update_security_scan_history()
RETURNS TRIGGER AS $$
BEGIN
    -- Update or insert daily scan statistics
    INSERT INTO security_scan_history (
        tenant_id, project_id, scan_date, scan_count, total_vulnerabilities,
        critical_vulnerabilities, high_vulnerabilities, medium_vulnerabilities, low_vulnerabilities,
        avg_risk_score
    )
    VALUES (
        NEW.tenant_id, NEW.project_id, CURRENT_DATE, 1, NEW.total_vulnerabilities,
        COALESCE((NEW.vulnerabilities_by_severity->>'critical')::INTEGER, 0),
        COALESCE((NEW.vulnerabilities_by_severity->>'high')::INTEGER, 0),
        COALESCE((NEW.vulnerabilities_by_severity->>'medium')::INTEGER, 0),
        COALESCE((NEW.vulnerabilities_by_severity->>'low')::INTEGER, 0),
        NEW.risk_score
    )
    ON CONFLICT (tenant_id, project_id, scan_date) DO UPDATE SET
        scan_count = security_scan_history.scan_count + 1,
        total_vulnerabilities = (security_scan_history.total_vulnerabilities + NEW.total_vulnerabilities) / 2,
        critical_vulnerabilities = (security_scan_history.critical_vulnerabilities + COALESCE((NEW.vulnerabilities_by_severity->>'critical')::INTEGER, 0)) / 2,
        high_vulnerabilities = (security_scan_history.high_vulnerabilities + COALESCE((NEW.vulnerabilities_by_severity->>'high')::INTEGER, 0)) / 2,
        medium_vulnerabilities = (security_scan_history.medium_vulnerabilities + COALESCE((NEW.vulnerabilities_by_severity->>'medium')::INTEGER, 0)) / 2,
        low_vulnerabilities = (security_scan_history.low_vulnerabilities + COALESCE((NEW.vulnerabilities_by_severity->>'low')::INTEGER, 0)) / 2,
        avg_risk_score = (security_scan_history.avg_risk_score + NEW.risk_score) / 2,
        updated_at = CURRENT_TIMESTAMP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update security_scan_history
CREATE TRIGGER trigger_update_security_scan_history
    AFTER INSERT ON security_scan_results
    FOR EACH ROW
    EXECUTE FUNCTION update_security_scan_history();

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER trigger_security_scan_results_updated_at
    BEFORE UPDATE ON security_scan_results
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_security_vulnerabilities_updated_at
    BEFORE UPDATE ON security_vulnerabilities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_security_recommendations_updated_at
    BEFORE UPDATE ON security_recommendations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_security_scan_history_updated_at
    BEFORE UPDATE ON security_scan_history
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create views for common queries
CREATE OR REPLACE VIEW security_dashboard_summary AS
SELECT 
    sr.tenant_id,
    sr.project_id,
    p.name as project_name,
    COUNT(sr.id) as total_scans,
    AVG(sr.risk_score) as avg_risk_score,
    SUM(sr.total_vulnerabilities) as total_vulnerabilities,
    SUM(COALESCE((sr.vulnerabilities_by_severity->>'critical')::INTEGER, 0)) as critical_vulnerabilities,
    SUM(COALESCE((sr.vulnerabilities_by_severity->>'high')::INTEGER, 0)) as high_vulnerabilities,
    SUM(COALESCE((sr.vulnerabilities_by_severity->>'medium')::INTEGER, 0)) as medium_vulnerabilities,
    SUM(COALESCE((sr.vulnerabilities_by_severity->>'low')::INTEGER, 0)) as low_vulnerabilities,
    MAX(sr.created_at) as last_scan_date,
    COUNT(CASE WHEN sr.status = 'completed' THEN 1 END) as completed_scans,
    COUNT(CASE WHEN sr.status = 'failed' THEN 1 END) as failed_scans
FROM security_scan_results sr
LEFT JOIN projects p ON sr.project_id = p.id
GROUP BY sr.tenant_id, sr.project_id, p.name;

-- Create view for vulnerability trends
CREATE OR REPLACE VIEW security_vulnerability_trends AS
SELECT 
    h.tenant_id,
    h.project_id,
    p.name as project_name,
    h.scan_date,
    h.total_vulnerabilities,
    h.critical_vulnerabilities,
    h.high_vulnerabilities,
    h.medium_vulnerabilities,
    h.low_vulnerabilities,
    h.avg_risk_score,
    h.fixed_vulnerabilities,
    h.new_vulnerabilities,
    LAG(h.total_vulnerabilities) OVER (PARTITION BY h.tenant_id, h.project_id ORDER BY h.scan_date) as prev_total_vulnerabilities,
    LAG(h.avg_risk_score) OVER (PARTITION BY h.tenant_id, h.project_id ORDER BY h.scan_date) as prev_avg_risk_score
FROM security_scan_history h
LEFT JOIN projects p ON h.project_id = p.id
ORDER BY h.tenant_id, h.project_id, h.scan_date DESC;

-- Grant permissions to application role
GRANT SELECT, INSERT, UPDATE, DELETE ON security_scan_results TO application_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON security_vulnerabilities TO application_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON security_recommendations TO application_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON security_scan_history TO application_role;
GRANT SELECT ON security_dashboard_summary TO application_role;
GRANT SELECT ON security_vulnerability_trends TO application_role;

-- Insert initial data or configuration if needed
-- (This section can be expanded based on requirements)

-- Log migration completion
INSERT INTO migration_log (migration_name, executed_at) 
VALUES ('002_create_security_scan_results', CURRENT_TIMESTAMP)
ON CONFLICT (migration_name) DO UPDATE SET executed_at = CURRENT_TIMESTAMP;

COMMIT; 