'use client'

import React, { useState } from 'react'
import { useAuth } from '@/components/providers/AuthProvider'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import Navigation from '@/components/Navigation'
import JobSubmissionForm from '@/components/JobSubmissionForm'
import JobMonitoringDashboard from '@/components/JobMonitoringDashboard'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Play, 
  BarChart3, 
  Settings, 
  Info,
  CheckCircle,
  AlertTriangle
} from 'lucide-react'

export default function JobsPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const [selectedTab, setSelectedTab] = useState('submit')
  const [recentJobId, setRecentJobId] = useState<string | null>(null)

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/app2/signin')
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

  if (!user) {
    return null // Will redirect
  }

  const handleJobSubmitted = (jobId: string) => {
    setRecentJobId(jobId)
    setSelectedTab('monitor')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100">
      <Navigation />
      
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-3 bg-primary-100 rounded-lg">
                <Play className="w-8 h-8 text-primary-600" />
              </div>
              <div>
                <h1 className="text-4xl font-bold text-primary-900">Jobs & Scheduling</h1>
                <p className="text-lg text-primary-600">Module 5: Background Job Processing Migration</p>
              </div>
            </div>
            
            {/* Migration Status */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <Card className="glass-card border-green-200">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <div>
                      <p className="font-medium text-green-900">Supabase Jobs</p>
                      <p className="text-sm text-green-600">Ready for migration</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="glass-card border-blue-200">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <BarChart3 className="w-5 h-5 text-blue-600" />
                    <div>
                      <p className="font-medium text-blue-900">Monitoring</p>
                      <p className="text-sm text-blue-600">Real-time dashboard</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="glass-card border-purple-200">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <Settings className="w-5 h-5 text-purple-600" />
                    <div>
                      <p className="font-medium text-purple-900">Feature Flags</p>
                      <p className="text-sm text-purple-600">Controlled rollout</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Job Alert */}
            {recentJobId && (
              <Card className="glass-card border-green-200 bg-green-50/50 mb-6">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <div>
                        <p className="font-medium text-green-900">Job Submitted Successfully!</p>
                        <p className="text-sm text-green-600">
                          Job ID: <Badge variant="outline" className="font-mono">{recentJobId}</Badge>
                        </p>
                      </div>
                    </div>
                    <Badge className="bg-green-100 text-green-800">
                      View in Monitor
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Main Content Tabs */}
          <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
            <TabsList className="grid w-full grid-cols-3 glass-card">
              <TabsTrigger value="submit">Submit Jobs</TabsTrigger>
              <TabsTrigger value="monitor">Monitor & Manage</TabsTrigger>
              <TabsTrigger value="info">System Info</TabsTrigger>
            </TabsList>

            {/* Submit Jobs Tab */}
            <TabsContent value="submit" className="space-y-6">
              <JobSubmissionForm 
                tenantId={user.tenant_id || '00000000-0000-0000-0000-000000000000'}
                onJobSubmitted={handleJobSubmitted}
              />
            </TabsContent>

            {/* Monitor & Manage Tab */}
            <TabsContent value="monitor" className="space-y-6">
              <JobMonitoringDashboard 
                tenantId={user.tenant_id || '00000000-0000-0000-0000-000000000000'}
              />
            </TabsContent>

            {/* System Info Tab */}
            <TabsContent value="info" className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Migration Overview */}
                <Card className="glass-card">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Info className="w-5 h-5 text-primary-600" />
                      <span>Migration Overview</span>
                    </CardTitle>
                    <CardDescription>
                      Current status of the Jobs & Scheduling migration
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                        <span className="text-sm font-medium text-green-900">Database Schema</span>
                        <Badge className="bg-green-100 text-green-800">Complete</Badge>
                      </div>
                      
                      <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                        <span className="text-sm font-medium text-green-900">Edge Functions</span>
                        <Badge className="bg-green-100 text-green-800">Ready</Badge>
                      </div>
                      
                      <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                        <span className="text-sm font-medium text-blue-900">Feature Flags</span>
                        <Badge className="bg-blue-100 text-blue-800">Active</Badge>
                      </div>
                      
                      <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                        <span className="text-sm font-medium text-yellow-900">Legacy System</span>
                        <Badge className="bg-yellow-100 text-yellow-800">Fallback</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Job Families */}
                <Card className="glass-card">
                  <CardHeader>
                    <CardTitle>Job Families</CardTitle>
                    <CardDescription>
                      Categorization of jobs by execution characteristics
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-3">
                      <div className="p-3 bg-blue-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-blue-900">Family A: Short Jobs</span>
                          <Badge className="bg-blue-100 text-blue-800">≤ 10s</Badge>
                        </div>
                        <p className="text-sm text-blue-700">
                          Quick tasks like security scans, code generation, and email sending.
                          Target: p95 ≤ 10s execution time.
                        </p>
                      </div>
                      
                      <div className="p-3 bg-green-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-green-900">Family B: Cron Jobs</span>
                          <Badge className="bg-green-100 text-green-800">≤ 1min</Badge>
                        </div>
                        <p className="text-sm text-green-700">
                          Scheduled tasks like health checks, backup cleanup, and maintenance.
                          Target: ≤ 1 minute drift from schedule.
                        </p>
                      </div>
                      
                      <div className="p-3 bg-purple-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-purple-900">Family C: Long Jobs</span>
                          <Badge className="bg-purple-100 text-purple-800">Background</Badge>
                        </div>
                        <p className="text-sm text-purple-700">
                          Background processes like data migration, ETL, and batch processing.
                          No strict time limits, but monitored for progress.
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Migration Benefits */}
                <Card className="glass-card">
                  <CardHeader>
                    <CardTitle>Migration Benefits</CardTitle>
                    <CardDescription>
                      Advantages of moving to the new job system
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-start space-x-3">
                      <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                      <div>
                        <p className="font-medium text-green-900">Better Performance</p>
                        <p className="text-sm text-green-700">
                          Optimized database queries and connection pooling
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-start space-x-3">
                      <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                      <div>
                        <p className="font-medium text-green-900">Real-time Monitoring</p>
                        <p className="text-sm text-green-700">
                          Live dashboard with SLA tracking and metrics
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-start space-x-3">
                      <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                      <div>
                        <p className="font-medium text-green-900">Improved Reliability</p>
                        <p className="text-sm text-green-700">
                          Dead letter queue, retry logic, and idempotency
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-start space-x-3">
                      <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                      <div>
                        <p className="font-medium text-green-900">Cost Optimization</p>
                        <p className="text-sm text-green-700">
                          Serverless execution with automatic scaling
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Rollback Plan */}
                <Card className="glass-card">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <AlertTriangle className="w-5 h-5 text-orange-600" />
                      <span>Rollback Plan</span>
                    </CardTitle>
                    <CardDescription>
                      How to revert to the legacy system if needed
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="p-3 bg-orange-50 rounded-lg">
                      <p className="text-sm text-orange-800">
                        <strong>Feature Flag Control:</strong> Disable the <code>jobs_pg</code> flag to instantly revert all job submissions to the legacy system.
                      </p>
                    </div>
                    
                    <div className="p-3 bg-orange-50 rounded-lg">
                      <p className="text-sm text-orange-800">
                        <strong>Dual-Write Mode:</strong> The system maintains both job queues during migration, ensuring no job loss.
                      </p>
                    </div>
                    
                    <div className="p-3 bg-orange-50 rounded-lg">
                      <p className="text-sm text-orange-800">
                        <strong>Data Preservation:</strong> All job data and metrics are preserved in Supabase for analysis and recovery.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}
