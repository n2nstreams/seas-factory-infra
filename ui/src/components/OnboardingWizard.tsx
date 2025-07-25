import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  X, 
  ArrowRight, 
  ArrowLeft, 
  Sparkles, 
  Lightbulb, 
  Palette, 
  Code2, 
  Rocket,
  BarChart3,
  MessageCircle,
  CheckCircle,
  Play,
  Plus
} from 'lucide-react';

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<any>;
  content: React.ReactNode;
  highlightElement?: string;
}

interface OnboardingWizardProps {
  isOpen: boolean;
  onComplete: () => void;
  onSkip: () => void;
}

export default function OnboardingWizard({ isOpen, onComplete, onSkip }: OnboardingWizardProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);

  const steps: OnboardingStep[] = [
    {
      id: 'welcome',
      title: 'Welcome to AI SaaS Factory! 🎉',
      description: 'Your intelligent development companion',
      icon: Sparkles,
      content: (
        <div className="space-y-4">
          <div className="glass-card p-6 rounded-xl border border-green-800/20 bg-green-50/30 backdrop-blur-sm">
            <div className="flex items-center gap-3 mb-3">
              <Sparkles className="w-6 h-6 text-green-800" />
              <h3 className="font-semibold text-green-900">Transform Ideas into Reality</h3>
            </div>
            <p className="text-green-800/80 text-sm leading-relaxed">
              Our AI-powered factory turns your ideas into fully-deployed SaaS applications. 
              From concept to code, design to deployment - all automated with enterprise-grade quality.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="glass-card p-4 rounded-lg bg-white/40 backdrop-blur-sm border border-green-800/10">
              <div className="text-2xl mb-2">⚡</div>
              <div className="text-sm font-medium text-green-900">Lightning Fast</div>
              <div className="text-xs text-green-800/70">Ideas to deployment in 24 hours</div>
            </div>
            <div className="glass-card p-4 rounded-lg bg-white/40 backdrop-blur-sm border border-green-800/10">
              <div className="text-2xl mb-2">🎨</div>
              <div className="text-sm font-medium text-green-900">Beautiful Design</div>
              <div className="text-xs text-green-800/70">AI-generated glassmorphism UI</div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'submit-idea',
      title: 'Submit Your First Idea',
      description: 'Start building with our intelligent idea validation',
      icon: Lightbulb,
      content: (
        <div className="space-y-4">
          <div className="glass-card p-6 rounded-xl border border-green-800/20 bg-green-50/30 backdrop-blur-sm">
            <div className="flex items-center gap-3 mb-3">
              <Lightbulb className="w-6 h-6 text-green-800" />
              <h3 className="font-semibold text-green-900">How It Works</h3>
            </div>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <div className="w-6 h-6 rounded-full bg-green-800 text-white text-xs flex items-center justify-center font-medium">1</div>
                <span className="text-sm text-green-800">Describe your SaaS idea in plain English</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-6 h-6 rounded-full bg-green-800 text-white text-xs flex items-center justify-center font-medium">2</div>
                <span className="text-sm text-green-800">AI validates market potential & technical feasibility</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-6 h-6 rounded-full bg-green-800 text-white text-xs flex items-center justify-center font-medium">3</div>
                <span className="text-sm text-green-800">Factory pipeline automatically builds your app</span>
              </div>
            </div>
          </div>
          <div className="flex items-center justify-center">
            <Button 
              className="bg-green-800 hover:bg-green-900 text-white shadow-lg"
              onClick={() => {
                // This would typically navigate to the idea submission
                console.log('Navigate to idea submission');
              }}
            >
              <Plus className="w-4 h-4 mr-2" />
              Submit Your First Idea
            </Button>
          </div>
        </div>
      ),
      highlightElement: '[data-onboarding="submit-idea"]'
    },
    {
      id: 'project-stages',
      title: 'Understanding Project Stages',
      description: 'Track your project through our intelligent pipeline',
      icon: BarChart3,
      content: (
        <div className="space-y-4">
          <div className="glass-card p-6 rounded-xl border border-green-800/20 bg-green-50/30 backdrop-blur-sm">
            <div className="flex items-center gap-3 mb-4">
              <BarChart3 className="w-6 h-6 text-green-800" />
              <h3 className="font-semibold text-green-900">AI Factory Pipeline</h3>
            </div>
            <div className="space-y-3">
              {[
                { stage: 'Idea', icon: '💡', desc: 'Market research & validation' },
                { stage: 'Design', icon: '🎨', desc: 'UI/UX wireframes & prototypes' },
                { stage: 'Development', icon: '💻', desc: 'Code generation & API creation' },
                { stage: 'Testing', icon: '🧪', desc: 'Automated QA & security scans' },
                { stage: 'Deployment', icon: '🚀', desc: 'Production deployment & monitoring' }
              ].map((item, index) => (
                <div key={item.stage} className="flex items-center gap-3 p-3 rounded-lg bg-white/30 backdrop-blur-sm">
                  <span className="text-lg">{item.icon}</span>
                  <div className="flex-1">
                    <div className="font-medium text-green-900 text-sm">{item.stage}</div>
                    <div className="text-xs text-green-800/70">{item.desc}</div>
                  </div>
                  <Badge variant="outline" className="text-xs">Auto</Badge>
                </div>
              ))}
            </div>
          </div>
        </div>
      ),
      highlightElement: '[data-onboarding="project-stages"]'
    },
    {
      id: 'dashboard-navigation',
      title: 'Navigate Your Dashboard',
      description: 'Explore powerful features and monitoring tools',
      icon: BarChart3,
      content: (
        <div className="space-y-4">
          <div className="glass-card p-6 rounded-xl border border-green-800/20 bg-green-50/30 backdrop-blur-sm">
            <div className="flex items-center gap-3 mb-4">
              <BarChart3 className="w-6 h-6 text-green-800" />
              <h3 className="font-semibold text-green-900">Dashboard Features</h3>
            </div>
            <div className="grid grid-cols-1 gap-3">
              <div className="flex items-center gap-3 p-3 rounded-lg bg-white/30 backdrop-blur-sm">
                <div className="w-8 h-8 rounded-lg bg-green-800/20 flex items-center justify-center">
                  <BarChart3 className="w-4 h-4 text-green-800" />
                </div>
                <div className="flex-1">
                  <div className="font-medium text-green-900 text-sm">Overview</div>
                  <div className="text-xs text-green-800/70">Project status & build hours</div>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-lg bg-white/30 backdrop-blur-sm">
                <div className="w-8 h-8 rounded-lg bg-green-800/20 flex items-center justify-center">
                  <Code2 className="w-4 h-4 text-green-800" />
                </div>
                <div className="flex-1">
                  <div className="font-medium text-green-900 text-sm">Projects</div>
                  <div className="text-xs text-green-800/70">Manage all your SaaS projects</div>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-lg bg-white/30 backdrop-blur-sm">
                <div className="w-8 h-8 rounded-lg bg-green-800/20 flex items-center justify-center">
                  <Rocket className="w-4 h-4 text-green-800" />
                </div>
                <div className="flex-1">
                  <div className="font-medium text-green-900 text-sm">Factory</div>
                  <div className="text-xs text-green-800/70">Real-time build monitoring</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      ),
      highlightElement: '[data-onboarding="dashboard-tabs"]'
    },
    {
      id: 'get-help',
      title: 'Get Help & Support',
      description: 'Resources to maximize your success',
      icon: MessageCircle,
      content: (
        <div className="space-y-4">
          <div className="glass-card p-6 rounded-xl border border-green-800/20 bg-green-50/30 backdrop-blur-sm">
            <div className="flex items-center gap-3 mb-4">
              <MessageCircle className="w-6 h-6 text-green-800" />
              <h3 className="font-semibold text-green-900">Support Resources</h3>
            </div>
            <div className="space-y-3">
              <div className="flex items-center gap-3 p-3 rounded-lg bg-white/30 backdrop-blur-sm">
                <MessageCircle className="w-5 h-5 text-green-800" />
                <div className="flex-1">
                  <div className="font-medium text-green-900 text-sm">AI Chat Assistant</div>
                  <div className="text-xs text-green-800/70">Get instant help (bottom-right corner)</div>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-lg bg-white/30 backdrop-blur-sm">
                <span className="text-lg">📖</span>
                <div className="flex-1">
                  <div className="font-medium text-green-900 text-sm">Documentation</div>
                  <div className="text-xs text-green-800/70">Guides, tutorials, and best practices</div>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-lg bg-white/30 backdrop-blur-sm">
                <span className="text-lg">💬</span>
                <div className="flex-1">
                  <div className="font-medium text-green-900 text-sm">Community Forum</div>
                  <div className="text-xs text-green-800/70">Connect with other builders</div>
                </div>
              </div>
            </div>
          </div>
          <div className="glass-card p-4 rounded-xl border border-green-800/20 bg-gradient-to-r from-green-800/10 to-green-900/15 backdrop-blur-sm">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-800" />
              <div>
                <div className="font-medium text-green-900 text-sm">You're all set!</div>
                <div className="text-xs text-green-800/70">Ready to build amazing SaaS applications</div>
              </div>
            </div>
          </div>
        </div>
      )
    }
  ];

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setIsAnimating(true);
      setTimeout(() => {
        setCurrentStep(currentStep + 1);
        setIsAnimating(false);
      }, 150);
    } else {
      onComplete();
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setIsAnimating(true);
      setTimeout(() => {
        setCurrentStep(currentStep - 1);
        setIsAnimating(false);
      }, 150);
    }
  };

  const progress = ((currentStep + 1) / steps.length) * 100;
  const currentStepData = steps[currentStep];

  useEffect(() => {
    // Highlight elements when step changes
    const highlightElement = currentStepData?.highlightElement;
    if (highlightElement) {
      const element = document.querySelector(highlightElement);
      if (element) {
        element.classList.add('onboarding-highlight');
        return () => element.classList.remove('onboarding-highlight');
      }
    }
  }, [currentStep, currentStepData]);

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40" />
      
      {/* Onboarding Modal */}
      <div className="fixed inset-0 flex items-center justify-center p-4 z-50">
        <Card className="w-full max-w-lg glass-card bg-white/80 backdrop-blur-xl border border-green-800/20 shadow-2xl">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-green-800/20 flex items-center justify-center">
                  <currentStepData.icon className="w-5 h-5 text-green-800" />
                </div>
                <div>
                  <CardTitle className="text-lg text-green-900">{currentStepData.title}</CardTitle>
                  <p className="text-sm text-green-800/70">{currentStepData.description}</p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={onSkip}
                className="text-green-800/60 hover:text-green-800 hover:bg-green-800/10"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
            
            {/* Progress */}
            <div className="space-y-2 mt-4">
              <div className="flex justify-between text-xs text-green-800/70">
                <span>Step {currentStep + 1} of {steps.length}</span>
                <span>{Math.round(progress)}% complete</span>
              </div>
              <Progress value={progress} className="h-2 bg-green-800/10" />
            </div>
          </CardHeader>
          
          <CardContent className="pt-0">
            <div className={`transition-all duration-150 ${isAnimating ? 'opacity-50 scale-95' : 'opacity-100 scale-100'}`}>
              {currentStepData.content}
            </div>
            
            {/* Navigation */}
            <div className="flex items-center justify-between mt-6 pt-4 border-t border-green-800/20">
              <div className="flex gap-2">
                <Button
                  variant="ghost"
                  onClick={onSkip}
                  className="text-green-800/60 hover:text-green-800 hover:bg-green-800/10"
                >
                  Skip Tour
                </Button>
              </div>
              
              <div className="flex gap-2">
                {currentStep > 0 && (
                  <Button
                    variant="outline"
                    onClick={prevStep}
                    className="border-green-800/30 text-green-800 hover:bg-green-800/10"
                  >
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Back
                  </Button>
                )}
                <Button
                  onClick={nextStep}
                  className="bg-green-800 hover:bg-green-900 text-white shadow-lg"
                >
                  {currentStep === steps.length - 1 ? (
                    <>
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Get Started
                    </>
                  ) : (
                    <>
                      Next
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </>
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Custom CSS for highlighting */}
      <style jsx>{`
        .onboarding-highlight {
          position: relative;
          z-index: 60;
        }
        .onboarding-highlight::before {
          content: '';
          position: absolute;
          inset: -4px;
          background: linear-gradient(45deg, rgba(34, 197, 94, 0.3), rgba(21, 128, 61, 0.3));
          border-radius: 12px;
          z-index: -1;
          animation: pulse 2s ease-in-out infinite;
        }
        @keyframes pulse {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 0.6; }
        }
      `}</style>
    </>
  );
} 