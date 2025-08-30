import { correlationIDManager } from './correlation-id'

// Alert threshold configuration interface
export interface AlertThreshold {
  name: string
  metric: string
  warning: number
  critical: number
  enabled: boolean
  description: string
  category: 'performance' | 'availability' | 'security' | 'business'
  severity: 'low' | 'medium' | 'high' | 'critical'
  cooldown: number // seconds between alerts
  lastTriggered?: number
  escalation?: {
    enabled: boolean
    levels: number[]
    contacts: string[]
  }
}

// Alert event interface
export interface AlertEvent {
  id: string
  threshold: AlertThreshold
  value: number
  status: 'warning' | 'critical' | 'resolved'
  timestamp: number
  correlationId?: string
  metadata: Record<string, any>
}

// Alert threshold manager
export class AlertThresholdManager {
  private static instance: AlertThresholdManager
  private thresholds: Map<string, AlertThreshold> = new Map()
  private alertHistory: AlertEvent[] = []
  private isMonitoring: boolean = false
  private monitoringInterval: NodeJS.Timeout | null = null

  static getInstance(): AlertThresholdManager {
    if (!AlertThresholdManager.instance) {
      AlertThresholdManager.instance = new AlertThresholdManager()
    }
    return AlertThresholdManager.instance
  }

  constructor() {
    this.initializeDefaultThresholds()
  }

  // Initialize default production thresholds
  private initializeDefaultThresholds(): void {
    const defaultThresholds: AlertThreshold[] = [
      // Performance thresholds
      {
        name: 'Error Rate Warning',
        metric: 'error_rate',
        warning: 2.0, // 2% error rate
        critical: 5.0, // 5% error rate
        enabled: true,
        description: 'System error rate threshold',
        category: 'performance',
        severity: 'medium',
        cooldown: 300, // 5 minutes
        escalation: {
          enabled: true,
          levels: [5.0, 10.0, 15.0],
          contacts: ['dev-team', 'oncall', 'management']
        }
      },
      {
        name: 'Response Time Warning',
        metric: 'response_time',
        warning: 500, // 500ms
        critical: 2000, // 2 seconds
        enabled: true,
        description: 'API response time threshold',
        category: 'performance',
        severity: 'medium',
        cooldown: 300,
        escalation: {
          enabled: true,
          levels: [2000, 5000, 10000],
          contacts: ['dev-team', 'oncall']
        }
      },
      {
        name: 'CPU Usage Warning',
        metric: 'cpu_usage',
        warning: 70.0, // 70%
        critical: 85.0, // 85%
        enabled: true,
        description: 'CPU utilization threshold',
        category: 'performance',
        severity: 'high',
        cooldown: 180, // 3 minutes
        escalation: {
          enabled: true,
          levels: [85.0, 90.0, 95.0],
          contacts: ['ops-team', 'oncall', 'management']
        }
      },
      {
        name: 'Memory Usage Warning',
        metric: 'memory_usage',
        warning: 80.0, // 80%
        critical: 90.0, // 90%
        enabled: true,
        description: 'Memory utilization threshold',
        category: 'performance',
        severity: 'high',
        cooldown: 180,
        escalation: {
          enabled: true,
          levels: [90.0, 95.0, 98.0],
          contacts: ['ops-team', 'oncall', 'management']
        }
      },
      {
        name: 'Disk Usage Warning',
        metric: 'disk_usage',
        warning: 75.0, // 75%
        critical: 85.0, // 85%
        enabled: true,
        description: 'Disk space utilization threshold',
        category: 'performance',
        severity: 'medium',
        cooldown: 600, // 10 minutes
        escalation: {
          enabled: true,
          levels: [85.0, 90.0, 95.0],
          contacts: ['ops-team', 'oncall']
        }
      },

      // Availability thresholds
      {
        name: 'Uptime Warning',
        metric: 'uptime',
        warning: 99.0, // 99%
        critical: 95.0, // 95%
        enabled: true,
        description: 'System uptime threshold',
        category: 'availability',
        severity: 'critical',
        cooldown: 60, // 1 minute
        escalation: {
          enabled: true,
          levels: [95.0, 90.0, 80.0],
          contacts: ['oncall', 'management', 'executive']
        }
      },
      {
        name: 'Health Check Failure',
        metric: 'health_check_failure',
        warning: 1, // 1 failure
        critical: 3, // 3 failures
        enabled: true,
        description: 'Health check failure threshold',
        category: 'availability',
        severity: 'high',
        cooldown: 120, // 2 minutes
        escalation: {
          enabled: true,
          levels: [3, 5, 10],
          contacts: ['dev-team', 'oncall', 'management']
        }
      },

      // Security thresholds
      {
        name: 'Failed Login Attempts',
        metric: 'failed_logins',
        warning: 10, // 10 attempts
        critical: 50, // 50 attempts
        enabled: true,
        description: 'Failed authentication attempts threshold',
        category: 'security',
        severity: 'high',
        cooldown: 300,
        escalation: {
          enabled: true,
          levels: [50, 100, 200],
          contacts: ['security-team', 'oncall', 'management']
        }
      },
      {
        name: 'API Rate Limit Exceeded',
        metric: 'rate_limit_exceeded',
        warning: 100, // 100 requests
        critical: 1000, // 1000 requests
        enabled: true,
        description: 'API rate limit violation threshold',
        category: 'security',
        severity: 'medium',
        cooldown: 180,
        escalation: {
          enabled: true,
          levels: [1000, 5000, 10000],
          contacts: ['security-team', 'dev-team']
        }
      },

      // Business thresholds
      {
        name: 'Transaction Failure Rate',
        metric: 'transaction_failure_rate',
        warning: 1.0, // 1%
        critical: 5.0, // 5%
        enabled: true,
        description: 'Business transaction failure threshold',
        category: 'business',
        severity: 'critical',
        cooldown: 60,
        escalation: {
          enabled: true,
          levels: [5.0, 10.0, 20.0],
          contacts: ['business-team', 'management', 'executive']
        }
      },
      {
        name: 'Revenue Impact',
        metric: 'revenue_impact',
        warning: 1000, // $1000
        critical: 10000, // $10,000
        enabled: true,
        description: 'Revenue impact threshold',
        category: 'business',
        severity: 'critical',
        cooldown: 300,
        escalation: {
          enabled: true,
          levels: [10000, 50000, 100000],
          contacts: ['business-team', 'executive', 'board']
        }
      }
    ]

    defaultThresholds.forEach(threshold => {
      this.thresholds.set(threshold.name, threshold)
    })
  }

