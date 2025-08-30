'use client'

import React, { useState, useEffect } from 'react'
import { useAuth } from '@/components/providers/AuthProvider'
import { useFeatureFlags } from '@/components/providers/FeatureFlagProvider'
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
  Brain, 
  Play, 
  Square, 
  RefreshCw, 
  CheckCircle, 
  AlertTriangle, 
  Clock,
  Users,
  Zap,
  Workflow,
  Settings,
  Activity,
  BarChart3,
  Code,
  Palette,
  TestTube,
  GitBranch,
  Plus,
  Trash2,
  Eye
} from 'lucide-react'
import { 
  AIAgentRequest, 
  AIAgentResponse, 
  OrchestratorWorkflow, 
  WorkflowStage,
  AgentStatus 
} from '@/lib/ai-agent-service'

interface AIAgentDashboardProps {
  className?: string
}

export function AIAgentDashboard({ className }: AIAgentDashboardProps) {
  const { user } = useAuth()
  const { flags } = useFeatureFlags()
  const [activeTab, setActiveTab] = useState('overview')
  
  // Agent request form state
  const [agentRequest, setAgentRequest] = useState<Partial<AIAgentRequest>>({
    agent_type: 'orchestrator',
    action: 'greet',
    payload: {},
    priority: 'medium'
  })
  
  // Workflow form state
  const [workflowForm, setWorkflowForm] = useState({
    name: '',
    description: '',
    stages: [] as Partial<WorkflowStage>[]
  })
  
  // Response and status state
  const [lastResponse, setLastResponse] = useState<AIAgentResponse | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [agentStatuses, setAgentStatuses] = useState<AgentStatus[]>([])
  const [workflows, setWorkflows] = useState<OrchestratorWorkflow[]>([])
  const [healthStatus, setHealthStatus] = useState<any>(null)
  
  // Check if user has access to AI agents
  if (!flags.agents_v2) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100">
        <div className="container mx-auto px-4 py-8">
          <div className="glass-card text-center">
            <h1 className="text-2xl font-bold text-primary-800 mb-4">
              AI Agents v2 Not Enabled
            </h1>
            <p className="text-primary-600 mb-4">
              This feature is currently disabled. Enable the agents_v2 feature flag to access AI agent management.
            </p>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-yellow-800">
                <strong>Note:</strong> AI Agents v2 is part of Module 6 of the tech stack migration.
                It will be enabled once the AI agent system migration is complete.
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Load initial data
  useEffect(() => {
    if (flags.agents_v2 && user) {
      loadDashboardData()
      
      // Set up auto-refresh every 30 seconds
      const interval = setInterval(loadDashboardData, 30000)
      
      return () => clearInterval(interval)
    }
  }, [flags.agents_v2, user])

  const loadDashboardData = async () => {
    try {
      // Load agent statuses and health
      const [agentsResponse, workflowsResponse] = await Promise.all([
        fetch('/api/ai-agents', {
          headers: {
            'x-tenant-id': user?.tenant_id || '',
            'x-user-id': user?.id || ''
          }
        }),
        fetch('/api/ai-agents/workflows', {
          headers: {
            'x-tenant-id': user?.tenant_id || '',
            'x-user-id': user?.id || ''
          }
        })
      ])
      
      if (agentsResponse.ok) {
        const agentsData = await agentsResponse.json()
        setAgentStatuses(agentsData.agents || [])
        setHealthStatus(agentsData.health || {})
      }
      
      if (workflowsResponse.ok) {
        const workflowsData = await workflowsResponse.json()
        setWorkflows(workflowsData.workflows || [])
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    }
  }

  const handleAgentRequest = async () => {
    if (!user || !agentRequest.agent_type || !agentRequest.action) {
      alert('Please fill in all required fields')
      return
    }

    try {
      setIsProcessing(true)
      
      const response = await fetch('/api/ai-agents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-tenant-id': user.tenant_id || '',
          'x-user-id': user.id || ''
        },
        body: JSON.stringify(agentRequest)
      })
      
      if (response.ok) {
        const result = await response.json()
        setLastResponse(result)
        
        // Refresh dashboard data
        await loadDashboardData()
      } else {
        const error = await response.json()
        setLastResponse({
          success: false,
          result: null,
          correlation_id: `error-${Date.now()}`,
          execution_time_ms: 0,
          agent_used: agentRequest.agent_type || 'unknown',
          error: error.error || 'Request failed'
        })
      }
    } catch (error) {
      console.error('Error processing agent request:', error)
      setLastResponse({
        success: false,
        result: null,
        correlation_id: `error-${Date.now()}`,
        execution_time_ms: 0,
        agent_used: agentRequest.agent_type || 'unknown',
        error: 'Network error'
      })
    } finally {
      setIsProcessing(false)
    }
  }

  const handleWorkflowSubmit = async () => {
    if (!user || !workflowForm.name || !workflowForm.description || workflowForm.stages.length === 0) {
      alert('Please fill in all required fields')
      return
    }

    try {
      setIsProcessing(true)
      
      const response = await fetch('/api/ai-agents/workflows', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-tenant-id': user.tenant_id || '',
          'x-user-id': user.id || ''
        },
        body: JSON.stringify(workflowForm)
      })
      
      if (response.ok) {
        const result = await response.json()
        alert('Workflow started successfully!')
        
        // Reset form
        setWorkflowForm({
          name: '',
          description: '',
          stages: []
        })
        
        // Refresh dashboard data
        await loadDashboardData()
      } else {
        const error = await response.json()
        alert(`Failed to start workflow: ${error.error}`)
      }
    } catch (error) {
      console.error('Error starting workflow:', error)
      alert('Failed to start workflow')
    } finally {
      setIsProcessing(false)
    }
  }

  const addWorkflowStage = () => {
    setWorkflowForm(prev => ({
      ...prev,
      stages: [...prev.stages, {
        name: '',
        agent_type: 'orchestrator',
        estimated_duration_seconds: 60
      }]
    }))
  }

  const removeWorkflowStage = (index: number) => {
    setWorkflowForm(prev => ({
      ...prev,
      stages: prev.stages.filter((_, i) => i !== index)
    }))
  }

  const updateWorkflowStage = (index: number, field: string, value: any) => {
    setWorkflowForm(prev => ({
      ...prev,
      stages: prev.stages.map((stage, i) => 
        i === index ? { ...stage, [field]: value } : stage
      )
    }))
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'available':
      case 'completed':
        return 'bg-green-500'
      case 'degraded':
      case 'busy':
      case 'running':
        return 'bg-yellow-500'
      case 'unhealthy':
      case 'offline':
      case 'failed':
      case 'error':
        return 'bg-red-500'
      case 'pending':
        return 'bg-blue-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'available':
        return 'Available'
      case 'degraded':
      case 'busy':
        return 'Busy'
      case 'unhealthy':
      case 'offline':
        return 'Offline'
      case 'pending':
        return 'Pending'
      case 'running':
        return 'Running'
      case 'completed':
        return 'Completed'
      case 'failed':
        return 'Failed'
      case 'cancelled':
        return 'Cancelled'
      default:
        return status
    }
  }

  const getAgentIcon = (agentType: string) => {
    switch (agentType) {
      case 'orchestrator':
        return <Brain className="w-5 h-5" />
      case 'techstack':
        return <Code className="w-5 h-5" />
      case 'design':
        return <Palette className="w-5 h-5" />
      case 'ui_dev':
        return <Code className="w-5 h-5" />
      case 'playwright_qa':
        return <TestTube className="w-5 h-5" />
      case 'github_merge':
        return <GitBranch className="w-5 h-5" />
      default:
        return <Brain className="w-5 h-5" />
    }
  }

  return (
    <div className={`space-y-6 p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-primary-800">AI Agent Dashboard</h1>
          <p className="text-primary-600">Manage AI agents and orchestrator workflows</p>
        </div>
        <div className="flex items-center space-x-2">
          <Button onClick={loadDashboardData} variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Health Status */}
      {healthStatus && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Service Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${getStatusColor(healthStatus.status)}`} />
                <span className="text-sm font-medium">{getStatusText(healthStatus.status)}</span>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Active Agents</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{healthStatus.agents}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Active Workflows</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{healthStatus.workflows}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Orchestrator</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${getStatusColor(healthStatus.orchestrator)}`} />
                <span className="text-sm font-medium">{getStatusText(healthStatus.orchestrator)}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4 glass-card">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="agents">Agent Requests</TabsTrigger>
          <TabsTrigger value="workflows">Workflows</TabsTrigger>
          <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Agent Statuses */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="w-5 h-5" />
                  <span>Agent Statuses</span>
                </CardTitle>
                <CardDescription>Current status of all AI agents</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {agentStatuses.map((agent) => (
                  <div key={agent.agent_id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      {getAgentIcon(agent.agent_type || 'orchestrator')}
                      <div>
                        <div className="font-medium">{agent.name}</div>
                        <div className="text-sm text-gray-500">{agent.capabilities.join(', ')}</div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className={`w-3 h-3 rounded-full ${getStatusColor(agent.status)}`} />
                      <span className="text-sm">{getStatusText(agent.status)}</span>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Recent Workflows */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Workflow className="w-5 h-5" />
                  <span>Recent Workflows</span>
                </CardTitle>
                <CardDescription>Latest orchestrator workflows</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {workflows.slice(0, 5).map((workflow) => (
                  <div key={workflow.workflow_id} className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-medium">{workflow.name}</div>
                      <Badge variant={workflow.status === 'completed' ? 'default' : 'secondary'}>
                        {workflow.status}
                      </Badge>
                    </div>
                    <div className="text-sm text-gray-500 mb-2">{workflow.description}</div>
                    <div className="flex items-center space-x-2 text-xs text-gray-400">
                      <Clock className="w-3 h-3" />
                      <span>{new Date(workflow.created_at).toLocaleDateString()}</span>
                      <span>•</span>
                      <span>{workflow.stages.length} stages</span>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Agent Requests Tab */}
        <TabsContent value="agents" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Submit Agent Request</CardTitle>
              <CardDescription>Send requests to specific AI agents</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="agent-type">Agent Type</Label>
                  <Select 
                    value={agentRequest.agent_type} 
                    onValueChange={(value) => setAgentRequest(prev => ({ ...prev, agent_type: value as any }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select agent type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="orchestrator">Orchestrator</SelectItem>
                      <SelectItem value="techstack">Tech Stack</SelectItem>
                      <SelectItem value="design">Design</SelectItem>
                      <SelectItem value="ui_dev">UI Development</SelectItem>
                      <SelectItem value="playwright_qa">Playwright QA</SelectItem>
                      <SelectItem value="github_merge">GitHub Merge</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="action">Action</Label>
                  <Input
                    id="action"
                    value={agentRequest.action}
                    onChange={(e) => setAgentRequest(prev => ({ ...prev, action: e.target.value }))}
                    placeholder="Action to perform"
                  />
                </div>
              </div>
              
              <div>
                <Label htmlFor="priority">Priority</Label>
                <Select 
                  value={agentRequest.priority} 
                  onValueChange={(value) => setAgentRequest(prev => ({ ...prev, priority: value as any }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select priority" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="critical">Critical</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="payload">Payload (JSON)</Label>
                <Textarea
                  id="payload"
                  value={JSON.stringify(agentRequest.payload, null, 2)}
                  onChange={(e) => {
                    try {
                      const parsed = JSON.parse(e.target.value)
                      setAgentRequest(prev => ({ ...prev, payload: parsed }))
                    } catch (error) {
                      // Allow invalid JSON during typing
                    }
                  }}
                  rows={4}
                  placeholder='{"key": "value"}'
                />
              </div>
              
              <Button onClick={handleAgentRequest} disabled={isProcessing} className="w-full">
                {isProcessing ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Submit Request
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Last Response */}
          {lastResponse && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Activity className="w-5 h-5" />
                  <span>Last Response</span>
                  <Badge variant={lastResponse.success ? 'default' : 'destructive'}>
                    {lastResponse.success ? 'Success' : 'Error'}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Correlation ID:</span>
                      <span className="ml-2 font-mono">{lastResponse.correlation_id}</span>
                    </div>
                    <div>
                      <span className="font-medium">Execution Time:</span>
                      <span className="ml-2">{lastResponse.execution_time_ms}ms</span>
                    </div>
                    <div>
                      <span className="font-medium">Agent Used:</span>
                      <span className="ml-2">{lastResponse.agent_used}</span>
                    </div>
                    {lastResponse.error && (
                      <div>
                        <span className="font-medium text-red-600">Error:</span>
                        <span className="ml-2 text-red-600">{lastResponse.error}</span>
                      </div>
                    )}
                  </div>
                  
                  <div>
                    <Label>Result</Label>
                    <Textarea
                      value={typeof lastResponse.result === 'string' 
                        ? lastResponse.result 
                        : JSON.stringify(lastResponse.result, null, 2)
                      }
                      rows={6}
                      readOnly
                      className="font-mono text-sm"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Workflows Tab */}
        <TabsContent value="workflows" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Create New Workflow</CardTitle>
              <CardDescription>Define a multi-stage orchestrator workflow</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="workflow-name">Workflow Name</Label>
                  <Input
                    id="workflow-name"
                    value={workflowForm.name}
                    onChange={(e) => setWorkflowForm(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="e.g., Full Project Pipeline"
                  />
                </div>
                
                <div>
                  <Label htmlFor="workflow-description">Description</Label>
                  <Input
                    id="workflow-description"
                    value={workflowForm.description}
                    onChange={(e) => setWorkflowForm(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Workflow description"
                  />
                </div>
              </div>
              
              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label>Workflow Stages</Label>
                  <Button onClick={addWorkflowStage} size="sm" variant="outline">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Stage
                  </Button>
                </div>
                
                <div className="space-y-3">
                  {workflowForm.stages.map((stage, index) => (
                    <div key={index} className="p-3 border rounded-lg space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="font-medium">Stage {index + 1}</span>
                        <Button 
                          onClick={() => removeWorkflowStage(index)} 
                          size="sm" 
                          variant="destructive"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div>
                          <Label>Name</Label>
                          <Input
                            value={stage.name}
                            onChange={(e) => updateWorkflowStage(index, 'name', e.target.value)}
                            placeholder="Stage name"
                          />
                        </div>
                        
                        <div>
                          <Label>Agent Type</Label>
                          <Select 
                            value={stage.agent_type} 
                            onValueChange={(value) => updateWorkflowStage(index, 'agent_type', value)}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Select agent" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="orchestrator">Orchestrator</SelectItem>
                              <SelectItem value="techstack">Tech Stack</SelectItem>
                              <SelectItem value="design">Design</SelectItem>
                              <SelectItem value="ui_dev">UI Development</SelectItem>
                              <SelectItem value="playwright_qa">Playwright QA</SelectItem>
                              <SelectItem value="github_merge">GitHub Merge</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        
                        <div>
                          <Label>Duration (seconds)</Label>
                          <Input
                            type="number"
                            value={stage.estimated_duration_seconds}
                            onChange={(e) => updateWorkflowStage(index, 'estimated_duration_seconds', parseInt(e.target.value))}
                            placeholder="60"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              <Button onClick={handleWorkflowSubmit} disabled={isProcessing} className="w-full">
                {isProcessing ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Starting Workflow...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Start Workflow
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Active Workflows */}
          <Card>
            <CardHeader>
              <CardTitle>Active Workflows</CardTitle>
              <CardDescription>Monitor running and completed workflows</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {workflows.map((workflow) => (
                  <div key={workflow.workflow_id} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h3 className="font-medium">{workflow.name}</h3>
                        <p className="text-sm text-gray-500">{workflow.description}</p>
                      </div>
                      <Badge variant={workflow.status === 'completed' ? 'default' : 'secondary'}>
                        {workflow.status}
                      </Badge>
                    </div>
                    
                    <div className="mb-3">
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span>Progress</span>
                        <span>{workflow.current_stage + 1} / {workflow.stages.length}</span>
                      </div>
                      <Progress value={((workflow.current_stage + 1) / workflow.stages.length) * 100} />
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="font-medium">Created:</span>
                        <span className="ml-2">{new Date(workflow.created_at).toLocaleString()}</span>
                      </div>
                      <div>
                        <span className="font-medium">Updated:</span>
                        <span className="ml-2">{new Date(workflow.updated_at).toLocaleString()}</span>
                      </div>
                    </div>
                    
                    <div className="mt-3">
                      <h4 className="font-medium mb-2">Stages</h4>
                      <div className="space-y-2">
                        {workflow.stages.map((stage, index) => (
                          <div key={stage.stage_id} className="flex items-center space-x-3 text-sm">
                            <div className={`w-3 h-3 rounded-full ${getStatusColor(stage.status)}`} />
                            <span className="font-medium">{stage.name}</span>
                            <span className="text-gray-500">({stage.agent_type})</span>
                            <span className="text-gray-400">
                              {stage.status === 'completed' && stage.completed_at && (
                                `Completed in ${Math.round((new Date(stage.completed_at).getTime() - new Date(stage.started_at || '').getTime()) / 1000)}s`
                              )}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
                
                {workflows.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <Workflow className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No workflows found</p>
                    <p className="text-sm">Create a new workflow to get started</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Monitoring Tab */}
        <TabsContent value="monitoring" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Agent Performance */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="w-5 h-5" />
                  <span>Agent Performance</span>
                </CardTitle>
                <CardDescription>Real-time agent metrics and performance</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {agentStatuses.map((agent) => (
                    <div key={agent.agent_id} className="p-3 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          {getAgentIcon(agent.agent_type || 'orchestrator')}
                          <span className="font-medium">{agent.name}</span>
                        </div>
                        <Badge variant="outline">{agent.current_load}/{agent.max_concurrent_requests}</Badge>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span>Current Load</span>
                          <span>{agent.current_load}</span>
                        </div>
                        <Progress value={(agent.current_load / agent.max_concurrent_requests) * 100} />
                      </div>
                      
                      <div className="text-xs text-gray-500 mt-2">
                        Last heartbeat: {new Date(agent.last_heartbeat).toLocaleTimeString()}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* System Health */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Activity className="w-5 h-5" />
                  <span>System Health</span>
                </CardTitle>
                <CardDescription>Overall system status and health metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center p-3 border rounded-lg">
                      <div className="text-2xl font-bold text-green-600">
                        {healthStatus?.agents || 0}
                      </div>
                      <div className="text-sm text-gray-500">Active Agents</div>
                    </div>
                    
                    <div className="text-center p-3 border rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">
                        {workflows.filter(w => w.status === 'running').length}
                      </div>
                      <div className="text-sm text-gray-500">Running Workflows</div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Service Status</span>
                      <div className="flex items-center space-x-2">
                        <div className={`w-3 h-3 rounded-full ${getStatusColor(healthStatus?.status || 'unknown')}`} />
                        <span className="text-sm font-medium">{getStatusText(healthStatus?.status || 'unknown')}</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Orchestrator</span>
                      <div className="flex items-center space-x-2">
                        <div className={`w-3 h-3 rounded-full ${getStatusColor(healthStatus?.orchestrator || 'unknown')}`} />
                        <span className="text-sm font-medium">{getStatusText(healthStatus?.orchestrator || 'unknown')}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
