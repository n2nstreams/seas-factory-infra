-- Migration 011: Create ZAP penetration test results tables
-- Night 78: Final security scan & penetration test script (OWASP ZAP)

-- Extend security_scan_results table to support ZAP scan types
-- Add ZAP-specific columns to existing security infrastructure

-- Create ZAP penetration test results table
CREATE TABLE IF NOT EXISTS zap_penetration_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    scan_result_id UUID NOT NULL,
    project_id UUID,
    target_url VARCHAR(2048) NOT NULL,
    scan_type VARCHAR(50) NOT NULL DEFAULT 'baseline',
    
    -- ZAP-specific scan metadata
    spider_results JSONB DEFAULT '{}',
    passive_scan_results JSONB DEFAULT '{}',
    active_scan_results JSONB DEFAULT '{}',
    zap_session_id VARCHAR(255),
    zap_version VARCHAR(50) DEFAULT 'OWASP ZAP 2.14.0',
    
    -- Scan configuration
    spider_timeout INTEGER DEFAULT 300,
    scan_timeout INTEGER DEFAULT 600,
    max_depth INTEGER DEFAULT 5,
    excluded_urls JSONB DEFAULT '[]',
    authentication_config JSONB DEFAULT '{}',
    
    -- Security posture assessment
    security_posture VARCHAR(50) DEFAULT 'unknown',
    vulnerabilities_by_confidence JSONB DEFAULT '{}',
    
    -- Timing information
    spider_duration_ms INTEGER DEFAULT 0,
    passive_scan_duration_ms INTEGER DEFAULT 0,
    active_scan_duration_ms INTEGER DEFAULT 0,
    
    -- Status tracking
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_zap_results_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    CONSTRAINT fk_zap_results_scan FOREIGN KEY (scan_result_id) REFERENCES security_scan_results(id) ON DELETE CASCADE,
    CONSTRAINT fk_zap_results_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_zap_penetration_results_tenant_id ON zap_penetration_results(tenant_id);
CREATE INDEX IF NOT EXISTS idx_zap_penetration_results_scan_result_id ON zap_penetration_results(scan_result_id);
CREATE INDEX IF NOT EXISTS idx_zap_penetration_results_project_id ON zap_penetration_results(project_id);
CREATE INDEX IF NOT EXISTS idx_zap_penetration_results_target_url ON zap_penetration_results(target_url);
CREATE INDEX IF NOT EXISTS idx_zap_penetration_results_scan_type ON zap_penetration_results(scan_type);
CREATE INDEX IF NOT EXISTS idx_zap_penetration_results_status ON zap_penetration_results(status);
CREATE INDEX IF NOT EXISTS idx_zap_penetration_results_security_posture ON zap_penetration_results(security_posture);
CREATE INDEX IF NOT EXISTS idx_zap_penetration_results_created_at ON zap_penetration_results(created_at);

-- Create composite index for common queries
CREATE INDEX IF NOT EXISTS idx_zap_penetration_results_tenant_project_date 
ON zap_penetration_results(tenant_id, project_id, created_at DESC);

-- Create ZAP alerts table for detailed vulnerability tracking
CREATE TABLE IF NOT EXISTS zap_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    zap_result_id UUID NOT NULL,
    
    -- ZAP alert identification
    zap_plugin_id VARCHAR(20) NOT NULL,
    zap_alert_id VARCHAR(255) NOT NULL,
    
    -- Vulnerability details
    name VARCHAR(500) NOT NULL,
    description TEXT,
    solution TEXT,
    reference TEXT,
    other_info TEXT,
    
    -- Risk assessment
    risk VARCHAR(20) NOT NULL,
    confidence VARCHAR(20) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    
    -- Location information
    url VARCHAR(2048),
    param VARCHAR(255),
    attack TEXT,
    evidence TEXT,
    
    -- Security classification
    cwe_id VARCHAR(10),
    wasc_id VARCHAR(10),
    
    -- Remediation tracking
    remediation_status VARCHAR(50) DEFAULT 'open',
    remediation_notes TEXT,
    false_positive BOOLEAN DEFAULT FALSE,
    risk_accepted BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_zap_alerts_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    CONSTRAINT fk_zap_alerts_zap_result FOREIGN KEY (zap_result_id) REFERENCES zap_penetration_results(id) ON DELETE CASCADE
);

