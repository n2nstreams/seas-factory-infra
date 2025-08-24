import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams, useParams } from 'react-router-dom';
import { useAuth } from '@/App';
import { Loader2, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function OAuthSuccess() {
  const { setUser } = useAuth();
  const navigate = useNavigate();
  const { provider } = useParams();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState('');
  const [errorDetails, setErrorDetails] = useState('');

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
      setErrorDetails('The OAuth provider did not return an authentication token. This might be a configuration issue.');
      return;
    }

    // Process the OAuth token
    processOAuthToken(token);
  }, [searchParams]);

  const processOAuthToken = async (token: string) => {
    try {
      // Validate token format
      if (!token.includes('.')) {
        throw new Error('Invalid token format');
      }

      // Store token in localStorage
      localStorage.setItem('authToken', token);
      
      // Decode JWT token to get user info (client-side only for display)
      const tokenParts = token.split('.');
      if (tokenParts.length !== 3) {
        throw new Error('Invalid JWT token structure');
      }

      let tokenPayload;
      try {
        tokenPayload = JSON.parse(atob(tokenParts[1]));
      } catch (e) {
        throw new Error('Failed to decode token payload');
      }

      // Validate required fields
      if (!tokenPayload.user_id || !tokenPayload.email) {
        throw new Error('Token missing required user information');
      }
      
      // Create user object from token
      const userData = {
        id: tokenPayload.user_id,
        email: tokenPayload.email,
        name: tokenPayload.name || 'OAuth User',
        role: tokenPayload.role || 'user',
        plan: tokenPayload.plan || 'starter' as const,
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
      setErrorDetails(error instanceof Error ? error.message : 'An unexpected error occurred while processing your authentication.');
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

  const handleContactSupport = () => {
    // You can implement this to open a support form or redirect to support
            window.open('mailto:support@forge95.com?subject=OAuth%20Authentication%20Issue', '_blank');
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
              Please wait while we complete your {provider ? `${provider} ` : ''}OAuth authentication...
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-green-100 p-4">
        <Card className="w-full max-w-lg glass-card">
          <CardHeader className="text-center pb-4">
            <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <CardTitle className="text-2xl font-semibold text-gray-800">
              Authentication Failed
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription className="font-medium">
                {errorMessage}
              </AlertDescription>
            </Alert>

            {errorDetails && (
              <div className="text-center">
                <p className="text-gray-600 mb-4">
                  {errorDetails}
                </p>
              </div>
            )}

            <div className="space-y-3">
              <Button onClick={handleRetry} className="w-full" size="lg">
                Try Again
              </Button>
              
              <Button onClick={handleContactSupport} variant="outline" className="w-full" size="lg">
                Contact Support
              </Button>
              
              <Button onClick={handleGoHome} variant="ghost" className="w-full" size="lg">
                Go Home
              </Button>
            </div>

            <div className="text-center pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-500">
                If you continue to experience issues, please contact our support team.
              </p>
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
            {provider ? `${provider.charAt(0).toUpperCase() + provider.slice(1)} Authentication Successful!` : 'Authentication Successful!'}
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
