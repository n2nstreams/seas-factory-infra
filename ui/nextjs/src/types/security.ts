// Security & Compliance Types for Module 11
// Comprehensive type definitions for the security and compliance system

// ============================================================================
// DATA CLASSIFICATION TYPES
// ============================================================================

export type DataClassificationLevel = 'P0' | 'P1' | 'P2';
export type DataType = 'pii' | 'payment' | 'user_content' | 'telemetry';

export interface DataClassification {
  id: string;
  tenant_id: string;
  table_name: string;
  column_name?: string;
  classification_level: DataClassificationLevel;
  data_type: DataType;
  gdpr_impact: boolean;
  pci_impact: boolean;
  retention_days?: number;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
}

export interface DataClassificationCreate {
  tenant_id: string;
  table_name: string;
  column_name?: string;
  classification_level: DataClassificationLevel;
  data_type: DataType;
  gdpr_impact?: boolean;
  pci_impact?: boolean;
  retention_days?: number;
}

export interface DataClassificationUpdate {
  classification_level?: DataClassificationLevel;
  data_type?: DataType;
  gdpr_impact?: boolean;
  pci_impact?: boolean;
  retention_days?: number;
}

// ============================================================================
// ACCESS REVIEW TYPES
// ============================================================================

export type ReviewType = 'quarterly' | 'annual' | 'ad-hoc' | 'incident';
export type ReviewStatus = 'pending' | 'in_progress' | 'completed' | 'overdue';

export interface AccessReview {
  id: string;
  tenant_id: string;
  review_type: ReviewType;
  review_period_start: string;
  review_period_end: string;
  status: ReviewStatus;
  scope_description: string;
  key_holders_count: number;
  service_accounts_count: number;
  findings_summary?: string;
  risk_score?: number;
  remediation_required: boolean;
  assigned_reviewer_id?: string;
  assigned_approver_id?: string;
  due_date: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
}

export interface AccessReviewCreate {
  tenant_id: string;
  review_type: ReviewType;
  review_period_start: string;
  review_period_end: string;
  scope_description: string;
  due_date: string;
  assigned_reviewer_id?: string;
  assigned_approver_id?: string;
}

export interface AccessReviewUpdate {
  status?: ReviewStatus;
  findings_summary?: string;
  risk_score?: number;
  remediation_required?: boolean;
  assigned_reviewer_id?: string;
  assigned_approver_id?: string;
  completed_at?: string;
}

// ============================================================================
// KEY HOLDER TYPES
// ============================================================================

export type KeyType = 'stripe' | 'service_account' | 'api_key' | 'database' | 'other';
export type AccessLevel = 'read' | 'write' | 'admin' | 'full';
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';
export type KeyStatus = 'active' | 'rotated' | 'revoked' | 'expired';

export interface KeyHolder {
  id: string;
  access_review_id: string;
  tenant_id: string;
  holder_name: string;
  holder_email?: string;
  holder_role?: string;
  key_type: KeyType;
  key_name: string;
  key_purpose?: string;
  key_scope?: string;
  access_level: AccessLevel;
  last_used_at?: string;
  rotation_schedule_days?: number;
  next_rotation_date?: string;
  risk_level: RiskLevel;
  justification?: string;
  status: KeyStatus;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
}

export interface KeyHolderCreate {
  access_review_id: string;
  tenant_id: string;
  holder_name: string;
  holder_email?: string;
  holder_role?: string;
  key_type: KeyType;
  key_name: string;
  key_purpose?: string;
  key_scope?: string;
  access_level: AccessLevel;
  rotation_schedule_days?: number;
  next_rotation_date?: string;
  risk_level?: RiskLevel;
  justification?: string;
}

export interface KeyHolderUpdate {
  holder_name?: string;
  holder_email?: string;
  holder_role?: string;
  key_purpose?: string;
  key_scope?: string;
  access_level?: AccessLevel;
  rotation_schedule_days?: number;
  next_rotation_date?: string;
  risk_level?: RiskLevel;
  justification?: string;
  status?: KeyStatus;
}

// ============================================================================
// ADMIN ACTION AUDIT TYPES
// ============================================================================

export type ActionCategory = 'security' | 'compliance' | 'user_management' | 'system_config';
export type RiskAssessment = 'low' | 'medium' | 'high' | 'critical';

