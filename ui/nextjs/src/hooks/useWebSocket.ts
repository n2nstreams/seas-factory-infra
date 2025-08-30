/**
 * WebSocket Hook for Next.js
 * Provides real-time communication with the WebSocket server
 */

import { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import { v4 as uuidv4 } from 'uuid'

// Types
export interface WebSocketMessage {
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

export interface WebSocketFilters {
  eventTypes?: string[]
  sources?: string[]
  priority?: string[]
  tenantId?: string
  userId?: string
  search?: string
  timeRange?: string
}

export interface UseWebSocketOptions {
  url?: string
  tenantId?: string
  userId?: string
  filters?: WebSocketFilters
  onMessage?: (message: WebSocketMessage) => void
  onOpen?: () => void
  onClose?: () => void
  onError?: (error: Event) => void
  reconnectInterval?: number
  maxReconnectAttempts?: number
  enabled?: boolean
  autoReconnect?: boolean
}

export interface WebSocketState {
  isConnected: boolean
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error'
  lastMessage: WebSocketMessage | null
  reconnectAttempts: number
  error: string | null
}

export interface WebSocketActions {
  connect: () => void
  disconnect: () => void
  sendMessage: (message: any) => boolean
  updateFilters: (filters: WebSocketFilters) => void
  subscribe: (channel: string, eventTypes?: string[]) => void
  unsubscribe: (channel: string, eventTypes?: string[]) => void
}

export function useWebSocket(options: UseWebSocketOptions): WebSocketState & WebSocketActions {
  const {
    url,
    tenantId,
    userId,
    filters = {},
    onMessage,
    onOpen,
    onClose,
    onError,
    reconnectInterval = 5000,
    maxReconnectAttempts = 5,
    enabled = true,
    autoReconnect = true
  } = options

  // State
  const [isConnected, setIsConnected] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [reconnectAttempts, setReconnectAttempts] = useState(0)
  const [error, setError] = useState<string | null>(null)

  // Refs
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const clientIdRef = useRef<string>(uuidv4())

  // Memoized WebSocket URL
  const wsUrl = useMemo(() => {
    if (url) return url
    
    // Default to Next.js WebSocket server
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const baseUrl = `${protocol}//${host}/ws`
    
    // Add query parameters
    const params = new URLSearchParams()
    if (tenantId) params.append('tenant_id', tenantId)
    if (userId) params.append('user_id', userId)
    if (filters.eventTypes?.length) params.append('event_types', filters.eventTypes.join(','))
    
    const queryString = params.toString()
    return queryString ? `${baseUrl}?${queryString}` : baseUrl
  }, [url, tenantId, userId, filters.eventTypes])

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (!enabled || wsRef.current?.readyState === WebSocket.CONNECTING) {
      return
    }

    try {
      setConnectionStatus('connecting')
      setError(null)
      
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
        setConnectionStatus('connected')
        setReconnectAttempts(0)
        setError(null)
        onOpen?.()
        
        // Send initial filters
        if (Object.keys(filters).length > 0) {
          ws.send(JSON.stringify({
            type: 'filters',
            filters
          }))
        }
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          setLastMessage(message)
          onMessage?.(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
          setError('Failed to parse message')
        }
      }

      ws.onclose = (event) => {
        setIsConnected(false)
        setConnectionStatus('disconnected')
        wsRef.current = null
        onClose?.()

        // Attempt to reconnect
        if (autoReconnect && enabled && reconnectAttempts < maxReconnectAttempts) {
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectAttempts(prev => prev + 1)
            connect()
          }, reconnectInterval)
        }
      }

      ws.onerror = (error) => {
        setConnectionStatus('error')
        setError('WebSocket connection error')
        onError?.(error)
      }

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      setConnectionStatus('error')
      setError('Failed to create connection')
    }
  }, [wsUrl, enabled, filters, reconnectAttempts, maxReconnectAttempts, reconnectInterval, autoReconnect, onOpen, onMessage, onClose, onError])

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    // Clear reconnect timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    // Close WebSocket connection
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    setIsConnected(false)
    setConnectionStatus('disconnected')
    setError(null)
  }, [])

  // Send message
  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
      return true
    }
    return false
  }, [])

  // Update filters
  const updateFilters = useCallback((newFilters: WebSocketFilters) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'filters',
        filters: newFilters
      }))
    }
  }, [])

  // Subscribe to channel
  const subscribe = useCallback((channel: string, eventTypes?: string[]) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'subscribe',
        channel,
        eventTypes
      }))
    }
  }, [])

  // Unsubscribe from channel
  const unsubscribe = useCallback((channel: string, eventTypes?: string[]) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'unsubscribe',
        channel,
        eventTypes
      }))
    }
  }, [])

  // Connect on mount if enabled
  useEffect(() => {
    if (enabled) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [enabled, connect, disconnect])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [disconnect])

  return {
    // State
    isConnected,
    connectionStatus,
    lastMessage,
    reconnectAttempts,
    error,
    
    // Actions
    connect,
    disconnect,
    sendMessage,
    updateFilters,
    subscribe,
    unsubscribe
  }
}

export default useWebSocket
