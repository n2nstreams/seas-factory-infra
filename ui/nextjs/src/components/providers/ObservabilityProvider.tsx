'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useFeatureFlags } from './FeatureFlagProvider'
import { healthMonitoring, type HealthCheckResult, type HealthIndexMetrics } from '@/lib/health-monitoring-simple'
import { correlationManager, createCorrelationContext, type CorrelationContext } from '@/lib/correlation-id'

// Observability context interface
interface ObservabilityContextType {
  // Health monitoring
  currentHealth: HealthCheckResult | null
  healthHistory: HealthCheckResult[]
  metricsHistory: HealthIndexMetrics[]
  isMonitoring: boolean
  startMonitoring: (intervalMs?: number) => Promise<void>
  stopMonitoring: () => void
  runHealthCheck: () => Promise<HealthCheckResult>
  
  // Correlation IDs
  correlationContext: CorrelationContext | null
  createCorrelationContext: (metadata?: Record<string, any>) => CorrelationContext
  updateCorrelationContext: (metadata: Record<string, any>) => void
  clearCorrelationContext: () => void
  
  // Feature flags
  isSentryEnabled: boolean
  isVercelAnalyticsEnabled: boolean
  isHealthMonitoringEnabled: boolean
  
  // Error tracking
  captureError: (error: Error, context?: Record<string, any>) => void
  captureMessage: (message: string, level?: 'info' | 'warn' | 'error') => void
  
  // Performance monitoring
  startTransaction: (name: string, operation: string) => void
  endTransaction: (name: string, status?: 'success' | 'error') => void
}

const ObservabilityContext = createContext<ObservabilityContextType | undefined>(undefined)

