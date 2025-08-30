'use client'

import React, { useState } from 'react'
import { useAuth } from '@/components/providers/AuthProvider'
import { useFeatureFlags } from '@/components/providers/FeatureFlagProvider'
import { jobService, JobSubmission } from '@/lib/job-service'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Play, 
  Clock, 
  Database, 
  Zap, 
  Palette, 
  Code, 
  Mail, 
  Webhook,
  CheckCircle,
  AlertCircle,
  Info
} from 'lucide-react'

interface JobSubmissionFormProps {
  tenantId: string
  onJobSubmitted?: (jobId: string) => void
}

const JOB_TEMPLATES = {
  'security_scan': {
    name: 'Security Scan',
    description: 'Run security vulnerability scan on project dependencies',
    icon: Zap,
    family: 'A' as const,
    defaultInput: {
      project_id: 'demo-project',
      scan_type: 'dependencies',
      include_dev: false
    }
  },
  'code_generation': {
    name: 'Code Generation',
    description: 'Generate code based on design specifications',
    icon: Code,
    family: 'A' as const,
    defaultInput: {
      project_id: 'demo-project',
      component_type: 'react',
      specifications: 'User authentication form with validation'
    }
  },
  'design_generation': {
    name: 'Design Generation',
    description: 'Generate design mockups and style guides',
    icon: Palette,
    family: 'A' as const,
    defaultInput: {
      project_id: 'demo-project',
      design_type: 'web_app',
      requirements: 'Modern, responsive design with glassmorphism theme'
    }
  },
  'data_migration': {
    name: 'Data Migration',
    description: 'Migrate data between database systems',
    icon: Database,
    family: 'C' as const,
    defaultInput: {
      source_system: 'legacy_postgres',
      target_system: 'supabase',
      tables: ['users', 'projects', 'ideas']
    }
  },
  'backup_cleanup': {
    name: 'Backup Cleanup',
    description: 'Clean up old backup files and logs',
    icon: Clock,
    family: 'B' as const,
    defaultInput: {
      retention_days: 30,
      file_types: ['backup', 'log', 'temp']
    }
  },
  'health_check': {
    name: 'Health Check',
    description: 'Monitor system health and performance',
    icon: CheckCircle,
    family: 'B' as const,
    defaultInput: {
      services: ['api', 'database', 'storage'],
      check_interval: 300
    }
  },
  'email_send': {
    name: 'Email Send',
    description: 'Send transactional emails to users',
    icon: Mail,
    family: 'A' as const,
    defaultInput: {
      template: 'welcome',
      recipient: 'user@example.com',
      variables: { name: 'John Doe' }
    }
  },
  'webhook_process': {
    name: 'Webhook Process',
    description: 'Process incoming webhook events',
    icon: Webhook,
    family: 'A' as const,
    defaultInput: {
      provider: 'stripe',
      event_type: 'payment.succeeded',
      payload: { amount: 1999, currency: 'usd' }
    }
  }
}

