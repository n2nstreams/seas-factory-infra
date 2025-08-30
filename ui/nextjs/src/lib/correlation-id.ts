import { v4 as uuidv4 } from 'uuid'

// Correlation ID context for request tracing
export interface CorrelationContext {
  correlationId: string
  requestId: string
  parentId?: string
  spanId: string
  traceId: string
  userId?: string
  tenantId?: string
  sessionId?: string
  timestamp: number
  metadata: Record<string, any>
}

// Global correlation context
let globalCorrelationContext: CorrelationContext | null = null

// Correlation ID manager
export class CorrelationIDManager {
  private static instance: CorrelationIDManager
  private contextMap = new Map<string, CorrelationContext>()

  static getInstance(): CorrelationIDManager {
    if (!CorrelationIDManager.instance) {
      CorrelationIDManager.instance = new CorrelationIDManager()
    }
    return CorrelationIDManager.instance
  }

  // Generate a new correlation context
  generateContext(
    parentId?: string,
    userId?: string,
    tenantId?: string,
    sessionId?: string,
    metadata: Record<string, any> = {}
  ): CorrelationContext {
    const correlationId = uuidv4()
    const requestId = uuidv4()
    const spanId = uuidv4()
    const traceId = parentId || uuidv4()

    const context: CorrelationContext = {
      correlationId,
      requestId,
      parentId,
      spanId,
      traceId,
      userId,
      tenantId,
      sessionId,
      timestamp: Date.now(),
      metadata: {
        service: 'frontend',
        version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
        environment: process.env.NODE_ENV || 'development',
        ...metadata
      }
    }

    this.contextMap.set(correlationId, context)
    globalCorrelationContext = context

    return context
  }

  // Get current correlation context
  getCurrentContext(): CorrelationContext | null {
    return globalCorrelationContext
  }

  // Get context by correlation ID
  getContext(correlationId: string): CorrelationContext | null {
    return this.contextMap.get(correlationId) || null
  }

  // Set current context
  setCurrentContext(context: CorrelationContext): void {
    globalCorrelationContext = context
    this.contextMap.set(context.correlationId, context)
  }

  // Clear current context
  clearCurrentContext(): void {
    globalCorrelationContext = null
  }

  // Propagate correlation ID to headers
  getHeaders(): Record<string, string> {
    const context = this.getCurrentContext()
    if (!context) return {}

    return {
      'X-Correlation-ID': context.correlationId,
      'X-Request-ID': context.requestId,
      'X-Span-ID': context.spanId,
      'X-Trace-ID': context.traceId,
      'X-Parent-ID': context.parentId || '',
      'X-User-ID': context.userId || '',
      'X-Tenant-ID': context.tenantId || '',
      'X-Session-ID': context.sessionId || '',
      'X-Timestamp': context.timestamp.toString(),
      'X-Service': context.metadata.service || 'frontend'
    }
  }

  // Extract correlation ID from headers
  extractFromHeaders(headers: Record<string, string>): CorrelationContext | null {
    const correlationId = headers['x-correlation-id'] || headers['X-Correlation-ID']
    if (!correlationId) return null

    // Check if we already have this context
    const existingContext = this.getContext(correlationId)
    if (existingContext) {
      this.setCurrentContext(existingContext)
      return existingContext
    }

    // Create new context from headers, preserving the incoming correlation ID
    const newContext: CorrelationContext = {
      correlationId: correlationId, // Use the incoming correlation ID exactly
      requestId: headers['x-request-id'] || headers['X-Request-ID'] || uuidv4(),
      parentId: headers['x-parent-id'] || headers['X-Parent-ID'] || undefined,
      spanId: headers['x-span-id'] || headers['X-Span-ID'] || uuidv4(),
      traceId: headers['x-trace-id'] || headers['X-Trace-ID'] || correlationId,
      userId: headers['x-user-id'] || headers['X-User-ID'] || undefined,
      tenantId: headers['x-tenant-id'] || headers['X-Tenant-ID'] || undefined,
      sessionId: headers['x-session-id'] || headers['X-Session-ID'] || undefined,
      timestamp: parseInt(headers['x-timestamp'] || headers['X-Timestamp'] || Date.now().toString()),
      metadata: {
        service: headers['x-service'] || headers['X-Service'] || 'unknown',
        version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
        environment: process.env.NODE_ENV || 'development'
      }
    }

    // Store and set as current context
    this.contextMap.set(correlationId, newContext)
    this.setCurrentContext(newContext)
    
    return newContext
  }

