import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { GitBranch, ExternalLink, XCircle, GitMerge, Eye, MessageSquare, RefreshCw } from 'lucide-react';

interface PullRequest {
  id: string;
  number: number;
  title: string;
  description?: string;
  url: string;
  branch_name: string;
  base_branch: string;
  status: 'open' | 'closed' | 'merged' | 'draft';
  state: 'open' | 'closed';
  mergeable: boolean;
  draft: boolean;
  created_at: string;
  updated_at: string;
  merged_at?: string;
  closed_at?: string;
  author: {
    username: string;
    avatar_url?: string;
  };
  labels: string[];
  checks: {
    status: 'pending' | 'success' | 'failure' | 'error';
    total_count: number;
    success_count: number;
    failure_count: number;
    pending_count: number;
  };
  review_status: 'approved' | 'changes_requested' | 'pending' | 'none';
  commits_count: number;
  additions: number;
  deletions: number;
  changed_files: number;
  project_id?: string;
  module_name?: string;
  generated_by?: string; // DevAgent, UIDevAgent, etc.
}

interface PullRequestsPanelProps {
  className?: string;
  maxPRs?: number;
  autoRefresh?: boolean;
  refreshInterval?: number;
  showOnlyAutoGenerated?: boolean;
}

const PullRequestsPanel: React.FC<PullRequestsPanelProps> = ({
  className = '',
  maxPRs = 10,
  autoRefresh = true,
  refreshInterval = 30000, // 30 seconds
  showOnlyAutoGenerated = false
}) => {
  const [pullRequests, setPullRequests] = useState<PullRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'open' | 'closed' | 'merged'>('all');

  // Fetch pull requests
  const fetchPullRequests = async () => {
    try {
      const params = new URLSearchParams({
        limit: maxPRs.toString(),
        auto_generated: showOnlyAutoGenerated.toString()
      });

      const response = await fetch(`/api/dev/pull-requests?${params}`, {
        headers: {
          'x-tenant-id': 'default', // TODO: Get from context
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setPullRequests(data.pull_requests || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching pull requests:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh logic
  useEffect(() => {
    fetchPullRequests();

    if (autoRefresh) {
      const interval = setInterval(fetchPullRequests, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval, maxPRs, showOnlyAutoGenerated]);

  // Filter pull requests
  const filteredPullRequests = pullRequests.filter(pr => {
    switch (filter) {
      case 'open':
        return pr.status === 'open' || pr.status === 'draft';
      case 'closed':
        return pr.status === 'closed';
      case 'merged':
        return pr.status === 'merged';
      default:
        return true;
    }
  });

  // Get status color and icon
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'bg-green-500/10 text-green-700 border-green-500/20';
      case 'draft':
        return 'bg-gray-500/10 text-gray-700 border-gray-500/20';
      case 'merged':
        return 'bg-purple-500/10 text-purple-700 border-purple-500/20';
      case 'closed':
        return 'bg-red-500/10 text-red-700 border-red-500/20';
      default:
        return 'bg-gray-500/10 text-gray-700 border-gray-500/20';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'open':
        return <GitBranch className="w-4 h-4" />;
      case 'draft':
        return <Eye className="w-4 h-4" />;
      case 'merged':
        return <GitMerge className="w-4 h-4" />;
      case 'closed':
        return <XCircle className="w-4 h-4" />;
      default:
        return <GitBranch className="w-4 h-4" />;
    }
  };

  // Get check status color
  const getCheckStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'text-green-600';
      case 'failure':
      case 'error':
        return 'text-red-600';
      case 'pending':
        return 'text-yellow-600';
      default:
        return 'text-gray-600';
    }
  };

  // Get review status color
  const getReviewStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'text-green-600';
      case 'changes_requested':
        return 'text-red-600';
      case 'pending':
        return 'text-yellow-600';
      default:
        return 'text-gray-600';
    }
  };

  // Format time
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) {
      return `${diffDays}d ago`;
    } else if (diffHours > 0) {
      return `${diffHours}h ago`;
    } else {
      const diffMinutes = Math.floor(diffMs / (1000 * 60));
      return `${diffMinutes}m ago`;
    }
  };

  // Get filter counts
  const getFilterCounts = () => {
    return {
      all: pullRequests.length,
      open: pullRequests.filter(pr => pr.status === 'open' || pr.status === 'draft').length,
      merged: pullRequests.filter(pr => pr.status === 'merged').length,
      closed: pullRequests.filter(pr => pr.status === 'closed').length
    };
  };

  const filterCounts = getFilterCounts();

  if (loading) {
    return (
      <Card className={`bg-white/60 backdrop-blur-sm border-green-200/50 ${className}`}>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
            <span className="ml-3 text-green-700">Loading pull requests...</span>
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
            <GitBranch className="w-6 h-6" />
            Pull Requests
            {pullRequests.length > 0 && (
              <Badge className="bg-green-500/10 text-green-700 border-green-500/20">
                {filteredPullRequests.length}
              </Badge>
            )}
          </CardTitle>
          
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={fetchPullRequests}
              disabled={loading}
              className="bg-white/40 backdrop-blur-sm border-green-200/50 hover:bg-white/60"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="flex flex-wrap gap-2 mt-4">
          {[
            { key: 'all', label: 'All', count: filterCounts.all },
            { key: 'open', label: 'Open', count: filterCounts.open },
            { key: 'merged', label: 'Merged', count: filterCounts.merged },
            { key: 'closed', label: 'Closed', count: filterCounts.closed }
          ].map(({ key, label, count }) => (
            <button
              key={key}
              onClick={() => setFilter(key as any)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                filter === key
                  ? 'bg-green-500/20 text-green-800 border border-green-500/30'
                  : 'bg-white/40 text-green-700 border border-green-200/50 hover:bg-white/60'
              }`}
            >
              {label} ({count})
            </button>
          ))}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
            <div className="flex items-center gap-2 text-red-700">
              <XCircle className="w-4 h-4" />
              <span className="text-sm font-medium">Error loading pull requests</span>
            </div>
            <p className="text-sm text-red-600 mt-1">{error}</p>
          </div>
        )}

        {filteredPullRequests.length === 0 && !error && (
          <div className="text-center py-12">
            <GitBranch className="w-12 h-12 text-green-400 mx-auto mb-4 opacity-50" />
            <p className="text-green-700 font-medium">No pull requests found</p>
            <p className="text-green-600 text-sm mt-1">
              PRs will appear here when code is generated and committed
            </p>
          </div>
        )}

        {filteredPullRequests.map((pr) => (
          <div
            key={pr.id}
            className="p-4 bg-white/40 backdrop-blur-sm rounded-xl border border-green-200/50 space-y-3"
          >
            {/* PR Header */}
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <a
                    href={pr.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-semibold text-green-900 hover:text-green-700 transition-colors flex items-center gap-2"
                  >
                    {pr.title}
                    <ExternalLink className="w-4 h-4" />
                  </a>
                  
                  <Badge className={getStatusColor(pr.status)}>
                    {getStatusIcon(pr.status)}
                    <span className="ml-1.5 capitalize">{pr.status}</span>
                  </Badge>
                  
                  <Badge variant="outline" className="bg-blue-50/50 text-blue-700 border-blue-300/50">
                    #{pr.number}
                  </Badge>
                </div>

                <div className="flex items-center gap-4 text-sm text-green-600 mb-2">
                  <span>
                    <span className="font-medium">{pr.branch_name}</span> → {pr.base_branch}
                  </span>
                  <span>•</span>
                  <span>
                    by {pr.author.username}
                  </span>
                  <span>•</span>
                  <span>
                    {formatTime(pr.created_at)}
                  </span>
                </div>

                {/* Code Stats */}
                <div className="flex items-center gap-6 text-sm text-green-600">
                  <div className="flex items-center gap-1">
                    <span>Files:</span>
                    <span className="font-medium">{pr.changed_files}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span>Commits:</span>
                    <span className="font-medium">{pr.commits_count}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="text-green-700">+{pr.additions}</span>
                    <span className="text-red-600">-{pr.deletions}</span>
                  </div>
                </div>
              </div>

              <div className="text-right">
                <a
                  href={pr.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-3 py-1.5 bg-green-500/10 text-green-700 rounded-md text-sm font-medium hover:bg-green-500/20 transition-colors"
                >
                  <ExternalLink className="w-4 h-4" />
                  View PR
                </a>
              </div>
            </div>

            {/* Labels */}
            {pr.labels.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {pr.labels.map((label, index) => (
                  <Badge
                    key={index}
                    variant="outline"
                    className="bg-gray-50/50 text-gray-700 border-gray-300/50 text-xs"
                  >
                    {label}
                  </Badge>
                ))}
              </div>
            )}

            {/* Status Indicators */}
            <div className="flex items-center gap-6 text-sm">
              {/* Check Status */}
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${
                  pr.checks.status === 'success' ? 'bg-green-500' :
                  pr.checks.status === 'failure' ? 'bg-red-500' :
                  pr.checks.status === 'pending' ? 'bg-yellow-500' : 'bg-gray-400'
                }`} />
                <span className={getCheckStatusColor(pr.checks.status)}>
                  {pr.checks.success_count}/{pr.checks.total_count} checks
                </span>
              </div>

              {/* Review Status */}
              <div className="flex items-center gap-2">
                <MessageSquare className={`w-4 h-4 ${getReviewStatusColor(pr.review_status)}`} />
                <span className={getReviewStatusColor(pr.review_status)}>
                  {pr.review_status === 'none' ? 'No reviews' : 
                   pr.review_status === 'pending' ? 'Review pending' :
                   pr.review_status === 'approved' ? 'Approved' : 'Changes requested'}
                </span>
              </div>

              {/* Auto-generated indicator */}
              {pr.generated_by && (
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-purple-500" />
                  <span className="text-purple-700">
                    Generated by {pr.generated_by}
                  </span>
                </div>
              )}
            </div>

            {/* Description (truncated) */}
            {pr.description && (
              <div className="text-sm text-green-700 bg-green-50/30 p-3 rounded-lg border border-green-200/30">
                <p className="line-clamp-2">
                  {pr.description.length > 120 
                    ? `${pr.description.substring(0, 120)}...` 
                    : pr.description}
                </p>
              </div>
            )}

            {/* Project/Module Info */}
            {(pr.project_id || pr.module_name) && (
              <div className="flex items-center gap-4 text-xs text-green-600 bg-green-50/30 p-2 rounded-lg">
                {pr.project_id && (
                  <span>Project: <span className="font-medium">{pr.project_id}</span></span>
                )}
                {pr.module_name && (
                  <span>Module: <span className="font-medium">{pr.module_name}</span></span>
                )}
              </div>
            )}
          </div>
        ))}

        {filteredPullRequests.length >= maxPRs && (
          <div className="text-center pt-4">
            <p className="text-sm text-green-600">
              Showing {maxPRs} most recent pull requests
            </p>
            <Button
              variant="outline"
              size="sm"
              className="mt-2 bg-white/40 backdrop-blur-sm border-green-200/50 hover:bg-white/60"
              onClick={() => {
                // TODO: Navigate to full PRs view
                console.log('Navigate to full PRs view');
              }}
            >
              View All PRs
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PullRequestsPanel; 