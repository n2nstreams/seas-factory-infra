'use client'

import { useState, useEffect } from 'react'
import { useHealthMonitoring } from '@/components/providers/ObservabilityProvider'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Database, 
  Eye, 
  EyeOff, 
  RefreshCw, 
  Server, 
  Shield, 
  Storage, 
  TrendingUp,
  TrendingDown,
  Minus
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'

// Health status indicator component
function HealthStatusIndicator({ status, size = 'default' }: { status: 'healthy' | 'degraded' | 'unhealthy'; size?: 'small' | 'default' | 'large' }) {
  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'healthy':
        return { color: 'bg-green-500', icon: CheckCircle, text: 'Healthy' }
      case 'degraded':
        return { color: 'bg-yellow-500', icon: AlertTriangle, text: 'Degraded' }
      case 'unhealthy':
        return { color: 'bg-red-500', icon: AlertTriangle, text: 'Unhealthy' }
      default:
        return { color: 'bg-gray-500', icon: Minus, text: 'Unknown' }
    }
  }

  const config = getStatusConfig(status)
  const Icon = config.icon

  const sizeClasses = {
    small: 'w-2 h-2',
    default: 'w-3 h-3',
    large: 'w-4 h-4'
  }

  return (
    <div className="flex items-center gap-2">
      <div className={`${config.color} ${sizeClasses[size]} rounded-full`} />
      <Icon className={`w-4 h-4 ${status === 'healthy' ? 'text-green-600' : status === 'degraded' ? 'text-yellow-600' : 'text-red-600'}`} />
      <span className={`text-sm font-medium ${status === 'healthy' ? 'text-green-600' : status === 'degraded' ? 'text-yellow-600' : 'text-red-600'}`}>
        {config.text}
      </span>
    </div>
  )
}