export interface AdminActionAudit {
  id: string;
  tenant_id: string;
  admin_user_id: string;
  action_type: string;
  action_category: ActionCategory;
  target_type: string;
  target_id: string;
  action_data: Record<string, any>;
  old_values?: Record<string, any>;
  new_values?: Record<string, any>;
  reason: string;
  business_justification?: string;
  risk_assessment: RiskAssessment;
  requires_approval: boolean;
  approved_by?: string;
  approved_at?: string;
  approval_notes?: string;
  ip_address?: string;
  user_agent?: string;
  session_id?: string;
  correlation_id?: string;
  action_started_at: string;
  action_completed_at?: string;
  duration_ms?: number;
  created_at: string;
  updated_at: string;
}

export interface AdminActionAuditCreate {
  tenant_id: string;
  admin_user_id: string;
  action_type: string;
  action_category: ActionCategory;
  target_type: string;
  target_id: string;
  action_data?: Record<string, any>;
  old_values?: Record<string, any>;
  new_values?: Record<string, any>;
  reason: string;
  business_justification?: string;
  risk_assessment?: RiskAssessment;
  requires_approval?: boolean;
  ip_address?: string;
  user_agent?: string;
  session_id?: string;
  correlation_id?: string;
}

export interface AdminActionAuditUpdate {
  action_completed_at?: string;
  duration_ms?: number;
  approved_by?: string;
  approved_at?: string;
  approval_notes?: string;
}

// ============================================================================
// SECURITY POLICIES TYPES
// ============================================================================

export type PolicyType = 'access_control' | 'data_protection' | 'audit' | 'incident_response';
export type EnforcementLevel = 'advisory' | 'recommended' | 'strict' | 'blocking';
export type PolicyStatus = 'draft' | 'active' | 'deprecated' | 'archived';

export interface SecurityPolicy {
  id: string;
  tenant_id: string;
  policy_name: string;
  policy_type: PolicyType;
  policy_version: string;
  policy_description: string;
  policy_rules: Record<string, any>;
  compliance_requirements: string[];
  is_enforced: boolean;
  enforcement_level: EnforcementLevel;
  status: PolicyStatus;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
}

export interface SecurityPolicyCreate {
  tenant_id: string;
  policy_name: string;
  policy_type: PolicyType;
  policy_version?: string;
  policy_description: string;
  policy_rules: Record<string, any>;
  compliance_requirements?: string[];
  is_enforced?: boolean;
  enforcement_level?: EnforcementLevel;
  status?: PolicyStatus;
}

export interface SecurityPolicyUpdate {
  policy_description?: string;
  policy_rules?: Record<string, any>;
  compliance_requirements?: string[];
  is_enforced?: boolean;
  enforcement_level?: EnforcementLevel;
  status?: PolicyStatus;
}

// ============================================================================
// COMPLIANCE CHECKS TYPES
// ============================================================================

export type CheckType = 'gdpr' | 'pci' | 'soc2' | 'custom';
export type CheckFrequency = 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'annually';
export type CheckResult = 'pending' | 'pass' | 'fail' | 'warning' | 'error';

export interface ComplianceCheck {
  id: string;
  tenant_id: string;
  check_name: string;
  check_type: CheckType;
  check_frequency: CheckFrequency;
  last_check_date?: string;
  last_check_result: CheckResult;
  last_check_details?: string;
  is_compliant: boolean;
  compliance_score?: number;
  next_check_date?: string;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
}

export interface ComplianceCheckCreate {
  tenant_id: string;
  check_name: string;
  check_type: CheckType;
  check_frequency?: CheckFrequency;
  next_check_date?: string;
}

export interface ComplianceCheckUpdate {
  last_check_date?: string;
  last_check_result?: CheckResult;
  last_check_details?: string;
  is_compliant?: boolean;
  compliance_score?: number;
  next_check_date?: string;
}

// ============================================================================
// SECURITY COMPLIANCE SUMMARY TYPES
// ============================================================================

