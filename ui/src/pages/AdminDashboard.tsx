import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { 
  Users, 
  Lightbulb, 
  TrendingUp,
  Clock,
  CheckCircle,
  XCircle,
  Eye,
  Settings,
  Database,
  BarChart3,
  Filter,
  Search,
  RefreshCw,
  AlertTriangle,
  ArrowUpRight,
  Building,
  Activity,
  Code2
} from 'lucide-react';
import AnalyticsPanel from '@/components/AnalyticsPanel';

// Types for admin data
interface Idea {
  id: string;
  project_name: string;
  description: string;
  problem: string;
  solution: string;
  target_audience: string;
  key_features: string;
  business_model: string;
  category: string;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'approved' | 'rejected' | 'in_review';
  admin_notes?: string;
  tenant_name: string;
  tenant_slug: string;
  submitted_by_name: string;
  submitted_by_email: string;
  reviewed_by_name?: string;
  created_at: string;
  reviewed_at?: string;
}

interface Tenant {
  id: string;
  name: string;
  slug: string;
  email: string;
  plan: 'starter' | 'pro' | 'growth';
  status: 'active' | 'inactive' | 'suspended';
  isolation_mode: 'shared' | 'isolated';
  user_count: number;
  project_count: number;
  idea_count: number;
  created_at: string;
  updated_at: string;
}

