'use client'

import { useFeatureFlag } from '@/components/providers/FeatureFlagProvider'
import { useAuth } from '@/components/providers/AuthProvider'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import LandingPage from './landing/page'

export default function HomePage() {
  const uiShellV2 = useFeatureFlag('ui_shell_v2')
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const [shouldRedirect, setShouldRedirect] = useState(false)

  // Route to appropriate UI based on feature flag
  useEffect(() => {
    if (isLoading) return // Don't redirect while still loading

    if (uiShellV2) {
      // New Next.js UI shell
      if (user) {
        setShouldRedirect(true)
        router.push('/dashboard')
      }
      // If no user, stay on this page and show landing page
    } else {
      // Legacy UI shell - redirect to legacy components
      if (user) {
        setShouldRedirect(true)
        router.push('/legacy/dashboard')
      } else {
        setShouldRedirect(true)
        router.push('/legacy')
      }
    }
  }, [uiShellV2, user, router, isLoading])

  // Show loading while authentication is being determined
  if (isLoading) {
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

  // If we should redirect, show loading
  if (shouldRedirect) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center">
        <div className="glass-card text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-primary-800 mb-2">
            AI SaaS Factory
          </h2>
          <p className="text-primary-600">Redirecting...</p>
        </div>
      </div>
    )
  }

  // Show landing page for unauthenticated users
  return <LandingPage />
}
