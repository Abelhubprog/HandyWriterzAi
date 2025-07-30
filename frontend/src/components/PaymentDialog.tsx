'use client';

import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, CreditCard, Wallet } from 'lucide-react';

interface PaymentDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  currentTier?: string;
}

interface PricingTier {
  name: string;
  price_usd: number;
  credits: number;
  features: string[];
  max_words: number;
}

const PRICING_TIERS: Record<string, PricingTier> = {
  free: {
    name: 'Free',
    price_usd: 0,
    credits: 3,
    features: ['3 documents', 'Basic templates', 'Community support'],
    max_words: 1000
  },
  basic: {
    name: 'Basic',
    price_usd: 19.99,
    credits: 50,
    features: ['50 documents', 'Advanced templates', 'Email support', 'Export to PDF/DOCX'],
    max_words: 5000
  },
  pro: {
    name: 'Pro',
    price_usd: 49.99,
    credits: 200,
    features: ['200 documents', 'All templates', 'Priority support', 'Advanced AI models', 'Plagiarism check'],
    max_words: 15000
  },
  enterprise: {
    name: 'Enterprise',
    price_usd: 199.99,
    credits: 1000,
    features: ['Unlimited documents', 'Custom templates', '24/7 support', 'Team collaboration', 'API access'],
    max_words: 50000
  }
};

export function PaymentDialog({ open, onOpenChange, currentTier = 'free' }: PaymentDialogProps) {
  const [selectedTier, setSelectedTier] = useState<string>('');
  const [selectedProvider, setSelectedProvider] = useState<'paystack' | 'coinbase_commerce'>('paystack');
  const [loading, setLoading] = useState(false);

  const handleUpgrade = async (tier: string) => {
    if (tier === 'free' || tier === currentTier) return;
    
    setLoading(true);
    try {
      const response = await fetch('/api/billing/upgrade', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}` // Dynamic.xyz token
        },
        body: JSON.stringify({
          tier,
          provider: selectedProvider,
          metadata: {
            upgrade_from: currentTier,
            frontend_version: '1.0.0'
          }
        })
      });

      const data = await response.json();

      if (data.success) {
        // Redirect to payment page
        window.open(data.payment_data.payment_url, '_blank');
        onOpenChange(false);
      } else {
        console.error('Payment creation failed:', data);
        alert('Failed to create payment. Please try again.');
      }
    } catch (error) {
      console.error('Error creating payment:', error);
      alert('Error creating payment. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const isCurrentTier = (tier: string) => tier === currentTier;
  const isDowngrade = (tier: string) => {
    const tiers = ['free', 'basic', 'pro', 'enterprise'];
    return tiers.indexOf(tier) < tiers.indexOf(currentTier);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Choose Your Plan</DialogTitle>
        </DialogHeader>

        {/* Payment Provider Selection */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3">Payment Method</h3>
          <div className="flex gap-4">
            <Button
              variant={selectedProvider === 'paystack' ? 'default' : 'outline'}
              onClick={() => setSelectedProvider('paystack')}
              className="flex items-center gap-2"
            >
              <CreditCard className="w-4 h-4" />
              Card Payment (Paystack)
            </Button>
            <Button
              variant={selectedProvider === 'coinbase_commerce' ? 'default' : 'outline'}
              onClick={() => setSelectedProvider('coinbase_commerce')}
              className="flex items-center gap-2"
            >
              <Wallet className="w-4 h-4" />
              Crypto Payment (USDC)
            </Button>
          </div>
        </div>

        {/* Pricing Tiers */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.entries(PRICING_TIERS).map(([key, tier]) => (
            <Card 
              key={key} 
              className={`relative ${isCurrentTier(key) ? 'ring-2 ring-primary' : ''} ${
                key === 'pro' ? 'border-primary' : ''
              }`}
            >
              {key === 'pro' && (
                <Badge className="absolute -top-2 left-1/2 transform -translate-x-1/2 bg-primary">
                  Most Popular
                </Badge>
              )}
              
              {isCurrentTier(key) && (
                <Badge className="absolute -top-2 left-1/2 transform -translate-x-1/2 bg-green-600">
                  Current Plan
                </Badge>
              )}

              <CardHeader className="text-center">
                <CardTitle className="text-xl">{tier.name}</CardTitle>
                <div className="text-3xl font-bold">
                  ${tier.price_usd}
                  {tier.price_usd > 0 && <span className="text-sm font-normal">/month</span>}
                </div>
                <CardDescription>
                  {tier.credits} credits • Up to {tier.max_words.toLocaleString()} words
                </CardDescription>
              </CardHeader>

              <CardContent>
                <ul className="space-y-2 mb-4">
                  {tier.features.map((feature, index) => (
                    <li key={index} className="flex items-center gap-2 text-sm">
                      <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>

                <Button
                  className="w-full"
                  variant={isCurrentTier(key) ? 'secondary' : 'default'}
                  disabled={isCurrentTier(key) || isDowngrade(key) || loading}
                  onClick={() => handleUpgrade(key)}
                >
                  {loading ? 'Processing...' : 
                   isCurrentTier(key) ? 'Current Plan' :
                   isDowngrade(key) ? 'Downgrade Not Available' :
                   key === 'free' ? 'Free Forever' : 
                   `Upgrade to ${tier.name}`}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Payment Information */}
        <div className="mt-6 p-4 bg-muted rounded-lg">
          <h4 className="font-semibold mb-2">Payment Information</h4>
          <ul className="text-sm space-y-1">
            <li>• All subscriptions are monthly and auto-renewing</li>
            <li>• Credits reset each month on your renewal date</li>
            <li>• You can cancel anytime from your account settings</li>
            <li>• Crypto payments are processed securely via Coinbase Commerce</li>
            <li>• Card payments are processed securely via Paystack</li>
          </ul>
        </div>
      </DialogContent>
    </Dialog>
  );
}

export default PaymentDialog;