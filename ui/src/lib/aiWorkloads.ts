/**
 * AI Workloads Service - Module 9 Implementation
 * 
 * Implements constrained AI workload management with:
 * - Cost guards and monitoring
 * - Request envelope and timeout policy
 * - Allowlist of permitted AI actions
 * - Fallback to legacy orchestrator
 */

export interface AIWorkloadRequest {
  org_id: string
  user_id: string
  purpose: string
  sensitivity_tag: 'public' | 'internal' | 'confidential'
  action_type: string
  payload: any
  correlation_id?: string
}

export interface AIWorkloadResponse {
  success: boolean
  result?: any
  error?: string
  cost_estimate?: number
  processing_time?: number
  fallback_used?: boolean
  correlation_id: string
}

export interface AIWorkloadConfig {
  max_latency_ms: number
  max_cost_usd: number
  max_tokens: number
  allowed_actions: string[]
  cost_per_token: number
  fallback_enabled: boolean
}

export class AIWorkloadsService {
  private config: AIWorkloadConfig
  private costTracker: Map<string, number> = new Map()
  private requestCount: Map<string, number> = new Map()
  private fallbackCount = 0

  constructor(config?: Partial<AIWorkloadConfig>) {
    this.config = {
      max_latency_ms: 10000, // 10 seconds p95 target
      max_cost_usd: 0.50, // $0.50 per request max
      max_tokens: 4000, // 4k tokens max per request
      allowed_actions: [
        'idea_validation',
        'tech_stack_recommendation',
        'design_generation',
        'code_review',
        'qa_test_generation',
        'documentation_generation'
      ],
      cost_per_token: 0.00001, // $0.00001 per token (approximate)
      fallback_enabled: true,
      ...config
    }
  }

