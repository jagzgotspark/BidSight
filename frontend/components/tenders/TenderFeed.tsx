"use client";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import axios from "axios";
import { Tender, TenderListResponse } from "@/types/tender";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
import TenderCard from "./TenderCard";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useState, useEffect, useRef } from "react";

export default function TenderFeed() {
  const [search, setSearch] = useState("");
  const [source, setSource] = useState("all");
  const [category, setCategory] = useState("all");
  const [scoringId, setScoringId] = useState<string | null>(null);
  const attempted = useRef<Set<string>>(new Set());
  const qc = useQueryClient();
  const { getToken } = useAuth();

  const queryKey = ["tenders", search, source, category];

  const { data, isLoading, isError } = useQuery<TenderListResponse>({
    queryKey,
    queryFn: async () => {
      const token = await getToken();
      const params: Record<string, string> = {};
      if (search) params.search = search;
      if (source !== "all") params.source = source;
      if (category !== "all") params.category = category;
      const res = await axios.get(`${BASE}/tenders/`, {
        params,
        headers: { Authorization: `Bearer ${token}` },
      });
      return res.data;
    },
  });

  // Background scoring queue: score unscored tenders one at a time
  useEffect(() => {
    if (!data?.items) return;
    const queue = data.items.filter(
      (t) =>
        (t.match_score === null || t.match_score === undefined) &&
        !attempted.current.has(t.id)
    );
    if (queue.length === 0) return;

    let cancelled = false;
    (async () => {
      for (const t of queue) {
        if (cancelled) break;
        attempted.current.add(t.id);
        setScoringId(t.id);
        try {
          const token = await getToken();
          const res = await axios.post(`${BASE}/match/score/${t.id}`, {}, {
            headers: { Authorization: `Bearer ${token}` },
          });
          const { match_score, match_reasoning } = res.data;
          qc.setQueryData<TenderListResponse>(queryKey, (old) => {
            if (!old) return old;
            return {
              ...old,
              items: old.items.map((it) =>
                it.id === t.id ? { ...it, match_score, match_reasoning } : it
              ),
            };
          });
        } catch {
          // Leave unscored — card will show "Not scored yet"
        }
      }
      if (!cancelled) setScoringId(null);
    })();

    return () => {
      cancelled = true;
      setScoringId(null);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, qc, search, source, category]);

  return (
    <div className="space-y-4">
      <div className="flex gap-3 flex-wrap">
        <Input placeholder="Search tenders..." className="max-w-xs"
          value={search} onChange={(e) => setSearch(e.target.value)} />
        <Select value={source} onValueChange={setSource}>
          <SelectTrigger className="w-36"><SelectValue placeholder="Source" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All sources</SelectItem>
            <SelectItem value="gem">GeM</SelectItem>
            <SelectItem value="cppp">CPPP</SelectItem>
          </SelectContent>
        </Select>
        <Select value={category} onValueChange={setCategory}>
          <SelectTrigger className="w-44"><SelectValue placeholder="Category" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All categories</SelectItem>
            <SelectItem value="it_software">IT / Software</SelectItem>
            <SelectItem value="cloud">Cloud</SelectItem>
            <SelectItem value="ai_ml">AI / ML</SelectItem>
            <SelectItem value="cybersecurity">Cybersecurity</SelectItem>
            <SelectItem value="consulting">Consulting</SelectItem>
            <SelectItem value="infrastructure">Infrastructure</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground py-12 text-center">Loading tenders...</p>}
      {isError && <p className="text-sm text-destructive py-12 text-center">Could not connect to the API. Make sure the backend is running.</p>}
      {data && data.items.length === 0 && (
        <p className="text-sm text-muted-foreground py-12 text-center">No tenders yet. Run the scraper to populate data.</p>
      )}
      {data && data.items.map((tender) => (
        <TenderCard key={tender.id} tender={tender} isScoring={scoringId === tender.id} />
      ))}
      {data && data.total > 0 && (
        <p className="text-xs text-muted-foreground text-right">Showing {data.items.length} of {data.total} tenders</p>
      )}
    </div>
  );
}