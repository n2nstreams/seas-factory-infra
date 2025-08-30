'use client'

import { useDualAuth } from '@/components/providers/DualAuthProvider'
import { useFeatureFlags } from '@/components/providers/FeatureFlagProvider'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function Dashboard() {
  const { user, loading, signOut } = useDualAuth()
  const { flags } = useFeatureFlags()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.push('/app2/signin')
    }
  }, [user, loading, router])

  const handleSignOut = async () => {
    try {
      await signOut()
      router.push('/app2/signin')
    } catch (error) {
      console.error('Error signing out:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-green-800 text-lg">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null // Will redirect to signin
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-6 mb-8 border border-green-200/50">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-green-800">Dashboard</h1>
              <p className="text-green-600">Welcome back, {user.name || user.email}!</p>
            </div>
            <button
              onClick={handleSignOut}
              className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
            >
              Sign Out
            </button>
          </div>
        </div>

        {/* User Info Card */}
        <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-6 mb-8 border border-green-200/50">
          <h2 className="text-2xl font-semibold text-green-800 mb-4">User Information</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-medium text-green-700 mb-2">Profile Details</h3>
              <div className="space-y-2">
                <p><span className="font-medium">ID:</span> {user.id}</p>
                <p><span className="font-medium">Email:</span> {user.email}</p>
                <p><span className="font-medium">Name:</span> {user.name || 'Not provided'}</p>
                <p><span className="font-medium">Provider:</span> {user.provider || 'Unknown'}</p>
              </div>
            </div>
            <div>
              <h3 className="text-lg font-medium text-green-700 mb-2">Authentication Status</h3>
              <div className="space-y-2">
                <p><span className="font-medium">Supabase Auth:</span> 
                  <span className={`ml-2 px-2 py-1 rounded text-sm ${flags.auth_supabase ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                    {flags.auth_supabase ? 'Enabled' : 'Disabled'}
                  </span>
                </p>
                <p><span className="font-medium">Legacy Auth:</span> 
                  <span className="ml-2 px-2 py-1 rounded text-sm bg-blue-100 text-blue-800">
                    Active
                  </span>
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Feature Flags Status */}
        <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-6 mb-8 border border-green-200/50">
          <h2 className="text-2xl font-semibold text-green-800 mb-4">Feature Flags Status</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium">UI Shell V2</span>
              <span className={`px-2 py-1 rounded text-sm ${flags.ui_shell_v2 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                {flags.ui_shell_v2 ? 'Active' : 'Pending'}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium">Supabase Auth</span>
              <span className={`px-2 py-1 rounded text-sm ${flags.auth_supabase ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                {flags.auth_supabase ? 'Active' : 'Pending'}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium">Database Dual Write</span>
              <span className={`px-2 py-1 rounded text-sm ${flags.db_dual_write ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                {flags.db_dual_write ? 'Active' : 'Pending'}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium">Supabase Storage</span>
              <span className={`px-2 py-1 rounded text-sm ${flags.storage_supabase ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                {flags.storage_supabase ? 'Active' : 'Pending'}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium">Email System V2</span>
              <span className={`px-2 py-1 rounded text-sm ${flags.emails_v2 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                {flags.emails_v2 ? 'Active' : 'Pending'}
              </span>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-6 border border-green-200/50">
          <h2 className="text-2xl font-semibold text-green-800 mb-4">Quick Actions</h2>
          <div className="grid md:grid-cols-3 gap-4">
            <button
              onClick={() => router.push('/app2/admin/feature-flags')}
              className="p-4 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-center"
            >
              Manage Feature Flags
            </button>
            <button
              onClick={() => router.push('/app2/profile')}
              className="p-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-center"
            >
              Edit Profile
            </button>
            <button
              onClick={() => router.push('/app2/settings')}
              className="p-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-center"
            >
              Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
