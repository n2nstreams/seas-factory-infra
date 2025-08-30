import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { AlertTriangle, RefreshCw, Home, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function OAuthError() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [errorDetails, setErrorDetails] = useState<{
    type: string;
    message: string;
    provider: string;
    details?: string;
  } | null>(null);

  useEffect(() => {
    const error = searchParams.get('error');
    const provider = searchParams.get('provider') || 'OAuth';
    const details = searchParams.get('details');

    if (error) {
      const errorInfo = getErrorInfo(error, provider, details);
      setErrorDetails(errorInfo);
    }
  }, [searchParams]);

  const getErrorInfo = (error: string, provider: string, details?: string) => {
    const errorMap: Record<string, { message: string; suggestion: string }> = {
      'no_code': {
        message: 'No authorization code received',
        suggestion: 'Please try signing in again from the beginning.'
      },
      'invalid_state': {
        message: 'Invalid state parameter - possible CSRF attack',
        suggestion: 'Please try signing in again from the beginning. This error usually indicates a security issue.'
      },
      'code_verifier_missing': {
        message: 'Security verification failed - missing code verifier',
        suggestion: 'Please try signing in again from the beginning. This is a security validation error.'
      },
      'invalid_input': {
        message: 'Invalid input parameters received',
        suggestion: 'Please try signing in again from the beginning. This error indicates malformed input.'
      },
      'scope_insufficient': {
        message: 'Insufficient permissions granted',
        suggestion: 'Please ensure you grant all required permissions during the OAuth flow.'
      },
      'token_expired': {
        message: 'Authentication token has expired',
        suggestion: 'Please sign in again to get a new authentication token.'
      },
      'token_validation_failed': {
        message: 'Token validation failed',
        suggestion: 'Please try signing in again or contact support if the issue persists.'
      },
      'token_exchange_failed': {
        message: 'Failed to exchange authorization code for access token',
        suggestion: 'This might be a temporary issue. Please try again in a few minutes.'
      },
      'no_access_token': {
        message: 'No access token received from the provider',
        suggestion: 'Please try signing in again or contact support if the issue persists.'
      },
      'user_info_failed': {
        message: 'Failed to retrieve user information',
        suggestion: 'Please try signing in again or check your account permissions.'
      },
      'emails_failed': {
        message: 'Failed to retrieve user email information',
        suggestion: 'Please ensure your account has a verified email address.'
      },
      'no_primary_email': {
        message: 'No primary email address found',
        suggestion: 'Please ensure your account has a verified primary email address.'
      },
      'no_email': {
        message: 'No email address provided by the authentication provider',
        suggestion: 'Please ensure your account has a verified email address.'
      },
      'http_error': {
        message: 'HTTP error occurred during authentication',
        suggestion: details ? `Error code: ${details}. Please try again or contact support.` : 'Please try again or contact support.'
      },
      'internal_error': {
        message: 'Internal server error occurred',
        suggestion: 'Please try again in a few minutes or contact support if the issue persists.'
      },
      'access_denied': {
        message: 'Access was denied by the user',
        suggestion: 'You can try signing in again or use a different authentication method.'
      },
      'invalid_scope': {
        message: 'Invalid scope requested',
        suggestion: 'Please try signing in again or contact support.'
      }
    };

    const errorInfo = errorMap[error] || {
      message: 'An unexpected error occurred',
      suggestion: 'Please try signing in again or contact support if the issue persists.'
    };

    return {
      type: error,
      message: errorInfo.message,
      provider,
      details,
      suggestion: errorInfo.suggestion
    };
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

  const handleGoBack = () => {
    navigate(-1);
  };

  if (!errorDetails) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-green-100">
        <Card className="w-full max-w-md glass-card">
          <CardContent className="p-8 text-center">
            <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-800 mb-2">
              Loading Error Details
            </h2>
            <p className="text-gray-600">
              Please wait while we load the error information...
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-green-100 p-4">
      <Card className="w-full max-w-lg glass-card">
        <CardHeader className="text-center pb-4">
          <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <CardTitle className="text-2xl font-semibold text-gray-800">
            {errorDetails.provider} Authentication Failed
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription className="font-medium">
              {errorDetails.message}
            </AlertDescription>
          </Alert>

          <div className="text-center">
            <p className="text-gray-600 mb-4">
              {errorDetails.suggestion}
            </p>
            
            {errorDetails.details && (
              <p className="text-sm text-gray-500 mb-4">
                Technical details: {errorDetails.details}
              </p>
            )}
          </div>

          <div className="space-y-3">
            <Button onClick={handleRetry} className="w-full" size="lg">
              <RefreshCw className="w-4 h-4 mr-2" />
              Try Again
            </Button>
            
            <Button onClick={handleGoBack} variant="outline" className="w-full" size="lg">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Go Back
            </Button>
            
            <Button onClick={handleGoHome} variant="ghost" className="w-full" size="lg">
              <Home className="w-4 h-4 mr-2" />
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
