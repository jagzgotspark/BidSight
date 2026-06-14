"use client";
import { useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import api from "@/lib/api";
import { Tender } from "@/types/tender";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { formatBudget, daysToDeadline, categoryLabel, sourceLabel,tenderSourceUrl } from "@/lib/tenderUtils";
import { ArrowLeft, ExternalLink, Clock, Building2, MapPin } from "lucide-react";

function MatchScoreSection({ score, reasoning }: { score: number; reasoning: string | null }) {
  const color = score >= 70 ? "bg-green-500" : score >= 50 ? "bg-amber-400" : "bg-gray-300";
  const labelColor = score >= 70 ? "text-green-700" : score >= 50 ? "text-amber-600" : "text-gray-500";
  const bgCard = score >= 70 ? "bg-green-50 border-green-100" : score >= 50 ? "bg-amber-50 border-amber-100" : "bg-gray-50 border-gray-100";

  return (
    <Card className={`p-4 border ${bgCard}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium">AI Match Score</span>
        <span className={`text-2xl font-bold tabular-nums ${labelColor}`}>{score}%</span>
      </div>
      <div className="h-2 rounded-full bg-gray-200 overflow-hidden mb-3">
        <div className={`h-full rounded-full ${color} transition-all`} style={{ width: `${score}%` }} />
      </div>
      {reasoning && (
        <p className="text-xs text-muted-foreground leading-relaxed">{reasoning}</p>
      )}
    </Card>
  );
}

export default function TenderDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  const { data: tender, isLoading, isError } = useQuery<Tender>({
    queryKey: ["tender", id],
    queryFn: async () => {
      const res = await api.get(`/tenders/${id}`);
      return res.data;
    },
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-sm text-muted-foreground">Loading tender...</p>
      </div>
    );
  }

  if (isError || !tender) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-sm text-destructive">Tender not found.</p>
      </div>
    );
  }

  const days = daysToDeadline(tender.deadline);

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b px-6 py-4 flex items-center justify-between">
        <span className="text-xl font-semibold tracking-tight">BidSight</span>
        <nav className="flex gap-4 text-sm text-muted-foreground">
          <a href="/dashboard" className="hover:text-foreground">Tenders</a>
          <a href="/dashboard/pipeline" className="hover:text-foreground">Pipeline</a>
          <a href="/dashboard/proposals" className="hover:text-foreground">Proposals</a>
          <a href="/dashboard/analytics" className="hover:text-foreground">Analytics</a>
          <a href="/dashboard/alerts" className="hover:text-foreground">Alerts</a>
        </nav>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8 space-y-6">
        <button onClick={() => router.back()}
          className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors">
          <ArrowLeft size={14} /> Back
        </button>

        {/* Title row */}
        <div className="space-y-2">
          <div className="flex items-start gap-3">
            <h1 className="text-xl font-semibold leading-snug flex-1">{tender.title}</h1>
            href={tenderSourceUrl(tender)}
              target="_blank"
              rel="noopener noreferrer"
              title={`Find on ${sourceLabel(tender.source)} — tender ID ${tender.tender_id}`}
              className="text-muted-foreground hover:text-foreground mt-1 flex-shrink-0"
            >
              <ExternalLink size={15} />
            </a>
          </div>
          <div className="flex flex-wrap gap-3 text-sm text-muted-foreground">
            {tender.authority && (
              <span className="flex items-center gap-1"><Building2 size={13} />{tender.authority}</span>
            )}
            {tender.location && (
              <span className="flex items-center gap-1"><MapPin size={13} />{tender.location}</span>
            )}
            {days !== null && (
              <span className="flex items-center gap-1">
                <Clock size={13} />
                {days <= 0 ? "Closed" : days === 1 ? "Closes tomorrow" : `Closes in ${days} days`}
              </span>
            )}
          </div>
          <div className="flex gap-2 flex-wrap">
            <Badge variant="outline">{sourceLabel(tender.source)}</Badge>
            <Badge variant="secondary">{categoryLabel(tender.category)}</Badge>
            {days !== null && days <= 7 && days > 0 && (
              <Badge variant="destructive">Urgent</Badge>
            )}
          </div>
        </div>

        {/* Match score */}
        {tender.match_score !== null && tender.match_score !== undefined && (
          <MatchScoreSection score={tender.match_score} reasoning={tender.match_reasoning} />
        )}

        {/* Key figures */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <Card className="p-4">
            <p className="text-xs text-muted-foreground mb-1">Budget</p>
            <p className="text-lg font-semibold">{formatBudget(tender)}</p>
          </Card>
          <Card className="p-4">
            <p className="text-xs text-muted-foreground mb-1">Deadline</p>
            <p className="text-lg font-semibold">
              {tender.deadline ? new Date(tender.deadline).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" }) : tender.deadline_raw || "—"}
            </p>
          </Card>
          <Card className="p-4">
            <p className="text-xs text-muted-foreground mb-1">Status</p>
            <p className="text-lg font-semibold capitalize">{tender.status}</p>
          </Card>
        </div>

        {/* Description */}
        {tender.description && (
          <section className="space-y-2">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">Description</h2>
            <p className="text-sm leading-relaxed whitespace-pre-line">{tender.description}</p>
          </section>
        )}

        {/* AI insights */}
        {(tender.ai_summary || tender.ai_risk || tender.ai_eligibility) && (
          <section className="space-y-3">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">AI Insights</h2>
            <div className="grid gap-3">
              {tender.ai_summary && (
                <Card className="p-4">
                  <p className="text-xs font-medium mb-1">Summary</p>
                  <p className="text-sm text-muted-foreground leading-relaxed">{tender.ai_summary}</p>
                </Card>
              )}
              {tender.ai_eligibility && (
                <Card className="p-4">
                  <p className="text-xs font-medium mb-1">Eligibility</p>
                  <p className="text-sm text-muted-foreground leading-relaxed">{tender.ai_eligibility}</p>
                </Card>
              )}
              {tender.ai_risk && (
                <Card className="p-4">
                  <p className="text-xs font-medium mb-1">Risk Flags</p>
                  <p className="text-sm text-muted-foreground leading-relaxed">{tender.ai_risk}</p>
                </Card>
              )}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
