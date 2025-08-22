import { useNavigate, useSearchParams } from 'react-router-dom';
import { XCircle, Home, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

export default function OAuthError() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  const error = searchParams.get('error') || 'Authentication failed';
  const errorDescription = searchParams.get('error_description') || 'An error occurred during OAuth authentication';

  const handleRetry = () => {
    navigate('/signin');
  };

  const handleGoHome = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-green-100">
      <Card className="w-full max-w-md glass-card">
        <CardContent className="p-8 text-center">
          <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-800 mb-2">
            OAuth Authentication Error
          </h1>
          <p className="text-gray-600 mb-2 font-medium">
            {error}
          </p>
          <p className="text-gray-500 text-sm mb-6">
            {errorDescription}
          </p>
          
          <div className="space-y-3">
            <Button onClick={handleRetry} className="w-full">
              <RefreshCw className="w-4 h-4 mr-2" />
              Try Again
            </Button>
            <Button onClick={handleGoHome} variant="outline" className="w-full">
              <Home className="w-4 h-4 mr-2" />
              Go Home
            </Button>
          </div>
          
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-500">
              If this problem persists, please contact support with the error details above.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
