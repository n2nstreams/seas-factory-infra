'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { healthMonitoring, type HealthResult, type HealthIndexMetrics } from '@/lib/health-monitoring-simple'
import { correlationIDManager, useCorrelationID } from '@/lib/correlation-id'
import { alertThresholdManager, type AlertThreshold, type AlertEvent } from '@/lib/alert-thresholds'

// Observability context interface
interface ObservabilityContextType {
  // Health monitoring
  currentHealth: HealthResult | null
  healthHistory: HealthResult[]
  metricsHistory: HealthIndexMetrics[]
  isMonitoring: boolean
  startMonitoring: () => void
  stopMonitoring: () => void
  runHealthCheck: () => Promise<void>
  
  // Correlation ID tracking
  correlationId: string | undefined
  requestId: string | undefined
  spanId: string | undefined
  traceId: string | undefined
  generateCorrelationContext: (
    parentId?: string,
    userId?: string,
    tenantId?: string,
    sessionId?: string,
    metadata?: Record<string, any>
  ) => void
  getCorrelationHeaders: () => Record<string, string>
  
  // Alert thresholds
  alertThresholds: AlertThreshold[]
  alertHistory: AlertEvent[]
  isAlertMonitoring: boolean
  startAlertMonitoring: () => void
  stopAlertMonitoring: () => void
  updateThreshold: (name: string, updates: Partial<AlertThreshold>) => boolean
  addThreshold: (threshold: AlertThreshold) => void
  removeThreshold: (name: string) => boolean
  
  // System status
  systemStatus: {
    health: 'healthy' | 'degraded' | 'unhealthy'
    alerts: {
      warning: number
      critical: number
      resolved: number
    }
    uptime: number
    lastUpdate: string
  }
}

// Create observability context
const ObservabilityContext = createContext<ObservabilityContextType | undefined>(undefined)

