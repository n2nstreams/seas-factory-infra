import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { 
  Lightbulb, 
  Rocket, 
  Target,
  Sparkles,
  CheckCircle,
  AlertCircle,
  ArrowRight,
  Loader2
} from "lucide-react";
import { type TenantContext } from "@/lib/api";

interface IdeaFormData {
  projectName: string;
  description: string;
  problem: string;
  solution: string;
  targetAudience: string;
  keyFeatures: string;
  businessModel: string;
  timeline: string;
  budget: string;
  priority: 'low' | 'medium' | 'high';
  category: string;
}

interface IdeaSubmissionFormProps {
  onSubmit?: (formData: IdeaFormData) => Promise<void>;
  tenantId?: string;
  userId?: string;
}

export default function IdeaSubmissionForm({ onSubmit, tenantId, userId }: IdeaSubmissionFormProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  
  const [formData, setFormData] = useState<IdeaFormData>({
    projectName: '',
    description: '',
    problem: '',
    solution: '',
    targetAudience: '',
    keyFeatures: '',
    businessModel: '',
    timeline: '',
    budget: '',
    priority: 'medium',
    category: ''
  });

  const updateFormData = (field: keyof IdeaFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const validateStep = (step: number): boolean => {
    switch (step) {
      case 1:
        return !!(formData.projectName && formData.description && formData.category);
      case 2:
        return !!(formData.problem && formData.solution && formData.targetAudience);
      case 3:
        return !!(formData.keyFeatures && formData.businessModel);
      default:
        return true;
    }
  };

  const nextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, 4));
    }
  };

  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const handleSubmit = async () => {
    if (!validateStep(3)) return;

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      // Call the onSubmit prop if provided
      if (onSubmit) {
        await onSubmit(formData);
      } else {
        // Submit idea to the new ideas API endpoint
        const response = await fetch('/api/ideas/submit', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'x-tenant-id': tenantId || 'default',
            'x-user-id': userId || 'default-user'
          },
          body: JSON.stringify(formData)
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || 'Failed to submit idea');
        }

        const result = await response.json();
        console.log('Idea submitted successfully:', result);
      }

      setSubmitSuccess(true);
      setCurrentStep(4);
    } catch (error) {
      console.error('Error submitting idea:', error);
      setSubmitError(error instanceof Error ? error.message : 'An unexpected error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStepProgress = () => {
    return (currentStep / 4) * 100;
  };

  const categories = [
    'E-commerce & Retail',
    'SaaS & Business Tools',
    'Education & Training',
    'Healthcare & Wellness',
    'Finance & Fintech',
    'Entertainment & Media',
    'Social & Community',
    'Productivity & Automation',
    'Marketing & Analytics',
    'Other'
  ];

  const priorities = [
    { value: 'low', label: 'Low Priority', color: 'bg-gray-500' },
    { value: 'medium', label: 'Medium Priority', color: 'bg-yellow-500' },
    { value: 'high', label: 'High Priority', color: 'bg-red-500' }
  ];

  const businessModels = [
    'Subscription (SaaS)',
    'One-time Purchase',
    'Freemium',
    'Marketplace Commission',
    'Advertising',
    'Licensing',
    'Consulting Services',
    'Other'
  ];

  const timelines = [
    '1-2 weeks',
    '1 month',
    '2-3 months',
    '6 months',
    '1 year',
    'More than 1 year'
  ];

  if (submitSuccess) {
    return (
      <Card className="glass-card max-w-2xl mx-auto">
        <CardContent className="p-8 text-center">
          <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-heading mb-4">Idea Submitted Successfully!</h2>
          <p className="text-body mb-6">
            Your idea "<strong>{formData.projectName}</strong>" has been submitted for review. 
            Our admin team will review it and you'll receive an update soon.
          </p>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-blue-800 mb-2">What happens next?</h3>
            <ul className="text-blue-700 text-sm space-y-1">
              <li>• Admin team reviews your idea within 48 hours</li>
              <li>• You'll receive email notification about the decision</li>
              <li>• If approved, your project will begin development automatically</li>
              <li>• You can track progress in your dashboard</li>
            </ul>
          </div>
          <Button 
            className="btn-primary"
            onClick={() => window.location.href = '/dashboard'}
          >
            Go to Dashboard
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-body">Step {currentStep} of 4</span>
          <span className="text-sm text-body">{Math.round(getStepProgress())}% Complete</span>
        </div>
        <div className="w-full bg-stone-200 rounded-full h-2">
          <div 
            className="bg-accent h-2 rounded-full transition-all duration-300"
            style={{ width: `${getStepProgress()}%` }}
          />
        </div>
      </div>

      <Card className="glass-card">
        <CardContent className="p-8">
          {/* Step 1: Basic Information */}
          {currentStep === 1 && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <Lightbulb className="w-12 h-12 text-accent mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-heading">Tell us about your idea</h2>
                <p className="text-body">Let's start with the basics of your project</p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-heading mb-2">
                    Project Name *
                  </label>
                  <Input
                    value={formData.projectName}
                    onChange={(e) => updateFormData('projectName', e.target.value)}
                    placeholder="e.g., TaskFlow Pro, Invoice Manager"
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-heading mb-2">
                    Project Description *
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => updateFormData('description', e.target.value)}
                    placeholder="Brief description of what your project does"
                    className="w-full h-24 px-3 py-2 border border-stone-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-heading mb-2">
                    Category *
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) => updateFormData('category', e.target.value)}
                    aria-label="Project category"
                    className="w-full px-3 py-2 border border-stone-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent"
                  >
                    <option value="">Select a category</option>
                    {categories.map(category => (
                      <option key={category} value={category}>{category}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-heading mb-2">
                    Priority Level
                  </label>
                  <div className="flex space-x-3">
                    {priorities.map(priority => (
                      <button
                        key={priority.value}
                        type="button"
                        onClick={() => updateFormData('priority', priority.value as 'low' | 'medium' | 'high')}
                        className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                          formData.priority === priority.value
                            ? 'bg-accent text-white'
                            : 'bg-stone-100 text-stone-700 hover:bg-stone-200'
                        }`}
                      >
                        {priority.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Problem & Solution */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <Target className="w-12 h-12 text-accent mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-heading">Problem & Solution</h2>
                <p className="text-body">Help us understand the problem you're solving</p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-heading mb-2">
                    What problem are you solving? *
                  </label>
                  <textarea
                    value={formData.problem}
                    onChange={(e) => updateFormData('problem', e.target.value)}
                    placeholder="Describe the problem your project addresses"
                    className="w-full h-24 px-3 py-2 border border-stone-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-heading mb-2">
                    How does your solution work? *
                  </label>
                  <textarea
                    value={formData.solution}
                    onChange={(e) => updateFormData('solution', e.target.value)}
                    placeholder="Explain your solution approach"
                    className="w-full h-24 px-3 py-2 border border-stone-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-heading mb-2">
                    Who is your target audience? *
                  </label>
                  <Input
                    value={formData.targetAudience}
                    onChange={(e) => updateFormData('targetAudience', e.target.value)}
                    placeholder="e.g., Small business owners, Freelancers, Students"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Business Details */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <Rocket className="w-12 h-12 text-accent mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-heading">Business Details</h2>
                <p className="text-body">Tell us about the business aspects</p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-heading mb-2">
                    Key Features *
                  </label>
                  <textarea
                    value={formData.keyFeatures}
                    onChange={(e) => updateFormData('keyFeatures', e.target.value)}
                    placeholder="List the main features your project should have"
                    className="w-full h-24 px-3 py-2 border border-stone-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-heading mb-2">
                    Business Model *
                  </label>
                  <select
                    value={formData.businessModel}
                    onChange={(e) => updateFormData('businessModel', e.target.value)}
                    aria-label="Business model"
                    className="w-full px-3 py-2 border border-stone-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent"
                  >
                    <option value="">Select business model</option>
                    {businessModels.map(model => (
                      <option key={model} value={model}>{model}</option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-heading mb-2">
                      Timeline
                    </label>
                    <select
                      value={formData.timeline}
                      onChange={(e) => updateFormData('timeline', e.target.value)}
                      aria-label="Project timeline"
                      className="w-full px-3 py-2 border border-stone-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent"
                    >
                      <option value="">Select timeline</option>
                      {timelines.map(timeline => (
                        <option key={timeline} value={timeline}>{timeline}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-heading mb-2">
                      Budget Range
                    </label>
                    <Input
                      value={formData.budget}
                      onChange={(e) => updateFormData('budget', e.target.value)}
                      placeholder="e.g., $1,000 - $5,000"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Error Display */}
          {submitError && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
              <div>
                <h4 className="font-medium text-red-800">Submission Error</h4>
                <p className="text-red-700 text-sm">{submitError}</p>
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex justify-between pt-6">
            <Button
              variant="outline"
              onClick={prevStep}
              disabled={currentStep === 1}
              className="btn-secondary"
            >
              Previous
            </Button>

            {currentStep < 3 ? (
              <Button
                onClick={nextStep}
                disabled={!validateStep(currentStep)}
                className="btn-primary"
              >
                Next
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            ) : (
              <Button
                onClick={handleSubmit}
                disabled={!validateStep(currentStep) || isSubmitting}
                className="btn-primary"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  <>
                    Submit Idea
                    <Sparkles className="w-4 h-4 ml-2" />
                  </>
                )}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 