import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Lightbulb, Clock, Target, Rocket, Code2 } from 'lucide-react';
import IdeaSubmissionForm from "@/components/IdeaSubmissionForm";
import { useAuth } from '@/App';

export default function SubmitIdea() {
  const { user } = useAuth();
  return (
    <div className="min-h-screen bg-homepage relative overflow-hidden">
      {/* Glassmorphism Background Elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-br from-green-800/20 to-green-900/25 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-40 right-32 w-80 h-80 bg-gradient-to-bl from-slate-700/20 to-green-800/25 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 left-1/3 w-64 h-64 bg-gradient-to-tr from-stone-600/20 to-green-700/25 rounded-full blur-3xl animate-pulse delay-2000"></div>
        <div className="absolute bottom-32 right-20 w-72 h-72 bg-gradient-to-tl from-green-800/20 to-stone-700/25 rounded-full blur-3xl animate-pulse delay-3000"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative z-10">
        {/* Header */}
        <div className="text-center mb-12">
          <Badge className="glass-button mb-6">
            <Lightbulb className="w-4 h-4 mr-2" />
            Idea Submission Portal
          </Badge>
          <h1 className="text-4xl lg:text-5xl font-bold text-heading mb-6">
            Transform Your{" "}
            <span className="text-accent">
              Vision
            </span>{" "}
            Into Reality
          </h1>
          <p className="text-xl text-body max-w-3xl mx-auto mb-8">
            Describe your SaaS idea and let our AI agents handle the entire development process. 
            From concept to deployment, we've got you covered.
          </p>
          
          {/* Enhanced Guidance */}
          <div className="bg-white/25 backdrop-blur-lg border border-stone-400/40 rounded-2xl p-6 max-w-4xl mx-auto">
            <h3 className="text-lg font-semibold text-heading mb-4">💡 How to Write a Great Idea</h3>
            <div className="grid md:grid-cols-2 gap-6 text-left">
              <div>
                <h4 className="font-medium text-heading mb-2">✅ Good Examples:</h4>
                <ul className="text-sm text-body space-y-1">
                  <li>• "AI-powered project management tool for remote teams"</li>
                  <li>• "Automated invoicing system for freelancers"</li>
                  <li>• "Customer feedback collection and analysis platform"</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-heading mb-2">❌ Avoid:</h4>
                <ul className="text-sm text-body space-y-1">
                  <li>• "Something like Uber but different"</li>
                  <li>• "A social media app"</li>
                  <li>• "I want to make money online"</li>
                </ul>
              </div>
            </div>
            <p className="text-sm text-stone-600 mt-4 text-center">
              <strong>Tip:</strong> Be specific about what problem you're solving and who it's for
            </p>
          </div>
          
          {/* Account Creation Prompt */}
          {!user && (
            <div className="bg-gradient-to-r from-green-800/10 to-green-900/10 backdrop-blur-lg border border-green-800/20 rounded-2xl p-6 max-w-4xl mx-auto mt-6">
              <div className="text-center">
                <h3 className="text-lg font-semibold text-green-800 mb-3">
                  🚀 Ready to Submit Your Idea?
                </h3>
                <p className="text-stone-700 mb-4">
                  Create your free account to submit ideas, track progress, and access your dashboard
                </p>
                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                  <Button 
                    size="lg" 
                    className="bg-gradient-to-r from-green-800 to-green-900 hover:from-green-900 hover:to-stone-800"
                    onClick={() => window.location.href = '/signup'}
                  >
                    Create Free Account
                  </Button>
                  <Button 
                    variant="outline" 
                    className="border-green-300 text-green-800 hover:bg-green-50"
                    onClick={() => window.location.href = '/signin'}
                  >
                    Sign In
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Process Overview */}
        <div className="glass-card p-8 mb-12">
          <h2 className="text-2xl font-bold text-heading text-center mb-8">Your Idea's Journey</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-accent-icon rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Lightbulb className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold text-heading mb-2">1. Submit Idea</h3>
              <p className="text-sm text-body">Describe your SaaS concept and target market</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-accent-secondary rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Target className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold text-heading mb-2">2. AI Analysis</h3>
              <p className="text-sm text-body">Our agents analyze and plan your application</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-accent-tertiary rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Clock className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold text-heading mb-2">3. Development</h3>
              <p className="text-sm text-body">Automated design, coding, and testing</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-accent-icon rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Rocket className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold text-heading mb-2">4. Launch</h3>
              <p className="text-sm text-body">Deploy your production-ready SaaS</p>
            </div>
          </div>
        </div>

        {/* Main Form */}
        <IdeaSubmissionForm 
          userId={user?.id}
          tenantId="5aff78c7-413b-4e0e-bbfb-090765835bab"
        />

        {/* Support Links */}
        <div className="mt-12 text-center">
          <h3 className="text-xl font-semibold text-heading mb-6">Need Help Getting Started?</h3>
          <div className="flex flex-wrap justify-center gap-4">
            <Button 
              variant="outline" 
              className="btn-secondary"
              onClick={() => window.open('/examples', '_blank')}
            >
              View Example Ideas
            </Button>
            <Button 
              variant="outline" 
              className="btn-secondary"
              onClick={() => window.open('/pricing', '_blank')}
            >
              Check Pricing
            </Button>
            <Button 
              variant="outline" 
              className="btn-secondary"
              onClick={() => window.open('/docs', '_blank')}
            >
              View Documentation
            </Button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-stone-900/95 backdrop-blur-lg text-white py-12 border-t border-stone-400/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
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