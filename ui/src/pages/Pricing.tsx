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
  Users
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import pricingData from '../data/pricing.json';

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
      
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-green-800/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-green-900/10 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

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
              <span className={`text-lg font-medium ${billingPeriod === 'monthly' ? 'text-accent' : 'text-body'}`}>
                Monthly
              </span>
                              <button
                  onClick={() => setBillingPeriod(billingPeriod === 'monthly' ? 'yearly' : 'monthly')}
                  className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 ${
                    billingPeriod === 'yearly' ? 'bg-accent' : 'bg-stone-300'
                  }`}
                  aria-label={`Switch to ${billingPeriod === 'monthly' ? 'yearly' : 'monthly'} billing`}
                >
                <span
                  className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                    billingPeriod === 'yearly' ? 'translate-x-7' : 'translate-x-1'
                  }`}
                />
              </button>
              <span className={`text-lg font-medium ${billingPeriod === 'yearly' ? 'text-accent' : 'text-body'}`}>
                Yearly
              </span>
              {billingPeriod === 'yearly' && (
                <Badge className="bg-green-800/20 text-green-800 ml-2">
                  Save 2 months
                </Badge>
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="relative py-16">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16">
          <div className="grid grid-cols-1 lg:grid-cols-3 xl:grid-cols-5 gap-8 xl:gap-6 max-w-7xl mx-auto">
            {pricingData.tiers.map((tier) => (
              <Card 
                key={tier.id}
                className="relative overflow-hidden h-full flex flex-col card-glass hover:shadow-xl transition-all duration-300 hover:scale-105"
              >
                
                <CardHeader className="text-center space-y-4 pb-4">
                  <div className="w-16 h-16 bg-gradient-to-r from-green-800 to-green-900 rounded-2xl flex items-center justify-center mx-auto shadow-lg">
                    {getPlanIcon(tier.id)}
                  </div>
                  <div className="space-y-2">
                    <CardTitle className="text-2xl font-bold text-heading">{tier.name}</CardTitle>
                    <CardDescription className="text-body text-sm leading-relaxed min-h-[2.5rem] flex items-center justify-center px-2">
                      {tier.description}
                    </CardDescription>
                  </div>
                  <div className="space-y-2 min-h-[4rem] flex flex-col justify-center">
                    <div className="flex items-baseline justify-center space-x-1">
                      {typeof getDisplayPrice(tier) === 'string' ? (
                        <span className="text-2xl lg:text-3xl font-bold text-accent">{getDisplayPrice(tier)}</span>
                      ) : (
                        <>
                          <span className="text-4xl lg:text-5xl font-bold text-accent">${getDisplayPrice(tier)}</span>
                          <span className="text-body text-sm">/{billingPeriod === 'yearly' ? 'year' : 'month'}</span>
                        </>
                      )}
                    </div>
                    {billingPeriod === 'yearly' && typeof tier.monthly === 'number' && tier.monthly > 0 && typeof tier.yearly === 'number' && (
                      <div className="space-y-1">
                        <p className="text-xs text-muted">
                          ${Math.round(tier.yearly / 12)}/month billed annually
                        </p>
                        {getYearlySavings(tier) && (
                          <p className="text-xs text-green-800 font-medium">
                            Save ${getYearlySavings(tier)?.savings}/year ({getYearlySavings(tier)?.savingsPercent}% off)
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                </CardHeader>

                <CardContent className="flex-1 flex flex-col space-y-6 pt-2">
                  <div className="flex-1 space-y-3 min-h-[10rem] flex flex-col justify-start">
                    {tier.features.map((feature, index) => (
                      <div key={index} className="flex items-center space-x-3 text-left">
                        <Check className="w-5 h-5 text-accent flex-shrink-0" />
                        <span className="text-body text-sm leading-relaxed text-left">{feature}</span>
                      </div>
                    ))}
                  </div>

                  <div className="pt-4">
                    <Button 
                      onClick={() => handleGetStarted(tier.id)}
                      className="w-full btn-primary shadow-lg hover:shadow-xl transition-all duration-300"
                      size="lg"
                    >
                      {tier.ctaText}
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative py-20">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16">
          <div className="max-w-5xl mx-auto text-center">
            <h2 className="text-3xl lg:text-5xl font-bold text-heading mb-6">
              Everything You Need to Succeed
            </h2>
            <p className="text-xl text-body mb-12">
              All plans include these core features to turn your ideas into profitable SaaS businesses
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {[
                {
                  icon: <Zap className="w-8 h-8 text-white" />,
                  title: "AI-Powered Development",
                  description: "Complete SaaS built by AI agents in under 24 hours"
                },
                {
                  icon: <Globe className="w-8 h-8 text-white" />,
                  title: "Global Deployment",
                  description: "Auto-deploy to cloud with custom domain and SSL"
                },
                {
                  icon: <CreditCard className="w-8 h-8 text-white" />,
                  title: "Payment Integration",
                  description: "Stripe checkout and subscription management included"
                },
                {
                  icon: <BarChart3 className="w-8 h-8 text-white" />,
                  title: "Analytics Dashboard",
                  description: "Real-time metrics and user behavior insights"
                },
                {
                  icon: <Shield className="w-8 h-8 text-white" />,
                  title: "Security First",
                  description: "Enterprise-grade security and compliance built-in"
                },
                {
                  icon: <Headphones className="w-8 h-8 text-white" />,
                  title: "Expert Support",
                  description: "Get help from our team when you need it most"
                }
              ].map((feature, index) => (
                <div key={index} className="card-glass p-6 text-center">
                  <div className="w-16 h-16 bg-gradient-to-r from-green-800 to-green-900 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-bold text-heading mb-2">{feature.title}</h3>
                  <p className="text-body">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="relative py-20">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl lg:text-5xl font-bold text-heading text-center mb-12">
              Frequently Asked Questions
            </h2>
            
            <div className="space-y-6">
              {[
                {
                  question: "What are build hours?",
                  answer: "Build hours represent the compute time our AI agents spend working on your project. This includes idea validation, design creation, code generation, testing, and deployment. Most simple SaaS projects use 10-20 hours, while complex ones may use 50+ hours."
                },
                {
                  question: "Can I upgrade or downgrade my plan?",
                  answer: "Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately, and you'll be charged or credited the prorated difference."
                },
                {
                  question: "What happens if I exceed my build hours?",
                  answer: `You'll be charged $${pricingData.overage.blockPrice} for every ${pricingData.overage.blockHours} additional hours. We'll notify you at 80% usage and offer auto-top-up to prevent project interruptions.`
                },
                {
                  question: "Do I retain ownership of my code and idea?",
                  answer: "Absolutely! You retain 100% ownership of your idea, code, and business. Forge95 just provides the tools and AI agents to help you build it."
                },
                {
                  question: "What's included in the Free plan?",
                  answer: "The Free plan lets you test our platform with 1 project, 5 build hours, and a demo deployment. Perfect for exploring how our AI agents work before committing to a paid plan."
                }
              ].map((faq, index) => (
                <div key={index} className="card-glass p-6">
                  <h3 className="text-xl font-bold text-heading mb-3">{faq.question}</h3>
                  <p className="text-body">{faq.answer}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative py-16 border-t border-stone-300/50">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16">
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              <div className="md:col-span-2">
                <div className="flex items-center space-x-2 mb-4">
                  <div className="w-10 h-10 bg-gradient-to-r from-green-800 to-green-900 rounded-xl flex items-center justify-center shadow-lg">
                    <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1H9V3H7V1H5V7L1 9V11L7 13V21H9V19H11V21H13V19H15V21H17V13L23 11V9H21ZM19 10.5L17 11.5V17H15V15H13V17H11V15H9V17H7V11.5L5 10.5V9.5L7 8.5V7H9V9H11V7H13V9H15V7H17V8.5L19 9.5V10.5Z"/>
                    </svg>
                  </div>
                  <span className="text-xl font-bold text-stone-900">Forge95</span>
                </div>
                <p className="text-stone-600 max-w-md">
                  Turn any idea into a live SaaS business – no code required. Built by AI agents, deployed globally, ready for customers.
                </p>
              </div>
              
              <div>
                <h4 className="font-semibold text-stone-900 mb-4">Product</h4>
                <ul className="space-y-2 text-stone-600">
                  <li><a href="/pricing" className="hover:text-stone-900 transition-colors">Pricing</a></li>
                  <li><a href="/faq" className="hover:text-stone-900 transition-colors">FAQ</a></li>
                  <li><a href="/signin" className="hover:text-stone-900 transition-colors">Sign In</a></li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-semibold text-stone-900 mb-4">Legal</h4>
                <ul className="space-y-2 text-stone-600">
                  <li><a href="/privacy" className="hover:text-stone-900 transition-colors">Privacy Policy</a></li>
                  <li><a href="/terms" className="hover:text-stone-900 transition-colors">Terms of Service</a></li>
                  <li><a href="/dpa" className="hover:text-stone-900 transition-colors">DPA</a></li>
                </ul>
              </div>
            </div>
            
            <div className="border-t border-stone-300/50 mt-12 pt-8 text-center">
              <p className="text-stone-500">
                &copy; 2025 Forge95. Turn any idea into a live SaaS business – no code required.
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
} 