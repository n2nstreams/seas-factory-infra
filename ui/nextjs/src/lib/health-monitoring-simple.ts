import { correlationIDManager, getCorrelationHeaders } from './correlation-id'

// Health check configuration interface
export interface HealthCheckConfig {
  name: string
  endpoint: string
  timeout: number
  expectedStatus?: number
  critical: boolean
  retries: number
  headers?: Record<string, string>
  method?: 'GET' | 'HEAD' // Added method for backend checks
}

// Health check result interface
export interface HealthCheckResult {
  status: 'pass' | 'warn' | 'fail'
  responseTime: number
  error?: string
  details?: any
  timestamp: string
  correlationId?: string
}

// Health index metrics interface
export interface HealthIndexMetrics {
  overallScore: number
  errorRate: number
  responseTime: number
  uptime: number
  lastCheck: string
}

// Health summary interface
export interface HealthSummary {
  overallHealth: number
  totalChecks: number
  passedChecks: number
  failedChecks: number
  warningChecks: number
  averageResponseTime: number
}

// Health result interface
export interface HealthResult {
  status: 'healthy' | 'degraded' | 'unhealthy'
  timestamp: string
  checks: Record<string, HealthCheckResult>
  summary: HealthSummary
  metadata: {
    service: string
    region: string
    instance: string
    build: string
    commit: string
    correlationId?: string
  }
}

// Default health check configurations
const DEFAULT_HEALTH_CHECKS: HealthCheckConfig[] = [
  {
    name: 'system',
    endpoint: 'internal', // Special case for system checks
    timeout: 5000,
    critical: false,
    retries: 2,
  },
  // Remove frontend self-check to avoid circular dependency
  // The frontend health is determined by the overall API response
  {
    name: 'backend-api',
    endpoint: process.env.NEXT_PUBLIC_HEALTH_API_URL || 'http://localhost:8000/health',
    timeout: 5000,
    expectedStatus: 200,
    critical: true,
    retries: 3,
    method: 'GET', // Use GET instead of HEAD for backend
  },
]

// Health monitoring service
class HealthMonitoringService {
  private healthHistory: HealthResult[] = []
  private metricsHistory: HealthIndexMetrics[] = []
  private isMonitoring: boolean = false
  private monitoringInterval: NodeJS.Timeout | null = null

  // Run a single health check
  async runHealthCheck(config: HealthCheckConfig): Promise<HealthCheckResult> {
    const startTime = Date.now()
    const correlationId = correlationIDManager.getCurrentContext()?.correlationId

    try {
      let result: HealthCheckResult

      if (config.endpoint === 'internal') {
        // Internal system check
        result = await this.runInternalHealthCheck(config)
      } else {
        // External endpoint check
        result = await this.runExternalHealthCheck(config)
      }

      // Add correlation ID to result
      if (correlationId) {
        result.correlationId = correlationId
      }

      return result
    } catch (error) {
      const responseTime = Date.now() - startTime
      return {
        status: 'fail',
        responseTime,
        error: error instanceof Error ? error.message : String(error),
        timestamp: new Date().toISOString(),
        correlationId
      }
    }
  }

  // Run internal health check
  private async runInternalHealthCheck(config: HealthCheckConfig): Promise<HealthCheckResult> {
    const startTime = Date.now()
    
    try {
      // Check system resources
      const systemInfo = await this.getSystemInfo()
      
      const responseTime = Date.now() - startTime
      
      return {
        status: 'pass',
        responseTime,
        details: systemInfo,
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      const responseTime = Date.now() - startTime
      return {
        status: 'fail',
        responseTime,
        error: error instanceof Error ? error.message : String(error),
        timestamp: new Date().toISOString()
      }
    }
  }

  // Run external health check
  private async runExternalHealthCheck(config: HealthCheckConfig): Promise<HealthCheckResult> {
    const startTime = Date.now()
    let lastError: Error | null = null

    // Try with retries
    for (let attempt = 1; attempt <= config.retries; attempt++) {
      try {
        const headers = {
          ...getCorrelationHeaders(),
          ...config.headers,
          'User-Agent': 'Health-Monitor/1.0'
        }

        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), config.timeout)

        const response = await fetch(config.endpoint, {
          method: config.method || 'HEAD', // Use method from config or default to HEAD
          headers,
          signal: controller.signal
        })

        clearTimeout(timeoutId)

        const responseTime = Date.now() - startTime

        if (config.expectedStatus && response.status !== config.expectedStatus) {
          throw new Error(`Expected status ${config.expectedStatus}, got ${response.status}`)
        }

        return {
          status: response.status < 400 ? 'pass' : response.status < 500 ? 'warn' : 'fail',
          responseTime,
          details: {
            status: response.status,
            statusText: response.statusText,
            headers: Object.fromEntries(response.headers.entries())
          },
          timestamp: new Date().toISOString()
        }
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error))
        
        // If this is the last attempt, throw the error
        if (attempt === config.retries) {
          break
        }