  /**
   * Process AI workload request with constraints
   */
  async processRequest(request: AIWorkloadRequest): Promise<AIWorkloadResponse> {
    const startTime = Date.now()
    const correlationId = request.correlation_id || this.generateCorrelationId()
    
    try {
      // Validate request
      const validation = this.validateRequest(request)
      if (!validation.valid) {
        return {
          success: false,
          error: validation.error,
          correlation_id: correlationId
        }
      }

      // Check cost limits
      const costCheck = this.checkCostLimits(request.org_id, request.user_id)
      if (!costCheck.allowed) {
        return {
          success: false,
          error: `Cost limit exceeded: ${costCheck.reason}`,
          correlation_id: correlationId
        }
      }

      // Check if action is allowed
      if (!this.config.allowed_actions.includes(request.action_type)) {
        return {
          success: false,
          error: `Action type '${request.action_type}' not in allowlist`,
          correlation_id: correlationId
        }
      }

      // Estimate cost
      const estimatedCost = this.estimateCost(request.payload)
      if (estimatedCost > this.config.max_cost_usd) {
        return {
          success: false,
          error: `Estimated cost $${estimatedCost.toFixed(4)} exceeds limit $${this.config.max_cost_usd}`,
          correlation_id: correlationId
        }
      }

      // Process with timeout
      const result = await this.processWithTimeout(request, startTime)
      
      // Update tracking
      this.updateTracking(request.org_id, request.user_id, estimatedCost)
      
      const processingTime = Date.now() - startTime
      
      return {
        success: true,
        result,
        cost_estimate: estimatedCost,
        processing_time: processingTime,
        correlation_id: correlationId
      }

    } catch (error) {
      // Fallback to legacy orchestrator if enabled
      if (this.config.fallback_enabled) {
        return await this.fallbackToLegacy(request, correlationId, startTime)
      }
      
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        correlation_id: correlationId
      }
    }
  }

  /**
   * Validate request format and content
   */
  private validateRequest(request: AIWorkloadRequest): { valid: boolean; error?: string } {
    if (!request.org_id || !request.user_id || !request.purpose || !request.action_type) {
      return { valid: false, error: 'Missing required fields: org_id, user_id, purpose, action_type' }
    }

    if (!['public', 'internal', 'confidential'].includes(request.sensitivity_tag)) {
      return { valid: false, error: 'Invalid sensitivity_tag' }
    }

    if (this.estimateTokens(request.payload) > this.config.max_tokens) {
      return { valid: false, error: `Payload too large: ${this.estimateTokens(request.payload)} tokens exceeds ${this.config.max_tokens}` }
    }

    return { valid: true }
  }

  /**
   * Check cost limits for organization and user
   */
  private checkCostLimits(orgId: string, userId: string): { allowed: boolean; reason?: string } {
    const orgCost = this.costTracker.get(orgId) || 0
    const userCost = this.costTracker.get(userId) || 0
    
    if (orgCost > this.config.max_cost_usd * 10) { // 10x per org
      return { allowed: false, reason: 'Organization cost limit exceeded' }
    }
    
    if (userCost > this.config.max_cost_usd * 5) { // 5x per user
      return { allowed: false, reason: 'User cost limit exceeded' }
    }
    
    return { allowed: true }
  }

  /**
   * Estimate cost based on payload size
   */
  private estimateCost(payload: any): number {
    const tokens = this.estimateTokens(payload)
    return tokens * this.config.cost_per_token
  }

  /**
   * Estimate token count (simplified)
   */
  private estimateTokens(payload: any): number {
    const text = JSON.stringify(payload)
    return Math.ceil(text.length / 4) // Rough estimate: 4 chars per token
  }

  /**
   * Process request with timeout constraint
   */
  private async processWithTimeout(request: AIWorkloadRequest, startTime: number): Promise<any> {
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Request timeout')), this.config.max_latency_ms)
    })

    const processPromise = this.processAIRequest(request)
    
    return Promise.race([processPromise, timeoutPromise])
  }

  /**
   * Process AI request (placeholder for actual AI processing)
   */
  private async processAIRequest(request: AIWorkloadRequest): Promise<any> {
    // Simulate AI processing time
    const processingTime = Math.random() * 5000 + 1000 // 1-6 seconds
    
    await new Promise(resolve => setTimeout(resolve, processingTime))
    
    // Simulate different results based on action type
    switch (request.action_type) {
      case 'idea_validation':
        return {
          validation_score: Math.random() * 100,
          market_potential: Math.random() > 0.5 ? 'high' : 'medium',
          technical_feasibility: Math.random() > 0.3 ? 'feasible' : 'challenging'
        }
      
      case 'tech_stack_recommendation':
        return {
          recommended_stack: ['Next.js', 'Supabase', 'TypeScript'],
          reasoning: 'Modern, scalable, and developer-friendly',
          complexity: 'medium'
        }
      
      case 'design_generation':
        return {
          design_type: 'glassmorphism',
          color_scheme: 'natural olive greens',
          components: ['navigation', 'dashboard', 'forms']
        }
      
      default:
        return { message: 'AI processing completed', action: request.action_type }
    }
  }

  /**
   * Fallback to legacy orchestrator
   */
  private async fallbackToLegacy(request: AIWorkloadRequest, correlationId: string, startTime: number): Promise<AIWorkloadResponse> {
    this.fallbackCount++
    
    try {
      // Call legacy orchestrator
      const legacyResponse = await this.callLegacyOrchestrator(request)
      
      const processingTime = Date.now() - startTime
      
      return {
        success: true,
        result: legacyResponse,
        processing_time: processingTime,
        fallback_used: true,
        correlation_id: correlationId
      }
    } catch (error) {
      return {
        success: false,
        error: `Legacy fallback failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        correlation_id: correlationId
      }
    }
  }

  /**
   * Call legacy orchestrator (placeholder)
   */
  private async callLegacyOrchestrator(request: AIWorkloadRequest): Promise<any> {
    // Simulate legacy orchestrator call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    return {
      legacy_processed: true,
      action: request.action_type,
      timestamp: new Date().toISOString()
    }
  }

  /**
   * Update cost and request tracking
   */
  private updateTracking(orgId: string, userId: string, cost: number): void {
    const orgCost = this.costTracker.get(orgId) || 0
    const userCost = this.costTracker.get(userId) || 0
    
    this.costTracker.set(orgId, orgCost + cost)
    this.costTracker.set(userId, userCost + cost)
    
    // Track request counts
    const orgRequests = this.requestCount.get(orgId) || 0
    const userRequests = this.requestCount.get(userId) || 0
    
    this.requestCount.set(orgId, orgRequests + 1)
    this.requestCount.set(userId, userRequests + 1)
  }

  /**
   * Generate correlation ID for request tracking
   */
  private generateCorrelationId(): string {
    return `ai-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  /**
   * Get service statistics
   */
  getStats() {
    return {
      total_requests: Array.from(this.requestCount.values()).reduce((a, b) => a + b, 0),
      total_cost: Array.from(this.costTracker.values()).reduce((a, b) => a + b, 0),
      fallback_count: this.fallbackCount,
      org_count: this.costTracker.size,
      user_count: this.requestCount.size,
      config: this.config
    }
  }

  /**
   * Reset cost tracking (for testing/admin)
   */
  resetTracking(): void {
    this.costTracker.clear()
    this.requestCount.clear()
    this.fallbackCount = 0
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig: Partial<AIWorkloadConfig>): void {
    this.config = { ...this.config, ...newConfig }
  }
}

// Global instance
export const aiWorkloadsService = new AIWorkloadsService()