  // Add or update a threshold
  addThreshold(threshold: AlertThreshold): void {
    this.thresholds.set(threshold.name, threshold)
    this.logThresholdChange('added', threshold)
  }

  // Remove a threshold
  removeThreshold(name: string): boolean {
    const threshold = this.thresholds.get(name)
    if (threshold) {
      this.thresholds.delete(name)
      this.logThresholdChange('removed', threshold)
      return true
    }
    return false
  }

  // Get all thresholds
  getAllThresholds(): AlertThreshold[] {
    return Array.from(this.thresholds.values())
  }

  // Get threshold by name
  getThreshold(name: string): AlertThreshold | undefined {
    return this.thresholds.get(name)
  }

  // Update threshold values
  updateThreshold(name: string, updates: Partial<AlertThreshold>): boolean {
    const threshold = this.thresholds.get(name)
    if (threshold) {
      const updatedThreshold = { ...threshold, ...updates }
      this.thresholds.set(name, updatedThreshold)
      this.logThresholdChange('updated', updatedThreshold)
      return true
    }
    return false
  }

  // Check if a metric value triggers an alert
  checkThreshold(metric: string, value: number): AlertEvent[] {
    const triggeredAlerts: AlertEvent[] = []
    const now = Date.now()

    for (const threshold of this.thresholds.values()) {
      if (!threshold.enabled || threshold.metric !== metric) continue

      // Check cooldown
      if (threshold.lastTriggered && 
          (now - threshold.lastTriggered) < (threshold.cooldown * 1000)) {
        continue
      }

      let status: 'warning' | 'critical' | 'resolved' | null = null

      if (value >= threshold.critical) {
        status = 'critical'
      } else if (value >= threshold.warning) {
        status = 'warning'
      } else if (threshold.lastTriggered) {
        // Check if we should resolve the alert
        status = 'resolved'
      }

      if (status) {
        const alertEvent: AlertEvent = {
          id: `${threshold.name}_${now}`,
          threshold,
          value,
          status,
          timestamp: now,
          correlationId: correlationIDManager.getCurrentContext()?.correlationId,
          metadata: {
            metric,
            value,
            threshold: {
              warning: threshold.warning,
              critical: threshold.critical
            },
            category: threshold.category,
            severity: threshold.severity
          }
        }

        triggeredAlerts.push(alertEvent)

        // Update last triggered time for warning/critical alerts
        if (status !== 'resolved') {
          threshold.lastTriggered = now
          this.thresholds.set(threshold.name, threshold)
        }

        // Log the alert
        this.logAlert(alertEvent)
      }
    }

    return triggeredAlerts
  }

