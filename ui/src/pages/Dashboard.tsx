import { useEffect, useState } from 'react'

interface AgentEvent {
  type: string
  timestamp: number
  stage?: string
  agent?: string
  request_id?: string
  status?: string
  result?: any
  error?: string
  received_at?: string
  message_id?: string
  publish_time?: string
}

interface EventsResponse {
  events: AgentEvent[]
  count: number
  timestamp: number
}

export default function Dashboard() {
  const [events, setEvents] = useState<AgentEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await fetch('/api/events')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data: EventsResponse = await response.json()
        setEvents(data.events)
        setLastUpdate(new Date())
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
        console.error('Error fetching events:', err)
      } finally {
        setLoading(false)
      }
    }

    // Initial fetch
    fetchEvents()

    // Set up polling every 3 seconds
    const interval = setInterval(fetchEvents, 3000)

    // Cleanup
    return () => clearInterval(interval)
  }, [])

  const formatTimestamp = (timestamp: number | string) => {
    const date = typeof timestamp === 'number' ? new Date(timestamp * 1000) : new Date(timestamp)
    return date.toLocaleString()
  }

  const getEventColor = (type: string) => {
    switch (type) {
      case 'START':
        return 'text-blue-600 bg-blue-50'
      case 'FINISH':
        return 'text-green-600 bg-green-50'
      case 'ERROR':
        return 'text-red-600 bg-red-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading events...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Agent Events Dashboard
          </h1>
          <p className="text-gray-600">
            Real-time monitoring of SaaS Factory agent activities
          </p>
          {lastUpdate && (
            <p className="text-sm text-gray-500 mt-2">
              Last updated: {lastUpdate.toLocaleString()}
            </p>
          )}
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">
              Recent Events ({events.length})
            </h2>
          </div>

          <div className="overflow-hidden">
            {events.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
                <p>No events yet. Events will appear here as agents perform tasks.</p>
              </div>
            ) : (
              <div className="max-h-96 overflow-y-auto">
                {events.map((event, index) => (
                  <div key={index} className="p-4 border-b border-gray-100 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getEventColor(event.type)}`}>
                            {event.type}
                          </span>
                          {event.stage && (
                            <span className="text-sm text-gray-600">
                              {event.stage}
                            </span>
                          )}
                          {event.agent && (
                            <span className="text-sm text-gray-500">
                              by {event.agent}
                            </span>
                          )}
                        </div>
                        
                        <div className="text-sm text-gray-600 mb-2">
                          {event.timestamp && (
                            <span>
                              {formatTimestamp(event.timestamp)}
                            </span>
                          )}
                          {event.request_id && (
                            <span className="ml-4 text-gray-400">
                              ID: {event.request_id}
                            </span>
                          )}
                        </div>

                        {event.result && (
                          <div className="mt-2 p-2 bg-gray-50 rounded text-sm">
                            <strong>Result:</strong>
                            <pre className="mt-1 text-xs text-gray-600 whitespace-pre-wrap">
                              {JSON.stringify(event.result, null, 2)}
                            </pre>
                          </div>
                        )}

                        {event.error && (
                          <div className="mt-2 p-2 bg-red-50 rounded text-sm">
                            <strong className="text-red-800">Error:</strong>
                            <p className="mt-1 text-red-700">{event.error}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="mt-6 text-center text-sm text-gray-500">
          <p>Dashboard updates every 3 seconds</p>
        </div>
      </div>
    </div>
  )
} 