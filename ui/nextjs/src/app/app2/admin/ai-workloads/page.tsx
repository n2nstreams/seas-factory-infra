'use client'

import { useState, useEffect } from 'react'
import { useFeatureFlags } from '@/components/providers/FeatureFlagProvider'
import { useAuth } from '@/components/providers/AuthProvider'
import { AIWorkloadRequest } from '@/lib/aiWorkloads'

interface AIWorkloadStats {
  total_requests: number
  total_cost: number
  fallback_count: number
  org_count: number
  user_count: number
  config: {
    max_latency_ms: number
    max_cost_usd: number
    max_tokens: number
    allowed_actions: string[]
    cost_per_token: number
    fallback_enabled: boolean
  }
}

export default function AIWorkloadsPage() {
  const { flags } = useFeatureFlags()
  const { user } = useAuth()
  const [stats, setStats] = useState<AIWorkloadStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [testResult, setTestResult] = useState<any>(null)
  const [testRequest, setTestRequest] = useState<Partial<AIWorkloadRequest>>({
    purpose: 'testing',
    sensitivity_tag: 'internal',
    action_type: 'idea_validation',
    payload: { idea: 'Test SaaS application idea' }
  })

  // Check if user has access to AI workloads admin
  if (!flags.ai_workloads_v2) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100">
        <div className="container mx-auto px-4 py-8">
          <div className="glass-card text-center">
            <h1 className="text-2xl font-bold text-primary-800 mb-4">
              AI Workloads v2 Not Enabled
            </h1>
            <p className="text-primary-600 mb-4">
              This feature is currently disabled. Enable the ai_workloads_v2 feature flag to access AI workload management.
            </p>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-yellow-800">
                <strong>Note:</strong> AI Workloads v2 is part of Module 9 of the tech stack migration.
                It will be enabled once the background job pipeline is ready.
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  useEffect(() => {
    if (flags.ai_workloads_v2) {
      fetchStats()
    }
  }, [flags.ai_workloads_v2])

  const fetchStats = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/ai-workloads')
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Error fetching AI workload stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const testAIWorkload = async () => {
    try {
      setLoading(true)
      setTestResult(null)
      
      const response = await fetch('/api/ai-workloads', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-tenant-id': user?.id || 'test-tenant',
          'x-user-id': user?.id || 'test-user'
        },
        body: JSON.stringify(testRequest)
      })
      
      const result = await response.json()
      setTestResult(result)
      
      // Refresh stats after test
      fetchStats()
    } catch (error) {
      console.error('Error testing AI workload:', error)
      setTestResult({ error: 'Test failed', details: error })
    } finally {
      setLoading(false)
    }
  }

  const resetTracking = async () => {
    try {
      const response = await fetch('/api/ai-workloads/reset', { method: 'POST' })
      if (response.ok) {
        fetchStats()
      }
    } catch (error) {
      console.error('Error resetting tracking:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="glass-card mb-8">
          <h1 className="text-3xl font-bold text-primary-800 mb-2">
            AI Workloads Management
          </h1>
          <p className="text-primary-600">
            Module 9: Constrained AI workload management with cost controls and latency constraints
          </p>
          <div className="mt-4 flex items-center space-x-2">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              flags.ai_workloads_v2 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
            }`}>
              {flags.ai_workloads_v2 ? 'Active' : 'Pending'}
            </span>
            <span className="text-sm text-primary-600">
              Feature Flag: ai_workloads_v2
            </span>
          </div>
        </div>

        {/* Service Statistics */}
        {stats && (
          <div className="glass-card mb-8">
            <h2 className="text-2xl font-semibold text-primary-800 mb-4">Service Statistics</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="bg-white/60 rounded-lg p-4">
                <h3 className="font-medium text-primary-700 mb-2">Requests</h3>
                <p className="text-3xl font-bold text-primary-800">{stats.total_requests}</p>
                <p className="text-sm text-primary-600">Total processed</p>
              </div>
              <div className="bg-white/60 rounded-lg p-4">
                <h3 className="font-medium text-primary-700 mb-2">Cost</h3>
                <p className="text-3xl font-bold text-primary-800">${stats.total_cost.toFixed(4)}</p>
                <p className="text-sm text-primary-600">Total spent</p>
              </div>
              <div className="bg-white/60 rounded-lg p-4">
                <h3 className="font-medium text-primary-700 mb-2">Fallbacks</h3>
                <p className="text-3xl font-bold text-primary-800">{stats.fallback_count}</p>
                <p className="text-sm text-primary-600">Legacy orchestrator calls</p>
              </div>
            </div>
            <div className="mt-6 grid md:grid-cols-2 gap-4">
              <div className="bg-white/60 rounded-lg p-4">
                <h3 className="font-medium text-primary-700 mb-2">Organizations</h3>
                <p className="text-2xl font-bold text-primary-800">{stats.org_count}</p>
              </div>
              <div className="bg-white/60 rounded-lg p-4">
                <h3 className="font-medium text-primary-700 mb-2">Users</h3>
                <p className="text-2xl font-bold text-primary-800">{stats.user_count}</p>
              </div>
            </div>
          </div>
        )}

        {/* Configuration */}
        {stats && (
          <div className="glass-card mb-8">
            <h2 className="text-2xl font-semibold text-primary-800 mb-4">Configuration</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-medium text-primary-700 mb-3">Performance Limits</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-primary-600">Max Latency:</span>
                    <span className="font-medium">{stats.config.max_latency_ms}ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-primary-600">Max Cost per Request:</span>
                    <span className="font-medium">${stats.config.max_cost_usd}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-primary-600">Max Tokens:</span>
                    <span className="font-medium">{stats.config.max_tokens.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-primary-600">Cost per Token:</span>
                    <span className="font-medium">${stats.config.cost_per_token.toFixed(6)}</span>
                  </div>
                </div>
              </div>
              <div>
                <h3 className="font-medium text-primary-700 mb-3">Allowed Actions</h3>
                <div className="space-y-2">
                  {stats.config.allowed_actions.map((action, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-primary-600">{action}</span>
                    </div>
                  ))}
                </div>
                <div className="mt-4">
                  <span className="text-sm text-primary-600">
                    Fallback Enabled: {stats.config.fallback_enabled ? 'Yes' : 'No'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Test AI Workload */}
        <div className="glass-card mb-8">
          <h2 className="text-2xl font-semibold text-primary-800 mb-4">Test AI Workload</h2>
          <div className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="purpose" className="block text-sm font-medium text-primary-700 mb-2">
                  Purpose
                </label>
                <input
                  id="purpose"
                  type="text"
                  value={testRequest.purpose}
                  onChange={(e) => setTestRequest(prev => ({ ...prev, purpose: e.target.value }))}
                  className="w-full px-3 py-2 border border-primary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Enter purpose for this AI workload"
                />
              </div>
              <div>
                <label htmlFor="sensitivity" className="block text-sm font-medium text-primary-700 mb-2">
                  Sensitivity Tag
                </label>
                <select
                  id="sensitivity"
                  value={testRequest.sensitivity_tag}
                  onChange={(e) => setTestRequest(prev => ({ ...prev, sensitivity_tag: e.target.value as any }))}
                  className="w-full px-3 py-2 border border-primary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  aria-label="Select sensitivity level"
                >
                  <option value="public">Public</option>
                  <option value="internal">Internal</option>
                  <option value="confidential">Confidential</option>
                </select>
              </div>
            </div>
            <div>
              <label htmlFor="action-type" className="block text-sm font-medium text-primary-700 mb-2">
                Action Type
              </label>
              <select
                id="action-type"
                value={testRequest.action_type}
                onChange={(e) => setTestRequest(prev => ({ ...prev, action_type: e.target.value }))}
                className="w-full px-3 py-2 border border-primary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                aria-label="Select AI action type"
              >
                <option value="idea_validation">Idea Validation</option>
                <option value="tech_stack_recommendation">Tech Stack Recommendation</option>
                <option value="design_generation">Design Generation</option>
                <option value="code_review">Code Review</option>
                <option value="qa_test_generation">QA Test Generation</option>
                <option value="documentation_generation">Documentation Generation</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-primary-700 mb-2">
                Payload
              </label>
              <textarea
                value={JSON.stringify(testRequest.payload, null, 2)}
                onChange={(e) => {
                  try {
                    const parsed = JSON.parse(e.target.value)
                    setTestRequest(prev => ({ ...prev, payload: parsed }))
                  } catch (error) {
                    // Allow invalid JSON during typing
                  }
                }}
                rows={4}
                className="w-full px-3 py-2 border border-primary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm"
                placeholder='{"idea": "Your SaaS idea description"}'
              />
            </div>
            <div className="flex space-x-4">
              <button
                onClick={testAIWorkload}
                disabled={loading}
                className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Testing...' : 'Test AI Workload'}
              </button>
              <button
                onClick={resetTracking}
                className="px-6 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
              >
                Reset Tracking
              </button>
            </div>
          </div>
        </div>

        {/* Test Results */}
        {testResult && (
          <div className="glass-card">
            <h2 className="text-2xl font-semibold text-primary-800 mb-4">Test Results</h2>
            <div className="bg-white/60 rounded-lg p-4">
              <pre className="text-sm text-primary-800 overflow-x-auto">
                {JSON.stringify(testResult, null, 2)}
              </pre>
            </div>
            {testResult.success && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <h3 className="font-medium text-green-800 mb-2">Success!</h3>
                <div className="space-y-1 text-sm text-green-700">
                  <div>Processing Time: {testResult.processing_time}ms</div>
                  <div>Cost Estimate: ${testResult.cost_estimate?.toFixed(6)}</div>
                  {testResult.fallback_used && (
                    <div className="text-yellow-700">⚠️ Legacy fallback used</div>
                  )}
                </div>
              </div>
            )}
            {!testResult.success && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <h3 className="font-medium text-red-800 mb-2">Error</h3>
                <p className="text-red-700">{testResult.error}</p>
              </div>
            )}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="glass-card text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-primary-600">Processing...</p>
          </div>
        )}
      </div>
    </div>
  )
}