-- Create indexes for ZAP alerts
CREATE INDEX IF NOT EXISTS idx_zap_alerts_tenant_id ON zap_alerts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_zap_alerts_zap_result_id ON zap_alerts(zap_result_id);
CREATE INDEX IF NOT EXISTS idx_zap_alerts_plugin_id ON zap_alerts(zap_plugin_id);
CREATE INDEX IF NOT EXISTS idx_zap_alerts_alert_id ON zap_alerts(zap_alert_id);
CREATE INDEX IF NOT EXISTS idx_zap_alerts_risk ON zap_alerts(risk);
CREATE INDEX IF NOT EXISTS idx_zap_alerts_confidence ON zap_alerts(confidence);
CREATE INDEX IF NOT EXISTS idx_zap_alerts_severity ON zap_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_zap_alerts_url ON zap_alerts(url);
CREATE INDEX IF NOT EXISTS idx_zap_alerts_cwe_id ON zap_alerts(cwe_id);
CREATE INDEX IF NOT EXISTS idx_zap_alerts_remediation_status ON zap_alerts(remediation_status);
CREATE INDEX IF NOT EXISTS idx_zap_alerts_false_positive ON zap_alerts(false_positive);

-- Create ZAP scan history for trend analysis
CREATE TABLE IF NOT EXISTS zap_scan_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    project_id UUID,
    target_url VARCHAR(2048) NOT NULL,
    scan_date DATE NOT NULL,
    
    -- Daily aggregated metrics
    scan_count INTEGER NOT NULL DEFAULT 0,
    total_alerts INTEGER NOT NULL DEFAULT 0,
    critical_alerts INTEGER NOT NULL DEFAULT 0,
    high_alerts INTEGER NOT NULL DEFAULT 0,
    medium_alerts INTEGER NOT NULL DEFAULT 0,
    low_alerts INTEGER NOT NULL DEFAULT 0,
    informational_alerts INTEGER NOT NULL DEFAULT 0,
    
    -- Risk trending
    avg_risk_score DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    max_risk_score DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    min_risk_score DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    
    -- Security posture trending
    security_posture VARCHAR(50),
    improvement_trend VARCHAR(20), -- 'improving', 'degrading', 'stable'
    
    -- Performance metrics
    avg_scan_duration_ms INTEGER DEFAULT 0,
    total_scan_duration_ms INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_zap_history_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    CONSTRAINT fk_zap_history_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    
    -- Unique constraint for daily aggregation
    UNIQUE(tenant_id, project_id, target_url, scan_date)
);

-- Create indexes for ZAP scan history
CREATE INDEX IF NOT EXISTS idx_zap_scan_history_tenant_id ON zap_scan_history(tenant_id);
CREATE INDEX IF NOT EXISTS idx_zap_scan_history_project_id ON zap_scan_history(project_id);
CREATE INDEX IF NOT EXISTS idx_zap_scan_history_target_url ON zap_scan_history(target_url);
CREATE INDEX IF NOT EXISTS idx_zap_scan_history_scan_date ON zap_scan_history(scan_date DESC);
CREATE INDEX IF NOT EXISTS idx_zap_scan_history_avg_risk_score ON zap_scan_history(avg_risk_score);
CREATE INDEX IF NOT EXISTS idx_zap_scan_history_security_posture ON zap_scan_history(security_posture);

-- Create composite index for trend analysis
CREATE INDEX IF NOT EXISTS idx_zap_scan_history_tenant_target_date 
ON zap_scan_history(tenant_id, target_url, scan_date DESC);

