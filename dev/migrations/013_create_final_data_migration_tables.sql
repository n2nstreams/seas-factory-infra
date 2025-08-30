-- Migration 013: Create Final Data Migration Tables
-- Module 13: Final Data Migration - Source-of-Truth Cutover
-- This migration creates the necessary tables for managing the final data migration process

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create cutover_tables table to track migration status for each table
CREATE TABLE IF NOT EXISTS cutover_tables (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'ready', 'cutover', 'completed', 'rolled_back')),
    read_source VARCHAR(50) NOT NULL DEFAULT 'legacy' CHECK (read_source IN ('legacy', 'supabase', 'dual')),
    write_source VARCHAR(50) NOT NULL DEFAULT 'dual' CHECK (write_source IN ('legacy', 'supabase', 'dual')),
    last_validation TIMESTAMP WITH TIME ZONE,
    validation_status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (validation_status IN ('pending', 'passed', 'failed')),
    drift_percentage DECIMAL(5,4) NOT NULL DEFAULT 0.0000,
    record_count_legacy INTEGER NOT NULL DEFAULT 0,
    record_count_supabase INTEGER NOT NULL DEFAULT 0,
    record_count_difference INTEGER NOT NULL DEFAULT 0,
    referential_integrity_status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (referential_integrity_status IN ('pending', 'clean', 'issues')),
    referential_integrity_issues TEXT[] DEFAULT '{}',
    cutover_date TIMESTAMP WITH TIME ZONE,
    rollback_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create cutover_checklists table to track pre-cutover validation
CREATE TABLE IF NOT EXISTS cutover_checklists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(255) NOT NULL,
    data_consistency BOOLEAN NOT NULL DEFAULT FALSE,
    referential_integrity BOOLEAN NOT NULL DEFAULT FALSE,
    performance_validation BOOLEAN NOT NULL DEFAULT FALSE,
    security_validation BOOLEAN NOT NULL DEFAULT FALSE,
    backup_complete BOOLEAN NOT NULL DEFAULT FALSE,
    freeze_window_scheduled BOOLEAN NOT NULL DEFAULT FALSE,
    team_notified BOOLEAN NOT NULL DEFAULT FALSE,
    rollback_plan_ready BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,
    completed_by UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (table_name) REFERENCES cutover_tables(name) ON DELETE CASCADE
);

-- Create freeze_windows table to manage cutover freeze periods
CREATE TABLE IF NOT EXISTS freeze_windows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'active', 'completed', 'cancelled')),
    affected_tables TEXT[] NOT NULL DEFAULT '{}',
    description TEXT NOT NULL,
    created_by UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create reconciliation_jobs table to track data reconciliation processes
CREATE TABLE IF NOT EXISTS reconciliation_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    type VARCHAR(50) NOT NULL CHECK (type IN ('full', 'incremental', 'drift_check')),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    records_processed INTEGER NOT NULL DEFAULT 0,
    records_total INTEGER NOT NULL DEFAULT 0,
    drift_detected INTEGER NOT NULL DEFAULT 0,
    errors TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (table_name) REFERENCES cutover_tables(name) ON DELETE CASCADE
);

-- Create cutover_audit_log table to track all cutover operations
CREATE TABLE IF NOT EXISTS cutover_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(255) NOT NULL,
    operation VARCHAR(50) NOT NULL CHECK (operation IN ('prepare', 'cutover', 'rollback', 'validation', 'reconciliation')),
    status VARCHAR(50) NOT NULL CHECK (status IN ('success', 'failure', 'in_progress')),
    user_id UUID NOT NULL,
    details JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (table_name) REFERENCES cutover_tables(name) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_cutover_tables_status ON cutover_tables(status);
CREATE INDEX IF NOT EXISTS idx_cutover_tables_read_source ON cutover_tables(read_source);
CREATE INDEX IF NOT EXISTS idx_cutover_tables_validation_status ON cutover_tables(validation_status);
CREATE INDEX IF NOT EXISTS idx_cutover_checklists_table_name ON cutover_checklists(table_name);
CREATE INDEX IF NOT EXISTS idx_freeze_windows_status ON freeze_windows(status);
CREATE INDEX IF NOT EXISTS idx_freeze_windows_start_time ON freeze_windows(start_time);
CREATE INDEX IF NOT EXISTS idx_reconciliation_jobs_table_name ON reconciliation_jobs(table_name);
CREATE INDEX IF NOT EXISTS idx_reconciliation_jobs_status ON reconciliation_jobs(status);
CREATE INDEX IF NOT EXISTS idx_cutover_audit_log_table_name ON cutover_audit_log(table_name);
CREATE INDEX IF NOT EXISTS idx_cutover_audit_log_operation ON cutover_audit_log(operation);
CREATE INDEX IF NOT EXISTS idx_cutover_audit_log_created_at ON cutover_audit_log(created_at);

-- Create RLS policies for tenant isolation
ALTER TABLE cutover_tables ENABLE ROW LEVEL SECURITY;
ALTER TABLE cutover_checklists ENABLE ROW LEVEL SECURITY;
ALTER TABLE freeze_windows ENABLE ROW LEVEL SECURITY;
ALTER TABLE reconciliation_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE cutover_audit_log ENABLE ROW LEVEL SECURITY;