export interface SecurityComplianceSummary {
  tenant_id: string;
  overall_compliance_score: number;
  data_classification_summary: {
    p0_count: number;
    p1_count: number;
    p2_count: number;
    gdpr_impact_count: number;
    pci_impact_count: number;
  };
  access_review_summary: {
    total_reviews: number;
    pending_reviews: number;
    overdue_reviews: number;
    completed_reviews: number;
  };
  key_holder_summary: {
    total_keys: number;
    high_risk_keys: number;
    keys_due_rotation: number;
    revoked_keys: number;
  };
  admin_actions_summary: {
    total_actions: number;
    pending_approvals: number;
    high_risk_actions: number;
    actions_this_month: number;
  };
  compliance_checks_summary: {
    total_checks: number;
    compliant_checks: number;
    non_compliant_checks: number;
    checks_due_soon: number;
  };
  last_updated: string;
}

// ============================================================================
// SECURITY COMPLIANCE API RESPONSES
// ============================================================================

export interface SecurityComplianceApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
  correlation_id?: string;
}

export interface SecurityComplianceListResponse<T> {
  success: boolean;
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
  };
  timestamp: string;
  correlation_id?: string;
}

// ============================================================================
// SECURITY COMPLIANCE FILTERS
// ============================================================================

export interface DataClassificationFilters {
  tenant_id?: string;
  classification_level?: DataClassificationLevel;
  data_type?: DataType;
  table_name?: string;
  gdpr_impact?: boolean;
  pci_impact?: boolean;
}

export interface AccessReviewFilters {
  tenant_id?: string;
  review_type?: ReviewType;
  status?: ReviewStatus;
  assigned_reviewer_id?: string;
  due_date_from?: string;
  due_date_to?: string;
}

export interface KeyHolderFilters {
  tenant_id?: string;
  access_review_id?: string;
  key_type?: KeyType;
  risk_level?: RiskLevel;
  status?: KeyStatus;
  next_rotation_date_from?: string;
  next_rotation_date_to?: string;
}

export interface AdminActionAuditFilters {
  tenant_id?: string;
  admin_user_id?: string;
  action_type?: string;
  action_category?: ActionCategory;
  target_type?: string;
  risk_assessment?: RiskAssessment;
  created_at_from?: string;
  created_at_to?: string;
}

export interface SecurityPolicyFilters {
  tenant_id?: string;
  policy_type?: PolicyType;
  status?: PolicyStatus;
  enforcement_level?: EnforcementLevel;
}

export interface ComplianceCheckFilters {
  tenant_id?: string;
  check_type?: CheckType;
  check_frequency?: CheckFrequency;
  is_compliant?: boolean;
  next_check_date_from?: string;
  next_check_date_to?: string;
}

// ============================================================================
// SECURITY COMPLIANCE CONSTANTS
// ============================================================================

export const SECURITY_CONSTANTS = {
  // Risk scores
  RISK_SCORE_MIN: 1,
  RISK_SCORE_MAX: 10,
  
  // Compliance scores
  COMPLIANCE_SCORE_MIN: 0,
  COMPLIANCE_SCORE_MAX: 100,
  
  // Retention periods (in days)
  RETENTION_PERIODS: {
    P0_DATA: 2555, // 7 years
    P1_DATA: 1825, // 5 years
    P2_DATA: 365,  // 1 year
  },
  
  // Rotation schedules (in days)
  ROTATION_SCHEDULES: {
    STRIPE_KEYS: 90,
    SERVICE_ACCOUNTS: 180,
    API_KEYS: 365,
    DATABASE_KEYS: 90,
  },
  
  // Review frequencies (in days)
  REVIEW_FREQUENCIES: {
    QUARTERLY: 90,
    ANNUAL: 365,
    AD_HOC: 30,
  },
} as const;

// ============================================================================
// SECURITY COMPLIANCE UTILITY TYPES
// ============================================================================

export type SecurityComplianceEntity = 
  | DataClassification 
  | AccessReview 
  | KeyHolder 
  | AdminActionAudit 
  | SecurityPolicy 
  | ComplianceCheck;

export type SecurityComplianceEntityType = 
  | 'data_classification'
  | 'access_review'
  | 'key_holder'
  | 'admin_action_audit'
  | 'security_policy'
  | 'compliance_check';

export interface SecurityComplianceEntityMetadata {
  entity_type: SecurityComplianceEntityType;
  entity_id: string;
  tenant_id: string;
  created_at: string;
  updated_at: string;
}
