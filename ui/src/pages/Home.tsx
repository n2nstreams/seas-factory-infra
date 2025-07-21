import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Zap, 
  Bot, 
  ChevronRight, 
  Globe, 
  Code, 
  Rocket, 
  Lightbulb,
  CheckCircle,
  Shield,
  Users,
  Settings,
  TrendingUp
} from "lucide-react";
import IdeaSubmissionForm from "@/components/IdeaSubmissionForm";

export default function Home() {
  const [showIdeaForm, setShowIdeaForm] = useState(false);
  const [isAdminUser] = useState(false); // This would come from auth context

  if (showIdeaForm) {
    return (
      <div className="min-h-screen bg-homepage relative overflow-hidden py-12">
        {/* Background elements */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-br from-green-800/20 to-green-900/25 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute top-40 right-32 w-80 h-80 bg-gradient-to-bl from-slate-700/20 to-green-800/25 rounded-full blur-3xl animate-pulse delay-1000"></div>
          <div className="absolute bottom-20 left-1/3 w-64 h-64 bg-gradient-to-tr from-stone-600/20 to-green-700/25 rounded-full blur-3xl animate-pulse delay-2000"></div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="mb-8">
            <Button
              variant="outline"
              onClick={() => setShowIdeaForm(false)}
              className="btn-secondary"
            >
              ← Back to Home
            </Button>
          </div>
          
          <IdeaSubmissionForm />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-homepage relative overflow-hidden">
      {/* Glassmorphism Background Elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-br from-green-800/20 to-green-900/25 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-40 right-32 w-80 h-80 bg-gradient-to-bl from-slate-700/20 to-green-800/25 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 left-1/3 w-64 h-64 bg-gradient-to-tr from-stone-600/20 to-green-700/25 rounded-full blur-3xl animate-pulse delay-2000"></div>
      </div>

      {/* Navigation */}
      <nav className="glass-nav sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-accent-icon rounded-xl flex items-center justify-center shadow-lg">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-heading">AI SaaS Factory</span>
            </div>
            <div className="flex items-center space-x-4">
              {isAdminUser && (
                <Button 
                  variant="outline" 
                  className="btn-secondary"
                  onClick={() => window.location.href = '/admin'}
                >
                  <Shield className="w-4 h-4 mr-2" />
                  Admin Dashboard
                </Button>
              )}
              <Button 
                variant="outline" 
                className="btn-secondary"
                onClick={() => window.location.href = '/dashboard'}
              >
                Dashboard
              </Button>
              <Button 
                className="btn-primary"
                onClick={() => setShowIdeaForm(true)}
              >
                Submit Idea
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 pt-16 pb-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-4xl mx-auto">
            <Badge className="bg-accent-glow text-white mb-6 px-4 py-2 text-sm">
              ✨ AI-Powered SaaS Generation
            </Badge>
            
            <h1 className="text-5xl md:text-6xl font-bold text-heading mb-6 leading-tight">
              Turn Your Ideas Into
              <span className="block bg-gradient-to-r from-green-700 to-green-900 bg-clip-text text-transparent">
                Production-Ready SaaS
              </span>
            </h1>
            
            <p className="text-xl text-body mb-10 max-w-3xl mx-auto leading-relaxed">
              Submit your idea and watch our AI agents design, develop, and deploy your complete SaaS application. 
              From concept to customer-ready product in record time.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button 
                size="lg" 
                className="btn-primary text-lg px-8 py-4"
                onClick={() => setShowIdeaForm(true)}
              >
                <Lightbulb className="w-5 h-5 mr-2" />
                Submit Your Idea
                <ChevronRight className="w-5 h-5 ml-2" />
              </Button>
              
              <Button 
                size="lg" 
                variant="outline" 
                className="btn-secondary text-lg px-8 py-4"
                onClick={() => window.location.href = '/dashboard'}
              >
                <TrendingUp className="w-5 h-5 mr-2" />
                View Dashboard
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-heading mb-4">
              How It Works
            </h2>
            <p className="text-lg text-body max-w-2xl mx-auto">
              Our AI agents handle every aspect of SaaS development, from initial concept to deployment.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="glass-card p-8 text-center group hover:scale-105 transition-transform duration-300">
              <div className="w-16 h-16 bg-accent-icon rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                <Lightbulb className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-heading mb-4">Submit Your Idea</h3>
              <p className="text-body leading-relaxed">
                Describe your SaaS concept, target audience, and key features. Our intelligent form guides you through the process.
              </p>
            </div>

            {/* Step 2 */}
            <div className="glass-card p-8 text-center group hover:scale-105 transition-transform duration-300">
              <div className="w-16 h-16 bg-accent-icon rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                <Bot className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-heading mb-4">AI Development</h3>
              <p className="text-body leading-relaxed">
                Specialized AI agents analyze your idea, design the architecture, generate code, and create beautiful UIs.
              </p>
            </div>

            {/* Step 3 */}
            <div className="glass-card p-8 text-center group hover:scale-105 transition-transform duration-300">
              <div className="w-16 h-16 bg-accent-icon rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                <Rocket className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-heading mb-4">Deploy & Scale</h3>
              <p className="text-body leading-relaxed">
                Your SaaS is automatically deployed, tested, and ready for customers with built-in scaling and monitoring.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Capabilities Section */}
      <section className="relative z-10 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-heading mb-4">
              Powered by Specialized AI Agents
            </h2>
            <p className="text-lg text-body max-w-2xl mx-auto">
              Each agent is an expert in their domain, working together to create your perfect SaaS.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Design Agent */}
            <div className="glass-card p-6 text-center">
              <div className="w-12 h-12 bg-pink-600 rounded-xl flex items-center justify-center mx-auto mb-4">
                <Globe className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-heading mb-2">Design Agent</h3>
              <p className="text-sm text-body">Creates beautiful, responsive UIs and optimal user experiences</p>
            </div>

            {/* Development Agent */}
            <div className="glass-card p-6 text-center">
              <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4">
                <Code className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-heading mb-2">Dev Agent</h3>
              <p className="text-sm text-body">Generates clean, scalable code following best practices</p>
            </div>

            {/* QA Agent */}
            <div className="glass-card p-6 text-center">
              <div className="w-12 h-12 bg-green-600 rounded-xl flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-heading mb-2">QA Agent</h3>
              <p className="text-sm text-body">Comprehensive testing and quality assurance automation</p>
            </div>

            {/* Ops Agent */}
            <div className="glass-card p-6 text-center">
              <div className="w-12 h-12 bg-purple-600 rounded-xl flex items-center justify-center mx-auto mb-4">
                <Settings className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-heading mb-2">Ops Agent</h3>
              <p className="text-sm text-body">Deployment, monitoring, and infrastructure management</p>
            </div>
          </div>
        </div>
      </section>

      {/* Admin Features Section (for admin users) */}
      {isAdminUser && (
        <section className="relative z-10 py-20 border-t border-stone-200/20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <Badge className="bg-red-600 text-white mb-4">Admin Access</Badge>
              <h2 className="text-3xl md:text-4xl font-bold text-heading mb-4">
                Admin Management
              </h2>
              <p className="text-lg text-body max-w-2xl mx-auto">
                Manage ideas, approve projects, and oversee tenant operations from the admin dashboard.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* Idea Management */}
              <div className="glass-card p-8 text-center">
                <div className="w-16 h-16 bg-yellow-500 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                  <Lightbulb className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-heading mb-4">Idea Management</h3>
                <p className="text-body leading-relaxed mb-6">
                  Review, approve, or reject submitted ideas. Provide feedback and guide the development process.
                </p>
                <Button 
                  variant="outline" 
                  className="btn-secondary"
                  onClick={() => window.location.href = '/admin#ideas'}
                >
                  Review Ideas
                </Button>
              </div>

              {/* Tenant Management */}
              <div className="glass-card p-8 text-center">
                <div className="w-16 h-16 bg-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                  <Users className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-heading mb-4">Tenant Management</h3>
                <p className="text-body leading-relaxed mb-6">
                  Manage tenant accounts, upgrade to isolated environments, and monitor usage patterns.
                </p>
                <Button 
                  variant="outline" 
                  className="btn-secondary"
                  onClick={() => window.location.href = '/admin#tenants'}
                >
                  Manage Tenants
                </Button>
              </div>

              {/* System Analytics */}
              <div className="glass-card p-8 text-center">
                <div className="w-16 h-16 bg-green-500 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                  <TrendingUp className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-heading mb-4">System Analytics</h3>
                <p className="text-body leading-relaxed mb-6">
                  Monitor system performance, track approval rates, and analyze development trends.
                </p>
                <Button 
                  variant="outline" 
                  className="btn-secondary"
                  onClick={() => window.location.href = '/admin#analytics'}
                >
                  View Analytics
                </Button>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* CTA Section */}
      <section className="relative z-10 py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="glass-card p-12">
            <h2 className="text-3xl md:text-4xl font-bold text-heading mb-6">
              Ready to Build Your SaaS?
            </h2>
            <p className="text-lg text-body mb-8 max-w-2xl mx-auto">
              Join thousands of entrepreneurs who've turned their ideas into successful SaaS products with our AI Factory.
            </p>
            <Button 
              size="lg" 
              className="btn-primary text-lg px-12 py-4"
              onClick={() => setShowIdeaForm(true)}
            >
              <Zap className="w-5 h-5 mr-2" />
              Get Started Now
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-stone-200/20 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <div className="w-8 h-8 bg-accent-icon rounded-lg flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-semibold text-heading">AI SaaS Factory</span>
            </div>
            <div className="text-body text-sm">
              © 2024 AI SaaS Factory. Powered by intelligent automation.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
} 