// Observability provider component
export function ObservabilityProvider({ children }: { children: ReactNode }) {
  // Health monitoring state
  const [currentHealth, setCurrentHealth] = useState<HealthResult | null>(null)
  const [healthHistory, setHealthHistory] = useState<HealthResult[]>([])
  const [metricsHistory, setMetricsHistory] = useState<HealthIndexMetrics[]>([])
  const [isMonitoring, setIsMonitoring] = useState(false)

  // Alert threshold state
  const [alertThresholds, setAlertThresholds] = useState<AlertThreshold[]>([])
  const [alertHistory, setAlertHistory] = useState<AlertEvent[]>([])
  const [isAlertMonitoring, setIsAlertMonitoring] = useState(false)

  // System status state
  const [systemStatus, setSystemStatus] = useState({
    health: 'healthy' as const,
    alerts: { warning: 0, critical: 0, resolved: 0 },
    uptime: 0,
    lastUpdate: new Date().toISOString()
  })

  // Initialize correlation ID context for this provider
  useEffect(() => {
    const context = correlationIDManager.generateContext(
      undefined,
      undefined,
      undefined,
      undefined,
      { operation: 'observability_provider_init', component: 'ObservabilityProvider' }
    )
    
    // Log the initialization
    correlationIDManager.logContext(context, 'info')
  }, [])

  // Initialize health monitoring
  useEffect(() => {
    const initializeHealthMonitoring = async () => {
      try {
        // Run initial health check
        await runHealthCheck()
        
        // Start monitoring
        startMonitoring()
      } catch (error) {
        console.error('Failed to initialize health monitoring:', error)
      }
    }

    initializeHealthMonitoring()

    return () => {
      stopMonitoring()
    }
  }, [])

  // Initialize alert thresholds
  useEffect(() => {
    const thresholds = alertThresholdManager.getAllThresholds()
    setAlertThresholds(thresholds)
    
    // Start alert monitoring
    startAlertMonitoring()
    
    return () => {
      stopAlertMonitoring()
    }
  }, [])

  // Update system status periodically
  useEffect(() => {
    const updateSystemStatus = () => {
      const health = currentHealth?.status || 'healthy'
      const alerts = {
        warning: alertHistory.filter(a => a.status === 'warning').length,
        critical: alertHistory.filter(a => a.status === 'critical').length,
        resolved: alertHistory.filter(a => a.status === 'resolved').length
      }
      const uptime = currentHealth ? Date.now() - new Date(currentHealth.timestamp).getTime() : 0
      
      setSystemStatus({
        health,
        alerts,
        uptime,
        lastUpdate: new Date().toISOString()
      })
    }

    const interval = setInterval(updateSystemStatus, 10000) // Update every 10 seconds
    updateSystemStatus() // Initial update

    return () => clearInterval(interval)
  }, [currentHealth, alertHistory])

  // Health monitoring functions
  const startMonitoring = () => {
    healthMonitoring.startMonitoring()
    setIsMonitoring(true)
  }

  const stopMonitoring = () => {
    healthMonitoring.stopMonitoring()
    setIsMonitoring(false)
  }

  const runHealthCheck = async () => {
    try {
      const result = await healthMonitoring.runComprehensiveHealthCheck()
      setCurrentHealth(result)
      setHealthHistory(healthMonitoring.getHealthHistory())
      setMetricsHistory(healthMonitoring.getMetricsHistory())
    } catch (error) {
      console.error('Health check failed:', error)
    }
  }

  // Alert monitoring functions
  const startAlertMonitoring = () => {
    alertThresholdManager.startMonitoring()
    setIsAlertMonitoring(true)
    
    // Set up periodic alert history updates
    const updateAlertHistory = () => {
      setAlertHistory(alertThresholdManager.getAlertHistory())
    }
    
    const interval = setInterval(updateAlertHistory, 5000) // Update every 5 seconds
    updateAlertHistory() // Initial update
    
    // Store interval for cleanup
    ;(window as any).alertHistoryInterval = interval
  }

  const stopAlertMonitoring = () => {
    alertThresholdManager.stopMonitoring()
    setIsAlertMonitoring(false)
    
    // Clear interval
    if ((window as any).alertHistoryInterval) {
      clearInterval((window as any).alertHistoryInterval)
    }
  }

  const updateThreshold = (name: string, updates: Partial<AlertThreshold>): boolean => {
    const success = alertThresholdManager.updateThreshold(name, updates)
    if (success) {
      setAlertThresholds(alertThresholdManager.getAllThresholds())
    }
    return success
  }

  const addThreshold = (threshold: AlertThreshold) => {
    alertThresholdManager.addThreshold(threshold)
    setAlertThresholds(alertThresholdManager.getAllThresholds())
  }

  const removeThreshold = (name: string): boolean => {
    const success = alertThresholdManager.removeThreshold(name)
    if (success) {
      setAlertThresholds(alertThresholdManager.getAllThresholds())
    }
    return success
  }

  // Correlation ID functions
  const generateCorrelationContext = (
    parentId?: string,
    userId?: string,
    tenantId?: string,
    sessionId?: string,
    metadata?: Record<string, any>
  ) => {
    correlationIDManager.generateContext(parentId, userId, tenantId, sessionId, metadata)
  }

  const getCorrelationHeaders = () => correlationIDManager.getHeaders()

  // Get current correlation context
  const currentContext = correlationIDManager.getCurrentContext()

  // Context value
  const contextValue: ObservabilityContextType = {
    // Health monitoring
    currentHealth,
    healthHistory,
    metricsHistory,
    isMonitoring,
    startMonitoring,
    stopMonitoring,
    runHealthCheck,
    
    // Correlation ID tracking
    correlationId: currentContext?.correlationId,
    requestId: currentContext?.requestId,
    spanId: currentContext?.spanId,
    traceId: currentContext?.traceId,
    generateCorrelationContext,
    getCorrelationHeaders,
    
    // Alert thresholds
    alertThresholds,
    alertHistory,
    isAlertMonitoring,
    startAlertMonitoring,
    stopAlertMonitoring,
    updateThreshold,
    addThreshold,
    removeThreshold,
    
    // System status
    systemStatus
  }

  return (
    <ObservabilityContext.Provider value={contextValue}>
      {children}
    </ObservabilityContext.Provider>
  )
}

// Hook to use observability context
export function useHealthMonitoring() {
  const context = useContext(ObservabilityContext)
  if (context === undefined) {
    throw new Error('useHealthMonitoring must be used within an ObservabilityProvider')
  }
  return context
}

// Hook to use correlation ID
export function useObservabilityCorrelationID() {
  const context = useContext(ObservabilityContext)
  if (context === undefined) {
    throw new Error('useObservabilityCorrelationID must be used within an ObservabilityProvider')
  }
  return {
    correlationId: context.correlationId,
    requestId: context.requestId,
    spanId: context.spanId,
    traceId: context.traceId,
    generateCorrelationContext: context.generateCorrelationContext,
    getCorrelationHeaders: context.getCorrelationHeaders
  }
}

// Hook to use alert thresholds
export function useAlertThresholds() {
  const context = useContext(ObservabilityContext)
  if (context === undefined) {
    throw new Error('useAlertThresholds must be used within an ObservabilityProvider')
  }
  return {
    alertThresholds: context.alertThresholds,
    alertHistory: context.alertHistory,
    isAlertMonitoring: context.isAlertMonitoring,
    startAlertMonitoring: context.startAlertMonitoring,
    stopAlertMonitoring: context.stopAlertMonitoring,
    updateThreshold: context.updateThreshold,
    addThreshold: context.addThreshold,
    removeThreshold: context.removeThreshold
  }
}

// Hook to use system status
export function useSystemStatus() {
  const context = useContext(ObservabilityContext)
  if (context === undefined) {
    throw new Error('useSystemStatus must be used within an ObservabilityProvider')
  }
  return context.systemStatus
}
