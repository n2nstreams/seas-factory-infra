/**
 * Performance Monitoring Service - Module 12
 * 
 * Integrates with existing:
 * - Cost monitoring (Night 49)
 * - Load testing (Night 69) 
 * - Health monitoring (Module 8)
 * - Feature flags
 * 
 * Provides comprehensive performance tracking, cost controls, and load testing orchestration
 */

import { healthMonitoring, type HealthCheckResult } from './health-monitoring'

// Performance metrics interface
export interface PerformanceMetrics {
  timestamp: Date
  service: string
  endpoint: string
  responseTime: number
  throughput: number
  errorRate: number
  costEstimate: number
  resourceUsage: {
    cpu: number
    memory: number
    databaseConnections: number
  }
}

// Cost budget interface
export interface CostBudget {
  service: string
  monthlyBudget: number
  currentSpend: number
  threshold: number
  alerts: CostAlert[]
}

// Cost alert interface
export interface CostAlert {
  id: string
  timestamp: Date
  severity: 'warning' | 'critical' | 'emergency'
  message: string
  threshold: number
  currentValue: number
  acknowledged: boolean
}

// Load test configuration interface
export interface LoadTestConfig {
  testType: 'spike' | 'load' | 'stress' | 'soak' | 'custom'
  target: {
    name: string
    baseUrl: string
    endpoints: string[]
    authRequired?: boolean
    authToken?: string
    customHeaders?: Record<string, string>
  }
  duration: number // minutes
  virtualUsers: number
  rampUpDuration?: number // seconds
  thresholds: {
    httpReqDuration: string[]
    httpReqFailed: string[]
    custom?: Record<string, string[]>
  }
}

// Load test result interface
export interface LoadTestResult {
  id: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  startTime: Date
  endTime?: Date
  config: LoadTestConfig
  metrics: {
    totalRequests: number
    failedRequests: number
    averageResponseTime: number
    p95ResponseTime: number
    p99ResponseTime: number
    requestsPerSecond: number
    errorRate: number
  }
  thresholds: {
    passed: string[]
    failed: string[]
  }
  anomalies: string[]
  recommendations: string[]
}

// Performance monitoring configuration
export interface PerformanceMonitoringConfig {
  enabled: boolean
  checkInterval: number // seconds
  costThresholds: {
    warning: number // percentage
    critical: number // percentage
    emergency: number // percentage
  }
  performanceThresholds: {
    responseTimeWarning: number // ms
    responseTimeCritical: number // ms
    errorRateWarning: number // percentage
    errorRateCritical: number // percentage
  }
  loadTestDefaults: {
    maxDuration: number // minutes
    maxVirtualUsers: number
    maxConcurrentTests: number
  }
}

// Default configuration
const DEFAULT_CONFIG: PerformanceMonitoringConfig = {
  enabled: true,
  checkInterval: 30,
  costThresholds: {
    warning: 50,
    critical: 80,
    emergency: 100
  },
  performanceThresholds: {
    responseTimeWarning: 1000,
    responseTimeCritical: 5000,
    errorRateWarning: 5,
    errorRateCritical: 10
  },
  loadTestDefaults: {
    maxDuration: 60,
    maxVirtualUsers: 100,
    maxConcurrentTests: 3
  }
}

/**
 * Performance Monitoring Service
 * 
 * Integrates cost monitoring, performance tracking, and load testing
 * to provide comprehensive system oversight and prevent regressions
 */
export class PerformanceMonitoringService {
  private config: PerformanceMonitoringConfig
  private metrics: PerformanceMetrics[] = []
  private budgets: CostBudget[] = []
  private loadTests: Map<string, LoadTestResult> = new Map()
  private monitoringActive = false
  private monitoringInterval?: NodeJS.Timeout

  constructor(config?: Partial<PerformanceMonitoringConfig>) {
    this.config = { ...DEFAULT_CONFIG, ...config }
    this.initializeBudgets()
  }

