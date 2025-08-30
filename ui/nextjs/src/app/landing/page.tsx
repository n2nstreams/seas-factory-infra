"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/features/ui/accordion";
import { Separator } from "@/components/ui/separator";
import { Input } from "@/components/ui/input";
import { Check, Code2, Shield, TrendingUp, Star, ArrowRight, Sparkles, Layers, Cpu, Wrench, Clock, Zap, Lightbulb, Rocket, Brain, Palette, TestTube } from "lucide-react";
import { useState, useEffect } from "react";
import Link from "next/link";

export default function Landing() {
  const [currentView, setCurrentView] = useState(0); // 0 = assembly line, 1 = dashboard
  const [assemblyStage, setAssemblyStage] = useState(0); // 0 = idea, 1 = design, 2 = code, 3 = dashboard
  const [email, setEmail] = useState("");

  // Switch between assembly line and dashboard every 8 seconds
  useEffect(() => {
    const viewInterval = setInterval(() => {
      setCurrentView(prev => (prev + 1) % 2);
    }, 8000);

    return () => clearInterval(viewInterval);
  }, []);

  // Assembly line animation stages every 1.5 seconds when showing assembly line
  useEffect(() => {
    if (currentView === 0) {
      const stageInterval = setInterval(() => {
        setAssemblyStage(prev => (prev + 1) % 4);
      }, 1500);

      return () => clearInterval(stageInterval);
    }
  }, [currentView]);

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Development',
      description: 'Intelligent agents that understand your requirements and generate production-ready code.'
    },
    {
      icon: Code2,
      title: 'Code Generation',
      description: 'Automated code generation for multiple languages and frameworks with best practices.'
    },
    {
      icon: Palette,
      title: 'Design System',
      description: 'AI-generated UI/UX designs with glassmorphism aesthetics and responsive layouts.'
    },
    {
      icon: TestTube,
      title: 'Quality Assurance',
      description: 'Automated testing and validation to ensure code quality and reliability.'
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Optimized performance with Next.js 15, Server Components, and modern React patterns.'
    },
    {
      icon: Shield,
      title: 'Enterprise Security',
      description: 'Built-in authentication, authorization, and data isolation for multi-tenant applications.'
    }
  ];

  const testimonials = [
    {
      name: 'Sarah Chen',
      role: 'Senior Developer',
      company: 'TechCorp',
      content: 'AI SaaS Factory reduced our development time by 70%. The AI agents are incredibly intelligent!',
      rating: 5
    },
    {
      name: 'Marcus Rodriguez',
      role: 'CTO',
      company: 'StartupXYZ',
      content: 'We went from idea to MVP in 2 weeks. This platform is a game-changer for rapid development.',
      rating: 5
    },
    {
      name: 'Emily Watson',
      role: 'Product Manager',
      company: 'InnovateLab',
      content: 'The design system is beautiful and the code quality is production-ready. Highly recommended!',
      rating: 5
    }
  ];

  const AssemblyLineVisual = () => (
    <div className="relative w-full h-96 bg-gradient-to-r from-stone-800/25 to-stone-700/30 backdrop-blur-xl rounded-3xl p-8 shadow-2xl border border-stone-400/40 overflow-hidden">
      {/* Assembly Line Track */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="relative w-full h-2 bg-stone-300/40 rounded-full overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-stone-800/60 to-stone-900/60 rounded-full animate-pulse"></div>
        </div>
      </div>

      {/* Assembly Stations */}
      <div className="relative z-10 flex justify-between items-center h-full">
        {/* Station 1: Idea Input */}
        <div className="flex flex-col items-center space-y-4">
          <div className="relative flex flex-col items-center">
            {assemblyStage === 0 && (
              <div className="mb-2 text-xs font-bold text-stone-800 animate-bounce whitespace-nowrap">
                Idea
              </div>
            )}
            <div className={`w-16 h-16 bg-gradient-to-br from-stone-800 to-stone-900 rounded-xl shadow-2xl transition-all duration-500 ${
              assemblyStage === 0 ? 'animate-bounce scale-110 shadow-stone-800/50' : 'scale-100'
            }`}>
              <div className="w-full h-full bg-gradient-to-r from-stone-700/80 to-stone-800/80 rounded-xl flex items-center justify-center">
                <Sparkles className="w-8 h-8 text-white animate-pulse" />
              </div>
            </div>
          </div>
          <div className="w-8 h-8 bg-stone-600/60 rounded-full flex items-center justify-center">
            <div className="w-3 h-3 bg-stone-800 rounded-full animate-pulse"></div>
          </div>
        </div>

        {/* Station 2: Design */}
        <div className="flex flex-col items-center space-y-4">
          <div className="relative flex flex-col items-center">
            {assemblyStage === 1 && (
              <div className="mb-2 text-xs font-bold text-stone-700 animate-bounce whitespace-nowrap">
                Design
              </div>
            )}
            <div className={`w-16 h-16 bg-gradient-to-br from-stone-700 to-stone-800 rounded-xl shadow-2xl transition-all duration-500 ${
              assemblyStage === 1 ? 'animate-bounce scale-110 shadow-stone-600/50' : 'scale-100'
            }`}>
              <div className="w-full h-full bg-gradient-to-r from-stone-600/80 to-stone-700/80 rounded-xl flex items-center justify-center">
                <Layers className="w-8 h-8 text-white" />
              </div>
              {assemblyStage === 1 && (
                <div className="absolute inset-0 bg-white/20 rounded-xl animate-ping"></div>
              )}
            </div>
          </div>
          <div className="w-8 h-8 bg-stone-600/60 rounded-full flex items-center justify-center">
            <Wrench className="w-4 h-4 text-stone-700" />
          </div>
        </div>

        {/* Station 3: Code */}
        <div className="flex flex-col items-center space-y-4">
          <div className="relative flex flex-col items-center">
            {assemblyStage === 2 && (
              <div className="mb-2 text-xs font-bold text-stone-700 animate-bounce whitespace-nowrap">
                Code
              </div>
            )}
            <div className={`w-16 h-16 bg-gradient-to-br from-stone-700 to-stone-800 rounded-xl shadow-2xl transition-all duration-500 ${
              assemblyStage === 2 ? 'animate-bounce scale-110 shadow-stone-600/50' : 'scale-100'
            }`}>
              <div className="w-full h-full bg-gradient-to-r from-stone-600/80 to-stone-700/80 rounded-xl flex items-center justify-center">
                <Code2 className="w-8 h-8 text-white" />
              </div>
              {assemblyStage === 2 && (
                <div className="absolute inset-0 bg-white/20 rounded-xl animate-ping"></div>
              )}
            </div>
          </div>
          <div className="w-8 h-8 bg-stone-600/60 rounded-full flex items-center justify-center">
            <Cpu className="w-4 h-4 text-stone-700" />
          </div>
        </div>

        {/* Station 4: Dashboard */}
        <div className="flex flex-col items-center space-y-4">
          <div className="relative flex flex-col items-center">
            {assemblyStage === 3 && (
              <div className="mb-2 text-xs font-bold text-stone-700 animate-bounce whitespace-nowrap">
                Launch
              </div>
            )}
            <div className={`w-16 h-16 bg-gradient-to-br from-stone-700 to-stone-800 rounded-xl shadow-2xl transition-all duration-500 ${
              assemblyStage === 3 ? 'animate-bounce scale-110 shadow-stone-600/50' : 'scale-100'
            }`}>
              <div className="w-full h-full bg-gradient-to-r from-stone-600/80 to-stone-700/80 rounded-xl flex items-center justify-center">
                <Rocket className="w-8 h-8 text-white" />
              </div>
              {assemblyStage === 3 && (
                <div className="absolute inset-0 bg-white/20 rounded-xl animate-ping"></div>
              )}
            </div>
          </div>
          <div className="w-8 h-8 bg-stone-600/60 rounded-full flex items-center justify-center">
            <TrendingUp className="w-4 h-4 text-stone-700" />
          </div>
        </div>
      </div>
    </div>
  );

  const DashboardVisual = () => (
    <div className="relative w-full h-96 bg-gradient-to-r from-stone-800/25 to-stone-700/30 backdrop-blur-xl rounded-3xl p-8 shadow-2xl border border-stone-400/40 overflow-hidden">
      <div className="relative z-10 h-full flex flex-col justify-center items-center space-y-6">
        <div className="text-center space-y-4">
          <div className="w-20 h-20 bg-gradient-to-br from-stone-600 to-stone-800 rounded-2xl shadow-2xl flex items-center justify-center mx-auto">
            <Lightbulb className="w-10 h-10 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-stone-900">Your SaaS Dashboard</h3>
          <p className="text-stone-700 max-w-md">
            Monitor performance, manage users, and scale your business with real-time insights
          </p>
        </div>
        
        <div className="grid grid-cols-3 gap-4 w-full max-w-md">
          <div className="bg-white/20 backdrop-blur-sm rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-stone-800">1.2K</div>
            <div className="text-sm text-stone-600">Users</div>
          </div>
          <div className="bg-white/20 backdrop-blur-sm rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-stone-800">$8.5K</div>
            <div className="text-sm text-stone-600">Revenue</div>
          </div>
          <div className="bg-white/20 backdrop-blur-sm rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-stone-800">99.9%</div>
            <div className="text-sm text-stone-600">Uptime</div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-stone-50 to-stone-100">
      {/* Navigation Bar */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-stone-300/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-3 sm:py-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-r from-stone-700 to-stone-800 rounded-xl flex items-center justify-center shadow-lg">
                <Sparkles className="w-4 h-4 sm:w-6 sm:h-6 text-white" />
              </div>
              <span className="text-lg sm:text-xl font-bold text-stone-900">AI SaaS Factory</span>
            </div>
            
            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center space-x-8">
              <a href="#features" className="text-stone-700 hover:text-stone-900 transition-colors font-medium">Features</a>
              <a href="#how-it-works" className="text-stone-700 hover:text-stone-900 transition-colors font-medium">How It Works</a>
              <a href="#testimonials" className="text-stone-700 hover:text-stone-900 transition-colors font-medium">Testimonials</a>
              <a href="#faq" className="text-stone-700 hover:text-stone-900 transition-colors font-medium">FAQ</a>
            </div>
            
            {/* Desktop Buttons */}
            <div className="hidden md:flex items-center space-x-3 sm:space-x-4">
              <Button asChild variant="ghost" className="text-stone-700 hover:text-stone-900 text-sm sm:text-base">
                <Link href="/signin">Sign In</Link>
              </Button>
              <Button asChild size="sm" className="bg-stone-700 hover:bg-stone-800 text-sm sm:text-base">
                <Link href="/signup">Get Started</Link>
              </Button>
            </div>

            {/* Mobile Menu Button */}
            <div className="lg:hidden">
              <Button variant="ghost" size="sm" className="p-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </Button>
            </div>
          </div>

          {/* Mobile Navigation Menu */}
          <div className="lg:hidden border-t border-stone-300/50 py-4">
            <div className="flex flex-col space-y-3">
              <a href="#features" className="text-stone-700 hover:text-stone-900 transition-colors font-medium py-2">Features</a>
              <a href="#how-it-works" className="text-stone-700 hover:text-stone-900 transition-colors font-medium py-2">How It Works</a>
              <a href="#testimonials" className="text-stone-700 hover:text-stone-900 transition-colors font-medium py-2">Testimonials</a>
              <a href="#faq" className="text-stone-700 hover:text-stone-900 transition-colors font-medium py-2">FAQ</a>
              <div className="flex flex-col space-y-2 pt-2">
                <Button asChild variant="ghost" className="text-stone-700 hover:text-stone-900 justify-start">
                  <Link href="/signin">Sign In</Link>
                </Button>
                <Button asChild className="bg-stone-700 hover:bg-stone-800 justify-start">
                  <Link href="/signup">Get Started</Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-stone-600/20 to-stone-800/20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20 lg:py-24 xl:py-32">
          <div className="text-center">
            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold text-stone-900 mb-4 sm:mb-6 leading-tight">
              Transform Your Idea into a{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-stone-700 to-stone-800">
                Production-Ready SaaS
              </span>{" "}
              – Automatically
            </h1>
            <p className="text-lg sm:text-xl md:text-2xl text-stone-700 mb-6 sm:mb-8 max-w-2xl sm:max-w-3xl mx-auto px-4 sm:px-0 leading-relaxed">
              Submit your SaaS concept and watch our AI agents design, develop, and deploy your complete application. From idea to paying customers in days, not months.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center items-center px-4 sm:px-0">
              <Button asChild size="lg" className="w-full sm:w-auto bg-stone-700 hover:bg-stone-800 text-base sm:text-lg px-6 sm:px-8 py-3 sm:py-4">
                <Link href="/signup">
                  Get Started Free
                  <ArrowRight className="ml-2 h-4 w-4 sm:h-5 sm:w-5" />
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="w-full sm:w-auto border-stone-300 text-stone-700 hover:bg-stone-50 text-base sm:text-lg px-6 sm:px-8 py-3 sm:py-4">
                <Link href="/signin">
                  Sign In
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Assembly Line Section */}
      <section id="how-it-works" className="py-16 sm:py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12 sm:mb-16">
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-stone-900 mb-3 sm:mb-4">
              Watch Your Idea Come to Life
            </h2>
            <p className="text-lg sm:text-xl text-stone-700 max-w-2xl mx-auto px-4 sm:px-0">
              Our AI assembly line transforms your concept through design, development, and deployment in real-time
            </p>
          </div>
          
          <div className="mb-8">
            {currentView === 0 ? <AssemblyLineVisual /> : <DashboardVisual />}
          </div>

          {/* Email Capture Form */}
          <div className="bg-white/25 backdrop-blur-lg border border-stone-400/40 rounded-2xl p-4 sm:p-6 shadow-xl max-w-2xl mx-auto">
            <h3 className="text-lg sm:text-xl font-semibold text-stone-900 mb-3 sm:mb-4 text-center">
              Ready to Build Your SaaS?
            </h3>
            <p className="text-stone-700 mb-4 sm:mb-6 text-center text-sm sm:text-base">
              Get early access and be the first to know when we launch
            </p>
            <div className="flex flex-col sm:flex-row gap-3">
              <Input
                type="email"
                placeholder="Enter your email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="flex-1 border-stone-300 focus:border-stone-500 text-sm sm:text-base"
              />
              <Button className="bg-stone-700 hover:bg-stone-800 whitespace-nowrap text-sm sm:text-base">
                Get Early Access
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-16 sm:py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12 sm:mb-16">
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-stone-900 mb-3 sm:mb-4">
              Powered by AI, Built for Developers
            </h2>
            <p className="text-lg sm:text-xl text-stone-700 max-w-2xl mx-auto px-4 sm:px-0">
              Our AI agents work together to handle every aspect of SaaS development, from concept to deployment.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="glass-card hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
                <CardHeader className="text-center p-4 sm:p-6">
                  <div className="w-12 h-12 sm:w-16 sm:h-16 bg-stone-100 rounded-full flex items-center justify-center mx-auto mb-3 sm:mb-4">
                    <feature.icon className="h-6 w-6 sm:h-8 sm:w-8 text-stone-700" />
                  </div>
                  <CardTitle className="text-lg sm:text-xl text-stone-900">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent className="p-4 sm:p-6">
                  <CardDescription className="text-stone-600 text-center text-sm sm:text-base">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-16 sm:py-20 px-4 sm:px-6 lg:px-8 bg-white/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12 sm:mb-16">
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-stone-900 mb-3 sm:mb-4">
              Trusted by Developers Worldwide
            </h2>
            <p className="text-lg sm:text-xl text-stone-700 px-4 sm:px-0">
              See what our users are saying about AI SaaS Factory
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="glass-card">
                <CardContent className="p-4 sm:p-6">
                  <div className="flex items-center mb-3 sm:mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="h-4 w-4 sm:h-5 sm:w-5 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <p className="text-stone-700 mb-3 sm:mb-4 italic text-sm sm:text-base">"{testimonial.content}"</p>
                  <div>
                    <p className="font-semibold text-stone-900 text-sm sm:text-base">{testimonial.name}</p>
                    <p className="text-xs sm:text-sm text-stone-600">{testimonial.role} at {testimonial.company}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-16 sm:py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12 sm:mb-16">
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-stone-900 mb-3 sm:mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-lg sm:text-xl text-stone-700 px-4 sm:px-0">
              Everything you need to know about AI SaaS Factory
            </p>
          </div>

          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="item-1">
              <AccordionTrigger className="text-left text-base sm:text-lg font-semibold text-stone-900">
                How does the AI assembly line work?
              </AccordionTrigger>
              <AccordionContent className="text-stone-700 text-sm sm:text-base">
                Our AI agents work in sequence: first analyzing your idea, then designing the UI/UX, generating production-ready code, and finally deploying to production. Each stage is automated and optimized for your specific requirements.
              </AccordionContent>
            </AccordionItem>
            
            <AccordionItem value="item-2">
              <AccordionTrigger className="text-left text-base sm:text-lg font-semibold text-stone-900">
                What technologies do you support?
              </AccordionTrigger>
              <AccordionContent className="text-stone-700 text-sm sm:text-base">
                We support modern web technologies including React, Next.js, Node.js, Python, and more. Our AI agents choose the best tech stack for your specific use case and requirements.
              </AccordionContent>
            </AccordionItem>
            
            <AccordionItem value="item-3">
              <AccordionTrigger className="text-left text-base sm:text-lg font-semibold text-stone-900">
                How long does it take to build a SaaS?
              </AccordionTrigger>
              <AccordionContent className="text-stone-700 text-sm sm:text-base">
                From idea submission to production deployment typically takes 2-4 weeks, depending on complexity. Our AI agents work 24/7 to ensure rapid development and deployment.
              </AccordionContent>
            </AccordionItem>
            
            <AccordionItem value="item-4">
              <AccordionTrigger className="text-left text-base sm:text-lg font-semibold text-stone-900">
                Is the code production-ready?
              </AccordionTrigger>
              <AccordionContent className="text-stone-700 text-sm sm:text-base">
                Absolutely! Our AI agents follow industry best practices, include comprehensive testing, security measures, and are optimized for production environments. You get enterprise-grade code quality.
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 sm:py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-stone-900 mb-4 sm:mb-6">
            Ready to Build the Future?
          </h2>
          <p className="text-lg sm:text-xl text-stone-700 mb-6 sm:mb-8 px-4 sm:px-0">
            Join thousands of developers who are already using AI SaaS Factory to build amazing applications.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center items-center px-4 sm:px-0">
            <Button asChild size="lg" className="w-full sm:w-auto bg-stone-700 hover:bg-stone-800 text-base sm:text-lg px-6 sm:px-8 py-3 sm:py-4">
              <Link href="/signup">
                Start Building Now
                <ArrowRight className="ml-2 h-4 w-4 sm:h-5 sm:w-5" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="w-full sm:w-auto border-stone-300 text-stone-700 hover:bg-stone-50 text-base sm:text-lg px-6 sm:px-8 py-3 sm:py-4">
              <Link href="/signin">
                Sign In
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-stone-900 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h3 className="text-xl sm:text-2xl font-bold mb-3 sm:mb-4">AI SaaS Factory</h3>
          <p className="text-stone-300 mb-4 sm:mb-6 text-sm sm:text-base">
            Modern, Clean Architecture for AI-Powered SaaS Applications
          </p>
          <div className="flex flex-col sm:flex-row justify-center space-y-2 sm:space-y-0 sm:space-x-6 text-stone-300 text-sm sm:text-base">
            <Link href="/signin" className="hover:text-white transition-colors">Sign In</Link>
            <Link href="/signup" className="hover:text-white transition-colors">Sign Up</Link>
            <Link href="/pricing" className="hover:text-white transition-colors">Pricing</Link>
          </div>
          <div className="mt-6 sm:mt-8 pt-6 sm:pt-8 border-t border-stone-800 text-stone-400 text-xs sm:text-sm">
            <p>&copy; 2025 AI SaaS Factory. Built with Next.js 15 and AI agents.</p>
          </div>
        </div>
      </footer>
    </div>
  );
} 