interface AdminStats {
  total_ideas: number;
  pending_ideas: number;
  approved_ideas: number;
  rejected_ideas: number;
  in_review_ideas: number;
  high_priority_ideas: number;
  medium_priority_ideas: number;
  low_priority_ideas: number;
  avg_review_time_days: number;
}

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [ideas, setIdeas] = useState<Idea[]>([]);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [priorityFilter, setPriorityFilter] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState<string>('');

  // Mock admin context - in production this would come from auth
  const adminContext = {
    tenantId: 'admin',
    userId: 'admin-user-123',
    userRole: 'admin'
  };

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Load ideas
      const ideasResponse = await fetch('/api/admin/ideas', {
        headers: {
          'x-tenant-id': adminContext.tenantId,
          'x-user-id': adminContext.userId,
          'x-user-role': adminContext.userRole
        }
      });

      if (ideasResponse.ok) {
        const ideasData = await ideasResponse.json();
        setIdeas(ideasData.ideas || []);
        setStats(ideasData.statistics || null);
      }

      // Load tenants
      const tenantsResponse = await fetch('/api/admin/tenants', {
        headers: {
          'x-tenant-id': adminContext.tenantId,
          'x-user-id': adminContext.userId,
          'x-user-role': adminContext.userRole
        }
      });

      if (tenantsResponse.ok) {
        const tenantsData = await tenantsResponse.json();
        setTenants(tenantsData.tenants || []);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load admin data');
    } finally {
      setLoading(false);
    }
  };

  const handleIdeaAction = async (ideaId: string, action: string, notes?: string) => {
    try {
      const response = await fetch(`/api/admin/ideas/${ideaId}/review`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'x-tenant-id': adminContext.tenantId,
          'x-user-id': adminContext.userId,
          'x-user-role': adminContext.userRole
        },
        body: JSON.stringify({
          status: action,
          admin_notes: notes,
          reason: `Admin ${action} via dashboard`
        })
      });

      if (response.ok) {
        await loadAdminData(); // Refresh data
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update idea');
      }
    } catch (err) {
      console.error('Error updating idea:', err);
      setError(err instanceof Error ? err.message : 'Failed to update idea');
    }
  };

  const handleTenantIsolation = async (tenantId: string, reason: string) => {
    try {
      const response = await fetch(`/api/admin/tenants/${tenantId}/isolate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-tenant-id': adminContext.tenantId,
          'x-user-id': adminContext.userId,
          'x-user-role': adminContext.userRole
        },
        body: JSON.stringify({
          tenant_id: tenantId,
          reason: reason
        })
      });

      if (response.ok) {
        await loadAdminData(); // Refresh data
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to upgrade tenant');
      }
    } catch (err) {
      console.error('Error upgrading tenant:', err);
      setError(err instanceof Error ? err.message : 'Failed to upgrade tenant');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'bg-green-800/20 text-green-800 border-green-700/40';
      case 'rejected':
        return 'bg-red-700/20 text-red-800 border-red-600/40';
      case 'in_review':
        return 'bg-stone-600/20 text-stone-700 border-stone-500/40';
      case 'pending':
        return 'bg-stone-700/20 text-stone-700 border-stone-600/40';
      default:
        return 'bg-stone-100 text-stone-800 border-stone-200';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-700';
      case 'medium':
        return 'bg-stone-600';
      case 'low':
        return 'bg-stone-500';
      default:
        return 'bg-stone-400';
    }
  };

  const filteredIdeas = ideas.filter(idea => {
    const matchesStatus = !statusFilter || idea.status === statusFilter;
    const matchesPriority = !priorityFilter || idea.priority === priorityFilter;
    const matchesSearch = !searchTerm || 
      idea.project_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      idea.tenant_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      idea.category.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesStatus && matchesPriority && matchesSearch;
  });

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now.getTime() - time.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return time.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-homepage relative overflow-hidden flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-accent mx-auto mb-4" />
          <p className="text-heading">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-homepage relative overflow-hidden">
      {/* Glassmorphism Background Elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-br from-green-800/20 to-green-900/25 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-40 right-32 w-80 h-80 bg-gradient-to-bl from-slate-700/20 to-green-800/25 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 left-1/3 w-64 h-64 bg-gradient-to-tr from-stone-600/20 to-green-700/25 rounded-full blur-3xl animate-pulse delay-2000"></div>
      </div>



      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
            <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5" />
            <div>
              <h4 className="font-medium text-red-800">Error</h4>
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Header */}
        <div className="glass-card p-6 mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
            <div>
              <h1 className="text-3xl font-bold text-heading">Admin Dashboard</h1>
              <p className="text-body mt-1">Manage ideas, tenants, and system operations</p>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className="card-glass">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-body">Total Ideas</p>
                    <p className="text-2xl font-bold text-heading">{stats.total_ideas}</p>
                  </div>
                  <div className="w-12 h-12 bg-accent-icon rounded-xl flex items-center justify-center">
                    <Lightbulb className="w-6 h-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="card-glass">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-body">Pending Review</p>
                    <p className="text-2xl font-bold text-heading">{stats.pending_ideas}</p>
                  </div>
                  <div className="w-12 h-12 bg-yellow-500 rounded-xl flex items-center justify-center">
                    <Clock className="w-6 h-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="card-glass">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-body">Approval Rate</p>
                    <p className="text-2xl font-bold text-heading">
                      {Math.round((stats.approved_ideas / Math.max(stats.total_ideas, 1)) * 100)}%
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-green-800 rounded-xl flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="card-glass">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-body">Avg Review Time</p>
                    <p className="text-2xl font-bold text-heading">
                      {Math.round(stats.avg_review_time_days || 0)}d
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-stone-700 rounded-xl flex items-center justify-center">
                    <BarChart3 className="w-6 h-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Main Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="glass-card p-1 mb-6">
            <TabsTrigger value="overview" className="btn-ghost">
              <Activity className="w-4 h-4 mr-2" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="ideas" className="btn-ghost">
              <Lightbulb className="w-4 h-4 mr-2" />
              Ideas ({stats?.pending_ideas || 0})
            </TabsTrigger>
            <TabsTrigger value="tenants" className="btn-ghost">
              <Users className="w-4 h-4 mr-2" />
              Tenants ({tenants.length})
            </TabsTrigger>
            <TabsTrigger value="analytics" className="btn-ghost">
              <BarChart3 className="w-4 h-4 mr-2" />
              Analytics
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Recent Ideas */}
              <Card className="card-glass">
                <CardHeader>
                  <CardTitle className="text-heading flex items-center">
                    <Lightbulb className="w-5 h-5 mr-2" />
                    Recent Ideas
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {ideas.slice(0, 5).map((idea) => (
                    <div key={idea.id} className="flex items-center justify-between p-4 glass-card">
                      <div className="flex items-center space-x-3">
                        <div className={`w-3 h-3 rounded-full ${getPriorityColor(idea.priority)}`} />
                        <div>
                          <p className="font-medium text-heading">{idea.project_name}</p>
                          <p className="text-sm text-body">{idea.tenant_name} • {formatTimeAgo(idea.created_at)}</p>
                        </div>
                      </div>
                      <Badge className={`text-xs border ${getStatusColor(idea.status)}`}>
                        {idea.status}
                      </Badge>
                    </div>
                  ))}
                  {ideas.length === 0 && (
                    <p className="text-center text-body py-4">No ideas submitted yet</p>
                  )}
                </CardContent>
              </Card>

              {/* Active Tenants */}
              <Card className="card-glass">
                <CardHeader>
                  <CardTitle className="text-heading flex items-center">
                    <Building className="w-5 h-5 mr-2" />
                    Active Tenants
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {tenants.filter(t => t.status === 'active').slice(0, 5).map((tenant) => (
                    <div key={tenant.id} className="flex items-center justify-between p-4 glass-card">
                      <div>
                        <p className="font-medium text-heading">{tenant.name}</p>
                        <p className="text-sm text-body">
                          {tenant.project_count} projects • {tenant.idea_count} ideas
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className="bg-accent text-white text-xs">
                          {tenant.plan}
                        </Badge>
                        {tenant.isolation_mode === 'isolated' && (
                          <Badge className="bg-stone-600 text-white text-xs">
                            <Database className="w-3 h-3 mr-1" />
                            Isolated
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Ideas Management Tab */}
          <TabsContent value="ideas" className="space-y-6">
            {/* Filters */}
            <Card className="card-glass">
              <CardContent className="p-4">
                <div className="flex flex-wrap items-center gap-4">
                  <div className="flex items-center space-x-2">
                    <Search className="w-4 h-4 text-body" />
                    <Input
                      placeholder="Search ideas..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-64"
                    />
                  </div>
                  
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    aria-label="Filter by status"
                    className="px-3 py-2 border border-stone-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent"
                  >
                    <option value="">All Statuses</option>
                    <option value="pending">Pending</option>
                    <option value="in_review">In Review</option>
                    <option value="approved">Approved</option>
                    <option value="rejected">Rejected</option>
                  </select>

                  <select
                    value={priorityFilter}
                    onChange={(e) => setPriorityFilter(e.target.value)}
                    aria-label="Filter by priority"
                    className="px-3 py-2 border border-stone-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent"
                  >
                    <option value="">All Priorities</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                  </select>

                  <Button
                    variant="outline"
                    onClick={() => {
                      setStatusFilter('');
                      setPriorityFilter('');
                      setSearchTerm('');
                    }}
                    className="btn-secondary"
                  >
                    <Filter className="w-4 h-4 mr-2" />
                    Clear Filters
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Ideas List */}
            <div className="space-y-4">
              {filteredIdeas.map((idea) => (
                <Card key={idea.id} className="card-glass">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <div className={`w-3 h-3 rounded-full ${getPriorityColor(idea.priority)}`} />
                          <h3 className="text-lg font-semibold text-heading">{idea.project_name}</h3>
                          <Badge className={`text-xs border ${getStatusColor(idea.status)}`}>
                            {idea.status}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {idea.category}
                          </Badge>
                        </div>
                        
                        <p className="text-body mb-3">{idea.description}</p>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="font-medium text-heading">Problem:</span>
                            <p className="text-body">{idea.problem}</p>
                          </div>
                          <div>
                            <span className="font-medium text-heading">Solution:</span>
                            <p className="text-body">{idea.solution}</p>
                          </div>
                        </div>
                        
                        <div className="mt-4 flex items-center justify-between text-sm text-body">
                          <div>
                            <span className="font-medium">Submitted by:</span> {idea.submitted_by_name} ({idea.tenant_name})
                          </div>
                          <div>
                            <span className="font-medium">Submitted:</span> {formatTimeAgo(idea.created_at)}
                          </div>
                        </div>

                        {idea.admin_notes && (
                          <div className="mt-3 p-3 bg-stone-100 rounded-lg">
                            <span className="font-medium text-heading">Admin Notes:</span>
                            <p className="text-body text-sm">{idea.admin_notes}</p>
                          </div>
                        )}
                      </div>
                      
                      <div className="flex flex-col space-y-2 ml-4">
                        {idea.status === 'pending' && (
                          <>
                            <Button
                              size="sm"
                              onClick={() => handleIdeaAction(idea.id, 'approved', 'Approved via admin dashboard')}
                              className="bg-green-600 hover:bg-green-700 text-white"
                            >
                              <CheckCircle className="w-4 h-4 mr-1" />
                              Approve
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleIdeaAction(idea.id, 'in_review', 'Under review')}
                              className="border-yellow-500 text-yellow-700 hover:bg-yellow-50"
                            >
                              <Eye className="w-4 h-4 mr-1" />
                              Review
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleIdeaAction(idea.id, 'rejected', 'Rejected via admin dashboard')}
                              className="border-red-500 text-red-700 hover:bg-red-50"
                            >
                              <XCircle className="w-4 h-4 mr-1" />
                              Reject
                            </Button>
                          </>
                        )}
                        
                        {idea.status === 'approved' && (
                          <Button
                            size="sm"
                            className="bg-blue-600 hover:bg-blue-700 text-white"
                          >
                            <ArrowUpRight className="w-4 h-4 mr-1" />
                            Promote to Project
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
              
              {filteredIdeas.length === 0 && (
                <Card className="card-glass">
                  <CardContent className="p-8 text-center">
                    <Lightbulb className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-heading mb-2">No Ideas Found</h3>
                    <p className="text-body">No ideas match your current filters.</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Tenants Tab */}
          <TabsContent value="tenants" className="space-y-6">
            <div className="grid grid-cols-1 gap-6">
              {tenants.map((tenant) => (
                <Card key={tenant.id} className="card-glass">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-lg font-semibold text-heading">{tenant.name}</h3>
                          <Badge className="bg-accent text-white text-xs">
                            {tenant.plan}
                          </Badge>
                          <Badge className={`text-xs ${
                            tenant.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {tenant.status}
                          </Badge>
                          {tenant.isolation_mode === 'isolated' && (
                            <Badge className="bg-stone-600 text-white text-xs">
                              <Database className="w-3 h-3 mr-1" />
                              Isolated
                            </Badge>
                          )}
                        </div>
                        
                        <p className="text-body mb-3">Slug: {tenant.slug}</p>
                        
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <span className="font-medium text-heading">Users:</span>
                            <p className="text-body">{tenant.user_count}</p>
                          </div>
                          <div>
                            <span className="font-medium text-heading">Projects:</span>
                            <p className="text-body">{tenant.project_count}</p>
                          </div>
                          <div>
                            <span className="font-medium text-heading">Ideas:</span>
                            <p className="text-body">{tenant.idea_count}</p>
                          </div>
                        </div>
                        
                        <div className="mt-4 text-sm text-body">
                          <span className="font-medium">Created:</span> {formatTimeAgo(tenant.created_at)}
                        </div>
                      </div>
                      
                      <div className="flex flex-col space-y-2 ml-4">
                        {tenant.isolation_mode === 'shared' && tenant.plan !== 'starter' && (
                          <Button
                            size="sm"
                            onClick={() => handleTenantIsolation(tenant.id, 'Admin-initiated isolation upgrade')}
                            className="bg-stone-600 hover:bg-stone-700 text-white"
                          >
                            <Database className="w-4 h-4 mr-1" />
                            Isolate
                          </Button>
                        )}
                        
                        <Button
                          size="sm"
                          variant="outline"
                          className="btn-secondary"
                        >
                          <Settings className="w-4 h-4 mr-1" />
                          Manage
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {stats && (
                <div className="flex justify-between items-center">
                  <span className="text-body">Pending</span>
                  <span className="font-semibold text-heading">{stats.pending_ideas}</span>
                </div>
              )}
              {stats && (
                <div className="flex justify-between items-center">
                  <span className="text-body">Approved</span>
                                            <span className="font-semibold text-heading text-green-800">{stats.approved_ideas}</span>
                </div>
              )}
              {stats && (
                <div className="flex justify-between items-center">
                  <span className="text-body">Rejected</span>
                  <span className="font-semibold text-heading text-red-700">{stats.rejected_ideas}</span>
                </div>
              )}
              {stats && (
                <div className="flex justify-between items-center">
                  <span className="text-body">In Review</span>
                  <span className="font-semibold text-heading text-stone-600">{stats.in_review_ideas}</span>
                </div>
              )}
            </div>
            <div className="mt-8">
              <AnalyticsPanel experimentKey="cta-text" />
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* Footer */}
      <footer className="bg-stone-900/95 backdrop-blur-lg text-white py-12 border-t border-stone-400/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <div className="w-10 h-10 bg-gradient-to-r from-green-800 to-green-900 rounded-xl flex items-center justify-center shadow-lg">
                  <Code2 className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold">Forge95</span>
              </div>
              <p className="text-stone-300">
                Turn any idea into a live SaaS business - no code required.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-stone-200">Product</h4>
              <div className="space-y-2 text-stone-400">
                <a href="/" className="block hover:text-white transition-colors">Features</a>
                <a href="/pricing" className="block hover:text-white transition-colors">Pricing</a>
                <a href="/dashboard" className="block hover:text-white transition-colors">Dashboard</a>
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-stone-200">Company</h4>
              <div className="space-y-2 text-stone-400">
                <a href="#" className="block hover:text-white transition-colors">About</a>
                <a href="#" className="block hover:text-white transition-colors">Blog</a>
                <a href="#" className="block hover:text-white transition-colors">Contact</a>
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-stone-200">Support</h4>
              <div className="space-y-2 text-stone-400">
                <a href="#" className="block hover:text-white transition-colors">Documentation</a>
                <a href="#" className="block hover:text-white transition-colors">Community</a>
                <a href="#" className="block hover:text-white transition-colors">Help Center</a>
              </div>
            </div>
          </div>
          <div className="border-t border-stone-700/50 mt-8 pt-8 text-center text-stone-300">
                          <p>&copy; 2025 Forge95. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
} 