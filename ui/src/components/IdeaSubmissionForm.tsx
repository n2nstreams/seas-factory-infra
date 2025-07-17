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
import { orchestratorApi, ApiError, type TenantContext } from "@/lib/api";

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
  onSubmit?: (data: IdeaFormData) => Promise<void>;
  tenantId?: string;
  userId?: string;
}

export default function IdeaSubmissionForm({ onSubmit, tenantId, userId }: IdeaSubmissionFormProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  
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

  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const handleInputChange = (field: keyof IdeaFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateStep = (step: number): boolean => {
    const newErrors: { [key: string]: string } = {};
    
    switch (step) {
      case 1:
        if (!formData.projectName.trim()) newErrors.projectName = 'Project name is required';
        if (!formData.description.trim()) newErrors.description = 'Description is required';
        if (!formData.category.trim()) newErrors.category = 'Category is required';
        break;
      case 2:
        if (!formData.problem.trim()) newErrors.problem = 'Problem description is required';
        if (!formData.solution.trim()) newErrors.solution = 'Solution description is required';
        if (!formData.targetAudience.trim()) newErrors.targetAudience = 'Target audience is required';
        break;
      case 3:
        if (!formData.keyFeatures.trim()) newErrors.keyFeatures = 'Key features are required';
        if (!formData.businessModel.trim()) newErrors.businessModel = 'Business model is required';
        break;
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, 4));
    }
  };

  const handlePrevious = () => {
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
        // Use the new API client with tenant context
        const tenantContext: TenantContext = {
          tenantId: tenantId || 'default',
          userId: userId || 'default-user'
        };

        const result = await orchestratorApi.submitIdea(formData, tenantContext);
        console.log('Idea submitted successfully:', result);
      }

      setSubmitSuccess(true);
      setCurrentStep(4);
    } catch (error) {
      console.error('Error submitting idea:', error);
      if (error instanceof ApiError) {
        setSubmitError(`Submission failed: ${error.message}`);
      } else {
        setSubmitError(error instanceof Error ? error.message : 'An unexpected error occurred');
      }
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

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Progress Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-stone-800">Submit Your Idea</h2>
          <Badge variant="outline" className="bg-white/20 backdrop-blur-sm border-stone-400/30">
            Step {currentStep} of 4
          </Badge>
        </div>
        <div className="w-full bg-stone-200/50 rounded-full h-2">
          <div 
            className="bg-gradient-to-r from-green-600 to-green-800 h-2 rounded-full transition-all duration-500"
            style={{ width: `${getStepProgress()}%` }}
          />
        </div>
      </div>

      <Card className="glass-card border border-stone-400/30 shadow-2xl">
        <CardContent className="p-8">
          {/* Step 1: Basic Information */}
          {currentStep === 1 && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <Lightbulb className="w-12 h-12 text-green-700 mx-auto mb-3" />
                <h3 className="text-xl font-semibold text-stone-800">Tell us about your idea</h3>
                <p className="text-stone-600">Let's start with the basics of your project</p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-2">
                    Project Name *
                  </label>
                  <Input
                    value={formData.projectName}
                    onChange={(e) => handleInputChange('projectName', e.target.value)}
                    placeholder="My Awesome SaaS Idea"
                    className="glass-input"
                  />
                  {errors.projectName && (
                    <p className="text-red-600 text-sm mt-1 flex items-center">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      {errors.projectName}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-2">
                    Brief Description *
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    placeholder="A brief overview of what your project is about..."
                    rows={3}
                    className="w-full px-3 py-2 border border-stone-300/50 rounded-md bg-white/20 backdrop-blur-sm focus:ring-2 focus:ring-green-600 focus:border-transparent resize-none"
                  />
                  {errors.description && (
                    <p className="text-red-600 text-sm mt-1 flex items-center">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      {errors.description}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-2">
                    Category *
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) => handleInputChange('category', e.target.value)}
                    aria-label="Project category"
                    className="w-full px-3 py-2 border border-stone-300/50 rounded-md bg-white/20 backdrop-blur-sm focus:ring-2 focus:ring-green-600 focus:border-transparent"
                  >
                    <option value="">Select a category</option>
                    {categories.map(category => (
                      <option key={category} value={category}>{category}</option>
                    ))}
                  </select>
                  {errors.category && (
                    <p className="text-red-600 text-sm mt-1 flex items-center">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      {errors.category}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Problem & Solution */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <Target className="w-12 h-12 text-green-700 mx-auto mb-3" />
                <h3 className="text-xl font-semibold text-stone-800">Problem & Solution</h3>
                <p className="text-stone-600">Define the problem you're solving and how</p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-2">
                    What problem are you solving? *
                  </label>
                  <textarea
                    value={formData.problem}
                    onChange={(e) => handleInputChange('problem', e.target.value)}
                    placeholder="Describe the specific problem or pain point you're addressing..."
                    rows={3}
                    className="w-full px-3 py-2 border border-stone-300/50 rounded-md bg-white/20 backdrop-blur-sm focus:ring-2 focus:ring-green-600 focus:border-transparent resize-none"
                  />
                  {errors.problem && (
                    <p className="text-red-600 text-sm mt-1 flex items-center">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      {errors.problem}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-2">
                    How does your solution solve this? *
                  </label>
                  <textarea
                    value={formData.solution}
                    onChange={(e) => handleInputChange('solution', e.target.value)}
                    placeholder="Explain how your solution addresses the problem..."
                    rows={3}
                    className="w-full px-3 py-2 border border-stone-300/50 rounded-md bg-white/20 backdrop-blur-sm focus:ring-2 focus:ring-green-600 focus:border-transparent resize-none"
                  />
                  {errors.solution && (
                    <p className="text-red-600 text-sm mt-1 flex items-center">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      {errors.solution}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-2">
                    Who is your target audience? *
                  </label>
                  <textarea
                    value={formData.targetAudience}
                    onChange={(e) => handleInputChange('targetAudience', e.target.value)}
                    placeholder="Describe your ideal users or customers..."
                    rows={2}
                    className="w-full px-3 py-2 border border-stone-300/50 rounded-md bg-white/20 backdrop-blur-sm focus:ring-2 focus:ring-green-600 focus:border-transparent resize-none"
                  />
                  {errors.targetAudience && (
                    <p className="text-red-600 text-sm mt-1 flex items-center">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      {errors.targetAudience}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Features & Business Model */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <Rocket className="w-12 h-12 text-green-700 mx-auto mb-3" />
                <h3 className="text-xl font-semibold text-stone-800">Features & Business Model</h3>
                <p className="text-stone-600">Define your key features and how you'll monetize</p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-2">
                    Key Features *
                  </label>
                  <textarea
                    value={formData.keyFeatures}
                    onChange={(e) => handleInputChange('keyFeatures', e.target.value)}
                    placeholder="List the main features your product will have..."
                    rows={3}
                    className="w-full px-3 py-2 border border-stone-300/50 rounded-md bg-white/20 backdrop-blur-sm focus:ring-2 focus:ring-green-600 focus:border-transparent resize-none"
                  />
                  {errors.keyFeatures && (
                    <p className="text-red-600 text-sm mt-1 flex items-center">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      {errors.keyFeatures}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-2">
                    Business Model *
                  </label>
                  <textarea
                    value={formData.businessModel}
                    onChange={(e) => handleInputChange('businessModel', e.target.value)}
                    placeholder="How will you make money? (subscription, one-time payment, freemium, etc.)"
                    rows={2}
                    className="w-full px-3 py-2 border border-stone-300/50 rounded-md bg-white/20 backdrop-blur-sm focus:ring-2 focus:ring-green-600 focus:border-transparent resize-none"
                  />
                  {errors.businessModel && (
                    <p className="text-red-600 text-sm mt-1 flex items-center">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      {errors.businessModel}
                    </p>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-stone-700 mb-2">
                      Timeline
                    </label>
                    <select
                      value={formData.timeline}
                      onChange={(e) => handleInputChange('timeline', e.target.value)}
                      aria-label="Project timeline"
                      className="w-full px-3 py-2 border border-stone-300/50 rounded-md bg-white/20 backdrop-blur-sm focus:ring-2 focus:ring-green-600 focus:border-transparent"
                    >
                      <option value="">Select timeline</option>
                      <option value="1-3 months">1-3 months</option>
                      <option value="3-6 months">3-6 months</option>
                      <option value="6-12 months">6-12 months</option>
                      <option value="12+ months">12+ months</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-stone-700 mb-2">
                      Priority Level
                    </label>
                    <select
                      value={formData.priority}
                      onChange={(e) => handleInputChange('priority', e.target.value as 'low' | 'medium' | 'high')}
                      aria-label="Project priority level"
                      className="w-full px-3 py-2 border border-stone-300/50 rounded-md bg-white/20 backdrop-blur-sm focus:ring-2 focus:ring-green-600 focus:border-transparent"
                    >
                      {priorities.map(priority => (
                        <option key={priority.value} value={priority.value}>
                          {priority.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-2">
                    Budget Range
                  </label>
                  <select
                    value={formData.budget}
                    onChange={(e) => handleInputChange('budget', e.target.value)}
                    aria-label="Budget range"
                    className="w-full px-3 py-2 border border-stone-300/50 rounded-md bg-white/20 backdrop-blur-sm focus:ring-2 focus:ring-green-600 focus:border-transparent"
                  >
                    <option value="">Select budget range</option>
                    <option value="$0 - $1,000">$0 - $1,000</option>
                    <option value="$1,000 - $5,000">$1,000 - $5,000</option>
                    <option value="$5,000 - $10,000">$5,000 - $10,000</option>
                    <option value="$10,000+">$10,000+</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Success */}
          {currentStep === 4 && (
            <div className="text-center space-y-6">
              {submitSuccess ? (
                <>
                  <CheckCircle className="w-16 h-16 text-green-600 mx-auto" />
                  <h3 className="text-2xl font-semibold text-stone-800">Idea Submitted Successfully!</h3>
                  <p className="text-stone-600">
                    Your idea has been submitted to our AI Factory. You'll receive updates as our agents
                    work on validating, designing, and building your project.
                  </p>
                  <div className="bg-green-50/50 backdrop-blur-sm border border-green-200/50 rounded-lg p-4">
                    <h4 className="font-semibold text-green-800 mb-2">What happens next?</h4>
                    <ul className="text-green-700 text-sm space-y-1 text-left">
                      <li>• Idea validation and market research</li>
                      <li>• Technology stack recommendation</li>
                      <li>• UI/UX design generation</li>
                      <li>• Code generation and testing</li>
                      <li>• Deployment and monitoring setup</li>
                    </ul>
                  </div>
                  <Button
                    onClick={() => window.location.href = '/dashboard'}
                    className="bg-gradient-to-r from-green-600 to-green-800 hover:from-green-700 hover:to-green-900"
                  >
                    View Dashboard
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </>
              ) : (
                <>
                  <AlertCircle className="w-16 h-16 text-red-500 mx-auto" />
                  <h3 className="text-2xl font-semibold text-stone-800">Submission Failed</h3>
                  <p className="text-stone-600">{submitError}</p>
                  <Button
                    onClick={() => setCurrentStep(3)}
                    variant="outline"
                    className="bg-white/20 backdrop-blur-sm border-stone-400/50"
                  >
                    Try Again
                  </Button>
                </>
              )}
            </div>
          )}

          {/* Navigation Buttons */}
          {currentStep < 4 && (
            <div className="flex justify-between items-center mt-8 pt-6 border-t border-stone-300/30">
              <Button
                onClick={handlePrevious}
                disabled={currentStep === 1}
                variant="outline"
                className="bg-white/20 backdrop-blur-sm border-stone-400/50 disabled:opacity-50"
              >
                Previous
              </Button>

              {currentStep < 3 ? (
                <Button
                  onClick={handleNext}
                  className="bg-gradient-to-r from-green-600 to-green-800 hover:from-green-700 hover:to-green-900"
                >
                  Next
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              ) : (
                <Button
                  onClick={handleSubmit}
                  disabled={isSubmitting}
                  className="bg-gradient-to-r from-green-600 to-green-800 hover:from-green-700 hover:to-green-900"
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
          )}
        </CardContent>
      </Card>
    </div>
  );
} 