// Observability provider component
export function ObservabilityProvider({ children }: { children: ReactNode }) {
  const { isEnabled } = useFeatureFlags()
  
  // Feature flags for observability
  const isSentryEnabled = isEnabled('observability_v2') && isEnabled('sentry_enabled')
  const isVercelAnalyticsEnabled = isEnabled('observability_v2') && isEnabled('vercel_analytics_enabled')
  const isHealthMonitoringEnabled = isEnabled('observability_v2') && isEnabled('health_monitoring_enabled')
  
  // State for health monitoring
  const [currentHealth, setCurrentHealth] = useState<HealthCheckResult | null>(null)
  const [healthHistory, setHealthHistory] = useState<HealthCheckResult[]>([])
  const [metricsHistory, setMetricsHistory] = useState<HealthIndexMetrics[]>([])
  const [isMonitoring, setIsMonitoring] = useState(false)
  
  // State for correlation context
  const [correlationContext, setCorrelationContext] = useState<CorrelationContext | null>(null)
  
  // Initialize observability when component mounts
  useEffect(() => {
    if (isHealthMonitoringEnabled) {
      initializeHealthMonitoring()
    }
    
    if (isSentryEnabled) {
      initializeSentry()
    }
    
    if (isVercelAnalyticsEnabled) {
      initializeVercelAnalytics()
    }
    
    // Initialize correlation context
    initializeCorrelationContext()
    
    // Cleanup on unmount
    return () => {
      if (isHealthMonitoringEnabled) {
        healthMonitoring.stopMonitoring()
      }
    }
  }, [isHealthMonitoringEnabled, isSentryEnabled, isVercelAnalyticsEnabled])
  
  // Initialize health monitoring
  const initializeHealthMonitoring = async () => {
    try {
      // Subscribe to health monitoring updates
      const updateHealth = () => {
        const current = healthMonitoring.getCurrentHealth()
        const history = healthMonitoring.getHealthHistory()
        const metrics = healthMonitoring.getMetricsHistory()
        
        setCurrentHealth(current)
        setHealthHistory(history)
        setMetricsHistory(metrics)
        setIsMonitoring(healthMonitoring.isMonitoringActive())
      }
      
      // Initial update
      updateHealth()
      
      // Start monitoring if not already running
      if (!healthMonitoring.isMonitoringActive()) {
        await healthMonitoring.startMonitoring()
        updateHealth()
      }
      
      // Set up periodic updates
      const interval = setInterval(updateHealth, 10000) // Update every 10 seconds
      
      return () => clearInterval(interval)
    } catch (error) {
      console.error('Failed to initialize health monitoring:', error)
    }
  }
  
  // Initialize Sentry
  const initializeSentry = () => {
    try {
      // Sentry is initialized via sentry.client.config.ts
      console.log('Sentry initialized for client-side error tracking')
    } catch (error) {
      console.error('Failed to initialize Sentry:', error)
    }
  }
  
  // Initialize Vercel Analytics
  const initializeVercelAnalytics = () => {
    try {
      // Vercel Analytics is initialized via the Analytics component in layout
      console.log('Vercel Analytics initialized')
    } catch (error) {
      console.error('Failed to initialize Vercel Analytics:', error)
    }
  }
  
  // Initialize correlation context
  const initializeCorrelationContext = () => {
    try {
      // Create initial correlation context
      const context = createCorrelationContext({}, {
        component: 'ObservabilityProvider',
        initialized_at: new Date().toISOString(),
      })
      
      correlationManager.setContext(context)
      setCorrelationContext(context)
      
      // Subscribe to correlation context changes
      const unsubscribe = correlationManager.subscribe((newContext) => {
        setCorrelationContext(newContext)
      })
      
      return unsubscribe
    } catch (error) {
      console.error('Failed to initialize correlation context:', error)
    }
  }
  
  // Health monitoring functions
  const startMonitoring = async (intervalMs: number = 30000) => {
    try {
      await healthMonitoring.startMonitoring(intervalMs)
      setIsMonitoring(true)
    } catch (error) {
      console.error('Failed to start health monitoring:', error)
    }
  }
  
  const stopMonitoring = () => {
    try {
      healthMonitoring.stopMonitoring()
      setIsMonitoring(false)
    } catch (error) {
      console.error('Failed to stop health monitoring:', error)
    }
  }
  
  const runHealthCheck = async (): Promise<HealthCheckResult> => {
    try {
      const result = await healthMonitoring.runHealthCheck()
      
      // Update state with new health check result
      setCurrentHealth(result)
      setHealthHistory(healthMonitoring.getHealthHistory())
      setMetricsHistory(healthMonitoring.getMetricsHistory())
      
      return result
    } catch (error) {
      console.error('Failed to run health check:', error)
      throw error
    }
  }
  
  // Correlation context functions
  const createNewCorrelationContext = (metadata: Record<string, any> = {}): CorrelationContext => {
    try {
      const context = correlationManager.createChildContext(metadata)
      return context
    } catch (error) {
      console.error('Failed to create correlation context:', error)
      // Return a fallback context
      return createCorrelationContext({}, metadata)
    }
  }
  
  const updateCorrelationContext = (metadata: Record<string, any>) => {
    try {
      correlationManager.updateContext(metadata)
    } catch (error) {
      console.error('Failed to update correlation context:', error)
    }
  }
  
  const clearCorrelationContext = () => {
    try {
      correlationManager.clearContext()
    } catch (error) {
      console.error('Failed to clear correlation context:', error)
    }
  }
  
  // Error tracking functions
  const captureError = (error: Error, context?: Record<string, any>) => {
    try {
      if (isSentryEnabled && typeof window !== 'undefined') {
        // Import Sentry dynamically to avoid SSR issues
        import('@sentry/nextjs').then((Sentry) => {
          Sentry.captureException(error, {
            extra: {
              ...context,
              correlation_id: correlationContext?.id,
              trace_id: correlationContext?.traceId,
              span_id: correlationContext?.spanId,
            },
          })
        })
      }
      
      // Always log to console for development
      console.error('Error captured:', error, context)
    } catch (err) {
      console.error('Failed to capture error:', err)
    }
  }
  
  const captureMessage = (message: string, level: 'info' | 'warn' | 'error' = 'info') => {
    try {
      if (isSentryEnabled && typeof window !== 'undefined') {
        import('@sentry/nextjs').then((Sentry) => {
          Sentry.captureMessage(message, {
            level: level === 'info' ? 'info' : level === 'warn' ? 'warning' : 'error',
            extra: {
              correlation_id: correlationContext?.id,
              trace_id: correlationContext?.traceId,
              span_id: correlationContext?.spanId,
            },
          })
        })
      }
      
      // Always log to console for development
      const logLevel = level === 'info' ? 'info' : level === 'warn' ? 'warn' : 'error'
      console[logLevel]('Message captured:', message)
    } catch (err) {
      console.error('Failed to capture message:', err)
    }
  }
  
  // Performance monitoring functions
  const startTransaction = (name: string, operation: string) => {
    try {
      if (isSentryEnabled && typeof window !== 'undefined') {
        import('@sentry/nextjs').then((Sentry) => {
          const transaction = Sentry.startTransaction({
            name,
            op: operation,
          })
          
          Sentry.getCurrentHub().configureScope((scope) => {
            scope.setSpan(transaction)
          })
          
          // Store transaction reference for later use
          ;(window as any).__currentTransaction = transaction
        })
      }
      
      // Log transaction start
      console.log('Transaction started:', name, operation)
    } catch (err) {
      console.error('Failed to start transaction:', err)
    }
  }
  
  const endTransaction = (name: string, status: 'success' | 'error' = 'success') => {
    try {
      if (isSentryEnabled && typeof window !== 'undefined') {
        import('@sentry/nextjs').then((Sentry) => {
          const transaction = (window as any).__currentTransaction
          if (transaction) {
            transaction.setStatus(status)
            transaction.finish()
            ;(window as any).__currentTransaction = null
          }
        })
      }
      
      // Log transaction end
      console.log('Transaction ended:', name, status)
    } catch (err) {
      console.error('Failed to end transaction:', err)
    }
  }
  
  // Context value
  const value: ObservabilityContextType = {
    // Health monitoring
    currentHealth,
    healthHistory,
    metricsHistory,
    isMonitoring,
    startMonitoring,
    stopMonitoring,
    runHealthCheck,
    
    // Correlation IDs
    correlationContext,
    createCorrelationContext: createNewCorrelationContext,
    updateCorrelationContext,
    clearCorrelationContext,
    
    // Feature flags
    isSentryEnabled,
    isVercelAnalyticsEnabled,
    isHealthMonitoringEnabled,
    
    // Error tracking
    captureError,
    captureMessage,
    
    // Performance monitoring
    startTransaction,
    endTransaction,
  }
  
  return (
    <ObservabilityContext.Provider value={value}>
      {children}
    </ObservabilityContext.Provider>
  )
}

