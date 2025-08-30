import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Code2,
  Eye,
  EyeOff,
  Shield,
  Sparkles,
  Github,
  Mail,
  Lock,
  User,
  CheckCircle,
  ArrowRight,
  Users,
  Zap,
  Star,
  TrendingUp,
  Loader2,
  ShoppingCart,
  Info
} from "lucide-react";
import { authApi, marketplaceApi } from '@/lib/api';
import { useAuth } from '@/App';
import { useNavigate } from 'react-router-dom';

interface SelectedProduct {
  id: string;
  name: string;
  price: string;
  category: string;
}

export default function Signup() {
  const { setUser } = useAuth();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [registrationSuccess, setRegistrationSuccess] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<SelectedProduct | null>(null);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false
  });
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    
    // Prevent checkbox from being unchecked during submission
    if (type === 'checkbox' && name === 'agreeToTerms' && isSubmitting) {
      return;
    }
    
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }

    // Clear submit error when user makes changes
    if (errors.submit) {
      setErrors(prev => ({ ...prev, submit: '' }));
    }
  };

  // Parse URL parameters and load selected product
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const productId = urlParams.get('product');
    const productName = urlParams.get('productName');

    if (productId && productName) {
      // Product info from URL parameters
      setSelectedProduct({
        id: productId,
        name: productName,
        price: urlParams.get('price') || '$29/month',
        category: urlParams.get('category') || 'Productivity'
      });
    } else if (productId) {
      // Load product details from API
      loadProductDetails(productId);
    }
  }, []);

  const loadProductDetails = async (productId: string) => {
    try {
      const productData = await marketplaceApi.getProduct(productId);
      setSelectedProduct({
        id: productData.id,
        name: productData.name,
        price: productData.price,
        category: productData.category
      });
    } catch (error) {
      console.error('Error loading product details:', error);
    }
  };

  const validateForm = () => {
    const newErrors: { [key: string]: string } = {};
    
    if (!formData.firstName.trim()) newErrors.firstName = 'First name is required';
    if (!formData.lastName.trim()) newErrors.lastName = 'Last name is required';
    if (!formData.email.trim()) newErrors.email = 'Email is required';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) newErrors.email = 'Please enter a valid email';
    if (!formData.password) newErrors.password = 'Password is required';
    if (formData.password.length < 8) newErrors.password = 'Password must be at least 8 characters';
    if (formData.password !== formData.confirmPassword) newErrors.confirmPassword = 'Passwords do not match';
    if (!formData.agreeToTerms) newErrors.agreeToTerms = 'You must agree to the terms';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Clear any previous errors
    setErrors({});
    
    if (validateForm()) {
      try {
        setIsSubmitting(true);
        
        // Submit registration using the new authApi
        const result = await authApi.register(formData);
        console.log('Registration successful:', result);
        
        // Set user data in auth context
        const userData = {
          id: result.id,
          name: result.name,
          email: result.email,
          plan: result.plan || 'starter',
          buildHours: {
            used: 0,
            total: result.plan === 'pro' ? 'unlimited' as const : 42
          }
        };

        setUser(userData);

        // Show success message and redirect
        setRegistrationSuccess(true);

        // Redirect to dashboard after 2 seconds
        setTimeout(() => {
          navigate('/dashboard');
        }, 2000);
        
      } catch (error: any) {
        console.error('Registration error:', error);
        
        // Handle different types of errors
        let errorMessage = 'Registration failed. Please try again.';

        if (error.status === 400) {
          errorMessage = error.data?.detail || 'Invalid registration data. Please check your information.';
        } else if (error.status === 409) {
          errorMessage = 'A user with this email already exists. Please try logging in instead.';
        } else if (error.status === 422) {
          errorMessage = 'Please check your information and try again.';
        } else if (error.status === 500) {
          errorMessage = 'Server error. Please try again in a few moments.';
        } else if (error.status === 0) {
          errorMessage = 'Network error. Please check your connection and try again.';
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        setErrors({ submit: errorMessage });
      } finally {
        setIsSubmitting(false);
      }
    }
  };

  const handleSocialLogin = (provider: string) => {
    console.log(`Initiating ${provider} OAuth flow for signup`);
    
          // OAuth configuration - use environment variables or defaults
      const oauthConfigs = {
        github: {
          clientId: import.meta.env.VITE_GITHUB_CLIENT_ID || 'Ov23liagpTNOZSHGv2Ym',
          redirectUri: `http://localhost:8000/auth/github`,
          scope: 'user:email',
          authUrl: 'https://github.com/login/oauth/authorize'
        },
        google: {
          clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID || '60641742068-5oi9ipvfkjf0l80sm0cmqvhogul6udk9.apps.googleusercontent.com',
          redirectUri: `http://localhost:8000/auth/google`,
        scope: 'openid email profile',
        authUrl: 'https://accounts.google.com/oauth2/v2/auth'
      }
    };

    const config = oauthConfigs[provider as keyof typeof oauthConfigs];
    
    if (!config) {
      console.error(`Unsupported OAuth provider: ${provider}`);
      return;
    }

    // Check if OAuth is properly configured
    if (config.clientId === 'your_github_client_id' || config.clientId === 'your_google_client_id') {
      console.error(`${provider} OAuth not configured. Please set VITE_${provider.toUpperCase()}_CLIENT_ID environment variable.`);
      alert(`${provider} OAuth is not configured. Please contact support.`);
      return;
    }

    try {
      // Store signup intent for OAuth flow
      sessionStorage.setItem('oauth_signup_intent', 'true');
      sessionStorage.setItem('oauth_redirect_path', '/dashboard');
      
      // Build OAuth URL with proper parameters
      const params = new URLSearchParams({
        client_id: config.clientId,
        redirect_uri: config.redirectUri,
        scope: config.scope,
        response_type: 'code',
        ...(provider === 'google' && {
          access_type: 'offline',
          prompt: 'consent'
        })
      });
      
      const oauthUrl = `${config.authUrl}?${params.toString()}`;
      console.log(`Redirecting to ${provider} OAuth for signup: ${oauthUrl}`);
      
      // Redirect to OAuth provider
      window.location.href = oauthUrl;
      
    } catch (error) {
      console.error(`Error initiating ${provider} OAuth for signup:`, error);
      alert(`Failed to start ${provider} signup. Please try again.`);
    }
  };

  const passwordStrength = (password: string) => {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    return strength;
  };

  const getPasswordStrengthColor = (strength: number) => {
    if (strength <= 2) return 'bg-red-700';
    if (strength <= 3) return 'bg-stone-600';
    if (strength <= 4) return 'bg-green-800';
    return 'bg-green-900';
  };

  const getPasswordStrengthText = (strength: number) => {
    if (strength <= 2) return 'Weak';
    if (strength <= 3) return 'Fair';
    if (strength <= 4) return 'Good';
    return 'Strong';
  };

  return (
    <div className="min-h-screen bg-homepage relative overflow-hidden">
      {/* Glassmorphism Background Elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-br from-green-800/20 to-green-900/25 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-40 right-32 w-80 h-80 bg-gradient-to-bl from-slate-700/20 to-green-800/25 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 left-1/3 w-64 h-64 bg-gradient-to-tr from-stone-600/20 to-green-700/25 rounded-full blur-3xl animate-pulse delay-2000"></div>
        <div className="absolute bottom-32 right-20 w-72 h-72 bg-gradient-to-tl from-green-800/20 to-stone-700/25 rounded-full blur-3xl animate-pulse delay-3000"></div>
      </div>



      <div className="flex min-h-screen relative">
        {/* Left Sidebar - Benefits */}
        <div className="hidden lg:flex flex-col w-1/2 p-12 relative">
          <div className="flex-1 flex flex-col justify-center space-y-8">
            <div className="space-y-6">
              <Badge className="glass-button w-fit">
                <Sparkles className="w-4 h-4 mr-2" />
                Join 10,000+ Entrepreneurs
              </Badge>
              <h1 className="text-4xl lg:text-5xl font-bold text-heading leading-tight">
                Build Your{" "}
                <span className="text-accent">
                  AI-Powered
                </span>{" "}
                SaaS Business
              </h1>
              <p className="text-xl text-body leading-relaxed">
                From idea to live business in hours. Our AI factory handles the complex stuff so you can focus on what matters.
              </p>
            </div>

            <div className="space-y-6">
              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-accent-icon rounded-xl flex items-center justify-center shadow-lg">
                  <Zap className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-heading">Lightning Fast Setup</h3>
                  <p className="text-body">Your complete SaaS platform deployed in under 24 hours</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-accent-secondary rounded-xl flex items-center justify-center shadow-lg">
                  <Shield className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-heading">Enterprise Security</h3>
                  <p className="text-body">Bank-level security with SOC 2 compliance built-in</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-accent-tertiary rounded-xl flex items-center justify-center shadow-lg">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-heading">Scale Automatically</h3>
                  <p className="text-body">AI-powered infrastructure that grows with your business</p>
                </div>
              </div>
            </div>

            <div className="glass-card p-6 space-y-4">
              <div className="flex items-center space-x-3">
                <div className="flex -space-x-2">
                  <div className="w-8 h-8 bg-accent rounded-full border-2 border-white flex items-center justify-center">
                    <User className="w-4 h-4 text-white" />
                  </div>
                  <div className="w-8 h-8 bg-accent-secondary rounded-full border-2 border-white flex items-center justify-center">
                    <User className="w-4 h-4 text-white" />
                  </div>
                  <div className="w-8 h-8 bg-accent-tertiary rounded-full border-2 border-white flex items-center justify-center">
                    <User className="w-4 h-4 text-white" />
                  </div>
                </div>
                <div>
                  <div className="text-sm text-heading font-medium">10,000+ founders building</div>
                  <div className="text-xs text-body">Average time to first customer: 3 days</div>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex space-x-1">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                  ))}
                </div>
                <span className="text-sm text-body">4.9/5 average rating</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Form */}
        <div className="flex-1 lg:w-1/2 p-8 lg:p-12 flex items-center justify-center">
          <Card className="w-full max-w-md card-glass">
            <CardHeader className="text-center space-y-4">
              <div className="w-16 h-16 bg-accent-icon rounded-2xl flex items-center justify-center mx-auto shadow-lg">
                <Users className="w-8 h-8 text-white" />
              </div>
              <div>
                <CardTitle className="text-2xl font-bold text-heading">Create Your Account</CardTitle>
                <p className="text-body mt-2">Start building your SaaS business today</p>
              </div>
            </CardHeader>

            {/* Selected Product Display */}
            {selectedProduct && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-start space-x-3">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <ShoppingCart className="w-5 h-5 text-green-800" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold text-green-900">Selected Product</h4>
                      <Badge variant="outline" className="text-green-700 border-green-300">
                        {selectedProduct.category}
                      </Badge>
                    </div>
                    <p className="text-green-800 font-medium">{selectedProduct.name}</p>
                    <p className="text-green-700 text-sm">{selectedProduct.price}</p>
                    <div className="mt-2 flex items-center space-x-1 text-green-700 text-sm">
                      <Info className="w-4 h-4" />
                      <span>Complete signup to get started with this product</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <CardContent className="space-y-6">
              {/* Social Login */}
              <div className="space-y-3">
                <Button 
                  variant="outline" 
                  className="w-full btn-secondary"
                  onClick={() => handleSocialLogin('github')}
                >
                  <Github className="w-5 h-5 mr-2" />
                  Continue with GitHub
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full btn-secondary"
                  onClick={() => handleSocialLogin('google')}
                >
                  <Mail className="w-5 h-5 mr-2" />
                  Continue with Google
                </Button>
              </div>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <Separator className="w-full" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-white px-2 text-muted">Or continue with email</span>
                </div>
              </div>

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-heading mb-1">
                      First Name
                    </label>
                    <Input
                      type="text"
                      name="firstName"
                      value={formData.firstName}
                      onChange={handleInputChange}
                      placeholder="John"
                      className="glass-input"
                    />
                    {errors.firstName && <p className="text-red-500 text-xs mt-1">{errors.firstName}</p>}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-heading mb-1">
                      Last Name
                    </label>
                    <Input
                      type="text"
                      name="lastName"
                      value={formData.lastName}
                      onChange={handleInputChange}
                      placeholder="Doe"
                      className="glass-input"
                    />
                    {errors.lastName && <p className="text-red-500 text-xs mt-1">{errors.lastName}</p>}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-heading mb-1">
                    Email Address
                  </label>
                  <Input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder="john@example.com"
                    className="glass-input"
                  />
                  {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-heading mb-1">
                    Password
                  </label>
                  <div className="relative">
                    <Input
                      type={showPassword ? "text" : "password"}
                      name="password"
                      value={formData.password}
                      onChange={handleInputChange}
                      placeholder="Create a strong password"
                      className="glass-input pr-10"
                    />
                    <button
                      type="button"
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted hover:text-heading transition-colors"
                      onClick={() => setShowPassword(!showPassword)}
                      aria-label={showPassword ? "Hide password" : "Show password"}
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                  {formData.password && (
                    <div className="mt-2 space-y-1">
                      <div className="progress-bar">
                        <div 
                          className={`h-3 rounded-full transition-all duration-300 ${getPasswordStrengthColor(passwordStrength(formData.password))}`}
                          style={{ width: `${(passwordStrength(formData.password) / 5) * 100}%` }}
                        />
                      </div>
                      <p className="text-xs text-body">
                        Password strength: {getPasswordStrengthText(passwordStrength(formData.password))}
                      </p>
                    </div>
                  )}
                  {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-heading mb-1">
                    Confirm Password
                  </label>
                  <div className="relative">
                    <Input
                      type={showConfirmPassword ? "text" : "password"}
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      placeholder="Confirm your password"
                      className="glass-input pr-10"
                    />
                    <button
                      type="button"
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted hover:text-heading transition-colors"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      aria-label={showConfirmPassword ? "Hide confirm password" : "Show confirm password"}
                    >
                      {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                  {formData.confirmPassword && formData.password === formData.confirmPassword && (
                    <div className="flex items-center space-x-2 mt-1">
                                      <CheckCircle className="w-4 h-4 text-green-800" />
                <span className="text-xs text-green-800">Passwords match</span>
                    </div>
                  )}
                  {errors.confirmPassword && <p className="text-red-500 text-xs mt-1">{errors.confirmPassword}</p>}
                </div>

                <div className="space-y-3">
                  <div className="flex items-start space-x-3">
                    <input
                      type="checkbox"
                      id="agreeToTerms"
                      name="agreeToTerms"
                      checked={formData.agreeToTerms}
                      onChange={handleInputChange}
                      className={`mt-1 h-5 w-5 focus:ring-2 focus:ring-green-800 focus:ring-offset-2 border rounded cursor-pointer ${
                        errors.agreeToTerms ? 'border-red-500 text-red-500' : 'border-stone-300 text-green-800'
                      }`}
                      aria-describedby="terms-description"
                    />
                    <label htmlFor="agreeToTerms" className="text-sm text-body cursor-pointer leading-relaxed">
                      I agree to the{" "}
                      <a href="/terms" className="text-accent hover:underline font-medium" target="_blank" rel="noopener noreferrer">
                        Terms of Service
                      </a>{" "}
                      and{" "}
                      <a href="/privacy" className="text-accent hover:underline font-medium" target="_blank" rel="noopener noreferrer">
                        Privacy Policy
                      </a>
                      <span id="terms-description" className="sr-only">
                        You must agree to the terms and privacy policy to continue
                      </span>
                    </label>
                  </div>
                  {errors.agreeToTerms && <p className="text-red-500 text-xs ml-8">{errors.agreeToTerms}</p>}
                </div>

                <Button 
                  type="submit" 
                  className="w-full btn-primary"
                  disabled={!formData.agreeToTerms || isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Creating Account...
                    </>
                  ) : (
                    <>
                      Create Account
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </>
                  )}
                </Button>
                
                {errors.submit && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
                    <p className="text-red-800 text-sm font-medium mb-2">{errors.submit}</p>
                    {errors.submit.includes('email already exists') && (
                      <Button
                        variant="link"
                        className="text-red-700 hover:text-red-800 p-0 h-auto"
                        onClick={() => window.location.href = '/signin'}
                      >
                        Click here to sign in instead
                      </Button>
                    )}
                    {errors.submit.includes('Network error') && (
                      <Button
                        variant="link"
                        className="text-red-700 hover:text-red-800 p-0 h-auto"
                        onClick={() => window.location.reload()}
                      >
                        Try again
                      </Button>
                    )}
                  </div>
                )}

                {registrationSuccess && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                    <div className="flex items-center justify-center mb-2">
                      <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                      <p className="text-green-800 text-sm font-medium">Account created successfully!</p>
                    </div>
                    <p className="text-green-700 text-sm">Redirecting to your dashboard...</p>
                  </div>
                )}
              </form>

              <div className="text-center">
                <p className="text-sm text-body">
                  Already have an account?{" "}
                  <a href="#" className="text-accent hover:underline font-medium">
                    Sign in
                  </a>
                </p>
              </div>

              {/* Trust Indicators */}
              <div className="glass-card p-4 space-y-3">
                <div className="flex items-center space-x-3">
                  <Shield className="w-5 h-5 text-accent" />
                  <div>
                    <p className="text-sm font-medium text-heading">Enterprise Security</p>
                    <p className="text-xs text-body">SOC 2 compliant with 256-bit encryption</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <Lock className="w-5 h-5 text-accent" />
                  <div>
                    <p className="text-sm font-medium text-heading">Data Protection</p>
                    <p className="text-xs text-body">GDPR compliant with automatic backups</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-stone-900/95 backdrop-blur-lg text-white py-8 border-t border-stone-400/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <div className="w-8 h-8 bg-accent-icon rounded-lg flex items-center justify-center shadow-lg">
                <Code2 className="w-5 h-5 text-white" />
              </div>
                              <span className="text-lg font-bold">Forge95</span>
            </div>
            <div className="flex space-x-6 text-sm text-stone-300">
              <a href="/privacy" className="hover:text-white transition-colors">Privacy Policy</a>
              <a href="/terms" className="hover:text-white transition-colors">Terms of Service</a>
              <a href="mailto:support@forge95.com" className="hover:text-white transition-colors">Support</a>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-stone-700/50 text-center text-stone-400 text-sm">
                            <p>&copy; 2025 Forge95. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
} 