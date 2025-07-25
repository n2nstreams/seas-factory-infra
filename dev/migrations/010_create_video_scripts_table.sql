-- Migration: 010_create_video_scripts_table.sql
-- Description: Add video scripts table for DocAgent YouTube script generation
-- Night: 73
-- Date: 2024-12-22

BEGIN;

-- Create video scripts table
CREATE TABLE IF NOT EXISTS video_scripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    script_content TEXT NOT NULL,
    script_style VARCHAR(50) NOT NULL DEFAULT 'overview', -- explainer, demo, tutorial, overview
    target_audience VARCHAR(50) NOT NULL DEFAULT 'general_audience',
    video_duration INTEGER NOT NULL DEFAULT 5, -- minutes
    word_count INTEGER NOT NULL,
    include_synthesia_cues BOOLEAN DEFAULT true,
    
    -- Metadata
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Version tracking
    version INTEGER DEFAULT 1,
    parent_script_id UUID REFERENCES video_scripts(id),
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'draft', -- draft, review, approved, published, archived
    published_at TIMESTAMP WITH TIME ZONE,
    
    -- Synthesia integration
    synthesia_video_id VARCHAR(255),
    synthesia_status VARCHAR(50), -- pending, processing, completed, failed
    video_url TEXT,
    thumbnail_url TEXT,
    
    -- Analytics
    view_count INTEGER DEFAULT 0,
    engagement_score DECIMAL(5,2),
    
    CONSTRAINT fk_video_scripts_tenant FOREIGN KEY (tenant_id) 
        REFERENCES tenants(id) ON DELETE CASCADE,
    CONSTRAINT fk_video_scripts_creator FOREIGN KEY (created_by) 
        REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT valid_script_style CHECK (script_style IN ('explainer', 'demo', 'tutorial', 'overview')),
    CONSTRAINT valid_target_audience CHECK (target_audience IN ('developers', 'users', 'admins', 'contributors', 'general_audience')),
    CONSTRAINT valid_status CHECK (status IN ('draft', 'review', 'approved', 'published', 'archived')),
    CONSTRAINT positive_duration CHECK (video_duration > 0 AND video_duration <= 60),
    CONSTRAINT positive_word_count CHECK (word_count > 0)
);

-- Create indexes for performance
CREATE INDEX idx_video_scripts_tenant_id ON video_scripts(tenant_id);
CREATE INDEX idx_video_scripts_status ON video_scripts(status);
CREATE INDEX idx_video_scripts_created_at ON video_scripts(generated_at);
CREATE INDEX idx_video_scripts_style ON video_scripts(script_style);
CREATE INDEX idx_video_scripts_audience ON video_scripts(target_audience);
CREATE INDEX idx_video_scripts_synthesia_status ON video_scripts(synthesia_status);

-- Enable Row Level Security
ALTER TABLE video_scripts ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY video_scripts_tenant_isolation ON video_scripts
    FOR ALL USING (tenant_id = current_setting('app.tenant_id')::UUID);

CREATE POLICY video_scripts_creator_access ON video_scripts
    FOR ALL USING (created_by = current_setting('app.user_id')::UUID);

-- Create trigger for updated_at
CREATE TRIGGER update_video_scripts_updated_at
    BEFORE UPDATE ON video_scripts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to generate script analytics
CREATE OR REPLACE FUNCTION calculate_script_engagement_score(script_id UUID)
RETURNS DECIMAL(5,2) AS $$
DECLARE
    score DECIMAL(5,2) := 0.0;
    script_length INTEGER;
    view_count INTEGER;
    word_density DECIMAL(5,2);
BEGIN
    SELECT 
        vs.word_count,
        vs.view_count,
        vs.video_duration
    INTO script_length, view_count, script_length
    FROM video_scripts vs
    WHERE vs.id = script_id;
    
    -- Calculate engagement based on views, length, and word density
    IF view_count > 0 THEN
        word_density := script_length / NULLIF(script_length, 0.0);
        score := LEAST(10.0, 
            (view_count * 0.1) + 
            (word_density * 2.0) + 
            (CASE WHEN script_length BETWEEN 3 AND 7 THEN 2.0 ELSE 0.0 END)
        );
    END IF;
    
    RETURN score;
END;
$$ LANGUAGE plpgsql;

-- Create view for script analytics
CREATE VIEW video_script_analytics AS
SELECT 
    vs.id,
    vs.tenant_id,
    vs.title,
    vs.script_style,
    vs.target_audience,
    vs.video_duration,
    vs.word_count,
    vs.view_count,
    vs.status,
    vs.generated_at,
    vs.published_at,
    calculate_script_engagement_score(vs.id) as engagement_score,
    -- Word density (words per minute)
    ROUND(vs.word_count::DECIMAL / vs.video_duration::DECIMAL, 2) as words_per_minute,
    -- Time metrics
    CASE 
        WHEN vs.published_at IS NOT NULL 
        THEN EXTRACT(EPOCH FROM (vs.published_at - vs.generated_at))/3600 
        ELSE NULL 
    END as hours_to_publish,
    -- Performance metrics
    CASE 
        WHEN vs.view_count > 1000 THEN 'high'
        WHEN vs.view_count > 100 THEN 'medium'
        ELSE 'low'
    END as performance_tier
FROM video_scripts vs;

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON video_scripts TO factory_app;
GRANT SELECT ON video_script_analytics TO factory_app;
GRANT USAGE ON SEQUENCE video_scripts_id_seq TO factory_app;

-- Add sample data for testing
INSERT INTO video_scripts (
    tenant_id, 
    title, 
    description,
    script_content,
    script_style,
    target_audience,
    video_duration,
    word_count,
    status,
    created_by
) VALUES (
    (SELECT id FROM tenants WHERE name = 'Default Tenant' LIMIT 1),
    'AI SaaS Factory Overview',
    'Introduction video explaining the AI SaaS Factory platform',
    '# AI SaaS Factory Overview\n\nWelcome to the future of software development...',
    'overview',
    'general_audience',
    5,
    850,
    'draft',
    (SELECT id FROM users WHERE email = 'admin@saas-factory.com' LIMIT 1)
);

COMMIT;

-- Add comment for documentation
COMMENT ON TABLE video_scripts IS 'Stores YouTube scripts generated by DocAgent for Synthesia video creation';
COMMENT ON COLUMN video_scripts.script_content IS 'Full script content with Synthesia formatting and timing cues';
COMMENT ON COLUMN video_scripts.synthesia_video_id IS 'ID returned by Synthesia API when video is generated';
COMMENT ON COLUMN video_scripts.engagement_score IS 'Calculated engagement score based on views and content quality'; 