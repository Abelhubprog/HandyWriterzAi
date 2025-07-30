'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  CheckCircle, 
  CreditCard, 
  Wallet, 
  ArrowLeft, 
  Star,
  Zap,
  Shield,
  Users
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/use-toast';

interface PricingTier {
  id: string;
  name: string;
  price_usd: number;
  credits: number;
  features: string[];
  max_words: number;
  icon: React.ReactNode;
  description: string;
  popular?: boolean;
}

interface CreditPackage {
  id: string;
  name: string;
  credits: number;
  price_usd: number;
  bonus_credits?: number;
  description: string;
}

const PRICING_TIERS: PricingTier[] = [
  {
    id: 'free',
    name: 'Free',
    price_usd: 0,
    credits: 500,
    features: [
      'AI Writing Agents',
      'Document Generation',
      'Research Assistant',
      'Citation Manager',
      'Basic Templates',
      'File Upload (PDF, DOC)',
      'Export to PDF/DOCX/MD',
      'Basic Formatting',
      'Grammar Check',
      'Plagiarism Detection'
    ],
    max_words: 1000,
    icon: <Star className="w-6 h-6" />,
    description: '500 credits per month'
  },
  {
    id: 'plus',
    name: 'Plus',
    price_usd: 20,
    credits: 5000,
    features: [
      'AI Writing Agents',
      'Advanced Document Generation',
      'Research Assistant',
      'Citation Manager',
      'Premium Templates',
      'File Upload (PDF, DOC)',
      'Export to PDF/DOCX/MD',
      'Advanced Formatting',
      'Grammar & Style Check',
      'Plagiarism Detection',
      'Priority Support',
      'Collaboration Tools'
    ],
    max_words: 5000,
    icon: <Zap className="w-6 h-6" />,
    description: '5,000 credits per month',
    popular: true
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price_usd: 0,
    credits: 0,
    features: [
      'AI Writing Agents',
      'Enterprise Document Generation',
      'Research Assistant',
      'Citation Manager',
      'Custom Templates',
      'Unlimited File Upload',
      'Export to PDF/DOCX/MD',
      'Advanced Formatting',
      'Grammar & Style Check',
      'Advanced Plagiarism Detection',
      'Priority Support',
      'Team Collaboration',
      'Custom Integrations',
      'White-label Options'
    ],
    max_words: 50000,
    icon: <Shield className="w-6 h-6" />,
    description: 'Custom credits per month'
  }
];

const CREDIT_PACKAGES: CreditPackage[] = [
  {
    id: 'credits_2000',
    name: '2,000',
    credits: 2000,
    price_usd: 9.20,
    description: '✓'
  },
  {
    id: 'credits_4000',
    name: '4,000',
    credits: 4000,
    price_usd: 18.40,
    description: ''
  },
  {
    id: 'credits_10000',
    name: '10,000',
    credits: 10000,
    price_usd: 46,
    description: ''
  },
  {
    id: 'credits_20000',
    name: '20,000',
    credits: 20000,
    price_usd: 92,
    description: ''
  },
  {
    id: 'credits_40000',
    name: '40,000',
    credits: 40000,
    price_usd: 184,
    description: ''
  }
];

