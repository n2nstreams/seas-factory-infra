-- Migration 008: Add GDPR consent tracking to users table
-- Night 65: Privacy stub with linkable DPA and GDPR checkbox

-- Add GDPR consent tracking columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS gdpr_consent_given BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS gdpr_consent_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS gdpr_consent_ip VARCHAR(45);
ALTER TABLE users ADD COLUMN IF NOT EXISTS privacy_policy_version VARCHAR(50) DEFAULT '1.0';
ALTER TABLE users ADD COLUMN IF NOT EXISTS dpa_version VARCHAR(50) DEFAULT '1.0';

-- Create privacy consent audit table for full compliance tracking
CREATE TABLE IF NOT EXISTS privacy_consent_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    consent_type VARCHAR(50) NOT NULL, -- 'gdpr', 'terms', 'privacy_policy', 'dpa'
    consent_given BOOLEAN NOT NULL,
    consent_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    consent_ip VARCHAR(45),
    document_version VARCHAR(50),
    user_agent TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_privacy_consent_audit_user_id ON privacy_consent_audit(user_id);
CREATE INDEX IF NOT EXISTS idx_privacy_consent_audit_tenant_id ON privacy_consent_audit(tenant_id);
CREATE INDEX IF NOT EXISTS idx_privacy_consent_audit_consent_type ON privacy_consent_audit(consent_type);
CREATE INDEX IF NOT EXISTS idx_privacy_consent_audit_consent_date ON privacy_consent_audit(consent_date);

-- Add comments for documentation
COMMENT ON TABLE privacy_consent_audit IS 'Full audit trail of all privacy consents for GDPR compliance';
COMMENT ON COLUMN privacy_consent_audit.consent_type IS 'Type of consent: gdpr, terms, privacy_policy, dpa';
COMMENT ON COLUMN privacy_consent_audit.consent_given IS 'True if consent was given, false if withdrawn';
COMMENT ON COLUMN privacy_consent_audit.document_version IS 'Version of the document when consent was given';

-- Update existing users to have default consent values
UPDATE users 
SET 
    gdpr_consent_given = TRUE,
    gdpr_consent_date = created_at,
    privacy_policy_version = '1.0',
    dpa_version = '1.0'
WHERE gdpr_consent_given IS NULL;

-- Insert audit records for existing users
INSERT INTO privacy_consent_audit (user_id, tenant_id, consent_type, consent_given, consent_date, document_version, notes)
SELECT 
    id,
    tenant_id,
    'gdpr',
    TRUE,
    created_at,
    '1.0',
    'Retroactive consent for existing users - Night 65 migration'
FROM users 
WHERE id NOT IN (
    SELECT DISTINCT user_id 
    FROM privacy_consent_audit 
    WHERE consent_type = 'gdpr' AND user_id IS NOT NULL
); 