'use client'

import { useFeatureFlags } from '@/components/providers/FeatureFlagProvider'
import { useAuth } from '@/components/providers/AuthProvider'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import Navigation from '@/components/Navigation'

export default function FeatureFlagsPage() {
  const { flags, setFlag, refreshFlags } = useFeatureFlags()
  const { user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/app2/signin')
    }
    // Only allow admin users
    if (!isLoading && user && user.plan !== 'growth') {
      router.push('/app2/dashboard')
    }
  }, [user, isLoading, router])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center">
        <div className="glass-card text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-primary-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user || user.plan !== 'growth') {
    return null // Will redirect
  }

  const handleToggleFlag = (flag: string, enabled: boolean) => {
    setFlag(flag, enabled)
  }

  const handleRefreshFlags = () => {
    refreshFlags()
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100">
      <Navigation />
      
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-primary-900 mb-2">
            Feature Flag Management
          </h1>
          <p className="text-primary-600">
            Control the rollout of new features and migration modules.
          </p>
        </div>

        {/* Feature Flags Grid */}
        <div className="grid gap-6 mb-8">
          {Object.entries(flags).map(([flag, enabled]) => (
            <div key={flag} className="glass-card">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-primary-800 mb-2">
                    {getFlagDisplayName(flag)}
                  </h3>
                  <p className="text-sm text-primary-600 mb-3">
                    {getFlagDescription(flag)}
                  </p>
                  <div className="flex items-center space-x-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      enabled 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {enabled ? 'Enabled' : 'Disabled'}
                    </span>
                    <span className="text-xs text-primary-500">
                      {getFlagStatus(flag, enabled)}
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => handleToggleFlag(flag, !enabled)}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      enabled
                        ? 'bg-red-100 text-red-700 hover:bg-red-200'
                        : 'bg-green-100 text-green-700 hover:bg-green-200'
                    }`}
                  >
                    {enabled ? 'Disable' : 'Enable'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Actions */}
        <div className="glass-card">
          <h2 className="text-xl font-semibold text-primary-800 mb-4">Actions</h2>
          <div className="flex space-x-4">
            <button
              onClick={handleRefreshFlags}
              className="glass-button text-primary-800 font-semibold"
            >
              Refresh Flags
            </button>
            <button
              onClick={() => {
                // Reset all flags to default
                Object.keys(flags).forEach(flag => {
                  setFlag(flag, false)
                })
              }}
              className="glass-button text-red-700 font-semibold bg-red-50 border-red-200 hover:bg-red-100"
            >
              Reset All to Default
            </button>
          </div>
        </div>

        {/* Migration Status */}
        <div className="glass-card mt-8">
          <h2 className="text-xl font-semibold text-primary-800 mb-4">Migration Status</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg bg-primary-50">
              <span className="font-medium text-primary-800">UI Shell Migration</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                flags.ui_shell_v2 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
              }`}>
                {flags.ui_shell_v2 ? 'Active' : 'Pending'}
              </span>
            </div>
            
            <div className="flex items-center justify-between p-3 rounded-lg bg-primary-50">
              <span className="font-medium text-primary-800">Authentication Migration</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                flags.auth_supabase ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
              }`}>
                {flags.auth_supabase ? 'Active' : 'Pending'}
              </span>
            </div>
            
            <div className="flex items-center justify-between p-3 rounded-lg bg-primary-50">
              <span className="font-medium text-primary-800">Database Migration</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                flags.db_dual_write ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
              }`}>
                {flags.db_dual_write ? 'Active' : 'Pending'}
              </span>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

function getFlagDisplayName(flag: string): string {
  const names: Record<string, string> = {
    ui_shell_v2: 'UI Shell v2',
    auth_supabase: 'Supabase Auth',
    db_dual_write: 'Database Dual Write',
    db_dual_write_tenants: 'DB Dual Write - Tenants',
    db_dual_write_users: 'DB Dual Write - Users',
    db_dual_write_projects: 'DB Dual Write - Projects',
    db_dual_write_ideas: 'DB Dual Write - Ideas',
    storage_supabase: 'Supabase Storage',
    jobs_pg: 'PostgreSQL Jobs',
    billing_v2: 'Billing v2',
    emails_v2: 'Email System v2',
    observability_v2: 'Observability v2',
    sentry_enabled: 'Sentry Error Tracking',
    vercel_analytics_enabled: 'Vercel Analytics',
    health_monitoring_enabled: 'Health Monitoring',
    ai_workloads_v2: 'AI Workloads v2',
    performance_monitoring: 'Performance Monitoring',
    data_migration_final: 'Final Data Migration',
    decommission_legacy: 'Legacy Decommission'
  }
  return names[flag] || flag.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

function getFlagDescription(flag: string): string {
  const descriptions: Record<string, string> = {
    ui_shell_v2: 'Next.js + shadcn/ui shell migration',
    auth_supabase: 'Supabase Auth integration with dual auth system',
    db_dual_write: 'Dual-write system for database migration',
    db_dual_write_tenants: 'Tenant migration with dual-write',
    db_dual_write_users: 'User migration with dual-write',
    db_dual_write_projects: 'Project migration with dual-write',
    db_dual_write_ideas: 'Ideas migration with dual-write',
    storage_supabase: 'Supabase Storage integration with migration system',
    jobs_pg: 'pg-boss job scheduling system',
    billing_v2: 'New Stripe billing system with customer portal',
    emails_v2: 'New email system with Resend integration',
    observability_v2: 'Enhanced observability and monitoring',
    sentry_enabled: 'Sentry error tracking and monitoring',
    vercel_analytics_enabled: 'Vercel Analytics integration',
    health_monitoring_enabled: 'System health monitoring',
    ai_workloads_v2: 'AI workload processing and management',
    performance_monitoring: 'Performance monitoring and optimization',
    data_migration_final: 'Source-of-truth cutover to new systems',
    decommission_legacy: 'Decommission legacy infrastructure'
  }
  return descriptions[flag] || 'Feature flag for system functionality'
}

function getFlagStatus(flag: string, enabled: boolean): string {
  if (flag === 'ui_shell_v2') {
    return enabled ? 'Users routed to /app2' : 'Users routed to legacy UI'
  }
  if (flag === 'auth_supabase') {
    return enabled ? 'Supabase auth active' : 'Legacy auth active'
  }
  if (flag === 'db_dual_write') {
    return enabled ? 'Dual-write mode active' : 'Legacy database only'
  }
  if (flag === 'storage_supabase') {
    return enabled ? 'Supabase storage active' : 'Legacy storage active'
  }
  if (flag === 'billing_v2') {
    return enabled ? 'New billing system active' : 'Legacy billing active'
  }
  if (flag === 'emails_v2') {
    return enabled ? 'New email system active' : 'Legacy email active'
  }
  if (flag === 'decommission_legacy') {
    return enabled ? 'Legacy decommission active' : 'Legacy systems maintained'
  }
  return enabled ? 'Feature active' : 'Feature inactive'
}
