-- Supabase Database Migration for Module 5: Jobs & Scheduling
-- This script creates the job system tables with Row Level Security (RLS) policies
-- Run this in your Supabase SQL editor to set up the job system foundation

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create job_catalog table for job definitions and metadata
CREATE TABLE IF NOT EXISTS job_catalog (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Job identification
    job_name VARCHAR(255) NOT NULL,
    job_family VARCHAR(50) NOT NULL CHECK (job_family IN ('A', 'B', 'C')), -- A: short, B: cron, C: long-running
    job_key VARCHAR(255) NOT NULL, -- Unique identifier for the job type
    
    -- Job configuration
    max_runtime_seconds INTEGER NOT NULL DEFAULT 300, -- 5 minutes default
    max_retries INTEGER NOT NULL DEFAULT 3,
    retry_delay_seconds INTEGER NOT NULL DEFAULT 60,
    timeout_seconds INTEGER NOT NULL DEFAULT 600, -- 10 minutes default
    
    -- Job metadata
    description TEXT,
    owner VARCHAR(100) NOT NULL, -- Service/agent that owns this job
    tags JSONB DEFAULT '[]',
    
    -- SLA configuration
    sla_p95_seconds INTEGER NOT NULL DEFAULT 10, -- Target p95 runtime
    sla_escalation_path JSONB DEFAULT '{}', -- Escalation rules
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    
    -- Constraints
    UNIQUE(tenant_id, job_key)
);

-- Create job_queue table for actual job instances
CREATE TABLE IF NOT EXISTS job_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    catalog_id UUID NOT NULL REFERENCES job_catalog(id) ON DELETE CASCADE,
    
    -- Job execution
    job_name VARCHAR(255) NOT NULL,
    job_family VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'in_progress', 'succeeded', 'failed', 'canceled', 'retrying')),
    
    -- Job data
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    error_data JSONB DEFAULT '{}',
    
    -- Execution tracking
    priority INTEGER NOT NULL DEFAULT 0, -- Higher number = higher priority
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    
    -- Timing information
    queued_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    
    -- Performance metrics
    execution_time_ms INTEGER,
    queue_time_ms INTEGER,
    
    -- Idempotency and deduplication
    idempotency_key VARCHAR(255),
    deduplication_window_seconds INTEGER DEFAULT 300, -- 5 minutes
    
    -- Worker assignment
    worker_id VARCHAR(255), -- Edge Function instance ID
    worker_heartbeat TIMESTAMP WITH TIME ZONE,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    -- Constraints
    UNIQUE(tenant_id, idempotency_key) WHERE idempotency_key IS NOT NULL
);

-- Create job_schedules table for cron and recurring jobs
CREATE TABLE IF NOT EXISTS job_schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    catalog_id UUID NOT NULL REFERENCES job_catalog(id) ON DELETE CASCADE,
    
    -- Schedule configuration
    schedule_name VARCHAR(255) NOT NULL,
    cron_expression VARCHAR(100) NOT NULL, -- Standard cron format
    timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
    
    -- Schedule metadata
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Execution tracking
    last_execution_at TIMESTAMP WITH TIME ZONE,
    next_execution_at TIMESTAMP WITH TIME ZONE,
    execution_count INTEGER NOT NULL DEFAULT 0,
    
    -- Schedule limits
    max_concurrent_executions INTEGER NOT NULL DEFAULT 1,
    max_executions_per_day INTEGER,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    -- Constraints
    UNIQUE(tenant_id, schedule_name)
);