  /**
   * Initialize default cost budgets for core services
   */
  private initializeBudgets(): void {
    this.budgets = [
      {
        service: 'supabase-database',
        monthlyBudget: 100,
        currentSpend: 0,
        threshold: this.config.costThresholds.warning,
        alerts: []
      },
      {
        service: 'supabase-storage',
        monthlyBudget: 50,
        currentSpend: 0,
        threshold: this.config.costThresholds.warning,
        alerts: []
      },
      {
        service: 'supabase-edge-functions',
        monthlyBudget: 75,
        currentSpend: 0,
        threshold: this.config.costThresholds.warning,
        alerts: []
      },
      {
        service: 'vercel-hosting',
        monthlyBudget: 200,
        currentSpend: 0,
        threshold: this.config.costThresholds.warning,
        alerts: []
      },
      {
        service: 'stripe-billing',
        monthlyBudget: 25,
        currentSpend: 0,
        threshold: this.config.costThresholds.warning,
        alerts: []
      }
    ]
  }

  /**
   * Start performance monitoring
   */
  async startMonitoring(): Promise<void> {
    if (this.monitoringActive) {
      console.warn('Performance monitoring already active')
      return
    }

    this.monitoringActive = true
    console.log('Starting performance monitoring...')

    // Start monitoring loop
    this.monitoringInterval = setInterval(async () => {
      await this.runPerformanceChecks()
    }, this.config.checkInterval * 1000)

    // Initial check
    await this.runPerformanceChecks()
  }

