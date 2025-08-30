import React from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { XCircle, ArrowLeft, ArrowRight, Heart, Shield, Zap } from 'lucide-react';

export default function BillingCancel() {
  const router = useRouter();

  const handleBackToPricing = () => {
    router.push('/pricing');
  };

  const handleContactSupport = () => {
    window.location.href = 'mailto:support@saasfactory.com?subject=Billing%20Question';
  };

  const handleTryAgain = () => {
    router.push('/pricing');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-stone-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-red-100 rounded-full mb-6">
              <XCircle className="w-12 h-12 text-red-600" />
            </div>
            <h1 className="text-4xl font-bold text-stone-900 mb-4">
              Checkout Cancelled
            </h1>
            <p className="text-xl text-stone-600">
              No worries! You can always come back and complete your purchase later.
            </p>
          </div>

          {/* Main Content */}
          <Card className="card-glass mb-8">
            <CardHeader className="text-center">
              <CardTitle className="text-heading">What Happened?</CardTitle>
              <CardDescription>
                Your checkout session was cancelled. Here are some common reasons:
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center space-x-3 mb-2">
                    <Shield className="w-5 h-5 text-blue-600" />
                    <h4 className="font-medium text-blue-900">Changed Your Mind?</h4>
                  </div>
                  <p className="text-sm text-blue-700">
                    That's totally fine! Take your time to review our plans and features.
                  </p>
                </div>
                
                <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex items-center space-x-3 mb-2">
                    <Zap className="w-5 h-5 text-yellow-600" />
                    <h4 className="font-medium text-yellow-900">Technical Issues?</h4>
                  </div>
                  <p className="text-sm text-yellow-700">
                    Sometimes things don't work as expected. We're here to help!
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Alternative Options */}
          <Card className="card-glass mb-8">
            <CardHeader>
              <CardTitle className="text-heading text-center">Still Interested?</CardTitle>
              <CardDescription className="text-center">
                Here are some alternatives to consider
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center space-x-3 mb-2">
                    <Heart className="w-5 h-5 text-green-600" />
                    <h4 className="font-medium text-green-900">Start with Free Plan</h4>
                  </div>
                  <p className="text-sm text-green-700 mb-3">
                    Try our platform risk-free with the free plan. You can upgrade anytime!
                  </p>
                  <Button 
                    variant="outline" 
                    className="btn-secondary"
                    onClick={() => router.push('/signup')}
                  >
                    Get Started Free
                  </Button>
                </div>
                
                <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                  <div className="flex items-center space-x-3 mb-2">
                    <Shield className="w-5 h-5 text-purple-600" />
                    <h4 className="font-medium text-purple-900">Contact Sales Team</h4>
                  </div>
                  <p className="text-sm text-purple-700 mb-3">
                    Have questions about our plans? Our sales team is here to help!
                  </p>
                  <Button 
                    variant="outline" 
                    className="btn-secondary"
                    onClick={handleContactSupport}
                  >
                    Contact Sales
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="text-center space-y-4">
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                onClick={handleTryAgain}
                className="btn-primary px-8 py-3 text-lg"
                size="lg"
              >
                <ArrowRight className="w-5 h-5 mr-2" />
                Try Again
              </Button>
              
              <Button 
                onClick={handleBackToPricing}
                variant="outline"
                className="btn-secondary px-8 py-3 text-lg"
                size="lg"
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Back to Pricing
              </Button>
            </div>
            
            <div className="text-sm text-stone-500 space-y-2">
              <p>
                Need help? Contact our support team at{' '}
                <a href="mailto:support@saasfactory.com" className="text-green-600 hover:underline">
                  support@saasfactory.com
                </a>
              </p>
              <p>
                Or call us at{' '}
                <a href="tel:+1-555-0123" className="text-green-600 hover:underline">
                  +1 (555) 0123
                </a>
              </p>
            </div>
          </div>

          {/* FAQ Section */}
          <Card className="card-glass mt-12">
            <CardHeader>
              <CardTitle className="text-heading text-center">Frequently Asked Questions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="border-b border-stone-200 pb-4">
                  <h4 className="font-medium text-stone-900 mb-2">
                    Will I be charged if I cancel during checkout?
                  </h4>
                  <p className="text-sm text-stone-600">
                    No, you won't be charged anything until you complete your purchase. Cancelling during checkout is completely free.
                  </p>
                </div>
                
                <div className="border-b border-stone-200 pb-4">
                  <h4 className="font-medium text-stone-900 mb-2">
                    Can I change my plan later?
                  </h4>
                  <p className="text-sm text-stone-600">
                    Yes! You can upgrade, downgrade, or cancel your plan at any time from your billing dashboard.
                  </p>
                </div>
                
                <div className="border-b border-stone-200 pb-4">
                  <h4 className="font-medium text-stone-900 mb-2">
                    Is there a free trial?
                  </h4>
                  <p className="text-sm text-stone-600">
                    We offer a free plan with limited features, and you can upgrade to paid plans anytime.
                  </p>
                </div>
                
                <div>
                  <h4 className="font-medium text-stone-900 mb-2">
                    What payment methods do you accept?
                  </h4>
                  <p className="text-sm text-stone-600">
                    We accept all major credit cards (Visa, Mastercard, American Express) and debit cards.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
