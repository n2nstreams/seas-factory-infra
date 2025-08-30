-- Migration 004: Create factory pipelines table
-- Night 56: Factory pipeline tracking and monitoring
-- Created: 2024-01-15

-- Create factory_pipelines table for tracking factory orchestration progress
CREATE TABLE IF NOT EXISTS factory_pipelines (
    pipeline_id VARCHAR(255) PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    project_id VARCHAR(255) NOT NULL, -- Maps to idea_id initially, then project_id
    project_name VARCHAR(255) NOT NULL,
    
    -- Pipeline status tracking
    current_stage VARCHAR(100) NOT NULL DEFAULT 'idea_validation',
    progress DECIMAL(5,2) NOT NULL DEFAULT 0.00 CHECK (progress >= 0.00 AND progress <= 100.00),
    status VARCHAR(50) NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'completed', 'failed', 'paused')),
    
    -- Stage details
    stages JSONB DEFAULT '{}', -- JSON object tracking individual stage status
    
    -- Timing information
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Audit fields
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_factory_pipelines_tenant_id ON factory_pipelines(tenant_id);
CREATE INDEX IF NOT EXISTS idx_factory_pipelines_status ON factory_pipelines(status);
CREATE INDEX IF NOT EXISTS idx_factory_pipelines_current_stage ON factory_pipelines(current_stage);
CREATE INDEX IF NOT EXISTS idx_factory_pipelines_project_id ON factory_pipelines(project_id);
CREATE INDEX IF NOT EXISTS idx_factory_pipelines_started_at ON factory_pipelines(started_at);
CREATE INDEX IF NOT EXISTS idx_factory_pipelines_completed_at ON factory_pipelines(completed_at);

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_factory_pipelines_tenant_status ON factory_pipelines(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_factory_pipelines_tenant_stage ON factory_pipelines(tenant_id, current_stage);

-- Create function for updating updated_at timestamp
CREATE OR REPLACE FUNCTION update_factory_pipelines_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updating updated_at
CREATE TRIGGER update_factory_pipelines_updated_at
    BEFORE UPDATE ON factory_pipelines
    FOR EACH ROW
    EXECUTE FUNCTION update_factory_pipelines_updated_at();

-- Add sample data for testing
INSERT INTO factory_pipelines (
    pipeline_id, tenant_id, project_id, project_name, current_stage, progress, status, stages, metadata
) 
SELECT 
    'demo-pipeline-' || t.id,
    t.id,
    'demo-project-001',
    'Demo TaskFlow Pro',
    'idea_validation',
    25.0,
    'running',
    '{"idea_validation": "running", "tech_stack": "pending", "design": "pending", "development": "pending", "qa": "pending", "deployment": "pending"}',
    '{"demo": true, "priority": "normal", "test_mode": true}'
FROM tenants t
WHERE t.slug = 'default'
ON CONFLICT (pipeline_id) DO NOTHING;

-- Create view for pipeline statistics
CREATE OR REPLACE VIEW factory_pipeline_stats AS
SELECT 
    tenant_id,
    COUNT(*) as total_pipelines,
    COUNT(*) FILTER (WHERE status = 'queued') as queued_pipelines,
    COUNT(*) FILTER (WHERE status = 'running') as running_pipelines,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_pipelines,
    COUNT(*) FILTER (WHERE status = 'failed') as failed_pipelines,
    COUNT(*) FILTER (WHERE status = 'paused') as paused_pipelines,
    
    -- Timing statistics
    AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) FILTER (WHERE status = 'completed') as avg_completion_time_seconds,
    MIN(started_at) as first_pipeline_started,
    MAX(COALESCE(completed_at, updated_at)) as last_activity,
    
    -- Success rate
    ROUND(
        (COUNT(*) FILTER (WHERE status = 'completed')::DECIMAL / NULLIF(COUNT(*) FILTER (WHERE status IN ('completed', 'failed')), 0)) * 100, 
        2
    ) as success_rate_percent,
    
    -- Current load (percentage of running pipelines vs max capacity)
    ROUND(
        (COUNT(*) FILTER (WHERE status = 'running')::DECIMAL / 10) * 100, 
        2
    ) as current_load_percent -- Assuming max 10 concurrent pipelines
    
FROM factory_pipelines
GROUP BY tenant_id;

-- Grant permissions
GRANT SELECT, INSERT, UPDATE ON factory_pipelines TO factoryadmin;
GRANT SELECT ON factory_pipeline_stats TO factoryadmin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO factoryadmin;

COMMENT ON TABLE factory_pipelines IS 'Tracks factory orchestration pipeline progress and status';
COMMENT ON COLUMN factory_pipelines.pipeline_id IS 'Unique identifier for the factory pipeline';
COMMENT ON COLUMN factory_pipelines.current_stage IS 'Current stage in the factory pipeline (idea_validation, tech_stack, design, development, qa, deployment)';
COMMENT ON COLUMN factory_pipelines.progress IS 'Overall pipeline progress as percentage (0.00 to 100.00)';
COMMENT ON COLUMN factory_pipelines.stages IS 'JSON object tracking individual stage status and details';
COMMENT ON COLUMN factory_pipelines.metadata IS 'Additional pipeline metadata and configuration';
COMMENT ON VIEW factory_pipeline_stats IS 'Aggregated statistics for factory pipeline performance by tenant'; 