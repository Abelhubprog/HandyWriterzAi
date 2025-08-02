"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { 
  Shield, 
  CheckCircle,
  AlertTriangle,
  Loader2,
  ExternalLink
} from 'lucide-react';
import { toast } from '@/components/ui/use-toast';
import { useWorkbenchAuth } from '@/contexts/WorkbenchAuthContext';

// Dynamic.xyz configuration - in production, this would be loaded from environment
const DYNAMIC_ENVIRONMENT_ID = process.env.NEXT_PUBLIC_DYNAMIC_ENVIRONMENT_ID || 'demo-workbench-env';

declare global {
  interface Window {
    DynamicSDK?: any;
  }
}

export default function WorkbenchLoginPage() {
  const router = useRouter();
  const { login, isAuthenticated, isLoading: authLoading } = useWorkbenchAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [dynamicSDK, setDynamicSDK] = useState<any>(null);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && !authLoading) {
      router.push('/workbench');
    }
  }, [isAuthenticated, authLoading, router]);

  // Load Dynamic.xyz SDK
  useEffect(() => {
    const loadDynamicSDK = async () => {
      try {
        // In a real implementation, you would load the Dynamic.xyz SDK
        // For now, we'll simulate the SDK loading
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock Dynamic SDK for demo purposes
        const mockSDK = {
          init: () => Promise.resolve(),
          authenticate: () => Promise.resolve({
            token: `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ3Yl91c2VyXzEiLCJlbWFpbCI6ImFsaWNlQHdvcmtiZW5jaC5oYW5keXdyaXRlcnouY29tIiwidXNlcm5hbWUiOiJhbGljZS1jaGVja2VyIiwidmVyaWZpZWQiOnRydWUsImlhdCI6MTcwNjc4NDAwMCwiZXhwIjoxNzA2ODcwNDAwfQ.demo-token-for-workbench`,
            user: {
              id: 'wb_user_1',
              email: 'alice@workbench.handywriterz.com',
              username: 'alice-checker',
              verified: true
            }
          }),
          isReady: true
        };
        
        setDynamicSDK(mockSDK);
      } catch (error) {
        console.error('Failed to load Dynamic SDK:', error);
        setError('Authentication service unavailable. Please try again later.');
      }
    };

    loadDynamicSDK();
  }, []);

  const handleDynamicLogin = async () => {
    if (!dynamicSDK) {
      setError('Authentication service not ready. Please wait and try again.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      // Authenticate with Dynamic.xyz
      const authResult = await dynamicSDK.authenticate();
      
      if (!authResult.token) {
        throw new Error('No authentication token received');
      }

      // Login with backend using Dynamic token
      await login(authResult.token);

      toast({
        title: "Login Successful",
        description: `Welcome to the workbench, ${authResult.user.username}!`,
      });

      // Navigation will happen via useEffect when isAuthenticated changes

    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.message || 'Login failed. Please ensure you are authorized for workbench access.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleContactAdmin = () => {
    // In production, this would open a support ticket or email
    toast({
      title: "Contact Administrator",
      description: "Please contact your system administrator for workbench access.",
    });
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600 dark:text-gray-400">Checking authentication...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <Shield className="w-12 h-12 text-blue-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Workbench Access
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Secure Dynamic.xyz authentication for verified workbench users
          </p>
        </div>

        {/* Login Card */}
        <Card>
          <CardHeader>
            <CardTitle className="text-center flex items-center justify-center">
              <ExternalLink className="w-5 h-5 mr-2" />
              Dynamic.xyz Authentication
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {error && (
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* Authentication Status */}
              <div className="text-center">
                {!dynamicSDK ? (
                  <div className="space-y-3">
                    <Loader2 className="w-6 h-6 animate-spin mx-auto text-blue-600" />
                    <p className="text-sm text-gray-600">Loading authentication service...</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <CheckCircle className="w-6 h-6 mx-auto text-green-600" />
                    <p className="text-sm text-gray-600">Authentication service ready</p>
                  </div>
                )}
              </div>

              {/* Login Button */}
              <Button 
                onClick={handleDynamicLogin}
                className="w-full" 
                disabled={isLoading || !dynamicSDK}
                size="lg"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Authenticating...
                  </>
                ) : (
                  <>
                    <Shield className="w-4 h-4 mr-2" />
                    Sign In with Dynamic.xyz
                  </>
                )}
              </Button>

              {/* Info Section */}
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  Only users added by administrators can access the workbench. 
                  If you don't have access, please contact your system administrator.
                </AlertDescription>
              </Alert>

              {/* Security Features */}
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Security Features:
                </h4>
                <div className="text-xs text-gray-500 space-y-1">
                  <div className="flex items-center">
                    <CheckCircle className="w-3 h-3 mr-2 text-green-500" />
                    End-to-end encryption
                  </div>
                  <div className="flex items-center">
                    <CheckCircle className="w-3 h-3 mr-2 text-green-500" />
                    Multi-factor authentication
                  </div>
                  <div className="flex items-center">
                    <CheckCircle className="w-3 h-3 mr-2 text-green-500" />
                    Session management
                  </div>
                  <div className="flex items-center">
                    <CheckCircle className="w-3 h-3 mr-2 text-green-500" />
                    Role-based access control
                  </div>
                </div>
              </div>

              {/* Contact Admin */}
              <div className="pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={handleContactAdmin}
                  className="w-full"
                  size="sm"
                >
                  Need Access? Contact Administrator
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-6 text-sm text-gray-600 dark:text-gray-400">
          <p>
            <span className="inline-flex items-center">
              <Shield className="w-4 h-4 mr-1" />
              Powered by Dynamic.xyz authentication
            </span>
          </p>
          <p className="mt-2">
            HandyWriterzAI Workbench - Human-in-the-loop quality assurance
          </p>
        </div>
      </div>
    </div>
  );
}