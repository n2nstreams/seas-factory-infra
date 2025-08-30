import { NextRequest, NextResponse } from 'next/server'
import { aiAgentService, OrchestratorWorkflow, WorkflowStage } from '@/lib/ai-agent-service'
import { getFeatureFlags } from '@/lib/feature-flags'

export async function POST(request: NextRequest) {
  try {
    // Check if AI agents v2 is enabled
    const featureFlags = await getFeatureFlags()
    if (!featureFlags.agents_v2) {
      return NextResponse.json(
        { error: 'AI Agents v2 not enabled' },
        { status: 503 }
      )
    }

    // Parse request body
    const body = await request.json()
    
    // Validate required headers
    const tenantId = request.headers.get('x-tenant-id')
    const userId = request.headers.get('x-user-id')
    
    if (!tenantId || !userId) {
      return NextResponse.json(
        { error: 'Missing required headers: x-tenant-id, x-user-id' },
        { status: 400 }
      )
    }

    // Validate workflow data
    if (!body.name || !body.description || !body.stages || !Array.isArray(body.stages)) {
      return NextResponse.json(
        { error: 'Missing required fields: name, description, stages' },
        { status: 400 }
      )
    }

    // Validate stages
    for (const stage of body.stages) {
      if (!stage.name || !stage.agent_type || !stage.estimated_duration_seconds) {
        return NextResponse.json(
          { error: 'Each stage must have: name, agent_type, estimated_duration_seconds' },
          { status: 400 }
        )
      }
      
      // Add stage_id if not provided
      if (!stage.stage_id) {
        stage.stage_id = `stage-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      }
    }

    // Create workflow
    const workflow: Omit<OrchestratorWorkflow, 'workflow_id' | 'created_at' | 'updated_at' | 'status' | 'current_stage'> = {
      name: body.name,
      description: body.description,
      stages: body.stages as WorkflowStage[],
      tenant_id: tenantId,
      user_id: userId
    }

    // Start workflow
    const startedWorkflow = await aiAgentService.startWorkflow(workflow)
    
    return NextResponse.json({
      status: 'success',
      workflow: startedWorkflow,
      message: 'Workflow started successfully'
    })

  } catch (error) {
    console.error('AI Agents Workflows API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function GET(request: NextRequest) {
  try {
    // Check if AI agents v2 is enabled
    const featureFlags = await getFeatureFlags()
    if (!featureFlags.agents_v2) {
      return NextResponse.json(
        { error: 'AI Agents v2 not enabled' },
        { status: 503 }
      )
    }

    // Get tenant ID from headers
    const tenantId = request.headers.get('x-tenant-id')
    if (!tenantId) {
      return NextResponse.json(
        { error: 'Missing required header: x-tenant-id' },
        { status: 400 }
      )
    }

    // Get workflow ID from query params if provided
    const { searchParams } = new URL(request.url)
    const workflowId = searchParams.get('workflow_id')

    if (workflowId) {
      // Get specific workflow
      const workflow = aiAgentService.getWorkflow(workflowId)
      if (!workflow) {
        return NextResponse.json(
          { error: 'Workflow not found' },
          { status: 404 }
        )
      }
      
      // Check tenant access
      if (workflow.tenant_id !== tenantId) {
        return NextResponse.json(
          { error: 'Access denied' },
          { status: 403 }
        )
      }
      
      return NextResponse.json({
        status: 'success',
        workflow
      })
    } else {
      // Get all workflows for tenant
      const workflows = aiAgentService.getTenantWorkflows(tenantId)
      
      return NextResponse.json({
        status: 'success',
        workflows,
        count: workflows.length
      })
    }

  } catch (error) {
    console.error('AI Agents Workflows API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function DELETE(request: NextRequest) {
  try {
    // Check if AI agents v2 is enabled
    const featureFlags = await getFeatureFlags()
    if (!featureFlags.agents_v2) {
      return NextResponse.json(
        { error: 'AI Agents v2 not enabled' },
        { status: 503 }
      )
    }

    // Get tenant ID from headers
    const tenantId = request.headers.get('x-tenant-id')
    if (!tenantId) {
      return NextResponse.json(
        { error: 'Missing required header: x-tenant-id' },
        { status: 400 }
      )
    }

    // Get workflow ID from query params
    const { searchParams } = new URL(request.url)
    const workflowId = searchParams.get('workflow_id')
    
    if (!workflowId) {
      return NextResponse.json(
        { error: 'Missing workflow_id parameter' },
        { status: 400 }
      )
    }

    // Get workflow to check tenant access
    const workflow = aiAgentService.getWorkflow(workflowId)
    if (!workflow) {
      return NextResponse.json(
        { error: 'Workflow not found' },
        { status: 404 }
      )
    }
    
    // Check tenant access
    if (workflow.tenant_id !== tenantId) {
      return NextResponse.json(
        { error: 'Access denied' },
        { status: 403 }
      )
    }

    // Cancel workflow
    const cancelled = aiAgentService.cancelWorkflow(workflowId)
    
    if (cancelled) {
      return NextResponse.json({
        status: 'success',
        message: 'Workflow cancelled successfully'
      })
    } else {
      return NextResponse.json(
        { error: 'Failed to cancel workflow' },
        { status: 400 }
      )
    }

  } catch (error) {
    console.error('AI Agents Workflows API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
