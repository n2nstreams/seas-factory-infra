// Simple Health Monitoring System
// This version provides basic health checks without external dependencies

export interface HealthCheckConfig {
  name: string
  endpoint: string
  timeout: number
  expectedStatus?: number
  critical: boolean
  retries: number
}

export interface HealthCheckResult {
  status: 'pass' | 'fail' | 'warn'
  responseTime?: number
  error?: string
  details?: any
}

export interface HealthIndexMetrics {
  timestamp: string
  errorRate: number
  responseTime: number
  uptime: number
  jobFailures: number
  authFailures: number
  webhookFailures: number
  overallScore: number
}

export interface HealthSummary {
  totalChecks: number
  passedChecks: number
  failedChecks: number
  warningChecks: number
  overallHealth: number
}

export interface HealthResult {
  status: 'healthy' | 'degraded' | 'unhealthy'
  timestamp: string
  checks: { [key: string]: HealthCheckResult }
  summary: HealthSummary
}

// Default health check configuration
const DEFAULT_HEALTH_CHECKS: HealthCheckConfig[] = [
  {
    name: 'system',
    endpoint: 'internal', // Special case for system checks
    timeout: 5000,
    critical: false,
    retries: 2,
  },
  {
    name: 'backend-api',
    endpoint: process.env.NEXT_PUBLIC_HEALTH_API_URL || 'http://localhost:8000/health',
    timeout: 5000,
    expectedStatus: 200,
    critical: true,
    retries: 3,
  },
]

class SimpleHealthMonitoringService {
  private healthHistory: HealthResult[] = []
  private metricsHistory: HealthIndexMetrics[] = []

  // Run comprehensive health check
  async runHealthCheck(): Promise<HealthResult> {
    const startTime = Date.now()
    const checks: { [key: string]: HealthCheckResult } = {}
    let totalChecks = 0
    let passedChecks = 0
    let failedChecks = 0
    let warningChecks = 0

    // Run all health checks in parallel
    const checkPromises = DEFAULT_HEALTH_CHECKS.map(async (config) => {
      const checkStartTime = Date.now()
      let retryCount = 0
      let lastError: string | undefined

      while (retryCount < config.retries) {
        try {
          const result = await this.performHealthCheck(config)
          const responseTime = Date.now() - checkStartTime
          
          checks[config.name] = {
            ...result,
            responseTime,
          }

          if (result.status === 'pass') {
            passedChecks++
          } else if (result.status === 'warn') {
            warningChecks++
          } else {
            failedChecks++
          }

          break // Success, no need to retry
        } catch (error) {
          lastError = error instanceof Error ? error.message : String(error)
          retryCount++
          
          if (retryCount >= config.retries) {
            checks[config.name] = {
              status: 'fail',
              error: lastError,
            }
            failedChecks++
          } else {
            // Wait before retry
            await new Promise(resolve => setTimeout(resolve, 1000 * retryCount))
          }
        }
      }
    })

    await Promise.all(checkPromises)

    totalChecks = Object.keys(checks).length
    const overallHealth = totalChecks > 0 ? (passedChecks / totalChecks) * 100 : 0

    const healthResult: HealthResult = {
      status: this.determineOverallStatus(overallHealth, failedChecks),
      timestamp: new Date().toISOString(),
      checks,
      summary: {
        totalChecks,
        passedChecks,
        failedChecks,
        warningChecks,
        overallHealth: Math.round(overallHealth),
      },
    }

    // Store in history
    this.healthHistory.push(healthResult)
    if (this.healthHistory.length > 100) {
      this.healthHistory = this.healthHistory.slice(-100)
    }

    // Calculate and store health index metrics
    await this.calculateHealthIndexMetrics(healthResult)

    console.log('Health check completed:', healthResult.summary)
    return healthResult
  }

