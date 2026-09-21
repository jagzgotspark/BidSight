"use client";

import { useState } from "react";
import Script from "next/script";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth, useUser } from "@clerk/nextjs";
import axios from "axios";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2 } from "lucide-react";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface Plan {
  id: string;
  name: string;
  amount_paise: number;
  amount_display: string;
  interval_days: number;
  features: string[];
}

interface SubscriptionStatus {
  plan: string;
  status: string;
  current_period_end: string | null;
  is_active: boolean;
}

declare global {
  interface Window {
    Razorpay: any;
  }
}

export default function BillingPage() {
  const { getToken } = useAuth();
  const { user } = useUser();
  const qc = useQueryClient();
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [agreed, setAgreed] = useState(false);

  const { data: plans } = useQuery<Plan[]>({
    queryKey: ["billing", "plans"],
    queryFn: async () => (await axios.get(`${BASE}/billing/plans`)).data,
  });

  const { data: status, isLoading: statusLoading } = useQuery<SubscriptionStatus>({
    queryKey: ["billing", "status"],
    queryFn: async () => {
      const token = await getToken();
      return (
        await axios.get(`${BASE}/billing/status`, {
          headers: { Authorization: `Bearer ${token}` },
        })
      ).data;
    },
  });

  async function handleUpgrade(planId: string) {
    if (!agreed) {
      setError("Please agree to the Terms of Service and Refund Policy before upgrading.");
      return;
    }
    setError(null);
    setProcessing(true);
    try {
      const token = await getToken();
      const { data: order } = await axios.post(
        `${BASE}/billing/checkout`,
        { plan: planId },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const rzp = new window.Razorpay({
        key: order.razorpay_key_id,
        amount: order.amount_paise,
        currency: order.currency,
        name: "BidSight",
        description: "Professional plan — monthly",
        order_id: order.order_id,
        prefill: {
          name: user?.fullName || "",
          email: user?.primaryEmailAddress?.emailAddress || "",
        },
        handler: async (response: any) => {
          try {
            const verifyToken = await getToken();
            await axios.post(
              `${BASE}/billing/verify`,
              {
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
              },
              { headers: { Authorization: `Bearer ${verifyToken}` } }
            );
            qc.invalidateQueries({ queryKey: ["billing", "status"] });
          } catch {
            setError("Payment succeeded but activation failed. Contact support with your payment ID.");
          } finally {
            setProcessing(false);
          }
        },
        modal: {
          ondismiss: () => setProcessing(false),
        },
        theme: { color: "#0F6E56" },
      });

      rzp.on("payment.failed", () => {
        setError("Payment failed. Please try again.");
        setProcessing(false);
      });

      rzp.open();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Could not start checkout.");
      setProcessing(false);
    }
  }

  const isPro = status?.is_active && status.plan === "professional";

  return (
    <div className="min-h-screen bg-background">
      <Script src="https://checkout.razorpay.com/v1/checkout.js" strategy="lazyOnload" />

      <header className="border-b px-6 py-4 flex items-center justify-between">
        <span className="text-xl font-semibold tracking-tight">BidSight</span>
        <nav className="flex gap-3 text-sm text-muted-foreground overflow-x-auto">
          <a href="/dashboard" className="hover:text-foreground">Tenders</a>
          <a href="/dashboard/pipeline" className="hover:text-foreground">Pipeline</a>
          <a href="/dashboard/proposals" className="hover:text-foreground">Proposals</a>
          <a href="/dashboard/analytics" className="hover:text-foreground">Analytics</a>
          <a href="/dashboard/alerts" className="hover:text-foreground">Alerts</a>
          <span className="text-foreground font-medium">Billing</span>
          <a href="/dashboard/settings" className="hover:text-foreground">Settings</a>
        </nav>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-8 space-y-6">
        <div>
          <h1 className="text-2xl font-semibold">Billing</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Manage your BidSight subscription
          </p>
        </div>

        {!statusLoading && status && (
          <Card className="p-5 flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Current plan</p>
              <p className="text-lg font-semibold capitalize">{status.plan}</p>
              {status.is_active && status.current_period_end && (
                <p className="text-xs text-muted-foreground mt-1">
                  Renews {new Date(status.current_period_end).toLocaleDateString("en-IN", {
                    day: "numeric", month: "short", year: "numeric",
                  })}
                </p>
              )}
            </div>
            <Badge variant={status.is_active ? "default" : "outline"}>
              {status.is_active ? "Active" : "Free tier"}
            </Badge>
          </Card>
        )}

        {error && (
          <div className="text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-md px-4 py-3">
            {error}
          </div>
        )}

        {!isPro && (
          <label className="flex items-start gap-2 text-xs text-muted-foreground">
            <input
              type="checkbox"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              className="mt-0.5"
            />
            <span>
              I agree to the{" "}
              <a href="/legal/terms" target="_blank" className="underline hover:text-foreground">Terms of Service</a>{" "}
              and{" "}
              <a href="/legal/refund" target="_blank" className="underline hover:text-foreground">Refund Policy</a>.
            </span>
          </label>
        )}

        <div className="grid gap-4">
          {plans?.map((plan) => (
            <Card key={plan.id} className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-lg font-semibold">{plan.name}</h2>
                  <p className="text-2xl font-bold mt-1">{plan.amount_display}</p>
                </div>
                {isPro && plan.id === "professional" ? (
                  <Badge>Current plan</Badge>
                ) : (
                  <button
                    onClick={() => handleUpgrade(plan.id)}
                    disabled={processing || !agreed}
                    className="px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium disabled:opacity-50"
                  >
                    {processing ? "Processing…" : "Upgrade"}
                  </button>
                )}
              </div>
              <ul className="space-y-2">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm text-muted-foreground">
                    <CheckCircle2 size={14} className="text-emerald-600 flex-shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>
            </Card>
          ))}
        </div>
      </main>
    </div>
  );
}
