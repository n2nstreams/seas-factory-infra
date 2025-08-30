import { NextRequest, NextResponse } from 'next/server'
import { aiAgentService, AIAgentRequest } from '@/lib/ai-agent-service'
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

    // Create AI agent request
    const aiRequest: AIAgentRequest = {
      org_id: tenantId,
      user_id: userId,
      agent_type: body.agent_type,
      action: body.action,
      payload: body.payload || {},
      correlation_id: body.correlation_id,
      priority: body.priority || 'medium',
      timeout_seconds: body.timeout_seconds
    }

    // Validate agent type
    const validAgentTypes = ['orchestrator', 'techstack', 'design', 'ui_dev', 'playwright_qa', 'github_merge']
    if (!validAgentTypes.includes(aiRequest.agent_type)) {
      return NextResponse.json(
        { error: `Invalid agent_type. Must be one of: ${validAgentTypes.join(', ')}` },
        { status: 400 }
      )
    }

    // Process request
    const response = await aiAgentService.processRequest(aiRequest)
    
    if (response.success) {
      return NextResponse.json(response)
    } else {
      return NextResponse.json(response, { status: 400 })
    }

  } catch (error) {
    console.error('AI Agents API error:', error)
    return NextResponse.json(
      { error: 'Internal server error', correlation_id: `error-${Date.now()}` },
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

    // Get agent statuses
    const agentStatuses = await aiAgentService.getAgentStatuses()
    
    // Get health status
    const healthStatus = await aiAgentService.healthCheck()
    
    return NextResponse.json({
      status: 'success',
      agents: agentStatuses,
      health: healthStatus,
      timestamp: new Date().toISOString()
    })

  } catch (error) {
    console.error('AI Agents API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
