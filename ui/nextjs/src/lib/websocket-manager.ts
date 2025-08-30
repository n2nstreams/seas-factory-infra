/**
 * WebSocket Manager for Next.js
 * Handles WebSocket connections, event broadcasting, and client management
 * Migrated from legacy Python WebSocket manager
 */

import { WebSocket, WebSocketServer } from 'ws'
import { EventEmitter } from 'events'
import { v4 as uuidv4 } from 'uuid'

// Types
export interface WebSocketClient {
  id: string
  websocket: WebSocket
  connectedAt: Date
  lastPing: Date
  filters: Record<string, any>
  tenantId?: string
  userId?: string
  metadata: Record<string, any>
}

export interface EventMessage {
  id: string
  eventType: string
  data: any
  timestamp: string
  source: string
  priority: 'low' | 'normal' | 'high' | 'critical'
  tenantId?: string
  userId?: string
  correlationId?: string
}

export interface WebSocketMetrics {
  totalConnections: number
  activeConnections: number
  eventsSent: number
  lastActivity: Date
  eventHistorySize: number
  clientCount: number
}

export interface WebSocketFilters {
  eventTypes?: string[]
  sources?: string[]
  priority?: string[]
  tenantId?: string
  userId?: string
  search?: string
  timeRange?: string
}

export class WebSocketManager extends EventEmitter {
  private wss: WebSocketServer | null = null
  private clients: Map<string, WebSocketClient> = new Map()
  private eventHistory: EventMessage[] = []
  private metrics: WebSocketMetrics
  private maxHistorySize: number = 1000
  private maxClients: number = 100
  private pingInterval: NodeJS.Timeout | null = null
  private cleanupInterval: NodeJS.Timeout | null = null

  constructor() {
    super()
    this.metrics = {
      totalConnections: 0,
      activeConnections: 0,
      eventsSent: 0,
      lastActivity: new Date(),
      eventHistorySize: 0,
      clientCount: 0
    }
    
    this.startCleanupInterval()
    console.log('WebSocket Manager initialized')
  }

  /**
   * Initialize WebSocket server
   */
  public initialize(server: any): void {
    if (this.wss) {
      console.warn('WebSocket server already initialized')
      return
    }

    this.wss = new WebSocketServer({ server })
    
    this.wss.on('connection', (ws: WebSocket, request: any) => {
      this.handleConnection(ws, request)
    })

    this.wss.on('error', (error: Error) => {
      console.error('WebSocket server error:', error)
      this.emit('error', error)
    })

    console.log('WebSocket server initialized')
  }

  /**
   * Handle new WebSocket connection
   */
  private handleConnection(ws: WebSocket, request: any): void {
    const clientId = uuidv4()
    const url = new URL(request.url, 'http://localhost')
    
    // Extract query parameters
    const tenantId = url.searchParams.get('tenant_id')
    const userId = url.searchParams.get('user_id')
    const eventTypes = url.searchParams.get('event_types')?.split(',') || []
    
    // Create client
    const client: WebSocketClient = {
      id: clientId,
      websocket: ws,
      connectedAt: new Date(),
      lastPing: new Date(),
      filters: {
        eventTypes,
        tenantId,
        userId
      },
      tenantId: tenantId || undefined,
      userId: userId || undefined,
      metadata: {
        userAgent: request.headers['user-agent'],
        ip: request.socket.remoteAddress,
        url: request.url
      }
    }

    // Store client
    this.clients.set(clientId, client)
    this.metrics.totalConnections++
    this.metrics.activeConnections++
    this.metrics.clientCount = this.clients.size
    this.metrics.lastActivity = new Date()

    // Send welcome message
    const welcomeEvent: EventMessage = {
      id: uuidv4(),
      eventType: 'connection',
      data: {
        message: `Connected to WebSocket server as ${clientId}`,
        clientId,
        timestamp: new Date().toISOString()
      },
      timestamp: new Date().toISOString(),
      source: 'websocket_manager',
      priority: 'normal',
      tenantId,
      userId
    }

    this.sendToClient(clientId, welcomeEvent)

    // Set up event handlers
    ws.on('message', (data: Buffer) => {
      this.handleClientMessage(clientId, data.toString())
    })

    ws.on('close', () => {
      this.handleClientDisconnect(clientId)
    })

    ws.on('error', (error: Error) => {
      console.error(`WebSocket error for client ${clientId}:`, error)
      this.handleClientDisconnect(clientId)
    })

    // Emit connection event
    this.emit('client_connected', client)
    console.log(`WebSocket client ${clientId} connected (${this.metrics.activeConnections} active)`)
  }

