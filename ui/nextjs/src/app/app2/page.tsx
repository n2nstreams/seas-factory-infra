'use client'

import { useAuth } from '@/components/providers/AuthProvider'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import Link from 'next/link'

export default function App2LandingPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  console.log('App2LandingPage: user:', user, 'isLoading:', isLoading)

  useEffect(() => {
    // Only redirect if we have a confirmed user and we're not loading
    if (!isLoading && user) {
      console.log('App2LandingPage: Redirecting to dashboard')
      router.push('/app2/dashboard')
    }
  }, [user, isLoading, router])

  if (isLoading) {
    console.log('App2LandingPage: Showing loading state')
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center">
        <div className="glass-card text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <h1 className="text-2xl font-bold text-primary-800 mb-2">AI SaaS Factory</h1>
          <p className="text-primary-600">Loading...</p>
        </div>
      </div>
    )
  }

  console.log('App2LandingPage: Showing landing page content')
  // If no user, show the landing page (no redirect)
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-primary-900 mb-6 animate-fade-in">
            AI SaaS Factory
          </h1>
          <p className="text-xl text-primary-700 mb-8 max-w-3xl mx-auto">
            Build, deploy, and scale AI-powered SaaS applications with our comprehensive platform.
            Experience the future of SaaS development.
          </p>
          <div className="flex gap-4 justify-center">
            <Link 
              href="/app2/signup"
              className="glass-button text-primary-800 font-semibold hover:scale-105 transition-transform"
            >
              Get Started
            </Link>
            <Link 
              href="/app2/pricing"
              className="glass-button text-primary-800 font-semibold hover:scale-105 transition-transform"
            >
              View Pricing
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="glass-card text-center">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-primary-800 mb-2">Lightning Fast</h3>
            <p className="text-primary-600">Build and deploy your SaaS in minutes, not months.</p>
          </div>

          <div className="glass-card text-center">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-primary-800 mb-2">AI-Powered</h3>
            <p className="text-primary-600">Leverage cutting-edge AI to automate and optimize your workflows.</p>
          </div>

          <div className="glass-card text-center">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-primary-800 mb-2">Enterprise Ready</h3>
            <p className="text-primary-600">Multi-tenant architecture with enterprise-grade security.</p>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <div className="glass-card inline-block">
            <h2 className="text-2xl font-semibold text-primary-800 mb-4">
              Ready to Transform Your SaaS?
            </h2>
            <p className="text-primary-600 mb-6">
              Join thousands of developers building the future of SaaS applications.
            </p>
            <Link 
              href="/app2/signup"
              className="glass-button text-primary-800 font-semibold hover:scale-105 transition-transform"
            >
              Start Building Today
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
