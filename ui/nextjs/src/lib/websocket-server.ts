/**
 * WebSocket Server Initialization for Next.js
 * Handles server setup and integration with Next.js
 */

import { getWebSocketManager, EventMessage } from './websocket-manager'
import { v4 as uuidv4 } from 'uuid'

// WebSocket server instance
let wsServer: any = null

/**
 * Initialize WebSocket server with HTTP server
 */
export function initializeWebSocketServer(server: any): void {
  try {
    const wsManager = getWebSocketManager()
    wsManager.initialize(server)
    
    // Start ping interval
    wsManager.startPingInterval(30000) // 30 seconds
    
    // Set up event handlers
    wsManager.on('client_connected', (client) => {
      console.log(`WebSocket client connected: ${client.id}`)
    })
    
    wsManager.on('client_disconnected', (client) => {
      console.log(`WebSocket client disconnected: ${client.id}`)
    })
    
    wsManager.on('error', (error) => {
      console.error('WebSocket manager error:', error)
    })
    
    wsServer = server
    console.log('WebSocket server initialized successfully')
  } catch (error) {
    console.error('Failed to initialize WebSocket server:', error)
  }
}

/**
 * Get WebSocket manager instance
 */
export function getWSManager() {
  return getWebSocketManager()
}

/**
 * Broadcast event to all connected clients
 */
export function broadcastEvent(
  eventType: string,
  data: any,
  source: string = 'system',
  priority: 'low' | 'normal' | 'high' | 'critical' = 'normal',
  tenantId?: string,
  userId?: string,
  correlationId?: string
): number {
  try {
    const wsManager = getWebSocketManager()
    
    const event: EventMessage = {
      id: uuidv4(),
      eventType,
      data,
      timestamp: new Date().toISOString(),
      source,
      priority,
      tenantId,
      userId,
      correlationId
    }
    
    return wsManager.broadcastEvent(event)
  } catch (error) {
    console.error('Failed to broadcast event:', error)
    return 0
  }
}

/**
 * Send event to specific client
 */
export function sendToClient(
  clientId: string,
  eventType: string,
  data: any,
  source: string = 'system',
  priority: 'low' | 'normal' | 'high' | 'critical' = 'normal',
  tenantId?: string,
  userId?: string,
  correlationId?: string
): boolean {
  try {
    const wsManager = getWebSocketManager()
    
    const event: EventMessage = {
      id: uuidv4(),
      eventType,
      data,
      timestamp: new Date().toISOString(),
      source,
      priority,
      tenantId,
      userId,
      correlationId
    }
    
    return wsManager.sendToClient(clientId, event)
  } catch (error) {
    console.error('Failed to send event to client:', error)
    return false
  }
}

/**
 * Send event to all clients in a tenant
 */
export function sendToTenant(
  tenantId: string,
  eventType: string,
  data: any,
  source: string = 'system',
  priority: 'low' | 'normal' | 'high' | 'critical' = 'normal',
  correlationId?: string
): number {
  try {
    const wsManager = getWebSocketManager()
    const tenantClients = wsManager.getClientsByTenant(tenantId)
    
    let successfulSends = 0
    
    for (const client of tenantClients) {
      if (sendToClient(
        client.id,
        eventType,
        data,
        source,
        priority,
        tenantId,
        client.userId,
        correlationId
      )) {
        successfulSends++
      }
    }
    
    return successfulSends
  } catch (error) {
    console.error('Failed to send event to tenant:', error)
    return 0
  }
}

/**
 * Send event to all clients of a specific user
 */
export function sendToUser(
  userId: string,
  eventType: string,
  data: any,
  source: string = 'system',
  priority: 'low' | 'normal' | 'high' | 'critical' = 'normal',
  tenantId?: string,
  correlationId?: string
): number {
  try {
    const wsManager = getWebSocketManager()
    const userClients = wsManager.getClientsByUser(userId)
    
    let successfulSends = 0
    
    for (const client of userClients) {
      if (sendToClient(
        client.id,
        eventType,
        data,
        source,
        priority,
        tenantId || client.tenantId,
        userId,
        correlationId
      )) {
        successfulSends++
      }
    }
    
    return successfulSends
  } catch (error) {
    console.error('Failed to send event to user:', error)
    return 0
  }
}

/**
 * Get WebSocket server status
 */
export function getWebSocketStatus() {
  try {
    const wsManager = getWebSocketManager()
    const metrics = wsManager.getMetrics()
    
    return {
      status: 'active',
      metrics,
      timestamp: new Date().toISOString()
    }
  } catch (error) {
    return {
      status: 'error',
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString()
    }
  }
}

/**
 * Shutdown WebSocket server
 */
export function shutdownWebSocketServer(): void {
  try {
    const wsManager = getWebSocketManager()
    wsManager.shutdown()
    wsServer = null
    console.log('WebSocket server shutdown complete')
  } catch (error) {
    console.error('Failed to shutdown WebSocket server:', error)
  }
}

/**
 * Check if WebSocket server is running
 */
export function isWebSocketServerRunning(): boolean {
  return wsServer !== null
}

// Export common event types for consistency
export const WebSocketEventTypes = {
  // System events
  CONNECTION: 'connection',
  DISCONNECTION: 'disconnection',
  PING: 'ping',
  PONG: 'pong',
  
  // User events
  USER_LOGIN: 'user_login',
  USER_LOGOUT: 'user_logout',
  USER_UPDATE: 'user_update',
  
  // Business events
  IDEA_CREATED: 'idea_created',
  IDEA_UPDATED: 'idea_updated',
  IDEA_DELETED: 'idea_deleted',
  
  PROJECT_CREATED: 'project_created',
  PROJECT_UPDATED: 'project_updated',
  PROJECT_DELETED: 'project_deleted',
  
  NOTIFICATION_CREATED: 'notification_created',
  NOTIFICATION_READ: 'notification_read',
  
  // AI Agent events
  AGENT_STARTED: 'agent_started',
  AGENT_COMPLETED: 'agent_completed',
  AGENT_ERROR: 'agent_error',
  
  // Factory events
  FACTORY_TRIGGERED: 'factory_triggered',
  FACTORY_PROGRESS: 'factory_progress',
  FACTORY_COMPLETED: 'factory_completed',
  FACTORY_ERROR: 'factory_error'
} as const

// Export common sources for consistency
export const WebSocketSources = {
  SYSTEM: 'system',
  WEBSOCKET_MANAGER: 'websocket_manager',
  USER_SERVICE: 'user_service',
  IDEA_SERVICE: 'idea_service',
  PROJECT_SERVICE: 'project_service',
  NOTIFICATION_SERVICE: 'notification_service',
  AI_AGENT_SERVICE: 'ai_agent_service',
  FACTORY_SERVICE: 'factory_service'
} as const
