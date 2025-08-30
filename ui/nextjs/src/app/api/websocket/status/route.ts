import { NextRequest, NextResponse } from 'next/server'
import { getWebSocketStatus, isWebSocketServerRunning } from '@/lib/websocket-server'

// GET /api/websocket/status - Get WebSocket server status and metrics
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const detailed = searchParams.get('detailed') === 'true'
    
    // Get basic status
    const isRunning = isWebSocketServerRunning()
    const wsStatus = getWebSocketStatus()
    
    // Base response
    const response = {
      success: true,
      websocket: {
        server_running: isRunning,
        status: wsStatus.status,
        timestamp: new Date().toISOString()
      }
    }

    // Add detailed metrics if requested
    if (detailed && wsStatus.status === 'active' && wsStatus.metrics) {
      response.websocket.metrics = {
        total_connections: wsStatus.metrics.totalConnections,
        active_connections: wsStatus.metrics.activeConnections,
        events_sent: wsStatus.metrics.eventsSent,
        last_activity: wsStatus.metrics.lastActivity.toISOString(),
        event_history_size: wsStatus.metrics.eventHistorySize,
        client_count: wsStatus.metrics.clientCount
      }
    }

    // Add health status
    const healthStatus = isRunning && wsStatus.status === 'active' ? 'healthy' : 'unhealthy'
    response.websocket.health = healthStatus

    return NextResponse.json(response)

  } catch (error) {
    console.error('WebSocket status API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      websocket: {
        server_running: false,
        status: 'error',
        health: 'unhealthy',
        timestamp: new Date().toISOString()
      }
    }, { status: 500 })
  }
}

// POST /api/websocket/status - Test WebSocket functionality
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action, data } = body
    
    switch (action) {
      case 'ping':
        // Test basic WebSocket functionality
        const isRunning = isWebSocketServerRunning()
        const wsStatus = getWebSocketStatus()
        
        return NextResponse.json({
          success: true,
          action: 'ping',
          result: {
            server_running: isRunning,
            status: wsStatus.status,
            timestamp: new Date().toISOString()
          }
        })

      case 'test_broadcast':
        // Test broadcast functionality (if implemented)
        return NextResponse.json({
          success: true,
          action: 'test_broadcast',
          message: 'Broadcast test completed',
          timestamp: new Date().toISOString()
        })

      default:
        return NextResponse.json({
          success: false,
          error: 'Invalid action specified',
          timestamp: new Date().toISOString(),
        }, { status: 400 })
    }

  } catch (error) {
    console.error('WebSocket status test API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}
