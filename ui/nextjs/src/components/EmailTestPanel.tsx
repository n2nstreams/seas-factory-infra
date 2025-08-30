'use client'

import { useState, useEffect } from 'react'
import { useFeatureFlag } from '@/components/providers/FeatureFlagProvider'

interface EmailTestData {
  template: string
  recipient: {
    email: string
    name: string
  }
  variables: Record<string, any>
}

interface TemplateInfo {
  name: string
  subject: string
  variables: string[]
}

interface ProviderStatus {
  resend: boolean
  supabase: boolean
  featureFlag: boolean
}

export default function EmailTestPanel() {
  const emailsV2Enabled = useFeatureFlag('emails_v2')
  const [testData, setTestData] = useState<EmailTestData>({
    template: 'welcome',
    recipient: { email: '', name: '' },
    variables: {}
  })
  const [templates, setTemplates] = useState<TemplateInfo[]>([])
  const [providerStatus, setProviderStatus] = useState<ProviderStatus | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  // Load templates and provider status
  useEffect(() => {
    loadEmailStatus()
  }, [])

  // Update variables when template changes
  useEffect(() => {
    updateVariablesForTemplate(testData.template)
  }, [testData.template])

  const loadEmailStatus = async () => {
    try {
      const response = await fetch('/api/email/test')
      const data = await response.json()
      
      if (data.success) {
        setTemplates(data.templateDetails)
        setProviderStatus(data.providerStatus)
      }
    } catch (err) {
      console.error('Failed to load email status:', err)
    }
  }

  const updateVariablesForTemplate = (templateName: string) => {
    const template = templates.find(t => t.name === templateName)
    if (template) {
      const defaultVariables: Record<string, any> = {}
      
      switch (templateName) {
        case 'welcome':
          defaultVariables.user_name = 'Test User'
          defaultVariables.plan_name = 'Pro'
          defaultVariables.trial_days = 14
          defaultVariables.dashboard_url = 'https://app.saasfactory.com/dashboard'
          break
        case 'payment_receipt':
          defaultVariables.user_name = 'Test User'
          defaultVariables.invoice_number = 'INV-001'
          defaultVariables.invoice_date = new Date().toLocaleDateString()
          defaultVariables.plan_name = 'Pro'
          defaultVariables.amount = 29.99
          defaultVariables.currency = 'USD'
          defaultVariables.dashboard_url = 'https://app.saasfactory.com/dashboard'
          break
        case 'password_reset':
          defaultVariables.user_name = 'Test User'
          defaultVariables.reset_url = 'https://app.saasfactory.com/reset-password?token=test123'
          defaultVariables.expiry_hours = 24
          break
      }
      
      setTestData(prev => ({
        ...prev,
        template: templateName,
        variables: defaultVariables
      }))
    }
  }

  const handleSendTest = async () => {
    if (!testData.recipient.email) {
      setError('Recipient email is required')
      return
    }

    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('/api/email/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(testData),
      })

      const data = await response.json()

      if (data.success) {
        setResult(data)
      } else {
        setError(data.error || 'Failed to send email')
      }
    } catch (err) {
      setError('Failed to send email')
      console.error('Email test error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleVariableChange = (key: string, value: string) => {
    setTestData(prev => ({
      ...prev,
      variables: {
        ...prev.variables,
        [key]: value
      }
    }))
  }

  if (!emailsV2Enabled) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">
              Email System v2 Disabled
            </h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>
                The new email system is currently disabled by the <code className="bg-yellow-100 px-1 rounded">emails_v2</code> feature flag.
                Enable it in the feature flags panel to test the email system.
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Provider Status */}
      {providerStatus && (
        <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-6 border border-green-200/50">
          <h3 className="text-lg font-semibold text-green-800 mb-4">Provider Status</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium">Resend</span>
              <span className={`px-2 py-1 rounded text-sm ${providerStatus.resend ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                {providerStatus.resend ? 'Available' : 'Not Configured'}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium">Supabase Email</span>
              <span className={`px-2 py-1 rounded text-sm ${providerStatus.supabase ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                {providerStatus.supabase ? 'Available' : 'Not Configured'}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium">Feature Flag</span>
              <span className={`px-2 py-1 rounded text-sm ${providerStatus.featureFlag ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                {providerStatus.featureFlag ? 'Enabled' : 'Disabled'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Email Test Form */}
      <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-6 border border-green-200/50">
        <h3 className="text-lg font-semibold text-green-800 mb-4">Send Test Email</h3>
        
        <div className="space-y-4">
          {/* Template Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Template
            </label>
            <select
              value={testData.template}
              onChange={(e) => setTestData(prev => ({ ...prev, template: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              aria-label="Select email template"
            >
              {templates.map((template) => (
                <option key={template.name} value={template.name}>
                  {template.name.charAt(0).toUpperCase() + template.name.slice(1).replace('_', ' ')}
                </option>
              ))}
            </select>
          </div>

          {/* Recipient Information */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Recipient Email *
              </label>
              <input
                type="email"
                value={testData.recipient.email}
                onChange={(e) => setTestData(prev => ({ 
                  ...prev, 
                  recipient: { ...prev.recipient, email: e.target.value }
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="test@example.com"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Recipient Name
              </label>
              <input
                type="text"
                value={testData.recipient.name}
                onChange={(e) => setTestData(prev => ({ 
                  ...prev, 
                  recipient: { ...prev.recipient, name: e.target.value }
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Test User"
              />
            </div>
          </div>

          {/* Template Variables */}
          {Object.keys(testData.variables).length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Template Variables
              </label>
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(testData.variables).map(([key, value]) => (
                  <div key={key}>
                    <label className="block text-xs font-medium text-gray-600 mb-1">
                      {key.replace('_', ' ')}
                    </label>
                                         <input
                       type="text"
                       value={String(value)}
                       onChange={(e) => handleVariableChange(key, e.target.value)}
                       className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm"
                       aria-label={`Enter ${key.replace('_', ' ')} value`}
                     />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Send Button */}
          <div className="pt-4">
            <button
              onClick={handleSendTest}
              disabled={isLoading || !testData.recipient.email}
              className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white font-medium py-3 px-6 rounded-lg hover:from-green-700 hover:to-green-800 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              {isLoading ? 'Sending...' : 'Send Test Email'}
            </button>
          </div>
        </div>
      </div>

      {/* Results */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {result && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-green-800">Email Sent Successfully</h3>
              <div className="mt-2 text-sm text-green-700">
                <p><strong>Provider:</strong> {result.provider}</p>
                <p><strong>Correlation ID:</strong> {result.correlationId}</p>
                <p><strong>Timestamp:</strong> {new Date(result.timestamp).toLocaleString()}</p>
                {result.metadata && (
                  <div className="mt-2">
                    <p><strong>Metadata:</strong></p>
                    <pre className="text-xs bg-green-100 p-2 rounded mt-1 overflow-x-auto">
                      {JSON.stringify(result.metadata, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
