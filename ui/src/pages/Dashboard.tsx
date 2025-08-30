import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import FactoryProgressMonitor from "@/components/FactoryProgressMonitor";
import OnboardingWizard from "@/components/OnboardingWizard";
import { onboardingUtils } from "@/lib/userPreferences";
import { apiClient } from '@/lib/api';
import { useAuth } from '@/App';
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
  BarChart3,
  Lightbulb
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

// Helper functions to map idea data to project format
const mapIdeaStatusToProjectStatus = (ideaStatus: string): Project['status'] => {
  switch (ideaStatus) {
    case 'pending': return 'active';
    case 'in_progress': return 'building';
    case 'completed': return 'deployed';
    case 'failed': return 'failed';
    case 'paused': return 'paused';
    default: return 'active';
  }
};

const getProgressByStatus = (ideaStatus: string): number => {
  switch (ideaStatus) {
    case 'pending': return 10;
    case 'in_progress': return 50;
    case 'completed': return 100;
    case 'failed': return 0;
    case 'paused': return 25;
    default: return 10;
  }
};

const mapIdeaStatusToStage = (ideaStatus: string): Project['stage'] => {
  switch (ideaStatus) {
    case 'pending': return 'idea';
    case 'in_progress': return 'development';
    case 'completed': return 'live';
    case 'failed': return 'idea';
    case 'paused': return 'design';
    default: return 'idea';
  }
};

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
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  // Check if user needs onboarding on component mount
  useEffect(() => {
    const needsOnboarding = !onboardingUtils.isCompleted();
    if (needsOnboarding) {
      // Small delay to ensure the dashboard has rendered
      setTimeout(() => setShowOnboarding(true), 500);
    }
  }, []);

  // Fetch user's submitted ideas
  useEffect(() => {
    const fetchUserIdeas = async () => {
      if (!user?.id) {
        setLoading(false);
        return;
      }

      try {
        const response = await apiClient.get('/api/ideas/my-ideas', {
          headers: {
            'x-user-id': user.id,
            'x-tenant-id': '5aff78c7-413b-4e0e-bbfb-090765835bab'
          }
        });

        // Map ideas to projects format
        const mappedProjects: Project[] = response.map((idea: any) => ({
          id: idea.id,
          name: idea.project_name || idea.title,
          status: mapIdeaStatusToProjectStatus(idea.status),
          progress: getProgressByStatus(idea.status),
          lastUpdated: idea.updated_at || idea.created_at,
          buildHours: 0, // Default for now
          stage: mapIdeaStatusToStage(idea.status)
        }));

        setProjects(mappedProjects);
      } catch (error) {
        console.error('Error fetching user ideas:', error);
        // Fallback to empty array
        setProjects([]);
      } finally {
        setLoading(false);
      }
    };

    fetchUserIdeas();
  }, [user]);

  const handleOnboardingComplete = () => {
    onboardingUtils.complete();
    setShowOnboarding(false);
  };

  const handleOnboardingSkip = () => {
    onboardingUtils.complete();
    setShowOnboarding(false);
  };

  // Calculate metrics from real user data
  const totalBuildHours = projects.reduce((sum, project) => sum + project.buildHours, 0);
  
  const subscription: UserSubscription = {
    plan: 'starter', // Default for new users
    buildHours: {
      used: totalBuildHours,
      total: 20 // Starter plan limit
    },
    projects: {
      used: projects.length,
      total: 5 // Starter plan limit
    },
    billing: {
      amount: 0, // Free starter plan
      period: 'monthly',
      nextBilling: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    },
    features: ['Basic AI Generation', 'Community Support', 'Standard Templates']
  };

  // Projects will be loaded from API

  // Build queue will be derived from user projects
  const builds: Build[] = projects.map((project) => ({
    id: project.id,
    projectId: project.id,
    projectName: project.name,
    status: project.status === 'building' ? 'running' : 
           project.status === 'deployed' ? 'completed' : 'queued',
    stage: project.stage === 'live' ? 'deployment' : project.stage as Build['stage'],
    startedAt: project.lastUpdated,
    buildHours: project.buildHours,
    logs: project.status === 'building' ? 
      [`Starting ${project.stage} phase for ${project.name}`, 'Initializing build environment'] :
      project.status === 'deployed' ? 
      [`${project.name} deployment completed successfully`] :
      [`${project.name} queued for processing`]
  }));

  // Generate activities from user's real projects
  const activities: ActivityItem[] = projects.map((project) => ({
    id: project.id,
    type: 'project_created' as const,
    message: `Project "${project.name}" was submitted for processing`,
    timestamp: project.lastUpdated,
    projectId: project.id
  })).slice(0, 5); // Show most recent 5 activities

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'deployed':
      case 'completed':
        return 'text-green-800 bg-green-800/20';
      case 'building':
      case 'running':
        return 'text-stone-700 bg-stone-700/20';
      case 'failed':
        return 'text-red-700 bg-red-700/20';
      case 'paused':
      case 'queued':
        return 'text-stone-600 bg-stone-600/20';
      default:
        return 'text-stone-700 bg-stone-100';
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

  if (loading) {
    return (
      <div className="min-h-screen bg-homepage relative overflow-hidden flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-heading" />
          <p className="text-heading">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  // Show welcome message for new users with no projects
  //const isNewUser = projects.length === 0;

  return (
    <div className="min-h-screen bg-homepage relative overflow-hidden">
      {/* Glassmorphism Background Elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-br from-green-800/20 to-green-900/25 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-40 right-32 w-80 h-80 bg-gradient-to-bl from-slate-700/20 to-green-800/25 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 left-1/3 w-64 h-64 bg-gradient-to-tr from-stone-600/20 to-green-700/25 rounded-full blur-3xl animate-pulse delay-2000"></div>
        <div className="absolute bottom-32 right-20 w-72 h-72 bg-gradient-to-tl from-green-800/20 to-stone-700/25 rounded-full blur-3xl animate-pulse delay-3000"></div>
      </div>



      <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16 py-8 relative z-10">
        <div className="space-y-8">
          {/* Header */}
          <div className="glass-card p-6">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
              <div>
                <h1 className="text-3xl xl:text-4xl font-bold text-heading">Dashboard</h1>
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
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
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
            <TabsList className="glass-card p-1 w-full" data-onboarding="dashboard-tabs">
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
              <TabsTrigger value="factory" className="btn-ghost">
                <Activity className="w-4 h-4 mr-2" />
                Factory
              </TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6">
              {/* Quick Start Actions */}
              <Card className="card-glass" data-onboarding="submit-idea">
                <CardHeader>
                  <CardTitle className="text-heading flex items-center">
                    <Sparkles className="w-5 h-5 mr-2" />
                    Quick Start
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-col sm:flex-row gap-4">
                    <div className="flex-1">
                      <h3 className="font-semibold text-green-900 mb-2">Got a SaaS idea?</h3>
                      <p className="text-sm text-green-800/70 mb-4">
                        Describe your idea and watch our AI factory build it into a real application in 24 hours.
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button 
                        className="bg-green-800 hover:bg-green-900 text-white shadow-lg"
                        onClick={() => window.location.href = '/submit-idea'}
                      >
                        <Lightbulb className="w-4 h-4 mr-2" />
                        Submit Your Idea
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                {/* Recent Projects */}
                <Card className="card-glass" data-onboarding="project-stages">
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
                            project.status === 'deployed' ? 'bg-green-800' :
                            project.status === 'building' ? 'bg-stone-700' :
                            project.status === 'active' ? 'bg-stone-600' :
                            'bg-stone-500'
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
                        activity.type === 'build_completed' ? 'bg-green-800' :
                        activity.type === 'build_started' ? 'bg-stone-700' :
                        activity.type === 'build_failed' ? 'bg-red-700' :
                        activity.type === 'project_created' ? 'bg-stone-600' :
                        activity.type === 'payment_processed' ? 'bg-green-800' :
                        'bg-stone-500'
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
                  <div className="grid grid-cols-1 xl:grid-cols-2 2xl:grid-cols-3 gap-6">
                    {projects.map((project) => (
                      <div key={project.id} className="p-6 glass-card">
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center space-x-3">
                            <div className={`w-4 h-4 rounded-full ${
                              project.status === 'deployed' ? 'bg-green-800' :
                              project.status === 'building' ? 'bg-stone-700' :
                              project.status === 'active' ? 'bg-stone-600' :
                              'bg-stone-500'
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
                          
                          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
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
                  </div>
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
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="billing" className="space-y-6">
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
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
                  <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
                    {activities.map((activity) => (
                      <div key={activity.id} className="flex items-start space-x-4 p-4 glass-card">
                        <div className={`w-3 h-3 rounded-full mt-2 ${
                          activity.type === 'build_completed' ? 'bg-green-800' :
                          activity.type === 'build_started' ? 'bg-stone-700' :
                          activity.type === 'build_failed' ? 'bg-red-700' :
                          activity.type === 'project_created' ? 'bg-stone-600' :
                          activity.type === 'payment_processed' ? 'bg-green-800' :
                          'bg-stone-500'
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
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="factory" className="space-y-6">
              <FactoryProgressMonitor 
                tenantId="default"
                userId="default-user"
                className="w-full"
              />
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-stone-900/95 backdrop-blur-lg text-white py-12 border-t border-stone-400/30 mt-16">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <div className="w-10 h-10 bg-accent-icon rounded-xl flex items-center justify-center shadow-lg">
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
      
      {/* Onboarding Wizard */}
      <OnboardingWizard
        isOpen={showOnboarding}
        onComplete={handleOnboardingComplete}
        onSkip={handleOnboardingSkip}
      />
    </div>
  );
} 