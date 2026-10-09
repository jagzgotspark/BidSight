"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import axios from "axios";
import { Sparkles } from "lucide-react";
import { TenderListResponse } from "@/types/tender";
import TenderCard from "./TenderCard";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const TOP_MATCH_THRESHOLD = 80;
export const TOP_MATCHES_KEY = ["tenders", "top-matches"];
const COLLAPSED_COUNT = 5;

// Active tenders scoring 80%+ against the profile, best first. Refetches on an
// interval so tenders scored in the background show up without a reload.
export default function TopMatches() {
  const [expanded, setExpanded] = useState(false);
  const { getToken } = useAuth();

  const { data } = useQuery<TenderListResponse>({
    queryKey: TOP_MATCHES_KEY,
    queryFn: async () => {
      const token = await getToken();
      const res = await axios.get(`${BASE}/tenders/`, {
        params: { min_score: TOP_MATCH_THRESHOLD, sort: "score", per_page: 50 },
        headers: { Authorization: `Bearer ${token}` },
      });
      return res.data;
    },
    refetchInterval: 60000,
    refetchOnWindowFocus: true,
    staleTime: 30000,
  });

  if (!data) return null;

  const items = expanded ? data.items : data.items.slice(0, COLLAPSED_COUNT);

  return (
    <section className="rounded-lg border border-green-200 bg-green-50/40 p-4 space-y-3 dark:border-green-900 dark:bg-green-950/20">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Sparkles size={16} className="text-green-600" />
          <h2 className="text-sm font-semibold">Top matches</h2>
          <span className="text-xs text-muted-foreground">
            {data.total} tender{data.total === 1 ? "" : "s"} scoring {TOP_MATCH_THRESHOLD}%+
          </span>
        </div>
        {data.items.length > COLLAPSED_COUNT && (
          <button
            type="button"
            onClick={() => setExpanded((v) => !v)}
            className="text-xs text-muted-foreground hover:text-foreground underline"
          >
            {expanded ? "Show fewer" : `Show all ${data.items.length}`}
          </button>
        )}
      </div>

      {data.total === 0 ? (
        <p className="text-xs text-muted-foreground">
          No tenders at {TOP_MATCH_THRESHOLD}%+ yet. New tenders are scored against your profile
          automatically, and strong matches will appear here.
        </p>
      ) : (
        items.map((tender) => <TenderCard key={tender.id} tender={tender} />)
      )}
    </section>
  );
}
