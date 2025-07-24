import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Button } from './ui/button';
import { 
  Activity, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Pause,
  Wifi,
  WifiOff,
  Sparkles,
  Palette,
  Code2,
  TestTube,
  Rocket,
  Globe,
  RefreshCw,
  Eye
} from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';

interface FactoryPipeline {
  pipeline_id: string;
  project_id: string;
  project_name: string;
  current_stage: string;
  progress: number;
  status: 'queued' | 'running' | 'completed' | 'failed' | 'paused';
  stages: { [key: string]: string };
  started_at: string;
  updated_at: string;
  completed_at?: string;
  error_message?: string;
  metadata: { [key: string]: any };
}

interface FactoryStage {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  estimatedDuration: string;
}

interface FactoryProgressMonitorProps {
  className?: string;
  tenantId?: string;
  userId?: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

const FactoryProgressMonitor: React.FC<FactoryProgressMonitorProps> = ({
  className = '',
  tenantId = 'default',
  userId = 'default-user',
  autoRefresh = true,
  refreshInterval = 5000
}) => {
  const [pipelines, setPipelines] = useState<FactoryPipeline[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPipeline, setSelectedPipeline] = useState<string | null>(null);

  // Factory stages configuration
  const factoryStages: FactoryStage[] = [
    {
      id: 'idea_validation',
      name: 'Idea Validation',
      description: 'Validating concept and market research',
      icon: <Sparkles className="w-5 h-5" />,
      estimatedDuration: '5-10 min'
    },
    {
      id: 'tech_stack',
      name: 'Tech Stack',
      description: 'Selecting optimal technology stack',
      icon: <Code2 className="w-5 h-5" />,
      estimatedDuration: '3-5 min'
    },
    {
      id: 'design',
      name: 'UI/UX Design',
      description: 'Creating wireframes and design system',
      icon: <Palette className="w-5 h-5" />,
      estimatedDuration: '10-15 min'
    },
    {
      id: 'development',
      name: 'Development',
      description: 'Generating code and components',
      icon: <Code2 className="w-5 h-5" />,
      estimatedDuration: '15-30 min'
    },
    {
      id: 'qa',
      name: 'Quality Assurance',
      description: 'Running tests and code quality checks',
      icon: <TestTube className="w-5 h-5" />,
      estimatedDuration: '5-10 min'
    },
    {
      id: 'deployment',
      name: 'Deployment',
      description: 'Deploying to production environment',
      icon: <Rocket className="w-5 h-5" />,
      estimatedDuration: '3-5 min'
    }
  ];

  // WebSocket connection for real-time updates
  const { isConnected } = useWebSocket({
    url: `ws://localhost:8000/ws/factory-monitor-${Math.random().toString(36).substr(2, 9)}`,
    onMessage: useCallback((message: { type: string; data: any }) => {
      if (message.type === 'factory_progress') {
        updatePipelineProgress(message.data);
      } else if (message.type === 'factory_triggered') {
        handleNewPipeline(message.data);
      }
    }, []),
    enabled: autoRefresh
  });

  // Fetch factory pipelines
  const fetchPipelines = useCallback(async () => {
    try {
      setError(null);
      const response = await fetch('/api/factory/pipelines?limit=10', {
        headers: {
          'x-tenant-id': tenantId,
          'x-user-id': userId
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch pipelines: ${response.statusText}`);
      }

      const data = await response.json();
      setPipelines(data);
    } catch (err) {
      console.error('Error fetching pipelines:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch pipelines');
    } finally {
      setLoading(false);
    }
  }, [tenantId, userId]);

  // Update pipeline progress from WebSocket
  const updatePipelineProgress = useCallback((data: any) => {
    setPipelines(prev => 
      prev.map(pipeline => 
        pipeline.pipeline_id === data.pipeline_id 
          ? {
              ...pipeline,
              current_stage: data.stage,
              progress: data.progress,
              status: data.status,
              stages: {
                ...pipeline.stages,
                [data.stage]: data.status
              },
              updated_at: data.timestamp
            }
          : pipeline
      )
    );
  }, []);

  // Handle new pipeline from WebSocket
  const handleNewPipeline = useCallback((_data: any) => {
    fetchPipelines(); // Refresh the entire list
  }, [fetchPipelines]);

  // Load pipelines on mount and set up refresh interval
  useEffect(() => {
    fetchPipelines();
    
    if (autoRefresh) {
      const interval = setInterval(fetchPipelines, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [fetchPipelines, autoRefresh, refreshInterval]);

  // Get status color for badges
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'running':
        return 'text-blue-600 bg-blue-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      case 'paused':
        return 'text-yellow-600 bg-yellow-100';
      case 'queued':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  // Get status icon
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'running':
        return <Activity className="w-4 h-4 text-blue-600 animate-pulse" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-600" />;
      case 'paused':
        return <Pause className="w-4 h-4 text-yellow-600" />;
      case 'queued':
        return <Clock className="w-4 h-4 text-gray-600" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-600" />;
    }
  };

  // Get stage status color
  const getStageStatusColor = (stageId: string, stages: { [key: string]: string }) => {
    const status = stages[stageId] || 'pending';
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'running':
        return 'bg-blue-500 animate-pulse';
      case 'failed':
        return 'bg-red-500';
      case 'pending':
      default:
        return 'bg-gray-300';
    }
  };

  // Format time ago
  const formatTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now.getTime() - time.getTime();
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMinutes / 60);
    
    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return time.toLocaleDateString();
  };

  // Calculate estimated completion time
  const getEstimatedCompletion = (pipeline: FactoryPipeline) => {
    if (pipeline.status === 'completed') return 'Completed';
    if (pipeline.status === 'failed') return 'Failed';
    if (pipeline.status === 'paused') return 'Paused';
    if (pipeline.status === 'queued') return 'Queued';
    
    // Rough estimation based on current progress
    const elapsed = new Date().getTime() - new Date(pipeline.started_at).getTime();
    const elapsedMinutes = elapsed / (1000 * 60);
    const progressRatio = pipeline.progress / 100;
    
    if (progressRatio > 0) {
      const estimatedTotal = elapsedMinutes / progressRatio;
      const remaining = Math.max(0, estimatedTotal - elapsedMinutes);
      return `~${Math.round(remaining)}m remaining`;
    }
    
    return '~45m remaining'; // Default estimate
  };

  if (loading) {
    return (
      <Card className={`card-glass ${className}`}>
        <CardHeader>
          <CardTitle className="text-heading flex items-center">
            <Activity className="w-5 h-5 mr-2" />
            Factory Progress Monitor
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="w-6 h-6 animate-spin text-accent mr-2" />
            <span className="text-body">Loading factory pipelines...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={`card-glass ${className}`}>
        <CardHeader>
          <CardTitle className="text-heading flex items-center">
            <Activity className="w-5 h-5 mr-2" />
            Factory Progress Monitor
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <XCircle className="w-6 h-6 text-red-500 mr-2" />
            <div className="text-center">
              <p className="text-red-600 font-medium">Error loading pipelines</p>
              <p className="text-red-500 text-sm">{error}</p>
              <Button 
                onClick={() => {
                  setError(null);
                  setLoading(true);
                  fetchPipelines();
                }}
                variant="outline" 
                className="btn-secondary mt-2"
              >
                <RefreshCw className="w-4 h-4 mr-1" />
                Retry
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`card-glass ${className}`}>
      <CardHeader>
        <CardTitle className="text-heading flex items-center justify-between">
          <span className="flex items-center">
            <Activity className="w-5 h-5 mr-2" />
            Factory Progress Monitor
          </span>
          <div className="flex items-center space-x-2">
            <div className={`flex items-center space-x-1 text-xs ${
              isConnected ? 'text-green-600' : 'text-red-600'
            }`}>
              {isConnected ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
              <span>{isConnected ? 'Live' : 'Offline'}</span>
            </div>
            <Button 
              onClick={fetchPipelines}
              variant="outline" 
              size="sm"
              className="btn-ghost"
            >
              <RefreshCw className="w-4 h-4" />
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {pipelines.length === 0 ? (
          <div className="text-center py-8">
            <Globe className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <h3 className="text-lg font-medium text-heading mb-2">No Active Pipelines</h3>
            <p className="text-body">Submit an idea to start your first factory pipeline</p>
          </div>
        ) : (
          pipelines.map((pipeline) => (
            <div key={pipeline.pipeline_id} className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(pipeline.status)}
                  <div>
                    <h3 className="font-semibold text-heading">{pipeline.project_name}</h3>
                    <p className="text-sm text-body">
                      {formatTimeAgo(pipeline.updated_at)} • {getEstimatedCompletion(pipeline)}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge className={`text-xs ${getStatusColor(pipeline.status)}`}>
                    {pipeline.status}
                  </Badge>
                  <Button 
                    size="sm" 
                    variant="ghost" 
                    className="btn-ghost"
                    onClick={() => setSelectedPipeline(
                      selectedPipeline === pipeline.pipeline_id ? null : pipeline.pipeline_id
                    )}
                  >
                    <Eye className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              {/* Progress bar */}
              <div className="space-y-2 mb-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-body">Overall Progress</span>
                  <span className="text-heading font-medium">{pipeline.progress.toFixed(1)}%</span>
                </div>
                <Progress value={pipeline.progress} className="h-2" />
              </div>

              {/* Stage indicators */}
              <div className="flex items-center space-x-2 mb-4">
                {factoryStages.map((stage, index) => (
                  <div key={stage.id} className="flex items-center">
                    <div 
                      className={`w-3 h-3 rounded-full ${getStageStatusColor(stage.id, pipeline.stages)}`}
                      title={`${stage.name}: ${pipeline.stages[stage.id] || 'pending'}`}
                    />
                    {index < factoryStages.length - 1 && (
                      <div className="w-8 h-0.5 bg-gray-300 mx-1" />
                    )}
                  </div>
                ))}
              </div>

              {/* Current stage info */}
              <div className="flex items-center space-x-2 text-sm">
                <span className="text-body">Current Stage:</span>
                <span className="text-heading font-medium capitalize">
                  {pipeline.current_stage.replace('_', ' ')}
                </span>
              </div>

              {/* Detailed view */}
              {selectedPipeline === pipeline.pipeline_id && (
                <div className="mt-4 pt-4 border-t border-stone-200 space-y-3">
                  <h4 className="font-medium text-heading">Stage Details</h4>
                  {factoryStages.map((stage) => (
                    <div key={stage.id} className="flex items-center justify-between p-3 glass-card">
                      <div className="flex items-center space-x-3">
                        {stage.icon}
                        <div>
                          <p className="font-medium text-heading">{stage.name}</p>
                          <p className="text-xs text-body">{stage.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge 
                          className={`text-xs ${getStatusColor(pipeline.stages[stage.id] || 'pending')}`}
                        >
                          {pipeline.stages[stage.id] || 'pending'}
                        </Badge>
                        <span className="text-xs text-body">{stage.estimatedDuration}</span>
                      </div>
                    </div>
                  ))}
                  
                  {/* Error message if any */}
                  {pipeline.error_message && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-sm text-red-800 font-medium">Error:</p>
                      <p className="text-sm text-red-600">{pipeline.error_message}</p>
                    </div>
                  )}
                  
                  {/* Metadata */}
                  {Object.keys(pipeline.metadata).length > 0 && (
                    <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg">
                      <p className="text-sm text-gray-800 font-medium mb-2">Pipeline Metadata:</p>
                      <pre className="text-xs text-gray-600 overflow-x-auto">
                        {JSON.stringify(pipeline.metadata, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
};

export default FactoryProgressMonitor; 