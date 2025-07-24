import { useState, useEffect } from 'react';
import IdeaSubmissionForm from '../components/IdeaSubmissionForm';
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Lightbulb,
  Rocket,
  CheckCircle,
  Users,
  Zap
} from "lucide-react";
import { tenantUtils, type TenantContext } from "@/lib/api";

// Mock user data - in a real app this would come from authentication context
const mockUser = {
  name: "John Developer",
  email: "john@example.com",
  plan: 'pro' as const,
  buildHours: {
    used: 42,
    total: 60
  }
};

export default function SubmitIdea() {
  const [tenantContext, setTenantContext] = useState<TenantContext | null>(null);

  // Initialize tenant context on mount
  useEffect(() => {
    const context = tenantUtils.initializeTenantContext();
    setTenantContext(context);
  }, []);

  const handleIdeaSubmit = async (formData: any) => {
    // Custom submission logic if needed
    console.log('Submitting idea:', formData);
    
    // The form component handles the actual API call
    // This is just for any additional processing
  };

  const handleSignOut = () => {
    // Handle sign out logic
    console.log('Signing out...');
  };

  return (
    <div className="min-h-screen bg-homepage relative overflow-hidden">
      {/* Glassmorphism background elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-br from-green-800/20 to-green-900/25 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-40 right-32 w-80 h-80 bg-gradient-to-bl from-slate-700/20 to-green-800/25 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 left-1/3 w-64 h-64 bg-gradient-to-tr from-stone-600/20 to-green-700/25 rounded-full blur-3xl animate-pulse delay-2000"></div>
        <div className="absolute bottom-32 right-20 w-72 h-72 bg-gradient-to-tl from-green-800/20 to-stone-700/25 rounded-full blur-3xl animate-pulse delay-3000"></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 pt-8 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header Section */}
          <div className="text-center mb-12">
            <div className="relative">
              <div className="flex items-center justify-center mb-4">
                <div className="w-16 h-16 bg-accent-icon rounded-2xl flex items-center justify-center shadow-2xl">
                  <Lightbulb className="w-8 h-8 text-white" />
                </div>
              </div>
              
              <h1 className="text-4xl md:text-5xl font-bold text-heading mb-4">
                Turn Your Idea Into Reality
              </h1>
              
              <p className="text-xl text-body max-w-3xl mx-auto leading-relaxed">
                Submit your SaaS idea and watch our AI Factory transform it into a fully-functional application. 
                From concept to deployment, we handle the entire development process.
              </p>

              {/* Feature highlights */}
              <div className="flex flex-wrap justify-center gap-4 mt-8">
                <Badge variant="outline" className="glass-button text-stone-700 px-4 py-2">
                  <CheckCircle className="w-4 h-4 mr-2 text-green-600" />
                  AI-Powered Development
                </Badge>
                <Badge variant="outline" className="glass-button text-stone-700 px-4 py-2">
                  <Rocket className="w-4 h-4 mr-2 text-green-600" />
                  24h to Deployment
                </Badge>
                <Badge variant="outline" className="glass-button text-stone-700 px-4 py-2">
                  <Users className="w-4 h-4 mr-2 text-green-600" />
                  Production Ready
                </Badge>
                <Badge variant="outline" className="glass-button text-stone-700 px-4 py-2">
                  <Zap className="w-4 h-4 mr-2 text-green-600" />
                  Auto Scaling
                </Badge>
              </div>
            </div>
          </div>

          {/* How it works section */}
          <div className="mb-12">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
              {[
                {
                  step: '1',
                  title: 'Submit',
                  description: 'Tell us about your idea',
                  icon: <Lightbulb className="w-6 h-6" />
                },
                {
                  step: '2',
                  title: 'Validate',
                  description: 'AI validates and researches',
                  icon: <CheckCircle className="w-6 h-6" />
                },
                {
                  step: '3',
                  title: 'Build',
                  description: 'Automated development',
                  icon: <Rocket className="w-6 h-6" />
                },
                {
                  step: '4',
                  title: 'Deploy',
                  description: 'Live on the web',
                  icon: <Zap className="w-6 h-6" />
                }
              ].map((item, index) => (
                <div key={index} className="text-center">
                  <div className="w-12 h-12 bg-accent-icon rounded-xl flex items-center justify-center text-white shadow-lg mx-auto mb-3">
                    {item.icon}
                  </div>
                  <div className="text-sm text-green-700 font-semibold mb-1">Step {item.step}</div>
                  <div className="font-semibold text-heading mb-1">{item.title}</div>
                  <div className="text-sm text-body">{item.description}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Idea Submission Form */}
          <IdeaSubmissionForm 
            onSubmit={handleIdeaSubmit}
            tenantId={tenantContext?.tenantId}
            userId={tenantContext?.userId}
          />

          {/* Support Section */}
          <div className="mt-16 text-center">
            <div className="glass-card p-8 max-w-2xl mx-auto">
              <h3 className="text-xl font-semibold text-heading mb-4">Need Help?</h3>
              <p className="text-body mb-6">
                Our team is here to help you refine your idea and get the most out of our AI Factory.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button
                  variant="outline"
                  className="btn-secondary"
                  onClick={() => window.open('mailto:support@saas-factory.com')}
                >
                  Contact Support
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
        </div>
      </div>
    </div>
  );
} 