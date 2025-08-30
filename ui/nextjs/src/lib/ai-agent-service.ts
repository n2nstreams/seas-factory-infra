/**
 * AI Agent Service - Module 6 Migration
 * Integrates existing orchestrator and agents with new Next.js + Supabase stack
 */

export interface AIAgentRequest {
  org_id: string
  user_id: string
  agent_type: 'orchestrator' | 'techstack' | 'design' | 'ui_dev' | 'playwright_qa' | 'github_merge'
  action: string
  payload: Record<string, any>
  correlation_id?: string
  priority?: 'low' | 'medium' | 'high' | 'critical'
  timeout_seconds?: number
}

export interface AIAgentResponse {
  success: boolean
  result: any
  correlation_id: string
  execution_time_ms: number
  agent_used: string
  metadata?: Record<string, any>
  error?: string
}

export interface AgentStatus {
  agent_id: string
  name: string
  status: 'available' | 'busy' | 'offline' | 'error'
  last_heartbeat: string
  capabilities: string[]
  current_load: number
  max_concurrent_requests: number
}

export interface OrchestratorWorkflow {
  workflow_id: string
  name: string
  description: string
  stages: WorkflowStage[]
  current_stage: number
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  created_at: string
  updated_at: string
  tenant_id: string
  user_id: string
}

export interface WorkflowStage {
  stage_id: string
  name: string
  agent_type: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  result?: any
  error?: string
  started_at?: string
  completed_at?: string
  estimated_duration_seconds: number
}

class AIAgentService {
  private orchestratorUrl: string
  private isInitialized: boolean = false
  private agentStatuses: Map<string, AgentStatus> = new Map()
  private activeWorkflows: Map<string, OrchestratorWorkflow> = new Map()

  constructor() {
    this.orchestratorUrl = process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || 'http://localhost:8001'
    this.initializeService()
  }

  private async initializeService() {
    try {
      // Initialize agent statuses
      await this.refreshAgentStatuses()
      this.isInitialized = true
      console.log('AI Agent Service initialized successfully')
    } catch (error) {
      console.error('Failed to initialize AI Agent Service:', error)
      this.isInitialized = false
    }
  }