-- Create ZAP scan configurations table for reusable scan profiles
CREATE TABLE IF NOT EXISTS zap_scan_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    
    -- Configuration identification
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Scan settings
    scan_type VARCHAR(50) NOT NULL DEFAULT 'baseline',
    spider_timeout INTEGER DEFAULT 300,
    scan_timeout INTEGER DEFAULT 600,
    max_depth INTEGER DEFAULT 5,
    
    -- Target configuration
    excluded_urls JSONB DEFAULT '[]',
    included_contexts JSONB DEFAULT '[]',
    authentication_config JSONB DEFAULT '{}',
    custom_rules JSONB DEFAULT '[]',
    
    -- Usage tracking
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    
    -- Configuration metadata
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_zap_config_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Unique constraint for tenant configuration names
    UNIQUE(tenant_id, name)
);

-- Create indexes for ZAP scan configurations
CREATE INDEX IF NOT EXISTS idx_zap_scan_configurations_tenant_id ON zap_scan_configurations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_zap_scan_configurations_name ON zap_scan_configurations(name);
CREATE INDEX IF NOT EXISTS idx_zap_scan_configurations_scan_type ON zap_scan_configurations(scan_type);
CREATE INDEX IF NOT EXISTS idx_zap_scan_configurations_is_default ON zap_scan_configurations(is_default);
CREATE INDEX IF NOT EXISTS idx_zap_scan_configurations_is_active ON zap_scan_configurations(is_active);
CREATE INDEX IF NOT EXISTS idx_zap_scan_configurations_usage_count ON zap_scan_configurations(usage_count DESC);

-- Add row-level security for tenant isolation
ALTER TABLE zap_penetration_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE zap_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE zap_scan_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE zap_scan_configurations ENABLE ROW LEVEL SECURITY;

-- Create policies for tenant isolation
CREATE POLICY zap_penetration_results_tenant_isolation ON zap_penetration_results
    USING (tenant_id = current_setting('app.tenant_id', true));

CREATE POLICY zap_alerts_tenant_isolation ON zap_alerts
    USING (tenant_id = current_setting('app.tenant_id', true));

CREATE POLICY zap_scan_history_tenant_isolation ON zap_scan_history
    USING (tenant_id = current_setting('app.tenant_id', true));

CREATE POLICY zap_scan_configurations_tenant_isolation ON zap_scan_configurations
    USING (tenant_id = current_setting('app.tenant_id', true));

-- Grant permissions to the application role
GRANT SELECT, INSERT, UPDATE, DELETE ON zap_penetration_results TO factoryadmin;
GRANT SELECT, INSERT, UPDATE, DELETE ON zap_alerts TO factoryadmin;
GRANT SELECT, INSERT, UPDATE, DELETE ON zap_scan_history TO factoryadmin;
GRANT SELECT, INSERT, UPDATE, DELETE ON zap_scan_configurations TO factoryadmin;

-- Create trigger for updating timestamps
CREATE OR REPLACE FUNCTION update_zap_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_zap_penetration_results_updated_at 
    BEFORE UPDATE ON zap_penetration_results 
    FOR EACH ROW EXECUTE FUNCTION update_zap_updated_at_column();

CREATE TRIGGER update_zap_alerts_updated_at 
    BEFORE UPDATE ON zap_alerts 
    FOR EACH ROW EXECUTE FUNCTION update_zap_updated_at_column();

CREATE TRIGGER update_zap_scan_history_updated_at 
    BEFORE UPDATE ON zap_scan_history 
    FOR EACH ROW EXECUTE FUNCTION update_zap_updated_at_column();

CREATE TRIGGER update_zap_scan_configurations_updated_at 
    BEFORE UPDATE ON zap_scan_configurations 
    FOR EACH ROW EXECUTE FUNCTION update_zap_updated_at_column();