export default function PricingPage() {
  const [selectedProvider, setSelectedProvider] = useState<'paystack' | 'coinbase_commerce'>('paystack');
  const [loading, setLoading] = useState<string | null>(null);
  const [currentPlan, setCurrentPlan] = useState<string>('free');
  const { toast } = useToast();
  const router = useRouter();

  useEffect(() => {
    // Load current plan from billing summary
    const loadCurrentPlan = async () => {
      try {
        const response = await fetch('/api/billing/summary', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        if (response.ok) {
          const data = await response.json();
          setCurrentPlan(data.plan || 'free');
        }
      } catch (error) {
        console.error('Error loading current plan:', error);
      }
    };

    loadCurrentPlan();
  }, []);

  const handleUpgrade = async (tierId: string) => {
    if (tierId === 'free' || tierId === currentPlan || loading) return;
    
    setLoading(tierId);
    try {
      const response = await fetch('/api/billing/upgrade', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          tier: tierId,
          provider: selectedProvider,
          metadata: {
            source: 'pricing_page',
            upgrade_from: currentPlan
          }
        })
      });

      const data = await response.json();

      if (data.success) {
        // Redirect to payment page
        window.open(data.payment_data.payment_url, '_blank');
        toast({
          title: "Payment initiated",
          description: "You'll be redirected to complete the payment.",
        });
      } else {
        toast({
          title: "Payment failed",
          description: data.message || "Failed to create payment. Please try again.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error creating payment:', error);
      toast({
        title: "Error",
        description: "Unable to process payment. Please check your connection.",
        variant: "destructive",
      });
    } finally {
      setLoading(null);
    }
  };

  const handleBuyCredits = async (packageId: string) => {
    if (loading) return;
    
    setLoading(packageId);
    try {
      const response = await fetch('/api/billing/buy-credits', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          package_id: packageId,
          provider: selectedProvider,
          metadata: {
            source: 'pricing_page'
          }
        })
      });

      const data = await response.json();

      if (data.success) {
        window.open(data.payment_data.payment_url, '_blank');
        toast({
          title: "Payment initiated",
          description: "You'll be redirected to complete the payment.",
        });
      } else {
        toast({
          title: "Payment failed",
          description: data.message || "Failed to create payment. Please try again.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error buying credits:', error);
      toast({
        title: "Error",
        description: "Unable to process payment. Please check your connection.",
        variant: "destructive",
      });
    } finally {
      setLoading(null);
    }
  };

  const isCurrentTier = (tierId: string) => tierId === currentPlan;

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 p-4">
        <div className="max-w-7xl mx-auto flex items-center gap-4">
          <Button
            variant="ghost"
            onClick={() => router.push('/chat')}
            className="text-gray-400 hover:text-white hover:bg-gray-700/50"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Chat
          </Button>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Pricing</h1>
            <p className="text-gray-400 text-sm">Choose the plan that works best for you</p>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* Payment Provider Selection */}
        <div className="text-center mb-12">
          <h2 className="text-lg font-semibold mb-4">Choose Payment Method</h2>
          <div className="flex justify-center gap-4">
            <Button
              variant={selectedProvider === 'paystack' ? 'default' : 'outline'}
              onClick={() => setSelectedProvider('paystack')}
              className="flex items-center gap-2"
            >
              <CreditCard className="w-4 h-4" />
              Card Payment
            </Button>
            <Button
              variant={selectedProvider === 'coinbase_commerce' ? 'default' : 'outline'}
              onClick={() => setSelectedProvider('coinbase_commerce')}
              className="flex items-center gap-2"
            >
              <Wallet className="w-4 h-4" />
              Crypto Payment
            </Button>
          </div>
        </div>

        {/* Subscription Plans */}
        <section className="mb-16">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold mb-4">Subscription Plans</h2>
            <p className="text-gray-400 text-lg">
              Get unlimited access with our monthly subscription plans
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {PRICING_TIERS.map((tier) => (
              <Card 
                key={tier.id} 
                className={`relative bg-gray-800 border-gray-700 ${
                  tier.popular ? 'ring-2 ring-blue-500 scale-105' : ''
                } ${isCurrentTier(tier.id) ? 'ring-2 ring-green-500' : ''}`}
              >
                {tier.popular && (
                  <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-blue-600 text-white">
                    Most Popular
                  </Badge>
                )}
                
                {isCurrentTier(tier.id) && (
                  <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-green-600 text-white">
                    Current Plan
                  </Badge>
                )}

                <CardHeader className="text-center pb-4">
                  <div className="w-12 h-12 mx-auto mb-4 flex items-center justify-center bg-blue-600/20 rounded-full text-blue-400">
                    {tier.icon}
                  </div>
                  <CardTitle className="text-2xl">{tier.name}</CardTitle>
                  <div className="text-4xl font-bold text-white mb-2">
                    ${tier.price_usd}
                    {tier.price_usd > 0 && <span className="text-lg font-normal text-gray-400">/month</span>}
                  </div>
                  <CardDescription className="text-gray-400">
                    {tier.description}
                  </CardDescription>
                </CardHeader>

                <CardContent>
                  <div className="text-center mb-6">
                    <div className="text-2xl font-bold text-blue-400">{tier.credits}</div>
                    <div className="text-sm text-gray-400">credits per month</div>
                    <div className="text-sm text-gray-500 mt-1">
                      Up to {tier.max_words.toLocaleString()} words per document
                    </div>
                  </div>

                  <ul className="space-y-3 mb-8">
                    {tier.features.map((feature, index) => (
                      <li key={index} className="flex items-start gap-3 text-sm">
                        <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                        <span className="text-gray-300">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <Button
                    className="w-full"
                    variant={isCurrentTier(tier.id) ? 'secondary' : (tier.popular ? 'default' : 'outline')}
                    disabled={isCurrentTier(tier.id) || loading === tier.id}
                    onClick={() => handleUpgrade(tier.id)}
                  >
                    {loading === tier.id ? 'Processing...' : 
                     isCurrentTier(tier.id) ? 'Current Plan' :
                     tier.id === 'free' ? 'Get Started Free' : 
                     `Upgrade to ${tier.name}`}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* Credit Packages */}
        <section>
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold mb-4">Credit Packages</h2>
            <p className="text-gray-400 text-lg">
              Top up your account with additional credits as needed
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {CREDIT_PACKAGES.map((pkg) => (
              <Card key={pkg.id} className="bg-gray-800 border-gray-700 text-center">
                <CardHeader>
                  <CardTitle className="text-xl">{pkg.name}</CardTitle>
                  <div className="text-3xl font-bold text-blue-400">
                    {pkg.credits}
                    {pkg.bonus_credits && (
                      <span className="text-sm text-green-400"> +{pkg.bonus_credits}</span>
                    )}
                  </div>
                  <div className="text-sm text-gray-400">credits</div>
                  <div className="text-2xl font-bold text-white">
                    ${pkg.price_usd}
                  </div>
                  <CardDescription className="text-gray-400">
                    {pkg.description}
                  </CardDescription>
                </CardHeader>

                <CardContent>
                  {pkg.bonus_credits && (
                    <div className="mb-4 p-2 bg-green-600/20 rounded-lg">
                      <div className="text-green-400 text-sm font-medium">
                        +{pkg.bonus_credits} Bonus Credits!
                      </div>
                    </div>
                  )}

                  <Button
                    className="w-full"
                    variant="outline"
                    disabled={loading === pkg.id}
                    onClick={() => handleBuyCredits(pkg.id)}
                  >
                    {loading === pkg.id ? 'Processing...' : 'Buy Credits'}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* FAQ Section */}
        <section className="mt-16 bg-gray-800/50 rounded-lg p-8">
          <h3 className="text-2xl font-bold text-center mb-8">Frequently Asked Questions</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h4 className="font-semibold mb-2 text-white">How do credits work?</h4>
              <p className="text-gray-400 text-sm">
                Each document generation uses credits based on length and complexity. Credits reset monthly for subscriptions 
                and never expire for one-time purchases.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-2 text-white">Can I change my plan anytime?</h4>
              <p className="text-gray-400 text-sm">
                Yes! You can upgrade or downgrade your plan at any time. Changes take effect 
                immediately with prorated billing.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-2 text-white">What payment methods do you accept?</h4>
              <p className="text-gray-400 text-sm">
                We accept all major credit cards via Paystack and cryptocurrency payments 
                (USDC, BTC, ETH) via Coinbase Commerce.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-2 text-white">Is there a free trial?</h4>
              <p className="text-gray-400 text-sm">
                Yes! Our Free plan includes 500 credits per month forever. No credit card required 
                to get started.
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}