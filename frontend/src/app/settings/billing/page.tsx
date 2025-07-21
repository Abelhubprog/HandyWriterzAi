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

import BillingPanel from "@/components/BillingPanel";

export default function BillingPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Billing</h1>
      <p className="text-muted-foreground">Manage your billing and subscription.</p>
      <div className="mt-6">
        <BillingPanel />
      </div>
    </div>
  );
}