  /**
   * Process an AI agent request
   */
  async processRequest(request: AIAgentRequest): Promise<AIAgentResponse> {
    const startTime = Date.now()
    const correlationId = request.correlation_id || `ai-agent-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

    try {
      if (!this.isInitialized) {
        await this.initializeService()
      }

      // Validate request
      this.validateRequest(request)

      // Route to appropriate agent
      let result: any
      let agentUsed: string

      switch (request.agent_type) {
        case 'orchestrator':
          result = await this.callOrchestrator(request)
          agentUsed = 'project_orchestrator'
          break
        case 'techstack':
          result = await this.callTechStackAgent(request)
          agentUsed = 'techstack_agent'
          break
        case 'design':
          result = await this.callDesignAgent(request)
          agentUsed = 'design_agent'
          break
        case 'ui_dev':
          result = await this.callUIDevAgent(request)
          agentUsed = 'ui_dev_agent'
          break
        case 'playwright_qa':
          result = await this.callPlaywrightQAAgent(request)
          agentUsed = 'playwright_qa_agent'
          break
        case 'github_merge':
          result = await this.callGitHubMergeAgent(request)
          agentUsed = 'github_merge_agent'
          break
        default:
          throw new Error(`Unknown agent type: ${request.agent_type}`)
      }

      const executionTime = Date.now() - startTime

      return {
        success: true,
        result,
        correlation_id: correlationId,
        execution_time_ms: executionTime,
        agent_used: agentUsed,
        metadata: {
          agent_type: request.agent_type,
          action: request.action,
          priority: request.priority || 'medium'
        }
      }

    } catch (error) {
      const executionTime = Date.now() - startTime
      console.error(`AI Agent request failed: ${error}`)

      return {
        success: false,
        result: null,
        correlation_id: correlationId,
        execution_time_ms: executionTime,
        agent_used: request.agent_type,
        error: error instanceof Error ? error.message : 'Unknown error',
        metadata: {
          agent_type: request.agent_type,
          action: request.action,
          priority: request.priority || 'medium'
        }
      }
    }
  }

  /**
   * Call the main project orchestrator
   */
  private async callOrchestrator(request: AIAgentRequest): Promise<any> {
    const response = await fetch(`${this.orchestratorUrl}/orchestrator`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-ID': request.org_id,
        'X-User-ID': request.user_id,
        'X-Correlation-ID': request.correlation_id || ''
      },
      body: JSON.stringify({
        name: request.payload.name || 'world',
        stage: request.payload.stage || 'greet',
        data: request.payload
      })
    })

    if (!response.ok) {
      throw new Error(`Orchestrator request failed: ${response.status} ${response.statusText}`)
    }

    const result = await response.json()
    return result.result || result
  }

  /**
   * Call the tech stack recommendation agent
   */
  private async callTechStackAgent(request: AIAgentRequest): Promise<any> {
    const response = await fetch(`${this.orchestratorUrl}/orchestrator`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-ID': request.org_id,
        'X-User-ID': request.user_id,
        'X-Correlation-ID': request.correlation_id || ''
      },
      body: JSON.stringify({
        name: 'techstack',
        stage: 'techstack',
        data: {
          project_type: request.payload.project_type,
          requirements: request.payload.requirements || '',
          team_size: request.payload.team_size,
          timeline: request.payload.timeline
        }
      })
    })

    if (!response.ok) {
      throw new Error(`TechStack agent request failed: ${response.status} ${response.statusText}`)
    }

    const result = await response.json()
    return result.result || result
  }

  /**
   * Call the design and wireframe generation agent
   */
  private async callDesignAgent(request: AIAgentRequest): Promise<any> {
    const response = await fetch(`${this.orchestratorUrl}/orchestrator`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-ID': request.org_id,
        'X-User-ID': request.user_id,
        'X-Correlation-ID': request.correlation_id || ''
      },
      body: JSON.stringify({
        name: 'design',
        stage: 'design',
        data: {
          project_type: request.payload.project_type,
          pages: request.payload.pages || '',
          style_preferences: request.payload.style_preferences || '',
          color_scheme: request.payload.color_scheme || 'natural',
          layout_type: request.payload.layout_type || 'clean'
        }
      })
    })

    if (!response.ok) {
      throw new Error(`Design agent request failed: ${response.status} ${response.statusText}`)
    }

    const result = await response.json()
    return result.result || result
  }

  /**
   * Call the UI development agent for React scaffolding
   */
  private async callUIDevAgent(request: AIAgentRequest): Promise<any> {
    const response = await fetch(`${this.orchestratorUrl}/orchestrator`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-ID': request.org_id,
        'X-User-ID': request.user_id,
        'X-Correlation-ID': request.correlation_id || ''
      },
      body: JSON.stringify({
        name: 'ui_dev',
        stage: 'ui_dev',
        data: {
          project_id: request.payload.project_id,
          figma_data: request.payload.figma_data,
          target_pages: request.payload.target_pages || [],
          style_framework: request.payload.style_framework || 'tailwind',
          component_library: request.payload.component_library || '',
          typescript: request.payload.typescript !== false,
          responsive: request.payload.responsive !== false,
          glassmorphism: request.payload.glassmorphism !== false,
          olive_green_theme: request.payload.olive_green_theme !== false
        }
      })
    })

    if (!response.ok) {
      throw new Error(`UI Dev agent request failed: ${response.status} ${response.statusText}`)
    }

    const result = await response.json()
    return result.result || result
  }

  /**
   * Call the Playwright QA agent for test generation
   */
  private async callPlaywrightQAAgent(request: AIAgentRequest): Promise<any> {
    const response = await fetch(`${this.orchestratorUrl}/orchestrator`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-ID': request.org_id,
        'X-User-ID': request.user_id,
        'X-Correlation-ID': request.correlation_id || ''
      },
      body: JSON.stringify({
        name: 'playwright_qa',
        stage: 'playwright_qa',
        data: {
          project_id: request.payload.project_id,
          ui_scaffold_result: request.payload.ui_scaffold_result || '',
          api_endpoints: request.payload.api_endpoints || ''
        }
      })
    })

    if (!response.ok) {
      throw new Error(`Playwright QA agent request failed: ${response.status} ${response.statusText}`)
    }

    const result = await response.json()
    return result.result || result
  }

  /**
   * Call the GitHub merge agent for PR management
   */
  private async callGitHubMergeAgent(request: AIAgentRequest): Promise<any> {
    const response = await fetch(`${this.orchestratorUrl}/orchestrator`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-ID': request.org_id,
        'X-User-ID': request.user_id,
        'X-Correlation-ID': request.correlation_id || ''
      },
      body: JSON.stringify({
        name: 'github_merge',
        stage: 'github_merge',
        data: {
          action: request.payload.action,
          pr_number: request.payload.pr_number,
          workflow_data: request.payload.workflow_data
        }
      })
    })

    if (!response.ok) {
      throw new Error(`GitHub Merge agent request failed: ${response.status} ${response.statusText}`)
    }

    const result = await response.json()
    return result.result || result
  }

  /**
   * Start a multi-stage orchestrator workflow
   */
  async startWorkflow(workflow: Omit<OrchestratorWorkflow, 'workflow_id' | 'created_at' | 'updated_at' | 'status' | 'current_stage'>): Promise<OrchestratorWorkflow> {
    const workflowId = `workflow-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    const now = new Date().toISOString()

    const newWorkflow: OrchestratorWorkflow = {
      ...workflow,
      workflow_id: workflowId,
      created_at: now,
      updated_at: now,
      status: 'pending',
      current_stage: 0
    }

    this.activeWorkflows.set(workflowId, newWorkflow)

    // Start the first stage
    await this.executeWorkflowStage(newWorkflow, 0)

    return newWorkflow
  }