  // Start monitoring thresholds
  startMonitoring(intervalMs: number = 30000): void {
    if (this.isMonitoring) return

    this.isMonitoring = true
    this.monitoringInterval = setInterval(() => {
      this.runThresholdChecks()
    }, intervalMs)

    console.log('Alert threshold monitoring started with interval:', intervalMs, 'ms')
  }

  // Stop monitoring thresholds
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval)
      this.monitoringInterval = null
    }
    this.isMonitoring = false
    console.log('Alert threshold monitoring stopped')
  }

  // Run threshold checks (placeholder for actual metric collection)
  private async runThresholdChecks(): Promise<void> {
    // This would typically collect metrics from various sources
    // For now, we'll just log that monitoring is active
    const activeThresholds = this.getAllThresholds().filter(t => t.enabled)
    if (activeThresholds.length > 0) {
      console.log(`Monitoring ${activeThresholds.length} active thresholds`)
    }
  }

  // Get alert history
  getAlertHistory(limit: number = 100): AlertEvent[] {
    return this.alertHistory.slice(-limit)
  }

  // Clear alert history
  clearAlertHistory(): void {
    this.alertHistory = []
  }

  // Get alerts by status
  getAlertsByStatus(status: 'warning' | 'critical' | 'resolved'): AlertEvent[] {
    return this.alertHistory.filter(alert => alert.status === status)
  }

  // Get alerts by category
  getAlertsByCategory(category: string): AlertEvent[] {
    return this.alertHistory.filter(alert => alert.threshold.category === category)
  }

  // Get alerts by severity
  getAlertsBySeverity(severity: string): AlertEvent[] {
    return this.alertHistory.filter(alert => alert.threshold.severity === severity)
  }

  // Log threshold changes
  private logThresholdChange(action: string, threshold: AlertThreshold): void {
    const context = correlationIDManager.getCurrentContext()
    if (context) {
      correlationIDManager.logContext(context, 'info')
    }

    console.log(`🔔 Alert threshold ${action}:`, {
      name: threshold.name,
      metric: threshold.metric,
      warning: threshold.warning,
      critical: threshold.critical,
      category: threshold.category,
      severity: threshold.severity,
      correlationId: context?.correlationId
    })
  }

  // Log alerts
  private logAlert(alert: AlertEvent): void {
    // Add to history
    this.alertHistory.push(alert)
    if (this.alertHistory.length > 1000) {
      this.alertHistory = this.alertHistory.slice(-1000)
    }

    // Log the alert
    const emoji = alert.status === 'critical' ? '🚨' : 
                  alert.status === 'warning' ? '⚠️' : '✅'
    
    console.log(`${emoji} Alert triggered:`, {
      name: alert.threshold.name,
      status: alert.status,
      value: alert.value,
      threshold: alert.threshold,
      timestamp: new Date(alert.timestamp).toISOString(),
      correlationId: alert.correlationId
    })

    // TODO: Send alerts to external systems (Slack, PagerDuty, etc.)
    this.sendExternalAlert(alert)
  }

  // Send external alert (placeholder)
  private async sendExternalAlert(alert: AlertEvent): Promise<void> {
    // This would integrate with external alerting systems
    // For now, we'll just log that we would send it
    console.log(`📤 Would send external alert for: ${alert.threshold.name}`)
  }

  // Get monitoring status
  getMonitoringStatus(): { isActive: boolean; interval: number | null; thresholdCount: number } {
    return {
      isActive: this.isMonitoring,
      interval: this.monitoringInterval ? 30000 : null,
      thresholdCount: this.thresholds.size
    }
  }

  // Export thresholds to JSON
  exportThresholds(): string {
    return JSON.stringify(Array.from(this.thresholds.values()), null, 2)
  }

  // Import thresholds from JSON
  importThresholds(jsonData: string): boolean {
    try {
      const thresholds = JSON.parse(jsonData) as AlertThreshold[]
      this.thresholds.clear()
      thresholds.forEach(threshold => {
        this.thresholds.set(threshold.name, threshold)
      })
      console.log(`Imported ${thresholds.length} thresholds`)
      return true
    } catch (error) {
      console.error('Failed to import thresholds:', error)
      return false
    }
  }
}

// Export singleton instance
export const alertThresholdManager = AlertThresholdManager.getInstance()

// Export types
export type { AlertThreshold, AlertEvent }
