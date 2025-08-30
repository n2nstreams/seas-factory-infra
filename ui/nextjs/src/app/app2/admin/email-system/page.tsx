'use client'

import { useAuth } from '@/components/providers/AuthProvider'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import Navigation from '@/components/Navigation'
import EmailTestPanel from '@/components/EmailTestPanel'

export default function EmailSystemPage() {
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100">
      <Navigation />
      
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-green-800 mb-4">
              Email System Management
            </h1>
            <p className="text-lg text-green-600 max-w-2xl mx-auto">
              Test and manage the new email notification system with dual provider support (Resend + Supabase email)
            </p>
          </div>

          {/* Email System Overview */}
          <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-6 mb-8 border border-green-200/50">
            <h2 className="text-2xl font-semibold text-green-800 mb-4">System Overview</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium text-green-700 mb-3">Features</h3>
                <ul className="space-y-2 text-green-600">
                  <li className="flex items-center">
                    <svg className="h-5 w-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    Dual provider support (Resend + Supabase)
                  </li>
                  <li className="flex items-center">
                    <svg className="h-5 w-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    Feature flag controlled rollout
                  </li>
                  <li className="flex items-center">
                    <svg className="h-5 w-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    Glassmorphism email templates
                  </li>
                  <li className="flex items-center">
                    <svg className="h-5 w-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    Correlation ID tracking
                  </li>
                  <li className="flex items-center">
                    <svg className="h-5 w-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    Automatic fallback between providers
                  </li>
                </ul>
              </div>
              <div>
                <h3 className="text-lg font-medium text-green-700 mb-3">Available Templates</h3>
                <div className="space-y-3">
                  <div className="bg-green-50 p-3 rounded-lg">
                    <h4 className="font-medium text-green-800">Welcome Email</h4>
                    <p className="text-sm text-green-600">Sent to new users upon account creation</p>
                  </div>
                  <div className="bg-green-50 p-3 rounded-lg">
                    <h4 className="font-medium text-green-800">Payment Receipt</h4>
                    <p className="text-sm text-green-600">Sent after successful payment processing</p>
                  </div>
                  <div className="bg-green-50 p-3 rounded-lg">
                    <h4 className="font-medium text-green-800">Password Reset</h4>
                    <p className="text-sm text-green-600">Sent when user requests password reset</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Email Testing Panel */}
          <div className="mb-8">
            <h2 className="text-2xl font-semibold text-green-800 mb-4">Test Email System</h2>
            <EmailTestPanel />
          </div>

          {/* Configuration Instructions */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-blue-800 mb-3">Configuration Required</h3>
            <div className="text-blue-700 space-y-2">
              <p>To enable the email system, you need to:</p>
              <ol className="list-decimal list-inside space-y-1 ml-4">
                <li>Set the <code className="bg-blue-100 px-1 rounded">emails_v2</code> feature flag to enabled</li>
                <li>Configure <code className="bg-blue-100 px-1 rounded">RESEND_API_KEY</code> environment variable</li>
                <li>Set <code className="bg-blue-100 px-1 rounded">FROM_EMAIL</code> for your sending domain</li>
                <li>Optionally configure Supabase email for fallback</li>
              </ol>
              <p className="mt-3 text-sm">
                <strong>Note:</strong> The system will automatically fall back to the legacy email system if the feature flag is disabled.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