        // Wait before retry (exponential backoff)
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 100))
      }
    }

    const responseTime = Date.now() - startTime
    throw lastError || new Error('Health check failed after all retries')
  }

  // Get system information
  private async getSystemInfo(): Promise<any> {
    if (typeof window === 'undefined') {
      // Server-side
      return {
        platform: 'server',
        timestamp: new Date().toISOString()
      }
    }

    // Client-side
    return {
      platform: 'browser',
      userAgent: navigator.userAgent,
      language: navigator.language,
      cookieEnabled: navigator.cookieEnabled,
      onLine: navigator.onLine,
      timestamp: new Date().toISOString()
    }
  }

  // Run comprehensive health check
  async runComprehensiveHealthCheck(): Promise<HealthResult> {
    const startTime = Date.now()
    const correlationId = correlationIDManager.getCurrentContext()?.correlationId

    // Generate correlation context for this health check
    const healthCheckContext = correlationIDManager.generateContext(
      correlationId,
      undefined,
      undefined,
      undefined,
      { operation: 'health_check', type: 'comprehensive' }
    )

    try {
      const checkResults: Record<string, HealthCheckResult> = {}
      const checkPromises = DEFAULT_HEALTH_CHECKS.map(async (config) => {
        const result = await this.runHealthCheck(config)
        checkResults[config.name] = result
        return result
      })

      await Promise.allSettled(checkPromises)

      // Calculate summary
      const summary = this.calculateHealthSummary(checkResults)
      
      // Determine overall status
      let status: 'healthy' | 'degraded' | 'unhealthy' = 'healthy'
      if (summary.failedChecks > 0) {
        status = 'unhealthy'
      } else if (summary.warningChecks > 0 || summary.overallHealth < 90) {
        status = 'degraded'
      }

      const result: HealthResult = {
        status,
        timestamp: new Date().toISOString(),
        checks: checkResults,
        summary,
        metadata: {
          service: 'AI SaaS Factory - Next.js Frontend',
          region: 'local',
          instance: 'localhost',
          build: 'local',
          commit: 'local',
          correlationId: healthCheckContext.correlationId
        }
      }

      // Add to history
      this.healthHistory.push(result)
      if (this.healthHistory.length > 100) {
        this.healthHistory = this.healthHistory.slice(-100)
      }

      // Update metrics
      this.updateMetrics(result)

      // Log correlation context
      correlationIDManager.logContext(healthCheckContext, 'info')

      return result
    } catch (error) {
      const responseTime = Date.now() - startTime
      
      // Create error result
      const errorResult: HealthResult = {
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        checks: {},
        summary: {
          overallHealth: 0,
          totalChecks: 0,
          passedChecks: 0,
          failedChecks: 1,
          warningChecks: 0,
          averageResponseTime: responseTime
        },
        metadata: {
          service: 'AI SaaS Factory - Next.js Frontend',
          region: 'local',
          instance: 'localhost',
          build: 'local',
          commit: 'local',
          correlationId: healthCheckContext.correlationId
        }
      }

      // Log error with correlation context
      correlationIDManager.logContext(healthCheckContext, 'error')
      
      return errorResult
    } finally {
      // Clear the health check context
      correlationIDManager.clearCurrentContext()
    }
  }

  // Calculate health summary
  private calculateHealthSummary(checks: Record<string, HealthCheckResult>): HealthSummary {
    const checkArray = Object.values(checks)
    const totalChecks = checkArray.length
    const passedChecks = checkArray.filter(c => c.status === 'pass').length
    const failedChecks = checkArray.filter(c => c.status === 'fail').length
    const warningChecks = checkArray.filter(c => c.status === 'warn').length

    const overallHealth = totalChecks > 0 ? (passedChecks / totalChecks) * 100 : 0
    const averageResponseTime = checkArray.length > 0 
      ? checkArray.reduce((sum, c) => sum + c.responseTime, 0) / checkArray.length 
      : 0

    return {
      overallHealth: Math.round(overallHealth),
      totalChecks,
      passedChecks,
      failedChecks,
      warningChecks,
      averageResponseTime: Math.round(averageResponseTime)
    }
  }

  // Update metrics history
  private updateMetrics(healthResult: HealthResult): void {
    const metrics: HealthIndexMetrics = {
      overallScore: healthResult.summary.overallHealth,
      errorRate: healthResult.summary.failedChecks / healthResult.summary.totalChecks,
      responseTime: healthResult.summary.averageResponseTime,
      uptime: healthResult.status === 'healthy' ? 100 : healthResult.status === 'degraded' ? 75 : 0,
      lastCheck: healthResult.timestamp
    }

    this.metricsHistory.push(metrics)
    if (this.metricsHistory.length > 1000) {
      this.metricsHistory = this.metricsHistory.slice(-1000)
    }
  }

  // Get health history
  getHealthHistory(): HealthResult[] {
    return [...this.healthHistory]
  }

  // Get metrics history
  getMetricsHistory(): HealthIndexMetrics[] {
    return [...this.metricsHistory]
  }

  // Start monitoring
  startMonitoring(intervalMs: number = 30000): void {
    if (this.isMonitoring) return

    this.isMonitoring = true
    this.monitoringInterval = setInterval(async () => {
      try {
        await this.runComprehensiveHealthCheck()
      } catch (error) {
        console.error('Health monitoring error:', error)
      }
    }, intervalMs)

    console.log('Health monitoring started with interval:', intervalMs, 'ms')
  }

  // Stop monitoring
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval)
      this.monitoringInterval = null
    }
    this.isMonitoring = false
    console.log('Health monitoring stopped')
  }

  // Get current health
  getCurrentHealth(): HealthResult | null {
    return this.healthHistory.length > 0 ? this.healthHistory[this.healthHistory.length - 1] : null
  }

  // Check if monitoring is active
  isMonitoringActive(): boolean {
    return this.isMonitoring
  }

  // Get monitoring status
  getMonitoringStatus(): { isActive: boolean; interval: number | null } {
    return {
      isActive: this.isMonitoring,
      interval: this.monitoringInterval ? 30000 : null
    }
  }
}

// Export singleton instance
export const healthMonitoring = new HealthMonitoringService()

// Export types
export type {
  HealthCheckConfig,
  HealthCheckResult,
  HealthIndexMetrics,
  HealthSummary,
  HealthResult
}
