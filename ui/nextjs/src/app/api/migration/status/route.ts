import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'
import { backendFeatureFlags, getBackendMigrationStatus } from '@/lib/feature-flags'

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
const supabase = createClient(supabaseUrl, supabaseServiceKey)

// GET /api/migration/status - Get backend migration status
export async function GET(request: NextRequest) {
  try {
    const tenantId = request.headers.get('X-Tenant-ID')
    
    if (!tenantId) {
      return NextResponse.json({
        success: false,
        error: 'Tenant ID is required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Get feature flag status
    const featureFlags = backendFeatureFlags.getAllFlags()
    const migrationStatus = getBackendMigrationStatus()
    const validation = backendFeatureFlags.validateMigrationSequence()

    // Check Supabase connectivity
    let supabaseHealth = 'unknown'
    try {
      const { data, error } = await supabase
        .from('tenants')
        .select('id')
        .eq('tenant_id', tenantId)
        .limit(1)
      
      if (error) {
        supabaseHealth = 'unhealthy'
      } else {
        supabaseHealth = 'healthy'
      }
    } catch (error) {
      supabaseHealth = 'unhealthy'
    }

    // Legacy backend health check - PERMANENTLY DISABLED for Module 5
    // All functionality now runs on Next.js + Supabase
    const legacyBackendHealth = 'permanently_disabled'

    // Get API endpoint status
    const apiEndpoints = [
      { name: 'users', path: '/api/users', enabled: featureFlags.users_api_nextjs },
      { name: 'privacy', path: '/api/privacy', enabled: featureFlags.privacy_api_nextjs },
      { name: 'admin', path: '/api/admin', enabled: featureFlags.admin_api_nextjs },
      { name: 'ideas', path: '/api/ideas', enabled: featureFlags.ideas_api_nextjs },
      { name: 'projects', path: '/api/projects', enabled: featureFlags.projects_api_nextjs },
      { name: 'websocket', path: '/api/websocket', enabled: featureFlags.websocket_nextjs }
    ]

    // Test each enabled API endpoint
    const apiStatus = await Promise.all(
      apiEndpoints.map(async (endpoint) => {
        if (!endpoint.enabled) {
          return {
            name: endpoint.name,
            path: endpoint.path,
            enabled: false,
            status: 'disabled',
            responseTime: null,
            error: null
          }
        }

        try {
          const startTime = Date.now()
          // Use relative URL for local API calls (not Supabase URL)
          const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:3000'
          const response = await fetch(`${baseUrl}${endpoint.path}`, {
            method: 'GET',
            headers: { 'X-Tenant-ID': tenantId },
            signal: AbortSignal.timeout(5000)
          })
          const responseTime = Date.now() - startTime

          return {
            name: endpoint.name,
            path: endpoint.path,
            enabled: true,
            status: response.ok ? 'healthy' : 'unhealthy',
            responseTime,
            error: response.ok ? null : `HTTP ${response.status}`
          }
        } catch (error) {
          return {
            name: endpoint.name,
            path: endpoint.path,
            enabled: true,
            status: 'error',
            responseTime: null,
            error: error instanceof Error ? error.message : 'Unknown error'
          }
        }
      })
    )

    // Calculate overall health
    const enabledApis = apiStatus.filter(api => api.enabled)
    const healthyApis = enabledApis.filter(api => api.status === 'healthy')
    const overallHealth = enabledApis.length > 0 
      ? (healthyApis.length / enabledApis.length) * 100 
      : 0

    return NextResponse.json({
      success: true,
      migration: {
        status: migrationStatus,
        feature_flags: featureFlags,
        validation: validation,
        overall_health: Math.round(overallHealth)
      },
      infrastructure: {
        supabase: supabaseHealth,
        legacy_backend: legacyBackendHealth,
        migration_mode: process.env.NEXT_PUBLIC_MIGRATION_MODE || 'nextjs_only',
        module_5_status: 'complete',
        health_migration_version: process.env.NEXT_PUBLIC_HEALTH_MIGRATION_VERSION || 'v2.0.0'
      },
      api_endpoints: apiStatus,
      recommendations: getRecommendations(migrationStatus, validation, overallHealth),
      timestamp: new Date().toISOString(),
    })

  } catch (error) {
    console.error('Migration status API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

// Helper function to generate recommendations
function getRecommendations(
  migrationStatus: any, 
  validation: any, 
  overallHealth: number
): string[] {
  const recommendations: string[] = []

  // Migration sequence validation
  if (!validation.isValid) {
    validation.issues.forEach(issue => {
      recommendations.push(`Fix migration sequence: ${issue}`)
    })
  }

  // Health recommendations
  if (overallHealth < 100) {
    recommendations.push('Investigate API endpoint failures')
  }

  if (overallHealth < 50) {
    recommendations.push('Review API endpoint configurations and check Supabase connectivity')
  }

  // Progress recommendations
  if (migrationStatus.overall === 'not_started') {
    recommendations.push('Begin backend migration by enabling backend_nextjs flag')
  } else if (migrationStatus.overall === 'in_progress') {
    recommendations.push(`Continue migration: ${migrationStatus.pendingApis.length} APIs remaining`)
  } else if (migrationStatus.overall === 'completed') {
    recommendations.push('Backend migration complete - ready for legacy decommission')
  }

  return recommendations
}
