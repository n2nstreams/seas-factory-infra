// Security & Compliance Service for Module 11
// Comprehensive service for managing security and compliance operations

import { 
  DataClassification, 
  DataClassificationCreate, 
  DataClassificationUpdate,
  DataClassificationFilters,
  AccessReview,
  AccessReviewCreate,
  AccessReviewUpdate,
  AccessReviewFilters,
  KeyHolder,
  KeyHolderCreate,
  KeyHolderUpdate,
  KeyHolderFilters,
  AdminActionAudit,
  AdminActionAuditCreate,
  AdminActionAuditUpdate,
  AdminActionAuditFilters,
  SecurityPolicy,
  SecurityPolicyCreate,
  SecurityPolicyUpdate,
  SecurityPolicyFilters,
  ComplianceCheck,
  ComplianceCheckCreate,
  ComplianceCheckUpdate,
  ComplianceCheckFilters,
  SecurityComplianceSummary,
  SecurityComplianceApiResponse,
  SecurityComplianceListResponse,
  SECURITY_CONSTANTS
} from '@/types/security';

export class SecurityComplianceService {
  private static instance: SecurityComplianceService;
  private baseUrl: string;
  private correlationId: string;

  private constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:3000/api';
    this.correlationId = this.generateCorrelationId();
  }

  public static getInstance(): SecurityComplianceService {
    if (!SecurityComplianceService.instance) {
      SecurityComplianceService.instance = new SecurityComplianceService();
    }
    return SecurityComplianceService.instance;
  }

  private generateCorrelationId(): string {
    return `sec-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private async makeRequest<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<SecurityComplianceApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'X-Correlation-ID': this.correlationId,
      'X-Request-ID': this.generateCorrelationId(),
    };

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      return data;
    } catch (error) {
      console.error('Security compliance service error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
        correlation_id: this.correlationId,
      };
    }
  }

  // ============================================================================
  // DATA CLASSIFICATION METHODS
  // ============================================================================

  async getDataClassifications(
    filters?: DataClassificationFilters,
    page: number = 1,
    limit: number = 50
  ): Promise<SecurityComplianceListResponse<DataClassification>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(filters && Object.fromEntries(
        Object.entries(filters).filter(([_, value]) => value !== undefined)
      )),
    });

    return this.makeRequest<DataClassification[]>(`/security/data-classification?${params}`);
  }

  async getDataClassification(id: string): Promise<SecurityComplianceApiResponse<DataClassification>> {
    return this.makeRequest<DataClassification>(`/security/data-classification/${id}`);
  }

  async createDataClassification(
    data: DataClassificationCreate
  ): Promise<SecurityComplianceApiResponse<DataClassification>> {
    return this.makeRequest<DataClassification>('/security/data-classification', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateDataClassification(
    id: string,
    data: DataClassificationUpdate
  ): Promise<SecurityComplianceApiResponse<DataClassification>> {
    return this.makeRequest<DataClassification>(`/security/data-classification/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteDataClassification(id: string): Promise<SecurityComplianceApiResponse<void>> {
    return this.makeRequest<void>(`/security/data-classification/${id}`, {
      method: 'DELETE',
    });
  }

  async getDataClassificationByTable(
    tableName: string,
    tenantId: string
  ): Promise<SecurityComplianceApiResponse<DataClassification[]>> {
    return this.makeRequest<DataClassification[]>(
      `/security/data-classification/table/${tableName}?tenant_id=${tenantId}`
    );
  }

  // ============================================================================
  // ACCESS REVIEW METHODS
  // ============================================================================

  async getAccessReviews(
    filters?: AccessReviewFilters,
    page: number = 1,
    limit: number = 50
  ): Promise<SecurityComplianceListResponse<AccessReview>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(filters && Object.fromEntries(
        Object.entries(filters).filter(([_, value]) => value !== undefined)
      )),
    });

    return this.makeRequest<AccessReview[]>(`/security/access-reviews?${params}`);
  }

  async getAccessReview(id: string): Promise<SecurityComplianceApiResponse<AccessReview>> {
    return this.makeRequest<AccessReview>(`/security/access-reviews/${id}`);
  }

  async createAccessReview(
    data: AccessReviewCreate
  ): Promise<SecurityComplianceApiResponse<AccessReview>> {
    return this.makeRequest<AccessReview>('/security/access-reviews', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateAccessReview(
    id: string,
    data: AccessReviewUpdate
  ): Promise<SecurityComplianceApiResponse<AccessReview>> {
    return this.makeRequest<AccessReview>(`/security/access-reviews/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteAccessReview(id: string): Promise<SecurityComplianceApiResponse<void>> {
    return this.makeRequest<void>(`/security/access-reviews/${id}`, {
      method: 'DELETE',
    });
  }

  async getOverdueAccessReviews(tenantId: string): Promise<SecurityComplianceApiResponse<AccessReview[]>> {
    return this.makeRequest<AccessReview[]>(
      `/security/access-reviews/overdue?tenant_id=${tenantId}`
    );
  }

  async completeAccessReview(
    id: string,
    findings: string,
    riskScore: number
  ): Promise<SecurityComplianceApiResponse<AccessReview>> {
    return this.makeRequest<AccessReview>(`/security/access-reviews/${id}/complete`, {
      method: 'POST',
      body: JSON.stringify({ findings_summary: findings, risk_score: riskScore }),
    });
  }

  // ============================================================================
  // KEY HOLDER METHODS
  // ============================================================================

  async getKeyHolders(
    filters?: KeyHolderFilters,
    page: number = 1,
    limit: number = 50
  ): Promise<SecurityComplianceListResponse<KeyHolder>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(filters && Object.fromEntries(
        Object.entries(filters).filter(([_, value]) => value !== undefined)
      )),
    });

    return this.makeRequest<KeyHolder[]>(`/security/key-holders?${params}`);
  }

  async getKeyHolder(id: string): Promise<SecurityComplianceApiResponse<KeyHolder>> {
    return this.makeRequest<KeyHolder>(`/security/key-holders/${id}`);
  }

  async createKeyHolder(
    data: KeyHolderCreate
  ): Promise<SecurityComplianceApiResponse<KeyHolder>> {
    return this.makeRequest<KeyHolder>('/security/key-holders', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateKeyHolder(
    id: string,
    data: KeyHolderUpdate
  ): Promise<SecurityComplianceApiResponse<KeyHolder>> {
    return this.makeRequest<KeyHolder>(`/security/key-holders/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteKeyHolder(id: string): Promise<SecurityComplianceApiResponse<void>> {
    return this.makeRequest<void>(`/security/key-holders/${id}`, {
      method: 'DELETE',
    });
  }

  async getKeysDueRotation(tenantId: string): Promise<SecurityComplianceApiResponse<KeyHolder[]>> {
    return this.makeRequest<KeyHolder[]>(
      `/security/key-holders/due-rotation?tenant_id=${tenantId}`
    );
  }

  async rotateKey(id: string): Promise<SecurityComplianceApiResponse<KeyHolder>> {
    return this.makeRequest<KeyHolder>(`/security/key-holders/${id}/rotate`, {
      method: 'POST',
    });
  }

  async revokeKey(id: string, reason: string): Promise<SecurityComplianceApiResponse<KeyHolder>> {
    return this.makeRequest<KeyHolder>(`/security/key-holders/${id}/revoke`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    });
  }

  // ============================================================================
  // ADMIN ACTION AUDIT METHODS
  // ============================================================================

  async getAdminActionAudits(
    filters?: AdminActionAuditFilters,
    page: number = 1,
    limit: number = 50
  ): Promise<SecurityComplianceListResponse<AdminActionAudit>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(filters && Object.fromEntries(
        Object.entries(filters).filter(([_, value]) => value !== undefined)
      )),
    });

    return this.makeRequest<AdminActionAudit[]>(`/security/admin-actions?${params}`);
  }

  async getAdminActionAudit(id: string): Promise<SecurityComplianceApiResponse<AdminActionAudit>> {
    return this.makeRequest<AdminActionAudit>(`/security/admin-actions/${id}`);
  }

  async createAdminActionAudit(
    data: AdminActionAuditCreate
  ): Promise<SecurityComplianceApiResponse<AdminActionAudit>> {
    return this.makeRequest<AdminActionAudit>('/security/admin-actions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateAdminActionAudit(
    id: string,
    data: AdminActionAuditUpdate
  ): Promise<SecurityComplianceApiResponse<AdminActionAudit>> {
    return this.makeRequest<AdminActionAudit>(`/security/admin-actions/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async getPendingApprovals(tenantId: string): Promise<SecurityComplianceApiResponse<AdminActionAudit[]>> {
    return this.makeRequest<AdminActionAudit[]>(
      `/security/admin-actions/pending-approvals?tenant_id=${tenantId}`
    );
  }

  async approveAdminAction(
    id: string,
    approverId: string,
    notes?: string
  ): Promise<SecurityComplianceApiResponse<AdminActionAudit>> {
    return this.makeRequest<AdminActionAudit>(`/security/admin-actions/${id}/approve`, {
      method: 'POST',
      body: JSON.stringify({ approved_by: approverId, approval_notes: notes }),
    });
  }

  async rejectAdminAction(
    id: string,
    approverId: string,
    reason: string
  ): Promise<SecurityComplianceApiResponse<AdminActionAudit>> {
    return this.makeRequest<AdminActionAudit>(`/security/admin-actions/${id}/reject`, {
      method: 'POST',
      body: JSON.stringify({ approved_by: approverId, approval_notes: reason }),
    });
  }

  // ============================================================================
  // SECURITY POLICIES METHODS
  // ============================================================================

  async getSecurityPolicies(
    filters?: SecurityPolicyFilters,
    page: number = 1,
    limit: number = 50
  ): Promise<SecurityComplianceListResponse<SecurityPolicy>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(filters && Object.fromEntries(
        Object.entries(filters).filter(([_, value]) => value !== undefined)
      )),
    });

    return this.makeRequest<SecurityPolicy[]>(`/security/policies?${params}`);
  }

  async getSecurityPolicy(id: string): Promise<SecurityComplianceApiResponse<SecurityPolicy>> {
    return this.makeRequest<SecurityPolicy>(`/security/policies/${id}`);
  }

  async createSecurityPolicy(
    data: SecurityPolicyCreate
  ): Promise<SecurityComplianceApiResponse<SecurityPolicy>> {
    return this.makeRequest<SecurityPolicy>('/security/policies', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateSecurityPolicy(
    id: string,
    data: SecurityPolicyUpdate
  ): Promise<SecurityComplianceApiResponse<SecurityPolicy>> {
    return this.makeRequest<SecurityPolicy>(`/security/policies/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteSecurityPolicy(id: string): Promise<SecurityComplianceApiResponse<void>> {
    return this.makeRequest<void>(`/security/policies/${id}`, {
      method: 'DELETE',
    });
  }

  async getActivePolicies(tenantId: string): Promise<SecurityComplianceApiResponse<SecurityPolicy[]>> {
    return this.makeRequest<SecurityPolicy[]>(
      `/security/policies/active?tenant_id=${tenantId}`
    );
  }

  // ============================================================================
  // COMPLIANCE CHECKS METHODS
  // ============================================================================

  async getComplianceChecks(
    filters?: ComplianceCheckFilters,
    page: number = 1,
    limit: number = 50
  ): Promise<SecurityComplianceListResponse<ComplianceCheck>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(filters && Object.fromEntries(
        Object.entries(filters).filter(([_, value]) => value !== undefined)
      )),
    });

    return this.makeRequest<ComplianceCheck[]>(`/security/compliance-checks?${params}`);
  }

  async getComplianceCheck(id: string): Promise<SecurityComplianceApiResponse<ComplianceCheck>> {
    return this.makeRequest<ComplianceCheck>(`/security/compliance-checks/${id}`);
  }

  async createComplianceCheck(
    data: ComplianceCheckCreate
  ): Promise<SecurityComplianceApiResponse<ComplianceCheck>> {
    return this.makeRequest<ComplianceCheck>('/security/compliance-checks', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateComplianceCheck(
    id: string,
    data: ComplianceCheckUpdate
  ): Promise<SecurityComplianceApiResponse<ComplianceCheck>> {
    return this.makeRequest<ComplianceCheck>(`/security/compliance-checks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteComplianceCheck(id: string): Promise<SecurityComplianceApiResponse<void>> {
    return this.makeRequest<void>(`/security/compliance-checks/${id}`, {
      method: 'DELETE',
    });
  }

  async runComplianceCheck(id: string): Promise<SecurityComplianceApiResponse<ComplianceCheck>> {
    return this.makeRequest<ComplianceCheck>(`/security/compliance-checks/${id}/run`, {
      method: 'POST',
    });
  }

  async getChecksDueSoon(tenantId: string): Promise<SecurityComplianceApiResponse<ComplianceCheck[]>> {
    return this.makeRequest<ComplianceCheck[]>(
      `/security/compliance-checks/due-soon?tenant_id=${tenantId}`
    );
  }

  // ============================================================================
  // SUMMARY AND ANALYTICS METHODS
  // ============================================================================

  async getSecurityComplianceSummary(
    tenantId: string
  ): Promise<SecurityComplianceApiResponse<SecurityComplianceSummary>> {
    return this.makeRequest<SecurityComplianceSummary>(
      `/security/summary?tenant_id=${tenantId}`
    );
  }

  async getComplianceScore(tenantId: string): Promise<SecurityComplianceApiResponse<number>> {
    return this.makeRequest<number>(`/security/compliance-score?tenant_id=${tenantId}`);
  }

  async getRiskAssessment(tenantId: string): Promise<SecurityComplianceApiResponse<{
    overall_risk_score: number;
    high_risk_items: number;
    medium_risk_items: number;
    low_risk_items: number;
  }>> {
    return this.makeRequest<{
      overall_risk_score: number;
      high_risk_items: number;
      medium_risk_items: number;
      low_risk_items: number;
    }>(`/security/risk-assessment?tenant_id=${tenantId}`);
  }

  // ============================================================================
  // UTILITY METHODS
  // ============================================================================

  async exportSecurityReport(
    tenantId: string,
    format: 'pdf' | 'csv' | 'json' = 'pdf'
  ): Promise<SecurityComplianceApiResponse<{ download_url: string }>> {
    return this.makeRequest<{ download_url: string }>(
      `/security/export?tenant_id=${tenantId}&format=${format}`
    );
  }

  async sendSecurityAlert(
    tenantId: string,
    alertType: 'high_risk' | 'compliance_failure' | 'access_review_overdue',
    message: string
  ): Promise<SecurityComplianceApiResponse<void>> {
    return this.makeRequest<void>('/security/alerts', {
      method: 'POST',
      body: JSON.stringify({
        tenant_id: tenantId,
        alert_type: alertType,
        message,
      }),
    });
  }

  // ============================================================================
  // HEALTH CHECK AND MONITORING
  // ============================================================================

  async healthCheck(): Promise<SecurityComplianceApiResponse<{
    status: string;
    services: Record<string, string>;
    last_check: string;
  }>> {
    return this.makeRequest<{
      status: string;
      services: Record<string, string>;
      last_check: string;
    }>('/security/health');
  }

  async getServiceMetrics(tenantId: string): Promise<SecurityComplianceApiResponse<{
    total_entities: number;
    active_policies: number;
    compliance_score: number;
    risk_score: number;
    last_updated: string;
  }>> {
    return this.makeRequest<{
      total_entities: number;
      active_policies: number;
      compliance_score: number;
      risk_score: number;
      last_updated: string;
    }>(`/security/metrics?tenant_id=${tenantId}`);
  }

  // ============================================================================
  // BULK OPERATIONS
  // ============================================================================

  async bulkUpdateDataClassification(
    updates: Array<{ id: string; data: DataClassificationUpdate }>
  ): Promise<SecurityComplianceApiResponse<{
    success_count: number;
    failure_count: number;
    errors: Array<{ id: string; error: string }>;
  }>> {
    return this.makeRequest<{
      success_count: number;
      failure_count: number;
      errors: Array<{ id: string; error: string }>;
    }>('/security/data-classification/bulk-update', {
      method: 'POST',
      body: JSON.stringify({ updates }),
    });
  }

  async bulkCreateAccessReviews(
    reviews: AccessReviewCreate[]
  ): Promise<SecurityComplianceApiResponse<{
    success_count: number;
    failure_count: number;
    created_reviews: AccessReview[];
    errors: Array<{ index: number; error: string }>;
  }>> {
    return this.makeRequest<{
      success_count: number;
      failure_count: number;
      created_reviews: AccessReview[];
      errors: Array<{ index: number; error: string }>;
    }>('/security/access-reviews/bulk-create', {
      method: 'POST',
      body: JSON.stringify({ reviews }),
    });
  }

  // ============================================================================
  // VALIDATION AND UTILITY METHODS
  // ============================================================================

  validateRiskScore(score: number): boolean {
    return score >= SECURITY_CONSTANTS.RISK_SCORE_MIN && 
           score <= SECURITY_CONSTANTS.RISK_SCORE_MAX;
  }

  validateComplianceScore(score: number): boolean {
    return score >= SECURITY_CONSTANTS.COMPLIANCE_SCORE_MIN && 
           score <= SECURITY_CONSTANTS.COMPLIANCE_SCORE_MAX;
  }

  calculateNextRotationDate(currentDate: Date, rotationDays: number): Date {
    const nextRotation = new Date(currentDate);
    nextRotation.setDate(nextRotation.getDate() + rotationDays);
    return nextRotation;
  }

  isKeyDueForRotation(key: KeyHolder): boolean {
    if (!key.next_rotation_date) return false;
    const nextRotation = new Date(key.next_rotation_date);
    const today = new Date();
    return today >= nextRotation;
  }

  isAccessReviewOverdue(review: AccessReview): boolean {
    const dueDate = new Date(review.due_date);
    const today = new Date();
    return today > dueDate && review.status !== 'completed';
  }

  getCorrelationId(): string {
    return this.correlationId;
  }

  generateNewCorrelationId(): string {
    this.correlationId = this.generateCorrelationId();
    return this.correlationId;
  }
}

// Export singleton instance
export const securityComplianceService = SecurityComplianceService.getInstance();