  /**
   * Handle client message
   */
  private handleClientMessage(clientId: string, message: string): void {
    try {
      const data = JSON.parse(message)
      const client = this.clients.get(clientId)
      
      if (!client) return

      // Update last ping
      client.lastPing = new Date()
      this.metrics.lastActivity = new Date()

      // Handle different message types
      switch (data.type) {
        case 'filters':
          this.updateClientFilters(clientId, data.filters || {})
          break
        case 'ping':
          this.sendToClient(clientId, {
            id: uuidv4(),
            eventType: 'pong',
            data: { timestamp: new Date().toISOString() },
            timestamp: new Date().toISOString(),
            source: 'websocket_manager',
            priority: 'normal'
          })
          break
        case 'subscribe':
          this.handleSubscription(clientId, data)
          break
        case 'unsubscribe':
          this.handleUnsubscription(clientId, data)
          break
        default:
          console.log(`Unknown message type from client ${clientId}:`, data.type)
      }
    } catch (error) {
      console.error(`Error parsing message from client ${clientId}:`, error)
    }
  }

  /**
   * Update client filters
   */
  private updateClientFilters(clientId: string, filters: WebSocketFilters): void {
    const client = this.clients.get(clientId)
    if (!client) return

    client.filters = { ...client.filters, ...filters }
    console.log(`Updated filters for client ${clientId}:`, filters)
    
    this.emit('filters_updated', { clientId, filters })
  }

  /**
   * Handle subscription request
   */
  private handleSubscription(clientId: string, data: any): void {
    const client = this.clients.get(clientId)
    if (!client) return

    const { channel, eventTypes } = data
    
    if (channel) {
      client.filters.channel = channel
    }
    
    if (eventTypes) {
      client.filters.eventTypes = Array.isArray(eventTypes) ? eventTypes : [eventTypes]
    }

    console.log(`Client ${clientId} subscribed to channel: ${channel}, events: ${eventTypes}`)
    this.emit('subscription_updated', { clientId, channel, eventTypes })
  }

  /**
   * Handle unsubscription request
   */
  private handleUnsubscription(clientId: string, data: any): void {
    const client = this.clients.get(clientId)
    if (!client) return

    const { channel, eventTypes } = data
    
    if (channel) {
      delete client.filters.channel
    }
    
    if (eventTypes) {
      client.filters.eventTypes = client.filters.eventTypes?.filter(
        (type: string) => !eventTypes.includes(type)
      )
    }

    console.log(`Client ${clientId} unsubscribed from channel: ${channel}, events: ${eventTypes}`)
    this.emit('subscription_updated', { clientId, channel, eventTypes })
  }

  /**
   * Handle client disconnect
   */
  private handleClientDisconnect(clientId: string): void {
    const client = this.clients.get(clientId)
    if (!client) return

    // Clean up client
    this.clients.delete(clientId)
    this.metrics.activeConnections--
    this.metrics.clientCount = this.clients.size
    this.metrics.lastActivity = new Date()

    // Emit disconnect event
    this.emit('client_disconnected', client)
    console.log(`WebSocket client ${clientId} disconnected (${this.metrics.activeConnections} active)`)
  }

  /**
   * Send message to specific client
   */
  public sendToClient(clientId: string, event: EventMessage): boolean {
    const client = this.clients.get(clientId)
    if (!client || client.websocket.readyState !== WebSocket.OPEN) {
      return false
    }

    try {
      client.websocket.send(JSON.stringify(event))
      this.metrics.eventsSent++
      this.metrics.lastActivity = new Date()
      return true
    } catch (error) {
      console.error(`Error sending message to client ${clientId}:`, error)
      return false
    }
  }

  /**
   * Broadcast event to all connected clients
   */
  public broadcastEvent(event: EventMessage): number {
    let successfulSends = 0
    const clientsToRemove: string[] = []

    // Add to history
    this.eventHistory.push(event)
    if (this.eventHistory.length > this.maxHistorySize) {
      this.eventHistory.shift()
    }
    this.metrics.eventHistorySize = this.eventHistory.length

    // Send to all connected clients
    for (const [clientId, client] of this.clients) {
      try {
        // Apply client filters
        if (this.shouldSendToClient(event, client)) {
          if (this.sendToClient(clientId, event)) {
            successfulSends++
          }
        }
      } catch (error) {
        console.error(`Error broadcasting to client ${clientId}:`, error)
        clientsToRemove.push(clientId)
      }
    }

    // Remove disconnected clients
    clientsToRemove.forEach(clientId => {
      this.handleClientDisconnect(clientId)
    })

    if (successfulSends > 0) {
      console.debug(`Broadcast event to ${successfulSends} clients`)
    }

    return successfulSends
  }

