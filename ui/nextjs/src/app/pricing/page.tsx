"use client";

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Check, 
  Sparkles, 
  ArrowRight, 
  CreditCard,
  Zap,
  Shield,
  Globe,
  BarChart3,
  Headphones,
  Rocket,
  Users,
  Star,
  Crown,
  Code2
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import pricingData from '@/data/pricing.json';

export default function Pricing() {
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly');
  const navigate = useNavigate();

  const handleGetStarted = (tierId: string) => {
    if (tierId === 'FREE') {
      navigate('/signup');
    } else if (tierId === 'ENTERPRISE') {
      // Contact sales logic
      window.location.href = 'mailto:sales@forge95.com';
    } else {
      navigate('/signup', { state: { plan: tierId, billing: billingPeriod } });
    }
  };

  const getPlanIcon = (planId: string) => {
    switch (planId) {
      case 'FREE':
        return <Rocket className="w-8 h-8 text-white" />;
      case 'STARTER':
        return <Zap className="w-8 h-8 text-white" />;
      case 'PRO':
        return <BarChart3 className="w-8 h-8 text-white" />;
      case 'SCALE':
        return <Users className="w-8 h-8 text-white" />;
      case 'ENTERPRISE':
        return <Shield className="w-8 h-8 text-white" />;
      default:
        return <Sparkles className="w-8 h-8 text-white" />;
    }
  };

  const getDisplayPrice = (tier: any) => {
    if (typeof tier.monthly === 'string') return tier.monthly;
    if (billingPeriod === 'yearly' && typeof tier.yearly === 'number') {
      return tier.yearly;
    }
    return tier.monthly;
  };

  const getYearlySavings = (tier: any) => {
    if (typeof tier.monthly === 'number' && typeof tier.yearly === 'number' && tier.monthly > 0) {
      const monthlyTotal = tier.monthly * 12;
      const savings = monthlyTotal - tier.yearly;
      const savingsPercent = Math.round((savings / monthlyTotal) * 100);
      return { savings, savingsPercent };
    }
    return null;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-stone-50 via-stone-100 to-stone-200">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(34,197,94,0.1),transparent_50%),radial-gradient(circle_at_70%_80%,rgba(34,197,94,0.05),transparent_50%)]" />
      
      {/* Background Elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-stone-800/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-stone-900/10 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      {/* Header */}
      <div className="text-center mb-16 relative z-10">
        <Badge className="bg-stone-800/20 text-stone-800 ml-2">
          Pricing
        </Badge>
        <h1 className="text-4xl lg:text-5xl xl:text-6xl font-bold text-stone-900 mt-4 mb-6">
          Simple, Transparent Pricing
        </h1>
        <p className="text-xl lg:text-2xl text-stone-700 max-w-3xl mx-auto leading-relaxed">
          Choose the plan that fits your needs. All plans include our core AI agents and infrastructure.
        </p>
      </div>

      {/* Billing Toggle */}
      <div className="flex items-center justify-center mb-12">
        <div className="bg-white/50 backdrop-blur-sm border border-stone-300/50 rounded-full p-1 shadow-lg">
          <div className="flex items-center space-x-1">
            <button
              onClick={() => setBillingPeriod('monthly')}
              className={`px-6 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
                billingPeriod === 'monthly' ? 'bg-accent' : 'bg-stone-300'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingPeriod('yearly')}
              className={`px-6 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
                billingPeriod === 'yearly' ? 'bg-accent' : 'bg-stone-300'
              }`}
            >
              Yearly
              <span className="text-xs text-green-800 font-medium">
                Save 20%
              </span>
            </button>
          </div>
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="grid lg:grid-cols-3 gap-8 mb-16">
        {/* Free Tier */}
        <Card className="glass-card hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-2 border-stone-300/60">
          <CardHeader className="text-center pb-8">
            <div className="w-16 h-16 bg-gradient-to-r from-stone-800 to-stone-900 rounded-2xl flex items-center justify-center mx-auto shadow-lg">
              <Rocket className="w-8 h-8 text-white" />
            </div>
            <CardTitle className="text-2xl text-stone-900">Free</CardTitle>
            <CardDescription className="text-body text-sm leading-relaxed min-h-[2.5rem] flex items-center justify-center px-2">
              Perfect for testing your first idea
            </CardDescription>
            <div className="space-y-2 min-h-[4rem] flex flex-col justify-center">
              <div className="flex items-baseline justify-center space-x-1">
                <span className="text-4xl font-bold text-stone-900">$0</span>
                <span className="text-stone-600">/month</span>
              </div>
              <p className="text-xs text-stone-800 font-medium">
                No credit card required
              </p>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <ul className="space-y-3">
              <li className="flex items-center space-x-3">
                <Check className="w-5 h-5 text-stone-800 flex-shrink-0" />
                <span className="text-stone-700">1 Project</span>
              </li>
              <li className="flex items-center space-x-3">
                <Check className="w-5 h-5 text-stone-800 flex-shrink-0" />
                <span className="text-stone-700">5 Build Hours</span>
              </li>
              <li className="flex items-center space-x-3">
                <Check className="w-5 h-5 text-stone-800 flex-shrink-0" />
                <span className="text-stone-700">Core AI Agents</span>
              </li>
              <li className="flex items-center space-x-3">
                <Check className="w-5 h-5 text-stone-800 flex-shrink-0" />
                <span className="text-stone-700">Demo Deploy</span>
              </li>
              <li className="flex items-center space-x-3">
                <Check className="w-5 h-5 text-stone-800 flex-shrink-0" />
                <span className="text-stone-700">Community Support</span>
              </li>
            </ul>
            <Button 
              className="w-full bg-gradient-to-r from-stone-800 to-stone-900 hover:from-stone-900 hover:to-stone-800 shadow-lg backdrop-blur-sm border border-stone-400/40"
              onClick={() => navigate('/signup')}
            >
              Get Started Free
            </Button>
          </CardContent>
        </Card>

        {/* Starter Tier */}
        <Card className="glass-card hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-2 border-stone-800/60 relative">
          <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
            <Badge className="bg-gradient-to-r from-stone-800 to-stone-900 text-white shadow-lg backdrop-blur-sm border border-stone-400/40">
              <Star className="w-4 h-4 mr-1" />
              Most Popular
            </Badge>
          </div>
          <CardHeader className="text-center pb-8">
            <div className="w-16 h-16 bg-gradient-to-r from-stone-800 to-stone-900 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
              <Zap className="w-8 h-8 text-white" />
            </div>
            <CardTitle className="text-2xl text-stone-900">Starter</CardTitle>
            <CardDescription className="text-body text-sm leading-relaxed min-h-[2.5rem] flex items-center justify-center px-2">
              Ideal for solo entrepreneurs launching their first SaaS
            </CardDescription>
            <div className="space-y-2 min-h-[4rem] flex flex-col justify-center">
              <div className="flex items-baseline justify-center space-x-1">
                <span className="text-4xl font-bold text-stone-900">$19</span>
                <span className="text-stone-600">/month</span>
              </div>
              <p className="text-xs text-stone-800 font-medium">
                Billed {billingPeriod === 'yearly' ? 'annually' : 'monthly'}
              </p>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <ul className="space-y-3">
              <li className="flex items-center space-x-3">
                <Check className="w-5 h-5 text-stone-800 flex-shrink-0" />
                <span className="text-stone-700">1 Project</span>
              </li>
              <li className="flex items-center space-x-3">
                <Check className="w-5 h-5 text-stone-800 flex-shrink-0" />
                <span className="text-stone-700">25 Build Hours</span>
              </li>
              <li className="flex items-center space-x-3">
                <Check className="w-5 h-5 text-stone-800 flex-shrink-0" />
                <span className="text-stone-700">Core + Advanced Agents</span>
              </li>
              <li className="flex items-center space-x-3">
                <Check className="w-5 h-5 text-stone-800 flex-shrink-0" />
                <span className="text-stone-700">Custom Domain</span>
              </li>
              <li className="flex items-center space-x-3">
                <Check className="w-5 h-5 text-stone-800 flex-shrink-0" />
                <span className="text-stone-700">Priority Support</span>
              </li>
              <li className="flex items-center space-x-3">
                <Check className="w-5 h-5 text-stone-800 flex-shrink-0" />
                <span className="text-stone-700">Analytics Dashboard</span>
              </li>
            </ul>
            <Button 
              className="w-full bg-gradient-to-r from-stone-800 to-stone-900 hover:from-stone-900 hover:to-stone-800 shadow-lg backdrop-blur-sm border border-stone-400/40"
              onClick={() => navigate('/signup')}
            >
              Start Building
            </Button>
          </CardContent>
        </Card>

        {/* Pro Tier */}
        <Card className="glass-card hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-2 border-stone-300/60">
          <CardHeader className="text-center pb-8">
            <div className="w-16 h-16 bg-gradient-to-r from-stone-800 to-stone-900 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
              <Crown className="w-8 h-8 text-white" />
            </div>
            <CardTitle className="text-2xl text-stone-900">Pro</CardTitle>
            <CardDescription className="text-body text-sm leading-relaxed min-h-[2.5rem] flex items-center justify-center px-2">
              For entrepreneurs building multiple SaaS products
            </CardDescription>
            <div className="space-y-2 min-h-[4rem] flex flex-col justify-center">
              <div className="flex items-baseline justify-center space-x-1">
                <span className="text-4xl font-bold text-stone-900">$79</span>
                <span className="text-stone-600">/month</span>
              </div>
              <p className="text-xs text-stone-800 font-medium">
                Billed {billingPeriod === 'yearly' ? 'annually' : 'monthly'}
              </p>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <ul className="space-y-3">
              <li className="flex items-center space-x-3">
                <Check className="w-5 h-5 text-stone-800 flex-shrink-0" />
                <span className="text-stone-700">3 Projects</span>
              </li>
              <li className="flex items-center space-x-3">
                <Check className="w-5 h-5 text-stone-800 flex-shrink-0" />
                <span className="text-stone-700">100 Build Hours</span>
              </li>
              <li className="flex items-center space-x-3">
                <Check className="w-5 h-5 text-stone-800 flex-shrink-0" />
                <span className="text-stone-700">All AI Agents</span>
              </li>
              <li className="flex items-center space-x-3">
                <Check className="w-5 h-5 text-stone-800 flex-shrink-0" />
                <span className="text-stone-700">Custom Branding</span>
              </li>
              <li className="flex items-center space-x-3">
                <Check className="w-5 h-5 text-stone-800 flex-shrink-0" />
                <span className="text-stone-700">Advanced Analytics</span>
              </li>
              <li className="flex items-center space-x-3">
                <Check className="w-5 h-5 text-stone-800 flex-shrink-0" />
                <span className="text-stone-700">Dedicated Support</span>
              </li>
            </ul>
            <Button 
              className="w-full bg-gradient-to-r from-stone-800 to-stone-900 hover:from-stone-900 hover:to-stone-800 shadow-lg backdrop-blur-sm border border-stone-400/40"
              onClick={() => navigate('/signup')}
            >
              Go Pro
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* FAQ Section */}
      <div className="max-w-4xl mx-auto mb-16">
        <h2 className="text-3xl font-bold text-stone-900 text-center mb-12">Frequently Asked Questions</h2>
        <div className="space-y-6">
          <div className="bg-white/50 backdrop-blur-sm border border-stone-300/50 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-stone-900 mb-3">Can I change my plan later?</h3>
            <p className="text-stone-700">Yes! You can upgrade, downgrade, or cancel your plan at any time from your billing dashboard.</p>
          </div>
          <div className="bg-white/50 backdrop-blur-sm border border-stone-300/50 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-stone-900 mb-3">What happens if I exceed my build hours?</h3>
            <p className="text-stone-700">We'll notify you when you're close to your limit. You can either upgrade your plan or wait until the next billing cycle.</p>
          </div>
          <div className="bg-white/50 backdrop-blur-sm border border-stone-300/50 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-stone-900 mb-3">Do you offer refunds?</h3>
            <p className="text-stone-700">We offer a 30-day money-back guarantee. If you're not satisfied, we'll refund your first month.</p>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="text-center">
        <div className="bg-gradient-to-r from-stone-800/10 to-stone-900/10 backdrop-blur-lg border border-stone-800/20 rounded-2xl p-8 max-w-2xl mx-auto">
          <h2 className="text-2xl lg:text-3xl font-bold text-stone-900 mb-4">
            Ready to Build Your SaaS?
          </h2>
          <p className="text-stone-700 mb-6">
            Join thousands of entrepreneurs who are already building successful businesses with AI.
          </p>
          <Button 
            size="lg" 
            className="bg-gradient-to-r from-stone-800 to-stone-900 hover:from-stone-900 hover:to-stone-800 text-lg px-8 py-6 shadow-xl backdrop-blur-sm border border-stone-400/40"
            onClick={() => navigate('/signup')}
          >
            Start Building Today
            <ArrowRight className="w-5 h-5 ml-2" />
          </Button>
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-20 border-t border-stone-200/50 pt-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <div className="w-10 h-10 bg-gradient-to-r from-stone-800 to-stone-900 rounded-xl flex items-center justify-center shadow-lg">
                  <Code2 className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold text-stone-900">Forge95</span>
              </div>
              <p className="text-stone-600 max-w-md">
                Transform your ideas into fully-deployed SaaS applications with AI-powered development agents.
              </p>
            </div>

            <div className="space-y-4">
              <h4 className="font-semibold text-stone-900 mb-4">Product</h4>
              <ul className="space-y-2 text-stone-600">
                <li><a href="/pricing" className="hover:text-stone-900 transition-colors">Pricing</a></li>
                <li><a href="/faq" className="hover:text-stone-900 transition-colors">FAQ</a></li>
                <li><a href="/signin" className="hover:text-stone-900 transition-colors">Sign In</a></li>
                <li><a href="/signup" className="hover:text-stone-900 transition-colors">Sign Up</a></li>
              </ul>
            </div>

            <div className="space-y-4">
              <h4 className="font-semibold text-stone-900 mb-4">Legal</h4>
              <ul className="space-y-2 text-stone-600">
                <li><a href="/privacy" className="hover:text-stone-900 transition-colors">Privacy Policy</a></li>
                <li><a href="/terms" className="hover:text-stone-900 transition-colors">Terms of Service</a></li>
                <li><a href="/dpa" className="hover:text-stone-900 transition-colors">DPA</a></li>
                <li><a href="/security" className="hover:text-stone-900 transition-colors">Security</a></li>
              </ul>
            </div>

            <div className="space-y-4">
              <h4 className="font-semibold text-stone-900 mb-4">Support</h4>
              <ul className="space-y-2 text-stone-600">
                <li><a href="/help" className="hover:text-stone-900 transition-colors">Help Center</a></li>
                <li><a href="/contact" className="hover:text-stone-900 transition-colors">Contact Us</a></li>
                <li><a href="/status" className="hover:text-stone-900 transition-colors">Status</a></li>
                <li><a href="/docs" className="hover:text-stone-900 transition-colors">Documentation</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-stone-200/50 mt-8 pt-8 text-center">
            <p className="text-stone-500">
              &copy; 2025 Forge95. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
} 