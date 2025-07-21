"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

// Mock data fetching functions
const fetchBillingSummary = async () => ({
  plan: "Pro",
  renew_date: "2025-08-17",
  usage_usd: 42.5,
  plan_limit_usd: 100,
});

const fetchPaymentMethods = async () => [
  { id: "pm_123", brand: "Visa", last4: "4242", type: "card" },
  { id: "cw_456", brand: "USDC", last4: "a1b2", type: "crypto" },
];

const fetchInvoices = async () => [
  { id: "in_123", pdf_url: "/invoices/in_123.pdf", total: 50.0, date: "2025-07-17" },
  { id: "in_456", pdf_url: "/invoices/in_456.pdf", total: 50.0, date: "2025-06-17" },
];

export default function BillingPanel() {
  const [summary, setSummary] = useState<{ plan: string; renew_date: string; usage_usd: number; plan_limit_usd: number; } | null>(null);
  const [methods, setMethods] = useState<{ id: string; brand: string; last4: string; type: string; }[]>([]);
  const [invoices, setInvoices] = useState<{ id: string; pdf_url: string; total: number; date: string; }[]>([]);

  useEffect(() => {
    fetchBillingSummary().then(setSummary);
    fetchPaymentMethods().then(setMethods);
    fetchInvoices().then(setInvoices);
  }, []);

  if (!summary) {
    return <div>Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Billing Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground">Current Plan</p>
              <p className="text-lg font-semibold">{summary.plan}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Next Renewal</p>
              <p className="text-lg font-semibold">{summary.renew_date}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Monthly Usage</p>
              <Progress value={(summary.usage_usd / summary.plan_limit_usd) * 100} className="h-2" />
              <p className="text-sm text-muted-foreground mt-2">
                ${summary.usage_usd.toFixed(2)} / ${summary.plan_limit_usd.toFixed(2)}
              </p>
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
            {methods.map((method) => (
              <div key={method.id} className="flex items-center justify-between">
                <p>{method.brand} ending in {method.last4}</p>
                <Button variant="outline">Remove</Button>
              </div>
            ))}
            <Button>Add Payment Method</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Invoices</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>PDF</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {invoices.map((invoice) => (
                <TableRow key={invoice.id}>
                  <TableCell>{invoice.date}</TableCell>
                  <TableCell>${invoice.total.toFixed(2)}</TableCell>
                  <TableCell>
                    <a href={invoice.pdf_url} target="_blank" rel="noopener noreferrer">
                      Download
                    </a>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
