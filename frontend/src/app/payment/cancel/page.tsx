'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { XCircle } from 'lucide-react';

export default function PaymentCancelPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <XCircle className="w-16 h-16 text-orange-600" />
          </div>
          <CardTitle className="text-2xl">Payment Cancelled</CardTitle>
          <CardDescription className="text-center">
            Your payment was cancelled. No charges have been made to your account.
          </CardDescription>
        </CardHeader>

        <CardContent className="text-center space-y-4">
          <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
            <p className="text-sm text-orange-800 dark:text-orange-200">
              You can try again anytime from your billing settings.
            </p>
          </div>

          <div className="flex gap-2">
            <Button
              onClick={() => router.push('/settings/billing')}
              className="flex-1"
            >
              Try Again
            </Button>
            
            <Button
              onClick={() => router.push('/chat')}
              variant="outline"
              className="flex-1"
            >
              Back to Chat
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}