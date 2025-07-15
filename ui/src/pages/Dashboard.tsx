import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Code2, 
  Settings, 
  CreditCard, 
  Activity, 
  Clock,
  DollarSign,
  ExternalLink,
  MoreHorizontal,
  Package,
  Sparkles,
  Globe,
  ArrowRight,
  RefreshCw,
  Palette,
  TestTube,
  Rocket,
  Plus,
  Check,
  Home,
  User,
  BarChart3
} from 'lucide-react';

// Types
interface UserSubscription {
  plan: 'starter' | 'pro' | 'growth';
  buildHours: {
    used: number;
    total: number | 'unlimited';
  };
  projects: {
    used: number;
    total: number;
  };
  billing: {
    amount: number;
    period: 'monthly' | 'yearly';
    nextBilling: string;
  };
  features: string[];
}

interface Project {
  id: string;
  name: string;
  status: 'active' | 'building' | 'deployed' | 'failed' | 'paused';
  progress: number;
  lastUpdated: string;
  url?: string;
  buildHours: number;
  stage: 'idea' | 'design' | 'development' | 'testing' | 'deployment' | 'live';
  revenue?: number;
  users?: number;
}

interface Build {
  id: string;
  projectId: string;
  projectName: string;
  status: 'running' | 'completed' | 'failed' | 'queued';
  stage: 'idea' | 'design' | 'development' | 'testing' | 'deployment';
  startedAt: string;
  completedAt?: string;
  duration?: number;
  buildHours: number;
  logs: string[];
}

