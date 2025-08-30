'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { 
  Activity, 
  AlertTriangle, 
  BarChart3, 
  DollarSign, 
  Play, 
  Square, 
  TrendingUp, 
  Zap,
  Clock,
  Users,
  Target,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react'

import { 
  performanceMonitoring, 
  type LoadTestConfig, 
  type LoadTestResult,
  type CostBudget,
  type CostAlert
} from '@/lib/performance-monitoring'

interface PerformanceMonitoringDashboardProps {
  className?: string
}

export function PerformanceMonitoringDashboard({ className }: PerformanceMonitoringDashboardProps) {
  const [isMonitoring, setIsMonitoring] = useState(false)
  const [performanceSummary, setPerformanceSummary] = useState<any>(null)
  const [costSummary, setCostSummary] = useState<any>(null)
  const [loadTests, setLoadTests] = useState<LoadTestResult[]>([])
  const [activeTab, setActiveTab] = useState('overview')
  
  // Load test form state
  const [loadTestForm, setLoadTestForm] = useState<Partial<LoadTestConfig>>({
    testType: 'load',
    target: {
      name: '',
      baseUrl: '',
      endpoints: []
    },
    duration: 5,
    virtualUsers: 10,
    thresholds: {
      httpReqDuration: ['p(95)<2000'],
      httpReqFailed: ['rate<0.1']
    }
  })

  // Update form state
  const updateLoadTestForm = (field: string, value: any) => {
    setLoadTestForm(prev => ({
      ...prev,
      [field]: value
    }))
  }

  // Update nested target field
  const updateTargetField = (field: string, value: any) => {
    setLoadTestForm(prev => ({
      ...prev,
      target: {
        ...prev.target!,
        [field]: value
      }
    }))
  }

  // Update endpoints array
  const updateEndpoints = (endpoints: string) => {
    const endpointsArray = endpoints.split(',').map(e => e.trim()).filter(e => e)
    updateTargetField('endpoints', endpointsArray)
  }

  // Start performance monitoring
  const startMonitoring = async () => {
    try {
      await performanceMonitoring.startMonitoring()
      setIsMonitoring(true)
      console.log('Performance monitoring started')
    } catch (error) {
      console.error('Failed to start monitoring:', error)
    }
  }

  // Stop performance monitoring
  const stopMonitoring = () => {
    performanceMonitoring.stopMonitoring()
    setIsMonitoring(false)
    console.log('Performance monitoring stopped')
  }

  // Start load test
  const startLoadTest = async () => {
    try {
      if (!loadTestForm.target?.name || !loadTestForm.target?.baseUrl || !loadTestForm.target?.endpoints?.length) {
        alert('Please fill in all required fields')
        return
      }

      const testId = await performanceMonitoring.startLoadTest(loadTestForm as LoadTestConfig)
      console.log('Load test started:', testId)
      
      // Reset form
      setLoadTestForm({
        testType: 'load',
        target: {
          name: '',
          baseUrl: '',
          endpoints: []
        },
        duration: 5,
        virtualUsers: 10,
        thresholds: {
          httpReqDuration: ['p(95)<2000'],
          httpReqFailed: ['rate<0.1']
        }
      })
      
      // Refresh load tests
      refreshLoadTests()
      
    } catch (error) {
      console.error('Failed to start load test:', error)
      alert(`Failed to start load test: ${error}`)
    }
  }

  // Cancel load test
  const cancelLoadTest = (testId: string) => {
    const cancelled = performanceMonitoring.cancelLoadTest(testId)
    if (cancelled) {
      refreshLoadTests()
    }
  }

  // Refresh load tests
  const refreshLoadTests = () => {
    setLoadTests(performanceMonitoring.getAllLoadTests())
  }

  // Acknowledge cost alert
  const acknowledgeAlert = (alertId: string) => {
    const acknowledged = performanceMonitoring.acknowledgeCostAlert(alertId)
    if (acknowledged) {
      refreshData()
    }
  }

  // Refresh all data
  const refreshData = () => {
    setPerformanceSummary(performanceMonitoring.getPerformanceSummary())
    setCostSummary(performanceMonitoring.getCostSummary())
    refreshLoadTests()
  }

  // Update cost data (for demo purposes)
  const updateCostData = (service: string, spend: number) => {
    performanceMonitoring.updateCostData(service, spend)
    refreshData()
  }

  // Load data on component mount
  useEffect(() => {
    refreshData()
    
    // Set up refresh interval
    const interval = setInterval(refreshData, 5000)
    
    return () => clearInterval(interval)
  }, [])

  // Get status color for load test
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800'
      case 'running': return 'bg-blue-100 text-blue-800'
      case 'failed': return 'bg-red-100 text-red-800'
      case 'cancelled': return 'bg-gray-100 text-gray-800'
      default: return 'bg-yellow-100 text-yellow-800'
    }
  }

  // Get severity color for cost alerts
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'emergency': return 'bg-red-100 text-red-800'
      case 'critical': return 'bg-orange-100 text-orange-800'
      case 'warning': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  // Format percentage
  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`
  }

  // Format duration
  const formatDuration = (minutes: number) => {
    if (minutes < 60) return `${minutes}m`
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return `${hours}h ${mins}m`
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Performance & Cost Monitoring</h1>
          <p className="text-muted-foreground">
            Comprehensive monitoring dashboard for performance metrics, cost controls, and load testing
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant={isMonitoring ? "destructive" : "default"}
            onClick={isMonitoring ? stopMonitoring : startMonitoring}
            className="flex items-center space-x-2"
          >
            {isMonitoring ? (
              <>
                <Square className="h-4 w-4" />
                Stop Monitoring
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                Start Monitoring
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Main Dashboard */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="costs">Cost Monitoring</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="loadtesting">Load Testing</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Key Metrics Cards */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Budget</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {costSummary ? formatCurrency(costSummary.totalMonthlyBudget) : '$0'}
                </div>
                <p className="text-xs text-muted-foreground">
                  Monthly budget allocation
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Current Spend</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {costSummary ? formatCurrency(costSummary.totalCurrentSpend) : '$0'}
                </div>
                <p className="text-xs text-muted-foreground">
                  {costSummary ? formatPercentage(costSummary.totalUtilization) : '0%'} of budget
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {costSummary?.alerts?.filter((a: CostAlert) => !a.acknowledged).length || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  Unacknowledged alerts
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Load Tests</CardTitle>
                <Zap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {loadTests.length}
                </div>
                <p className="text-xs text-muted-foreground">
                  Total tests executed
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Cost Utilization Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Cost Utilization</CardTitle>
              <CardDescription>
                Monthly budget utilization across services
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {performanceSummary?.budgets?.map((budget: CostBudget) => {
                const utilization = (budget.currentSpend / budget.monthlyBudget) * 100
                return (
                  <div key={budget.service} className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium">{budget.service}</span>
                      <span className="text-muted-foreground">
                        {formatCurrency(budget.currentSpend)} / {formatCurrency(budget.monthlyBudget)}
                      </span>
                    </div>
                    <Progress value={utilization} className="h-2" />
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>{formatPercentage(utilization)} utilized</span>
                      <div className="flex space-x-2">
                        <Badge variant="outline" className="text-xs">50%</Badge>
                        <Badge variant="outline" className="text-xs">80%</Badge>
                        <Badge variant="outline" className="text-xs">100%</Badge>
                      </div>
                    </div>
                  </div>
                )
              })}
            </CardContent>
          </Card>

          {/* Recent Load Tests */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Load Tests</CardTitle>
              <CardDescription>
                Latest load test results and status
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {loadTests.slice(0, 5).map((test) => (
                  <div key={test.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Badge className={getStatusColor(test.status)}>
                        {test.status}
                      </Badge>
                      <div>
                        <p className="font-medium">{test.config.target.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {test.config.testType} • {test.config.virtualUsers} users • {formatDuration(test.config.duration)}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">
                        {test.metrics.totalRequests} requests
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {test.metrics.errorRate.toFixed(1)}% error rate
                      </p>
                    </div>
                  </div>
                ))}
                {loadTests.length === 0 && (
                  <p className="text-center text-muted-foreground py-8">
                    No load tests executed yet
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Cost Monitoring Tab */}
        <TabsContent value="costs" className="space-y-6">
          {/* Cost Alerts */}
          <Card>
            <CardHeader>
              <CardTitle>Cost Alerts</CardTitle>
              <CardDescription>
                Active cost alerts and budget warnings
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {costSummary?.alerts?.filter((alert: CostAlert) => !alert.acknowledged).map((alert: CostAlert) => (
                  <div key={alert.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <AlertCircle className={`h-5 w-5 ${
                        alert.severity === 'emergency' ? 'text-red-500' :
                        alert.severity === 'critical' ? 'text-orange-500' : 'text-yellow-500'
                      }`} />
                      <div>
                        <p className="font-medium">{alert.message}</p>
                        <p className="text-sm text-muted-foreground">
                          {alert.timestamp.toLocaleString()} • Threshold: {alert.threshold}%
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={getSeverityColor(alert.severity)}>
                        {alert.severity}
                      </Badge>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => acknowledgeAlert(alert.id)}
                      >
                        Acknowledge
                      </Button>
                    </div>
                  </div>
                ))}
                {(!costSummary?.alerts || costSummary.alerts.filter((a: CostAlert) => !a.acknowledged).length === 0) && (
                  <p className="text-center text-muted-foreground py-8">
                    No active cost alerts
                  </p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Cost Budgets */}
          <Card>
            <CardHeader>
              <CardTitle>Cost Budgets</CardTitle>
              <CardDescription>
                Monthly budgets and current spending by service
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {performanceSummary?.budgets?.map((budget: CostBudget) => {
                  const utilization = (budget.currentSpend / budget.monthlyBudget) * 100
                  return (
                    <div key={budget.service} className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-medium">{budget.service}</h3>
                          <p className="text-sm text-muted-foreground">
                            Monthly budget: {formatCurrency(budget.monthlyBudget)}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">{formatCurrency(budget.currentSpend)}</p>
                          <p className="text-sm text-muted-foreground">
                            {formatPercentage(utilization)} utilized
                          </p>
                        </div>
                      </div>
                      
                      <Progress value={utilization} className="h-2" />
                      
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>Thresholds</span>
                        <div className="flex space-x-2">
                          <Badge variant="outline">50%</Badge>
                          <Badge variant="outline">80%</Badge>
                          <Badge variant="outline">100%</Badge>
                        </div>
                      </div>

                      {/* Demo cost update */}
                      <div className="flex items-center space-x-2">
                        <Input
                          type="number"
                          placeholder="Update spend"
                          className="w-32"
                          onChange={(e) => {
                            const value = parseFloat(e.target.value) || 0
                            updateCostData(budget.service, value)
                          }}
                        />
                        <Button variant="outline" size="sm">
                          Update
                        </Button>
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-6">
          {/* Performance Metrics */}
          <Card>
            <CardHeader>
              <CardTitle>Performance Metrics</CardTitle>
              <CardDescription>
                Real-time performance data and trends
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {performanceSummary?.metrics?.slice(-10).reverse().map((metric: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Activity className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="font-medium">{metric.service}</p>
                        <p className="text-sm text-muted-foreground">
                          {metric.endpoint} • {metric.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{metric.responseTime.toFixed(0)}ms</p>
                      <p className="text-xs text-muted-foreground">
                        {metric.errorRate.toFixed(1)}% errors
                      </p>
                    </div>
                  </div>
                ))}
                {(!performanceSummary?.metrics || performanceSummary.metrics.length === 0) && (
                  <p className="text-center text-muted-foreground py-8">
                    No performance metrics available
                  </p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Performance Thresholds */}
          <Card>
            <CardHeader>
              <CardTitle>Performance Thresholds</CardTitle>
              <CardDescription>
                Current threshold settings and violations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-4">
                  <h4 className="font-medium">Response Time</h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Warning</span>
                      <Badge variant="outline">
                        {performanceMonitoring.getConfig().performanceThresholds.responseTimeWarning}ms
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Critical</span>
                      <Badge variant="outline">
                        {performanceMonitoring.getConfig().performanceThresholds.responseTimeCritical}ms
                      </Badge>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <h4 className="font-medium">Error Rate</h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Warning</span>
                      <Badge variant="outline">
                        {performanceMonitoring.getConfig().performanceThresholds.errorRateWarning}%
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Critical</span>
                      <Badge variant="outline">
                        {performanceMonitoring.getConfig().performanceThresholds.errorRateCritical}%
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Load Testing Tab */}
        <TabsContent value="loadtesting" className="space-y-6">
          {/* Start Load Test Form */}
          <Card>
            <CardHeader>
              <CardTitle>Start Load Test</CardTitle>
              <CardDescription>
                Configure and execute load tests to validate performance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="testType">Test Type</Label>
                    <Select
                      value={loadTestForm.testType}
                      onValueChange={(value) => updateLoadTestForm('testType', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select test type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="spike">Spike Test</SelectItem>
                        <SelectItem value="load">Load Test</SelectItem>
                        <SelectItem value="stress">Stress Test</SelectItem>
                        <SelectItem value="soak">Soak Test</SelectItem>
                        <SelectItem value="custom">Custom Test</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="targetName">Target Name</Label>
                    <Input
                      id="targetName"
                      placeholder="e.g., API Service"
                      value={loadTestForm.target?.name || ''}
                      onChange={(e) => updateTargetField('name', e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="baseUrl">Base URL</Label>
                    <Input
                      id="baseUrl"
                      placeholder="https://api.example.com"
                      value={loadTestForm.target?.baseUrl || ''}
                      onChange={(e) => updateTargetField('baseUrl', e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="endpoints">Endpoints (comma-separated)</Label>
                    <Input
                      id="endpoints"
                      placeholder="/health, /users, /orders"
                      value={loadTestForm.target?.endpoints?.join(', ') || ''}
                      onChange={(e) => updateEndpoints(e.target.value)}
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="duration">Duration (minutes)</Label>
                    <Input
                      id="duration"
                      type="number"
                      min="1"
                      max="60"
                      value={loadTestForm.duration}
                      onChange={(e) => updateLoadTestForm('duration', parseInt(e.target.value) || 5)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="virtualUsers">Virtual Users</Label>
                    <Input
                      id="virtualUsers"
                      type="number"
                      min="1"
                      max="100"
                      value={loadTestForm.virtualUsers}
                      onChange={(e) => updateLoadTestForm('virtualUsers', parseInt(e.target.value) || 10)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="thresholds">Performance Thresholds</Label>
                    <Textarea
                      id="thresholds"
                      placeholder="p(95)<2000, rate<0.1"
                      value={loadTestForm.thresholds?.httpReqDuration?.join(', ') || ''}
                      onChange={(e) => updateLoadTestForm('thresholds', {
                        ...loadTestForm.thresholds,
                        httpReqDuration: e.target.value.split(',').map(t => t.trim()).filter(t => t)
                      })}
                    />
                  </div>

                  <Button 
                    onClick={startLoadTest}
                    className="w-full"
                    disabled={!loadTestForm.target?.name || !loadTestForm.target?.baseUrl || !loadTestForm.target?.endpoints?.length}
                  >
                    <Play className="h-4 w-4 mr-2" />
                    Start Load Test
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Load Test Results */}
          <Card>
            <CardHeader>
              <CardTitle>Load Test Results</CardTitle>
              <CardDescription>
                Monitor active tests and view results
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {loadTests.map((test) => (
                  <div key={test.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <Badge className={getStatusColor(test.status)}>
                          {test.status}
                        </Badge>
                        <h3 className="font-medium">{test.config.target.name}</h3>
                      </div>
                      <div className="flex items-center space-x-2">
                        {test.status === 'running' && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => cancelLoadTest(test.id)}
                          >
                            <Square className="h-4 w-4 mr-2" />
                            Cancel
                          </Button>
                        )}
                        <Button variant="outline" size="sm" onClick={refreshLoadTests}>
                          <RefreshCw className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>

                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                      <div className="text-center">
                        <p className="text-2xl font-bold">{test.metrics.totalRequests}</p>
                        <p className="text-sm text-muted-foreground">Total Requests</p>
                      </div>
                      <div className="text-center">
                        <p className="text-2xl font-bold">{test.metrics.requestsPerSecond.toFixed(1)}</p>
                        <p className="text-sm text-muted-foreground">RPS</p>
                      </div>
                      <div className="text-center">
                        <p className="text-2xl font-bold">{test.metrics.averageResponseTime.toFixed(0)}ms</p>
                        <p className="text-sm text-muted-foreground">Avg Response</p>
                      </div>
                      <div className="text-center">
                        <p className="text-2xl font-bold">{test.metrics.errorRate.toFixed(1)}%</p>
                        <p className="text-sm text-muted-foreground">Error Rate</p>
                      </div>
                    </div>

                    {test.status === 'completed' && (
                      <div className="mt-4 space-y-3">
                        {/* Threshold Results */}
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium">Thresholds:</span>
                          {test.thresholds.passed.map((threshold, index) => (
                            <Badge key={index} variant="secondary" className="text-green-700 bg-green-100">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              {threshold}
                            </Badge>
                          ))}
                          {test.thresholds.failed.map((threshold, index) => (
                            <Badge key={index} variant="secondary" className="text-red-700 bg-red-100">
                              <XCircle className="h-3 w-3 mr-1" />
                              {threshold}
                            </Badge>
                          ))}
                        </div>

                        {/* Anomalies */}
                        {test.anomalies.length > 0 && (
                          <div className="flex items-center space-x-2">
                            <span className="text-sm font-medium">Anomalies:</span>
                            {test.anomalies.map((anomaly, index) => (
                              <Badge key={index} variant="destructive">
                                <AlertTriangle className="h-3 w-3 mr-1" />
                                {anomaly}
                              </Badge>
                            ))}
                          </div>
                        )}

                        {/* Recommendations */}
                        {test.recommendations.length > 0 && (
                          <div className="space-y-2">
                            <span className="text-sm font-medium">Recommendations:</span>
                            <ul className="text-sm text-muted-foreground space-y-1">
                              {test.recommendations.map((rec, index) => (
                                <li key={index} className="flex items-center space-x-2">
                                  <span>•</span>
                                  <span>{rec}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}

                    <div className="mt-4 text-xs text-muted-foreground">
                      Started: {test.startTime.toLocaleString()}
                      {test.endTime && ` • Ended: ${test.endTime.toLocaleString()}`}
                    </div>
                  </div>
                ))}
                
                {loadTests.length === 0 && (
                  <p className="text-center text-muted-foreground py-8">
                    No load tests executed yet. Start a test above to see results.
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

// Missing icon component
function RefreshCw({ className, ...props }: React.ComponentProps<'svg'>) {
  return (
    <svg
      className={className}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
      {...props}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
      />
    </svg>
  )
}
