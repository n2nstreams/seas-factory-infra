import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Separator } from "@/components/ui/separator";
import { Check, Code2, CreditCard, Shield, TrendingUp, Users, Zap, Star, ArrowRight, Sparkles, Layers, Globe, Cpu, Wrench } from "lucide-react";
import { useState, useEffect } from "react";

export default function Landing() {
  const [currentView, setCurrentView] = useState(0); // 0 = assembly line, 1 = dashboard
  const [assemblyStage, setAssemblyStage] = useState(0); // 0 = idea, 1 = design, 2 = code, 3 = dashboard

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

  const AssemblyLineVisual = () => (
    <div className="relative w-full h-96 bg-gradient-to-r from-green-800/25 to-stone-700/30 backdrop-blur-xl rounded-3xl p-8 shadow-2xl border border-stone-400/40 overflow-hidden">
      {/* Assembly Line Track */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="relative w-full h-2 bg-stone-300/40 rounded-full overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-green-800/60 to-green-900/60 rounded-full animate-pulse"></div>
        </div>
      </div>

      {/* Assembly Stations */}
      <div className="relative z-10 flex justify-between items-center h-full">
                 {/* Station 1: Idea Input */}
         <div className="flex flex-col items-center space-y-4">
           <div className="relative flex flex-col items-center">
             {assemblyStage === 0 && (
               <div className="mb-2 text-xs font-bold text-green-800 animate-bounce whitespace-nowrap">
                 Idea
               </div>
             )}
             <div className={`w-16 h-16 bg-gradient-to-br from-green-800 to-green-900 rounded-xl shadow-2xl transition-all duration-500 ${
               assemblyStage === 0 ? 'animate-bounce scale-110 shadow-green-800/50' : 'scale-100'
             }`}>
               <div className="w-full h-full bg-gradient-to-r from-green-700/80 to-green-800/80 rounded-xl flex items-center justify-center">
                 <Sparkles className="w-8 h-8 text-white animate-pulse" />
               </div>
             </div>
           </div>
           <div className="w-8 h-8 bg-stone-600/60 rounded-full flex items-center justify-center">
             <div className="w-3 h-3 bg-green-800 rounded-full animate-pulse"></div>
           </div>
         </div>

         {/* Station 2: Design */}
         <div className="flex flex-col items-center space-y-4">
           <div className="relative flex flex-col items-center">
             {assemblyStage === 1 && (
               <div className="mb-2 text-xs font-bold text-slate-700 animate-bounce whitespace-nowrap">
                 Design
               </div>
             )}
             <div className={`w-16 h-16 bg-gradient-to-br from-slate-700 to-green-800 rounded-xl shadow-2xl transition-all duration-500 ${
               assemblyStage === 1 ? 'animate-bounce scale-110 shadow-slate-600/50' : 'scale-100'
             }`}>
               <div className="w-full h-full bg-gradient-to-r from-slate-600/80 to-green-700/80 rounded-xl flex items-center justify-center">
                 <Layers className="w-8 h-8 text-white" />
               </div>
               {assemblyStage === 1 && (
                 <div className="absolute inset-0 bg-white/20 rounded-xl animate-ping"></div>
               )}
             </div>
           </div>
           <div className="w-8 h-8 bg-stone-600/60 rounded-full flex items-center justify-center">
             <Wrench className="w-4 h-4 text-slate-700" />
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
             <div className={`w-16 h-16 bg-gradient-to-br from-stone-700 to-green-800 rounded-xl shadow-2xl transition-all duration-500 ${
               assemblyStage === 2 ? 'animate-bounce scale-110 shadow-stone-600/50' : 'scale-100'
             }`}>
               <div className="w-full h-full bg-gradient-to-r from-stone-600/80 to-green-700/80 rounded-xl flex items-center justify-center">
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

         {/* Station 4: Live Business */}
         <div className="flex flex-col items-center space-y-4">
           <div className="relative flex flex-col items-center">
             {assemblyStage === 3 && (
               <div className="mb-2 text-xs font-bold text-green-800 animate-bounce whitespace-nowrap">
                 Live Business
               </div>
             )}
             <div className={`w-16 h-16 bg-gradient-to-br from-green-800 to-green-900 rounded-xl shadow-2xl transition-all duration-500 ${
               assemblyStage === 3 ? 'animate-bounce scale-110 shadow-green-800/50' : 'scale-100'
             }`}>
               <div className="w-full h-full bg-gradient-to-r from-green-700/80 to-green-800/80 rounded-xl flex items-center justify-center">
                 <TrendingUp className="w-8 h-8 text-white" />
               </div>
               {assemblyStage === 3 && (
                 <div className="absolute inset-0 bg-white/20 rounded-xl animate-ping"></div>
               )}
             </div>
           </div>
           <div className="w-8 h-8 bg-stone-600/60 rounded-full flex items-center justify-center">
             <div className="w-3 h-3 bg-green-800 rounded-full animate-pulse"></div>
           </div>
         </div>
       </div>

      {/* Progress Indicator */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
        {[0, 1, 2, 3].map((stage) => (
          <div
            key={stage}
            className={`w-2 h-2 rounded-full transition-all duration-300 ${
              assemblyStage >= stage ? 'bg-green-800' : 'bg-stone-400/40'
            }`}
          />
        ))}
      </div>

      {/* AI Factory Label */}
      <div className="absolute top-4 left-1/2 transform -translate-x-1/2 text-center">
        <div className="bg-white/20 backdrop-blur-sm rounded-full px-4 py-2 border border-stone-400/40">
          <span className="text-sm font-bold text-stone-800">AI Factory</span>
        </div>
      </div>
    </div>
  );

  const DashboardVisual = () => (
    <div className="bg-gradient-to-r from-green-800/25 to-stone-700/30 backdrop-blur-xl rounded-3xl p-8 shadow-2xl border border-stone-400/40">
      <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-8 space-y-6 shadow-inner border border-stone-300/60">
        <div className="flex items-center space-x-3">
          <div className="w-4 h-4 bg-green-800 rounded-full animate-pulse shadow-lg"></div>
          <span className="text-sm font-semibold text-stone-900">Live Business Dashboard</span>
          <Badge className="bg-stone-300/60 text-stone-800 text-xs">Active</Badge>
        </div>
        <div className="space-y-4">
          <div className="flex justify-between items-center p-4 bg-stone-200/60 rounded-xl border border-stone-300/60">
            <span className="text-sm text-stone-800 font-medium">Monthly Revenue</span>
            <span className="text-3xl font-bold text-green-800">$12,847</span>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-stone-100/70 rounded-xl border border-stone-300/50">
              <div className="text-sm text-stone-700 font-medium mb-1">Active Users</div>
              <div className="text-2xl font-bold text-green-800">1,234</div>
            </div>
            <div className="p-4 bg-neutral-100/70 rounded-xl border border-stone-300/50">
              <div className="text-sm text-stone-700 font-medium mb-1">Uptime</div>
              <div className="text-2xl font-bold text-green-800">99.9%</div>
            </div>
          </div>
        </div>
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-stone-700">Growth Rate</span>
            <span className="text-green-800 font-semibold">+23.5%</span>
          </div>
          <div className="w-full bg-stone-300/60 rounded-full h-3 overflow-hidden">
            <div className="bg-gradient-to-r from-green-800 to-green-900 h-3 rounded-full w-3/4 animate-pulse shadow-inner"></div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-stone-100 via-neutral-200 to-stone-200 relative overflow-hidden">
      {/* Glassmorphism Background Elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-br from-green-800/20 to-green-900/25 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-40 right-32 w-80 h-80 bg-gradient-to-bl from-slate-700/20 to-green-800/25 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 left-1/3 w-64 h-64 bg-gradient-to-tr from-stone-600/20 to-green-700/25 rounded-full blur-3xl animate-pulse delay-2000"></div>
        <div className="absolute bottom-32 right-20 w-72 h-72 bg-gradient-to-tl from-green-800/20 to-stone-700/25 rounded-full blur-3xl animate-pulse delay-3000"></div>
      </div>

      {/* Navigation */}
      <nav className="bg-white/15 backdrop-blur-md border-b border-stone-400/30 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-r from-green-800 to-green-900 rounded-xl flex items-center justify-center shadow-lg backdrop-blur-sm">
                <Code2 className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-stone-900">AI SaaS Factory</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-stone-700 hover:text-stone-900 transition-colors font-medium">Features</a>
              <a href="#pricing" className="text-stone-700 hover:text-stone-900 transition-colors font-medium">Pricing</a>
              <a href="#faq" className="text-stone-700 hover:text-stone-900 transition-colors font-medium">FAQ</a>
              <Button size="sm" className="bg-gradient-to-r from-green-800 to-green-900 hover:from-green-900 hover:to-stone-800 shadow-lg backdrop-blur-sm border border-stone-400/40">
                Launch Your Business
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8 relative z-10">
              <div className="space-y-6">
                <Badge className="bg-stone-300/60 backdrop-blur-sm text-stone-800 border border-stone-400/50 shadow-lg">
                  <Sparkles className="w-4 h-4 mr-2" />
                  Powered by AI
                </Badge>
                <h1 className="text-4xl lg:text-6xl font-bold text-stone-900 leading-tight">
                  Go From Idea to{" "}
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-800 to-green-900">
                    Live Business
                  </span>{" "}
                  in Hours.
                </h1>
                <p className="text-xl text-stone-700 leading-relaxed">
                  Describe your SaaS idea. Our AI factory builds the app, configures payments, and automates your operations, launching a ready-to-run business on Google Cloud.
                </p>
              </div>
              <div className="flex flex-col sm:flex-row gap-4">
                <Button size="lg" className="bg-gradient-to-r from-green-800 to-green-900 hover:from-green-900 hover:to-stone-800 text-lg px-8 py-6 shadow-xl backdrop-blur-sm border border-stone-400/40">
                  Start My Business
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
                <Button size="lg" variant="outline" className="text-lg px-8 py-6 bg-white/25 backdrop-blur-sm border border-stone-400/50 text-stone-800 hover:bg-white/40">
                  Watch Demo
                </Button>
              </div>
            </div>
            <div className="relative">
              <div className="transition-opacity duration-1000">
                {currentView === 0 ? <AssemblyLineVisual /> : <DashboardVisual />}
              </div>
              
              {/* View Indicator */}
              <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 flex space-x-2">
                <div className={`w-2 h-2 rounded-full transition-all duration-300 ${currentView === 0 ? 'bg-green-800' : 'bg-stone-400/60'}`}></div>
                <div className={`w-2 h-2 rounded-full transition-all duration-300 ${currentView === 1 ? 'bg-green-800' : 'bg-stone-400/60'}`}></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Social Proof Banner */}
      <section className="py-16 bg-white/15 backdrop-blur-md border-y border-stone-400/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center space-y-8">
            <p className="text-stone-700 font-semibold">Built on the world's most trusted platforms</p>
            <div className="flex justify-center items-center space-x-16 opacity-80">
              <div className="text-2xl font-bold text-stone-800">Google Cloud</div>
              <div className="text-2xl font-bold text-stone-800">Stripe</div>
              <div className="text-2xl font-bold text-stone-800">OpenAI</div>
              <div className="text-2xl font-bold text-stone-800">GitHub</div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Highlights */}
      <section id="features" className="py-20 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-stone-900">
              More Than Code, A Complete Business System
            </h2>
            <p className="text-xl text-stone-700 max-w-3xl mx-auto">
              We don't just build apps - we launch complete businesses with everything you need to start selling immediately.
            </p>
          </div>
          
          <div className="grid lg:grid-cols-3 gap-8">
            <Card className="bg-white/25 backdrop-blur-lg border border-stone-400/40 hover:border-stone-500/60 transition-all duration-300 hover:shadow-xl hover:bg-white/35">
              <CardHeader>
                <div className="w-14 h-14 bg-gradient-to-r from-green-800 to-green-900 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
                  <CreditCard className="w-7 h-7 text-white" />
                </div>
                <CardTitle className="text-xl text-stone-900">Automated Billing, Instantly</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-stone-700">
                  Don't spend weeks wrestling with payment APIs. Your business launches with Stripe Checkout fully integrated for subscriptions, complete with a customer portal for your new users.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-white/25 backdrop-blur-lg border border-stone-400/40 hover:border-stone-500/60 transition-all duration-300 hover:shadow-xl hover:bg-white/35">
              <CardHeader>
                <div className="w-14 h-14 bg-gradient-to-r from-slate-700 to-green-800 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
                  <Shield className="w-7 h-7 text-white" />
                </div>
                <CardTitle className="text-xl text-stone-900">Your AI Operations Team</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-stone-700">
                  Launch with a built-in operations team. Our AIOpsAgent and CostGuardAgent monitor for issues, manage your cloud budget, and alert you proactively, saving you time and preventing surprises.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-white/25 backdrop-blur-lg border border-stone-400/40 hover:border-stone-500/60 transition-all duration-300 hover:shadow-xl hover:bg-white/35">
              <CardHeader>
                <div className="w-14 h-14 bg-gradient-to-r from-stone-700 to-green-800 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
                  <Code2 className="w-7 h-7 text-white" />
                </div>
                <CardTitle className="text-xl text-stone-900">Full Ownership & Control</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-stone-700">
                  It's your business, you own everything. Get the full application source code, customer data, and the freedom to extend or migrate your service at any time. No vendor lock-in.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-gradient-to-br from-stone-200/60 to-neutral-200/60 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-stone-900">
              Choose Your Level of Automation
            </h2>
            <p className="text-xl text-stone-700">
              Start with launching your business, then scale with advanced automation
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Launch Tier */}
            <Card className="bg-white/35 backdrop-blur-lg border border-stone-400/60 hover:border-stone-500/80 transition-all duration-300 hover:shadow-xl hover:bg-white/45">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl font-bold text-stone-900">Launch</CardTitle>
                <CardDescription className="text-stone-700">Launch a transactable business</CardDescription>
                <div className="mt-6 p-4 bg-stone-200/60 rounded-xl border border-stone-300/60">
                  <span className="text-4xl font-bold text-green-800">$49</span>
                  <span className="text-stone-700">/month</span>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center space-x-3 p-2 rounded-lg bg-stone-200/40">
                    <Check className="w-5 h-5 text-green-800" />
                    <span className="text-sm text-stone-800">Full Idea-to-Deploy Pipeline</span>
                  </div>
                  <div className="flex items-center space-x-3 p-2 rounded-lg bg-stone-200/40">
                    <Check className="w-5 h-5 text-green-800" />
                    <span className="text-sm text-stone-800">Stripe Payment Integration</span>
                  </div>
                  <div className="flex items-center space-x-3 p-2 rounded-lg bg-stone-200/40">
                    <Check className="w-5 h-5 text-green-800" />
                    <span className="text-sm text-stone-800">Basic Monitoring</span>
                  </div>
                  <div className="flex items-center space-x-3 p-2 rounded-lg">
                    <span className="text-sm text-stone-700">Community Forum Support</span>
                  </div>
                </div>
                <Button className="w-full bg-white/50 backdrop-blur-sm border border-stone-400/60 text-stone-800 hover:bg-white/70">
                  Start with Launch
                </Button>
              </CardContent>
            </Card>

            {/* Operate Tier */}
            <Card className="bg-white/45 backdrop-blur-lg border-2 border-green-800/60 relative hover:shadow-2xl transition-all duration-300 hover:bg-white/55">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <Badge className="bg-gradient-to-r from-green-800 to-green-900 text-white shadow-lg backdrop-blur-sm border border-stone-400/40">
                  <Star className="w-4 h-4 mr-1" />
                  Most Popular
                </Badge>
              </div>
              <CardHeader className="text-center">
                <CardTitle className="text-2xl font-bold text-stone-900">Operate</CardTitle>
                <CardDescription className="text-stone-700">Automate operations & marketing</CardDescription>
                <div className="mt-6 p-4 bg-gradient-to-r from-stone-200/60 to-stone-300/60 rounded-xl border border-stone-400/60">
                  <span className="text-4xl font-bold text-green-800">$129</span>
                  <span className="text-stone-700">/month</span>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center space-x-3 p-2 rounded-lg bg-stone-200/50">
                    <Check className="w-5 h-5 text-green-800" />
                    <span className="text-sm text-stone-800">Everything in Launch</span>
                  </div>
                  <div className="flex items-center space-x-3 p-2 rounded-lg bg-stone-200/50">
                    <Check className="w-5 h-5 text-green-800" />
                    <span className="text-sm text-stone-800">Business Operations Agents</span>
                  </div>
                  <div className="flex items-center space-x-3 p-2 rounded-lg bg-stone-200/50">
                    <Check className="w-5 h-5 text-green-800" />
                    <span className="text-sm text-stone-800">Customer Engagement Agents</span>
                  </div>
                  <div className="flex items-center space-x-3 p-2 rounded-lg bg-stone-200/50">
                    <Check className="w-5 h-5 text-green-800" />
                    <span className="text-sm text-stone-800">Analytics Dashboard</span>
                  </div>
                  <div className="flex items-center space-x-3 p-2 rounded-lg">
                    <span className="text-sm text-stone-700">Email Support, 48h SLA</span>
                  </div>
                </div>
                <Button className="w-full bg-gradient-to-r from-green-800 to-green-900 hover:from-green-900 hover:to-stone-800 shadow-lg backdrop-blur-sm border border-stone-400/40">
                  Choose Operate
                </Button>
              </CardContent>
            </Card>

            {/* Scale Tier */}
            <Card className="bg-white/35 backdrop-blur-lg border border-stone-400/60 hover:border-stone-500/80 transition-all duration-300 hover:shadow-xl hover:bg-white/45">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl font-bold text-stone-900">Scale</CardTitle>
                <CardDescription className="text-stone-700">Optimize growth & infrastructure</CardDescription>
                <div className="mt-6 p-4 bg-stone-200/60 rounded-xl border border-stone-300/60">
                  <span className="text-4xl font-bold text-green-800">$349</span>
                  <span className="text-stone-700">/month</span>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center space-x-3 p-2 rounded-lg bg-stone-200/40">
                    <Check className="w-5 h-5 text-green-800" />
                    <span className="text-sm text-stone-800">Everything in Operate</span>
                  </div>
                  <div className="flex items-center space-x-3 p-2 rounded-lg bg-stone-200/40">
                    <Check className="w-5 h-5 text-green-800" />
                    <span className="text-sm text-stone-800">Growth & Personalization Agents</span>
                  </div>
                  <div className="flex items-center space-x-3 p-2 rounded-lg bg-stone-200/40">
                    <Check className="w-5 h-5 text-green-800" />
                    <span className="text-sm text-stone-800">Advanced Infrastructure</span>
                  </div>
                  <div className="flex items-center space-x-3 p-2 rounded-lg">
                    <span className="text-sm text-stone-700">Slack Support, 24h SLA</span>
                  </div>
                </div>
                <Button className="w-full bg-white/50 backdrop-blur-sm border border-stone-400/60 text-stone-800 hover:bg-white/70">
                  Choose Scale
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-20 relative">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-stone-900">
              Frequently Asked Questions
            </h2>
            <p className="text-xl text-stone-700">
              Everything you need to know about launching your AI-powered business
            </p>
          </div>

          <Accordion type="single" collapsible className="space-y-4">
            <AccordionItem value="item-1" className="bg-white/25 backdrop-blur-lg border border-stone-400/60 rounded-xl px-6 hover:bg-white/35 transition-all duration-300">
              <AccordionTrigger className="text-left text-stone-900 font-semibold">
                How does the payment processing work?
              </AccordionTrigger>
              <AccordionContent className="text-stone-700">
                We integrate Stripe Checkout directly into your application, handling subscriptions, one-time payments, and customer billing automatically. You'll get your own Stripe account and keep 100% of your revenue minus standard Stripe fees.
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-2" className="bg-white/25 backdrop-blur-lg border border-stone-400/60 rounded-xl px-6 hover:bg-white/35 transition-all duration-300">
              <AccordionTrigger className="text-left text-stone-900 font-semibold">
                Do I need my own Stripe account?
              </AccordionTrigger>
              <AccordionContent className="text-stone-700">
                Yes, you'll need your own Stripe account. This ensures you have complete control over your payments and customer data. We'll help you set it up and integrate it seamlessly into your application.
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-3" className="bg-white/25 backdrop-blur-lg border border-stone-400/60 rounded-xl px-6 hover:bg-white/35 transition-all duration-300">
              <AccordionTrigger className="text-left text-stone-900 font-semibold">
                What business metrics can I see on my dashboard?
              </AccordionTrigger>
              <AccordionContent className="text-stone-700">
                Your dashboard includes revenue tracking, user analytics, subscription metrics, system uptime, cost monitoring, and performance insights. Everything you need to understand and grow your business.
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-4" className="bg-white/25 backdrop-blur-lg border border-stone-400/60 rounded-xl px-6 hover:bg-white/35 transition-all duration-300">
              <AccordionTrigger className="text-left text-stone-900 font-semibold">
                Can I export my customer and user data?
              </AccordionTrigger>
              <AccordionContent className="text-stone-700">
                Absolutely. You own all your data completely. You can export customer data, user information, and application data at any time. No vendor lock-in - it's your business, your data.
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-5" className="bg-white/25 backdrop-blur-lg border border-stone-400/60 rounded-xl px-6 hover:bg-white/35 transition-all duration-300">
              <AccordionTrigger className="text-left text-stone-900 font-semibold">
                What happens if my cloud costs get too high?
              </AccordionTrigger>
              <AccordionContent className="text-stone-700">
                Our CostGuardAgent monitors your Google Cloud spending in real-time and alerts you before costs spike. You can set budget limits and get automated recommendations for cost optimization.
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-stone-900/95 backdrop-blur-lg text-white py-12 border-t border-stone-400/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <div className="w-10 h-10 bg-gradient-to-r from-green-800 to-green-900 rounded-xl flex items-center justify-center shadow-lg">
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
                <a href="#features" className="block hover:text-white transition-colors">Features</a>
                <a href="#pricing" className="block hover:text-white transition-colors">Pricing</a>
                <a href="#faq" className="block hover:text-white transition-colors">FAQ</a>
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
          <Separator className="my-8 bg-stone-700/50" />
          <div className="text-center text-stone-300">
            <p>&copy; 2024 AI SaaS Factory. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
} 