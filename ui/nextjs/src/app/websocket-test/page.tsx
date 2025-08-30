/**
 * WebSocket Test Page
 * Demonstrates WebSocket functionality and provides testing interface
 */

import React from 'react'
import WebSocketDashboard from '@/components/WebSocketDashboard'

export default function WebSocketTestPage() {
  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">WebSocket Testing & Monitoring</h1>
          <p className="mt-2 text-gray-600">
            Test and monitor real-time WebSocket communication in the Next.js application
          </p>
        </div>
        
        <WebSocketDashboard 
          tenantId="test-tenant-123"
          userId="test-user-456"
        />
        
        <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">WebSocket Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <h3 className="font-medium text-blue-900">Real-time Communication</h3>
              <p className="text-sm text-blue-700 mt-1">
                Instant message delivery with sub-second latency
              </p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <h3 className="font-medium text-green-900">Auto-reconnection</h3>
              <p className="text-sm text-green-700 mt-1">
                Automatic reconnection with configurable retry attempts
              </p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <h3 className="font-medium text-purple-900">Message Filtering</h3>
              <p className="text-sm text-purple-700 mt-1">
                Filter messages by type, source, priority, and more
              </p>
            </div>
            <div className="bg-orange-50 rounded-lg p-4">
              <h3 className="font-medium text-orange-900">Channel Management</h3>
              <p className="text-sm text-orange-700 mt-1">
                Subscribe/unsubscribe to specific channels
              </p>
            </div>
            <div className="bg-red-50 rounded-lg p-4">
              <h3 className="font-medium text-red-900">Priority System</h3>
              <p className="text-sm text-red-700 mt-1">
                Message priority levels: low, normal, high, critical
              </p>
            </div>
            <div className="bg-indigo-50 rounded-lg p-4">
              <h3 className="font-medium text-indigo-900">Tenant Isolation</h3>
              <p className="text-sm text-indigo-700 mt-1">
                Secure multi-tenant communication with isolation
              </p>
            </div>
          </div>
        </div>
        
        <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Usage Instructions</h2>
          <div className="space-y-4 text-sm text-gray-700">
            <div>
              <h3 className="font-medium text-gray-900">1. Connection</h3>
              <p>Click "Connect" to establish a WebSocket connection. The status will show "Connected" when successful.</p>
            </div>
            <div>
              <h3 className="font-medium text-gray-900">2. Filters</h3>
              <p>Use the filter options to control which messages you receive. You can filter by event type, source, and priority.</p>
            </div>
            <div>
              <h3 className="font-medium text-gray-900">3. Channels</h3>
              <p>Subscribe to specific channels (tenant, ideas, users, projects, notifications) to receive relevant messages.</p>
            </div>
            <div>
              <h3 className="font-medium text-gray-900">4. Test Events</h3>
              <p>Send test events to verify the WebSocket functionality. Customize the event type, source, priority, and data.</p>
            </div>
            <div>
              <h3 className="font-medium text-gray-900">5. Monitoring</h3>
              <p>Monitor incoming messages in real-time. Messages are displayed with timestamps and metadata.</p>
            </div>
          </div>
        </div>
        
        <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">API Endpoints</h2>
          <div className="space-y-3 text-sm">
            <div className="bg-gray-50 rounded p-3">
              <code className="text-blue-600">GET /api/websocket</code>
              <p className="text-gray-600 mt-1">Get WebSocket connection information and status</p>
            </div>
            <div className="bg-gray-50 rounded p-3">
              <code className="text-blue-600">POST /api/websocket</code>
              <p className="text-gray-600 mt-1">Send real-time message via WebSocket</p>
            </div>
            <div className="bg-gray-50 rounded p-3">
              <code className="text-blue-600">GET /api/websocket/status</code>
              <p className="text-gray-600 mt-1">Get WebSocket server status and metrics</p>
            </div>
            <div className="bg-gray-50 rounded p-3">
              <code className="text-blue-600">POST /api/websocket/status</code>
              <p className="text-gray-600 mt-1">Test WebSocket functionality</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