  /**
   * Check if event should be sent to client based on filters
   */
  private shouldSendToClient(event: EventMessage, client: WebSocketClient): boolean {
    const { filters } = client

    // Check event type filter
    if (filters.eventTypes && filters.eventTypes.length > 0) {
      if (!filters.eventTypes.includes(event.eventType)) {
        return false
      }
    }

    // Check source filter
    if (filters.sources && filters.sources.length > 0) {
      if (!filters.sources.includes(event.source)) {
        return false
      }
    }

    // Check priority filter
    if (filters.priority && filters.priority.length > 0) {
      if (!filters.priority.includes(event.priority)) {
        return false
      }
    }

    // Check tenant isolation
    if (filters.tenantId && event.tenantId) {
      if (filters.tenantId !== event.tenantId) {
        return false
      }
    }

    // Check user isolation
    if (filters.userId && event.userId) {
      if (filters.userId !== event.userId) {
        return false
      }
    }

    return true
  }

  /**
   * Get client by ID
   */
  public getClient(clientId: string): WebSocketClient | undefined {
    return this.clients.get(clientId)
  }

  /**
   * Get all clients
   */
  public getAllClients(): WebSocketClient[] {
    return Array.from(this.clients.values())
  }

  /**
   * Get clients by tenant
   */
  public getClientsByTenant(tenantId: string): WebSocketClient[] {
    return Array.from(this.clients.values()).filter(client => client.tenantId === tenantId)
  }

  /**
   * Get clients by user
   */
  public getClientsByUser(userId: string): WebSocketClient[] {
    return Array.from(this.clients.values()).filter(client => client.userId === userId)
  }

  /**
   * Get metrics
   */
  public getMetrics(): WebSocketMetrics {
    return { ...this.metrics }
  }

  /**
   * Get event history
   */
  public getEventHistory(limit: number = 100): EventMessage[] {
    return this.eventHistory.slice(-limit)
  }

  /**
   * Start ping interval
   */
  public startPingInterval(intervalMs: number = 30000): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval)
    }

    this.pingInterval = setInterval(() => {
      const pingEvent: EventMessage = {
        id: uuidv4(),
        eventType: 'ping',
        data: { timestamp: new Date().toISOString() },
        timestamp: new Date().toISOString(),
        source: 'websocket_manager',
        priority: 'normal'
      }

      this.broadcastEvent(pingEvent)
    }, intervalMs)

    console.log(`Started ping interval: ${intervalMs}ms`)
  }

  /**
   * Stop ping interval
   */
  public stopPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval)
      this.pingInterval = null
      console.log('Stopped ping interval')
    }
  }

  /**
   * Start cleanup interval
   */
  private startCleanupInterval(): void {
    this.cleanupInterval = setInterval(() => {
      this.cleanupInactiveClients()
    }, 60000) // Run every minute
  }

  /**
   * Clean up inactive clients
   */
  private cleanupInactiveClients(): void {
    const now = new Date()
    const inactiveThreshold = 5 * 60 * 1000 // 5 minutes

    for (const [clientId, client] of this.clients) {
      const timeSinceLastPing = now.getTime() - client.lastPing.getTime()
      
      if (timeSinceLastPing > inactiveThreshold) {
        console.log(`Cleaning up inactive client ${clientId}`)
        this.handleClientDisconnect(clientId)
      }
    }
  }

  /**
   * Shutdown WebSocket server
   */
  public shutdown(): void {
    // Stop intervals
    this.stopPingInterval()
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval)
      this.cleanupInterval = null
    }

    // Close all client connections
    for (const [clientId, client] of this.clients) {
      try {
        client.websocket.close()
      } catch (error) {
        console.error(`Error closing client ${clientId}:`, error)
      }
    }

    // Close server
    if (this.wss) {
      this.wss.close()
      this.wss = null
    }

    // Clear clients
    this.clients.clear()
    this.metrics.activeConnections = 0
    this.metrics.clientCount = 0

    console.log('WebSocket server shutdown complete')
  }
}

// Singleton instance
let websocketManager: WebSocketManager | null = null

export function getWebSocketManager(): WebSocketManager {
  if (!websocketManager) {
    websocketManager = new WebSocketManager()
  }
  return websocketManager
}

export function shutdownWebSocketManager(): void {
  if (websocketManager) {
    websocketManager.shutdown()
    websocketManager = null
  }
}
