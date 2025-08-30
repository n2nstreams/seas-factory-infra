import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  
  // Performance Monitoring
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
  
  // Environment
  environment: process.env.NODE_ENV || 'development',
  
  // Release tracking
  release: process.env.npm_package_version || '0.1.0',
  
  // Before send hook to filter sensitive data
  beforeSend(event) {
    // Filter out health check errors
    if (event.request?.url?.includes('/api/health')) {
      return null
    }
    
    // Filter out development errors in production
    if (process.env.NODE_ENV === 'production' && event.exception) {
      const errorMessage = event.exception.values?.[0]?.value || ''
      if (errorMessage.includes('development') || errorMessage.includes('localhost')) {
        return null
      }
    }
    
    return event
  },
  
  // Integrations
  integrations: [
    Sentry.nodeProfilingIntegration(),
  ],
  
  // Debug mode in development
  debug: process.env.NODE_ENV === 'development',
})
