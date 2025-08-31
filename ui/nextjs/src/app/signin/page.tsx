"use client";

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/features/ui/separator";
import { authApi, tenantUtils } from '@/lib/api';
import { useAuth } from '@/components/providers/AuthProvider';
import { supabase } from '@/lib/supabase';
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
import { useRouter } from 'next/navigation';
import { Label } from '@/components/ui/label';
import { Loader2 } from 'lucide-react';

interface SignInFormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

export default function SignIn() {
  const { setUser } = useAuth();
  const router = useRouter();

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
      // Initialize tenant context
      tenantUtils.initializeTenantContext();

      // Call the actual backend API
      const result = await authApi.login({
        email: formData.email,
        password: formData.password
      });

      console.log('Login successful:', result);

      // Set user data in auth context
      if (result.id) {
        const userData = {
          id: result.id,
          email: result.email,
          name: result.name || formData.email,
          plan: result.plan || 'starter',
          buildHours: {
            used: 0,
            total: result.plan === 'pro' ? 'unlimited' as const : 42
          }
        };

        setUser(userData);

        // Navigate to dashboard using Next.js router
        router.push('/dashboard');
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('Sign in error:', error);
      setErrors({ submit: 'Invalid email or password. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSocialLogin = async (provider: string) => {
    console.log(`Initiating ${provider} OAuth flow via Supabase`);
    
    try {
      // Store current path for redirect after authentication
      sessionStorage.setItem('oauth_redirect_path', window.location.pathname);
      
      // Use Supabase OAuth for social login
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: provider as 'github' | 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`
        }
      });
      
      if (error) {
        console.error(`Error initiating ${provider} OAuth:`, error);
        alert(`Failed to start ${provider} authentication. Please try again.`);
        return;
      }
      
      console.log(`Successfully initiated ${provider} OAuth flow`);
      
    } catch (error) {
      console.error(`Error initiating ${provider} OAuth:`, error);
      alert(`Failed to start ${provider} authentication. Please try again.`);
    }
  };

  return (
    <div className="min-h-screen bg-homepage relative overflow-hidden">
      {/* Glassmorphism Background Elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-br from-stone-800/20 to-stone-900/25 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-40 right-32 w-80 h-80 bg-gradient-to-bl from-stone-700/20 to-stone-800/25 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 left-1/3 w-64 h-64 bg-gradient-to-tr from-stone-600/20 to-stone-700/25 rounded-full blur-3xl animate-pulse delay-2000"></div>
        <div className="absolute bottom-32 right-20 w-72 h-72 bg-gradient-to-tl from-stone-800/20 to-stone-700/25 rounded-full blur-3xl animate-pulse delay-3000"></div>
      </div>

      {/* Main Content */}
      <div className="flex min-h-screen items-center justify-center px-4 py-12 relative z-10">
        <div className="w-full max-w-md">
          {/* Logo */}
          <div className="flex items-center justify-center mb-4">
            <div className="w-16 h-16 bg-gradient-to-r from-stone-800 to-stone-900 rounded-2xl flex items-center justify-center shadow-2xl">
              <Code2 className="w-8 h-8 text-white" />
            </div>
          </div>

          {/* Brand Name */}
          <div className="text-center mb-8">
            <div className="w-12 h-12 bg-accent-icon rounded-xl flex items-center justify-center mx-auto">
              <Code2 className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-stone-900 mt-4">AI SaaS Factory</h1>
            <p className="text-stone-600 mt-2">Sign in to your account</p>
          </div>

          {/* Sign In Form */}
          <Card className="glass-card border border-stone-300/50 shadow-2xl">
            <CardContent className="p-8">
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Email Field */}
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-stone-700 font-medium">
                    Email
                  </Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-stone-400" />
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      placeholder="Enter your email"
                      className="pl-10 bg-white/50 backdrop-blur-sm border border-stone-300/50 text-stone-800 placeholder-stone-500 focus:border-stone-500 focus:ring-2 focus:ring-stone-500/20"
                      required
                    />
                  </div>
                </div>

                {/* Password Field */}
                <div className="space-y-2">
                  <Label htmlFor="password" className="text-stone-700 font-medium">
                    Password
                  </Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 h-4 w-4 text-stone-400" />
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      value={formData.password}
                      onChange={handleInputChange}
                      placeholder="Enter your password"
                      className="pl-10 bg-white/50 backdrop-blur-sm border border-stone-300/50 text-stone-800 placeholder-stone-500 focus:ring-stone-500 focus:ring-2 focus:ring-stone-500/20"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-3 text-stone-400 hover:text-stone-600"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                {/* Remember Me & Forgot Password */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="remember"
                      name="rememberMe"
                      checked={formData.rememberMe}
                      onChange={handleInputChange}
                      className="h-4 w-4 text-stone-800 focus:ring-stone-800 border-stone-300 rounded"
                      aria-label="Remember me"
                    />
                    <Label htmlFor="remember" className="text-sm text-stone-600">
                      Remember me
                    </Label>
                  </div>
                  <a href="#" className="text-sm text-stone-700 hover:text-stone-800 font-medium">
                    Forgot password?
                  </a>
                </div>

                {/* Sign In Button */}
                <Button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full bg-gradient-to-r from-stone-800 to-stone-900 hover:from-stone-900 hover:to-stone-800 text-white font-semibold py-3 px-4 rounded-lg shadow-lg backdrop-blur-sm border border-stone-400/40 transition-all duration-300 hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Signing in...
                    </>
                  ) : (
                    "Sign In"
                  )}
                </Button>

                {/* Divider */}
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-white px-2 text-stone-500">Or continue with</span>
                  <Separator className="absolute inset-0 -z-10" />
                </div>

                {/* Social Login Buttons */}
                <div className="grid grid-cols-2 gap-3">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => handleSocialLogin('github')}
                    disabled={isSubmitting}
                    className="bg-white/50 backdrop-blur-sm border border-stone-300/50 text-stone-800 hover:bg-white/70 hover:border-stone-400/60 transition-all duration-300"
                  >
                    <Github className="w-4 h-4 mr-2" />
                    GitHub
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => handleSocialLogin('google')}
                    disabled={isSubmitting}
                    className="bg-white/50 backdrop-blur-sm border border-stone-300/50 text-stone-800 hover:bg-white/70 hover:border-stone-400/60 transition-all duration-300"
                  >
                    <Mail className="w-4 h-4 mr-2" />
                    Google
                  </Button>
                </div>

                {/* Error Message */}
                {errors.submit && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-600 text-sm">{errors.submit}</p>
                  </div>
                )}
              </form>
            </CardContent>
          </Card>

          {/* Sign Up Link */}
          <div className="text-center mt-6">
            <p className="text-stone-600">
              Don't have an account?{" "}
              <a href="/signup" className="text-stone-700 hover:text-stone-800 font-medium underline">
                Sign up
              </a>
            </p>
          </div>

          {/* Additional Info */}
          <div className="mt-8 text-center">
            <div className="flex items-center justify-center space-x-4 text-xs text-stone-500">
              <span>🔒 Enterprise-grade security</span>
              <span>⚡ Lightning fast</span>
              <span>🚀 AI-powered</span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-stone-900/95 backdrop-blur-lg text-white py-12 border-t border-stone-400/30 absolute bottom-0 w-full">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <div className="w-10 h-10 bg-gradient-to-r from-stone-800 to-stone-900 rounded-xl flex items-center justify-center shadow-lg">
                  <Code2 className="w-6 h-6 text-white" />
                </div>
                <span className="text-lg font-bold">AI SaaS Factory</span>
              </div>
              <p className="text-stone-300">
                Modern, Clean Architecture for AI-Powered SaaS Applications
              </p>
            </div>

            <div className="space-y-4">
              <h4 className="font-semibold mb-4 text-stone-200">Product</h4>
              <div className="space-y-2 text-stone-400">
                <a href="/dashboard" className="block hover:text-white transition-colors">Dashboard</a>
                <a href="/pricing" className="block hover:text-white transition-colors">Pricing</a>
                <a href="/docs" className="block hover:text-white transition-colors">Documentation</a>
                <a href="/api" className="block hover:text-white transition-colors">API</a>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-semibold mb-4 text-stone-200">Company</h4>
              <div className="space-y-2 text-stone-400">
                <a href="/about" className="block hover:text-white transition-colors">About</a>
                <a href="/blog" className="block hover:text-white transition-colors">Blog</a>
                <a href="/careers" className="block hover:text-white transition-colors">Careers</a>
                <a href="/contact" className="block hover:text-white transition-colors">Contact</a>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-semibold mb-4 text-stone-200">Support</h4>
              <div className="space-y-2 text-stone-400">
                <a href="/help" className="block hover:text-white transition-colors">Help Center</a>
                <a href="/status" className="block hover:text-white transition-colors">Status</a>
                <a href="/security" className="block hover:text-white transition-colors">Security</a>
                <a href="/privacy" className="block hover:text-white transition-colors">Privacy</a>
              </div>
            </div>
          </div>

          <div className="border-t border-stone-700/50 mt-8 pt-8 text-center text-stone-300">
            <p>&copy; 2025 AI SaaS Factory. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
} 