-- RLS Policy for cutover_tables (admin only)
CREATE POLICY "cutover_tables_admin_only" ON cutover_tables
    FOR ALL USING (
        auth.jwt() ->> 'role' = 'admin' OR
        auth.jwt() ->> 'plan' = 'growth'
    );

-- RLS Policy for cutover_checklists (admin only)
CREATE POLICY "cutover_checklists_admin_only" ON cutover_checklists
    FOR ALL USING (
        auth.jwt() ->> 'role' = 'admin' OR
        auth.jwt() ->> 'plan' = 'growth'
    );

-- RLS Policy for freeze_windows (admin only)
CREATE POLICY "freeze_windows_admin_only" ON freeze_windows
    FOR ALL USING (
        auth.jwt() ->> 'role' = 'admin' OR
        auth.jwt() ->> 'plan' = 'growth'
    );

-- RLS Policy for reconciliation_jobs (admin only)
CREATE POLICY "reconciliation_jobs_admin_only" ON reconciliation_jobs
    FOR ALL USING (
        auth.jwt() ->> 'role' = 'admin' OR
        auth.jwt() ->> 'plan' = 'growth'
    );

-- RLS Policy for cutover_audit_log (admin only)
CREATE POLICY "cutover_audit_log_admin_only" ON cutover_audit_log
    FOR ALL USING (
        auth.jwt() ->> 'role' = 'admin' OR
        auth.jwt() ->> 'plan' = 'growth'
    );

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_cutover_tables_updated_at 
    BEFORE UPDATE ON cutover_tables 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cutover_checklists_updated_at 
    BEFORE UPDATE ON cutover_checklists 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_freeze_windows_updated_at 
    BEFORE UPDATE ON freeze_windows 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reconciliation_jobs_updated_at 
    BEFORE UPDATE ON reconciliation_jobs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial data for core tables
INSERT INTO cutover_tables (name, status, read_source, write_source) VALUES
    ('tenants', 'pending', 'legacy', 'dual'),
    ('users', 'pending', 'legacy', 'dual'),
    ('projects', 'pending', 'legacy', 'dual'),
    ('ideas', 'pending', 'legacy', 'dual')
ON CONFLICT (name) DO NOTHING;

-- Create view for migration overview
CREATE OR REPLACE VIEW migration_overview AS
SELECT 
    COUNT(*) as total_tables,
    COUNT(*) FILTER (WHERE status = 'ready') as ready_for_cutover,
    COUNT(*) FILTER (WHERE status = 'cutover') as in_progress,
    COUNT(*) FILTER (WHERE status = 'completed') as completed,
    COUNT(*) FILTER (WHERE status = 'rolled_back') as rolled_back,
    ROUND(
        (COUNT(*) FILTER (WHERE status = 'completed')::DECIMAL / COUNT(*)::DECIMAL) * 100, 2
    ) as overall_progress
FROM cutover_tables;

-- Create function to get table migration status
CREATE OR REPLACE FUNCTION get_table_migration_status(p_table_name VARCHAR)
RETURNS TABLE (
    table_name VARCHAR,
    status VARCHAR,
    read_source VARCHAR,
    write_source VARCHAR,
    validation_status VARCHAR,
    drift_percentage DECIMAL,
    record_count_legacy INTEGER,
    record_count_supabase INTEGER,
    record_count_difference INTEGER,
    last_validation TIMESTAMP WITH TIME ZONE,
    cutover_date TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ct.name,
        ct.status,
        ct.read_source,
        ct.write_source,
        ct.validation_status,
        ct.drift_percentage,
        ct.record_count_legacy,
        ct.record_count_supabase,
        ct.record_count_difference,
        ct.last_validation,
        ct.cutover_date
    FROM cutover_tables ct
    WHERE ct.name = p_table_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON cutover_tables TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON cutover_checklists TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON freeze_windows TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON reconciliation_jobs TO authenticated;
GRANT SELECT, INSERT ON cutover_audit_log TO authenticated;
GRANT SELECT ON migration_overview TO authenticated;
GRANT EXECUTE ON FUNCTION get_table_migration_status(VARCHAR) TO authenticated;

-- Create comment documentation
COMMENT ON TABLE cutover_tables IS 'Tracks the migration status of each table during final data migration';
COMMENT ON TABLE cutover_checklists IS 'Pre-cutover validation checklists for each table';
COMMENT ON TABLE freeze_windows IS 'Scheduled freeze windows for safe cutover operations';
COMMENT ON TABLE reconciliation_jobs IS 'Data reconciliation jobs to maintain consistency';
COMMENT ON TABLE cutover_audit_log IS 'Audit log of all cutover operations for compliance';
COMMENT ON VIEW migration_overview IS 'Overview of migration progress across all tables';
COMMENT ON FUNCTION get_table_migration_status(VARCHAR) IS 'Get detailed migration status for a specific table';
