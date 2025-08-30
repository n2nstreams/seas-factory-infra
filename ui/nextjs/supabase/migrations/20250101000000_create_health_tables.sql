-- Create health monitoring tables for Module 8: Observability
-- This migration sets up tables for storing health check results and metrics

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create health_check table for storing individual health check results
CREATE TABLE IF NOT EXISTS health_check (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    service_name TEXT NOT NULL,
    check_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pass', 'fail', 'warn')),
    response_time_ms INTEGER,
    error_message TEXT,
    details JSONB,
    correlation_id TEXT,
    trace_id TEXT,
    span_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create health_metrics table for storing aggregated health metrics
CREATE TABLE IF NOT EXISTS health_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    error_rate DECIMAL(5,4) NOT NULL CHECK (error_rate >= 0 AND error_rate <= 1),
    response_time_ms INTEGER NOT NULL CHECK (response_time_ms >= 0),
    uptime DECIMAL(5,4) NOT NULL CHECK (uptime >= 0 AND uptime <= 1),
    job_failures INTEGER NOT NULL DEFAULT 0 CHECK (job_failures >= 0),
    auth_failures INTEGER NOT NULL DEFAULT 0 CHECK (auth_failures >= 0),
    webhook_failures INTEGER NOT NULL DEFAULT 0 CHECK (webhook_failures >= 0),
    overall_score INTEGER NOT NULL CHECK (overall_score >= 0 AND overall_score <= 100),
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create health_summary table for storing daily health summaries
CREATE TABLE IF NOT EXISTS health_summary (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL UNIQUE,
    total_checks INTEGER NOT NULL DEFAULT 0,
    passed_checks INTEGER NOT NULL DEFAULT 0,
    failed_checks INTEGER NOT NULL DEFAULT 0,
    warning_checks INTEGER NOT NULL DEFAULT 0,
    avg_health_score DECIMAL(5,2) NOT NULL CHECK (avg_health_score >= 0 AND avg_health_score <= 100),
    avg_response_time_ms INTEGER NOT NULL DEFAULT 0,
    uptime_percentage DECIMAL(5,2) NOT NULL DEFAULT 0 CHECK (uptime_percentage >= 0 AND uptime_percentage <= 100),
    error_rate DECIMAL(5,4) NOT NULL DEFAULT 0 CHECK (error_rate >= 0 AND error_rate <= 1),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_health_check_timestamp ON health_check(timestamp);
CREATE INDEX IF NOT EXISTS idx_health_check_service_name ON health_check(service_name);
CREATE INDEX IF NOT EXISTS idx_health_check_status ON health_check(status);
CREATE INDEX IF NOT EXISTS idx_health_check_correlation_id ON health_check(correlation_id);

CREATE INDEX IF NOT EXISTS idx_health_metrics_timestamp ON health_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_health_metrics_overall_score ON health_metrics(overall_score);

CREATE INDEX IF NOT EXISTS idx_health_summary_date ON health_summary(date);

-- Create RLS policies for multi-tenant security
ALTER TABLE health_check ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_summary ENABLE ROW LEVEL SECURITY;

-- RLS policy for health_check table
CREATE POLICY "Allow read access to health checks for authenticated users" ON health_check
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow insert access to health checks for service accounts" ON health_check
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- RLS policy for health_metrics table
CREATE POLICY "Allow read access to health metrics for authenticated users" ON health_metrics
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow insert access to health metrics for service accounts" ON health_metrics
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- RLS policy for health_summary table
CREATE POLICY "Allow read access to health summaries for authenticated users" ON health_summary
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow insert access to health summaries for service accounts" ON health_summary
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Create function to update health summary
CREATE OR REPLACE FUNCTION update_health_summary()
RETURNS TRIGGER AS $$
BEGIN
    -- Update or insert daily summary
    INSERT INTO health_summary (
        date,
        total_checks,
        passed_checks,
        failed_checks,
        warning_checks,
        avg_health_score,
        avg_response_time_ms,
        uptime_percentage,
        error_rate
    )
    VALUES (
        DATE(NEW.timestamp),
        (SELECT COUNT(*) FROM health_check WHERE DATE(timestamp) = DATE(NEW.timestamp)),
        (SELECT COUNT(*) FROM health_check WHERE DATE(timestamp) = DATE(NEW.timestamp) AND status = 'pass'),
        (SELECT COUNT(*) FROM health_check WHERE DATE(timestamp) = DATE(NEW.timestamp) AND status = 'fail'),
        (SELECT COUNT(*) FROM health_check WHERE DATE(timestamp) = DATE(NEW.timestamp) AND status = 'warn'),
        (SELECT AVG(overall_score) FROM health_metrics WHERE DATE(timestamp) = DATE(NEW.timestamp)),
        (SELECT AVG(response_time_ms) FROM health_metrics WHERE DATE(timestamp) = DATE(NEW.timestamp)),
        (SELECT AVG(uptime) * 100 FROM health_metrics WHERE DATE(timestamp) = DATE(NEW.timestamp)),
        (SELECT AVG(error_rate) FROM health_metrics WHERE DATE(timestamp) = DATE(NEW.timestamp))
    )
    ON CONFLICT (date) DO UPDATE SET
        total_checks = EXCLUDED.total_checks,
        passed_checks = EXCLUDED.passed_checks,
        failed_checks = EXCLUDED.failed_checks,
        warning_checks = EXCLUDED.warning_checks,
        avg_health_score = EXCLUDED.avg_health_score,
        avg_response_time_ms = EXCLUDED.avg_response_time_ms,
        uptime_percentage = EXCLUDED.uptime_percentage,
        error_rate = EXCLUDED.error_rate,
        updated_at = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update health summary
CREATE TRIGGER trigger_update_health_summary
    AFTER INSERT OR UPDATE ON health_metrics
    FOR EACH ROW
    EXECUTE FUNCTION update_health_summary();

-- Create function to clean up old health data (keep last 30 days)
CREATE OR REPLACE FUNCTION cleanup_old_health_data()
RETURNS void AS $$
BEGIN
    DELETE FROM health_check WHERE timestamp < NOW() - INTERVAL '30 days';
    DELETE FROM health_metrics WHERE timestamp < NOW() - INTERVAL '30 days';
    DELETE FROM health_summary WHERE date < CURRENT_DATE - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Create a scheduled job to clean up old data (runs daily)
SELECT cron.schedule(
    'cleanup-old-health-data',
    '0 2 * * *', -- Daily at 2 AM
    'SELECT cleanup_old_health_data();'
);

-- Insert initial health check record for testing
INSERT INTO health_check (
    service_name,
    check_name,
    status,
    response_time_ms,
    details
) VALUES (
    'system',
    'initialization',
    'pass',
    0,
    '{"message": "Health monitoring system initialized", "version": "1.0.0"}'
) ON CONFLICT DO NOTHING;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON health_check TO authenticated;
GRANT ALL ON health_metrics TO authenticated;
GRANT ALL ON health_summary TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;
