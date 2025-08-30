'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'

export default function AuthCallback() {
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        console.log('🔐 OAuth Callback: Starting authentication callback...')
        
        // Check URL parameters for OAuth response
        const urlParams = new URLSearchParams(window.location.search)
        const error = urlParams.get('error')
        const errorDescription = urlParams.get('error_description')
        
        if (error) {
          console.error('OAuth Error:', error, errorDescription)
          setError(`OAuth Error: ${error}${errorDescription ? ` - ${errorDescription}` : ''}`)
          setLoading(false)
          return
        }
        
        console.log('🔐 OAuth Callback: Getting session from Supabase...')
        const { data, error: sessionError } = await supabase.auth.getSession()
        
        if (sessionError) {
          console.error('Error getting session:', sessionError)
          setError('Authentication failed. Please try again.')
          setLoading(false)
          return
        }

        console.log('🔐 OAuth Callback: Session data:', data)
        
        if (data.session) {
          console.log('🔐 OAuth Callback: Successfully authenticated, redirecting to dashboard...')
          // Successfully authenticated, redirect to dashboard
          router.push('/app2/dashboard')
        } else {
          console.log('🔐 OAuth Callback: No session found, redirecting to sign in...')
          // No session found, redirect to sign in
          router.push('/app2/signin')
        }
      } catch (err) {
        console.error('Unexpected error during auth callback:', err)
        setError('An unexpected error occurred. Please try again.')
        setLoading(false)
      }
    }

    handleAuthCallback()
  }, [router])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-green-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-green-800 text-lg">Completing authentication...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-red-100">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-red-600 text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-red-800 mb-4">Authentication Error</h1>
          <p className="text-red-700 mb-6">{error}</p>
          <button
            onClick={() => router.push('/app2/signin')}
            className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return null
}
