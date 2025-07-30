'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useDynamicAuth } from '@/hooks/useDynamicAuth';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Brain, Mail, Chrome, Twitter, Wallet } from 'lucide-react';

export default function AuthPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading, login } = useDynamicAuth();

  useEffect(() => {
    if (isAuthenticated && !isLoading) {
      router.push('/chat');
    }
  }, [isAuthenticated, isLoading, router]);

  const handleLogin = async () => {
    try {
      await login();
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-gray-900/90 backdrop-blur-sm border-gray-800">
        <CardHeader className="text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Brain className="h-10 w-10 text-blue-400" />
            <CardTitle className="text-3xl font-bold bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
              HandyWriterz
            </CardTitle>
          </div>
          <CardDescription className="text-gray-400 text-lg">
            Sign in to start creating amazing content
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Primary login button */}
          <Button
            onClick={handleLogin}
            size="lg"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-6 text-lg font-medium"
          >
            <Mail className="mr-2 h-5 w-5" />
            Continue with Email
          </Button>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-gray-700" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-gray-900 px-2 text-gray-500">Or continue with</span>
            </div>
          </div>

          {/* Social login options */}
          <div className="grid grid-cols-2 gap-3">
            <Button
              onClick={handleLogin}
              variant="outline"
              className="border-gray-700 hover:bg-gray-800 text-gray-300"
            >
              <Chrome className="mr-2 h-4 w-4" />
              Google
            </Button>
            <Button
              onClick={handleLogin}
              variant="outline"
              className="border-gray-700 hover:bg-gray-800 text-gray-300"
            >
              <Twitter className="mr-2 h-4 w-4" />
              Twitter
            </Button>
          </div>

          {/* Wallet connection (disabled for now) */}
          <Button
            variant="outline"
            disabled
            className="w-full border-gray-700 text-gray-500 cursor-not-allowed"
          >
            <Wallet className="mr-2 h-4 w-4" />
            Connect Wallet (Coming Soon)
          </Button>

          <div className="text-center text-sm text-gray-500 pt-4">
            By signing in, you agree to our{' '}
            <a href="#" className="text-blue-400 hover:underline">
              Terms of Service
            </a>{' '}
            and{' '}
            <a href="#" className="text-blue-400 hover:underline">
              Privacy Policy
            </a>
          </div>
        </CardContent>
      </Card>

      {/* Benefits section */}
      <div className="hidden lg:block lg:ml-12 max-w-sm">
        <h2 className="text-2xl font-bold text-white mb-6">Why HandyWriterz?</h2>
        <ul className="space-y-4 text-gray-300">
          <li className="flex items-start">
            <span className="text-green-400 mr-2">✓</span>
            <span>30+ specialized AI agents working together</span>
          </li>
          <li className="flex items-start">
            <span className="text-green-400 mr-2">✓</span>
            <span>Academic-grade writing with proper citations</span>
          </li>
          <li className="flex items-start">
            <span className="text-green-400 mr-2">✓</span>
            <span>Built-in plagiarism detection</span>
          </li>
          <li className="flex items-start">
            <span className="text-green-400 mr-2">✓</span>
            <span>Export to PDF, DOCX, and more</span>
          </li>
          <li className="flex items-start">
            <span className="text-green-400 mr-2">✓</span>
            <span>3 free documents to start</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