-- Create job_metrics table for performance monitoring
CREATE TABLE IF NOT EXISTS job_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    catalog_id UUID REFERENCES job_catalog(id) ON DELETE SET NULL,
    job_id UUID REFERENCES job_queue(id) ON DELETE SET NULL,
    
    -- Metric data
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    metric_unit VARCHAR(50),
    
    -- Metric context
    metric_type VARCHAR(50) NOT NULL CHECK (metric_type IN ('counter', 'gauge', 'histogram', 'summary')),
    labels JSONB DEFAULT '{}',
    
    -- Timing
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create job_dead_letter table for failed jobs that exceed retry limits
CREATE TABLE IF NOT EXISTS job_dead_letter (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    original_job_id UUID NOT NULL REFERENCES job_queue(id) ON DELETE CASCADE,
    
    -- Failure details
    failure_reason TEXT NOT NULL,
    failure_count INTEGER NOT NULL DEFAULT 1,
    last_failure_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Job data snapshot
    job_data_snapshot JSONB NOT NULL,
    
    -- Remediation
    remediation_status VARCHAR(50) DEFAULT 'pending' CHECK (remediation_status IN ('pending', 'investigating', 'resolved', 'archived')),
    remediation_notes TEXT,
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    
    -- Retention policy
    retention_expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days'),
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_job_catalog_tenant_id ON job_catalog(tenant_id);
CREATE INDEX IF NOT EXISTS idx_job_catalog_job_family ON job_catalog(job_family);
CREATE INDEX IF NOT EXISTS idx_job_catalog_job_key ON job_catalog(job_key);

CREATE INDEX IF NOT EXISTS idx_job_queue_tenant_id ON job_queue(tenant_id);
CREATE INDEX IF NOT EXISTS idx_job_queue_status ON job_queue(status);
CREATE INDEX IF NOT EXISTS idx_job_queue_job_family ON job_queue(job_family);
CREATE INDEX IF NOT EXISTS idx_job_queue_priority ON job_queue(priority DESC);
CREATE INDEX IF NOT EXISTS idx_job_queue_queued_at ON job_queue(queued_at);
CREATE INDEX IF NOT EXISTS idx_job_queue_next_retry_at ON job_queue(next_retry_at);
CREATE INDEX IF NOT EXISTS idx_job_queue_worker_id ON job_queue(worker_id);
CREATE INDEX IF NOT EXISTS idx_job_queue_idempotency_key ON job_queue(tenant_id, idempotency_key);

CREATE INDEX IF NOT EXISTS idx_job_schedules_tenant_id ON job_schedules(tenant_id);
CREATE INDEX IF NOT EXISTS idx_job_schedules_next_execution ON job_schedules(next_execution_at);
CREATE INDEX IF NOT EXISTS idx_job_schedules_active ON job_schedules(is_active);

CREATE INDEX IF NOT EXISTS idx_job_metrics_tenant_id ON job_metrics(tenant_id);
CREATE INDEX IF NOT EXISTS idx_job_metrics_catalog_id ON job_metrics(catalog_id);
CREATE INDEX IF NOT EXISTS idx_job_metrics_recorded_at ON job_metrics(recorded_at);

CREATE INDEX IF NOT EXISTS idx_job_dead_letter_tenant_id ON job_dead_letter(tenant_id);
CREATE INDEX IF NOT EXISTS idx_job_dead_letter_remediation_status ON job_dead_letter(remediation_status);
CREATE INDEX IF NOT EXISTS idx_job_dead_letter_retention_expires ON job_dead_letter(retention_expires_at);

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_job_queue_tenant_status_priority ON job_queue(tenant_id, status, priority DESC);
CREATE INDEX IF NOT EXISTS idx_job_queue_tenant_family_status ON job_queue(tenant_id, job_family, status);
CREATE INDEX IF NOT EXISTS idx_job_queue_worker_heartbeat ON job_queue(worker_id, worker_heartbeat);

-- Enable Row Level Security (RLS)
ALTER TABLE job_catalog ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_dead_letter ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for tenant isolation
-- Job Catalog policies
CREATE POLICY "tenant_isolation_job_catalog" ON job_catalog
    FOR ALL USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Job Queue policies
CREATE POLICY "tenant_isolation_job_queue" ON job_queue
    FOR ALL USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Job Schedules policies
CREATE POLICY "tenant_isolation_job_schedules" ON job_schedules
    FOR ALL USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Job Metrics policies
CREATE POLICY "tenant_isolation_job_metrics" ON job_metrics
    FOR ALL USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Job Dead Letter policies
CREATE POLICY "tenant_isolation_job_dead_letter" ON job_dead_letter
    FOR ALL USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Create functions for job management
CREATE OR REPLACE FUNCTION enqueue_job(
    p_tenant_id UUID,
    p_job_name VARCHAR(255),
    p_job_family VARCHAR(50),
    p_input_data JSONB DEFAULT '{}',
    p_priority INTEGER DEFAULT 0,
    p_idempotency_key VARCHAR(255) DEFAULT NULL,
    p_max_retries INTEGER DEFAULT 3,
    p_timeout_seconds INTEGER DEFAULT 600
) RETURNS UUID AS $$
DECLARE
    v_catalog_id UUID;
    v_job_id UUID;
    v_dedup_window INTEGER;
BEGIN
    -- Get catalog entry
    SELECT id INTO v_catalog_id
    FROM job_catalog
    WHERE tenant_id = p_tenant_id AND job_name = p_job_name;
    
    IF v_catalog_id IS NULL THEN
        RAISE EXCEPTION 'Job % not found in catalog for tenant %', p_job_name, p_tenant_id;
    END IF;
    
    -- Check for duplicate if idempotency key provided
    IF p_idempotency_key IS NOT NULL THEN
        SELECT id INTO v_job_id
        FROM job_queue
        WHERE tenant_id = p_tenant_id 
          AND idempotency_key = p_idempotency_key
          AND status IN ('queued', 'in_progress', 'retrying');
        
        IF v_job_id IS NOT NULL THEN
            RETURN v_job_id; -- Return existing job
        END IF;
    END IF;
    
    -- Get deduplication window from catalog
    SELECT deduplication_window_seconds INTO v_dedup_window
    FROM job_catalog
    WHERE id = v_catalog_id;
    
    -- Create new job
    INSERT INTO job_queue (
        tenant_id, catalog_id, job_name, job_family, input_data,
        priority, idempotency_key, max_retries, timeout_seconds
    ) VALUES (
        p_tenant_id, v_catalog_id, p_job_name, p_job_family, p_input_data,
        p_priority, p_idempotency_key, p_max_retries, p_timeout_seconds
    ) RETURNING id INTO v_job_id;
    
    RETURN v_job_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get next available job for a worker
CREATE OR REPLACE FUNCTION get_next_job(
    p_tenant_id UUID,
    p_worker_id VARCHAR(255),
    p_job_family VARCHAR(50) DEFAULT NULL
) RETURNS TABLE(
    job_id UUID,
    job_name VARCHAR(255),
    input_data JSONB,
    max_runtime_seconds INTEGER,
    timeout_seconds INTEGER
) AS $$
BEGIN
    -- Update current_tenant_id for RLS
    PERFORM set_config('app.current_tenant_id', p_tenant_id::TEXT, FALSE);
    
    RETURN QUERY
    UPDATE job_queue
    SET 
        status = 'in_progress',
        worker_id = p_worker_id,
        started_at = NOW(),
        worker_heartbeat = NOW()
    WHERE id = (
        SELECT id
        FROM job_queue
        WHERE tenant_id = p_tenant_id
          AND status = 'queued'
          AND (p_job_family IS NULL OR job_family = p_job_family)
          AND (next_retry_at IS NULL OR next_retry_at <= NOW())
        ORDER BY priority DESC, queued_at ASC
        LIMIT 1
        FOR UPDATE SKIP LOCKED
    )
    RETURNING 
        id,
        job_name,
        input_data,
        (SELECT max_runtime_seconds FROM job_catalog WHERE id = catalog_id),
        timeout_seconds;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to complete a job
CREATE OR REPLACE FUNCTION complete_job(
    p_job_id UUID,
    p_status VARCHAR(50),
    p_output_data JSONB DEFAULT '{}',
    p_error_data JSONB DEFAULT '{}'
) RETURNS VOID AS $$
DECLARE
    v_tenant_id UUID;
    v_job_family VARCHAR(50);
    v_execution_time_ms INTEGER;
BEGIN
    -- Get job details
    SELECT tenant_id, job_family INTO v_tenant_id, v_job_family
    FROM job_queue
    WHERE id = p_job_id;
    
    IF v_tenant_id IS NULL THEN
        RAISE EXCEPTION 'Job % not found', p_job_id;
    END IF;
    
    -- Update current_tenant_id for RLS
    PERFORM set_config('app.current_tenant_id', v_tenant_id::TEXT, FALSE);
    
    -- Calculate execution time
    SELECT EXTRACT(EPOCH FROM (NOW() - started_at)) * 1000 INTO v_execution_time_ms
    FROM job_queue
    WHERE id = p_job_id;
    
    -- Update job status
    UPDATE job_queue
    SET 
        status = p_status,
        output_data = CASE WHEN p_status = 'succeeded' THEN p_output_data ELSE output_data END,
        error_data = CASE WHEN p_status = 'failed' THEN p_error_data ELSE error_data END,
        completed_at = NOW(),
        execution_time_ms = v_execution_time_ms,
        worker_id = NULL,
        worker_heartbeat = NULL
    WHERE id = p_job_id;
    
    -- Move to dead letter if max retries exceeded
    IF p_status = 'failed' THEN
        INSERT INTO job_dead_letter (
            tenant_id, original_job_id, failure_reason, job_data_snapshot
        )
        SELECT 
            tenant_id, id, 
            COALESCE(p_error_data->>'error', 'Unknown error'),
            jsonb_build_object(
                'job_name', job_name,
                'input_data', input_data,
                'retry_count', retry_count,
                'max_retries', max_retries
            )
        FROM job_queue
        WHERE id = p_job_id AND retry_count >= max_retries;
    END IF;
    
    -- Record metrics
    INSERT INTO job_metrics (tenant_id, catalog_id, job_id, metric_name, metric_value, metric_unit, metric_type)
    VALUES (
        v_tenant_id,
        (SELECT catalog_id FROM job_queue WHERE id = p_job_id),
        p_job_id,
        'execution_time_ms',
        v_execution_time_ms,
        'milliseconds',
        'histogram'
    );
    
    INSERT INTO job_metrics (tenant_id, catalog_id, job_id, metric_name, metric_value, metric_unit, metric_type)
    VALUES (
        v_tenant_id,
        (SELECT catalog_id FROM job_queue WHERE id = p_job_id),
        p_job_id,
        'job_status',
        CASE p_status 
            WHEN 'succeeded' THEN 1 
            WHEN 'failed' THEN 0 
            ELSE 0.5 
        END,
        'status',
        'gauge'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to retry a failed job
CREATE OR REPLACE FUNCTION retry_job(
    p_job_id UUID,
    p_delay_seconds INTEGER DEFAULT 60
) RETURNS BOOLEAN AS $$
DECLARE
    v_tenant_id UUID;
    v_retry_count INTEGER;
    v_max_retries INTEGER;
BEGIN
    -- Get job details
    SELECT tenant_id, retry_count, max_retries INTO v_tenant_id, v_retry_count, v_max_retries
    FROM job_queue
    WHERE id = p_job_id;
    
    IF v_tenant_id IS NULL THEN
        RAISE EXCEPTION 'Job % not found', p_job_id;
    END IF;
    
    -- Check retry limits
    IF v_retry_count >= v_max_retries THEN
        RETURN FALSE;
    END IF;
    
    -- Update current_tenant_id for RLS
    PERFORM set_config('app.current_tenant_id', v_tenant_id::TEXT, FALSE);
    
    -- Update job for retry
    UPDATE job_queue
    SET 
        status = 'retrying',
        retry_count = retry_count + 1,
        next_retry_at = NOW() + (p_delay_seconds || ' seconds')::INTERVAL,
        worker_id = NULL,
        worker_heartbeat = NULL
    WHERE id = p_job_id;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to clean up old completed jobs
CREATE OR REPLACE FUNCTION cleanup_old_jobs(p_days_to_keep INTEGER DEFAULT 30) RETURNS INTEGER AS $$
DECLARE
    v_deleted_count INTEGER;
BEGIN
    DELETE FROM job_queue
    WHERE status IN ('succeeded', 'failed', 'canceled')
      AND completed_at < NOW() - (p_days_to_keep || ' days')::INTERVAL;
    
    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    
    -- Clean up old metrics
    DELETE FROM job_metrics
    WHERE recorded_at < NOW() - (p_days_to_keep || ' days')::INTERVAL;
    
    -- Clean up expired dead letter entries
    DELETE FROM job_dead_letter
    WHERE retention_expires_at < NOW();
    
    RETURN v_deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a cron job to clean up old jobs (runs daily at 2 AM)
SELECT cron.schedule(
    'cleanup-old-jobs',
    '0 2 * * *',
    'SELECT cleanup_old_jobs(30);'
);

-- Insert default job catalog entries for common job types
INSERT INTO job_catalog (tenant_id, job_name, job_family, job_key, max_runtime_seconds, max_retries, description, owner, sla_p95_seconds)
VALUES 
    ('00000000-0000-0000-0000-000000000000', 'security_scan', 'A', 'security_scan', 300, 3, 'Security vulnerability scan', 'SecurityAgent', 10),
    ('00000000-0000-0000-0000-000000000000', 'code_generation', 'A', 'code_generation', 600, 2, 'AI-powered code generation', 'DevAgent', 30),
    ('00000000-0000-0000-0000-000000000000', 'design_generation', 'A', 'design_generation', 900, 2, 'AI-powered design generation', 'DesignAgent', 45),
    ('00000000-0000-0000-0000-000000000000', 'data_migration', 'C', 'data_migration', 3600, 1, 'Database migration and ETL', 'MigrationAgent', 1800),
    ('00000000-0000-0000-0000-000000000000', 'backup_cleanup', 'B', 'backup_cleanup', 300, 3, 'Cleanup old backups and logs', 'OpsAgent', 60),
    ('00000000-0000-0000-0000-000000000000', 'health_check', 'B', 'health_check', 60, 3, 'System health monitoring', 'OpsAgent', 10),
    ('00000000-0000-0000-0000-000000000000', 'email_send', 'A', 'email_send', 120, 3, 'Send transactional emails', 'EmailAgent', 5),
    ('00000000-0000-0000-0000-000000000000', 'webhook_process', 'A', 'webhook_process', 180, 3, 'Process external webhooks', 'WebhookAgent', 15)
ON CONFLICT (tenant_id, job_key) DO NOTHING;

-- Create default schedules for recurring jobs
INSERT INTO job_schedules (tenant_id, catalog_id, schedule_name, cron_expression, description)
SELECT 
    '00000000-0000-0000-0000-000000000000',
    id,
    'daily_backup_cleanup',
    '0 2 * * *',
    'Daily backup cleanup at 2 AM UTC'
FROM job_catalog 
WHERE job_key = 'backup_cleanup';

INSERT INTO job_schedules (tenant_id, catalog_id, schedule_name, cron_expression, description)
SELECT 
    '00000000-0000-0000-0000-000000000000',
    id,
    'health_check_every_5min',
    '*/5 * * * *',
    'Health check every 5 minutes'
FROM job_catalog 
WHERE job_key = 'health_check';

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Create view for job monitoring
CREATE OR REPLACE VIEW job_monitoring AS
SELECT 
    jq.id,
    jq.tenant_id,
    jq.job_name,
    jq.job_family,
    jq.status,
    jq.priority,
    jq.retry_count,
    jq.queued_at,
    jq.started_at,
    jq.completed_at,
    jq.execution_time_ms,
    jq.queue_time_ms,
    jc.max_runtime_seconds,
    jc.sla_p95_seconds,
    jc.owner,
    CASE 
        WHEN jq.status = 'succeeded' AND jq.execution_time_ms <= (jc.sla_p95_seconds * 1000) THEN 'within_sla'
        WHEN jq.status = 'succeeded' AND jq.execution_time_ms > (jc.sla_p95_seconds * 1000) THEN 'sla_breach'
        WHEN jq.status = 'failed' THEN 'failed'
        WHEN jq.status = 'in_progress' AND jq.started_at < NOW() - (jc.max_runtime_seconds || ' seconds')::INTERVAL THEN 'timeout'
        ELSE 'normal'
    END as sla_status
FROM job_queue jq
JOIN job_catalog jc ON jq.catalog_id = jc.id;

-- Grant access to monitoring view
GRANT SELECT ON job_monitoring TO authenticated;