  /**
   * Stop performance monitoring
   */
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval)
      this.monitoringInterval = undefined
    }
    this.monitoringActive = false
    console.log('Performance monitoring stopped')
  }

  /**
   * Run comprehensive performance checks
   */
  private async runPerformanceChecks(): Promise<void> {
    try {
      // Collect health metrics
      const healthResult = await healthMonitoring.runHealthCheck()
      
      // Collect performance metrics
      await this.collectPerformanceMetrics()
      
      // Check cost budgets
      await this.checkCostBudgets()
      
      // Validate performance thresholds
      this.validatePerformanceThresholds()
      
      // Store metrics
      this.storeMetrics()
      
    } catch (error) {
      console.error('Error running performance checks:', error)
    }
  }

  /**
   * Collect performance metrics from various sources
   */
  private async collectPerformanceMetrics(): Promise<void> {
    try {
      // Collect from health monitoring
      const healthMetrics = await healthMonitoring.getHealthSummary()
      
      // Collect from browser performance API
      if (typeof window !== 'undefined' && 'performance' in window) {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
        if (navigation) {
          this.metrics.push({
            timestamp: new Date(),
            service: 'frontend',
            endpoint: window.location.pathname,
            responseTime: navigation.loadEventEnd - navigation.loadEventStart,
            throughput: 1 / (navigation.loadEventEnd - navigation.loadEventStart) * 1000,
            errorRate: 0,
            costEstimate: 0,
            resourceUsage: {
              cpu: 0,
              memory: 0,
              databaseConnections: 0
            }
          })
        }
      }
      
      // Collect from health monitoring
      if (healthMetrics.checks) {
        Object.entries(healthMetrics.checks).forEach(([service, check]: [string, any]) => {
          this.metrics.push({
            timestamp: new Date(),
            service,
            endpoint: '/health',
            responseTime: check.responseTime || 0,
            throughput: 1 / (check.responseTime || 1) * 1000,
            errorRate: check.status === 'pass' ? 0 : 100,
            costEstimate: 0,
            resourceUsage: {
              cpu: 0,
              memory: 0,
              databaseConnections: 0
            }
          })
        })
      }
      
    } catch (error) {
      console.error('Error collecting performance metrics:', error)
    }
  }

  /**
   * Check cost budgets and generate alerts
   */
  private async checkCostBudgets(): Promise<void> {
    try {
      // In a real implementation, this would fetch actual cost data
      // from GCP billing API, Supabase dashboard, etc.
      
      this.budgets.forEach(budget => {
        const utilization = (budget.currentSpend / budget.monthlyBudget) * 100
        
        if (utilization >= this.config.costThresholds.emergency) {
          this.createCostAlert(budget, 'emergency', utilization)
        } else if (utilization >= this.config.costThresholds.critical) {
          this.createCostAlert(budget, 'critical', utilization)
        } else if (utilization >= this.config.costThresholds.warning) {
          this.createCostAlert(budget, 'warning', utilization)
        }
      })
      
    } catch (error) {
      console.error('Error checking cost budgets:', error)
    }
  }

  /**
   * Create cost alert
   */
  private createCostAlert(budget: CostBudget, severity: 'warning' | 'critical' | 'emergency', utilization: number): void {
    const alert: CostAlert = {
      id: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
      severity,
      message: `${severity.toUpperCase()}: ${budget.service} has used ${utilization.toFixed(1)}% of monthly budget`,
      threshold: this.config.costThresholds[severity],
      currentValue: utilization,
      acknowledged: false
    }
    
    budget.alerts.push(alert)
    
    // Log alert
    console.warn(`Cost Alert: ${alert.message}`)
    
    // In production, this would trigger notifications
    // this.notifyCostAlert(alert)
  }

  /**
   * Validate performance thresholds
   */
  private validatePerformanceThresholds(): void {
    const recentMetrics = this.metrics.slice(-10) // Last 10 metrics
    
    recentMetrics.forEach(metric => {
      // Check response time thresholds
      if (metric.responseTime > this.config.performanceThresholds.responseTimeCritical) {
        console.error(`Critical: ${metric.service} response time ${metric.responseTime}ms exceeds threshold`)
      } else if (metric.responseTime > this.config.performanceThresholds.responseTimeWarning) {
        console.warn(`Warning: ${metric.service} response time ${metric.responseTime}ms exceeds warning threshold`)
      }
      
      // Check error rate thresholds
      if (metric.errorRate > this.config.performanceThresholds.errorRateCritical) {
        console.error(`Critical: ${metric.service} error rate ${metric.errorRate}% exceeds threshold`)
      } else if (metric.errorRate > this.config.performanceThresholds.errorRateWarning) {
        console.warn(`Warning: ${metric.service} error rate ${metric.errorRate}% exceeds warning threshold`)
      }
    })
  }

  /**
   * Store metrics (in production, this would go to a database)
   */
  private storeMetrics(): void {
    // Keep only last 1000 metrics in memory
    if (this.metrics.length > 1000) {
      this.metrics = this.metrics.slice(-1000)
    }
  }

  /**
   * Start a load test
   */
  async startLoadTest(config: LoadTestConfig): Promise<string> {
    try {
      // Validate configuration
      this.validateLoadTestConfig(config)
      
      // Check concurrent test limits
      const runningTests = Array.from(this.loadTests.values()).filter(
        test => test.status === 'running'
      )
      
      if (runningTests.length >= this.config.loadTestDefaults.maxConcurrentTests) {
        throw new Error(`Maximum concurrent tests (${this.config.loadTestDefaults.maxConcurrentTests}) exceeded`)
      }
      
      // Create test result
      const testId = `load_test_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      const testResult: LoadTestResult = {
        id: testId,
        status: 'pending',
        startTime: new Date(),
        config,
        metrics: {
          totalRequests: 0,
          failedRequests: 0,
          averageResponseTime: 0,
          p95ResponseTime: 0,
          p99ResponseTime: 0,
          requestsPerSecond: 0,
          errorRate: 0
        },
        thresholds: {
          passed: [],
          failed: []
        },
        anomalies: [],
        recommendations: []
      }
      
      // Store test
      this.loadTests.set(testId, testResult)
      
      // Start test execution (in production, this would use k6 or similar)
      this.executeLoadTest(testId, config)
      
      return testId
      
    } catch (error) {
      console.error('Error starting load test:', error)
      throw error
    }
  }

  /**
   * Validate load test configuration
   */
  private validateLoadTestConfig(config: LoadTestConfig): void {
    if (config.duration > this.config.loadTestDefaults.maxDuration) {
      throw new Error(`Duration ${config.duration} minutes exceeds maximum ${this.config.loadTestDefaults.maxDuration} minutes`)
    }
    
    if (config.virtualUsers > this.config.loadTestDefaults.maxVirtualUsers) {
      throw new Error(`Virtual users ${config.virtualUsers} exceeds maximum ${this.config.loadTestDefaults.maxVirtualUsers}`)
    }
    
    if (!config.target.baseUrl || !config.target.endpoints || config.target.endpoints.length === 0) {
      throw new Error('Invalid target configuration')
    }
  }

  /**
   * Execute load test (simplified implementation)
   */
  private async executeLoadTest(testId: string, config: LoadTestConfig): Promise<void> {
    const testResult = this.loadTests.get(testId)
    if (!testResult) return
    
    try {
      // Update status to running
      testResult.status = 'running'
      
      // Simulate test execution
      // In production, this would integrate with k6 or similar tool
      await this.simulateLoadTest(testResult, config)
      
      // Update status to completed
      testResult.status = 'completed'
      testResult.endTime = new Date()
      
      // Analyze results
      this.analyzeLoadTestResults(testResult)
      
    } catch (error) {
      testResult.status = 'failed'
      testResult.endTime = new Date()
      console.error(`Load test ${testId} failed:`, error)
    }
  }

  /**
   * Simulate load test execution (for demo purposes)
   */
  private async simulateLoadTest(testResult: LoadTestResult, config: LoadTestConfig): Promise<void> {
    const startTime = Date.now()
    const duration = config.duration * 60 * 1000 // Convert to milliseconds
    
    // Simulate test execution over time
    while (Date.now() - startTime < duration) {
      // Simulate requests
      const responseTime = Math.random() * 2000 + 100 // 100-2100ms
      const success = Math.random() > 0.1 // 90% success rate
      
      testResult.metrics.totalRequests++
      if (!success) {
        testResult.metrics.failedRequests++
      }
      
      // Update average response time
      const currentAvg = testResult.metrics.averageResponseTime
      const newAvg = (currentAvg * (testResult.metrics.totalRequests - 1) + responseTime) / testResult.metrics.totalRequests
      testResult.metrics.averageResponseTime = newAvg
      
      // Update requests per second
      const elapsed = (Date.now() - startTime) / 1000
      testResult.metrics.requestsPerSecond = testResult.metrics.totalRequests / elapsed
      
      // Update error rate
      testResult.metrics.errorRate = (testResult.metrics.failedRequests / testResult.metrics.totalRequests) * 100
      
      // Simulate some delay
      await new Promise(resolve => setTimeout(resolve, 100))
    }
    
    // Calculate percentiles (simplified)
    testResult.metrics.p95ResponseTime = testResult.metrics.averageResponseTime * 1.5
    testResult.metrics.p99ResponseTime = testResult.metrics.averageResponseTime * 2.0
  }

  /**
   * Analyze load test results
   */
  private analyzeLoadTestResults(testResult: LoadTestResult): void {
    // Check thresholds
    testResult.config.thresholds.httpReqDuration.forEach(threshold => {
      const match = threshold.match(/p\((\d+)\)<(\d+)/)
      if (match) {
        const percentile = parseInt(match[1])
        const limit = parseInt(match[2])
        
        let actualValue: number
        if (percentile === 95) {
          actualValue = testResult.metrics.p95ResponseTime
        } else if (percentile === 99) {
          actualValue = testResult.metrics.p99ResponseTime
        } else {
          actualValue = testResult.metrics.averageResponseTime
        }
        
        if (actualValue < limit) {
          testResult.thresholds.passed.push(threshold)
        } else {
          testResult.thresholds.failed.push(threshold)
        }
      }
    })
    
    testResult.config.thresholds.httpReqFailed.forEach(threshold => {
      const match = threshold.match(/rate<(\d+\.?\d*)/)
      if (match) {
        const limit = parseFloat(match[1])
        if (testResult.metrics.errorRate < limit) {
          testResult.thresholds.passed.push(threshold)
        } else {
          testResult.thresholds.failed.push(threshold)
        }
      }
    })
    
    // Detect anomalies
    if (testResult.metrics.errorRate > 5) {
      testResult.anomalies.push('High error rate detected')
    }
    
    if (testResult.metrics.averageResponseTime > 2000) {
      testResult.anomalies.push('Slow response times detected')
    }
    
    // Generate recommendations
    if (testResult.thresholds.failed.length > 0) {
      testResult.recommendations.push('Review failed thresholds and optimize performance')
    }
    
    if (testResult.anomalies.length > 0) {
      testResult.recommendations.push('Investigate anomalies and implement fixes')
    }
    
    if (testResult.metrics.errorRate > 10) {
      testResult.recommendations.push('High error rate suggests system instability - investigate immediately')
    }
  }

  /**
   * Get load test status
   */
  getLoadTestStatus(testId: string): LoadTestResult | null {
    return this.loadTests.get(testId) || null
  }

  /**
   * Get all load tests
   */
  getAllLoadTests(): LoadTestResult[] {
    return Array.from(this.loadTests.values())
  }

  /**
   * Cancel load test
   */
  cancelLoadTest(testId: string): boolean {
    const testResult = this.loadTests.get(testId)
    if (testResult && testResult.status === 'running') {
      testResult.status = 'cancelled'
      testResult.endTime = new Date()
      return true
    }
    return false
  }

  /**
   * Get performance summary
   */
  getPerformanceSummary(): {
    metrics: PerformanceMetrics[]
    budgets: CostBudget[]
    loadTests: LoadTestResult[]
    health: any
  } {
    return {
      metrics: this.metrics,
      budgets: this.budgets,
      loadTests: Array.from(this.loadTests.values()),
      health: healthMonitoring.getHealthSummary()
    }
  }

  /**
   * Get cost summary
   */
  getCostSummary(): {
    totalMonthlyBudget: number
    totalCurrentSpend: number
    totalUtilization: number
    alerts: CostAlert[]
  } {
    const totalMonthlyBudget = this.budgets.reduce((sum, budget) => sum + budget.monthlyBudget, 0)
    const totalCurrentSpend = this.budgets.reduce((sum, budget) => sum + budget.currentSpend, 0)
    const totalUtilization = (totalCurrentSpend / totalMonthlyBudget) * 100
    
    const allAlerts = this.budgets.flatMap(budget => budget.alerts)
    
    return {
      totalMonthlyBudget,
      totalCurrentSpend,
      totalUtilization,
      alerts: allAlerts
    }
  }

  /**
   * Update cost data (for integration with actual cost monitoring)
   */
  updateCostData(service: string, currentSpend: number): void {
    const budget = this.budgets.find(b => b.service === service)
    if (budget) {
      budget.currentSpend = currentSpend
    }
  }

  /**
   * Acknowledge cost alert
   */
  acknowledgeCostAlert(alertId: string): boolean {
    for (const budget of this.budgets) {
      const alert = budget.alerts.find(a => a.id === alertId)
      if (alert) {
        alert.acknowledged = true
        return true
      }
    }
    return false
  }

  /**
   * Get configuration
   */
  getConfig(): PerformanceMonitoringConfig {
    return { ...this.config }
  }

  /**
   * Update configuration
   */
  updateConfig(updates: Partial<PerformanceMonitoringConfig>): void {
    this.config = { ...this.config, ...updates }
  }
}

// Export singleton instance
export const performanceMonitoring = new PerformanceMonitoringService()

// Export types for external use
export type {
  PerformanceMetrics,
  CostBudget,
  CostAlert,
  LoadTestConfig,
  LoadTestResult,
  PerformanceMonitoringConfig
}
