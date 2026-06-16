"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { Bid, STAGES } from "@/types/bid";
import { daysToDeadline } from "@/lib/tenderUtils";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Clock, Building2, Trash2 } from "lucide-react";
import { useState } from "react";

export default function PipelinePage() {
  const queryClient = useQueryClient();
  const [draggingId, setDraggingId] = useState<string | null>(null);

  const { data: bids = [], isLoading, isError } = useQuery<Bid[]>({
    queryKey: ["bids"],
    queryFn: async () => {
      const res = await api.get("/bids/");
      return res.data;
    },
  });

  const updateBid = useMutation({
    mutationFn: async ({ id, stage }: { id: string; stage: string }) => {
      const res = await api.patch(`/bids/${id}`, { stage });
      return res.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["bids"] }),
  });

  const deleteBid = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/bids/${id}`);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["bids"] }),
  });

  const handleDrop = (stage: string) => {
    if (draggingId) {
      updateBid.mutate({ id: draggingId, stage });
      setDraggingId(null);
    }
  };

  const bidsByStage = (stageId: string) =>
    bids.filter((b) => b.stage === stageId);

  if (isError) {
    return (
      <div className="min-h-screen bg-background">
        <header className="border-b px-6 py-4 flex items-center justify-between">
          <span className="text-xl font-semibold tracking-tight">BidSight</span>
          <nav className="flex gap-3 text-sm text-muted-foreground overflow-x-auto">
            <a href="/dashboard" className="hover:text-foreground">Tenders</a>
            <span className="text-foreground font-medium">Pipeline</span>
            <a href="/dashboard/proposals" className="hover:text-foreground">Proposals</a>
            <a href="/dashboard/analytics" className="hover:text-foreground">Analytics</a>
            <a href="/dashboard/alerts" className="hover:text-foreground">Alerts</a>
            <a href="/dashboard/settings" className="hover:text-foreground">Settings</a>
          </nav>
        </header>
        <div className="flex items-center justify-center h-64 text-destructive text-sm">
          Could not load pipeline. Make sure the backend is running.
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <header className="border-b px-6 py-4 flex items-center justify-between">
          <span className="text-xl font-semibold tracking-tight">BidSight</span>
          <nav className="flex gap-4 text-sm text-muted-foreground">
            <a href="/dashboard" className="hover:text-foreground">Tenders</a>
            <span className="text-foreground font-medium">Pipeline</span>
            <a href="/dashboard/proposals" className="hover:text-foreground">Proposals</a>
            <a href="/dashboard/analytics" className="hover:text-foreground">Analytics</a>
            <a href="/dashboard/alerts" className="hover:text-foreground">Alerts</a>
            <a href="/dashboard/settings" style={{ color: "#a3a3a3", textDecoration: "none", fontSize: "0.875rem" }} className="hover:text-foreground">Settings</a>
        
          </nav>
        </header>
        <div className="flex items-center justify-center h-64 text-muted-foreground text-sm">
          Loading pipeline...
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b px-6 py-4 flex items-center justify-between">
        <span className="text-xl font-semibold tracking-tight">BidSight</span>
        <nav className="flex gap-4 text-sm text-muted-foreground">
          <a href="/dashboard" className="hover:text-foreground">Tenders</a>
          <span className="text-foreground font-medium">Pipeline</span>
          <a href="/dashboard/proposals" className="hover:text-foreground">Proposals</a>
          <a href="/dashboard/analytics" className="hover:text-foreground">Analytics</a>
          <a href="/dashboard/alerts" className="hover:text-foreground">Alerts</a>
          <a href="/dashboard/settings" style={{ color: "#a3a3a3", textDecoration: "none", fontSize: "0.875rem" }} className="hover:text-foreground">Settings</a>
        
        </nav>
      </header>

      <main className="px-6 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold">Bid Pipeline</h1>
          <p className="text-muted-foreground text-sm mt-1">
            {bids.length} total bids · drag cards to move between stages
          </p>
        </div>

        <div className="flex gap-3 overflow-x-auto pb-4">
          {STAGES.map((stage) => {
            const stageBids = bidsByStage(stage.id);
            return (
              <div
                key={stage.id}
                className="flex-shrink-0 w-64"
                onDragOver={(e) => e.preventDefault()}
                onDrop={() => handleDrop(stage.id)}
              >
                {/* Column header */}
                <div className={`rounded-t-lg px-3 py-2 ${stage.color} border border-b-0`}>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                      {stage.label}
                    </span>
                    <span className="text-xs font-medium bg-white rounded-full px-2 py-0.5 border">
                      {stageBids.length}
                    </span>
                  </div>
                </div>

                {/* Cards */}
                <div className={`min-h-48 border rounded-b-lg p-2 space-y-2 ${stage.color}`}>
                  {stageBids.map((bid) => (
                    <BidCard
                      key={bid.id}
                      bid={bid}
                      onDragStart={() => setDraggingId(bid.id)}
                      onDelete={() => deleteBid.mutate(bid.id)}
                    />
                  ))}
                  {stageBids.length === 0 && (
                    <div className="text-center py-8 text-xs text-muted-foreground">
                      Drop here
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {bids.length === 0 && (
          <div className="text-center py-16 text-muted-foreground">
            <p className="text-sm">No bids in pipeline yet.</p>
            <p className="text-xs mt-1">
              Go to the{" "}
              <a href="/dashboard" className="underline">
                Tender Feed
              </a>{" "}
              and click "Track" on a tender to add it here.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}

function BidCard({
  bid,
  onDragStart,
  onDelete,
}: {
  bid: Bid;
  onDragStart: () => void;
  onDelete: () => void;
}) {
  const days = daysToDeadline(bid.tender_deadline);

  return (
    <Card
      draggable
      onDragStart={onDragStart}
      className="p-3 cursor-grab active:cursor-grabbing hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <p className="text-xs font-medium leading-snug line-clamp-2 flex-1">
          {bid.tender_title || "Untitled tender"}
        </p>
        <button
          onClick={onDelete}
          className="text-muted-foreground hover:text-destructive flex-shrink-0"
        >
          <Trash2 size={12} />
        </button>
      </div>

      <div className="space-y-1">
        {bid.tender_authority && (
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <Building2 size={10} />
            <span className="truncate">{bid.tender_authority}</span>
          </div>
        )}
        {days !== null && (
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <Clock size={10} />
            <span>
              {days <= 0
                ? "Closed"
                : days === 1
                ? "Tomorrow"
                : `${days} days left`}
            </span>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between mt-2">
        <div className="flex gap-1">
          {bid.tender_source && (
            <Badge variant="outline" className="text-xs px-1.5 py-0">
              {bid.tender_source.toUpperCase()}
            </Badge>
          )}
          {bid.tender_budget_raw && (
            <Badge variant="secondary" className="text-xs px-1.5 py-0">
              {bid.tender_budget_raw}
            </Badge>
          )}
        </div>
        {bid.match_score !== null && bid.match_score !== undefined && (
          <span
            className={`text-xs font-semibold ${
              bid.match_score >= 70
                ? "text-green-600"
                : bid.match_score >= 50
                ? "text-amber-600"
                : "text-muted-foreground"
            }`}
          >
            {bid.match_score}%
          </span>
        )}
      </div>
    </Card>
  );
}