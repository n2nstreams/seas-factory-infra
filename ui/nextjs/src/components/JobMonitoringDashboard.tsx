'use client'

import React, { useState, useEffect } from 'react'
import { useAuth } from '@/components/providers/AuthProvider'
import { jobService, JobStatus, JobMetrics } from '@/lib/job-service'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Play, 
  Pause, 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertTriangle, 
  RefreshCw,
  BarChart3,
  List,
  Settings,
  Trash2
} from 'lucide-react'

interface JobMonitoringDashboardProps {
  tenantId: string
}

export default function JobMonitoringDashboard({ tenantId }: JobMonitoringDashboardProps) {
  const { user } = useAuth()
  const [jobs, setJobs] = useState<JobStatus[]>([])
  const [metrics, setMetrics] = useState<JobMetrics | null>(null)
  const [deadLetterQueue, setDeadLetterQueue] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [selectedTab, setSelectedTab] = useState('overview')

  // Load initial data
  useEffect(() => {
    loadDashboardData()
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(loadDashboardData, 30000)
    
    return () => clearInterval(interval)
  }, [tenantId])

  const loadDashboardData = async () => {
    try {
      setRefreshing(true)
      
      // Load jobs and metrics in parallel
      const [jobsData, metricsData, deadLetterData] = await Promise.all([
        jobService.getTenantJobs(tenantId),
        jobService.getJobMetrics(tenantId),
        jobService.getDeadLetterQueue(tenantId)
      ])
      
      setJobs(jobsData)
      setMetrics(metricsData)
      setDeadLetterQueue(deadLetterData)
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const handleRetryJob = async (jobId: string) => {
    try {
      const success = await jobService.retryJob(jobId, tenantId)
      if (success) {
        await loadDashboardData()
      }
    } catch (error) {
      console.error('Error retrying job:', error)
    }
  }

  const handleCancelJob = async (jobId: string) => {
    try {
      const success = await jobService.cancelJob(jobId, tenantId)
      if (success) {
        await loadDashboardData()
      }
    } catch (error) {
      console.error('Error canceling job:', error)
    }
  }

  const handleResolveDeadLetter = async (entryId: string, notes: string) => {
    try {
      const success = await jobService.resolveDeadLetterEntry(entryId, tenantId, notes, user?.id || 'system')
      if (success) {
        await loadDashboardData()
      }
    } catch (error) {
      console.error('Error resolving dead letter entry:', error)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'succeeded': return 'bg-green-100 text-green-800'
      case 'failed': return 'bg-red-100 text-red-800'
      case 'in_progress': return 'bg-blue-100 text-blue-800'
      case 'queued': return 'bg-yellow-100 text-yellow-800'
      case 'retrying': return 'bg-orange-100 text-orange-800'
      case 'canceled': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getFamilyColor = (family: string) => {
    switch (family) {
      case 'A': return 'bg-blue-100 text-blue-800'
      case 'B': return 'bg-green-100 text-green-800'
      case 'C': return 'bg-purple-100 text-purple-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getSLAStatusColor = (slaStatus?: string) => {
    switch (slaStatus) {
      case 'within_sla': return 'bg-green-100 text-green-800'
      case 'sla_breach': return 'bg-yellow-100 text-yellow-800'
      case 'failed': return 'bg-red-100 text-red-800'
      case 'timeout': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDuration = (ms?: number) => {
    if (!ms) return 'N/A'
    if (ms < 1000) return `${ms}ms`
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
    return `${(ms / 60000).toFixed(1)}m`
  }

  const formatDateTime = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString()
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center">
        <div className="glass-card text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-primary-600">Loading job monitoring dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-primary-900">Job Monitoring Dashboard</h1>
            <p className="text-primary-600">Real-time monitoring and management of background jobs</p>
          </div>
          <Button 
            onClick={loadDashboardData} 
            disabled={refreshing}
            className="glass-button"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {/* Metrics Overview */}
        {metrics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <Card className="glass-card">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Jobs</CardTitle>
                <BarChart3 className="h-4 w-4 text-primary-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-primary-900">{metrics.total_jobs}</div>
                <p className="text-xs text-primary-600">All time</p>
              </CardContent>
            </Card>

            <Card className="glass-card">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">SLA Compliance</CardTitle>
                <CheckCircle className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{metrics.sla_compliance_rate.toFixed(1)}%</div>
                <Progress value={metrics.sla_compliance_rate} className="mt-2" />
              </CardContent>
            </Card>

            <Card className="glass-card">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg Execution Time</CardTitle>
                <Clock className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">{formatDuration(metrics.avg_execution_time_ms)}</div>
                <p className="text-xs text-blue-600">Per job</p>
              </CardContent>
            </Card>

            <Card className="glass-card">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Failed Jobs</CardTitle>
                <XCircle className="h-4 w-4 text-red-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">{metrics.failed_jobs_count}</div>
                <p className="text-xs text-red-600">Retry rate: {metrics.retry_rate.toFixed(1)}%</p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Main Content Tabs */}
        <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 glass-card">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="jobs">Active Jobs</TabsTrigger>
            <TabsTrigger value="deadletter">Dead Letter</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Job Status Distribution */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle>Job Status Distribution</CardTitle>
                <CardDescription>Current distribution of jobs by status</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                  {metrics && Object.entries(metrics.jobs_by_status).map(([status, count]) => (
                    <div key={status} className="text-center">
                      <div className="text-2xl font-bold text-primary-900">{count}</div>
                      <Badge className={getStatusColor(status)}>{status}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Job Family Distribution */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle>Job Family Distribution</CardTitle>
                <CardDescription>Jobs categorized by execution type</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4">
                  {metrics && Object.entries(metrics.jobs_by_family).map(([family, count]) => (
                    <div key={family} className="text-center">
                      <div className="text-2xl font-bold text-primary-900">{count}</div>
                      <Badge className={getFamilyColor(family)}>
                        {family === 'A' ? 'Short' : family === 'B' ? 'Cron' : 'Long'}
                      </Badge>
                      <p className="text-xs text-primary-600 mt-1">
                        {family === 'A' ? 'Quick tasks' : family === 'B' ? 'Scheduled' : 'Background'}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle>Recent Job Activity</CardTitle>
                <CardDescription>Latest job executions and status changes</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {jobs.slice(0, 5).map((job) => (
                    <div key={job.id} className="flex items-center justify-between p-3 bg-white/50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <Badge className={getStatusColor(job.status)}>{job.status}</Badge>
                        <div>
                          <p className="font-medium text-primary-900">{job.job_name}</p>
                          <p className="text-sm text-primary-600">
                            Queued: {formatDateTime(job.queued_at)}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getFamilyColor(job.job_family)}>{job.job_family}</Badge>
                        {job.execution_time_ms && (
                          <span className="text-sm text-primary-600">
                            {formatDuration(job.execution_time_ms)}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Jobs Tab */}
          <TabsContent value="jobs" className="space-y-6">
            <Card className="glass-card">
              <CardHeader>
                <CardTitle>Active Jobs</CardTitle>
                <CardDescription>Monitor and manage running and queued jobs</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {jobs.map((job) => (
                    <div key={job.id} className="border border-primary-200 rounded-lg p-4 bg-white/50">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <h3 className="font-semibold text-primary-900">{job.job_name}</h3>
                          <Badge className={getStatusColor(job.status)}>{job.status}</Badge>
                          <Badge className={getFamilyColor(job.job_family)}>{job.job_family}</Badge>
                          {job.sla_status && (
                            <Badge className={getSLAStatusColor(job.sla_status)}>
                              {job.sla_status.replace('_', ' ')}
                            </Badge>
                          )}
                        </div>
                        <div className="flex items-center space-x-2">
                          {job.status === 'failed' && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleRetryJob(job.id)}
                              className="text-orange-600 border-orange-200 hover:bg-orange-50"
                            >
                              <RefreshCw className="w-3 h-3 mr-1" />
                              Retry
                            </Button>
                          )}
                          {(job.status === 'queued' || job.status === 'in_progress') && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleCancelJob(job.id)}
                              className="text-red-600 border-red-200 hover:bg-red-50"
                            >
                              <XCircle className="w-3 h-3 mr-1" />
                              Cancel
                            </Button>
                          )}
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-primary-600">Priority:</span>
                          <span className="ml-2 font-medium">{job.priority}</span>
                        </div>
                        <div>
                          <span className="text-primary-600">Retries:</span>
                          <span className="ml-2 font-medium">{job.retry_count}/{job.max_retries}</span>
                        </div>
                        <div>
                          <span className="text-primary-600">Queued:</span>
                          <span className="ml-2 font-medium">{formatDateTime(job.queued_at)}</span>
                        </div>
                        {job.started_at && (
                          <div>
                            <span className="text-primary-600">Started:</span>
                            <span className="ml-2 font-medium">{formatDateTime(job.started_at)}</span>
                          </div>
                        )}
                      </div>

                      {job.execution_time_ms && (
                        <div className="mt-3 pt-3 border-t border-primary-200">
                          <span className="text-primary-600">Execution Time:</span>
                          <span className="ml-2 font-medium">{formatDuration(job.execution_time_ms)}</span>
                        </div>
                      )}
                    </div>
                  ))}

                  {jobs.length === 0 && (
                    <div className="text-center py-8 text-primary-600">
                      <List className="w-12 h-12 mx-auto mb-4 text-primary-400" />
                      <p>No jobs found</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Dead Letter Tab */}
          <TabsContent value="deadletter" className="space-y-6">
            <Card className="glass-card">
              <CardHeader>
                <CardTitle>Dead Letter Queue</CardTitle>
                <CardDescription>Failed jobs that exceeded retry limits</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {deadLetterQueue.map((entry) => (
                    <div key={entry.id} className="border border-red-200 rounded-lg p-4 bg-red-50/50">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <AlertTriangle className="w-5 h-5 text-red-600" />
                          <h3 className="font-semibold text-red-900">
                            {entry.job_data_snapshot?.job_name || 'Unknown Job'}
                          </h3>
                          <Badge className="bg-red-100 text-red-800">
                            {entry.remediation_status}
                          </Badge>
                        </div>
                        <div className="text-sm text-red-600">
                          {formatDateTime(entry.last_failure_at)}
                        </div>
                      </div>

                      <div className="mb-3">
                        <p className="text-sm text-red-700">
                          <strong>Failure Reason:</strong> {entry.failure_reason}
                        </p>
                        <p className="text-sm text-red-600 mt-1">
                          <strong>Failure Count:</strong> {entry.failure_count}
                        </p>
                      </div>

                      {entry.remediation_status === 'pending' && (
                        <div className="flex space-x-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleResolveDeadLetter(entry.id, 'Investigated and resolved')}
                            className="text-green-600 border-green-200 hover:bg-green-50"
                          >
                            <CheckCircle className="w-3 h-3 mr-1" />
                            Mark Resolved
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleResolveDeadLetter(entry.id, 'Archived without action')}
                            className="text-gray-600 border-gray-200 hover:bg-gray-50"
                          >
                            <Trash2 className="w-3 h-3 mr-1" />
                            Archive
                          </Button>
                        </div>
                      )}

                      {entry.remediation_notes && (
                        <div className="mt-3 pt-3 border-t border-red-200">
                          <p className="text-sm text-red-700">
                            <strong>Notes:</strong> {entry.remediation_notes}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}

                  {deadLetterQueue.length === 0 && (
                    <div className="text-center py-8 text-primary-600">
                      <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-400" />
                      <p>No dead letter entries found</p>
                      <p className="text-sm text-primary-500">All jobs are processing successfully</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="space-y-6">
            <Card className="glass-card">
              <CardHeader>
                <CardTitle>Job System Settings</CardTitle>
                <CardDescription>Configure job processing and monitoring</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-white/50 rounded-lg">
                    <div>
                      <h4 className="font-medium text-primary-900">Auto-retry Failed Jobs</h4>
                      <p className="text-sm text-primary-600">Automatically retry failed jobs with exponential backoff</p>
                    </div>
                    <Button variant="outline" size="sm">
                      <Settings className="w-4 h-4 mr-2" />
                      Configure
                    </Button>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-white/50 rounded-lg">
                    <div>
                      <h4 className="font-medium text-primary-900">Job Cleanup</h4>
                      <p className="text-sm text-primary-600">Automatically clean up old completed jobs after 30 days</p>
                    </div>
                    <Button variant="outline" size="sm">
                      <Settings className="w-4 h-4 mr-2" />
                      Configure
                    </Button>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-white/50 rounded-lg">
                    <div>
                      <h4 className="font-medium text-primary-900">SLA Monitoring</h4>
                      <p className="text-sm text-primary-600">Alert when jobs exceed SLA thresholds</p>
                    </div>
                    <Button variant="outline" size="sm">
                      <Settings className="w-4 h-4 mr-2" />
                      Configure
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
