'use client'

import { useFeatureFlag } from '@/components/providers/FeatureFlagProvider'
import { useAuth } from '@/components/providers/AuthProvider'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function HomePage() {
  const uiShellV2 = useFeatureFlag('ui_shell_v2')
  const { user } = useAuth()
  const router = useRouter()

  // Route to appropriate UI based on feature flag
  useEffect(() => {
    if (uiShellV2) {
      // New Next.js UI shell
      if (user) {
        router.push('/dashboard')
      } else {
        router.push('/')
      }
    } else {
      // Legacy UI shell - redirect to legacy components
      if (user) {
        router.push('/legacy/dashboard')
      } else {
        router.push('/legacy')
      }
    }
  }, [uiShellV2, user, router])

  // Show loading while routing
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center">
      <div className="glass-card text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
        <h2 className="text-xl font-semibold text-primary-800 mb-2">
          AI SaaS Factory
        </h2>
        <p className="text-primary-600">
          {uiShellV2 ? 'Loading new interface...' : 'Loading legacy interface...'}
        </p>
      </div>
    </div>
  )
}
