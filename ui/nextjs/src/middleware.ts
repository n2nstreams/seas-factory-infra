import { NextRequest, NextResponse } from 'next/server'
import { correlationIDManager } from './lib/correlation-id'

export function middleware(request: NextRequest) {
  // Extract correlation ID from incoming request headers
  const headers = Object.fromEntries(request.headers.entries())
  const correlationContext = correlationIDManager.extractFromHeaders(headers)
  
  // If no correlation context exists, create one
  if (!correlationContext) {
    correlationIDManager.generateContext(
      undefined,
      undefined,
      undefined,
      undefined,
      { 
        operation: 'http_request', 
        path: request.nextUrl.pathname,
        method: request.method,
        userAgent: headers['user-agent'],
        referer: headers['referer']
      }
    )
  }

  // Clone the request headers to add correlation IDs
  const requestHeaders = new Headers(request.headers)
  const correlationHeaders = correlationIDManager.getHeaders()
  
  // Add correlation headers to the request
  Object.entries(correlationHeaders).forEach(([key, value]) => {
    if (value) {
      requestHeaders.set(key, value)
    }
  })

  // Create a new request with correlation headers
  const enhancedRequest = new NextRequest(request, {
    headers: requestHeaders
  })

  // Process the request
  const response = NextResponse.next({
    request: enhancedRequest
  })

  // Add correlation headers to the response
  Object.entries(correlationHeaders).forEach(([key, value]) => {
    if (value) {
      response.headers.set(key, value)
    }
  })

  // Add additional response headers for tracking
  response.headers.set('X-Request-ID', correlationIDManager.getCurrentContext()?.requestId || '')
  response.headers.set('X-Span-ID', correlationIDManager.getCurrentContext()?.spanId || '')
  response.headers.set('X-Trace-ID', correlationIDManager.getCurrentContext()?.traceId || '')

  // Log the request with correlation context
  const currentContext = correlationIDManager.getCurrentContext()
  if (currentContext) {
    // Only log for non-asset requests to avoid noise
    if (!request.nextUrl.pathname.startsWith('/_next/') && 
        !request.nextUrl.pathname.startsWith('/favicon.ico') &&
        !request.nextUrl.pathname.startsWith('/api/health')) {
      correlationIDManager.logContext(currentContext, 'info')
    }
  }

  return response
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}
