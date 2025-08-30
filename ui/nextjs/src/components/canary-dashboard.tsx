'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Settings,
  Activity,
  Users,
  Clock
} from 'lucide-react';

interface CanaryStatus {
  isActive: boolean;
  currentTrafficPercentage: number;
  healthStatus: 'healthy' | 'degraded' | 'critical';
  lastHealthCheck: Date;
  metrics: {
    errorRate: number;
    responseTime: number;
    uptime: number;
    userSatisfaction: number;
    timestamp: Date;
  };
  rollbackTriggered: boolean;
}

interface CanaryConfig {
  enabled: boolean;
  trafficPercentage: number;
  rollbackThreshold: number;
  healthCheckEndpoint: string;
  metricsEndpoint: string;
}

export function CanaryDashboard() {
  const [status, setStatus] = useState<CanaryStatus | null>(null);
  const [config, setConfig] = useState<CanaryConfig | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch canary status and config
  const fetchCanaryData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/canary');
      if (!response.ok) {
        throw new Error('Failed to fetch canary data');
      }
      
      const data = await response.json();
      setStatus(data.data.status);
      setConfig(data.data.config);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  // Control canary deployment
  const controlCanary = async (action: string, trafficPercentage?: number) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/canary', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action, trafficPercentage }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to control canary deployment');
      }
      
      // Refresh data after action
      await fetchCanaryData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  // Update configuration
  const updateConfig = async (newConfig: Partial<CanaryConfig>) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/canary', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          action: 'update-config', 
          ...newConfig 
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to update configuration');
      }
      
      // Refresh data after update
      await fetchCanaryData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh data every 30 seconds
  useEffect(() => {
    fetchCanaryData();
    
    const interval = setInterval(fetchCanaryData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !status) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardContent className="p-6">
          <div className="flex items-center space-x-2 text-red-600">
            <XCircle className="h-5 w-5" />
            <span className="font-medium">Error: {error}</span>
          </div>
          <Button 
            onClick={fetchCanaryData} 
            variant="outline" 
            className="mt-4"
          >
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!status || !config) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center text-gray-500">
            No canary data available
          </div>
        </CardContent>
      </Card>
    );
  }

  const getHealthStatusColor = (health: string) => {
    switch (health) {
      case 'healthy': return 'bg-green-100 text-green-800 border-green-200';
      case 'degraded': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getHealthStatusIcon = (health: string) => {
    switch (health) {
      case 'healthy': return <CheckCircle className="h-4 w-4" />;
      case 'degraded': return <AlertTriangle className="h-4 w-4" />;
      case 'critical': return <XCircle className="h-4 w-4" />;
      default: return <Activity className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Canary Deployment Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Monitor and control traffic distribution between legacy and new systems
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge 
            variant={status.isActive ? 'default' : 'secondary'}
            className={status.isActive ? 'bg-green-100 text-green-800' : ''}
          >
            {status.isActive ? 'Active' : 'Inactive'}
          </Badge>
          <Badge className={getHealthStatusColor(status.healthStatus)}>
            {getHealthStatusIcon(status.healthStatus)}
            <span className="ml-1 capitalize">{status.healthStatus}</span>
          </Badge>
        </div>
      </div>

      {/* Control Panel */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Settings className="h-5 w-5" />
            <span>Deployment Controls</span>
          </CardTitle>
          <CardDescription>
            Start, stop, and control canary deployment traffic
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-4">
            {!status.isActive ? (
              <Button 
                onClick={() => controlCanary('start', 10)}
                disabled={loading}
                className="bg-green-600 hover:bg-green-700"
              >
                <Play className="h-4 w-4 mr-2" />
                Start Canary (10%)
              </Button>
            ) : (
              <>
                <Button 
                  onClick={() => controlCanary('increase', 10)}
                  disabled={loading || status.currentTrafficPercentage >= 100}
                  variant="outline"
                >
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Increase Traffic (+10%)
                </Button>
                <Button 
                  onClick={() => controlCanary('rollback')}
                  disabled={loading}
                  variant="destructive"
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Emergency Rollback
                </Button>
              </>
            )}
          </div>
          
          {status.isActive && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Current Traffic: {status.currentTrafficPercentage}%</span>
                <span>Legacy Traffic: {100 - status.currentTrafficPercentage}%</span>
              </div>
              <Progress value={status.currentTrafficPercentage} className="h-2" />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Users className="h-4 w-4 text-blue-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Traffic</p>
                <p className="text-2xl font-bold">{status.currentTrafficPercentage}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <div className="p-2 bg-red-100 rounded-lg">
                <XCircle className="h-4 w-4 text-red-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Error Rate</p>
                <p className="text-2xl font-bold">{(status.metrics.errorRate * 100).toFixed(2)}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <div className="p-2 bg-green-100 rounded-lg">
                <Activity className="h-4 w-4 text-green-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Response Time</p>
                <p className="text-2xl font-bold">{status.metrics.responseTime}ms</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <div className="p-2 bg-purple-100 rounded-lg">
                <CheckCircle className="h-4 w-4 text-purple-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Uptime</p>
                <p className="text-2xl font-bold">{(status.metrics.uptime * 100).toFixed(1)}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Configuration</CardTitle>
          <CardDescription>
            Canary deployment settings and thresholds
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="rollback-threshold" className="block text-sm font-medium text-gray-700 mb-2">
                Rollback Threshold (Error Rate)
              </label>
              <div className="flex items-center space-x-2">
                <input
                  id="rollback-threshold"
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  value={config.rollbackThreshold}
                  onChange={(e) => updateConfig({ rollbackThreshold: parseFloat(e.target.value) })}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  aria-describedby="rollback-threshold-help"
                />
                <span id="rollback-threshold-help" className="text-sm text-gray-500">(0.05 = 5%)</span>
              </div>
            </div>
            
            <div>
              <label htmlFor="health-check-endpoint" className="block text-sm font-medium text-gray-700 mb-2">
                Health Check Endpoint
              </label>
              <input
                id="health-check-endpoint"
                type="text"
                value={config.healthCheckEndpoint}
                disabled
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500"
                aria-describedby="health-check-endpoint-help"
              />
              <span id="health-check-endpoint-help" className="sr-only">Health check endpoint for canary deployment monitoring</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Status Details */}
      <Card>
        <CardHeader>
          <CardTitle>Status Details</CardTitle>
          <CardDescription>
            Detailed information about the current deployment
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Deployment Status</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Active:</span>
                  <span className={status.isActive ? 'text-green-600' : 'text-red-600'}>
                    {status.isActive ? 'Yes' : 'No'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Rollback Triggered:</span>
                  <span className={status.rollbackTriggered ? 'text-red-600' : 'text-green-600'}>
                    {status.rollbackTriggered ? 'Yes' : 'No'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Last Health Check:</span>
                  <span className="text-gray-900">
                    {new Date(status.lastHealthCheck).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Performance Metrics</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">User Satisfaction:</span>
                  <span className="text-gray-900">
                    {(status.metrics.userSatisfaction * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Memory Usage:</span>
                  <span className="text-gray-900">
                    {(process.memoryUsage?.()?.heapUsed / 1024 / 1024).toFixed(1)} MB
                  </span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
