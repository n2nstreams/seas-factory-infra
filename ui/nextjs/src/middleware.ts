import { NextRequest, NextResponse } from 'next/server';
import { canaryDeploymentService } from './lib/canary-deployment';

/**
 * Canary Deployment Middleware
 * Routes traffic between legacy and new systems based on canary configuration
 */

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Skip middleware for static assets and API routes
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.startsWith('/static') ||
    pathname.includes('.')
  ) {
    return NextResponse.next();
  }

  // Check if canary deployment is active
  const canaryStatus = canaryDeploymentService.getStatus();
  
  if (!canaryStatus.isActive || canaryStatus.rollbackTriggered) {
    // Canary is not active or rolled back - route to legacy
    return NextResponse.next();
  }

  // Get user identifier for consistent routing
  const userId = getUserId(request);
  
  // Check if user should be routed to canary
  const shouldRouteToCanary = canaryDeploymentService.shouldRouteToCanary(userId);
  
  if (shouldRouteToCanary && !pathname.startsWith('/app2')) {
    // Route to canary version
    const canaryUrl = new URL(`/app2${pathname}`, request.url);
    canaryUrl.search = request.nextUrl.search;
    
    const response = NextResponse.rewrite(canaryUrl);
    
    // Add canary headers
    response.headers.set('X-Canary-Version', 'v2');
    response.headers.set('X-Migration-Status', 'active');
    response.headers.set('X-Traffic-Percentage', canaryStatus.currentTrafficPercentage.toString());
    
    return response;
  }

  // Route to legacy version
  const response = NextResponse.next();
  response.headers.set('X-App-Version', 'legacy');
  response.headers.set('X-Canary-Version', 'v1');
  
  return response;
}

/**
 * Get user identifier from request
 */
function getUserId(request: NextRequest): string | undefined {
  // Try to get user ID from various sources
  const authHeader = request.headers.get('authorization');
  const cookieHeader = request.headers.get('cookie');
  const userIdHeader = request.headers.get('x-user-id');
  
  if (userIdHeader) {
    return userIdHeader;
  }
  
  if (authHeader && authHeader.startsWith('Bearer ')) {
    // Extract user ID from JWT token if possible
    const token = authHeader.substring(7);
    try {
      // Simple JWT payload extraction (in production, use proper JWT library)
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.sub || payload.userId;
    } catch {
      // Ignore JWT parsing errors
    }
  }
  
  if (cookieHeader) {
    // Try to extract user ID from cookies
    const cookies = cookieHeader.split(';').reduce((acc, cookie) => {
      const [key, value] = cookie.trim().split('=');
      acc[key] = value;
      return acc;
    }, {} as Record<string, string>);
    
    return cookies.userId || cookies.user_id || cookies.sub;
  }
  
  return undefined;
}

/**
 * Configure middleware matcher
 */
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - static files (images, etc.)
     */
    '/((?!api|_next/static|_next/image|favicon.ico|static|.*\\.).*)',
  ],
};
