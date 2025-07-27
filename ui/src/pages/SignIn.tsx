import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { 
  Mail, 
  Lock, 
  Github, 
  Eye, 
  EyeOff, 
  ArrowRight,
  LogIn,
  Code2
} from 'lucide-react';

interface SignInFormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

export default function SignIn() {
  const [formData, setFormData] = useState<SignInFormData>({
    email: '',
    password: '',
    rememberMe: false
  });

  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Partial<SignInFormData & { submit: string }>>({});

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // Clear error when user starts typing
    if (errors[name as keyof typeof errors]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<SignInFormData & { submit: string }> = {};

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!formData.password.trim()) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsSubmitting(true);
    setErrors({});

    try {
      // TODO: Implement actual sign-in logic
      console.log('Signing in with:', formData);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Redirect to dashboard on success
      window.location.href = '/dashboard';
    } catch (error) {
      console.error('Sign in error:', error);
      setErrors({ submit: 'Invalid email or password. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSocialLogin = (provider: string) => {
    console.log(`Initiating ${provider} OAuth flow`);
    
    // OAuth configuration
    const oauthConfigs = {
      github: {
        clientId: 'your_github_client_id',
        redirectUri: `${window.location.origin}/auth/callback/github`,
        scope: 'user:email',
        authUrl: 'https://github.com/login/oauth/authorize'
      },
      google: {
        clientId: 'your_google_client_id',
        redirectUri: `${window.location.origin}/auth/callback/google`,
        scope: 'openid email profile',
        authUrl: 'https://accounts.google.com/oauth2/v2/auth'
      }
    };

    const config = oauthConfigs[provider as keyof typeof oauthConfigs];
    
    if (!config) {
      console.error(`Unsupported OAuth provider: ${provider}`);
      return;
    }

    try {
      // Store current path for redirect after authentication
      sessionStorage.setItem('oauth_redirect_path', window.location.pathname);
      
      // Build OAuth URL
      const params = new URLSearchParams({
        client_id: config.clientId,
        redirect_uri: config.redirectUri,
        scope: config.scope,
        response_type: 'code',
        state: btoa(JSON.stringify({ provider, timestamp: Date.now() }))
      });

      const oauthUrl = `${config.authUrl}?${params.toString()}`;
      
      // For development/demo purposes, show what would happen
      if (import.meta.env.DEV) {
        console.log(`Would redirect to: ${oauthUrl}`);
        alert(`OAuth flow initiated for ${provider}!\n\nIn production, this would redirect to:\n${oauthUrl}\n\nFor demo purposes, redirecting to dashboard...`);
        
        // Simulate successful authentication
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 1000);
        return;
      }

      // In production, redirect to OAuth provider
      window.location.href = oauthUrl;
      
    } catch (error) {
      console.error(`${provider} OAuth error:`, error);
      setErrors({ 
        submit: `Failed to initiate ${provider} authentication. Please try again.` 
      });
    }
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

      <div className="flex min-h-screen items-center justify-center px-4 py-12 relative z-10">
        <div className="w-full max-w-md">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center mb-4">
              <div className="w-16 h-16 bg-gradient-to-r from-green-800 to-green-900 rounded-2xl flex items-center justify-center shadow-2xl">
                <Code2 className="w-8 h-8 text-white" />
              </div>
            </div>
            <h1 className="text-3xl font-bold text-heading mb-2">Welcome Back!</h1>
                            <p className="text-body">Sign in to your Forge95 account</p>
          </div>

          <Card className="card-glass">
            <CardHeader className="text-center space-y-2">
              <div className="w-12 h-12 bg-accent-icon rounded-xl flex items-center justify-center mx-auto">
                <LogIn className="w-6 h-6 text-white" />
              </div>
              <CardTitle className="text-xl font-bold text-heading">Sign In</CardTitle>
            </CardHeader>

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
                  <span className="bg-white px-2 text-muted">Or sign in with email</span>
                </div>
              </div>

              {/* Sign In Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <label htmlFor="email" className="text-sm font-medium text-heading">
                    Email Address
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-stone-400" />
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      className="pl-10"
                      placeholder="your@email.com"
                    />
                  </div>
                  {errors.email && <p className="text-red-500 text-xs">{errors.email}</p>}
                </div>

                <div className="space-y-2">
                  <label htmlFor="password" className="text-sm font-medium text-heading">
                    Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 h-4 w-4 text-stone-400" />
                    <Input
                      id="password"
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      value={formData.password}
                      onChange={handleInputChange}
                      className="pl-10 pr-10"
                      placeholder="Enter your password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-3 text-stone-400 hover:text-stone-600"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                  {errors.password && <p className="text-red-500 text-xs">{errors.password}</p>}
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="rememberMe"
                      name="rememberMe"
                      checked={formData.rememberMe}
                      onChange={handleInputChange}
                      className="h-4 w-4 text-green-800 focus:ring-green-800 border-stone-300 rounded"
                    />
                    <label htmlFor="rememberMe" className="text-sm text-body">
                      Remember me
                    </label>
                  </div>
                  <a href="/forgot-password" className="text-sm text-accent hover:underline">
                    Forgot password?
                  </a>
                </div>

                {errors.submit && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-600 text-sm">{errors.submit}</p>
                  </div>
                )}

                <Button 
                  type="submit" 
                  className="w-full btn-primary"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Signing in...' : 'Sign In'}
                  {!isSubmitting && <ArrowRight className="w-4 h-4 ml-2" />}
                </Button>
              </form>

              {/* Sign Up Link */}
              <div className="text-center pt-4">
                <p className="text-sm text-body">
                  Don't have an account?{' '}
                  <a href="/signup" className="text-accent hover:underline font-medium">
                    Get started for free
                  </a>
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Additional Links */}
          <div className="text-center mt-8 space-y-2">
            <p className="text-sm text-body">
              Need help? <a href="/support" className="text-accent hover:underline">Contact Support</a>
            </p>
            <div className="flex items-center justify-center space-x-4 text-xs text-muted">
              <a href="/privacy" className="hover:text-body">Privacy Policy</a>
              <span>•</span>
              <a href="/terms" className="hover:text-body">Terms of Service</a>
            </div>
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