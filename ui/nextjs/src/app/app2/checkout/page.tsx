import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Check, ArrowLeft, CreditCard, Shield, Zap, Users, HardDrive, Brain } from 'lucide-react';
import { billingService, PricingTier } from '../../../../lib/billing';

export default function Checkout() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [selectedTier, setSelectedTier] = useState<PricingTier | null>(null);
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const planId = searchParams.get('plan');
  const customerId = searchParams.get('customer');

  useEffect(() => {
    if (planId) {
      const tier = billingService.getTierById(planId);
      if (tier) {
        setSelectedTier(tier);
      } else {
        setError('Invalid plan selected');
      }
    }
  }, [planId]);

  const handleCheckout = async () => {
    if (!selectedTier || !customerId) {
      setError('Missing plan or customer information');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const session = await billingService.createCheckoutSession(
        selectedTier.id,
        billingPeriod,
        `${window.location.origin}/billing/success`,
        `${window.location.origin}/billing/cancel`,
        customerId
      );

      await billingService.redirectToCheckout(session);
    } catch (error) {
      console.error('Checkout error:', error);
      setError('Failed to start checkout process. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getDisplayPrice = (tier: PricingTier) => {
    return billingPeriod === 'yearly' ? tier.yearly : tier.monthly;
  };

  const getAnnualSavings = (tier: PricingTier) => {
    return billingService.calculateAnnualSavings(tier);
  };

  const getAnnualDiscount = (tier: PricingTier) => {
    return billingService.getAnnualDiscount(tier);
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-stone-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-red-600">Error</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={() => navigate('/pricing')}
              className="w-full"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Pricing
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!selectedTier) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-stone-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle>Loading...</CardTitle>
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-stone-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate('/pricing')}
            className="mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Pricing
          </Button>
          <h1 className="text-3xl font-bold text-stone-900 mb-2">
            Complete Your Purchase
          </h1>
          <p className="text-stone-600">
            You're just a few steps away from unlocking {selectedTier.name} features
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {/* Plan Summary */}
          <div className="space-y-6">
            <Card className="card-glass">
              <CardHeader>
                <CardTitle className="text-heading flex items-center">
                  <Shield className="w-5 h-5 mr-2" />
                  Plan Summary
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 bg-green-800/10 rounded-xl border border-green-800/20">
                  <div className="text-center">
                    <h3 className="text-2xl font-bold text-green-800 mb-2">
                      {selectedTier.name} Plan
                    </h3>
                    <div className="text-4xl font-bold text-green-800">
                      ${getDisplayPrice(selectedTier)}
                    </div>
                    <div className="text-stone-700">
                      per {billingPeriod === 'yearly' ? 'year' : 'month'}
                    </div>
                    {billingPeriod === 'yearly' && (
                      <Badge className="mt-2 bg-green-100 text-green-800">
                        Save ${getAnnualSavings(selectedTier)} annually
                      </Badge>
                    )}
                  </div>
                </div>

                {/* Billing Period Toggle */}
                <div className="space-y-3">
                  <label className="text-sm font-medium text-stone-700">
                    Billing Period
                  </label>
                  <div className="grid grid-cols-2 gap-3">
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
                      <Badge className="ml-2 bg-green-100 text-green-800 text-xs">
                        Save {getAnnualDiscount(selectedTier).toFixed(0)}%
                      </Badge>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Plan Features */}
            <Card className="card-glass">
              <CardHeader>
                <CardTitle className="text-heading">What's Included</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {selectedTier.features.map((feature, index) => (
                    <div key={index} className="flex items-center space-x-3">
                      <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
                      <span className="text-stone-700">{feature}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Plan Limits */}
            <Card className="card-glass">
              <CardHeader>
                <CardTitle className="text-heading">Plan Limits</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-stone-100/50 rounded-lg">
                    <Users className="w-6 h-6 text-stone-600 mx-auto mb-2" />
                    <div className="text-lg font-semibold text-stone-800">
                      {selectedTier.limits.projects}
                    </div>
                    <div className="text-sm text-stone-600">Projects</div>
                  </div>
                  <div className="text-center p-3 bg-stone-100/50 rounded-lg">
                    <Zap className="w-6 h-6 text-stone-600 mx-auto mb-2" />
                    <div className="text-lg font-semibold text-stone-800">
                      {selectedTier.limits.buildHours === -1 ? '∞' : selectedTier.limits.buildHours}
                    </div>
                    <div className="text-sm text-stone-600">Build Hours</div>
                  </div>
                  <div className="text-center p-3 bg-stone-100/50 rounded-lg">
                    <HardDrive className="w-6 h-6 text-stone-600 mx-auto mb-2" />
                    <div className="text-lg font-semibold text-stone-800">
                      {selectedTier.limits.storageGB}
                    </div>
                    <div className="text-sm text-stone-600">Storage GB</div>
                  </div>
                  {selectedTier.limits.embeddingsMB && (
                    <div className="text-center p-3 bg-stone-100/50 rounded-lg">
                      <Brain className="w-6 h-6 text-stone-600 mx-auto mb-2" />
                      <div className="text-lg font-semibold text-stone-800">
                        {selectedTier.limits.embeddingsMB}
                      </div>
                      <div className="text-sm text-stone-600">Embeddings MB</div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Checkout Form */}
          <div className="space-y-6">
            <Card className="card-glass">
              <CardHeader>
                <CardTitle className="text-heading flex items-center">
                  <CreditCard className="w-5 h-5 mr-2" />
                  Secure Checkout
                </CardTitle>
                <CardDescription>
                  Your payment will be processed securely by Stripe
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Security Notice */}
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <Shield className="w-5 h-5 text-blue-600" />
                    <span className="text-sm text-blue-800 font-medium">
                      Secure Payment Processing
                    </span>
                  </div>
                  <p className="text-sm text-blue-700 mt-2">
                    Your payment information is encrypted and secure. We never store your credit card details.
                  </p>
                </div>

                {/* Order Summary */}
                <div className="space-y-3">
                  <h4 className="font-medium text-stone-900">Order Summary</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-stone-600">
                        {selectedTier.name} Plan ({billingPeriod})
                      </span>
                      <span className="font-medium">
                        ${getDisplayPrice(selectedTier)}
                      </span>
                    </div>
                    {billingPeriod === 'yearly' && (
                      <div className="flex justify-between text-green-600">
                        <span>Annual Discount</span>
                        <span>-${getAnnualSavings(selectedTier)}</span>
                      </div>
                    )}
                    <div className="border-t pt-2">
                      <div className="flex justify-between font-semibold text-lg">
                        <span>Total</span>
                        <span>${getDisplayPrice(selectedTier)}</span>
                      </div>
                      <div className="text-sm text-stone-600">
                        {billingPeriod === 'yearly' ? 'Billed annually' : 'Billed monthly'}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Checkout Button */}
                <Button
                  onClick={handleCheckout}
                  disabled={loading || !customerId}
                  className="w-full btn-primary h-12 text-lg"
                >
                  {loading ? (
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span>Processing...</span>
                    </div>
                  ) : (
                    <>
                      <CreditCard className="w-5 h-5 mr-2" />
                      Complete Purchase
                    </>
                  )}
                </Button>

                {/* Terms */}
                <div className="text-xs text-stone-500 text-center">
                  By completing your purchase, you agree to our{' '}
                  <a href="/terms" className="text-green-600 hover:underline">
                    Terms of Service
                  </a>{' '}
                  and{' '}
                  <a href="/privacy" className="text-green-600 hover:underline">
                    Privacy Policy
                  </a>
                </div>
              </CardContent>
            </Card>

            {/* Money Back Guarantee */}
            <Card className="card-glass">
              <CardHeader>
                <CardTitle className="text-heading text-center">30-Day Money Back Guarantee</CardTitle>
              </CardHeader>
              <CardContent className="text-center">
                <p className="text-stone-600 mb-3">
                  Not satisfied? Get a full refund within 30 days, no questions asked.
                </p>
                <div className="flex items-center justify-center space-x-2 text-green-600">
                  <Shield className="w-4 h-4" />
                  <span className="text-sm font-medium">100% Risk-Free</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
