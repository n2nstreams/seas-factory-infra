import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Check, Star, ArrowRight, Code2, Sparkles, Shield, Zap, Users, CreditCard, HeadphonesIcon } from "lucide-react";
import { loadStripe } from '@stripe/stripe-js';

export default function Pricing() {
  const [isYearly, setIsYearly] = useState(false);
  const [loadingPlan, setLoadingPlan] = useState<string | null>(null);

  // TODO: Replace with real customer_id from auth context
  const customerId = 'cus_test123';

  const handleCheckout = async (planId: string) => {
    setLoadingPlan(planId);
    try {
      // Map planId to SubscriptionTier
      const tier = planId.toUpperCase(); // 'starter' -> 'STARTER'
      const response = await fetch('/api/billing/create-checkout-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_id: customerId,
          tier,
          success_url: window.location.origin + '/dashboard',
          cancel_url: window.location.origin + '/pricing',
          metadata: {}
        })
      });
      if (!response.ok) throw new Error('Failed to create checkout session');
      const data = await response.json();
      const stripe = await loadStripe(import.meta.env.VITE_STRIPE_PUBLIC_KEY);
      if (!stripe) throw new Error('Stripe.js failed to load');
      await stripe.redirectToCheckout({ sessionId: data.id });
    } catch (err) {
      alert('Error starting checkout: ' + (err as Error).message);
    } finally {
      setLoadingPlan(null);
    }
  };

  const plans = [
    {
      id: 'starter',
      name: 'Starter',
      description: 'Perfect for trying out the platform',
      monthlyPrice: 29,
      yearlyPrice: 23,
      features: [
        '1 project included',
        '15 build hours per month',
        'Basic design templates',
        'Email support',
        'Community access'
      ],
      buildHours: 15,
      projects: 1,
      support: 'Community forum',
      popular: false
    },
    {
      id: 'pro',
      name: 'Pro',
      description: 'For growing businesses',
      monthlyPrice: 99,
      yearlyPrice: 79,
      features: [
        '3 projects included',
        '60 build hours per month',
        'Advanced design system',
        'Priority email support',
        'Analytics dashboard',
        'Custom integrations'
      ],
      buildHours: 60,
      projects: 3,
      support: 'Email, 48h SLA',
      popular: true
    },
    {
      id: 'growth',
      name: 'Growth',
      description: 'For scaling teams',
      monthlyPrice: 299,
      yearlyPrice: 239,
      features: [
        '5 projects included',
        'Unlimited build hours',
        'Custom design system',
        'Slack support',
        'Advanced analytics',
        'White-label options',
        'API access'
      ],
      buildHours: 'Unlimited',
      projects: 5,
      support: 'Slack, 24h SLA',
      popular: false
    }
  ];

  const faqs = [
    {
      question: "What are build hours?",
      answer: "Build hours represent the computational time our AI agents spend creating your application. This includes design generation, code development, testing, and deployment processes."
    },
    {
      question: "Can I change plans anytime?",
      answer: "Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately, and we'll pro-rate your billing accordingly."
    },
    {
      question: "Do you offer refunds?",
      answer: "We offer a 14-day money-back guarantee. If you're not satisfied within the first 14 days, we'll provide a full refund."
    },
    {
      question: "What happens if I exceed my build hours?",
      answer: "Your projects will be paused until the next billing cycle. You can upgrade your plan or purchase additional build hours if needed."
    },
    {
      question: "Is there a free trial?",
      answer: "Yes! All plans come with a 7-day free trial. No credit card required to start."
    }
  ];

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
              <a href="/pricing" className="text-heading font-medium">Pricing</a>
              <a href="/signup" className="text-body hover:text-heading transition-colors font-medium">Sign Up</a>
              <a href="/dashboard" className="text-body hover:text-heading transition-colors font-medium">Dashboard</a>
              <Button size="sm" className="btn-primary">
                Get Started
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative py-20 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center space-y-8">
            <div className="space-y-6">
              <Badge className="glass-button">
                <Sparkles className="w-4 h-4 mr-2" />
                Simple, Transparent Pricing
              </Badge>
              <h1 className="text-4xl lg:text-6xl font-bold text-heading leading-tight">
                Choose Your{" "}
                <span className="text-accent">
                  Perfect Plan
                </span>
              </h1>
              <p className="text-xl text-body leading-relaxed max-w-3xl mx-auto">
                Start building your AI-powered SaaS business today. All plans include our complete platform with different levels of usage and support.
              </p>
            </div>

            {/* Billing Toggle */}
            <div className="flex items-center justify-center space-x-4 p-1 glass-card max-w-sm mx-auto">
              <span className={`text-sm font-medium transition-colors ${!isYearly ? 'text-heading' : 'text-body'}`}>
                Monthly
              </span>
              <button
                onClick={() => setIsYearly(!isYearly)}
                className={`relative w-12 h-6 rounded-full transition-all duration-200 ${
                  isYearly ? 'bg-accent' : 'bg-stone-300'
                }`}
                aria-label={`Switch to ${isYearly ? 'monthly' : 'yearly'} billing`}
              >
                <div className={`absolute w-5 h-5 bg-white rounded-full shadow-md top-0.5 transition-all duration-200 ${
                  isYearly ? 'left-6' : 'left-0.5'
                }`} />
              </button>
              <span className={`text-sm font-medium transition-colors ${isYearly ? 'text-heading' : 'text-body'}`}>
                Yearly
              </span>
              <Badge className="bg-accent text-white text-xs">
                Save 20%
              </Badge>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Plans */}
      <section className="py-20 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-3 gap-8">
            {plans.map((plan) => (
              <Card key={plan.id} className={plan.popular ? 'card-glass-highlighted relative' : 'card-glass'}>
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-accent text-white shadow-lg">
                      <Star className="w-4 h-4 mr-1" />
                      Most Popular
                    </Badge>
                  </div>
                )}
                <CardHeader className="text-center">
                  <CardTitle className="text-2xl font-bold text-heading">{plan.name}</CardTitle>
                  <CardDescription className="text-body">{plan.description}</CardDescription>
                  <div className="mt-6 p-4 glass-card">
                    <span className="text-4xl font-bold text-accent">
                      ${isYearly ? plan.yearlyPrice : plan.monthlyPrice}
                    </span>
                    <span className="text-body">/month</span>
                    {isYearly && (
                      <div className="text-sm text-muted mt-1">
                        Billed annually (${plan.yearlyPrice * 12})
                      </div>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 glass-card">
                      <div className="flex items-center space-x-2">
                        <Users className="w-4 h-4 text-accent" />
                        <span className="text-sm font-medium text-heading">Projects</span>
                      </div>
                      <span className="text-accent font-bold">{plan.projects}</span>
                    </div>
                    <div className="flex items-center justify-between p-3 glass-card">
                      <div className="flex items-center space-x-2">
                        <Zap className="w-4 h-4 text-accent" />
                        <span className="text-sm font-medium text-heading">Build Hours</span>
                      </div>
                      <span className="text-accent font-bold">{plan.buildHours}</span>
                    </div>
                    <div className="flex items-center justify-between p-3 glass-card">
                      <div className="flex items-center space-x-2">
                        <HeadphonesIcon className="w-4 h-4 text-accent" />
                        <span className="text-sm font-medium text-heading">Support</span>
                      </div>
                      <span className="text-body text-sm">{plan.support}</span>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <h4 className="font-semibold text-heading">Everything included:</h4>
                    {plan.features.map((feature, index) => (
                      <div key={index} className="flex items-center space-x-3 p-2 rounded-lg glass-card">
                        <Check className="w-5 h-5 text-accent" />
                        <span className="text-sm text-body">{feature}</span>
                      </div>
                    ))}
                  </div>

                  <Button 
                    className={plan.popular ? 'btn-primary w-full' : 'btn-secondary w-full'}
                    onClick={() => handleCheckout(plan.id)}
                    disabled={loadingPlan === plan.id}
                  >
                    {loadingPlan === plan.id ? 'Redirecting...' : (plan.popular ? 'Get Started' : 'Choose Plan')}
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Features Comparison */}
      <section className="py-20 bg-stone-200/60 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-heading">
              Compare All Features
            </h2>
            <p className="text-xl text-body">
              See what's included in each plan
            </p>
          </div>

          <div className="glass-card p-8 overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-stone-300/50">
                  <th className="text-left p-4 text-heading font-semibold">Feature</th>
                  <th className="text-center p-4 text-heading font-semibold">Starter</th>
                  <th className="text-center p-4 text-heading font-semibold">Pro</th>
                  <th className="text-center p-4 text-heading font-semibold">Growth</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-300/50">
                <tr>
                  <td className="p-4 text-body font-medium">Projects</td>
                  <td className="text-center p-4 text-accent font-bold">1</td>
                  <td className="text-center p-4 text-accent font-bold">3</td>
                  <td className="text-center p-4 text-accent font-bold">5</td>
                </tr>
                <tr>
                  <td className="p-4 text-body font-medium">Build Hours</td>
                  <td className="text-center p-4 text-accent font-bold">15/month</td>
                  <td className="text-center p-4 text-accent font-bold">60/month</td>
                  <td className="text-center p-4 text-accent font-bold">Unlimited</td>
                </tr>
                <tr>
                  <td className="p-4 text-body font-medium">AI Design Generation</td>
                  <td className="text-center p-4"><Check className="w-5 h-5 text-accent mx-auto" /></td>
                  <td className="text-center p-4"><Check className="w-5 h-5 text-accent mx-auto" /></td>
                  <td className="text-center p-4"><Check className="w-5 h-5 text-accent mx-auto" /></td>
                </tr>
                <tr>
                  <td className="p-4 text-body font-medium">Code Generation</td>
                  <td className="text-center p-4"><Check className="w-5 h-5 text-accent mx-auto" /></td>
                  <td className="text-center p-4"><Check className="w-5 h-5 text-accent mx-auto" /></td>
                  <td className="text-center p-4"><Check className="w-5 h-5 text-accent mx-auto" /></td>
                </tr>
                <tr>
                  <td className="p-4 text-body font-medium">Stripe Integration</td>
                  <td className="text-center p-4"><Check className="w-5 h-5 text-accent mx-auto" /></td>
                  <td className="text-center p-4"><Check className="w-5 h-5 text-accent mx-auto" /></td>
                  <td className="text-center p-4"><Check className="w-5 h-5 text-accent mx-auto" /></td>
                </tr>
                <tr>
                  <td className="p-4 text-body font-medium">Analytics Dashboard</td>
                  <td className="text-center p-4 text-muted">-</td>
                  <td className="text-center p-4"><Check className="w-5 h-5 text-accent mx-auto" /></td>
                  <td className="text-center p-4"><Check className="w-5 h-5 text-accent mx-auto" /></td>
                </tr>
                <tr>
                  <td className="p-4 text-body font-medium">API Access</td>
                  <td className="text-center p-4 text-muted">-</td>
                  <td className="text-center p-4 text-muted">-</td>
                  <td className="text-center p-4"><Check className="w-5 h-5 text-accent mx-auto" /></td>
                </tr>
                <tr>
                  <td className="p-4 text-body font-medium">White-label Options</td>
                  <td className="text-center p-4 text-muted">-</td>
                  <td className="text-center p-4 text-muted">-</td>
                  <td className="text-center p-4"><Check className="w-5 h-5 text-accent mx-auto" /></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 relative">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-heading">
              Frequently Asked Questions
            </h2>
            <p className="text-xl text-body">
              Everything you need to know about our pricing
            </p>
          </div>

          <Accordion type="single" collapsible className="space-y-4">
            {faqs.map((faq, index) => (
              <AccordionItem key={index} value={`item-${index}`} className="card-glass px-6">
                <AccordionTrigger className="text-left text-heading font-semibold">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent className="text-body">
                  {faq.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-stone-200/60 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="glass-card p-12 space-y-6">
            <div className="space-y-4">
              <h2 className="text-3xl lg:text-4xl font-bold text-heading">
                Ready to Build Your SaaS?
              </h2>
              <p className="text-xl text-body">
                Join thousands of entrepreneurs who've launched their businesses with AI SaaS Factory
              </p>
            </div>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="btn-primary text-lg px-8 py-6">
                Start Your Free Trial
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
              <Button size="lg" variant="outline" className="btn-secondary text-lg px-8 py-6">
                <CreditCard className="w-5 h-5 mr-2" />
                View Live Demo
              </Button>
            </div>
            <div className="flex items-center justify-center space-x-6 pt-6">
              <div className="flex items-center space-x-2">
                <Shield className="w-5 h-5 text-accent" />
                <span className="text-sm text-body">14-day money-back guarantee</span>
              </div>
              <div className="flex items-center space-x-2">
                <CreditCard className="w-5 h-5 text-accent" />
                <span className="text-sm text-body">No credit card required</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-stone-900/95 backdrop-blur-lg text-white py-12 border-t border-stone-400/30">
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