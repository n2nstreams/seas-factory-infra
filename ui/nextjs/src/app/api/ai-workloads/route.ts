import { NextRequest, NextResponse } from 'next/server'
import { aiWorkloadsService, AIWorkloadRequest } from '@/lib/aiWorkloads'
import { useFeatureFlags } from '@/components/providers/FeatureFlagProvider'

export async function POST(request: NextRequest) {
  try {
    // Check if AI workloads v2 is enabled
    const featureFlags = await getFeatureFlags()
    if (!featureFlags.ai_workloads_v2) {
      return NextResponse.json(
        { error: 'AI Workloads v2 not enabled' },
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

    // Create AI workload request
    const aiRequest: AIWorkloadRequest = {
      org_id: tenantId,
      user_id: userId,
      purpose: body.purpose || 'general',
      sensitivity_tag: body.sensitivity_tag || 'internal',
      action_type: body.action_type,
      payload: body.payload || {},
      correlation_id: body.correlation_id
    }

    // Process request
    const response = await aiWorkloadsService.processRequest(aiRequest)
    
    if (response.success) {
      return NextResponse.json(response)
    } else {
      return NextResponse.json(response, { status: 400 })
    }

  } catch (error) {
    console.error('AI Workloads API error:', error)
    return NextResponse.json(
      { error: 'Internal server error', correlation_id: `error-${Date.now()}` },
      { status: 500 }
    )
  }
}

export async function GET(request: NextRequest) {
  try {
    // Check if AI workloads v2 is enabled
    const featureFlags = await getFeatureFlags()
    if (!featureFlags.ai_workloads_v2) {
      return NextResponse.json(
        { error: 'AI Workloads v2 not enabled' },
        { status: 503 }
      )
    }

    // Return service statistics
    const stats = aiWorkloadsService.getStats()
    return NextResponse.json(stats)

  } catch (error) {
    console.error('AI Workloads stats API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// Helper function to get feature flags (simplified for API route)
async function getFeatureFlags() {
  // In a real implementation, this would check environment variables or database
  return {
    ai_workloads_v2: process.env.NODE_ENV === 'development' || 
                      process.env.NEXT_PUBLIC_FEATURE_AI_WORKLOADS_V2 === 'true'
  }
}