// Hook to use observability context
export function useObservability() {
  const context = useContext(ObservabilityContext)
  if (context === undefined) {
    throw new Error('useObservability must be used within an ObservabilityProvider')
  }
  return context
}

// Hook for specific observability features
export function useHealthMonitoring() {
  const { 
    currentHealth, 
    healthHistory, 
    metricsHistory, 
    isMonitoring, 
    startMonitoring, 
    stopMonitoring, 
    runHealthCheck 
  } = useObservability()
  
  return {
    currentHealth,
    healthHistory,
    metricsHistory,
    isMonitoring,
    startMonitoring,
    stopMonitoring,
    runHealthCheck,
  }
}

export function useCorrelationContext() {
  const { 
    correlationContext, 
    createCorrelationContext, 
    updateCorrelationContext, 
    clearCorrelationContext 
  } = useObservability()
  
  return {
    correlationContext,
    createCorrelationContext,
    updateCorrelationContext,
    clearCorrelationContext,
  }
}

export function useErrorTracking() {
  const { captureError, captureMessage } = useObservability()
  
  return {
    captureError,
    captureMessage,
  }
}

export function usePerformanceMonitoring() {
  const { startTransaction, endTransaction } = useObservability()
  
  return {
    startTransaction,
    endTransaction,
  }
}
