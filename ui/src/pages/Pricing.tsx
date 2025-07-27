import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Check, 
  Sparkles, 
  Star, 
  ArrowRight, 
  CreditCard,
  Zap,
  Shield,
  Code2,
  Globe,
  BarChart3,
  Headphones
} from 'lucide-react';

interface Plan {
  name: string;
  price: number;
  period: string;
  description: string;
  features: string[];
  popular?: boolean;
  ctaText: string;
  ctaVariant: 'default' | 'outline';
}

interface FAQ {
  question: string;
  answer: string;
}

export default function Pricing() {
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly');

  const plans: Plan[] = [
    {
      name: 'Starter',
      price: billingPeriod === 'monthly' ? 29 : 290,
      period: billingPeriod === 'monthly' ? 'month' : 'year',
      description: 'Perfect for individual entrepreneurs testing ideas',
      features: [
        '1 Active Project',
        '20 Build Hours/month',
        'Basic AI Agents',
        'Community Support',
        'Standard Deployment',
        'Basic Analytics'
      ],
      ctaText: 'Start Free Trial',
      ctaVariant: 'outline'
    },
    {
      name: 'Pro',
      price: billingPeriod === 'monthly' ? 99 : 990,
      period: billingPeriod === 'monthly' ? 'month' : 'year',
      description: 'Ideal for serious entrepreneurs building multiple SaaS',
      features: [
        '5 Active Projects',
        '100 Build Hours/month',
        'Advanced AI Agents',
        'Priority Support',
        'Auto-scaling Infrastructure',
        'Advanced Analytics',
        'Custom Integrations',
        'A/B Testing Tools'
      ],
      popular: true,
      ctaText: 'Get Started',
      ctaVariant: 'default'
    },
    {
      name: 'Enterprise',
      price: billingPeriod === 'monthly' ? 299 : 2990,
      period: billingPeriod === 'monthly' ? 'month' : 'year',
      description: 'For teams building multiple high-scale SaaS products',
      features: [
        'Unlimited Projects',
        'Unlimited Build Hours',
        'Premium AI Agents',
        'Dedicated Support',
        'Enterprise Infrastructure',
        'White-label Options',
        'Custom AI Training',
        'SLA Guarantees',
        'Multi-tenant Architecture'
      ],
      ctaText: 'Contact Sales',
      ctaVariant: 'outline'
    }
  ];

  const faqs: FAQ[] = [
    {
      question: 'What are build hours?',
      answer: 'Build hours represent the time our AI agents spend developing your SaaS application. This includes design generation, code development, testing, and deployment activities.'
    },
    {
      question: 'Can I change my plan anytime?',
      answer: 'Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately, and we\'ll prorate any billing adjustments.'
    },
    {
      question: 'What happens if I exceed my build hours?',
      answer: 'If you exceed your monthly build hours, we\'ll notify you and pause builds until the next billing cycle, or you can purchase additional hours as needed.'
    },
    {
      question: 'Do I own the code generated?',
      answer: 'Absolutely! You have full ownership of all generated code, designs, and intellectual property. You can export, modify, or migrate your applications at any time.'
    },
    {
      question: 'Is there a free trial?',
      answer: 'Yes! We offer a 14-day free trial with 10 build hours so you can experience the full power of Forge95 before committing.'
    }
  ];

  const getPlanIcon = (planName: string) => {
    switch (planName) {
      case 'Starter':
        return <Zap className="w-8 h-8 text-white" />;
      case 'Pro':
        return <Star className="w-8 h-8 text-white" />;
      case 'Enterprise':
        return <Shield className="w-8 h-8 text-white" />;
      default:
        return <Sparkles className="w-8 h-8 text-white" />;
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



      {/* Hero Section */}
      <section className="relative py-20 lg:py-32">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16">
          <div className="text-center space-y-8 max-w-5xl mx-auto">
            <div className="space-y-6">
              <Badge className="glass-button">
                <Sparkles className="w-4 h-4 mr-2" />
                Simple, Transparent Pricing
              </Badge>
              <h1 className="text-4xl lg:text-6xl xl:text-7xl font-bold text-heading leading-tight">
                Choose Your{" "}
                <span className="text-accent">
                  Perfect Plan
                </span>
              </h1>
              <p className="text-xl lg:text-2xl text-body leading-relaxed max-w-4xl mx-auto">
                Start building your AI-powered SaaS business today. All plans include our complete platform with different levels of usage and support.
              </p>
            </div>

            {/* Billing Toggle */}
            <div className="flex items-center justify-center space-x-4">
              <span className={`text-sm ${billingPeriod === 'monthly' ? 'text-heading font-semibold' : 'text-body'}`}>
                Monthly
              </span>
              <button
                onClick={() => setBillingPeriod(billingPeriod === 'monthly' ? 'yearly' : 'monthly')}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 ${
                  billingPeriod === 'yearly' ? 'bg-accent' : 'bg-stone-300'
                }`}
                aria-label={`Switch to ${billingPeriod === 'monthly' ? 'yearly' : 'monthly'} billing`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    billingPeriod === 'yearly' ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
              <div className="flex items-center space-x-2">
                <span className={`text-sm ${billingPeriod === 'yearly' ? 'text-heading font-semibold' : 'text-body'}`}>
                  Yearly
                </span>
                {billingPeriod === 'yearly' && (
                  <Badge className="bg-accent text-white text-xs">
                    Save 20%
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="relative py-16">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 xl:gap-12 max-w-7xl mx-auto">
            {plans.map((plan) => (
              <Card 
                key={plan.name}
                className={`relative overflow-hidden ${
                  plan.popular 
                    ? 'card-glass border-2 border-accent shadow-2xl scale-105 lg:scale-110' 
                    : 'card-glass hover:shadow-xl transition-all duration-300 hover:scale-105'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-accent text-white shadow-lg">
                      <Star className="w-4 h-4 mr-1" />
                      Most Popular
                    </Badge>
                  </div>
                )}
                
                <CardHeader className="text-center space-y-4">
                  <div className="w-16 h-16 bg-accent-icon rounded-2xl flex items-center justify-center mx-auto shadow-lg">
                    {getPlanIcon(plan.name)}
                  </div>
                  <div>
                    <CardTitle className="text-2xl font-bold text-heading">{plan.name}</CardTitle>
                    <CardDescription className="text-body mt-2">{plan.description}</CardDescription>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-baseline justify-center space-x-1">
                      <span className="text-4xl lg:text-5xl font-bold text-accent">${plan.price}</span>
                      <span className="text-body">/{plan.period}</span>
                    </div>
                    {billingPeriod === 'yearly' && plan.name !== 'Enterprise' && (
                      <p className="text-sm text-body">
                        ${Math.round(plan.price / 12)}/month billed annually
                      </p>
                    )}
                  </div>
                </CardHeader>

                <CardContent className="space-y-6">
                  <div className="space-y-3">
                    {plan.features.map((feature, featureIndex) => (
                      <div key={featureIndex} className="flex items-start space-x-3">
                        <Check className="w-5 h-5 text-accent mt-0.5 flex-shrink-0" />
                        <span className="text-body text-sm leading-relaxed">{feature}</span>
                      </div>
                    ))}
                  </div>
                  
                  <Button 
                    className={`w-full ${
                      plan.ctaVariant === 'default' 
                        ? 'btn-primary text-lg py-6' 
                        : 'btn-secondary text-lg py-6'
                    }`}
                    onClick={() => console.log(`Selected ${plan.name} plan`)}
                  >
                    {plan.ctaText}
                    <ArrowRight className="w-5 h-5 ml-2" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Features Comparison */}
      <section className="py-16 bg-white/10 backdrop-blur-sm">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl xl:text-5xl font-bold text-heading mb-4">
              Everything You Need to Succeed
            </h2>
            <p className="text-xl lg:text-2xl text-body max-w-3xl mx-auto">
              All plans include these core features to turn your ideas into profitable SaaS businesses
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-8 max-w-6xl mx-auto">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-accent-icon rounded-2xl flex items-center justify-center mx-auto shadow-lg">
                <Code2 className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-heading">AI Development</h3>
              <p className="text-body">
                Full-stack application generation from your ideas using advanced AI agents
              </p>
            </div>

            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-accent-secondary rounded-2xl flex items-center justify-center mx-auto shadow-lg">
                <CreditCard className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-heading">Payment Integration</h3>
              <p className="text-body">
                Stripe payment processing, subscriptions, and billing automatically configured
              </p>
            </div>

            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-accent-tertiary rounded-2xl flex items-center justify-center mx-auto shadow-lg">
                <Globe className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-heading">Global Deployment</h3>
              <p className="text-body">
                Automatic deployment to Google Cloud with global CDN and auto-scaling
              </p>
            </div>

            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-gradient-to-r from-green-800 to-green-900 rounded-2xl flex items-center justify-center mx-auto shadow-lg">
                <BarChart3 className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-heading">Business Analytics</h3>
              <p className="text-body">
                Real-time dashboards, user analytics, and revenue tracking built-in
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 relative">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16">
          <div className="text-center mb-16 max-w-4xl mx-auto">
            <h2 className="text-3xl lg:text-4xl xl:text-5xl font-bold text-heading mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-xl lg:text-2xl text-body">
              Get answers to common questions about our pricing and features
            </p>
          </div>

          <div className="max-w-4xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
            {faqs.map((faq, index) => (
              <div key={index} className="glass-card p-6 space-y-4">
                <h3 className="text-lg font-semibold text-heading">{faq.question}</h3>
                <p className="text-body leading-relaxed">{faq.answer}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-green-800/20 to-green-900/20 backdrop-blur-sm">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16">
          <div className="text-center space-y-8 max-w-4xl mx-auto">
            <h2 className="text-3xl lg:text-4xl xl:text-5xl font-bold text-heading">
              Ready to Build Your SaaS?
            </h2>
            <p className="text-xl lg:text-2xl text-body">
              Join thousands of entrepreneurs who have already launched their AI-powered businesses
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button size="lg" className="btn-primary text-lg px-8 py-6">
                <Sparkles className="w-5 h-5 mr-2" />
                Start Free Trial
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
              <Button size="lg" variant="outline" className="btn-secondary text-lg px-8 py-6">
                <Headphones className="w-5 h-5 mr-2" />
                Talk to Sales
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-stone-900/95 backdrop-blur-lg text-white py-12 border-t border-stone-400/30">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16">
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