  // Create child span
  createChildSpan(metadata: Record<string, any> = {}): CorrelationContext {
    const parentContext = this.getCurrentContext()
    if (!parentContext) {
      return this.generateContext(undefined, undefined, undefined, undefined, metadata)
    }

    const childContext: CorrelationContext = {
      ...parentContext,
      requestId: uuidv4(),
      spanId: uuidv4(),
      parentId: parentContext.spanId,
      timestamp: Date.now(),
      metadata: {
        ...parentContext.metadata,
        ...metadata,
        parentSpanId: parentContext.spanId
      }
    }

    this.contextMap.set(childContext.correlationId, childContext)
    return childContext
  }

  // Log correlation context
  logContext(context: CorrelationContext, level: 'info' | 'warn' | 'error' = 'info'): void {
    const logData = {
      level,
      correlationId: context.correlationId,
      requestId: context.requestId,
      spanId: context.spanId,
      traceId: context.traceId,
      parentId: context.parentId,
      userId: context.userId,
      tenantId: context.tenantId,
      sessionId: context.sessionId,
      timestamp: context.timestamp,
      metadata: context.metadata
    }

    switch (level) {
      case 'error':
        console.error('🔗 Correlation Context:', logData)
        break
      case 'warn':
        console.warn('🔗 Correlation Context:', logData)
        break
      default:
        console.log('🔗 Correlation Context:', logData)
    }
  }

  // Get all contexts for a trace
  getTraceContexts(traceId: string): CorrelationContext[] {
    return Array.from(this.contextMap.values()).filter(context => context.traceId === traceId)
  }

  // Clean up old contexts (older than 1 hour)
  cleanup(): void {
    const oneHourAgo = Date.now() - (60 * 60 * 1000)
    for (const [correlationId, context] of this.contextMap.entries()) {
      if (context.timestamp < oneHourAgo) {
        this.contextMap.delete(correlationId)
      }
    }
  }
}

// Export singleton instance
export const correlationIDManager = CorrelationIDManager.getInstance()

// React hook for correlation ID
export function useCorrelationID() {
  const context = correlationIDManager.getCurrentContext()
  
  const generateNew = (
    parentId?: string,
    userId?: string,
    tenantId?: string,
    sessionId?: string,
    metadata?: Record<string, any>
  ) => {
    return correlationIDManager.generateContext(parentId, userId, tenantId, sessionId, metadata)
  }

  const getHeaders = () => correlationIDManager.getHeaders()
  const logContext = (level: 'info' | 'warn' | 'error' = 'info') => {
    if (context) correlationIDManager.logContext(context, level)
  }

  return {
    context,
    generateNew,
    getHeaders,
    logContext,
    correlationId: context?.correlationId,
    requestId: context?.requestId,
    spanId: context?.spanId,
    traceId: context?.traceId
  }
}

// Utility function to add correlation headers to fetch requests
export function fetchWithCorrelation(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const headers = correlationIDManager.getHeaders()
  
  const enhancedOptions: RequestInit = {
    ...options,
    headers: {
      ...headers,
      ...options.headers
    }
  }

  return fetch(url, enhancedOptions)
}

// Utility function to add correlation headers to axios requests
export function getCorrelationHeaders(): Record<string, string> {
  return correlationIDManager.getHeaders()
}

// Auto-cleanup every hour
if (typeof window !== 'undefined') {
  setInterval(() => {
    correlationIDManager.cleanup()
  }, 60 * 60 * 1000) // 1 hour
}
