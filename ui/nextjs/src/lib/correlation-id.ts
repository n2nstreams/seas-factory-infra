// Correlation ID service for request tracing and observability

// Configuration
const CORRELATION_ID_HEADER = process.env.NEXT_PUBLIC_CORRELATION_ID_HEADER || 'X-Correlation-ID'
const CORRELATION_ID_LENGTH = parseInt(process.env.NEXT_PUBLIC_CORRELATION_ID_LENGTH || '16', 10)

// Correlation ID interface
export interface CorrelationContext {
  id: string
  parentId?: string
  traceId?: string
  spanId?: string
  userId?: string
  sessionId?: string
  requestId?: string
  timestamp: string
  metadata: Record<string, any>
}

// Generate a unique correlation ID
export function generateCorrelationId(): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < CORRELATION_ID_LENGTH; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

// Generate a trace ID (longer, more unique identifier)
export function generateTraceId(): string {
  return generateCorrelationId() + generateCorrelationId()
}

// Generate a span ID (shorter identifier for individual operations)
export function generateSpanId(): string {
  return generateCorrelationId().substring(0, 8)
}

// Create a new correlation context
export function createCorrelationContext(
  parentContext?: Partial<CorrelationContext>,
  metadata: Record<string, any> = {}
): CorrelationContext {
  const now = new Date().toISOString()
  
  return {
    id: parentContext?.id || generateCorrelationId(),
    parentId: parentContext?.parentId,
    traceId: parentContext?.traceId || generateTraceId(),
    spanId: generateSpanId(),
    userId: parentContext?.userId,
    sessionId: parentContext?.sessionId,
    requestId: parentContext?.requestId || generateCorrelationId(),
    timestamp: now,
    metadata: {
      ...parentContext?.metadata,
      ...metadata,
      created_at: now,
    },
  }
}

// Extract correlation ID from headers
export function extractCorrelationId(headers: Headers | Record<string, string>): string | null {
  if (headers instanceof Headers) {
    return headers.get(CORRELATION_ID_HEADER) || null
  }
  return headers[CORRELATION_ID_HEADER] || null
}

// Add correlation ID to headers
export function addCorrelationId(
  headers: Headers | Record<string, string>,
  correlationId: string
): void {
  if (headers instanceof Headers) {
    headers.set(CORRELATION_ID_HEADER, correlationId)
  } else {
    headers[CORRELATION_ID_HEADER] = correlationId
  }
}

// Create headers with correlation ID
export function createHeadersWithCorrelation(
  correlationId: string,
  additionalHeaders: Record<string, string> = {}
): Record<string, string> {
  return {
    [CORRELATION_ID_HEADER]: correlationId,
    'Content-Type': 'application/json',
    ...additionalHeaders,
  }
}

// Create fetch options with correlation ID
export function createFetchOptionsWithCorrelation(
  correlationId: string,
  options: RequestInit = {}
): RequestInit {
  return {
    ...options,
    headers: {
      ...createHeadersWithCorrelation(correlationId),
      ...options.headers,
    },
  }
}

// Correlation context manager for React components
class CorrelationContextManager {
  private currentContext: CorrelationContext | null = null
  private listeners: Set<(context: CorrelationContext | null) => void> = new Set()

  // Set the current correlation context
  setContext(context: CorrelationContext): void {
    this.currentContext = context
    this.notifyListeners()
  }

  // Get the current correlation context
  getContext(): CorrelationContext | null {
    return this.currentContext
  }

  // Create a child context
  createChildContext(metadata: Record<string, any> = {}): CorrelationContext {
    if (!this.currentContext) {
      return createCorrelationContext({}, metadata)
    }
    
    return createCorrelationContext(this.currentContext, {
      ...metadata,
      parent_correlation_id: this.currentContext.id,
    })
  }

  // Update the current context with additional metadata
  updateContext(metadata: Record<string, any>): void {
    if (this.currentContext) {
      this.currentContext.metadata = {
        ...this.currentContext.metadata,
        ...metadata,
        updated_at: new Date().toISOString(),
      }
      this.notifyListeners()
    }
  }

  // Clear the current context
  clearContext(): void {
    this.currentContext = null
    this.notifyListeners()
  }

  // Subscribe to context changes
  subscribe(listener: (context: CorrelationContext | null) => void): () => void {
    this.listeners.add(listener)
    return () => {
      this.listeners.delete(listener)
    }
  }

  // Notify all listeners of context changes
  private notifyListeners(): void {
    this.listeners.forEach(listener => {
      try {
        listener(this.currentContext)
      } catch (error) {
        console.error('Error in correlation context listener:', error)
      }
    })
  }
}

// Export singleton instance
export const correlationManager = new CorrelationContextManager()

// Utility function to log with correlation context
export function logWithCorrelation(
  level: 'info' | 'warn' | 'error' | 'debug',
  message: string,
  data?: any
): void {
  const context = correlationManager.getContext()
  const logData = {
    message,
    data,
    correlation_id: context?.id,
    trace_id: context?.traceId,
    span_id: context?.spanId,
    timestamp: new Date().toISOString(),
  }

  switch (level) {
    case 'info':
      console.info('📊', logData)
      break
    case 'warn':
      console.warn('⚠️', logData)
      break
    case 'error':
      console.error('❌', logData)
      break
    case 'debug':
      console.debug('🔍', logData)
      break
  }
}

// Utility function to create a correlation-aware fetch wrapper
export function createCorrelationAwareFetch(): typeof fetch {
  return async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    const context = correlationManager.getContext()
    
    if (context) {
      const options = createFetchOptionsWithCorrelation(context.id, init)
      
      // Log the request
      logWithCorrelation('info', 'API Request', {
        url: typeof input === 'string' ? input : input.toString(),
        method: options.method || 'GET',
        correlation_id: context.id,
      })
      
      try {
        const response = await fetch(input, options)
        
        // Log the response
        logWithCorrelation('info', 'API Response', {
          url: typeof input === 'string' ? input : input.toString(),
          status: response.status,
          statusText: response.statusText,
          correlation_id: context.id,
        })
        
        return response
      } catch (error) {
        // Log the error
        logWithCorrelation('error', 'API Request Failed', {
          url: typeof input === 'string' ? input : input.toString(),
          error: error instanceof Error ? error.message : String(error),
          correlation_id: context.id,
        })
        
        throw error
      }
    }
    
    // Fallback to regular fetch if no correlation context
    return fetch(input, init)
  }
}

// Export the correlation-aware fetch function
export const correlationAwareFetch = createCorrelationAwareFetch()

// Utility function to wrap async operations with correlation context
export function withCorrelationContext<T>(
  operation: () => Promise<T>,
  metadata: Record<string, any> = {}
): Promise<T> {
  const childContext = correlationManager.createChildContext(metadata)
  correlationManager.setContext(childContext)
  
  return operation().finally(() => {
    // Restore parent context if it exists
    if (childContext.parentId) {
      const parentContext = correlationManager.getContext()
      if (parentContext && parentContext.id === childContext.parentId) {
        correlationManager.setContext(parentContext)
      }
    }
  })
}

// Export types for external use
export type { CorrelationContext }