  /**
   * Execute a specific workflow stage
   */
  private async executeWorkflowStage(workflow: OrchestratorWorkflow, stageIndex: number): Promise<void> {
    if (stageIndex >= workflow.stages.length) {
      // Workflow completed
      workflow.status = 'completed'
      workflow.updated_at = new Date().toISOString()
      return
    }

    const stage = workflow.stages[stageIndex]
    stage.status = 'running'
    stage.started_at = new Date().toISOString()
    workflow.current_stage = stageIndex
    workflow.status = 'running'
    workflow.updated_at = new Date().toISOString()

    try {
      // Execute the stage
      const result = await this.processRequest({
        org_id: workflow.tenant_id,
        user_id: workflow.user_id,
        agent_type: stage.agent_type as any,
        action: stage.name,
        payload: { workflow_id: workflow.workflow_id, stage_id: stage.stage_id },
        correlation_id: `workflow-${workflow.workflow_id}-stage-${stage.stage_id}`
      })

      if (result.success) {
        stage.status = 'completed'
        stage.result = result.result
        stage.completed_at = new Date().toISOString()
        
        // Move to next stage
        await this.executeWorkflowStage(workflow, stageIndex + 1)
      } else {
        stage.status = 'failed'
        stage.error = result.error
        stage.completed_at = new Date().toISOString()
        workflow.status = 'failed'
        workflow.updated_at = new Date().toISOString()
      }
    } catch (error) {
      stage.status = 'failed'
      stage.error = error instanceof Error ? error.message : 'Unknown error'
      stage.completed_at = new Date().toISOString()
      workflow.status = 'failed'
      workflow.updated_at = new Date().toISOString()
    }
  }

  /**
   * Get workflow status
   */
  getWorkflow(workflowId: string): OrchestratorWorkflow | undefined {
    return this.activeWorkflows.get(workflowId)
  }

  /**
   * Get all active workflows for a tenant
   */
  getTenantWorkflows(tenantId: string): OrchestratorWorkflow[] {
    return Array.from(this.activeWorkflows.values()).filter(w => w.tenant_id === tenantId)
  }

  /**
   * Cancel a workflow
   */
  cancelWorkflow(workflowId: string): boolean {
    const workflow = this.activeWorkflows.get(workflowId)
    if (workflow && workflow.status === 'running') {
      workflow.status = 'cancelled'
      workflow.updated_at = new Date().toISOString()
      return true
    }
    return false
  }

  /**
   * Get agent statuses
   */
  async getAgentStatuses(): Promise<AgentStatus[]> {
    await this.refreshAgentStatuses()
    return Array.from(this.agentStatuses.values())
  }

  /**
   * Refresh agent statuses from orchestrator
   */
  private async refreshAgentStatuses(): Promise<void> {
    try {
      const response = await fetch(`${this.orchestratorUrl}/orchestrator/agents`)
      if (response.ok) {
        const result = await response.json()
        
        // Update agent statuses based on response
        const agents = result.agents || []
        agents.forEach((agentName: string) => {
          this.agentStatuses.set(agentName, {
            agent_id: agentName,
            name: agentName,
            status: 'available',
            last_heartbeat: new Date().toISOString(),
            capabilities: ['general'],
            current_load: 0,
            max_concurrent_requests: 10
          })
        })
      }
    } catch (error) {
      console.error('Failed to refresh agent statuses:', error)
      // Mark all agents as offline if we can't reach the orchestrator
      this.agentStatuses.forEach(agent => {
        agent.status = 'offline'
      })
    }
  }

  /**
   * Validate request parameters
   */
  private validateRequest(request: AIAgentRequest): void {
    if (!request.org_id) {
      throw new Error('org_id is required')
    }
    if (!request.user_id) {
      throw new Error('user_id is required')
    }
    if (!request.agent_type) {
      throw new Error('agent_type is required')
    }
    if (!request.action) {
      throw new Error('action is required')
    }
    if (!request.payload) {
      throw new Error('payload is required')
    }
  }

  /**
   * Health check for the AI agent service
   */
  async healthCheck(): Promise<{ status: string; agents: number; workflows: number; orchestrator: string }> {
    try {
      const orchestratorResponse = await fetch(`${this.orchestratorUrl}/health`)
      const orchestratorStatus = orchestratorResponse.ok ? 'healthy' : 'unhealthy'
      
      return {
        status: this.isInitialized ? 'healthy' : 'unhealthy',
        agents: this.agentStatuses.size,
        workflows: this.activeWorkflows.size,
        orchestrator: orchestratorStatus
      }
    } catch (error) {
      return {
        status: 'unhealthy',
        agents: 0,
        workflows: 0,
        orchestrator: 'unreachable'
      }
    }
  }
}

// Export singleton instance
export const aiAgentService = new AIAgentService()
