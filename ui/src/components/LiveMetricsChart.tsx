import React, { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';

interface Metrics {
  active_connections: number;
  total_connections: number;
  events_sent: number;
  last_activity: string;
}

interface EventMessage {
  event_type: string;
  data: any;
  timestamp: string;
  source: string;
  priority: string;
}

interface LiveMetricsChartProps {
  metrics: Metrics;
  events: EventMessage[];
  className?: string;
}

interface ChartDataPoint {
  timestamp: Date;
  count: number;
}

const LiveMetricsChart: React.FC<LiveMetricsChartProps> = ({
  metrics,
  events,
  className = ""
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [priorityStats, setPriorityStats] = useState<Record<string, number>>({});
  const [sourceStats, setSourceStats] = useState<Record<string, number>>({});
  const [eventTypeStats, setEventTypeStats] = useState<Record<string, number>>({});

  // Update chart data every minute
  useEffect(() => {
    const updateChartData = () => {
      const now = new Date();
      const oneMinuteAgo = new Date(now.getTime() - 60 * 1000);
      
      // Count events in the last minute
      const recentEvents = events.filter(event => 
        new Date(event.timestamp) > oneMinuteAgo
      );
      
      const newDataPoint: ChartDataPoint = {
        timestamp: now,
        count: recentEvents.length
      };
      
      setChartData(prev => {
        const newData = [...prev, newDataPoint];
        // Keep only last 30 minutes of data
        const thirtyMinutesAgo = new Date(now.getTime() - 30 * 60 * 1000);
        return newData.filter(point => point.timestamp > thirtyMinutesAgo);
      });
    };

    updateChartData();
    const interval = setInterval(updateChartData, 60000); // Update every minute
    
    return () => clearInterval(interval);
  }, [events]);

  // Update statistics
  useEffect(() => {
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
    
    // Get events from the last hour
    const recentEvents = events.filter(event => 
      new Date(event.timestamp) > oneHourAgo
    );

    // Calculate priority distribution
    const priorityCount: Record<string, number> = {};
    const sourceCount: Record<string, number> = {};
    const eventTypeCount: Record<string, number> = {};

    recentEvents.forEach(event => {
      priorityCount[event.priority] = (priorityCount[event.priority] || 0) + 1;
      sourceCount[event.source] = (sourceCount[event.source] || 0) + 1;
      eventTypeCount[event.event_type] = (eventTypeCount[event.event_type] || 0) + 1;
    });

    setPriorityStats(priorityCount);
    setSourceStats(sourceCount);
    setEventTypeStats(eventTypeCount);
  }, [events]);

  // Draw chart
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || chartData.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    const { width, height } = canvas;
    const padding = 40;
    const chartWidth = width - 2 * padding;
    const chartHeight = height - 2 * padding;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw background
    ctx.fillStyle = 'rgba(248, 250, 252, 0.8)';
    ctx.fillRect(0, 0, width, height);

    // Draw grid
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.3)';
    ctx.lineWidth = 1;

    // Vertical grid lines
    for (let i = 0; i <= 10; i++) {
      const x = padding + (i * chartWidth) / 10;
      ctx.beginPath();
      ctx.moveTo(x, padding);
      ctx.lineTo(x, height - padding);
      ctx.stroke();
    }

    // Horizontal grid lines
    for (let i = 0; i <= 5; i++) {
      const y = padding + (i * chartHeight) / 5;
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(width - padding, y);
      ctx.stroke();
    }

    if (chartData.length > 1) {
      // Find max value for scaling
      const maxValue = Math.max(...chartData.map(d => d.count), 10);

      // Draw line chart
      ctx.strokeStyle = 'rgba(16, 185, 129, 0.8)';
      ctx.lineWidth = 2;
      ctx.beginPath();

      chartData.forEach((point, index) => {
        const x = padding + (index * chartWidth) / (chartData.length - 1);
        const y = height - padding - (point.count * chartHeight) / maxValue;
        
        if (index === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });

      ctx.stroke();

      // Draw points
      ctx.fillStyle = 'rgba(16, 185, 129, 1)';
      chartData.forEach((point, index) => {
        const x = padding + (index * chartWidth) / (chartData.length - 1);
        const y = height - padding - (point.count * chartHeight) / maxValue;
        
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, 2 * Math.PI);
        ctx.fill();
      });

      // Draw labels
      ctx.fillStyle = 'rgba(71, 85, 105, 0.8)';
      ctx.font = '12px sans-serif';
      ctx.textAlign = 'center';
      
      // Y-axis labels
      ctx.textAlign = 'right';
      for (let i = 0; i <= 5; i++) {
        const value = (maxValue * (5 - i)) / 5;
        const y = padding + (i * chartHeight) / 5;
        ctx.fillText(value.toFixed(0), padding - 10, y + 4);
      }
      
      // X-axis labels (time)
      ctx.textAlign = 'center';
      if (chartData.length > 0) {
        const firstPoint = chartData[0];
        const lastPoint = chartData[chartData.length - 1];
        
        ctx.fillText(
          firstPoint.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          padding,
          height - padding + 20
        );
        
        ctx.fillText(
          lastPoint.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          width - padding,
          height - padding + 20
        );
      }
    }

    // Draw title
    ctx.fillStyle = 'rgba(30, 41, 59, 0.9)';
    ctx.font = 'bold 14px sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('Events per Minute', padding, padding - 10);

  }, [chartData]);

  const getTopItems = (stats: Record<string, number>, limit: number = 5) => {
    return Object.entries(stats)
      .sort(([, a], [, b]) => b - a)
      .slice(0, limit);
  };

  return (
    <div className={`grid grid-cols-1 lg:grid-cols-2 gap-6 ${className}`}>
      {/* Events Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="text-slate-800">Events per Minute</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 w-full">
            <canvas
              ref={canvasRef}
              className="w-full h-full"
              style={{ width: '100%', height: '100%' }}
            />
          </div>
        </CardContent>
      </Card>

      {/* Priority Distribution */}
      <Card>
        <CardHeader>
          <CardTitle className="text-slate-800">Priority Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(priorityStats).length === 0 ? (
              <div className="text-center py-8 text-slate-500">
                No recent events
              </div>
            ) : (
              getTopItems(priorityStats).map(([priority, count]) => {
                const total = Object.values(priorityStats).reduce((sum, val) => sum + val, 0);
                const percentage = total > 0 ? (count / total) * 100 : 0;
                
                const colorClass = priority === 'high' ? 'bg-red-500' :
                                 priority === 'normal' ? 'bg-blue-500' : 'bg-green-500';
                
                return (
                  <div key={priority} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className={`w-3 h-3 rounded-full ${colorClass}`} />
                      <span className="text-sm font-medium text-slate-700 capitalize">
                        {priority}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className="bg-slate-100 text-slate-700">
                        {count}
                      </Badge>
                      <span className="text-sm text-slate-500">
                        {percentage.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </CardContent>
      </Card>

      {/* Agent Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="text-slate-800">Agent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(sourceStats).length === 0 ? (
              <div className="text-center py-8 text-slate-500">
                No recent activity
              </div>
            ) : (
              getTopItems(sourceStats).map(([source, count]) => {
                const total = Object.values(sourceStats).reduce((sum, val) => sum + val, 0);
                const percentage = total > 0 ? (count / total) * 100 : 0;
                
                return (
                  <div key={source} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-700">
                        {source}
                      </span>
                      <div className="flex items-center space-x-2">
                        <Badge className="bg-slate-100 text-slate-700">
                          {count}
                        </Badge>
                        <span className="text-sm text-slate-500">
                          {percentage.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-2">
                      <div
                        className="bg-emerald-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </CardContent>
      </Card>

      {/* Event Types */}
      <Card>
        <CardHeader>
          <CardTitle className="text-slate-800">Event Types</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {Object.entries(eventTypeStats).length === 0 ? (
              <div className="text-center py-8 text-slate-500">
                No recent events
              </div>
            ) : (
              getTopItems(eventTypeStats).map(([eventType, count]) => {
                const total = Object.values(eventTypeStats).reduce((sum, val) => sum + val, 0);
                const percentage = total > 0 ? (count / total) * 100 : 0;
                
                return (
                  <div key={eventType} className="flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-700">
                      {eventType}
                    </span>
                    <div className="flex items-center space-x-2">
                      <Badge className="bg-slate-100 text-slate-700">
                        {count}
                      </Badge>
                      <span className="text-sm text-slate-500">
                        {percentage.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export { LiveMetricsChart }; 