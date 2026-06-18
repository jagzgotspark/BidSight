"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import axios from "axios";
import { Alert } from "@/types/alert";
import { Card } from "@/components/ui/card";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

function thresholdColor(days: number | null) {
  if (days === null) return { bg: "#F1EFE8", fg: "#444441" };
  if (days <= 3) return { bg: "#FCEBEB", fg: "#A32D2D" };
  if (days <= 7) return { bg: "#FAEEDA", fg: "#854F0B" };
  return { bg: "#E1F5EE", fg: "#0F6E56" };
}

export default function AlertsPage() {
  const qc = useQueryClient();
  const { getToken } = useAuth();

  const { data: alerts, isLoading } = useQuery<Alert[]>({
    queryKey: ["alerts"],
    queryFn: async () => {
      const token = await getToken();
      const res = await axios.get(`${BASE}/alerts/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      return res.data;
    },
  });

  const markRead = useMutation({
    mutationFn: async (id: string) => {
      const token = await getToken();
      return axios.post(`${BASE}/alerts/${id}/read`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["alerts"] }),
  });

  const markAll = useMutation({
    mutationFn: async () => {
      const token = await getToken();
      return axios.post(`${BASE}/alerts/read-all`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["alerts"] }),
  });

  const unread = alerts?.filter((a) => !a.is_read).length ?? 0;

  return (
    <div className="min-h-screen bg-background">
      <Header unread={unread} />
      <main className="max-w-3xl mx-auto px-6 py-8">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Deadline Alerts</h1>
            <p className="text-muted-foreground text-sm mt-1">
              Reminders for tenders in your pipeline
            </p>
          </div>
          {unread > 0 && (
            <button
              onClick={() => markAll.mutate()}
              className="text-sm text-muted-foreground hover:text-foreground"
            >
              Mark all read
            </button>
          )}
        </div>

        {isLoading && (
          <p className="text-sm text-muted-foreground py-12 text-center">Loading...</p>
        )}

        {alerts && alerts.length === 0 && (
          <p className="text-sm text-muted-foreground py-12 text-center">
            No alerts yet. Track tenders in your pipeline and you&apos;ll be reminded as deadlines approach.
          </p>
        )}

        <div className="space-y-3">
          {alerts?.map((a) => {
            const isMatch = a.kind === "match";
            const c = isMatch ? { bg: "#E1F5EE", fg: "#0F6E56" } : thresholdColor(a.days_left);
            return (
              <Card
                key={a.id}
                className={`p-4 flex items-start justify-between gap-4 ${a.is_read ? "opacity-60" : ""}`}
              >
                <div className="flex-1 space-y-1">
                  <div className="flex items-center gap-2">
                    <span
                      className="text-xs font-medium px-2 py-0.5 rounded-full"
                      style={{ background: c.bg, color: c.fg }}
                    >
                      {isMatch
                        ? `New ${a.score}% match`
                        : a.days_left === 0
                        ? "Closes today"
                        : a.days_left === 1
                        ? "1 day left"
                        : `${a.days_left} days left`}
                    </span>
                    {!a.is_read && (
                      <span className="w-1.5 h-1.5 rounded-full bg-foreground" />
                    )}
                  </div>
                  <p className="text-sm font-medium leading-snug">{a.tender_title}</p>
                  <p className="text-xs text-muted-foreground">
                    Deadline {a.deadline ? new Date(a.deadline).toLocaleDateString() : "—"}
                  </p>
                </div>
                {!a.is_read && (
                  <button
                    onClick={() => markRead.mutate(a.id)}
                    className="text-xs text-muted-foreground hover:text-foreground flex-shrink-0"
                  >
                    Mark read
                  </button>
                )}
              </Card>
            );
          })}
        </div>
      </main>
    </div>
  );
}

function Header({ unread }: { unread: number }) {
  return (
    <header className="border-b px-6 py-4 flex items-center justify-between">
      <span className="text-xl font-semibold tracking-tight">BidSight</span>
      <nav className="flex gap-3 text-sm text-muted-foreground overflow-x-auto">
        <a href="/dashboard" className="hover:text-foreground">Tenders</a>
        <a href="/dashboard/pipeline" className="hover:text-foreground">Pipeline</a>
        <a href="/dashboard/proposals" className="hover:text-foreground">Proposals</a>
        <a href="/dashboard/analytics" className="hover:text-foreground">Analytics</a>
        <a href="/dashboard/settings" style={{ color: "#a3a3a3", textDecoration: "none", fontSize: "0.875rem" }} className="hover:text-foreground">Settings</a>
        
        <span className="text-foreground font-medium flex items-center gap-1">
          Alerts
          {unread > 0 && (
            <span className="text-[10px] bg-red-500 text-white rounded-full px-1.5 py-0.5 leading-none">
              {unread}
            </span>
          )}
        </span>
      </nav>
    </header>
  );
}