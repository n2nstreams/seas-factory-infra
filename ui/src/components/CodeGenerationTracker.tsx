import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Button } from './ui/button';
import { Clock, Code2, GitBranch, CheckCircle, XCircle, AlertCircle, Play, Pause, Wifi, WifiOff } from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';

interface CodeGenerationTask {
  id: string;
  project_id: string;
  module_name: string;
  module_type: string;
  language: string;
  framework?: string;
  status: 'queued' | 'started' | 'generating' | 'validating' | 'creating_pr' | 'completed' | 'failed';
  progress: number;
  current_stage: string;
  created_at: string;
  updated_at: string;
  estimated_completion?: string;
  error_message?: string;
  total_files?: number;
  completed_files?: number;
  total_lines?: number;
  github_pr?: {
    number: number;
    url: string;
    status: string;
    branch_name: string;
  };
}

interface CodeGenerationTrackerProps {
  className?: string;
  maxTasks?: number;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

const CodeGenerationTracker: React.FC<CodeGenerationTrackerProps> = ({
  className = '',
  maxTasks = 5,
  autoRefresh = true,
  refreshInterval = 3000
}) => {
  const [tasks, setTasks] = useState<CodeGenerationTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isPaused, setIsPaused] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);

  // WebSocket connection for real-time updates
  const { isConnected, connectionStatus, lastMessage } = useWebSocket({
    url: 'ws://localhost:8000/ws/code-generation',
    onMessage: useCallback((message) => {
      if (message.type === 'code_generation_update') {
        // Update specific task
        setTasks(prevTasks => 
          prevTasks.map(task => 
            task.id === message.data.task_id 
              ? { ...task, ...message.data.updates }
              : task
          )
        );
      } else if (message.type === 'code_generation_new') {
        // Add new task
        setTasks(prevTasks => [message.data.task, ...prevTasks]);
      } else if (message.type === 'code_generation_complete') {
        // Mark task as completed
        setTasks(prevTasks =>
          prevTasks.map(task =>
            task.id === message.data.task_id
              ? { ...task, status: 'completed', progress: 100 }
              : task
          )
        );
      }
    }, []),
    onOpen: () => setWsConnected(true),
    onClose: () => setWsConnected(false),
    enabled: !isPaused
  });

  // Fetch code generation tasks
  const fetchTasks = async () => {
    try {
      const response = await fetch('/api/dev/active-tasks', {
        headers: {
          'x-tenant-id': 'default', // TODO: Get from context
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setTasks(data.tasks || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching code generation tasks:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh logic
  useEffect(() => {
    fetchTasks();

    if (autoRefresh && !isPaused) {
      const interval = setInterval(fetchTasks, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, isPaused, refreshInterval]);

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'queued':
        return 'bg-gray-500/10 text-gray-700 border-gray-500/20';
      case 'started':
      case 'generating':
        return 'bg-blue-500/10 text-blue-700 border-blue-500/20';
      case 'validating':
        return 'bg-yellow-500/10 text-yellow-700 border-yellow-500/20';
      case 'creating_pr':
        return 'bg-purple-500/10 text-purple-700 border-purple-500/20';
      case 'completed':
        return 'bg-green-500/10 text-green-700 border-green-500/20';
      case 'failed':
        return 'bg-red-500/10 text-red-700 border-red-500/20';
      default:
        return 'bg-gray-500/10 text-gray-700 border-gray-500/20';
    }
  };

  // Get status icon
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'queued':
        return <Clock className="w-4 h-4" />;
      case 'started':
      case 'generating':
        return <Code2 className="w-4 h-4 animate-pulse" />;
      case 'validating':
        return <AlertCircle className="w-4 h-4 animate-bounce" />;
      case 'creating_pr':
        return <GitBranch className="w-4 h-4 animate-pulse" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4" />;
      case 'failed':
        return <XCircle className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  // Get progress bar color
  const getProgressColor = (status: string, progress: number) => {
    if (status === 'failed') return 'bg-red-500';
    if (status === 'completed') return 'bg-green-500';
    if (progress > 75) return 'bg-green-600';
    if (progress > 50) return 'bg-yellow-500';
    if (progress > 25) return 'bg-blue-500';
    return 'bg-gray-400';
  };

  // Format time
  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString();
  };

  // Calculate estimated time remaining
  const getEstimatedTimeRemaining = (task: CodeGenerationTask) => {
    if (task.status === 'completed' || task.status === 'failed') {
      return null;
    }

    const startTime = new Date(task.created_at).getTime();
    const currentTime = new Date().getTime();
    const elapsed = currentTime - startTime;
    
    if (task.progress <= 0) return 'Calculating...';
    
    const estimatedTotal = (elapsed / task.progress) * 100;
    const remaining = estimatedTotal - elapsed;
    
    if (remaining <= 0) return 'Almost done...';
    
    const minutes = Math.floor(remaining / (1000 * 60));
    const seconds = Math.floor((remaining % (1000 * 60)) / 1000);
    
    if (minutes > 0) {
      return `~${minutes}m ${seconds}s`;
    }
    return `~${seconds}s`;
  };

  if (loading) {
    return (
      <Card className={`bg-white/60 backdrop-blur-sm border-green-200/50 ${className}`}>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
            <span className="ml-3 text-green-700">Loading code generation tasks...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`bg-white/60 backdrop-blur-sm border-green-200/50 ${className}`}>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-3 text-green-800">
            <Code2 className="w-6 h-6" />
            Code Generation Progress
            {tasks.length > 0 && (
              <Badge className="bg-green-500/10 text-green-700 border-green-500/20">
                {tasks.filter(t => ['started', 'generating', 'validating', 'creating_pr'].includes(t.status)).length} active
              </Badge>
            )}
          </CardTitle>
          
          <div className="flex items-center gap-2">
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm ${
              isConnected 
                ? 'bg-green-500/10 text-green-700 border border-green-500/20' 
                : 'bg-red-500/10 text-red-700 border border-red-500/20'
            }`}>
              {isConnected ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
              <span className="font-medium">
                {isConnected ? 'Live' : 'Disconnected'}
              </span>
            </div>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsPaused(!isPaused)}
              className="bg-white/40 backdrop-blur-sm border-green-200/50 hover:bg-white/60"
            >
              {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
              {isPaused ? 'Resume' : 'Pause'}
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={fetchTasks}
              className="bg-white/40 backdrop-blur-sm border-green-200/50 hover:bg-white/60"
            >
              Refresh
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
            <div className="flex items-center gap-2 text-red-700">
              <XCircle className="w-4 h-4" />
              <span className="text-sm font-medium">Error loading tasks</span>
            </div>
            <p className="text-sm text-red-600 mt-1">{error}</p>
          </div>
        )}

        {tasks.length === 0 && !error && (
          <div className="text-center py-12">
            <Code2 className="w-12 h-12 text-green-400 mx-auto mb-4 opacity-50" />
            <p className="text-green-700 font-medium">No active code generation tasks</p>
            <p className="text-green-600 text-sm mt-1">
              Tasks will appear here when code generation starts
            </p>
          </div>
        )}

        {tasks.slice(0, maxTasks).map((task) => (
          <div
            key={task.id}
            className="p-4 bg-white/40 backdrop-blur-sm rounded-xl border border-green-200/50 space-y-3"
          >
            {/* Task Header */}
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="font-semibold text-green-900">{task.module_name}</h3>
                  <Badge className={getStatusColor(task.status)}>
                    {getStatusIcon(task.status)}
                    <span className="ml-1.5 capitalize">{task.status.replace('_', ' ')}</span>
                  </Badge>
                  {task.language && (
                    <Badge variant="outline" className="bg-green-50/50 text-green-700 border-green-300/50">
                      {task.language}
                    </Badge>
                  )}
                  {task.framework && (
                    <Badge variant="outline" className="bg-blue-50/50 text-blue-700 border-blue-300/50">
                      {task.framework}
                    </Badge>
                  )}
                </div>
                
                <p className="text-sm text-green-700 mb-2">
                  Type: <span className="font-medium">{task.module_type}</span>
                  {task.project_id && (
                    <span className="text-green-600"> • Project: {task.project_id}</span>
                  )}
                </p>

                <p className="text-sm text-green-600">
                  {task.current_stage}
                </p>
              </div>

              <div className="text-right text-sm text-green-600">
                <div>Started: {formatTime(task.created_at)}</div>
                {task.status !== 'completed' && task.status !== 'failed' && (
                  <div className="text-green-700 font-medium">
                    ETA: {getEstimatedTimeRemaining(task)}
                  </div>
                )}
              </div>
            </div>

            {/* Progress Bar */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-green-700">Progress</span>
                <span className="text-green-600 font-medium">{Math.round(task.progress)}%</span>
              </div>
              
              <div className="relative">
                <Progress 
                  value={task.progress} 
                  className="h-3 bg-green-100/50"
                />
                <div 
                  className={`absolute inset-0 h-3 rounded-full ${getProgressColor(task.status, task.progress)} transition-all duration-500`}
                  style={{ width: `${task.progress}%` }}
                />
              </div>
            </div>

            {/* Task Metrics */}
            {(task.total_files || task.total_lines) && (
              <div className="flex items-center gap-6 text-sm text-green-600">
                {task.total_files && (
                  <div className="flex items-center gap-1">
                    <span>Files:</span>
                    <span className="font-medium">
                      {task.completed_files || 0}/{task.total_files}
                    </span>
                  </div>
                )}
                {task.total_lines && (
                  <div className="flex items-center gap-1">
                    <span>Lines:</span>
                    <span className="font-medium">{task.total_lines.toLocaleString()}</span>
                  </div>
                )}
              </div>
            )}

            {/* GitHub PR Link */}
            {task.github_pr && (
              <div className="flex items-center gap-3 p-3 bg-purple-50/50 rounded-lg border border-purple-200/50">
                <GitBranch className="w-4 h-4 text-purple-600" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-purple-800">
                    Pull Request #{task.github_pr.number}
                  </p>
                  <p className="text-xs text-purple-600">
                    Branch: {task.github_pr.branch_name}
                  </p>
                </div>
                <a
                  href={task.github_pr.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-1 bg-purple-500/10 text-purple-700 rounded-md text-sm font-medium hover:bg-purple-500/20 transition-colors"
                >
                  View PR
                </a>
              </div>
            )}

            {/* Error Message */}
            {task.error_message && (
              <div className="p-3 bg-red-50/50 rounded-lg border border-red-200/50">
                <p className="text-sm text-red-700">
                  <span className="font-medium">Error:</span> {task.error_message}
                </p>
              </div>
            )}
          </div>
        ))}

        {tasks.length > maxTasks && (
          <div className="text-center pt-4">
            <p className="text-sm text-green-600">
              Showing {maxTasks} of {tasks.length} tasks
            </p>
            <Button
              variant="outline"
              size="sm"
              className="mt-2 bg-white/40 backdrop-blur-sm border-green-200/50 hover:bg-white/60"
              onClick={() => {
                // TODO: Navigate to full tasks view
                console.log('Navigate to full tasks view');
              }}
            >
              View All Tasks
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default CodeGenerationTracker; 