-- Insert default ZAP scan configurations
INSERT INTO zap_scan_configurations (
    tenant_id, 
    name, 
    description, 
    scan_type, 
    spider_timeout, 
    scan_timeout, 
    max_depth, 
    is_default
) VALUES 
(
    '00000000-0000-0000-0000-000000000000', -- System default tenant
    'Quick Scan',
    'Fast scan for basic vulnerability detection',
    'quick',
    180,  -- 3 minutes
    300,  -- 5 minutes
    3,
    false
),
(
    '00000000-0000-0000-0000-000000000000',
    'Baseline Scan',
    'Standard security scan with moderate coverage',
    'baseline',
    600,  -- 10 minutes
    1200, -- 20 minutes
    5,
    true  -- Default configuration
),
(
    '00000000-0000-0000-0000-000000000000',
    'Comprehensive Scan',
    'Thorough security scan with full coverage',
    'full',
    1800, -- 30 minutes
    3600, -- 60 minutes
    10,
    false
)
ON CONFLICT (tenant_id, name) DO NOTHING;

-- Create a view for ZAP penetration test summary
CREATE OR REPLACE VIEW zap_penetration_summary AS
SELECT 
    zpr.id,
    zpr.tenant_id,
    zpr.project_id,
    zpr.target_url,
    zpr.scan_type,
    zpr.security_posture,
    zpr.status,
    zpr.created_at,
    
    -- Aggregate alert counts
    COUNT(za.id) as total_alerts,
    COUNT(CASE WHEN za.risk = 'Critical' THEN 1 END) as critical_alerts,
    COUNT(CASE WHEN za.risk = 'High' THEN 1 END) as high_alerts,
    COUNT(CASE WHEN za.risk = 'Medium' THEN 1 END) as medium_alerts,
    COUNT(CASE WHEN za.risk = 'Low' THEN 1 END) as low_alerts,
    COUNT(CASE WHEN za.risk = 'Informational' THEN 1 END) as informational_alerts,
    
    -- Security scan result data
    ssr.risk_score,
    ssr.total_vulnerabilities,
    ssr.vulnerabilities_by_severity,
    ssr.recommendations
    
FROM zap_penetration_results zpr
LEFT JOIN zap_alerts za ON zpr.id = za.zap_result_id
LEFT JOIN security_scan_results ssr ON zpr.scan_result_id = ssr.id
GROUP BY 
    zpr.id, zpr.tenant_id, zpr.project_id, zpr.target_url, 
    zpr.scan_type, zpr.security_posture, zpr.status, zpr.created_at,
    ssr.risk_score, ssr.total_vulnerabilities, ssr.vulnerabilities_by_severity, ssr.recommendations;

-- Grant permissions on the view
GRANT SELECT ON zap_penetration_summary TO factoryadmin;

-- Create a function to calculate security trend
CREATE OR REPLACE FUNCTION calculate_zap_security_trend(
    p_tenant_id UUID,
    p_target_url VARCHAR,
    p_days INTEGER DEFAULT 30
) RETURNS TABLE (
    scan_date DATE,
    risk_score DECIMAL,
    security_posture VARCHAR,
    total_alerts INTEGER,
    trend_direction VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    WITH daily_scores AS (
        SELECT 
            zsh.scan_date,
            zsh.avg_risk_score,
            zsh.security_posture,
            zsh.total_alerts,
            LAG(zsh.avg_risk_score) OVER (ORDER BY zsh.scan_date) as prev_risk_score
        FROM zap_scan_history zsh
        WHERE zsh.tenant_id = p_tenant_id
        AND zsh.target_url = p_target_url
        AND zsh.scan_date >= CURRENT_DATE - INTERVAL '%s days' % p_days
        ORDER BY zsh.scan_date
    )
    SELECT 
        ds.scan_date,
        ds.avg_risk_score,
        ds.security_posture,
        ds.total_alerts,
        CASE 
            WHEN ds.prev_risk_score IS NULL THEN 'baseline'
            WHEN ds.avg_risk_score < ds.prev_risk_score THEN 'improving'
            WHEN ds.avg_risk_score > ds.prev_risk_score THEN 'degrading'
            ELSE 'stable'
        END as trend_direction
    FROM daily_scores ds;
END;
$$ LANGUAGE plpgsql;

-- Grant execute permission on the function
GRANT EXECUTE ON FUNCTION calculate_zap_security_trend TO factoryadmin; 