import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { 
  Bot, 
  ChevronRight, 
  Rocket, 
  Lightbulb,
  TrendingUp,
  Code2
} from "lucide-react";
import IdeaSubmissionForm from "@/components/IdeaSubmissionForm";

export default function Home() {
  const [showIdeaForm, setShowIdeaForm] = useState(false);

  const handleCTAClick = () => {
    setShowIdeaForm(true);
  };

  if (showIdeaForm) {
    return (
      <div className="min-h-screen bg-homepage relative overflow-hidden py-12">
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
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-br from-green-800/20 to-green-900/25 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-40 right-32 w-80 h-80 bg-gradient-to-bl from-slate-700/20 to-green-800/25 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 left-1/3 w-64 h-64 bg-gradient-to-tr from-stone-600/20 to-green-700/25 rounded-full blur-3xl animate-pulse delay-2000"></div>
      </div>
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
                onClick={handleCTAClick}
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
            <div className="glass-card p-8 text-center group hover:scale-105 transition-transform duration-300">
              <div className="w-16 h-16 bg-accent-icon rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                <Lightbulb className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-heading mb-4">Submit Your Idea</h3>
              <p className="text-body leading-relaxed">
                Describe your SaaS concept, target audience, and key features. Our intelligent form guides you through the process.
              </p>
            </div>
            <div className="glass-card p-8 text-center group hover:scale-105 transition-transform duration-300">
              <div className="w-16 h-16 bg-accent-icon rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                <Bot className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-heading mb-4">AI Development</h3>
              <p className="text-body leading-relaxed">
                Specialized AI agents analyze your idea, design the architecture, generate code, and create beautiful UIs.
              </p>
            </div>
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