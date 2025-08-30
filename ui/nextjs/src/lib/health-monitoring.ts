import { supabase } from './supabase'

// Health check result interface
export interface HealthCheckResult {
  status: 'healthy' | 'degraded' | 'unhealthy'
  timestamp: string
  checks: {
    [key: string]: {
      status: 'pass' | 'fail' | 'warn'
      responseTime?: number
      error?: string
      details?: any
    }
  }
  summary: {
    totalChecks: number
    passedChecks: number
    failedChecks: number
    warningChecks: number
    overallHealth: number // 0-100 percentage
  }
}

// Health check configuration
export interface HealthCheckConfig {
  name: string
  endpoint: string
  timeout: number
  expectedStatus?: number
  critical: boolean
  retries: number
}

// Health index metrics
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
    name: 'frontend',
    endpoint: '/api/health',
    timeout: 5000,
    expectedStatus: 200,
    critical: true,
    retries: 3,
  },
  {
    name: 'backend-api',
    endpoint: process.env.NEXT_PUBLIC_HEALTH_API_URL || 'http://localhost:8000/health',
    timeout: 5000,
    expectedStatus: 200,
    critical: true,
    retries: 3,
  },
  {
    name: 'supabase-database',
    endpoint: 'internal', // Special case for Supabase
    timeout: 5000,
    critical: false,
    retries: 2,
  },
  {
    name: 'supabase-auth',
    endpoint: 'internal', // Special case for Supabase
    timeout: 5000,
    critical: false,
    retries: 2,
  },
  {
    name: 'supabase-storage',
    endpoint: 'internal', // Special case for Supabase
    timeout: 5000,
    critical: false,
    retries: 2,
  },
]

class HealthMonitoringService {
  private healthHistory: HealthCheckResult[] = []
  private metricsHistory: HealthIndexMetrics[] = []
  private isMonitoring = false
  private monitoringInterval: NodeJS.Timeout | null = null

  // Start health monitoring
  async startMonitoring(intervalMs: number = 30000): Promise<void> {
    if (this.isMonitoring) {
      console.warn('Health monitoring is already running')
      return
    }

    this.isMonitoring = true
    console.log('Starting health monitoring with interval:', intervalMs, 'ms')

    // Run initial health check
    await this.runHealthCheck()

    // Set up periodic monitoring
    this.monitoringInterval = setInterval(async () => {
      await this.runHealthCheck()
    }, intervalMs)
  }

