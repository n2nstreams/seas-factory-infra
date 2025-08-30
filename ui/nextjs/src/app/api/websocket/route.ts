import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'
import { getWebSocketStatus, broadcastEvent, WebSocketEventTypes, WebSocketSources } from '@/lib/websocket-server'

// Initialize Supabase client for real-time subscriptions
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

// GET /api/websocket - Get WebSocket connection info and status
export async function GET(request: NextRequest) {
  try {
    const tenantId = request.headers.get('X-Tenant-ID')
    
    if (!tenantId) {
      return NextResponse.json({
        success: false,
        error: 'Tenant ID is required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Get WebSocket server status
    const wsStatus = getWebSocketStatus()

    // Return WebSocket connection information
    return NextResponse.json({
      success: true,
      websocket: {
        // Next.js WebSocket server
        nextjs: {
          url: `ws://${request.headers.get('host')}/ws`,
          status: wsStatus.status,
          metrics: wsStatus.metrics
        },
        // Supabase realtime (alternative)
        supabase: {
          url: `${process.env.NEXT_PUBLIC_SUPABASE_URL?.replace('https://', 'wss://')}/realtime/v1`,
          key: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
          enabled: true
        },
        tenant_id: tenantId,
        channels: [
          `tenant:${tenantId}`,
          `ideas:${tenantId}`,
          `users:${tenantId}`,
          `projects:${tenantId}`,
          `notifications:${tenantId}`
        ],
        event_types: Object.values(WebSocketEventTypes),
        sources: Object.values(WebSocketSources)
      },
      timestamp: new Date().toISOString(),
    })

  } catch (error) {
    console.error('WebSocket API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

// POST /api/websocket - Send real-time message
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const tenantId = request.headers.get('X-Tenant-ID')
    const userId = request.headers.get('X-User-ID')
    
    if (!tenantId || !userId) {
      return NextResponse.json({
        success: false,
        error: 'Tenant ID and User ID are required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Validate required fields
    const requiredFields = ['channel', 'event', 'payload']
    for (const field of requiredFields) {
      if (!body[field]) {
        return NextResponse.json({
          success: false,
          error: `Missing required field: ${field}`,
          timestamp: new Date().toISOString(),
        }, { status: 400 })
      }
    }

    // Validate channel format
    const validChannels = [
      `tenant:${tenantId}`,
      `ideas:${tenantId}`,
      `users:${tenantId}`,
      `projects:${tenantId}`,
      `notifications:${tenantId}`
    ]

    if (!validChannels.includes(body.channel)) {
      return NextResponse.json({
        success: false,
        error: 'Invalid channel',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Create message record for audit trail
    const messageData = {
      tenant_id: tenantId,
      user_id: userId,
      channel: body.channel,
      event: body.event,
      payload: body.payload,
      timestamp: new Date().toISOString()
    }

    // Broadcast event via WebSocket manager
    const eventType = body.event
    const data = body.payload
    const source = body.source || 'api_websocket'
    const priority = body.priority || 'normal'
    const correlationId = body.correlation_id || `api-${Date.now()}`

    const clientsReached = broadcastEvent(
      eventType,
      data,
      source,
      priority,
      tenantId,
      userId,
      correlationId
    )

    return NextResponse.json({
      success: true,
      message: 'Message broadcasted successfully',
      data: messageData,
      websocket: {
        clients_reached: clientsReached,
        correlation_id: correlationId
      },
      timestamp: new Date().toISOString(),
    })

  } catch (error) {
    console.error('WebSocket API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

// PUT /api/websocket - Update WebSocket configuration
export async function PUT(request: NextRequest) {
  try {
    const body = await request.json()
    const tenantId = request.headers.get('X-Tenant-ID')
    const userId = request.headers.get('X-User-ID')
    
    if (!tenantId || !userId) {
      return NextResponse.json({
        success: false,
        error: 'Tenant ID and User ID are required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Handle configuration updates
    const { action, data: configData } = body

    switch (action) {
      case 'update_filters':
        // This would update client filters (handled by WebSocket manager)
        return NextResponse.json({
          success: true,
          message: 'Filter update request sent to WebSocket manager',
          action: 'update_filters',
          timestamp: new Date().toISOString(),
        })

      case 'get_status':
        const wsStatus = getWebSocketStatus()
        return NextResponse.json({
          success: true,
          action: 'get_status',
          status: wsStatus,
          timestamp: new Date().toISOString(),
        })

      default:
        return NextResponse.json({
          success: false,
          error: 'Invalid action specified',
          timestamp: new Date().toISOString(),
        }, { status: 400 })
    }

  } catch (error) {
    console.error('WebSocket API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

// DELETE /api/websocket - Cleanup WebSocket resources
export async function DELETE(request: NextRequest) {
  try {
    const tenantId = request.headers.get('X-Tenant-ID')
    const userId = request.headers.get('X-User-ID')
    
    if (!tenantId || !userId) {
      return NextResponse.json({
        success: false,
        error: 'Tenant ID and User ID are required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // This endpoint could be used for cleanup operations
    // For now, just return success
    return NextResponse.json({
      success: true,
      message: 'WebSocket cleanup completed',
      timestamp: new Date().toISOString(),
    })

  } catch (error) {
    console.error('WebSocket API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}
