"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { Card } from "@/components/ui/card";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from "recharts";

const CATEGORY_LABELS: Record<string, string> = {
  it_software: "IT / Software",
  cloud: "Cloud",
  ai_ml: "AI / ML",
  cybersecurity: "Cybersecurity",
  consulting: "Consulting",
  infrastructure: "Infrastructure",
  hardware: "Hardware",
  other: "Other",
};

const STAGE_ORDER = ["new", "interested", "evaluating", "drafting", "submitted", "won", "lost"];

const COLORS = ["#1D9E75", "#3B82F6", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#6B7280"];

export default function AnalyticsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["analytics"],
    queryFn: async () => {
      const res = await api.get("/analytics/overview");
      return res.data;
    },
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <div className="flex items-center justify-center h-64 text-muted-foreground text-sm">
          Loading analytics...
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <div className="flex items-center justify-center h-64 text-destructive text-sm">
          Could not load analytics. Make sure the backend is running.
        </div>
      </div>
    );
  }

  const categoryData = data?.by_category?.map((c: any) => ({
    name: CATEGORY_LABELS[c.category] || c.category,
    count: c.count,
  })) || [];

  const scoreData = [
    { name: "High (70+)", value: data?.score_distribution?.high || 0, color: "#1D9E75" },
    { name: "Medium (50-69)", value: data?.score_distribution?.medium || 0, color: "#F59E0B" },
    { name: "Low (<50)", value: data?.score_distribution?.low || 0, color: "#EF4444" },
  ];

  const sourceData = data?.by_source?.map((s: any) => ({
    name: s.source.toUpperCase(),
    count: s.count,
  })) || [];

  const pipelineData = STAGE_ORDER
    .filter((stage) => data?.pipeline?.[stage] !== undefined)
    .map((stage) => ({
      name: stage.charAt(0).toUpperCase() + stage.slice(1),
      count: data?.pipeline?.[stage] || 0,
    }));

  const timeData = data?.tenders_over_time?.map((t: any) => ({
    date: t.date.slice(5), // show MM-DD
    count: t.count,
  })) || [];

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="max-w-6xl mx-auto px-6 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold">Analytics</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Overview of your tender intelligence
          </p>
        </div>

        {/* Top stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {[
            { label: "Total Tenders", value: data?.total_tenders || 0 },
            { label: "Active Tenders", value: data?.active_tenders || 0 },
            { label: "Avg Match Score", value: `${data?.avg_match_score || 0}%` },
            { label: "Bids in Pipeline", value: Object.values(data?.pipeline || {}).reduce((a: number, b: any) => a + b, 0) },
          ].map((stat) => (
            <Card key={stat.label} className="p-4 text-center">
              <div className="text-2xl font-bold">{stat.value}</div>
              <div className="text-xs text-muted-foreground mt-1">{stat.label}</div>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* By Category */}
          <Card className="p-5">
            <h2 className="text-sm font-semibold mb-4">Tenders by Category</h2>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={categoryData} layout="vertical">
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={90} />
                <Tooltip />
                <Bar dataKey="count" fill="#1D9E75" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {/* Match Score Distribution */}
          <Card className="p-5">
            <h2 className="text-sm font-semibold mb-4">Match Score Distribution</h2>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={scoreData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                  labelLine={false}
                >
                  {scoreData.map((entry, index) => (
                    <Cell key={index} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>

          {/* By Source */}
          <Card className="p-5">
            <h2 className="text-sm font-semibold mb-4">Tenders by Source</h2>
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={sourceData}>
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {/* Pipeline funnel */}
          <Card className="p-5">
            <h2 className="text-sm font-semibold mb-4">Bid Pipeline</h2>
            {pipelineData.length === 0 ? (
              <div className="flex items-center justify-center h-32 text-xs text-muted-foreground">
                No bids in pipeline yet
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={pipelineData}>
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </Card>
        </div>

        {/* Tenders over time */}
        {timeData.length > 0 && (
          <Card className="p-5">
            <h2 className="text-sm font-semibold mb-4">Tenders Scraped Over Time</h2>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={timeData}>
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#1D9E75" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        )}
      </main>
    </div>
  );
}

function Header() {
  return (
    <header className="border-b px-6 py-4 flex items-center justify-between">
      <span className="text-xl font-semibold tracking-tight">BidSight</span>
      <nav className="flex gap-4 text-sm text-muted-foreground">
        <a href="/dashboard" className="hover:text-foreground">Tenders</a>
        <a href="/dashboard/pipeline" className="hover:text-foreground">Pipeline</a>
        <a href="/dashboard/proposals" className="hover:text-foreground">Proposals</a>
        <span className="text-foreground font-medium">Analytics</span>
        <a href="/dashboard/alerts" className="hover:text-foreground">Alerts</a>
        <a href="/dashboard/settings" style={{ color: "#a3a3a3", textDecoration: "none", fontSize: "0.875rem" }} className="hover:text-foreground">Settings</a>
        
      </nav>
    </header>
  );
}