'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';

interface PaymentVerificationState {
  status: 'loading' | 'success' | 'failed' | 'pending';
  message: string;
  tier?: string;
}

export function PaymentSuccess() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [verification, setVerification] = useState<PaymentVerificationState>({
    status: 'loading',
    message: 'Verifying your payment...'
  });

  useEffect(() => {
    const verifyPayment = async () => {
      const reference = searchParams.get('reference') || searchParams.get('charge_id');
      const provider = searchParams.get('provider') || 'paystack';

      if (!reference) {
        setVerification({
          status: 'failed',
          message: 'Payment reference is missing. Please contact support.'
        });
        return;
      }

      try {
        const response = await fetch('/api/billing/verify-payment', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          },
          body: JSON.stringify({
            reference,
            provider
          })
        });

        const data = await response.json();

        if (data.success) {
          setVerification({
            status: 'success',
            message: `Payment successful! Your subscription has been upgraded to ${data.tier}.`,
            tier: data.tier
          });
        } else {
          setVerification({
            status: data.status === 'pending' ? 'pending' : 'failed',
            message: data.message || 'Payment verification failed.'
          });
        }
      } catch (error) {
        console.error('Payment verification error:', error);
        setVerification({
          status: 'failed',
          message: 'Error verifying payment. Please contact support.'
        });
      }
    };

    verifyPayment();
  }, [searchParams]);

  const handleContinue = () => {
    router.push('/chat');
  };

  const handleRetry = () => {
    router.push('/settings/billing');
  };

  const getIcon = () => {
    switch (verification.status) {
      case 'loading':
        return <Loader2 className="w-16 h-16 text-blue-600 animate-spin" />;
      case 'success':
        return <CheckCircle className="w-16 h-16 text-green-600" />;
      case 'pending':
        return <Loader2 className="w-16 h-16 text-yellow-600" />;
      case 'failed':
        return <XCircle className="w-16 h-16 text-red-600" />;
    }
  };

  const getTitle = () => {
    switch (verification.status) {
      case 'loading':
        return 'Verifying Payment';
      case 'success':
        return 'Payment Successful!';
      case 'pending':
        return 'Payment Pending';
      case 'failed':
        return 'Payment Failed';
    }
  };

  const getButtonText = () => {
    switch (verification.status) {
      case 'success':
        return 'Continue to Chat';
      case 'pending':
        return 'Check Again Later';
      case 'failed':
        return 'Try Again';
      default:
        return 'Please Wait...';
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            {getIcon()}
          </div>
          <CardTitle className="text-2xl">{getTitle()}</CardTitle>
          <CardDescription className="text-center">
            {verification.message}
          </CardDescription>
        </CardHeader>

        <CardContent className="text-center space-y-4">
          {verification.tier && verification.status === 'success' && (
            <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <p className="text-sm text-green-800 dark:text-green-200">
                You now have access to all {verification.tier} plan features!
              </p>
            </div>
          )}

          {verification.status === 'pending' && (
            <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
              <p className="text-sm text-yellow-800 dark:text-yellow-200">
                Your crypto payment is being confirmed on the blockchain. 
                This may take a few minutes.
              </p>
            </div>
          )}

          {verification.status === 'failed' && (
            <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
              <p className="text-sm text-red-800 dark:text-red-200">
                If you believe this is an error, please contact our support team 
                with your payment reference.
              </p>
            </div>
          )}

          <div className="flex gap-2">
            {verification.status !== 'loading' && (
              <Button
                onClick={verification.status === 'success' ? handleContinue : handleRetry}
                className="flex-1"
                variant={verification.status === 'success' ? 'default' : 'secondary'}
              >
                {getButtonText()}
              </Button>
            )}

            {verification.status !== 'success' && verification.status !== 'loading' && (
              <Button
                onClick={() => router.push('/chat')}
                variant="outline"
                className="flex-1"
              >
                Back to Chat
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default PaymentSuccess;