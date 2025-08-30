'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Activity, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  RefreshCw, 
  Database, 
  Shield, 
  Zap,
  Clock,
  TrendingUp
} from 'lucide-react'

interface HealthCheckResult {
  status: 'pass' | 'fail' | 'warn'
  responseTime?: number
  error?: string
  details?: any
  timestamp: string
}

interface HealthSummary {
  totalChecks: number
  passedChecks: number
  failedChecks: number
  warningChecks: number
  overallHealth: number
}

interface HealthData {
  status: string
  timestamp: string
  version: string
  environment: string
  uptime: number
  checks: Record<string, HealthCheckResult>
  summary: HealthSummary
  responseTime: number
  correlationId: string
}

interface HealthMetrics {
  timestamp: string
  errorRate: number
  responseTime: number
  uptime: number
  overallScore: number
}

export default function HealthDashboard() {
  const [healthData, setHealthData] = useState<HealthData | null>(null)
  const [metrics, setMetrics] = useState<HealthMetrics[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch health data
  const fetchHealthData = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      const response = await fetch('/api/health', {
        headers: {
          'X-Correlation-ID': `health-dashboard-${Date.now()}`
        }
      })
      
      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`)
      }
      
      const data = await response.json()
      setHealthData(data)
      setLastUpdate(new Date())
      
      // Add to metrics history
      if (data.summary) {
        const newMetric: HealthMetrics = {
          timestamp: new Date().toISOString(),
          errorRate: data.summary.failedChecks / data.summary.totalChecks,
          responseTime: data.responseTime || 0,
          uptime: data.uptime || 0,
          overallScore: data.summary.overallHealth
        }
        setMetrics(prev => [...prev.slice(-50), newMetric]) // Keep last 50 metrics
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      console.error('Health check error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  // Auto-refresh effect
  useEffect(() => {
    if (!autoRefresh) return
    
    const interval = setInterval(fetchHealthData, 30000) // 30 seconds
    return () => clearInterval(interval)
  }, [autoRefresh])

  // Initial fetch
  useEffect(() => {
    fetchHealthData()
  }, [])

  // Get status icon and color
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'fail':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'warn':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      default:
        return <AlertTriangle className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pass':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'fail':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'warn':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getOverallStatusColor = (health: number) => {
    if (health >= 90) return 'text-green-600'
    if (health >= 70) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <XCircle className="h-4 w-4" />
        <AlertTitle>Health Check Error</AlertTitle>
        <AlertDescription>
          {error}
          <Button 
            variant="outline" 
            size="sm" 
            className="ml-2"
            onClick={fetchHealthData}
          >
            Retry
          </Button>
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Health Monitoring Dashboard</h1>
          <p className="text-muted-foreground">
            Module 5: Health Monitoring & Environment Configuration Cleanup
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={fetchHealthData}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button
            variant={autoRefresh ? 'default' : 'outline'}
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            <Clock className="h-4 w-4 mr-2" />
            {autoRefresh ? 'Auto' : 'Manual'}
          </Button>
        </div>
      </div>

      {/* Overall Health Status */}
      {healthData && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="h-5 w-5" />
              <span>Overall System Health</span>
            </CardTitle>
            <CardDescription>
              Last updated: {lastUpdate?.toLocaleTimeString()}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className={`text-3xl font-bold ${getOverallStatusColor(healthData.summary.overallHealth)}`}>
                  {healthData.summary.overallHealth}%
                </div>
                <div className="text-sm text-muted-foreground">Health Score</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">
                  {healthData.summary.passedChecks}
                </div>
                <div className="text-sm text-muted-foreground">Passed Checks</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-red-600">
                  {healthData.summary.failedChecks}
                </div>
                <div className="text-sm text-muted-foreground">Failed Checks</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-yellow-600">
                  {healthData.summary.warningChecks}
                </div>
                <div className="text-sm text-muted-foreground">Warnings</div>
              </div>
            </div>
            
            <div className="mt-4">
              <Progress value={healthData.summary.overallHealth} className="h-2" />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Health Checks */}
      {healthData && (
        <Card>
          <CardHeader>
            <CardTitle>Health Check Details</CardTitle>
            <CardDescription>
              Individual service health status and response times
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(healthData.checks).map(([name, check]) => (
                <div key={name} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(check.status)}
                    <div>
                      <div className="font-medium capitalize">{name.replace('-', ' ')}</div>
                      {check.error && (
                        <div className="text-sm text-red-600">{check.error}</div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    {check.responseTime && (
                      <Badge variant="outline">
                        <Zap className="h-3 w-3 mr-1" />
                        {check.responseTime}ms
                      </Badge>
                    )}
                    <Badge className={getStatusColor(check.status)}>
                      {check.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* System Information */}
      {healthData && (
        <Card>
          <CardHeader>
            <CardTitle>System Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="text-sm font-medium text-muted-foreground">Version</div>
                <div className="text-lg">{healthData.version}</div>
              </div>
              <div>
                <div className="text-sm font-medium text-muted-foreground">Environment</div>
                <div className="text-lg capitalize">{healthData.environment}</div>
              </div>
              <div>
                <div className="text-sm font-medium text-muted-foreground">Uptime</div>
                <div className="text-lg">{Math.floor(healthData.uptime / 3600)}h {Math.floor((healthData.uptime % 3600) / 60)}m</div>
              </div>
              <div>
                <div className="text-sm font-medium text-muted-foreground">Response Time</div>
                <div className="text-lg">{healthData.responseTime}ms</div>
              </div>
            </div>
            {healthData.correlationId && (
              <div className="mt-4">
                <div className="text-sm font-medium text-muted-foreground">Correlation ID</div>
                <div className="text-sm font-mono bg-gray-100 p-2 rounded">
                  {healthData.correlationId}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Metrics History */}
      {metrics.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Health Metrics History</CardTitle>
            <CardDescription>
              Historical health data and trends
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="overview" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="trends">Trends</TabsTrigger>
                <TabsTrigger value="details">Details</TabsTrigger>
              </TabsList>
              
              <TabsContent value="overview" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {metrics.length}
                    </div>
                    <div className="text-sm text-muted-foreground">Data Points</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {Math.round(metrics.reduce((acc, m) => acc + m.overallScore, 0) / metrics.length)}%
                    </div>
                    <div className="text-sm text-muted-foreground">Avg Health</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {Math.round(metrics.reduce((acc, m) => acc + m.responseTime, 0) / metrics.length)}ms
                    </div>
                    <div className="text-sm text-muted-foreground">Avg Response</div>
                  </div>
                </div>
              </TabsContent>
              
              <TabsContent value="trends" className="space-y-4">
                <div className="h-64 flex items-center justify-center text-muted-foreground">
                  <TrendingUp className="h-8 w-8 mr-2" />
                  Health trends visualization (coming soon)
                </div>
              </TabsContent>
              
              <TabsContent value="details" className="space-y-4">
                <div className="max-h-64 overflow-y-auto">
                  {metrics.slice().reverse().map((metric, index) => (
                    <div key={index} className="flex items-center justify-between p-2 border-b">
                      <div className="text-sm">
                        {new Date(metric.timestamp).toLocaleTimeString()}
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">{Math.round(metric.overallScore)}%</Badge>
                        <Badge variant="outline">{metric.responseTime}ms</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}

      {/* Module 5 Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="h-5 w-5" />
            <span>Module 5 Status</span>
          </CardTitle>
          <CardDescription>
            Health Monitoring & Environment Configuration Cleanup
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span>Health Monitoring Migration</span>
              <Badge className="bg-green-100 text-green-800 border-green-200">
                Complete
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span>Legacy References Cleanup</span>
              <Badge className="bg-green-100 text-green-800 border-green-200">
                Complete
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span>Environment Configuration</span>
              <Badge className="bg-green-100 text-green-800 border-green-200">
                Complete
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span>Feature Flag Configuration</span>
              <Badge className="bg-green-100 text-green-800 border-green-200">
                Complete
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
