import { NextRequest, NextResponse } from 'next/server'
import { healthMonitoring } from '@/lib/health-monitoring-simple'

// Health check response interface
interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy'
  timestamp: string
  version: string
  environment: string
  uptime: number
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
    overallHealth: number
  }
  metadata: {
    service: string
    region?: string
    instance?: string
    build?: string
    commit?: string
  }
}

// GET /api/health - Health check endpoint
export async function GET(request: NextRequest) {
  const startTime = Date.now()
  
  try {
    // Get correlation ID from headers if present
    const correlationId = request.headers.get('X-Correlation-ID')
    
    // Run health check
    const healthResult = await healthMonitoring.runHealthCheck()
    
    // Calculate response time
    const responseTime = Date.now() - startTime
    
    // Prepare response
    const response: HealthResponse = {
      status: healthResult.status,
      timestamp: healthResult.timestamp,
      version: process.env.npm_package_version || '0.1.0',
      environment: process.env.NODE_ENV || 'development',
      uptime: process.uptime ? Math.floor(process.uptime()) : 0,
      checks: healthResult.checks,
      summary: healthResult.summary,
      metadata: {
        service: 'AI SaaS Factory - Next.js Frontend',
        region: process.env.VERCEL_REGION || 'local',
        instance: process.env.VERCEL_URL ? new URL(process.env.VERCEL_URL).hostname : 'localhost',
        build: process.env.VERCEL_GIT_COMMIT_SHA || 'local',
        commit: process.env.VERCEL_GIT_COMMIT_SHA || 'local',
      },
    }
    
    // Set response headers
    const headers = new Headers()
    headers.set('Content-Type', 'application/json')
    headers.set('Cache-Control', 'no-cache, no-store, must-revalidate')
    headers.set('Pragma', 'no-cache')
    headers.set('Expires', '0')
    
    // Add correlation ID to response if present
    if (correlationId) {
      headers.set('X-Correlation-ID', correlationId)
    }
    
    // Add response time header
    headers.set('X-Response-Time', `${responseTime}ms`)
    
    // Return response with appropriate status code
    const statusCode = healthResult.status === 'healthy' ? 200 : 
                      healthResult.status === 'degraded' ? 200 : 503
    
    return NextResponse.json(response, {
      status: statusCode,
      headers,
    })
    
  } catch (error) {
    // Handle errors gracefully
    const errorResponse = {
      status: 'unhealthy' as const,
      timestamp: new Date().toISOString(),
      version: process.env.npm_package_version || '0.1.0',
      environment: process.env.NODE_ENV || 'development',
      uptime: process.uptime ? Math.floor(process.uptime()) : 0,
      error: error instanceof Error ? error.message : 'Unknown error occurred',
      checks: {},
      summary: {
        totalChecks: 0,
        passedChecks: 0,
        failedChecks: 1,
        warningChecks: 0,
        overallHealth: 0,
      },
      metadata: {
        service: 'AI SaaS Factory - Next.js Frontend',
        region: process.env.VERCEL_REGION || 'local',
        instance: process.env.VERCEL_URL ? new URL(process.env.VERCEL_URL).hostname : 'localhost',
        build: process.env.VERCEL_GIT_COMMIT_SHA || 'local',
        commit: process.env.VERCEL_GIT_COMMIT_SHA || 'local',
      },
    }
    
    const headers = new Headers()
    headers.set('Content-Type', 'application/json')
    headers.set('Cache-Control', 'no-cache, no-store, must-revalidate')
    
    // Add correlation ID to response if present
    const correlationId = request.headers.get('X-Correlation-ID')
    if (correlationId) {
      headers.set('X-Correlation-ID', correlationId)
    }
    
    return NextResponse.json(errorResponse, {
      status: 503, // Service Unavailable
      headers,
    })
  }
}

// HEAD /api/health - Lightweight health check (no body)
export async function HEAD(request: NextRequest) {
  try {
    // Run a quick health check
    const healthResult = await healthMonitoring.runHealthCheck()
    
    // Set response headers
    const headers = new Headers()
    headers.set('Content-Type', 'application/json')
    headers.set('Cache-Control', 'no-cache, no-store, must-revalidate')
    headers.set('Pragma', 'no-cache')
    headers.set('Expires', '0')
    
    // Add correlation ID to response if present
    const correlationId = request.headers.get('X-Correlation-ID')
    if (correlationId) {
      headers.set('X-Correlation-ID', correlationId)
    }
    
    // Add health status header
    headers.set('X-Health-Status', healthResult.status)
    headers.set('X-Health-Score', healthResult.summary.overallHealth.toString())
    
    // Return response with appropriate status code
    const statusCode = healthResult.status === 'healthy' ? 200 : 
                      healthResult.status === 'degraded' ? 200 : 503
    
    return new NextResponse(null, {
      status: statusCode,
      headers,
    })
    
  } catch (error) {
    // Handle errors gracefully
    const headers = new Headers()
    headers.set('Content-Type', 'application/json')
    headers.set('Cache-Control', 'no-cache, no-store, must-revalidate')
    headers.set('X-Health-Status', 'unhealthy')
    headers.set('X-Health-Score', '0')
    
    // Add correlation ID to response if present
    const correlationId = request.headers.get('X-Correlation-ID')
    if (correlationId) {
      headers.set('X-Correlation-ID', correlationId)
    }
    
    return new NextResponse(null, {
      status: 503, // Service Unavailable
      headers,
    })
  }
}

// OPTIONS /api/health - CORS preflight
export async function OPTIONS(request: NextRequest) {
  const headers = new Headers()
  headers.set('Access-Control-Allow-Origin', '*')
  headers.set('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
  headers.set('Access-Control-Allow-Headers', 'Content-Type, X-Correlation-ID')
  headers.set('Access-Control-Max-Age', '86400')
  
  return new NextResponse(null, {
    status: 200,
    headers,
  })
}