  // Stop health monitoring
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval)
      this.monitoringInterval = null
    }
    this.isMonitoring = false
    console.log('Health monitoring stopped')
  }

  // Run comprehensive health check
  async runHealthCheck(): Promise<HealthCheckResult> {
    const startTime = Date.now()
    const checks: HealthCheckResult['checks'] = {}
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
            status: result.status,
            responseTime,
            details: result.details,
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

    const healthResult: HealthCheckResult = {
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
  private async performHealthCheck(config: HealthCheckConfig): Promise<{ status: 'pass' | 'fail' | 'warn'; details?: any }> {
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

  // Perform internal health checks (Supabase services)
  private async performInternalHealthCheck(config: HealthCheckConfig): Promise<{ status: 'pass' | 'fail' | 'warn'; details?: any }> {
    try {
      switch (config.name) {
        case 'system':
          // System health check (e.g., uptime, memory, CPU)
          // This is a placeholder and would require actual system monitoring
          return {
            status: 'pass',
            details: { message: 'System health check passed (placeholder)' },
          }

        case 'supabase-database':
          const { data: dbData, error: dbError } = await supabase
            .from('health_check')
            .select('*')
            .limit(1)
          
          if (dbError) {
            return {
              status: 'fail',
              details: { error: dbError.message },
            }
          }
          
          return {
            status: 'pass',
            details: { connected: true, data: dbData },
          }

        case 'supabase-auth':
          const { data: authData, error: authError } = await supabase.auth.getSession()
          
          if (authError) {
            return {
              status: 'warn',
              details: { error: authError.message },
            }
          }
          
          return {
            status: 'pass',
            details: { connected: true, session: !!authData.session },
          }

        case 'supabase-storage':
          // Test storage access by listing buckets
          const { data: storageData, error: storageError } = await supabase.storage.listBuckets()
          
          if (storageError) {
            return {
              status: 'warn',
              details: { error: storageError.message },
            }
          }
          
          return {
            status: 'pass',
            details: { connected: true, buckets: storageData?.length || 0 },
          }

        default:
          return {
            status: 'fail',
            details: { error: 'Unknown internal health check' },
          }
      }
    } catch (error) {
      return {
        status: 'fail',
        details: { error: error instanceof Error ? error.message : String(error) },
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
  private async calculateHealthIndexMetrics(healthResult: HealthCheckResult): Promise<void> {
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

    // Calculate uptime percentage
    const healthyChecks = recentChecks.filter(check => check.status === 'healthy').length
    const uptime = recentChecks.length > 0 ? healthyChecks / recentChecks.length : 1

    // Calculate job failures (placeholder - would integrate with actual job monitoring)
    const jobFailures = 0 // TODO: Integrate with job monitoring system

    // Calculate auth failures (placeholder - would integrate with auth monitoring)
    const authFailures = 0 // TODO: Integrate with auth monitoring system

    // Calculate webhook failures (placeholder - would integrate with webhook monitoring)
    const webhookFailures = 0 // TODO: Integrate with webhook monitoring system

    // Calculate overall score (weighted average)
    const overallScore = Math.round(
      (1 - errorRate) * 0.3 +
      (1 - avgResponseTime / 5000) * 0.2 +
      uptime * 0.3 +
      (1 - (jobFailures + authFailures + webhookFailures) / 100) * 0.2
    ) * 100

    const metrics: HealthIndexMetrics = {
      timestamp: now.toISOString(),
      errorRate,
      responseTime: avgResponseTime,
      uptime,
      jobFailures,
      authFailures,
      webhookFailures,
      overallScore: Math.max(0, Math.min(100, overallScore)),
    }

    this.metricsHistory.push(metrics)
    if (this.metricsHistory.length > 1000) {
      this.metricsHistory = this.metricsHistory.slice(-1000)
    }

    // Store metrics in Supabase for historical analysis
    try {
      await supabase
        .from('health_metrics')
        .insert([metrics])
    } catch (error) {
      console.warn('Failed to store health metrics:', error)
    }
  }

  // Get current health status
  getCurrentHealth(): HealthCheckResult | null {
    return this.healthHistory.length > 0 ? this.healthHistory[this.healthHistory.length - 1] : null
  }

  // Get health history
  getHealthHistory(limit: number = 50): HealthCheckResult[] {
    return this.healthHistory.slice(-limit)
  }

  // Get metrics history
  getMetricsHistory(limit: number = 100): HealthIndexMetrics[] {
    return this.metricsHistory.slice(-limit)
  }

  // Get health trend (last N checks)
  getHealthTrend(checks: number = 10): { trend: 'improving' | 'stable' | 'declining'; change: number } {
    if (this.healthHistory.length < checks) {
      return { trend: 'stable', change: 0 }
    }

    const recent = this.healthHistory.slice(-checks)
    const firstHalf = recent.slice(0, Math.floor(checks / 2))
    const secondHalf = recent.slice(Math.floor(checks / 2))

    const firstAvg = firstHalf.reduce((sum, check) => sum + check.summary.overallHealth, 0) / firstHalf.length
    const secondAvg = secondHalf.reduce((sum, check) => sum + check.summary.overallHealth, 0) / secondHalf.length

    const change = secondAvg - firstAvg

    if (change > 5) return { trend: 'improving', change }
    if (change < -5) return { trend: 'declining', change }
    return { trend: 'stable', change }
  }

  // Check if monitoring is active
  isMonitoringActive(): boolean {
    return this.isMonitoring
  }

  // Get monitoring statistics
  getMonitoringStats(): {
    totalChecks: number
    averageHealth: number
    uptime: number
    lastCheck: string | null
  } {
    if (this.healthHistory.length === 0) {
      return {
        totalChecks: 0,
        averageHealth: 0,
        uptime: 0,
        lastCheck: null,
      }
    }

    const totalChecks = this.healthHistory.length
    const averageHealth = this.healthHistory.reduce((sum, check) => sum + check.summary.overallHealth, 0) / totalChecks
    const healthyChecks = this.healthHistory.filter(check => check.status === 'healthy').length
    const uptime = healthyChecks / totalChecks
    const lastCheck = this.healthHistory[this.healthHistory.length - 1].timestamp

    return {
      totalChecks,
      averageHealth: Math.round(averageHealth),
      uptime: Math.round(uptime * 100) / 100,
      lastCheck,
    }
  }
}

// Export singleton instance
export const healthMonitoring = new HealthMonitoringService()

// Export types for external use
export type { HealthCheckResult, HealthCheckConfig, HealthIndexMetrics }
