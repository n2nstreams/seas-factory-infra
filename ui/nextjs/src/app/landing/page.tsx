import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Separator } from "@/components/ui/separator";
import { Input } from "@/components/ui/input";
import { Check, Code2, Shield, TrendingUp, Star, ArrowRight, Sparkles, Layers, Cpu, Wrench, Clock, Zap, Lightbulb, Rocket } from "lucide-react";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function Landing() {
  const navigate = useNavigate();
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

      {/* Navigation - Minimal & Conversion-Focused */}
      <nav className="bg-white/15 backdrop-blur-md border-b border-stone-400/30 sticky top-0 z-50">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-r from-green-800 to-green-900 rounded-xl flex items-center justify-center shadow-lg backdrop-blur-sm">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1H9V3H7V1H5V7L1 9V11L7 13V21H9V19H11V21H13V19H15V21H17V13L23 11V9H21ZM19 10.5L17 11.5V17H15V15H13V17H11V15H9V17H7V11.5L5 10.5V9.5L7 8.5V7H9V9H11V7H13V9H15V7H17V8.5L19 9.5V10.5Z"/>
                </svg>
              </div>
              <span className="text-xl font-bold text-stone-900">Forge95</span>
            </div>
            <div className="flex items-center space-x-4">
              <a href="#how-it-works" className="hidden sm:block text-stone-700 hover:text-stone-900 transition-colors font-medium">How It Works</a>
              <a href="#faq" className="hidden sm:block text-stone-700 hover:text-stone-900 transition-colors font-medium">FAQ</a>
              <Button 
                size="sm" 
                variant="ghost" 
                className="hidden md:block text-stone-700 hover:text-stone-900"
                onClick={() => navigate('/signin')}
              >
                Sign In
              </Button>
              <Button 
                size="sm" 
                className="bg-gradient-to-r from-green-800 to-green-900 hover:from-green-900 hover:to-stone-800 shadow-lg backdrop-blur-sm border border-stone-400/40"
                onClick={() => navigate('/submit-idea')}
              >
                Get Started Free
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section - Enhanced */}
      <section className="relative overflow-hidden">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16 py-20 lg:py-32">
          <div className="grid lg:grid-cols-2 gap-12 items-center max-w-none">
            <div className="space-y-8 relative z-10">
              <div className="space-y-6">
                <Badge className="bg-green-800/20 backdrop-blur-sm text-green-800 border border-green-800/40 shadow-lg">
                  <Sparkles className="w-4 h-4 mr-2" />
                  Built by AI • No Code Required
                </Badge>
                <h1 className="text-4xl lg:text-6xl xl:text-7xl font-bold text-stone-900 leading-tight">
                  Transform Your Idea into a{" "}
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-800 to-green-900">
                    Production-Ready SaaS
                  </span>{" "}
                  – Automatically
                </h1>
                <p className="text-xl lg:text-2xl text-stone-700 leading-relaxed max-w-3xl">
                  Submit your SaaS concept and watch our AI agents design, develop, and deploy your complete application. From idea to paying customers in days, not months.
                </p>
              </div>

              {/* Email Capture Form */}
              <div className="bg-white/25 backdrop-blur-lg border border-stone-400/40 rounded-2xl p-6 shadow-xl">
                <div className="flex flex-col sm:flex-row gap-4">
                  <div className="flex-1">
                    <Input
                      type="email"
                      placeholder="Enter your work email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="bg-white/40 backdrop-blur-sm border border-stone-400/50 text-stone-800 placeholder-stone-600 text-lg py-6"
                    />
                  </div>
                  <Button 
                    size="lg" 
                    className="bg-gradient-to-r from-green-800 to-green-900 hover:from-green-900 hover:to-stone-800 text-lg px-8 py-6 shadow-xl backdrop-blur-sm border border-stone-400/40"
                    onClick={() => navigate('/submit-idea')}
                  >
                    Start Building Now
                    <ArrowRight className="w-5 h-5 ml-2" />
                  </Button>
                </div>
                <p className="text-sm text-stone-600 mt-3 text-center">
                  Free during beta • No credit card required • Own 100% of your code
                </p>
              </div>

              {/* Alternative CTA */}
              <div className="flex flex-col sm:flex-row gap-4">
                <Button 
                  size="lg" 
                  variant="outline" 
                  className="text-lg px-8 py-6 bg-white/25 backdrop-blur-sm border border-stone-400/50 text-stone-800 hover:bg-white/40"
                  onClick={() => navigate('/design')}
                >
                  🎨 See Demo
                </Button>
                <Button 
                  size="lg" 
                  variant="outline" 
                  className="text-lg px-8 py-6 bg-white/25 backdrop-blur-sm border border-stone-400/50 text-stone-800 hover:bg-white/40"
                  onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
                >
                  How It Works
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

      {/* Enhanced Social Proof Section */}
      <section className="py-20 bg-white/15 backdrop-blur-md border-y border-stone-400/30">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16">
          <div className="space-y-12">
            {/* Metrics */}
            <div className="text-center space-y-8">
              <p className="text-stone-700 font-semibold text-lg">Trusted by founders who've already launched</p>
              <div className="grid grid-cols-3 lg:grid-cols-4 gap-8 max-w-4xl mx-auto">
                <div className="text-center">
                  <div className="text-3xl lg:text-4xl font-bold text-green-800">50+</div>
                  <div className="text-sm text-stone-700 mt-1">SaaS Products Built</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl lg:text-4xl font-bold text-green-800">48hrs</div>
                  <div className="text-sm text-stone-700 mt-1">Average Build Time</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl lg:text-4xl font-bold text-green-800">$0</div>
                  <div className="text-sm text-stone-700 mt-1">Dev Team Costs</div>
                </div>
                <div className="text-center lg:block hidden">
                  <div className="text-3xl lg:text-4xl font-bold text-green-800">100%</div>
                  <div className="text-sm text-stone-700 mt-1">Code Ownership</div>
                </div>
              </div>
            </div>

            {/* Testimonial */}
            <div className="max-w-4xl mx-auto">
              <div className="bg-white/25 backdrop-blur-lg border border-stone-400/40 rounded-2xl p-8 shadow-xl">
                <div className="text-center space-y-6">
                  <div className="flex justify-center">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="w-5 h-5 text-yellow-500 fill-current" />
                    ))}
                  </div>
                  <blockquote className="text-xl lg:text-2xl text-stone-800 italic leading-relaxed">
                    "I submitted my marketplace idea on Monday, and by Wednesday I had a fully functional SaaS with Stripe payments and user management. Three customers signed up in the first week."
                  </blockquote>
                  <div className="flex items-center justify-center space-x-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-green-800 to-green-900 rounded-full flex items-center justify-center">
                      <span className="text-white font-bold text-lg">JS</span>
                    </div>
                    <div className="text-left">
                      <div className="font-semibold text-stone-900">Jordan Smith</div>
                      <div className="text-sm text-stone-600">Founder, TaskFlow Pro</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Platform Logos */}
            <div className="text-center space-y-6">
              <p className="text-stone-600 font-medium">Built on enterprise-grade infrastructure</p>
              <div className="flex justify-center items-center space-x-8 lg:space-x-16 opacity-80">
                <div className="text-xl lg:text-2xl font-bold text-stone-800">Google Cloud</div>
                <div className="text-xl lg:text-2xl font-bold text-stone-800">Stripe</div>
                <div className="text-xl lg:text-2xl font-bold text-stone-800">OpenAI</div>
                <div className="text-xl lg:text-2xl font-bold text-stone-800">GitHub</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Enhanced Benefits Section */}
      <section id="features" className="py-20 relative">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16">
          <div className="text-center space-y-6 mb-20">
            <h2 className="text-3xl lg:text-4xl xl:text-5xl font-bold text-stone-900">
              Why Solo Founders Choose Forge95
            </h2>
            <p className="text-xl lg:text-2xl text-stone-700 max-w-4xl mx-auto">
              Skip the expensive dev team, lengthy timelines, and technical headaches. Get a complete, revenue-ready business faster and cheaper than ever before.
            </p>
          </div>
          
          <div className="grid lg:grid-cols-2 gap-12 xl:gap-16 mb-20">
            {/* Speed to Market */}
            <div className="space-y-6">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-gradient-to-r from-green-800 to-green-900 rounded-2xl flex items-center justify-center shadow-lg">
                  <Rocket className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-stone-900">Launch in Days, Not Months</h3>
                  <p className="text-green-800 font-semibold">10x faster than traditional development</p>
                </div>
              </div>
              <p className="text-lg text-stone-700 leading-relaxed">
                While your competitors are still hiring developers and debating tech stacks, you'll already be selling to customers. Our AI agents work 24/7 to transform your idea into a live, functioning SaaS – complete with payments, user management, and scalable infrastructure.
              </p>
            </div>

            {/* Cost Efficiency */}
            <div className="space-y-6">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-gradient-to-r from-green-800 to-green-900 rounded-2xl flex items-center justify-center shadow-lg">
                  <TrendingUp className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-stone-900">Save $50K+ on Development</h3>
                  <p className="text-green-800 font-semibold">Cost of a dev team vs. AI automation</p>
                </div>
              </div>
              <p className="text-lg text-stone-700 leading-relaxed">
                Skip the $150K+ cost of hiring developers or agencies. No equity given to co-founders, no delayed timelines, no communication overhead. Get the same quality output at a fraction of the cost, and keep 100% ownership of your business.
              </p>
            </div>

            {/* Technical Excellence */}
            <div className="space-y-6">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-gradient-to-r from-green-800 to-green-900 rounded-2xl flex items-center justify-center shadow-lg">
                  <Shield className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-stone-900">Enterprise-Grade from Day One</h3>
                  <p className="text-green-800 font-semibold">Built-in security, scaling, and monitoring</p>
                </div>
              </div>
              <p className="text-lg text-stone-700 leading-relaxed">
                Don't worry about technical debt or scalability issues later. Every application is built with production-ready architecture, automated testing, security best practices, and monitoring. Scale confidently from your first customer to thousands.
              </p>
            </div>

            {/* Complete Ownership */}
            <div className="space-y-6">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-gradient-to-r from-green-800 to-green-900 rounded-2xl flex items-center justify-center shadow-lg">
                  <Code2 className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-stone-900">It's Your Business, Completely</h3>
                  <p className="text-green-800 font-semibold">Full source code and data ownership</p>
                </div>
              </div>
              <p className="text-lg text-stone-700 leading-relaxed">
                No vendor lock-in, no revenue sharing, no restrictions. You get the complete source code, own all customer data, and can modify or migrate your application whenever you want. It's your business – you should control every aspect of it.
              </p>
            </div>
          </div>

          {/* Call-to-Action */}
          <div className="text-center">
            <div className="bg-gradient-to-r from-green-800/10 to-green-900/10 backdrop-blur-lg border border-green-800/20 rounded-2xl p-8 max-w-4xl mx-auto">
              <h3 className="text-2xl lg:text-3xl font-bold text-stone-900 mb-4">
                Ready to Skip the Development Headaches?
              </h3>
              <p className="text-lg text-stone-700 mb-6">
                Join founders who've already launched profitable SaaS businesses in days, not months.
              </p>
              <Button 
                size="lg" 
                className="bg-gradient-to-r from-green-800 to-green-900 hover:from-green-900 hover:to-stone-800 text-lg px-8 py-6 shadow-xl"
                onClick={() => navigate('/submit-idea')}
              >
                Start Building Your SaaS Now
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 bg-gradient-to-br from-green-800/5 to-stone-200/60 backdrop-blur-sm">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16">
          <div className="text-center space-y-6 mb-20">
            <h2 className="text-3xl lg:text-4xl xl:text-5xl font-bold text-stone-900">
              How It Works: From Idea to Live Business in 3 Steps
            </h2>
            <p className="text-xl lg:text-2xl text-stone-700 max-w-4xl mx-auto">
              Our AI factory handles every step of building your SaaS, so you can focus on growing your business.
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8 lg:gap-12 max-w-7xl mx-auto">
            {/* Step 1: Submit Your Idea */}
            <div className="relative">
              <div className="bg-white/35 backdrop-blur-lg border border-stone-400/40 rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 h-full">
                <div className="text-center space-y-6">
                  <div className="relative mx-auto">
                    <div className="w-20 h-20 bg-gradient-to-r from-green-800 to-green-900 rounded-2xl flex items-center justify-center shadow-lg mx-auto">
                      <Lightbulb className="w-10 h-10 text-white" />
                    </div>
                    <div className="absolute -top-2 -right-2 w-8 h-8 bg-green-800 rounded-full flex items-center justify-center text-white font-bold text-sm">
                      1
                    </div>
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-stone-900 mb-3">Submit Your Idea</h3>
                    <p className="text-stone-700 leading-relaxed">
                      Describe your SaaS concept in our simple form. Tell us what you want to build – even a few sentences are enough to get started. Our AI understands your vision.
                    </p>
                  </div>
                  <div className="bg-stone-200/60 rounded-xl p-4">
                    <p className="text-sm text-stone-600 italic">
                      "A project management tool for remote teams with time tracking and invoicing"
                    </p>
                  </div>
                </div>
              </div>
              {/* Arrow for desktop */}
              <div className="hidden lg:block absolute top-1/2 -right-6 transform -translate-y-1/2">
                <ArrowRight className="w-8 h-8 text-green-800" />
              </div>
            </div>

            {/* Step 2: AI Agents Build It */}
            <div className="relative">
              <div className="bg-white/35 backdrop-blur-lg border border-stone-400/40 rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 h-full">
                <div className="text-center space-y-6">
                  <div className="relative mx-auto">
                    <div className="w-20 h-20 bg-gradient-to-r from-green-800 to-green-900 rounded-2xl flex items-center justify-center shadow-lg mx-auto">
                      <Cpu className="w-10 h-10 text-white" />
                    </div>
                    <div className="absolute -top-2 -right-2 w-8 h-8 bg-green-800 rounded-full flex items-center justify-center text-white font-bold text-sm">
                      2
                    </div>
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-stone-900 mb-3">AI Agents Build It</h3>
                    <p className="text-stone-700 leading-relaxed">
                      Our specialized AI agents go to work: designing the UI, writing production code, setting up databases, integrating payments, and deploying your application.
                    </p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2 text-sm text-stone-600">
                      <Clock className="w-4 h-4" />
                      <span>Typically completed in 24-48 hours</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-stone-600">
                      <Zap className="w-4 h-4" />
                      <span>Real-time progress updates</span>
                    </div>
                  </div>
                </div>
              </div>
              {/* Arrow for desktop */}
              <div className="hidden lg:block absolute top-1/2 -right-6 transform -translate-y-1/2">
                <ArrowRight className="w-8 h-8 text-green-800" />
              </div>
            </div>

            {/* Step 3: Launch Your SaaS */}
            <div className="relative">
              <div className="bg-white/35 backdrop-blur-lg border border-stone-400/40 rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 h-full">
                <div className="text-center space-y-6">
                  <div className="relative mx-auto">
                    <div className="w-20 h-20 bg-gradient-to-r from-green-800 to-green-900 rounded-2xl flex items-center justify-center shadow-lg mx-auto">
                      <Rocket className="w-10 h-10 text-white" />
                    </div>
                    <div className="absolute -top-2 -right-2 w-8 h-8 bg-green-800 rounded-full flex items-center justify-center text-white font-bold text-sm">
                      3
                    </div>
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-stone-900 mb-3">Launch Your SaaS</h3>
                    <p className="text-stone-700 leading-relaxed">
                      Review your fully-functional product in the dashboard. Make any adjustments you need, then launch to your customers with one click. Your SaaS is live and ready to generate revenue.
                    </p>
                  </div>
                  <div className="bg-green-800/10 rounded-xl p-4 border border-green-800/20">
                    <p className="text-sm text-green-800 font-semibold">
                      🚀 Ready to accept payments and serve customers
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom CTA */}
          <div className="text-center mt-16">
            <Button 
              size="lg" 
              className="bg-gradient-to-r from-green-800 to-green-900 hover:from-green-900 hover:to-stone-800 text-lg px-10 py-6 shadow-xl"
              onClick={() => navigate('/submit-idea')}
            >
              Start Your 3-Step Journey
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
            <p className="text-sm text-stone-600 mt-3">
              Join 50+ founders who've already launched their SaaS
            </p>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-gradient-to-br from-stone-200/60 to-neutral-200/60 backdrop-blur-sm">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl lg:text-4xl xl:text-5xl font-bold text-stone-900">
              Choose Your Level of Automation
            </h2>
            <p className="text-xl lg:text-2xl text-stone-700">
              Start with launching your business, then scale with advanced automation
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8 xl:gap-12">
            {/* Free Tier */}
            <Card className="bg-white/35 backdrop-blur-lg border border-stone-400/60 hover:border-stone-500/80 transition-all duration-300 hover:shadow-xl hover:bg-white/45">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl font-bold text-stone-900">Free</CardTitle>
                <CardDescription className="text-stone-700">Perfect for testing your first idea</CardDescription>
                <div className="mt-6 p-4 bg-stone-200/60 rounded-xl border border-stone-300/60">
                  <span className="text-4xl font-bold text-green-800">$0</span>
                  <span className="text-stone-700">/month</span>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center space-x-3 p-2 rounded-lg bg-stone-200/40">
                    <Check className="w-5 h-5 text-green-800" />
                    <span className="text-sm text-stone-800">1 Project</span>
                  </div>
                  <div className="flex items-center space-x-3 p-2 rounded-lg bg-stone-200/40">
                    <Check className="w-5 h-5 text-green-800" />
                    <span className="text-sm text-stone-800">5 Build Hours</span>
                  </div>
                  <div className="flex items-center space-x-3 p-2 rounded-lg bg-stone-200/40">
                    <Check className="w-5 h-5 text-green-800" />
                    <span className="text-sm text-stone-800">Demo Deploy</span>
                  </div>
                  <div className="flex items-center space-x-3 p-2 rounded-lg">
                    <span className="text-sm text-stone-700">Community Support</span>
                  </div>
                </div>
                <Button 
                  onClick={() => navigate('/signup')}
                  className="w-full bg-white/50 backdrop-blur-sm border border-stone-400/60 text-stone-800 hover:bg-white/70"
                >
                  Get Started Free
                </Button>
              </CardContent>
            </Card>

            {/* Starter Tier */}
            <Card className="bg-white/45 backdrop-blur-lg border-2 border-green-800/60 relative hover:shadow-2xl transition-all duration-300 hover:bg-white/55">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <Badge className="bg-gradient-to-r from-green-800 to-green-900 text-white shadow-lg backdrop-blur-sm border border-stone-400/40">
                  <Star className="w-4 h-4 mr-1" />
                  Most Popular
                </Badge>
              </div>
              <CardHeader className="text-center">
                <CardTitle className="text-2xl font-bold text-stone-900">Starter</CardTitle>
                <CardDescription className="text-stone-700">Ideal for solo entrepreneurs launching their first SaaS</CardDescription>
                <div className="mt-6 p-4 bg-gradient-to-r from-stone-200/60 to-stone-300/60 rounded-xl border border-stone-400/60">
                  <span className="text-4xl font-bold text-green-800">$19</span>
                  <span className="text-stone-700">/month</span>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center space-x-3 p-2 rounded-lg bg-stone-200/50">
                    <Check className="w-5 h-5 text-green-800" />
                    <span className="text-sm text-stone-800">1 Project</span>
                  </div>
                  <div className="flex items-center space-x-3 p-2 rounded-lg bg-stone-200/50">
                    <Check className="w-5 h-5 text-green-800" />
                    <span className="text-sm text-stone-800">25 Build Hours</span>
                  </div>
                  <div className="flex items-center space-x-3 p-2 rounded-lg bg-stone-200/50">
                    <Check className="w-5 h-5 text-green-800" />
                    <span className="text-sm text-stone-800">Core Agents</span>
                  </div>
                  <div className="flex items-center space-x-3 p-2 rounded-lg bg-stone-200/50">
                    <Check className="w-5 h-5 text-green-800" />
                    <span className="text-sm text-stone-800">Custom Domain</span>
                  </div>
                  <div className="flex items-center space-x-3 p-2 rounded-lg">
                    <span className="text-sm text-stone-700">Email Support (72h)</span>
                  </div>
                </div>
                <Button 
                  onClick={() => navigate('/signup')}
                  className="w-full bg-gradient-to-r from-green-800 to-green-900 hover:from-green-900 hover:to-stone-800 shadow-lg backdrop-blur-sm border border-stone-400/40"
                >
                  Start Building
                </Button>
              </CardContent>
            </Card>

            {/* Pro Tier */}
            <Card className="bg-white/35 backdrop-blur-lg border border-stone-400/60 hover:border-stone-500/80 transition-all duration-300 hover:shadow-xl hover:bg-white/45">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl font-bold text-stone-900">Pro</CardTitle>
                <CardDescription className="text-stone-700">For entrepreneurs building multiple SaaS products</CardDescription>
                <div className="mt-6 p-4 bg-stone-200/60 rounded-xl border border-stone-300/60">
                  <span className="text-4xl font-bold text-green-800">$79</span>
                  <span className="text-stone-700">/month</span>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center space-x-3 p-2 rounded-lg bg-stone-200/40">
                    <Check className="w-5 h-5 text-green-800" />
                    <span className="text-sm text-stone-800">3 Projects</span>
                  </div>
                  <div className="flex items-center space-x-3 p-2 rounded-lg bg-stone-200/40">
                    <Check className="w-5 h-5 text-green-800" />
                    <span className="text-sm text-stone-800">100 Build Hours</span>
                  </div>
                  <div className="flex items-center space-x-3 p-2 rounded-lg bg-stone-200/40">
                    <Check className="w-5 h-5 text-green-800" />
                    <span className="text-sm text-stone-800">Advanced Agents</span>
                  </div>
                  <div className="flex items-center space-x-3 p-2 rounded-lg">
                    <span className="text-sm text-stone-700">Email Support (24-48h)</span>
                  </div>
                </div>
                <Button 
                  onClick={() => navigate('/signup')}
                  className="w-full bg-white/50 backdrop-blur-sm border border-stone-400/60 text-stone-800 hover:bg-white/70"
                >
                  Scale Up
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-20 relative">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16">
          <div className="text-center space-y-4 mb-16 max-w-4xl mx-auto">
            <h2 className="text-3xl lg:text-4xl xl:text-5xl font-bold text-stone-900">
              Frequently Asked Questions
            </h2>
            <p className="text-xl lg:text-2xl text-stone-700">
              Everything you need to know about launching your AI-powered business
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <Accordion type="single" collapsible className="space-y-4" defaultValue="item-1">
              <AccordionItem value="item-1" className="bg-white/25 backdrop-blur-lg border border-stone-400/60 rounded-xl px-6 hover:bg-white/35 transition-all duration-300">
                <AccordionTrigger className="text-left text-stone-900 font-semibold">
                  Do I retain ownership of the product and code?
                </AccordionTrigger>
                <AccordionContent className="text-stone-700">
                  <strong>Yes, you own 100% of everything.</strong> You get the complete source code, own all customer data, and can modify or migrate your application whenever you want. No revenue sharing, no restrictions, no vendor lock-in. It's your business – you control every aspect of it.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-2" className="bg-white/25 backdrop-blur-lg border border-stone-400/60 rounded-xl px-6 hover:bg-white/35 transition-all duration-300">
                <AccordionTrigger className="text-left text-stone-900 font-semibold">
                  What kind of SaaS ideas can I submit?
                </AccordionTrigger>
                <AccordionContent className="text-stone-700">
                  We can build a wide range of web applications: CRMs, project management tools, e-commerce platforms, marketplaces, booking systems, dashboards, and more. If it's a typical SaaS that handles user accounts, data, and payments, our AI can build it. Complex AI models or highly specialized systems may require additional consultation.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-3" className="bg-white/25 backdrop-blur-lg border border-stone-400/60 rounded-xl px-6 hover:bg-white/35 transition-all duration-300">
                <AccordionTrigger className="text-left text-stone-900 font-semibold">
                  How much does it cost and when do I pay?
                </AccordionTrigger>
                <AccordionContent className="text-stone-700">
                  <strong>Currently free during our beta program.</strong> No credit card required to start. You only pay for your own cloud hosting costs (typically $10-50/month depending on usage). Post-beta pricing will be founder-friendly with transparent monthly plans starting at $30/month.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-4" className="bg-white/25 backdrop-blur-lg border border-stone-400/60 rounded-xl px-6 hover:bg-white/35 transition-all duration-300">
                <AccordionTrigger className="text-left text-stone-900 font-semibold">
                  How long does it take to get a working product?
                </AccordionTrigger>
                <AccordionContent className="text-stone-700">
                  Most SaaS applications are ready in <strong>24-48 hours</strong> from idea submission. Complex features or unique requirements may take 3-5 days. You'll receive real-time updates on progress and can review the application at each milestone before final deployment.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-5" className="bg-white/25 backdrop-blur-lg border border-stone-400/60 rounded-xl px-6 hover:bg-white/35 transition-all duration-300">
                <AccordionTrigger className="text-left text-stone-900 font-semibold">
                  Is coding experience required?
                </AccordionTrigger>
                <AccordionContent className="text-stone-700">
                  <strong>No coding experience needed at all.</strong> The system is designed specifically for non-technical founders. You describe your idea in plain English, and our AI handles everything technical. You can focus on your business strategy, marketing, and customers while we handle the development.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-6" className="bg-white/25 backdrop-blur-lg border border-stone-400/60 rounded-xl px-6 hover:bg-white/35 transition-all duration-300">
                <AccordionTrigger className="text-left text-stone-900 font-semibold">
                  Can I make changes after the SaaS is built?
                </AccordionTrigger>
                <AccordionContent className="text-stone-700">
                  Yes! You can request modifications through our dashboard, add new features, or make adjustments to the existing functionality. Since you own the source code, you can also hire developers to make changes or extend the platform as your business grows.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-7" className="bg-white/25 backdrop-blur-lg border border-stone-400/60 rounded-xl px-6 hover:bg-white/35 transition-all duration-300">
                <AccordionTrigger className="text-left text-stone-900 font-semibold">
                  How does AI handle quality and ensure my app is bug-free?
                </AccordionTrigger>
                <AccordionContent className="text-stone-700">
                  Every application goes through automated testing with our QA agents before deployment. We use industry best practices: code reviews, security scans, performance testing, and user acceptance testing. Plus, our monitoring agents watch your app 24/7 after launch to catch and resolve any issues proactively.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-8" className="bg-white/25 backdrop-blur-lg border border-stone-400/60 rounded-xl px-6 hover:bg-white/35 transition-all duration-300">
                <AccordionTrigger className="text-left text-stone-900 font-semibold">
                  What about security and data privacy?
                </AccordionTrigger>
                <AccordionContent className="text-stone-700">
                  Security is built-in from day one. Every application includes encryption, secure authentication, HTTPS, and follows industry best practices. We're working toward compliance with GDPR, SOC 2, and other standards. Your customers' data is protected with enterprise-grade security measures.
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-20 bg-gradient-to-br from-green-800/10 to-stone-300/40 backdrop-blur-sm">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16">
          <div className="max-w-4xl mx-auto text-center space-y-8">
            <div className="space-y-6">
              <h2 className="text-3xl lg:text-4xl xl:text-5xl font-bold text-stone-900">
                Turn Your Idea Into Reality Today
              </h2>
              <p className="text-xl lg:text-2xl text-stone-700 leading-relaxed">
                Don't let another great idea slip away. Join the founders who've already built successful SaaS businesses with AI in days, not months.
              </p>
            </div>
            
            <div className="bg-white/35 backdrop-blur-lg border border-stone-400/40 rounded-2xl p-8 shadow-xl max-w-2xl mx-auto">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <Input
                    type="email"
                    placeholder="Enter your email to get started"
                    className="bg-white/50 backdrop-blur-sm border border-stone-400/50 text-stone-800 placeholder-stone-600 text-lg py-6"
                  />
                </div>
                <Button 
                  size="lg" 
                  className="bg-gradient-to-r from-green-800 to-green-900 hover:from-green-900 hover:to-stone-800 text-lg px-8 py-6 shadow-xl backdrop-blur-sm border border-stone-400/40"
                  onClick={() => navigate('/submit-idea')}
                >
                  Start Building Now
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </div>
              <div className="flex items-center justify-center space-x-6 mt-6 text-sm text-stone-600">
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-green-800" />
                  <span>Free during beta</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-green-800" />
                  <span>No credit card required</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4 text-green-800" />
                  <span>100% code ownership</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mt-12 max-w-3xl mx-auto">
              <div className="text-center space-y-2">
                <div className="text-2xl font-bold text-green-800">24-48hrs</div>
                <div className="text-sm text-stone-600">From idea to live SaaS</div>
              </div>
              <div className="text-center space-y-2">
                <div className="text-2xl font-bold text-green-800">$0</div>
                <div className="text-sm text-stone-600">Development costs</div>
              </div>
              <div className="text-center space-y-2">
                <div className="text-2xl font-bold text-green-800">50+</div>
                <div className="text-sm text-stone-600">SaaS already built</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Minimal Footer */}
      <footer className="bg-stone-900/95 backdrop-blur-lg text-white py-8 border-t border-stone-400/30">
        <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16">
          <div className="max-w-4xl mx-auto">
            <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-green-800 to-green-900 rounded-lg flex items-center justify-center shadow-lg">
                  <Code2 className="w-5 h-5 text-white" />
                </div>
                <span className="text-lg font-bold">Forge95</span>
              </div>
              <div className="flex items-center space-x-8 text-sm text-stone-400">
                <a href="/terms" className="hover:text-white transition-colors">Terms of Service</a>
                <a href="/privacy" className="hover:text-white transition-colors">Privacy Policy</a>
                                  <a href="mailto:hello@forge95.com" className="hover:text-white transition-colors">Contact</a>
              </div>
            </div>
            <Separator className="my-6 bg-stone-700/50" />
            <div className="text-center text-stone-400 text-sm">
                              <p>&copy; 2025 Forge95. Turn any idea into a live SaaS business – no code required.</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
} 