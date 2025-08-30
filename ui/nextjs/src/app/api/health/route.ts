import { NextRequest, NextResponse } from 'next/server'
import { healthMonitoring } from '@/lib/health-monitoring-simple'

// GET /api/health - Health check endpoint
export async function GET(request: NextRequest) {
  const startTime = Date.now()
  
  try {
    // Extract correlation ID from request headers
    const correlationId = request.headers.get('X-Correlation-ID') || request.headers.get('x-correlation-id')
    
    // Run comprehensive health check
    const healthResult = await healthMonitoring.runComprehensiveHealthCheck()
    
    const responseTime = Date.now() - startTime
    
    // Add response metadata
    const response = {
      ...healthResult,
      responseTime,
      correlationId: correlationId || 'generated-' + Math.random().toString(36).substr(2, 9),
      requestHeaders: {
        'user-agent': request.headers.get('user-agent'),
        'accept': request.headers.get('accept'),
        'host': request.headers.get('host')
      }
    }

    // Build response headers with exact case expected by verification script
    const responseHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'X-Response-Time': `${responseTime}ms`
    }

    // Always include the correlation ID in response headers with exact case
    if (correlationId) {
      responseHeaders['X-Correlation-ID'] = correlationId
    }

    return NextResponse.json(response, {
      status: 200,
      headers: responseHeaders
    })
  } catch (error) {
    const responseTime = Date.now() - startTime
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    const correlationId = request.headers.get('X-Correlation-ID') || request.headers.get('x-correlation-id')

    // Build error response headers
    const responseHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      'X-Response-Time': `${responseTime}ms`
    }

    // Include correlation ID in error response headers with exact case
    if (correlationId) {
      responseHeaders['X-Correlation-ID'] = correlationId
    }

    return NextResponse.json(
      {
        status: 'unhealthy',
        error: errorMessage,
        responseTime,
        timestamp: new Date().toISOString(),
        correlationId: correlationId || 'error-' + Math.random().toString(36).substr(2, 9),
        metadata: {
          service: 'AI SaaS Factory - Next.js Frontend',
          region: 'local',
          instance: 'localhost',
          build: 'local',
          commit: 'local'
        }
      },
      {
        status: 503,
        headers: responseHeaders
      }
    )
  }
}

// HEAD /api/health - Lightweight health check (no body)
export async function HEAD(request: NextRequest) {
  try {
    const correlationId = request.headers.get('X-Correlation-ID') || request.headers.get('x-correlation-id')
    
    // Quick health check - just return basic status
    const currentHealth = healthMonitoring.getCurrentHealth()
    
    // Build response headers
    const responseHeaders: Record<string, string> = {
      'X-Timestamp': new Date().toISOString()
    }

    // Include correlation ID in response headers with exact case
    if (correlationId) {
      responseHeaders['X-Correlation-ID'] = correlationId
    }
    
    if (currentHealth && currentHealth.status === 'healthy') {
      responseHeaders['X-Health-Status'] = 'healthy'
      return new NextResponse(null, {
        status: 200,
        headers: responseHeaders
      })
    } else {
      responseHeaders['X-Health-Status'] = 'unhealthy'
      return new NextResponse(null, {
        status: 503,
        headers: responseHeaders
      })
    }
  } catch (error) {
    const correlationId = request.headers.get('X-Correlation-ID') || request.headers.get('x-correlation-id')
    
    // Build error response headers
    const responseHeaders: Record<string, string> = {
      'X-Health-Status': 'error',
      'X-Timestamp': new Date().toISOString()
    }

    // Include correlation ID in error response headers with exact case
    if (correlationId) {
      responseHeaders['X-Correlation-ID'] = correlationId
    }
    
    return new NextResponse(null, {
      status: 503,
      headers: responseHeaders
    })
  }
} 
