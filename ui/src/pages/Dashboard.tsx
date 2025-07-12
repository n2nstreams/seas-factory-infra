import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import CodeGenerationTracker from '../components/CodeGenerationTracker'
import PullRequestsPanel from '../components/PullRequestsPanel'
import { Activity, Code2, GitBranch, Clock, CheckCircle, XCircle, RefreshCw, BarChart3 } from 'lucide-react'

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
  total_count: number
  last_updated: string
}

interface DashboardStats {
  active_generations: number
  completed_generations: number
  failed_generations: number
  open_prs: number
  merged_prs: number
  total_events: number
  last_activity: string
}

export default function Dashboard() {
  const [events, setEvents] = useState<AgentEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [stats, setStats] = useState<DashboardStats>({
    active_generations: 0,
    completed_generations: 0,
    failed_generations: 0,
    open_prs: 0,
    merged_prs: 0,
    total_events: 0,
    last_activity: new Date().toISOString()
  })
  const [activeTab, setActiveTab] = useState('overview')

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

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/dev/dashboard/stats')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data: DashboardStats = await response.json()
      setStats(data)
    } catch (err) {
      console.error('Error fetching dashboard stats:', err)
    }
  }

  useEffect(() => {
    // Initial fetch
    fetchEvents()
    fetchStats()

    // Set up polling every 5 seconds
    const interval = setInterval(() => {
      fetchEvents()
      fetchStats()
    }, 5000)

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
        return 'text-blue-600 bg-blue-50/50'
      case 'FINISH':
        return 'text-green-600 bg-green-50/50'
      case 'ERROR':
        return 'text-red-600 bg-red-50/50'
      default:
        return 'text-gray-600 bg-gray-50/50'
    }
  }

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'START':
        return <Clock className="w-4 h-4" />
      case 'FINISH':
        return <CheckCircle className="w-4 h-4" />
      case 'ERROR':
        return <XCircle className="w-4 h-4" />
      default:
        return <Activity className="w-4 h-4" />
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-green-700 font-medium">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-green-900 mb-2">
                🚀 SaaS Factory Dashboard
              </h1>
              <p className="text-green-700 text-lg">
                Monitor code generation, pull requests, and agent activities
              </p>
              {lastUpdate && (
                <p className="text-sm text-green-600 mt-2">
                  Last updated: {lastUpdate.toLocaleString()}
                </p>
              )}
            </div>
            <Badge variant="outline" className="text-sm bg-white/80 backdrop-blur-sm border-green-200">
              Live Dashboard
            </Badge>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-white/60 backdrop-blur-sm border-green-200/50">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-600">Active Generations</p>
                  <p className="text-3xl font-bold text-green-900">{stats.active_generations}</p>
                </div>
                <div className="p-3 bg-blue-500/10 rounded-full">
                  <Code2 className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/60 backdrop-blur-sm border-green-200/50">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-600">Completed</p>
                  <p className="text-3xl font-bold text-green-900">{stats.completed_generations}</p>
                </div>
                <div className="p-3 bg-green-500/10 rounded-full">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/60 backdrop-blur-sm border-green-200/50">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-600">Open PRs</p>
                  <p className="text-3xl font-bold text-green-900">{stats.open_prs}</p>
                </div>
                <div className="p-3 bg-purple-500/10 rounded-full">
                  <GitBranch className="w-6 h-6 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/60 backdrop-blur-sm border-green-200/50">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-600">Total Events</p>
                  <p className="text-3xl font-bold text-green-900">{stats.total_events}</p>
                </div>
                <div className="p-3 bg-gray-500/10 rounded-full">
                  <BarChart3 className="w-6 h-6 text-gray-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 bg-red-50/80 backdrop-blur-sm border border-red-200/50 rounded-lg">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <XCircle className="h-5 w-5 text-red-400" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
              <div className="ml-auto">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setError(null)
                    fetchEvents()
                    fetchStats()
                  }}
                  className="bg-white/40 backdrop-blur-sm border-red-200/50 hover:bg-white/60"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Retry
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Main Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 mb-6 bg-white/60 backdrop-blur-sm border-green-200/50">
            <TabsTrigger 
              value="overview" 
              className="data-[state=active]:bg-green-500/20 data-[state=active]:text-green-800"
            >
              Overview
            </TabsTrigger>
            <TabsTrigger 
              value="codegen" 
              className="data-[state=active]:bg-green-500/20 data-[state=active]:text-green-800"
            >
              Code Generation
            </TabsTrigger>
            <TabsTrigger 
              value="pulls" 
              className="data-[state=active]:bg-green-500/20 data-[state=active]:text-green-800"
            >
              Pull Requests
            </TabsTrigger>
            <TabsTrigger 
              value="events" 
              className="data-[state=active]:bg-green-500/20 data-[state=active]:text-green-800"
            >
              Events
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <CodeGenerationTracker maxTasks={3} />
              <PullRequestsPanel maxPRs={5} />
            </div>

            {/* Recent Activity Summary */}
            <Card className="bg-white/60 backdrop-blur-sm border-green-200/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-green-800">
                  <Activity className="w-5 h-5" />
                  Recent Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                {events.length === 0 ? (
                  <div className="text-center py-8">
                    <Activity className="w-12 h-12 text-green-400 mx-auto mb-4 opacity-50" />
                    <p className="text-green-700 font-medium">No recent activity</p>
                    <p className="text-green-600 text-sm mt-1">
                      Agent events will appear here as they occur
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {events.slice(0, 5).map((event, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-white/40 backdrop-blur-sm rounded-lg border border-green-200/50"
                      >
                        <div className="flex items-center gap-3">
                          <div className={`p-2 rounded-full ${getEventColor(event.type)}`}>
                            {getEventIcon(event.type)}
                          </div>
                          <div>
                            <p className="font-medium text-green-900">{event.type}</p>
                            {event.stage && (
                              <p className="text-sm text-green-600">{event.stage}</p>
                            )}
                            {event.agent && (
                              <p className="text-xs text-green-500">by {event.agent}</p>
                            )}
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-green-600">
                            {formatTimestamp(event.timestamp)}
                          </p>
                          {event.request_id && (
                            <p className="text-xs text-green-500">
                              {event.request_id}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Code Generation Tab */}
          <TabsContent value="codegen" className="space-y-6">
            <CodeGenerationTracker maxTasks={10} />
          </TabsContent>

          {/* Pull Requests Tab */}
          <TabsContent value="pulls" className="space-y-6">
            <PullRequestsPanel maxPRs={20} />
          </TabsContent>

          {/* Events Tab */}
          <TabsContent value="events" className="space-y-6">
            <Card className="bg-white/60 backdrop-blur-sm border-green-200/50">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2 text-green-800">
                    <Activity className="w-5 h-5" />
                    Agent Events ({events.length})
                  </CardTitle>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      fetchEvents()
                      fetchStats()
                    }}
                    className="bg-white/40 backdrop-blur-sm border-green-200/50 hover:bg-white/60"
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Refresh
                  </Button>
                </div>
              </CardHeader>

              <CardContent>
                {events.length === 0 ? (
                  <div className="text-center py-12">
                    <Activity className="w-12 h-12 text-green-400 mx-auto mb-4 opacity-50" />
                    <p className="text-green-700 font-medium">No events yet</p>
                    <p className="text-green-600 text-sm mt-1">
                      Events will appear here as agents perform tasks
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {events.map((event, index) => (
                      <div
                        key={index}
                        className="p-4 bg-white/40 backdrop-blur-sm rounded-lg border border-green-200/50"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-2">
                              <span className={`inline-flex items-center gap-1.5 px-2 py-1 text-xs font-medium rounded-full ${getEventColor(event.type)}`}>
                                {getEventIcon(event.type)}
                                {event.type}
                              </span>
                              {event.stage && (
                                <span className="text-sm text-green-600">
                                  {event.stage}
                                </span>
                              )}
                              {event.agent && (
                                <span className="text-sm text-green-500">
                                  by {event.agent}
                                </span>
                              )}
                            </div>
                            
                            <div className="text-sm text-green-600 mb-2">
                              {event.timestamp && (
                                <span>
                                  {formatTimestamp(event.timestamp)}
                                </span>
                              )}
                              {event.request_id && (
                                <span className="ml-4 text-green-400">
                                  ID: {event.request_id}
                                </span>
                              )}
                            </div>

                            {event.result && (
                              <div className="text-sm">
                                <pre className="text-green-700 bg-green-50/50 p-2 rounded overflow-x-auto">
                                  {JSON.stringify(event.result, null, 2)}
                                </pre>
                              </div>
                            )}

                            {event.error && (
                              <div className="text-sm text-red-700 bg-red-50/50 p-2 rounded">
                                <span className="font-medium">Error:</span> {event.error}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
} 