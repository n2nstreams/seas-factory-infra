-- Migration 009: Create secrets rotation tracking table
-- Night 67: SecretsManagerAgent for automated token rotation
-- Created: 2024-01-20

-- Create secrets_rotation_schedule table for tracking secret rotation
CREATE TABLE IF NOT EXISTS secrets_rotation_schedule (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Secret identification
    secret_name VARCHAR(255) NOT NULL,
    secret_provider VARCHAR(50) NOT NULL CHECK (secret_provider IN ('gcp', 'aws', 'azure')),
    secret_type VARCHAR(100) NOT NULL, -- 'api_key', 'token', 'certificate', etc.
    
    -- Rotation configuration
    rotation_interval_days INTEGER NOT NULL DEFAULT 30,
    next_rotation_date TIMESTAMP WITH TIME ZONE NOT NULL,
    auto_rotation_enabled BOOLEAN DEFAULT TRUE,
    
    -- Provider-specific configuration
    provider_config JSONB DEFAULT '{}', -- Store provider-specific settings
    
    -- Metadata
    description TEXT,
    criticality VARCHAR(20) DEFAULT 'medium' CHECK (criticality IN ('low', 'medium', 'high', 'critical')),
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Create secrets_rotation_history table for audit trail
CREATE TABLE IF NOT EXISTS secrets_rotation_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_id UUID NOT NULL REFERENCES secrets_rotation_schedule(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Rotation details
    rotation_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    rotation_status VARCHAR(50) NOT NULL CHECK (rotation_status IN ('success', 'failed', 'partial')),
    previous_version VARCHAR(100),
    new_version VARCHAR(100),
    
    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Metadata
    rotation_method VARCHAR(50) DEFAULT 'automatic', -- 'automatic', 'manual', 'emergency'
    duration_seconds INTEGER,
    
    -- Audit
    performed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    notes TEXT
);

-- Create secrets_access_tracking table for monitoring secret usage
CREATE TABLE IF NOT EXISTS secrets_access_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_id UUID NOT NULL REFERENCES secrets_rotation_schedule(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Access details
    access_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    service_name VARCHAR(255) NOT NULL,
    access_type VARCHAR(50) NOT NULL, -- 'read', 'write', 'rotate'
    
    -- Request metadata
    ip_address INET,
    user_agent TEXT,
    request_id VARCHAR(255),
    
    -- Response
    response_status VARCHAR(20), -- 'success', 'denied', 'error'
    error_code VARCHAR(50)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_secrets_rotation_schedule_tenant_id ON secrets_rotation_schedule(tenant_id);
CREATE INDEX IF NOT EXISTS idx_secrets_rotation_schedule_provider ON secrets_rotation_schedule(secret_provider);
CREATE INDEX IF NOT EXISTS idx_secrets_rotation_schedule_next_rotation ON secrets_rotation_schedule(next_rotation_date);
CREATE INDEX IF NOT EXISTS idx_secrets_rotation_schedule_auto_enabled ON secrets_rotation_schedule(auto_rotation_enabled);

CREATE INDEX IF NOT EXISTS idx_secrets_rotation_history_schedule_id ON secrets_rotation_history(schedule_id);
CREATE INDEX IF NOT EXISTS idx_secrets_rotation_history_tenant_id ON secrets_rotation_history(tenant_id);
CREATE INDEX IF NOT EXISTS idx_secrets_rotation_history_date ON secrets_rotation_history(rotation_date);
CREATE INDEX IF NOT EXISTS idx_secrets_rotation_history_status ON secrets_rotation_history(rotation_status);

CREATE INDEX IF NOT EXISTS idx_secrets_access_tracking_schedule_id ON secrets_access_tracking(schedule_id);
CREATE INDEX IF NOT EXISTS idx_secrets_access_tracking_timestamp ON secrets_access_tracking(access_timestamp);
CREATE INDEX IF NOT EXISTS idx_secrets_access_tracking_service ON secrets_access_tracking(service_name);

-- Enable Row Level Security for tenant isolation
ALTER TABLE secrets_rotation_schedule ENABLE ROW LEVEL SECURITY;
ALTER TABLE secrets_rotation_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE secrets_access_tracking ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for secrets_rotation_schedule
CREATE POLICY secrets_rotation_schedule_tenant_policy ON secrets_rotation_schedule
    FOR ALL
    TO application_role
    USING (tenant_id = COALESCE(current_setting('app.current_tenant_id', true), '')::uuid);

-- Create RLS policies for secrets_rotation_history
CREATE POLICY secrets_rotation_history_tenant_policy ON secrets_rotation_history
    FOR ALL
    TO application_role
    USING (tenant_id = COALESCE(current_setting('app.current_tenant_id', true), '')::uuid);

-- Create RLS policies for secrets_access_tracking
CREATE POLICY secrets_access_tracking_tenant_policy ON secrets_access_tracking
    FOR ALL
    TO application_role
    USING (tenant_id = COALESCE(current_setting('app.current_tenant_id', true), '')::uuid);

-- Create function to update next_rotation_date automatically
CREATE OR REPLACE FUNCTION update_next_rotation_date()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    
    -- If rotation_interval_days changed, recalculate next rotation
    IF OLD.rotation_interval_days IS DISTINCT FROM NEW.rotation_interval_days THEN
        NEW.next_rotation_date = CURRENT_TIMESTAMP + (NEW.rotation_interval_days || ' days')::interval;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic next_rotation_date updates
CREATE TRIGGER secrets_rotation_schedule_update_trigger
    BEFORE UPDATE ON secrets_rotation_schedule
    FOR EACH ROW
    EXECUTE FUNCTION update_next_rotation_date();

-- Create function to automatically create rotation history entry
CREATE OR REPLACE FUNCTION create_rotation_history_entry()
RETURNS TRIGGER AS $$
BEGIN
    -- When next_rotation_date is updated (indicating a rotation occurred)
    IF OLD.next_rotation_date IS DISTINCT FROM NEW.next_rotation_date 
       AND NEW.next_rotation_date > OLD.next_rotation_date THEN
        
        INSERT INTO secrets_rotation_history (
            schedule_id,
            tenant_id,
            rotation_status,
            rotation_method,
            performed_by
        ) VALUES (
            NEW.id,
            NEW.tenant_id,
            'success', -- Default to success, can be updated if needed
            'automatic',
            NEW.updated_by
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic history creation
CREATE TRIGGER secrets_rotation_history_trigger
    AFTER UPDATE ON secrets_rotation_schedule
    FOR EACH ROW
    EXECUTE FUNCTION create_rotation_history_entry();

-- Add comments for documentation
COMMENT ON TABLE secrets_rotation_schedule IS 'Tracks secret rotation schedules across multiple cloud providers';
COMMENT ON TABLE secrets_rotation_history IS 'Audit trail of all secret rotation activities';
COMMENT ON TABLE secrets_access_tracking IS 'Monitors access patterns to secrets for security analysis';

COMMENT ON COLUMN secrets_rotation_schedule.provider_config IS 'JSON configuration specific to each cloud provider (GCP project, AWS region, Azure vault, etc.)';
COMMENT ON COLUMN secrets_rotation_schedule.criticality IS 'Business criticality level affecting rotation urgency and alerting';
COMMENT ON COLUMN secrets_rotation_history.rotation_method IS 'How the rotation was triggered: automatic, manual, or emergency'; 