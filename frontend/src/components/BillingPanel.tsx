"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import PaymentDialog from "./PaymentDialog";

interface BillingSummary {
  plan: string;
  renew_date: string;
  usage_usd: number;
  credits_remaining: number;
  max_words: number;
  features: string[];
}

interface PaymentMethod {
  id: string;
  brand: string;
  last4: string;
  type: string;
}

interface Invoice {
  id: string;
  pdf_url: string;
  total: number;
  date: string;
}

// API functions to fetch data from backend
const fetchBillingSummary = async (): Promise<BillingSummary> => {
  try {
    const response = await fetch('/api/billing/summary', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      }
    });
    if (response.ok) {
      return await response.json();
    }
  } catch (error) {
    console.error('Error fetching billing summary:', error);
  }
  
  // Fallback mock data
  return {
    plan: "free",
    renew_date: "N/A",
    usage_usd: 0,
    credits_remaining: 3,
    max_words: 1000,
    features: ["3 documents", "Basic templates", "Community support"]
  };
};

const fetchPaymentMethods = async (): Promise<PaymentMethod[]> => {
  try {
    const response = await fetch('/api/billing/methods', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      }
    });
    if (response.ok) {
      return await response.json();
    }
  } catch (error) {
    console.error('Error fetching payment methods:', error);
  }
  
  return [
    { id: "paystack_card", brand: "Paystack", last4: "Card", type: "fiat" },
    { id: "coinbase_crypto", brand: "Coinbase", last4: "USDC", type: "crypto" }
  ];
};

const fetchInvoices = async (): Promise<Invoice[]> => {
  try {
    const response = await fetch('/api/billing/invoices', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      }
    });
    if (response.ok) {
      return await response.json();
    }
  } catch (error) {
    console.error('Error fetching invoices:', error);
  }
  
  return [];
};

export default function BillingPanel() {
  const [summary, setSummary] = useState<BillingSummary | null>(null);
  const [methods, setMethods] = useState<PaymentMethod[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const [summaryData, methodsData, invoicesData] = await Promise.all([
          fetchBillingSummary(),
          fetchPaymentMethods(),
          fetchInvoices()
        ]);
        
        setSummary(summaryData);
        setMethods(methodsData);
        setInvoices(invoicesData);
      } catch (error) {
        console.error('Error loading billing data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center p-8">Loading...</div>;
  }

  if (!summary) {
    return <div className="text-center p-8">Unable to load billing information</div>;
  }

  const creditsUsed = summary.credits_remaining < 3 ? 3 - summary.credits_remaining : 0;
  const creditProgress = creditsUsed > 0 ? (creditsUsed / 3) * 100 : 0;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Billing Summary</CardTitle>
          <Button onClick={() => setShowPaymentDialog(true)}>
            Upgrade Plan
          </Button>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <p className="text-sm text-muted-foreground">Current Plan</p>
              <Badge variant={summary.plan === 'free' ? 'secondary' : 'default'}>
                {summary.plan.charAt(0).toUpperCase() + summary.plan.slice(1)}
              </Badge>
            </div>
            
            <div>
              <p className="text-sm text-muted-foreground">Next Renewal</p>
              <p className="text-lg font-semibold">{summary.renew_date}</p>
            </div>
            
            <div>
              <p className="text-sm text-muted-foreground">Credits Remaining</p>
              <Progress value={(summary.credits_remaining / 3) * 100} className="h-2" />
              <p className="text-sm text-muted-foreground mt-2">
                {summary.credits_remaining} credits remaining
              </p>
            </div>

            <div>
              <p className="text-sm text-muted-foreground">Monthly Usage</p>
              <p className="text-lg font-semibold">${summary.usage_usd.toFixed(2)}</p>
            </div>

            <div>
              <p className="text-sm text-muted-foreground">Plan Features</p>
              <ul className="text-sm space-y-1 mt-1">
                {summary.features.map((feature, index) => (
                  <li key={index} className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-primary rounded-full"></span>
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Payment Methods</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {methods.length > 0 ? (
              methods.map((method) => (
                <div key={method.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-muted rounded flex items-center justify-center">
                      {method.type === 'crypto' ? '₿' : '💳'}
                    </div>
                    <div>
                      <p className="font-medium">{method.brand}</p>
                      <p className="text-sm text-muted-foreground">
                        {method.type === 'crypto' ? 'Crypto Wallet' : `Card ending in ${method.last4}`}
                      </p>
                    </div>
                  </div>
                  <Badge variant="outline">{method.type}</Badge>
                </div>
              ))
            ) : (
              <p className="text-muted-foreground">No payment methods configured</p>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Invoice History</CardTitle>
        </CardHeader>
        <CardContent>
          {invoices.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Download</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {invoices.map((invoice) => (
                  <TableRow key={invoice.id}>
                    <TableCell>{new Date(invoice.date).toLocaleDateString()}</TableCell>
                    <TableCell>${invoice.total.toFixed(2)}</TableCell>
                    <TableCell>
                      <Badge variant="default">Paid</Badge>
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm" asChild>
                        <a href={invoice.pdf_url} target="_blank" rel="noopener noreferrer">
                          Download PDF
                        </a>
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <p className="text-muted-foreground">No invoices available</p>
          )}
        </CardContent>
      </Card>

      <PaymentDialog 
        open={showPaymentDialog}
        onOpenChange={setShowPaymentDialog}
        currentTier={summary.plan}
      />
    </div>
  );
}
