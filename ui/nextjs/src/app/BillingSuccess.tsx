import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, ArrowRight, Zap, Users, HardDrive, Brain, Rocket } from 'lucide-react';
import { billingService, PricingTier } from '../lib/billing';

export default function BillingSuccess() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [subscription, setSubscription] = useState<any>(null);
  const [tier, setTier] = useState<PricingTier | null>(null);

  const sessionId = searchParams.get('session_id');
  const customerId = searchParams.get('customer_id');

  useEffect(() => {
    if (sessionId && customerId) {
      // In a real implementation, you would verify the session with your backend
      // and get the actual subscription details
      loadSubscriptionDetails();
    }
  }, [sessionId, customerId]);

  const loadSubscriptionDetails = async () => {
    try {
      setLoading(true);
      
      // Mock loading - replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // For demo purposes, we'll use a mock subscription
      // In production, verify the session with Stripe and get real data
      const mockSubscription = {
        id: 'sub_mock_123',
        status: 'active',
        tier: 'PRO',
        currentPeriodStart: new Date(),
        currentPeriodEnd: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days from now
      };
      
      setSubscription(mockSubscription);
      
      // Get tier details
      const tierDetails = billingService.getTierById(mockSubscription.tier);
      setTier(tierDetails || null);
      
    } catch (error) {
      console.error('Error loading subscription details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGetStarted = () => {
    navigate('/dashboard');
  };

  const handleViewBilling = () => {
    // Navigate to billing management
    navigate('/dashboard?tab=billing');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-stone-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle>Setting up your account...</CardTitle>
            <CardDescription>Please wait while we configure your new plan</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="animate-pulse space-y-4">
              <div className="h-4 bg-gray-200 rounded w-3/4 mx-auto"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2 mx-auto"></div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!subscription || !tier) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-stone-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-red-600">Error</CardTitle>
            <CardDescription>Unable to load subscription details</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => navigate('/dashboard')} className="w-full">
              Go to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-stone-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Success Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-6">
              <CheckCircle className="w-12 h-12 text-green-600" />
            </div>
            <h1 className="text-4xl font-bold text-stone-900 mb-4">
              Welcome to {tier.name}! 🎉
            </h1>
            <p className="text-xl text-stone-600 mb-6">
              Your subscription is now active and you have access to all {tier.name} features.
            </p>
            <Badge className="bg-green-100 text-green-800 text-lg px-4 py-2">
              Subscription Active
            </Badge>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
            {/* Plan Details */}
            <Card className="card-glass">
              <CardHeader>
                <CardTitle className="text-heading flex items-center">
                  <Rocket className="w-5 h-5 mr-2" />
                  Your New Plan
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 bg-green-800/10 rounded-xl border border-green-800/20">
                  <div className="text-center">
                    <h3 className="text-2xl font-bold text-green-800 mb-2">
                      {tier.name} Plan
                    </h3>
                    <p className="text-stone-700">{tier.description}</p>
                  </div>
                </div>

                <div className="space-y-3">
                  <h4 className="font-medium text-stone-900">What's Now Available:</h4>
                  <div className="space-y-2">
                    {tier.features.slice(0, 5).map((feature, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                        <span className="text-stone-700">{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Next Steps */}
            <Card className="card-glass">
              <CardHeader>
                <CardTitle className="text-heading">Next Steps</CardTitle>
                <CardDescription>
                  Get started with your new features
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <h4 className="font-medium text-blue-900 mb-2">1. Explore Your Dashboard</h4>
                    <p className="text-sm text-blue-700">
                      Check out your new project limits and features in the dashboard.
                    </p>
                  </div>
                  
                  <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                    <h4 className="font-medium text-purple-900 mb-2">2. Create Your First Project</h4>
                    <p className="text-sm text-purple-700">
                      Start building with your new {tier.limits.projects} project limit.
                    </p>
                  </div>
                  
                  <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
                    <h4 className="font-medium text-orange-900 mb-2">3. Set Up Billing</h4>
                    <p className="text-sm text-orange-700">
                      Manage your subscription and payment methods.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Plan Limits Overview */}
          <Card className="card-glass mb-12">
            <CardHeader>
              <CardTitle className="text-heading text-center">Your New Limits</CardTitle>
              <CardDescription className="text-center">
                Here's what you can now do with your {tier.name} plan
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="text-center p-4 bg-stone-100/50 rounded-lg">
                  <Users className="w-8 h-8 text-stone-600 mx-auto mb-3" />
                  <div className="text-2xl font-bold text-stone-800">
                    {tier.limits.projects}
                  </div>
                  <div className="text-sm text-stone-600">Projects</div>
                </div>
                
                <div className="text-center p-4 bg-stone-100/50 rounded-lg">
                  <Zap className="w-8 h-8 text-stone-600 mx-auto mb-3" />
                  <div className="text-2xl font-bold text-stone-800">
                    {tier.limits.buildHours === -1 ? '∞' : tier.limits.buildHours}
                  </div>
                  <div className="text-sm text-stone-600">Build Hours</div>
                </div>
                
                <div className="text-center p-4 bg-stone-100/50 rounded-lg">
                  <HardDrive className="w-8 h-8 text-stone-600 mx-auto mb-3" />
                  <div className="text-2xl font-bold text-stone-800">
                    {tier.limits.storageGB}
                  </div>
                  <div className="text-sm text-stone-600">Storage GB</div>
                </div>
                
                {tier.limits.embeddingsMB && (
                  <div className="text-center p-4 bg-stone-100/50 rounded-lg">
                    <Brain className="w-8 h-8 text-stone-600 mx-auto mb-3" />
                    <div className="text-2xl font-bold text-stone-800">
                      {tier.limits.embeddingsMB}
                    </div>
                    <div className="text-sm text-stone-600">Embeddings MB</div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="text-center space-y-4">
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                onClick={handleGetStarted}
                className="btn-primary px-8 py-3 text-lg"
                size="lg"
              >
                <Rocket className="w-5 h-5 mr-2" />
                Get Started
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
              
              <Button 
                onClick={handleViewBilling}
                variant="outline"
                className="btn-secondary px-8 py-3 text-lg"
                size="lg"
              >
                Manage Billing
              </Button>
            </div>
            
            <p className="text-sm text-stone-500">
              Need help? Contact our support team at{' '}
              <a href="mailto:support@saasfactory.com" className="text-green-600 hover:underline">
                support@saasfactory.com
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