  // Perform individual health check
  private async performHealthCheck(config: HealthCheckConfig): Promise<HealthCheckResult> {
    if (config.endpoint === 'internal') {
      return this.performInternalHealthCheck(config)
    }

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), config.timeout)

    try {
      const response = await fetch(config.endpoint, {
        method: 'GET',
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
        },
      })

      clearTimeout(timeoutId)

      if (response.ok) {
        const data = await response.json()
        return {
          status: 'pass',
          details: data,
        }
      } else if (response.status >= 500) {
        return {
          status: 'fail',
          details: { status: response.status, statusText: response.statusText },
        }
      } else {
        return {
          status: 'warn',
          details: { status: response.status, statusText: response.statusText },
        }
      }
    } catch (error) {
      clearTimeout(timeoutId)
      
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error(`Health check timeout after ${config.timeout}ms`)
      }
      
      throw error
    }
  }

  // Perform internal health checks
  private async performInternalHealthCheck(config: HealthCheckConfig): Promise<HealthCheckResult> {
    try {
      switch (config.name) {
        case 'system':
          // Basic system health check that doesn't require external services
          return {
            status: 'pass',
            details: { 
              uptime: process.uptime(),
              memory: process.memoryUsage(),
              nodeVersion: process.version,
              platform: process.platform,
              timestamp: new Date().toISOString()
            },
          }

        default:
          return {
            status: 'warn',
            details: { error: 'Unknown internal health check' },
          }
      }
    } catch (error) {
      return {
        status: 'warn',
        details: { 
          error: error instanceof Error ? error.message : String(error),
          message: 'Internal health check failed'
        },
      }
    }
  }

  // Determine overall health status
  private determineOverallStatus(overallHealth: number, failedChecks: number): 'healthy' | 'degraded' | 'unhealthy' {
    if (overallHealth >= 90 && failedChecks === 0) {
      return 'healthy'
    } else if (overallHealth >= 70 && failedChecks <= 1) {
      return 'degraded'
    } else {
      return 'unhealthy'
    }
  }

  // Calculate health index metrics
  private async calculateHealthIndexMetrics(healthResult: HealthResult): Promise<void> {
    const now = new Date()
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000)
    
    // Get recent health checks for metrics calculation
    const recentChecks = this.healthHistory.filter(
      check => new Date(check.timestamp) >= oneHourAgo
    )

    if (recentChecks.length === 0) return

    // Calculate error rate
    const totalChecks = recentChecks.reduce((sum, check) => sum + check.summary.totalChecks, 0)
    const totalFailures = recentChecks.reduce((sum, check) => sum + check.summary.failedChecks, 0)
    const errorRate = totalChecks > 0 ? totalFailures / totalChecks : 0

    // Calculate average response time
    const responseTimes = recentChecks.flatMap(check => 
      Object.values(check.checks)
        .map(c => c.responseTime)
        .filter((rt): rt is number => rt !== undefined)
    )
    const avgResponseTime = responseTimes.length > 0 
      ? responseTimes.reduce((sum, rt) => sum + rt, 0) / responseTimes.length 
      : 0

    // Calculate uptime (simplified - just check if we have recent health checks)
    const uptime = recentChecks.length > 0 ? 1.0 : 0.0

    // Create metrics entry
    const metrics: HealthIndexMetrics = {
      timestamp: now.toISOString(),
      errorRate: errorRate * 100, // Convert to percentage
      responseTime: avgResponseTime,
      uptime: uptime * 100, // Convert to percentage
      jobFailures: 0, // Placeholder
      authFailures: 0, // Placeholder
      webhookFailures: 0, // Placeholder
      overallScore: healthResult.summary.overallHealth,
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

  // Start monitoring (placeholder for future implementation)
  async startMonitoring(intervalMs: number = 30000): Promise<void> {
    console.log(`Health monitoring started with ${intervalMs}ms interval`)
  }

  // Stop monitoring (placeholder for future implementation)
  stopMonitoring(): void {
    console.log('Health monitoring stopped')
  }
}

// Export singleton instance
export const healthMonitoring = new SimpleHealthMonitoringService()

// Export types for external use
export type { HealthCheckConfig, HealthCheckResult, HealthIndexMetrics, HealthSummary, HealthResult }
