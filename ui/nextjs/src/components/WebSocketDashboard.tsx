/**
 * WebSocket Dashboard Component
 * Provides real-time monitoring and testing of WebSocket functionality
 */

import React, { useState, useCallback, useEffect } from 'react'
import useWebSocket from '@/hooks/useWebSocket'
import { WebSocketEventTypes, WebSocketSources } from '@/lib/websocket-server'

interface WebSocketDashboardProps {
  className?: string
  tenantId?: string
  userId?: string
}

interface TestEvent {
  eventType: string
  data: any
  source: string
  priority: 'low' | 'normal' | 'high' | 'critical'
}

const WebSocketDashboard: React.FC<WebSocketDashboardProps> = ({
  className = '',
  tenantId = 'test-tenant',
  userId = 'test-user'
}) => {
  const [messages, setMessages] = useState<any[]>([])
  const [filters, setFilters] = useState({
    eventTypes: [] as string[],
    sources: [] as string[],
    priority: [] as string[]
  })
  const [testEvent, setTestEvent] = useState<TestEvent>({
    eventType: 'test',
    data: { message: 'Test message' },
    source: 'dashboard',
    priority: 'normal'
  })

  // WebSocket connection
  const {
    isConnected,
    connectionStatus,
    lastMessage,
    reconnectAttempts,
    error,
    connect,
    disconnect,
    sendMessage,
    updateFilters,
    subscribe,
    unsubscribe
  } = useWebSocket({
    tenantId,
    userId,
    filters,
    onMessage: (message) => {
      setMessages(prev => [message, ...prev.slice(0, 99)]) // Keep last 100 messages
    },
    onOpen: () => {
      console.log('WebSocket connected')
    },
    onClose: () => {
      console.log('WebSocket disconnected')
    },
    onError: (error) => {
      console.error('WebSocket error:', error)
    },
    enabled: true,
    autoReconnect: true
  })

  // Handle incoming messages
  useEffect(() => {
    if (lastMessage) {
      setMessages(prev => [lastMessage, ...prev.slice(0, 99)])
    }
  }, [lastMessage])

  // Update filters
  const handleFilterChange = useCallback((key: string, value: string[]) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)
    updateFilters(newFilters)
  }, [filters, updateFilters])

  // Subscribe to channel
  const handleSubscribe = useCallback((channel: string) => {
    subscribe(channel, filters.eventTypes)
  }, [subscribe, filters.eventTypes])

  // Unsubscribe from channel
  const handleUnsubscribe = useCallback((channel: string) => {
    unsubscribe(channel, filters.eventTypes)
  }, [unsubscribe, filters.eventTypes])

  // Send test event
  const handleSendTestEvent = useCallback(() => {
    const success = sendMessage({
      type: 'test_event',
      event: testEvent.eventType,
      payload: testEvent.data,
      source: testEvent.source,
      priority: testEvent.priority
    })

    if (success) {
      console.log('Test event sent successfully')
    } else {
      console.error('Failed to send test event')
    }
  }, [sendMessage, testEvent])

  // Clear messages
  const handleClearMessages = useCallback(() => {
    setMessages([])
  }, [])

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'text-green-600'
      case 'connecting': return 'text-yellow-600'
      case 'disconnected': return 'text-red-600'
      case 'error': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  return (
    <div className={`bg-white rounded-lg shadow-lg p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">WebSocket Dashboard</h2>
        <div className="flex items-center space-x-4">
          <div className={`text-sm font-medium ${getStatusColor(connectionStatus)}`}>
            {connectionStatus.toUpperCase()}
          </div>
          <div className="text-sm text-gray-500">
            Reconnects: {reconnectAttempts}
          </div>
        </div>
      </div>

      {/* Connection Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-3">Connection</h3>
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium">Status:</span>
              <span className={`text-sm ${getStatusColor(connectionStatus)}`}>
                {connectionStatus}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium">Connected:</span>
              <span className={`text-sm ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
                {isConnected ? 'Yes' : 'No'}
              </span>
            </div>
            {error && (
              <div className="text-sm text-red-600">
                Error: {error}
              </div>
            )}
            <div className="flex space-x-2">
              <button
                onClick={connect}
                disabled={isConnected}
                className="px-3 py-1 bg-blue-600 text-white rounded text-sm disabled:opacity-50"
              >
                Connect
              </button>
              <button
                onClick={disconnect}
                disabled={!isConnected}
                className="px-3 py-1 bg-red-600 text-white rounded text-sm disabled:opacity-50"
              >
                Disconnect
              </button>
            </div>
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-3">Filters</h3>
          <div className="space-y-3">
            <div>
              <label htmlFor="event-types" className="block text-sm font-medium mb-1">Event Types</label>
              <select
                id="event-types"
                multiple
                value={filters.eventTypes}
                onChange={(e) => {
                  const values = Array.from(e.target.selectedOptions, option => option.value)
                  handleFilterChange('eventTypes', values)
                }}
                className="w-full p-2 border rounded text-sm"
                aria-label="Select event types to filter"
              >
                {Object.values(WebSocketEventTypes).map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="sources" className="block text-sm font-medium mb-1">Sources</label>
              <select
                id="sources"
                multiple
                value={filters.sources}
                onChange={(e) => {
                  const values = Array.from(e.target.selectedOptions, option => option.value)
                  handleFilterChange('sources', values)
                }}
                className="w-full p-2 border rounded text-sm"
                aria-label="Select sources to filter"
              >
                {Object.values(WebSocketSources).map(source => (
                  <option key={source} value={source}>{source}</option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="priority" className="block text-sm font-medium mb-1">Priority</label>
              <select
                id="priority"
                multiple
                value={filters.priority}
                onChange={(e) => {
                  const values = Array.from(e.target.selectedOptions, option => option.value)
                  handleFilterChange('priority', values)
                }}
                className="w-full p-2 border rounded text-sm"
                aria-label="Select priority levels to filter"
              >
                {['low', 'normal', 'high', 'critical'].map(priority => (
                  <option key={priority} value={priority}>{priority}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Channel Management */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <h3 className="text-lg font-semibold mb-3">Channel Management</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {['tenant', 'ideas', 'users', 'projects', 'notifications'].map(channel => (
            <div key={channel} className="text-center">
              <div className="text-sm font-medium mb-2">{channel}</div>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleSubscribe(channel)}
                  disabled={!isConnected}
                  className="px-2 py-1 bg-green-600 text-white rounded text-xs disabled:opacity-50"
                  aria-label={`Subscribe to ${channel} channel`}
                >
                  Subscribe
                </button>
                <button
                  onClick={() => handleUnsubscribe(channel)}
                  disabled={!isConnected}
                  className="px-2 py-1 bg-red-600 text-white rounded text-xs disabled:opacity-50"
                  aria-label={`Unsubscribe from ${channel} channel`}
                >
                  Unsubscribe
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Test Event */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <h3 className="text-lg font-semibold mb-3">Test Event</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label htmlFor="event-type" className="block text-sm font-medium mb-1">Event Type</label>
            <input
              id="event-type"
              type="text"
              value={testEvent.eventType}
              onChange={(e) => setTestEvent(prev => ({ ...prev, eventType: e.target.value }))}
              className="w-full p-2 border rounded text-sm"
              placeholder="Enter event type"
              aria-label="Event type for test message"
            />
          </div>
          <div>
            <label htmlFor="event-source" className="block text-sm font-medium mb-1">Source</label>
            <select
              id="event-source"
              value={testEvent.source}
              onChange={(e) => setTestEvent(prev => ({ ...prev, source: e.target.value }))}
              className="w-full p-2 border rounded text-sm"
              aria-label="Select source for test message"
            >
              {Object.values(WebSocketSources).map(source => (
                <option key={source} value={source}>{source}</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="event-priority" className="block text-sm font-medium mb-1">Priority</label>
            <select
              id="event-priority"
              value={testEvent.priority}
              onChange={(e) => setTestEvent(prev => ({ ...prev, priority: e.target.value as any }))}
              className="w-full p-2 border rounded text-sm"
              aria-label="Select priority for test message"
            >
              {['low', 'normal', 'high', 'critical'].map(priority => (
                <option key={priority} value={priority}>{priority}</option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={handleSendTestEvent}
              disabled={!isConnected}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
              aria-label="Send test event message"
            >
              Send Test Event
            </button>
          </div>
        </div>
        <div className="mt-3">
          <label htmlFor="message-data" className="block text-sm font-medium mb-1">Message Data</label>
          <textarea
            id="message-data"
            value={JSON.stringify(testEvent.data, null, 2)}
            onChange={(e) => {
              try {
                const data = JSON.parse(e.target.value)
                setTestEvent(prev => ({ ...prev, data }))
              } catch (error) {
                // Ignore invalid JSON
              }
            }}
            className="w-full p-2 border rounded text-sm font-mono text-xs"
            rows={3}
            placeholder="Enter JSON data for test message"
            aria-label="JSON data for test message"
          />
        </div>
      </div>

      {/* Messages */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold">Messages ({messages.length})</h3>
          <button
            onClick={handleClearMessages}
            className="px-3 py-1 bg-gray-600 text-white rounded text-sm"
            aria-label="Clear all messages"
          >
            Clear
          </button>
        </div>
        <div className="max-h-96 overflow-y-auto space-y-2">
          {messages.length === 0 ? (
            <div className="text-gray-500 text-center py-8">No messages received</div>
          ) : (
            messages.map((message, index) => (
              <div key={index} className="bg-white rounded border p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-blue-600">
                      {message.eventType}
                    </span>
                    <span className="text-xs text-gray-500">
                      {message.source}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded ${
                      message.priority === 'critical' ? 'bg-red-100 text-red-800' :
                      message.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                      message.priority === 'normal' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {message.priority}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {formatTimestamp(message.timestamp)}
                  </span>
                </div>
                <div className="text-sm text-gray-700">
                  <pre className="whitespace-pre-wrap">{JSON.stringify(message.data, null, 2)}</pre>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default WebSocketDashboard
