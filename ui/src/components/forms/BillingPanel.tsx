import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  CreditCard, 
  Settings, 
  ArrowUpRight, 
  Check, 
  AlertTriangle,
  Calendar,
  Zap,
  Database,
  HardDrive,
  Brain,
  Users,
  Shield,
  Headphones,
  Rocket
} from 'lucide-react';
import { 
  billingService, 
  PricingTier, 
  Subscription, 
  Customer 
} from '../lib/billing';

interface BillingPanelProps {
  customerId?: string;
  className?: string;
}

export default function BillingPanel({ customerId, className = '' }: BillingPanelProps) {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState(false);
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly');
  const [usage, setUsage] = useState({
    projects: 0,
    buildHours: 0,
    storageGB: 0,
    embeddingsMB: 0,
  });

  useEffect(() => {
    if (customerId) {
      loadCustomerData();
    }
  }, [customerId]);

  const loadCustomerData = async () => {
    if (!customerId) return;
    
    try {
      setLoading(true);
      const sub = await billingService.getCustomerSubscription(customerId);
      setSubscription(sub);
      
      // Mock usage data - replace with real API call
      setUsage({
        projects: 1,
        buildHours: 12,
        storageGB: 2.5,
        embeddingsMB: 75,
      });
    } catch (error) {
      console.error('Error loading customer data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (tierId: string) => {
    if (!customerId) return;
    
    try {
      setUpgrading(true);
      const session = await billingService.createCheckoutSession(
        tierId,
        billingPeriod,
        `${window.location.origin}/billing/success`,
        `${window.location.origin}/billing/cancel`,
        customerId
      );
      
      await billingService.redirectToCheckout(session);
    } catch (error) {
      console.error('Error creating checkout session:', error);
      alert('Failed to start upgrade process. Please try again.');
    } finally {
      setUpgrading(false);
    }
  };

  const handleManageBilling = async () => {
    try {
      const portalUrl = await billingService.createCustomerPortalSession(
        `${window.location.origin}/dashboard`
      );
      window.location.href = portalUrl;
    } catch (error) {
      console.error('Error creating portal session:', error);
      alert('Failed to open billing portal. Please try again.');
    }
  };

  const getCurrentTier = (): PricingTier | undefined => {
    if (!subscription) return undefined;
    return billingService.getTierById(subscription.tier);
  };

  const getUpgradeOptions = (): PricingTier[] => {
    if (!subscription) return billingService.getPricingTiers().filter(tier => tier.id !== 'FREE');
    return billingService.getUpgradeOptions(subscription.tier);
  };

  const getUsagePercentage = (current: number, limit: number): number => {
    if (limit === -1) return 0; // Unlimited
    if (limit === 0) return 100;
    return Math.min((current / limit) * 100, 100);
  };

  const getUsageColor = (percentage: number): string => {
    if (percentage >= 90) return 'text-red-600';
    if (percentage >= 75) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      active: { color: 'bg-green-100 text-green-800', text: 'Active' },
      trialing: { color: 'bg-blue-100 text-blue-800', text: 'Trial' },
      past_due: { color: 'bg-yellow-100 text-yellow-800', text: 'Past Due' },
      canceled: { color: 'bg-gray-100 text-gray-800', text: 'Canceled' },
      incomplete: { color: 'bg-orange-100 text-orange-800', text: 'Incomplete' },
      incomplete_expired: { color: 'bg-red-100 text-red-800', text: 'Expired' },
      unpaid: { color: 'bg-red-100 text-red-800', text: 'Unpaid' },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.active;
    
    return (
      <Badge className={config.color}>
        {config.text}
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className={`animate-pulse ${className}`}>
        <Card>
          <CardHeader>
            <div className="h-6 bg-gray-200 rounded w-1/3"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="h-20 bg-gray-200 rounded"></div>
              <div className="h-32 bg-gray-200 rounded"></div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const currentTier = getCurrentTier();
  const upgradeOptions = getUpgradeOptions();

  return (
    <div className={className}>
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="usage">Usage</TabsTrigger>
          <TabsTrigger value="upgrade">Upgrade</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Current Plan Card */}
          <Card className="card-glass">
            <CardHeader>
              <CardTitle className="text-heading flex items-center">
                <CreditCard className="w-5 h-5 mr-2" />
                Current Plan
              </CardTitle>
              <CardDescription>
                Your current subscription and billing information
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {subscription && currentTier ? (
                <>
                  <div className="p-4 glass-card">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-heading capitalize">
                        {currentTier.name} Plan
                      </h3>
                      {getStatusBadge(subscription.status)}
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div className="text-center p-3 bg-green-800/10 rounded-lg">
                        <div className="text-2xl font-bold text-green-800">
                          ${billingPeriod === 'yearly' ? currentTier.yearly : currentTier.monthly}
                        </div>
                        <div className="text-sm text-stone-700">
                          per {billingPeriod === 'yearly' ? 'year' : 'month'}
                        </div>
                      </div>
                      <div className="text-center p-3 bg-stone-100/50 rounded-lg">
                        <div className="text-lg font-semibold text-stone-800">
                          {currentTier.limits.projects}
                        </div>
                        <div className="text-sm text-stone-700">Projects</div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      {currentTier.features.slice(0, 3).map((feature, index) => (
                        <div key={index} className="flex items-center space-x-2">
                          <Check className="w-4 h-4 text-accent" />
                          <span className="text-sm text-body">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="flex space-x-2">
                    <Button 
                      className="btn-primary flex-1"
                      onClick={() => document.querySelector('[data-tab="upgrade"]')?.click()}
                    >
                      <ArrowUpRight className="w-4 h-4 mr-2" />
                      Upgrade Plan
                    </Button>
                    <Button 
                      variant="outline" 
                      className="btn-secondary"
                      onClick={handleManageBilling}
                    >
                      <Settings className="w-4 h-4 mr-2" />
                      Manage Billing
                    </Button>
                  </div>
                </>
              ) : (
                <div className="text-center py-8">
                  <Rocket className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    No Active Subscription
                  </h3>
                  <p className="text-gray-600 mb-4">
                    You're currently on the free plan. Upgrade to unlock more features.
                  </p>
                  <Button 
                    className="btn-primary"
                    onClick={() => document.querySelector('[data-tab="upgrade"]')?.click()}
                  >
                    <ArrowUpRight className="w-4 h-4 mr-2" />
                    View Plans
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Billing Period Toggle */}
          {subscription && (
            <Card className="card-glass">
              <CardHeader>
                <CardTitle className="text-heading">Billing Period</CardTitle>
                <CardDescription>
                  Switch between monthly and annual billing
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center space-x-4">
                  <Button
                    variant={billingPeriod === 'monthly' ? 'default' : 'outline'}
                    onClick={() => setBillingPeriod('monthly')}
                    className="flex-1"
                  >
                    Monthly
                  </Button>
                  <Button
                    variant={billingPeriod === 'yearly' ? 'default' : 'outline'}
                    onClick={() => setBillingPeriod('yearly')}
                    className="flex-1"
                  >
                    Yearly
                    <Badge className="ml-2 bg-green-100 text-green-800">
                      Save {currentTier ? billingService.getAnnualDiscount(currentTier).toFixed(0) : 0}%
                    </Badge>
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="usage" className="space-y-6">
          {/* Usage Limits Card */}
          <Card className="card-glass">
            <CardHeader>
              <CardTitle className="text-heading flex items-center">
                <Zap className="w-5 h-5 mr-2" />
                Usage Limits
              </CardTitle>
              <CardDescription>
                Track your usage against plan limits
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {currentTier ? (
                <>
                  {/* Projects Usage */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Users className="w-4 h-4 text-gray-600" />
                        <span className="font-medium">Projects</span>
                      </div>
                      <span className="text-sm text-gray-600">
                        {usage.projects} / {currentTier.limits.projects}
                      </span>
                    </div>
                    <Progress 
                      value={getUsagePercentage(usage.projects, currentTier.limits.projects)} 
                      className="h-2"
                    />
                  </div>

                  {/* Build Hours Usage */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Zap className="w-4 h-4 text-gray-600" />
                        <span className="font-medium">Build Hours</span>
                      </div>
                      <span className="text-sm text-gray-600">
                        {usage.buildHours} / {currentTier.limits.buildHours === -1 ? '∞' : currentTier.limits.buildHours}
                      </span>
                    </div>
                    {currentTier.limits.buildHours !== -1 && (
                      <Progress 
                        value={getUsagePercentage(usage.buildHours, currentTier.limits.buildHours)} 
                        className="h-2"
                      />
                    )}
                  </div>

                  {/* Storage Usage */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <HardDrive className="w-4 h-4 text-gray-600" />
                        <span className="font-medium">Storage</span>
                      </div>
                      <span className="text-sm text-gray-600">
                        {usage.storageGB.toFixed(1)} GB / {currentTier.limits.storageGB} GB
                      </span>
                    </div>
                    <Progress 
                      value={getUsagePercentage(usage.storageGB, currentTier.limits.storageGB)} 
                      className="h-2"
                    />
                  </div>

                  {/* Embeddings Usage */}
                  {currentTier.limits.embeddingsMB && (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Brain className="w-4 h-4 text-gray-600" />
                          <span className="font-medium">AI Embeddings</span>
                        </div>
                        <span className="text-sm text-gray-600">
                          {usage.embeddingsMB} MB / {currentTier.limits.embeddingsMB} MB
                        </span>
                      </div>
                      <Progress 
                        value={getUsagePercentage(usage.embeddingsMB, currentTier.limits.embeddingsMB)} 
                        className="h-2"
                      />
                    </div>
                  )}

                  {/* Usage Warnings */}
                  {Object.entries(usage).some(([key, value]) => {
                    const limit = currentTier.limits[key as keyof typeof currentTier.limits];
                    return limit !== -1 && getUsagePercentage(value, limit) >= 80;
                  }) && (
                    <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <AlertTriangle className="w-4 h-4 text-yellow-600" />
                        <span className="text-sm text-yellow-800 font-medium">
                          You're approaching your plan limits. Consider upgrading to avoid service interruptions.
                        </span>
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-600">No active subscription to display usage for.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="upgrade" className="space-y-6">
          {/* Upgrade Options */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {upgradeOptions.map((tier) => (
              <Card key={tier.id} className="card-glass hover:shadow-lg transition-shadow">
                <CardHeader className="text-center">
                  <CardTitle className="text-xl font-bold text-heading">
                    {tier.name}
                  </CardTitle>
                  <CardDescription className="text-body">
                    {tier.description}
                  </CardDescription>
                  <div className="mt-4 p-4 bg-green-800/10 rounded-xl border border-green-800/20">
                    <span className="text-3xl font-bold text-green-800">
                      ${billingPeriod === 'yearly' ? tier.yearly : tier.monthly}
                    </span>
                    <span className="text-stone-700 ml-1">
                      /{billingPeriod === 'yearly' ? 'year' : 'month'}
                    </span>
                    {billingPeriod === 'yearly' && (
                      <div className="text-sm text-green-700 mt-1">
                        Save ${billingService.calculateAnnualSavings(tier)} annually
                      </div>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    {tier.features.slice(0, 5).map((feature, index) => (
                      <div key={index} className="flex items-center space-x-2">
                        <Check className="w-4 h-4 text-accent" />
                        <span className="text-sm text-body">{feature}</span>
                      </div>
                    ))}
                  </div>
                  
                  <Button 
                    className="btn-primary w-full"
                    onClick={() => handleUpgrade(tier.id)}
                    disabled={upgrading}
                  >
                    {upgrading ? 'Processing...' : tier.ctaText}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Current Plan Comparison */}
          {currentTier && (
            <Card className="card-glass">
              <CardHeader>
                <CardTitle className="text-heading">Current Plan: {currentTier.name}</CardTitle>
                <CardDescription>
                  Compare your current plan with upgrade options
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-stone-100/50 rounded-lg">
                    <div className="text-2xl font-bold text-stone-800">
                      {currentTier.limits.projects}
                    </div>
                    <div className="text-sm text-stone-700">Projects</div>
                  </div>
                  <div className="text-center p-4 bg-stone-100/50 rounded-lg">
                    <div className="text-2xl font-bold text-stone-800">
                      {currentTier.limits.buildHours === -1 ? '∞' : currentTier.limits.buildHours}
                    </div>
                    <div className="text-sm text-stone-700">Build Hours</div>
                  </div>
                  <div className="text-center p-4 bg-stone-100/50 rounded-lg">
                    <div className="text-2xl font-bold text-stone-800">
                      {currentTier.limits.storageGB}
                    </div>
                    <div className="text-sm text-stone-700">Storage GB</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
