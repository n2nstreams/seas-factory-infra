import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { EventFilterPanel } from '../components/EventFilterPanel';
import { LiveMetricsChart } from '../components/LiveMetricsChart';

interface EventMessage {
  event_type: string;
  data: any;
  timestamp: string;
  source: string;
  priority: string;
}

interface EventFilter {
  event_types?: string[];
  sources?: string[];
  priority?: string[];
  search?: string;
  time_range?: string;
}

interface Metrics {
  active_connections: number;
  total_connections: number;
  events_sent: number;
  last_activity: string;
}

interface AgentStatus {
  name: string;
  status: string;
  last_seen: string;
}

const EventDashboard: React.FC = () => {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [events, setEvents] = useState<EventMessage[]>([]);
  const [filteredEvents, setFilteredEvents] = useState<EventMessage[]>([]);
  const [filters, setFilters] = useState<EventFilter>({});
  const [metrics, setMetrics] = useState<Metrics>({
    active_connections: 0,
    total_connections: 0,
    events_sent: 0,
    last_activity: new Date().toISOString()
  });
  const [agents, setAgents] = useState<AgentStatus[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [connectionId, setConnectionId] = useState<string>('');

  // WebSocket connection management
  const connectWebSocket = useCallback(() => {
    const clientId = `dashboard-${Math.random().toString(36).substr(2, 9)}`;
    setConnectionId(clientId);
    
    const wsUrl = `ws://localhost:8000/ws/${clientId}`;
    const websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      setWs(websocket);
    };

    websocket.onmessage = (event) => {
      const message: EventMessage = JSON.parse(event.data);
      setEvents(prev => [message, ...prev.slice(0, 99)]); // Keep last 100 events
    };

    websocket.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      setWs(null);
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    return websocket;
  }, []);

  const disconnectWebSocket = useCallback(() => {
    if (ws) {
      ws.close();
      setWs(null);
      setIsConnected(false);
    }
  }, [ws]);

  // Auto-connect on mount
  useEffect(() => {
    const websocket = connectWebSocket();
    
    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, [connectWebSocket]);

  // Filter events based on current filters
  useEffect(() => {
    let filtered = events;

    if (filters.event_types && filters.event_types.length > 0) {
      filtered = filtered.filter(event => 
        filters.event_types!.includes(event.event_type)
      );
    }

    if (filters.sources && filters.sources.length > 0) {
      filtered = filtered.filter(event => 
        filters.sources!.includes(event.source)
      );
    }

    if (filters.priority && filters.priority.length > 0) {
      filtered = filtered.filter(event => 
        filters.priority!.includes(event.priority)
      );
    }

    if (filters.search) {
      const search = filters.search.toLowerCase();
      filtered = filtered.filter(event => 
        event.event_type.toLowerCase().includes(search) ||
        event.source.toLowerCase().includes(search) ||
        JSON.stringify(event.data).toLowerCase().includes(search)
      );
    }

    setFilteredEvents(filtered);
  }, [events, filters]);

  // Fetch metrics periodically
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch('/api/metrics');
        const data = await response.json();
        setMetrics(data);
      } catch (error) {
        console.error('Error fetching metrics:', error);
      }
    };

    const fetchAgents = async () => {
      try {
        const response = await fetch('/api/agents/status');
        const data = await response.json();
        setAgents(data.agents);
      } catch (error) {
        console.error('Error fetching agents:', error);
      }
    };

    fetchMetrics();
    fetchAgents();
    
    const interval = setInterval(() => {
      fetchMetrics();
      fetchAgents();
    }, 10000); // Every 10 seconds

    return () => clearInterval(interval);
  }, []);

  // Send test event
  const sendTestEvent = async () => {
    try {
      const response = await fetch('/api/test/publish-event', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          event_type: 'test',
          source: 'dashboard',
          priority: 'normal',
          data: {
            message: 'Test event from dashboard',
            timestamp: new Date().toISOString(),
            user: 'dashboard-user'
          }
        })
      });
      
      if (response.ok) {
        console.log('Test event sent successfully');
      }
    } catch (error) {
      console.error('Error sending test event:', error);
    }
  };

  // Clear all events
  const clearEvents = () => {
    setEvents([]);
    setFilteredEvents([]);
  };

  // Get priority color
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-500/10 text-red-700 border-red-500/20';
      case 'normal': return 'bg-blue-500/10 text-blue-700 border-blue-500/20';
      case 'low': return 'bg-green-500/10 text-green-700 border-green-500/20';
      default: return 'bg-gray-500/10 text-gray-700 border-gray-500/20';
    }
  };

  // Get agent status color
  const getAgentStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/10 text-green-700 border-green-500/20';
      case 'inactive': return 'bg-red-500/10 text-red-700 border-red-500/20';
      case 'warning': return 'bg-yellow-500/10 text-yellow-700 border-yellow-500/20';
      default: return 'bg-gray-500/10 text-gray-700 border-gray-500/20';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-800">Event Dashboard</h1>
              <p className="text-slate-600 mt-1">
                Real-time monitoring of SaaS Factory events
              </p>
            </div>
            
            {/* Connection Status */}
            <div className="flex items-center space-x-4">
              <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg backdrop-blur-sm border ${
                isConnected 
                  ? 'bg-green-500/10 text-green-700 border-green-500/20' 
                  : 'bg-red-500/10 text-red-700 border-red-500/20'
              }`}>
                <div className={`w-2 h-2 rounded-full ${
                  isConnected ? 'bg-green-500' : 'bg-red-500'
                }`} />
                <span className="text-sm font-medium">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              
              <div className="text-xs text-slate-500">
                ID: {connectionId}
              </div>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="mb-6">
          <div className="flex flex-wrap gap-2">
            <Button
              onClick={isConnected ? disconnectWebSocket : connectWebSocket}
              variant={isConnected ? "outline" : "default"}
              className="backdrop-blur-sm bg-white/60 hover:bg-white/80 border-slate-200/50"
            >
              {isConnected ? 'Disconnect' : 'Connect'}
            </Button>
            
            <Button
              onClick={sendTestEvent}
              disabled={!isConnected}
              className="backdrop-blur-sm bg-emerald-500/80 hover:bg-emerald-600/80 text-white"
            >
              Send Test Event
            </Button>
            
            <Button
              onClick={clearEvents}
              variant="outline"
              className="backdrop-blur-sm bg-white/60 hover:bg-white/80 border-slate-200/50"
            >
              Clear Events
            </Button>
            
            <Button
              onClick={() => setShowFilters(!showFilters)}
              variant="outline"
              className="backdrop-blur-sm bg-white/60 hover:bg-white/80 border-slate-200/50"
            >
              {showFilters ? 'Hide Filters' : 'Show Filters'}
              {Object.keys(filters).length > 0 && (
                <Badge className="ml-2 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs">
                  {Object.keys(filters).length}
                </Badge>
              )}
            </Button>
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="mb-6">
            <EventFilterPanel
              filters={filters}
              onFiltersChange={setFilters}
              className="backdrop-blur-sm bg-white/60 border-slate-200/50"
            />
          </div>
        )}

        {/* Main Content */}
        <Tabs defaultValue="events" className="w-full">
          <TabsList className="grid w-full grid-cols-4 backdrop-blur-sm bg-white/60 border-slate-200/50">
            <TabsTrigger value="events" className="data-[state=active]:bg-emerald-500/20 data-[state=active]:text-emerald-700">
              Live Events
              <Badge className="ml-2 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs">
                {filteredEvents.length}
              </Badge>
            </TabsTrigger>
            <TabsTrigger value="charts" className="data-[state=active]:bg-emerald-500/20 data-[state=active]:text-emerald-700">
              Live Charts
            </TabsTrigger>
            <TabsTrigger value="flows" className="data-[state=active]:bg-emerald-500/20 data-[state=active]:text-emerald-700">
              Event Flows
            </TabsTrigger>
            <TabsTrigger value="agents" className="data-[state=active]:bg-emerald-500/20 data-[state=active]:text-emerald-700">
              Agent Status
            </TabsTrigger>
          </TabsList>

          {/* Live Events Tab */}
          <TabsContent value="events" className="mt-6">
            <Card className="backdrop-blur-sm bg-white/60 border-slate-200/50">
              <CardHeader>
                <CardTitle className="text-slate-800">Live Events</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 max-h-[600px] overflow-y-auto">
                  {filteredEvents.length === 0 ? (
                    <div className="text-center py-8 text-slate-500">
                      No events to display
                    </div>
                  ) : (
                    filteredEvents.map((event, index) => (
                      <div
                        key={index}
                        className="p-4 rounded-lg border backdrop-blur-sm bg-white/40 border-slate-200/50"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              <Badge className="bg-slate-500/10 text-slate-700 border-slate-500/20">
                                {event.event_type}
                              </Badge>
                              <Badge className={getPriorityColor(event.priority)}>
                                {event.priority}
                              </Badge>
                              <span className="text-sm text-slate-500">
                                from {event.source}
                              </span>
                            </div>
                            <pre className="text-sm text-slate-700 bg-slate-50/50 p-2 rounded overflow-x-auto">
                              {JSON.stringify(event.data, null, 2)}
                            </pre>
                          </div>
                          <div className="text-xs text-slate-500 ml-4">
                            {new Date(event.timestamp).toLocaleTimeString()}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Live Charts Tab */}
          <TabsContent value="charts" className="mt-6">
            <LiveMetricsChart 
              metrics={metrics} 
              events={events}
              className="backdrop-blur-sm bg-white/60 border-slate-200/50"
            />
          </TabsContent>

          {/* Event Flows Tab */}
          <TabsContent value="flows" className="mt-6">
            <Card className="backdrop-blur-sm bg-white/60 border-slate-200/50">
              <CardHeader>
                <CardTitle className="text-slate-800">Event Flows</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 rounded-lg border backdrop-blur-sm bg-white/40 border-slate-200/50">
                    <h3 className="font-semibold text-slate-700 mb-2">Agent Communication</h3>
                    <p className="text-sm text-slate-600 mb-3">
                      Communication between agents and orchestrator
                    </p>
                    <div className="flex flex-wrap gap-2">
                      <Badge className="bg-blue-500/10 text-blue-700 border-blue-500/20">agent_request</Badge>
                      <Badge className="bg-green-500/10 text-green-700 border-green-500/20">agent_response</Badge>
                      <Badge className="bg-red-500/10 text-red-700 border-red-500/20">agent_error</Badge>
                    </div>
                  </div>

                  <div className="p-4 rounded-lg border backdrop-blur-sm bg-white/40 border-slate-200/50">
                    <h3 className="font-semibold text-slate-700 mb-2">System Events</h3>
                    <p className="text-sm text-slate-600 mb-3">
                      System health and monitoring events
                    </p>
                    <div className="flex flex-wrap gap-2">
                      <Badge className="bg-emerald-500/10 text-emerald-700 border-emerald-500/20">system_health</Badge>
                      <Badge className="bg-purple-500/10 text-purple-700 border-purple-500/20">metrics</Badge>
                      <Badge className="bg-yellow-500/10 text-yellow-700 border-yellow-500/20">alerts</Badge>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Agent Status Tab */}
          <TabsContent value="agents" className="mt-6">
            <Card className="backdrop-blur-sm bg-white/60 border-slate-200/50">
              <CardHeader>
                <CardTitle className="text-slate-800">Agent Status</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {agents.map((agent, index) => (
                    <div
                      key={index}
                      className="p-4 rounded-lg border backdrop-blur-sm bg-white/40 border-slate-200/50"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-semibold text-slate-700">{agent.name}</h3>
                        <Badge className={getAgentStatusColor(agent.status)}>
                          {agent.status}
                        </Badge>
                      </div>
                      <p className="text-sm text-slate-600">
                        Last seen: {new Date(agent.last_seen).toLocaleString()}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default EventDashboard; 