interface ActivityItem {
  id: string;
  type: 'build_started' | 'build_completed' | 'build_failed' | 'project_created' | 'payment_processed' | 'user_joined';
  message: string;
  timestamp: string;
  projectId?: string;
  buildId?: string;
  metadata?: any;
}

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview');

  // Mock data
  const subscription: UserSubscription = {
    plan: 'pro',
    buildHours: {
      used: 42,
      total: 60
    },
    projects: {
      used: 2,
      total: 3
    },
    billing: {
      amount: 99,
      period: 'monthly',
      nextBilling: '2024-02-15'
    },
    features: ['AI Design Generation', 'Advanced Analytics', 'Priority Support', 'Custom Integrations']
  };

  const projects: Project[] = [
    {
      id: '1',
      name: 'TaskFlow Pro',
      status: 'deployed',
      progress: 100,
      lastUpdated: '2024-01-15T10:30:00Z',
      url: 'https://taskflow-pro.com',
      buildHours: 24,
      stage: 'live',
      revenue: 2840,
      users: 156
    },
    {
      id: '2',
      name: 'Invoice Genius',
      status: 'building',
      progress: 75,
      lastUpdated: '2024-01-15T14:20:00Z',
      buildHours: 18,
      stage: 'development'
    },
    {
      id: '3',
      name: 'SocialSync',
      status: 'active',
      progress: 25,
      lastUpdated: '2024-01-15T09:15:00Z',
      buildHours: 8,
      stage: 'design'
    }
  ];

  const builds: Build[] = [
    {
      id: '1',
      projectId: '2',
      projectName: 'Invoice Genius',
      status: 'running',
      stage: 'development',
      startedAt: '2024-01-15T13:00:00Z',
      buildHours: 3.5,
      logs: ['Started development phase', 'Generating API endpoints', 'Setting up database schema']
    },
    {
      id: '2',
      projectId: '1',
      projectName: 'TaskFlow Pro',
      status: 'completed',
      stage: 'deployment',
      startedAt: '2024-01-15T08:00:00Z',
      completedAt: '2024-01-15T10:30:00Z',
      duration: 2.5,
      buildHours: 2.5,
      logs: ['Deployment successful', 'SSL certificate configured', 'Domain linked']
    },
    {
      id: '3',
      projectId: '3',
      projectName: 'SocialSync',
      status: 'queued',
      stage: 'design',
      startedAt: '2024-01-15T16:00:00Z',
      buildHours: 0,
      logs: ['Waiting for design generation to start']
    }
  ];

  const activities: ActivityItem[] = [
    {
      id: '1',
      type: 'build_completed',
      message: 'TaskFlow Pro deployment completed successfully',
      timestamp: '2024-01-15T10:30:00Z',
      projectId: '1',
      buildId: '2'
    },
    {
      id: '2',
      type: 'build_started',
      message: 'Invoice Genius development phase started',
      timestamp: '2024-01-15T13:00:00Z',
      projectId: '2',
      buildId: '1'
    },
    {
      id: '3',
      type: 'project_created',
      message: 'New project SocialSync created',
      timestamp: '2024-01-15T09:15:00Z',
      projectId: '3'
    },
    {
      id: '4',
      type: 'payment_processed',
      message: 'Monthly Pro plan payment processed ($99.00)',
      timestamp: '2024-01-15T00:00:00Z'
    },
    {
      id: '5',
      type: 'user_joined',
      message: '12 new users joined TaskFlow Pro',
      timestamp: '2024-01-14T18:45:00Z',
      projectId: '1'
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'deployed':
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'building':
      case 'running':
        return 'text-blue-600 bg-blue-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      case 'paused':
      case 'queued':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

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

  const getStageIcon = (stage: string) => {
    switch (stage) {
      case 'idea':
        return <Sparkles className="w-4 h-4" />;
      case 'design':
        return <Palette className="w-4 h-4" />;
      case 'development':
        return <Code2 className="w-4 h-4" />;
      case 'testing':
        return <TestTube className="w-4 h-4" />;
      case 'deployment':
        return <Rocket className="w-4 h-4" />;
      case 'live':
        return <Globe className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-homepage relative overflow-hidden">
      {/* Glassmorphism Background Elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-br from-green-800/20 to-green-900/25 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-40 right-32 w-80 h-80 bg-gradient-to-bl from-slate-700/20 to-green-800/25 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 left-1/3 w-64 h-64 bg-gradient-to-tr from-stone-600/20 to-green-700/25 rounded-full blur-3xl animate-pulse delay-2000"></div>
        <div className="absolute bottom-32 right-20 w-72 h-72 bg-gradient-to-tl from-green-800/20 to-stone-700/25 rounded-full blur-3xl animate-pulse delay-3000"></div>
      </div>

      {/* Navigation */}
      <nav className="glass-nav sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-accent-icon rounded-xl flex items-center justify-center shadow-lg">
                <Code2 className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-heading">AI SaaS Factory</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="/" className="text-body hover:text-heading transition-colors font-medium">Home</a>
              <a href="/pricing" className="text-body hover:text-heading transition-colors font-medium">Pricing</a>
              <a href="/signup" className="text-body hover:text-heading transition-colors font-medium">Sign Up</a>
              <a href="/dashboard" className="text-heading font-medium">Dashboard</a>
              <div className="flex items-center space-x-2">
                <Badge className="bg-accent text-white text-xs">
                  Pro Plan
                </Badge>
                <Button size="sm" variant="outline" className="btn-ghost">
                  <User className="w-4 h-4 mr-1" />
                  Account
                </Button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        <div className="space-y-8">
          {/* Header */}
          <div className="glass-card p-6">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
              <div>
                <h1 className="text-3xl font-bold text-heading">Dashboard</h1>
                <p className="text-body mt-1">Manage your AI-powered SaaS projects</p>
              </div>
              <div className="flex items-center space-x-4">
                <Button className="btn-primary">
                  <Plus className="w-4 h-4 mr-2" />
                  New Project
                </Button>
                <Button variant="outline" className="btn-secondary">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Sync
                </Button>
              </div>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card className="card-glass">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-body">Build Hours</p>
                    <p className="text-2xl font-bold text-heading">
                      {subscription.buildHours.used}
                      <span className="text-sm text-body">
                        /{subscription.buildHours.total === 'unlimited' ? '∞' : subscription.buildHours.total}
                      </span>
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-accent-icon rounded-xl flex items-center justify-center">
                    <Clock className="w-6 h-6 text-white" />
                  </div>
                </div>
                {subscription.buildHours.total !== 'unlimited' && (
                  <div className="mt-4">
                    <Progress 
                      value={(subscription.buildHours.used / subscription.buildHours.total) * 100} 
                      className="h-2"
                    />
                    <p className="text-xs text-body mt-1">
                      {Math.round((subscription.buildHours.used / subscription.buildHours.total) * 100)}% used
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="card-glass">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-body">Projects</p>
                    <p className="text-2xl font-bold text-heading">
                      {subscription.projects.used}
                      <span className="text-sm text-body">/{subscription.projects.total}</span>
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-accent-secondary rounded-xl flex items-center justify-center">
                    <Package className="w-6 h-6 text-white" />
                  </div>
                </div>
                <div className="mt-4">
                  <Progress 
                    value={(subscription.projects.used / subscription.projects.total) * 100} 
                    className="h-2"
                  />
                  <p className="text-xs text-body mt-1">
                    {subscription.projects.total - subscription.projects.used} slots remaining
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card className="card-glass">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-body">Active Builds</p>
                    <p className="text-2xl font-bold text-heading">
                      {builds.filter(b => b.status === 'running').length}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-accent-tertiary rounded-xl flex items-center justify-center">
                    <Activity className="w-6 h-6 text-white" />
                  </div>
                </div>
                <div className="mt-4">
                  <p className="text-xs text-body">
                    {builds.filter(b => b.status === 'queued').length} queued
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card className="card-glass">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-body">Monthly Spend</p>
                    <p className="text-2xl font-bold text-heading">
                      ${subscription.billing.amount}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-gradient-to-r from-green-800 to-green-900 rounded-xl flex items-center justify-center">
                    <DollarSign className="w-6 h-6 text-white" />
                  </div>
                </div>
                <div className="mt-4">
                  <p className="text-xs text-body">
                    Next billing: {new Date(subscription.billing.nextBilling).toLocaleDateString()}
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Content Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="glass-card p-1">
              <TabsTrigger value="overview" className="btn-ghost">
                <Home className="w-4 h-4 mr-2" />
                Overview
              </TabsTrigger>
              <TabsTrigger value="projects" className="btn-ghost">
                <Package className="w-4 h-4 mr-2" />
                Projects
              </TabsTrigger>
              <TabsTrigger value="builds" className="btn-ghost">
                <Activity className="w-4 h-4 mr-2" />
                Builds
              </TabsTrigger>
              <TabsTrigger value="billing" className="btn-ghost">
                <CreditCard className="w-4 h-4 mr-2" />
                Billing
              </TabsTrigger>
              <TabsTrigger value="activity" className="btn-ghost">
                <Clock className="w-4 h-4 mr-2" />
                Activity
              </TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Recent Projects */}
                <Card className="card-glass">
                  <CardHeader>
                    <CardTitle className="text-heading flex items-center">
                      <Package className="w-5 h-5 mr-2" />
                      Recent Projects
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {projects.slice(0, 3).map((project) => (
                      <div key={project.id} className="flex items-center justify-between p-4 glass-card">
                        <div className="flex items-center space-x-3">
                          <div className={`w-3 h-3 rounded-full ${
                            project.status === 'deployed' ? 'bg-green-500' :
                            project.status === 'building' ? 'bg-blue-500' :
                            project.status === 'active' ? 'bg-yellow-500' :
                            'bg-gray-500'
                          }`} />
                          <div>
                            <p className="font-medium text-heading">{project.name}</p>
                            <p className="text-sm text-body">{formatTimeAgo(project.lastUpdated)}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={`text-xs ${getStatusColor(project.status)}`}>
                            {project.status}
                          </Badge>
                          {project.url && (
                            <Button size="sm" variant="ghost" className="btn-ghost p-1">
                              <ExternalLink className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                {/* Build Queue */}
                <Card className="card-glass">
                  <CardHeader>
                    <CardTitle className="text-heading flex items-center">
                      <Activity className="w-5 h-5 mr-2" />
                      Build Queue
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {builds.slice(0, 3).map((build) => (
                      <div key={build.id} className="flex items-center justify-between p-4 glass-card">
                        <div className="flex items-center space-x-3">
                          {getStageIcon(build.stage)}
                          <div>
                            <p className="font-medium text-heading">{build.projectName}</p>
                            <p className="text-sm text-body capitalize">{build.stage}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={`text-xs ${getStatusColor(build.status)}`}>
                            {build.status}
                          </Badge>
                          <span className="text-xs text-body">{build.buildHours}h</span>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>

              {/* Activity Feed */}
              <Card className="card-glass">
                <CardHeader>
                  <CardTitle className="text-heading flex items-center">
                    <Clock className="w-5 h-5 mr-2" />
                    Recent Activity
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {activities.slice(0, 5).map((activity) => (
                    <div key={activity.id} className="flex items-start space-x-3 p-4 glass-card">
                      <div className={`w-2 h-2 rounded-full mt-2 ${
                        activity.type === 'build_completed' ? 'bg-green-500' :
                        activity.type === 'build_started' ? 'bg-blue-500' :
                        activity.type === 'build_failed' ? 'bg-red-500' :
                        activity.type === 'project_created' ? 'bg-purple-500' :
                        activity.type === 'payment_processed' ? 'bg-green-500' :
                        'bg-gray-500'
                      }`} />
                      <div className="flex-1">
                        <p className="text-sm text-heading">{activity.message}</p>
                        <p className="text-xs text-body">{formatTimeAgo(activity.timestamp)}</p>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="projects" className="space-y-6">
              <Card className="card-glass">
                <CardHeader>
                  <CardTitle className="text-heading flex items-center justify-between">
                    <span className="flex items-center">
                      <Package className="w-5 h-5 mr-2" />
                      Projects ({projects.length})
                    </span>
                    <Button className="btn-primary">
                      <Plus className="w-4 h-4 mr-2" />
                      New Project
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {projects.map((project) => (
                    <div key={project.id} className="p-6 glass-card">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className={`w-4 h-4 rounded-full ${
                            project.status === 'deployed' ? 'bg-green-500' :
                            project.status === 'building' ? 'bg-blue-500' :
                            project.status === 'active' ? 'bg-yellow-500' :
                            'bg-gray-500'
                          }`} />
                          <div>
                            <h3 className="font-semibold text-heading">{project.name}</h3>
                            <p className="text-sm text-body capitalize">{project.stage} • {formatTimeAgo(project.lastUpdated)}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={`${getStatusColor(project.status)}`}>
                            {project.status}
                          </Badge>
                          {project.url && (
                            <Button size="sm" variant="outline" className="btn-secondary">
                              <ExternalLink className="w-4 h-4 mr-1" />
                              View
                            </Button>
                          )}
                          <Button size="sm" variant="outline" className="btn-ghost">
                            <MoreHorizontal className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                      
                      <div className="space-y-3">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-body">Progress</span>
                          <span className="text-heading">{project.progress}%</span>
                        </div>
                        <Progress value={project.progress} className="h-2" />
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                          <div className="text-center">
                            <div className="text-lg font-semibold text-heading">{project.buildHours}h</div>
                            <div className="text-xs text-body">Build Hours</div>
                          </div>
                          {project.revenue && (
                            <div className="text-center">
                              <div className="text-lg font-semibold text-heading">${project.revenue}</div>
                              <div className="text-xs text-body">Revenue</div>
                            </div>
                          )}
                          {project.users && (
                            <div className="text-center">
                              <div className="text-lg font-semibold text-heading">{project.users}</div>
                              <div className="text-xs text-body">Users</div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="builds" className="space-y-6">
              <Card className="card-glass">
                <CardHeader>
                  <CardTitle className="text-heading flex items-center">
                    <Activity className="w-5 h-5 mr-2" />
                    Build History
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {builds.map((build) => (
                    <div key={build.id} className="p-6 glass-card">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          {getStageIcon(build.stage)}
                          <div>
                            <h3 className="font-semibold text-heading">{build.projectName}</h3>
                            <p className="text-sm text-body capitalize">{build.stage} • {formatTimeAgo(build.startedAt)}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={`${getStatusColor(build.status)}`}>
                            {build.status}
                          </Badge>
                          <span className="text-sm text-body">{build.buildHours}h</span>
                        </div>
                      </div>
                      
                      <div className="space-y-3">
                        <div className="glass-card p-4">
                          <h4 className="font-medium text-heading mb-2">Build Logs</h4>
                          <div className="space-y-1">
                            {build.logs.map((log, index) => (
                              <div key={index} className="text-sm text-body font-mono">
                                {log}
                              </div>
                            ))}
                          </div>
                        </div>
                        
                        {build.status === 'completed' && build.duration && (
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-body">Duration</span>
                            <span className="text-heading">{build.duration}h</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="billing" className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="card-glass">
                  <CardHeader>
                    <CardTitle className="text-heading flex items-center">
                      <CreditCard className="w-5 h-5 mr-2" />
                      Current Plan
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="p-4 glass-card">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold text-heading capitalize">{subscription.plan} Plan</h3>
                        <Badge className="bg-accent text-white">${subscription.billing.amount}/{subscription.billing.period}</Badge>
                      </div>
                      <div className="space-y-2">
                        {subscription.features.map((feature, index) => (
                          <div key={index} className="flex items-center space-x-2">
                            <Check className="w-4 h-4 text-accent" />
                            <span className="text-sm text-body">{feature}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div className="flex space-x-2">
                      <Button className="btn-primary flex-1">
                        <ArrowRight className="w-4 h-4 mr-2" />
                        Upgrade Plan
                      </Button>
                      <Button variant="outline" className="btn-secondary">
                        <Settings className="w-4 h-4 mr-2" />
                        Manage
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                <Card className="card-glass">
                  <CardHeader>
                    <CardTitle className="text-heading flex items-center">
                      <BarChart3 className="w-5 h-5 mr-2" />
                      Usage Analytics
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-4">
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-body">Build Hours</span>
                          <span className="text-sm text-heading">
                            {subscription.buildHours.used} / {subscription.buildHours.total === 'unlimited' ? '∞' : subscription.buildHours.total}
                          </span>
                        </div>
                        {subscription.buildHours.total !== 'unlimited' && (
                          <Progress value={(subscription.buildHours.used / subscription.buildHours.total) * 100} className="h-2" />
                        )}
                      </div>
                      
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-body">Projects</span>
                          <span className="text-sm text-heading">
                            {subscription.projects.used} / {subscription.projects.total}
                          </span>
                        </div>
                        <Progress value={(subscription.projects.used / subscription.projects.total) * 100} className="h-2" />
                      </div>
                      
                      <div className="pt-4 border-t border-stone-200">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-body">Next billing</span>
                          <span className="text-sm text-heading">
                            {new Date(subscription.billing.nextBilling).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="activity" className="space-y-6">
              <Card className="card-glass">
                <CardHeader>
                  <CardTitle className="text-heading flex items-center">
                    <Clock className="w-5 h-5 mr-2" />
                    Activity Feed
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {activities.map((activity) => (
                    <div key={activity.id} className="flex items-start space-x-4 p-4 glass-card">
                      <div className={`w-3 h-3 rounded-full mt-2 ${
                        activity.type === 'build_completed' ? 'bg-green-500' :
                        activity.type === 'build_started' ? 'bg-blue-500' :
                        activity.type === 'build_failed' ? 'bg-red-500' :
                        activity.type === 'project_created' ? 'bg-purple-500' :
                        activity.type === 'payment_processed' ? 'bg-green-500' :
                        'bg-gray-500'
                      }`} />
                      <div className="flex-1">
                        <p className="text-sm text-heading">{activity.message}</p>
                        <p className="text-xs text-body">{formatTimeAgo(activity.timestamp)}</p>
                        {activity.metadata && (
                          <div className="mt-2 text-xs text-body bg-stone-100 p-2 rounded">
                            {JSON.stringify(activity.metadata, null, 2)}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-stone-900/95 backdrop-blur-lg text-white py-12 border-t border-stone-400/30 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <div className="w-10 h-10 bg-accent-icon rounded-xl flex items-center justify-center shadow-lg">
                  <Code2 className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold">AI SaaS Factory</span>
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
            <p>&copy; 2024 AI SaaS Factory. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
} 