export default function JobSubmissionForm({ tenantId, onJobSubmitted }: JobSubmissionFormProps) {
  const { user } = useAuth()
  const { flags } = useFeatureFlags()
  
  const [selectedTemplate, setSelectedTemplate] = useState<string>('security_scan')
  const [customJobName, setCustomJobName] = useState('')
  const [customInputData, setCustomInputData] = useState('')
  const [priority, setPriority] = useState('0')
  const [maxRetries, setMaxRetries] = useState('3')
  const [timeoutSeconds, setTimeoutSeconds] = useState('600')
  const [idempotencyKey, setIdempotencyKey] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submissionResult, setSubmissionResult] = useState<{
    success: boolean
    jobId?: string
    message: string
    destination: 'supabase' | 'legacy'
  } | null>(null)

  const selectedJobTemplate = JOB_TEMPLATES[selectedTemplate as keyof typeof JOB_TEMPLATES]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!user) {
      setSubmissionResult({
        success: false,
        message: 'User not authenticated',
        destination: 'legacy'
      })
      return
    }

    setSubmitting(true)
    setSubmissionResult(null)

    try {
      // Prepare job submission
      const submission: JobSubmission = {
        tenant_id: tenantId,
        job_name: customJobName || selectedTemplate,
        job_family: selectedJobTemplate.family,
        input_data: customInputData ? JSON.parse(customInputData) : selectedJobTemplate.defaultInput,
        priority: parseInt(priority),
        max_retries: parseInt(maxRetries),
        timeout_seconds: parseInt(timeoutSeconds),
        idempotency_key: idempotencyKey || undefined
      }

      // Submit job
      const jobId = await jobService.submitJob(submission)
      
      // Determine destination based on feature flag
      const destination = flags.jobs_pg ? 'supabase' : 'legacy'
      
      setSubmissionResult({
        success: true,
        jobId,
        message: `Job submitted successfully to ${destination} system`,
        destination
      })

      // Notify parent component
      if (onJobSubmitted) {
        onJobSubmitted(jobId)
      }

    } catch (error) {
      setSubmissionResult({
        success: false,
        message: `Failed to submit job: ${error instanceof Error ? error.message : 'Unknown error'}`,
        destination: 'legacy'
      })
    } finally {
      setSubmitting(false)
    }
  }

  const handleTemplateChange = (template: string) => {
    setSelectedTemplate(template)
    setCustomJobName('')
    setCustomInputData('')
  }

  const generateIdempotencyKey = () => {
    const key = `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    setIdempotencyKey(key)
  }

  return (
    <div className="space-y-6">
      {/* Feature Flag Status */}
      <Alert className={flags.jobs_pg ? 'border-green-200 bg-green-50' : 'border-yellow-200 bg-yellow-50'}>
        <Info className="h-4 w-4" />
        <AlertDescription>
          <strong>Jobs System:</strong> {flags.jobs_pg ? (
            <span className="text-green-700">
              Supabase jobs enabled - Jobs will be processed by the new system
            </span>
          ) : (
            <span className="text-yellow-700">
              Legacy jobs enabled - Jobs will be processed by the existing system
            </span>
          )}
        </AlertDescription>
      </Alert>

      {/* Job Templates */}
      <Card className="glass-card">
        <CardHeader>
          <CardTitle>Job Templates</CardTitle>
          <CardDescription>Select a predefined job template or create a custom one</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(JOB_TEMPLATES).map(([key, template]) => {
              const Icon = template.icon
              return (
                <button
                  key={key}
                  onClick={() => handleTemplateChange(key)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    selectedTemplate === key
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-primary-200 bg-white hover:border-primary-300 hover:bg-primary-25'
                  }`}
                >
                  <Icon className="w-8 h-8 mx-auto mb-2 text-primary-600" />
                  <h3 className="font-medium text-primary-900 text-sm">{template.name}</h3>
                  <p className="text-xs text-primary-600 mt-1">{template.description}</p>
                  <Badge className={`mt-2 ${
                    template.family === 'A' ? 'bg-blue-100 text-blue-800' :
                    template.family === 'B' ? 'bg-green-100 text-green-800' :
                    'bg-purple-100 text-purple-800'
                  }`}>
                    {template.family === 'A' ? 'Short' : template.family === 'B' ? 'Cron' : 'Long'}
                  </Badge>
                </button>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Job Submission Form */}
      <Card className="glass-card">
        <CardHeader>
          <CardTitle>Submit Job</CardTitle>
          <CardDescription>
            Configure and submit a new job to the {flags.jobs_pg ? 'Supabase' : 'legacy'} system
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Job Configuration */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="jobName">Job Name</Label>
                <Input
                  id="jobName"
                  value={customJobName || selectedTemplate}
                  onChange={(e) => setCustomJobName(e.target.value)}
                  placeholder="Enter custom job name or use template"
                />
                <p className="text-xs text-primary-600">
                  Current template: {selectedJobTemplate.name}
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="priority">Priority</Label>
                <Select value={priority} onValueChange={setPriority}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0">Normal (0)</SelectItem>
                    <SelectItem value="1">Low (1)</SelectItem>
                    <SelectItem value="5">Medium (5)</SelectItem>
                    <SelectItem value="10">High (10)</SelectItem>
                    <SelectItem value="20">Critical (20)</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-primary-600">Higher numbers = higher priority</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-2">
                <Label htmlFor="maxRetries">Max Retries</Label>
                <Input
                  id="maxRetries"
                  type="number"
                  min="0"
                  max="10"
                  value={maxRetries}
                  onChange={(e) => setMaxRetries(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="timeoutSeconds">Timeout (seconds)</Label>
                <Input
                  id="timeoutSeconds"
                  type="number"
                  min="60"
                  max="3600"
                  value={timeoutSeconds}
                  onChange={(e) => setTimeoutSeconds(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="idempotencyKey">Idempotency Key</Label>
                <div className="flex space-x-2">
                  <Input
                    id="idempotencyKey"
                    value={idempotencyKey}
                    onChange={(e) => setIdempotencyKey(e.target.value)}
                    placeholder="Optional: prevents duplicate jobs"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={generateIdempotencyKey}
                  >
                    Generate
                  </Button>
                </div>
              </div>
            </div>

            {/* Input Data */}
            <div className="space-y-2">
              <Label htmlFor="inputData">Input Data (JSON)</Label>
              <Textarea
                id="inputData"
                value={customInputData || JSON.stringify(selectedJobTemplate.defaultInput, null, 2)}
                onChange={(e) => setCustomInputData(e.target.value)}
                rows={6}
                placeholder="Enter JSON input data for the job"
              />
              <p className="text-xs text-primary-600">
                This data will be passed to the job when it executes
              </p>
            </div>

            {/* Submit Button */}
            <div className="flex justify-end">
              <Button
                type="submit"
                disabled={submitting}
                className="glass-button"
                size="lg"
              >
                <Play className="w-4 h-4 mr-2" />
                {submitting ? 'Submitting...' : 'Submit Job'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Submission Result */}
      {submissionResult && (
        <Alert className={
          submissionResult.success 
            ? 'border-green-200 bg-green-50' 
            : 'border-red-200 bg-red-50'
        }>
          {submissionResult.success ? (
            <CheckCircle className="h-4 w-4" />
          ) : (
            <AlertCircle className="h-4 w-4" />
          )}
          <AlertDescription>
            <div className="space-y-2">
              <p className="font-medium">
                {submissionResult.success ? 'Job Submitted Successfully!' : 'Job Submission Failed'}
              </p>
              <p>{submissionResult.message}</p>
              {submissionResult.success && submissionResult.jobId && (
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium">Job ID:</span>
                  <Badge variant="outline" className="font-mono">
                    {submissionResult.jobId}
                  </Badge>
                </div>
              )}
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium">Destination:</span>
                <Badge className={
                  submissionResult.destination === 'supabase' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-yellow-100 text-yellow-800'
                }>
                  {submissionResult.destination === 'supabase' ? 'Supabase' : 'Legacy'}
                </Badge>
              </div>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* System Information */}
      <Card className="glass-card">
        <CardHeader>
          <CardTitle>System Information</CardTitle>
          <CardDescription>Current job system configuration and capabilities</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="font-medium text-primary-900">Feature Flags</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-primary-600">Supabase Jobs</span>
                  <Badge className={flags.jobs_pg ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                    {flags.jobs_pg ? 'Enabled' : 'Disabled'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-primary-600">Legacy Jobs</span>
                  <Badge className={!flags.jobs_pg ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                    {!flags.jobs_pg ? 'Active' : 'Fallback'}
                  </Badge>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <h4 className="font-medium text-primary-900">Job Families</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-primary-600">Family A (Short)</span>
                  <Badge className="bg-blue-100 text-blue-800">≤ 10s target</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-primary-600">Family B (Cron)</span>
                  <Badge className="bg-green-100 text-green-800">≤ 1min drift</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-primary-600">Family C (Long)</span>
                  <Badge className="bg-purple-100 text-purple-800">Background</Badge>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
