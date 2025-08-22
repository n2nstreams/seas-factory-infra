import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '@/App';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function OAuthSuccess() {
  const { setUser } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    const token = searchParams.get('token');
    const error = searchParams.get('error');

    if (error) {
      setStatus('error');
      setErrorMessage(error);
      return;
    }

    if (!token) {
      setStatus('error');
      setErrorMessage('No authentication token received');
      return;
    }

    // Process the OAuth token
    processOAuthToken(token);
  }, [searchParams]);

  const processOAuthToken = async (token: string) => {
    try {
      // Store token in localStorage
      localStorage.setItem('authToken', token);
      
      // Decode JWT token to get user info (client-side only for display)
      const tokenPayload = JSON.parse(atob(token.split('.')[1]));
      
      // Create user object from token
      const userData = {
        id: tokenPayload.user_id,
        email: tokenPayload.email,
        name: tokenPayload.name || 'OAuth User',
        role: tokenPayload.role || 'user',
        plan: 'starter' as const, // Default plan for OAuth users
        buildHours: {
          used: 0,
          total: 42
        }
      };

      // Set user in auth context
      setUser(userData);
      
      setStatus('success');
      
      // Redirect after a short delay
      setTimeout(() => {
        const redirectPath = sessionStorage.getItem('oauth_redirect_path') || '/dashboard';
        sessionStorage.removeItem('oauth_redirect_path');
        sessionStorage.removeItem('oauth_signup_intent');
        navigate(redirectPath);
      }, 2000);
      
    } catch (error) {
      console.error('Error processing OAuth token:', error);
      setStatus('error');
      setErrorMessage('Failed to process authentication token');
    }
  };

  const handleRetry = () => {
    // Clear any stored OAuth data and redirect to signin
    sessionStorage.removeItem('oauth_redirect_path');
    sessionStorage.removeItem('oauth_signup_intent');
    navigate('/signin');
  };

  const handleGoHome = () => {
    navigate('/');
  };

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-green-100">
        <Card className="w-full max-w-md glass-card">
          <CardContent className="p-8 text-center">
            <Loader2 className="w-12 h-12 text-green-600 mx-auto mb-4 animate-spin" />
            <h2 className="text-xl font-semibold text-gray-800 mb-2">
              Completing Authentication
            </h2>
            <p className="text-gray-600">
              Please wait while we complete your OAuth authentication...
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-green-100">
        <Card className="w-full max-w-md glass-card">
          <CardContent className="p-8 text-center">
            <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-800 mb-2">
              Authentication Failed
            </h2>
            <p className="text-gray-600 mb-6">
              {errorMessage || 'An error occurred during OAuth authentication'}
            </p>
            <div className="space-y-3">
              <Button onClick={handleRetry} className="w-full">
                Try Again
              </Button>
              <Button onClick={handleGoHome} variant="outline" className="w-full">
                Go Home
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-green-100">
      <Card className="w-full max-w-md glass-card">
        <CardContent className="p-8 text-center">
          <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            Authentication Successful!
          </h2>
          <p className="text-gray-600 mb-6">
            Welcome to SaaS Factory! Redirecting you to your dashboard...
          </p>
          <div className="flex items-center justify-center">
            <Loader2 className="w-5 h-5 text-green-600 animate-spin mr-2" />
            <span className="text-sm text-gray-500">Redirecting...</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