// Health check detail component
function HealthCheckDetail({ 
  name, 
  check, 
  isExpanded, 
  onToggle 
}: { 
  name: string; 
  check: any; 
  isExpanded: boolean; 
  onToggle: () => void 
}) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pass': return 'text-green-600 bg-green-100'
      case 'warn': return 'text-yellow-600 bg-yellow-100'
      case 'fail': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass': return <CheckCircle className="w-4 h-4" />
      case 'warn': return <AlertTriangle className="w-4 h-4" />
      case 'fail': return <AlertTriangle className="w-4 h-4" />
      default: return <Minus className="w-4 h-4" />
    }
  }

  return (
    <div className="border rounded-lg p-3 space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge className={getStatusColor(check.status)}>
            {getStatusIcon(check.status)}
            <span className="ml-1 capitalize">{check.status}</span>
          </Badge>
          <span className="font-medium">{name}</span>
        </div>
        <Button variant="ghost" size="sm" onClick={onToggle}>
          {isExpanded ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
        </Button>
      </div>
      
      {isExpanded && (
        <div className="space-y-2 text-sm">
          {check.responseTime && (
            <div className="flex justify-between">
              <span>Response Time:</span>
              <span className="font-mono">{check.responseTime}ms</span>
            </div>
          )}
          {check.error && (
            <div className="text-red-600">
              <span className="font-medium">Error:</span> {check.error}
            </div>
          )}
          {check.details && (
            <div>
              <span className="font-medium">Details:</span>
              <pre className="mt-1 p-2 bg-gray-50 rounded text-xs overflow-x-auto">
                {JSON.stringify(check.details, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// Metrics chart component
function MetricsChart({ data, title, dataKey, color = '#10b981' }: { 
  data: any[]; 
  title: string; 
  dataKey: string; 
  color?: string 
}) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-32 text-gray-500">
        No data available
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-medium text-gray-700">{title}</h4>
      <ResponsiveContainer width="100%" height={120}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="timestamp" 
            tickFormatter={(value) => new Date(value).toLocaleTimeString()}
            fontSize={10}
          />
          <YAxis fontSize={10} />
          <Tooltip 
            labelFormatter={(value) => new Date(value).toLocaleString()}
            formatter={(value: any) => [value, title]}
          />
          <Line type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

// Main health monitoring dashboard component
export default function HealthMonitoringDashboard() {
  const {
    currentHealth,
    healthHistory,
    metricsHistory,
    isMonitoring,
    startMonitoring,
    stopMonitoring,
    runHealthCheck
  } = useHealthMonitoring()

  const [expandedChecks, setExpandedChecks] = useState<Set<string>>(new Set())
  const [autoRefresh, setAutoRefresh] = useState(true)

  // Auto-refresh effect
  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      if (isMonitoring) {
        runHealthCheck()
      }
    }, 30000) // Refresh every 30 seconds

    return () => clearInterval(interval)
  }, [autoRefresh, isMonitoring, runHealthCheck])

  // Toggle check expansion
  const toggleCheckExpansion = (checkName: string) => {
    const newExpanded = new Set(expandedChecks)
    if (newExpanded.has(checkName)) {
      newExpanded.delete(checkName)
    } else {
      newExpanded.add(checkName)
    }
    setExpandedChecks(newExpanded)
  }

  // Format timestamp for display
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString()
  }

  // Get health trend
  const getHealthTrend = () => {
    if (healthHistory.length < 2) return { trend: 'stable', change: 0 }
    
    const recent = healthHistory.slice(-5)
    const firstHalf = recent.slice(0, Math.floor(recent.length / 2))
    const secondHalf = recent.slice(Math.floor(recent.length / 2))
    
    const firstAvg = firstHalf.reduce((sum, check) => sum + check.summary.overallHealth, 0) / firstHalf.length
    const secondAvg = secondHalf.reduce((sum, check) => sum + check.summary.overallHealth, 0) / secondHalf.length
    
    const change = secondAvg - firstAvg
    
    if (change > 5) return { trend: 'improving', change: Math.round(change) }
    if (change < -5) return { trend: 'declining', change: Math.round(change) }
    return { trend: 'stable', change: Math.round(change) }
  }

  const healthTrend = getHealthTrend()

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Health Monitoring Dashboard</h1>
          <p className="text-gray-600 mt-1">Real-time system health and performance monitoring</p>
        </div>
        
        <div className="flex items-center gap-3">
          <Button
            variant={isMonitoring ? "destructive" : "default"}
            onClick={isMonitoring ? stopMonitoring : () => startMonitoring()}
            className="flex items-center gap-2"
          >
            {isMonitoring ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            {isMonitoring ? 'Stop Monitoring' : 'Start Monitoring'}
          </Button>
          
          <Button
            variant="outline"
            onClick={() => runHealthCheck()}
            className="flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Run Health Check
          </Button>
        </div>
      </div>

      {/* Current Status Overview */}
      {currentHealth && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Overall Status</CardTitle>
            </CardHeader>
            <CardContent>
              <HealthStatusIndicator status={currentHealth.status} size="large" />
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Health Score</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="text-2xl font-bold text-gray-900">
                  {currentHealth.summary.overallHealth}%
                </div>
                <Progress value={currentHealth.summary.overallHealth} className="h-2" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Checks Passed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {currentHealth.summary.passedChecks}/{currentHealth.summary.totalChecks}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                {currentHealth.summary.failedChecks} failed, {currentHealth.summary.warningChecks} warnings
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Health Trend</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                {healthTrend.trend === 'improving' ? (
                  <TrendingUp className="w-5 h-5 text-green-600" />
                ) : healthTrend.trend === 'declining' ? (
                  <TrendingDown className="w-5 h-5 text-red-600" />
                ) : (
                  <Minus className="w-5 h-5 text-gray-600" />
                )}
                <span className={`text-sm font-medium ${
                  healthTrend.trend === 'improving' ? 'text-green-600' : 
                  healthTrend.trend === 'declining' ? 'text-red-600' : 
                  'text-gray-600'
                }`}>
                  {healthTrend.trend.charAt(0).toUpperCase() + healthTrend.trend.slice(1)}
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                {healthTrend.change > 0 ? '+' : ''}{healthTrend.change}% change
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="details">Health Checks</TabsTrigger>
          <TabsTrigger value="metrics">Metrics</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Health Checks Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="w-5 h-5" />
                  Health Checks Summary
                </CardTitle>
                <CardDescription>
                  Current status of all monitored services
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {currentHealth && Object.entries(currentHealth.checks).map(([name, check]) => (
                  <div key={name} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      {name === 'supabase-database' && <Database className="w-4 h-4 text-blue-600" />}
                      {name === 'supabase-auth' && <Shield className="w-4 h-4 text-green-600" />}
                      {name === 'supabase-storage' && <Storage className="w-4 h-4 text-purple-600" />}
                      {name === 'backend-api' && <Server className="w-4 h-4 text-orange-600" />}
                      {name === 'frontend' && <Activity className="w-4 h-4 text-indigo-600" />}
                      
                      <span className="font-medium">{name.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                    </div>
                    
                    <Badge className={
                      check.status === 'pass' ? 'bg-green-100 text-green-800' :
                      check.status === 'warn' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }>
                      {check.status === 'pass' ? <CheckCircle className="w-3 h-3 mr-1" /> :
                       check.status === 'warn' ? <AlertTriangle className="w-3 h-3 mr-1" /> :
                       <AlertTriangle className="w-3 h-3 mr-1" />}
                      {check.status}
                    </Badge>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Recent Metrics */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Recent Metrics
                </CardTitle>
                <CardDescription>
                  Performance metrics over time
                </CardDescription>
              </CardHeader>
              <CardContent>
                {metricsHistory.length > 0 ? (
                  <MetricsChart 
                    data={metricsHistory.slice(-20)} 
                    title="Overall Health Score" 
                    dataKey="overallScore"
                    color="#10b981"
                  />
                ) : (
                  <div className="text-center text-gray-500 py-8">
                    No metrics data available yet
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Details Tab */}
        <TabsContent value="details" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Detailed Health Checks</CardTitle>
              <CardDescription>
                Expand each check to see detailed information
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {currentHealth && Object.entries(currentHealth.checks).map(([name, check]) => (
                <HealthCheckDetail
                  key={name}
                  name={name}
                  check={check}
                  isExpanded={expandedChecks.has(name)}
                  onToggle={() => toggleCheckExpansion(name)}
                />
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Metrics Tab */}
        <TabsContent value="metrics" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Error Rate</CardTitle>
                <CardDescription>System error rate over time</CardDescription>
              </CardHeader>
              <CardContent>
                <MetricsChart 
                  data={metricsHistory.slice(-20)} 
                  title="Error Rate" 
                  dataKey="errorRate"
                  color="#ef4444"
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Response Time</CardTitle>
                <CardDescription>Average response time over time</CardDescription>
              </CardHeader>
              <CardContent>
                <MetricsChart 
                  data={metricsHistory.slice(-20)} 
                  title="Response Time (ms)" 
                  dataKey="responseTime"
                  color="#f59e0b"
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Uptime</CardTitle>
                <CardDescription>System uptime percentage</CardDescription>
              </CardHeader>
              <CardContent>
                <MetricsChart 
                  data={metricsHistory.slice(-20)} 
                  title="Uptime %" 
                  dataKey="uptime"
                  color="#3b82f6"
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Health Score Trend</CardTitle>
                <CardDescription>Overall health score over time</CardDescription>
              </CardHeader>
              <CardContent>
                <MetricsChart 
                  data={metricsHistory.slice(-20)} 
                  title="Health Score" 
                  dataKey="overallScore"
                  color="#10b981"
                />
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Health Check History</CardTitle>
              <CardDescription>
                Historical health check results
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {healthHistory.slice(-10).reverse().map((check, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <HealthStatusIndicator status={check.status} size="small" />
                      <span className="text-sm text-gray-600">
                        {formatTimestamp(check.timestamp)}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm">
                      <span>Score: {check.summary.overallHealth}%</span>
                      <span className="text-green-600">
                        {check.summary.passedChecks}/{check.summary.totalChecks} passed
                      </span>
                      {check.summary.failedChecks > 0 && (
                        <span className="text-red-600">{check.summary.failedChecks} failed</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Footer */}
      <div className="text-center text-sm text-gray-500">
        <p>Last updated: {currentHealth ? formatTimestamp(currentHealth.timestamp) : 'Never'}</p>
        <p>Monitoring status: {isMonitoring ? 'Active' : 'Inactive'}</p>
      </div>
    </div>
  )
}
