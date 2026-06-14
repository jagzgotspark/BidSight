import { Tender } from "@/types/tender";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { formatBudget, daysToDeadline, categoryLabel, sourceLabel, tenderSourceUrl } from "@/lib/tenderUtils";
import { ExternalLink, Clock, Building2, MapPin, Loader2 } from "lucide-react";

function MatchScoreBar({ score }: { score: number }) {
  const color = score >= 70 ? "bg-green-500" : score >= 50 ? "bg-amber-500" : "bg-gray-300";
  const label = score >= 70 ? "text-green-700" : score >= 50 ? "text-amber-600" : "text-gray-500";
  return (
    <div className="flex items-center gap-2 mt-2">
      <div className="flex-1 h-1.5 rounded-full bg-muted overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${score}%` }} />
      </div>
      <span className={`text-xs font-medium tabular-nums ${label}`}>{score}% match</span>
    </div>
  );
}

async function trackTender(tenderId: string) {
  try {
    const res = await fetch("http://localhost:8000/api/v1/bids/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tender_id: tenderId }),
    });
    if (res.ok) {
      alert("Added to pipeline!");
    } else {
      const data = await res.json();
      alert(data.detail || "Error adding to pipeline.");
    }
  } catch {
    alert("Could not connect to API.");
  }
}

export default function TenderCard({ tender, isScoring = false }: { tender: Tender; isScoring?: boolean }) {
  const days = daysToDeadline(tender.deadline);

  return (
    <Card className="p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-2">
          {/* Title */}
          <div className="flex items-start gap-2">
            <h3 className="font-medium text-sm leading-snug">{tender.title}</h3>
            <a
              href={tenderSourceUrl(tender)}
              target="_blank"
              rel="noopener noreferrer"
              title={`Find on ${sourceLabel(tender.source)} — tender ID ${tender.tender_id}`}
              className="text-muted-foreground hover:text-foreground mt-0.5 flex-shrink-0"
            >
              <ExternalLink size={13} />
            </a>
          </div>

          {/* Meta */}
          <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
            {tender.authority && (
              <span className="flex items-center gap-1">
                <Building2 size={11} />{tender.authority}
              </span>
            )}
            {tender.location && (
              <span className="flex items-center gap-1">
                <MapPin size={11} />{tender.location}
              </span>
            )}
            {days !== null && (
              <span className="flex items-center gap-1">
                <Clock size={11} />
                {days <= 0 ? "Closed" : days === 1 ? "Closes tomorrow" : `Closes in ${days} days`}
              </span>
            )}
          </div>

          {/* AI summary */}
          {tender.ai_summary && (
            <p className="text-xs text-muted-foreground line-clamp-2">{tender.ai_summary}</p>
          )}

          {/* Match score */}
          {tender.match_score !== null && tender.match_score !== undefined ? (
            <MatchScoreBar score={tender.match_score} />
          ) : isScoring ? (
            <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
              <Loader2 size={12} className="animate-spin" />
              Scoring against your profile…
            </div>
          ) : (
            <div className="mt-2 text-xs text-muted-foreground/60">Not scored yet</div>
          )}
        </div>

        {/* Right column */}
        <div className="flex flex-col items-end gap-2 flex-shrink-0">
          <span className="text-sm font-semibold">{formatBudget(tender)}</span>
          <div className="flex gap-1.5 flex-wrap justify-end">
            <Badge variant="outline" className="text-xs">{sourceLabel(tender.source)}</Badge>
            <Badge variant="secondary" className="text-xs">{categoryLabel(tender.category)}</Badge>
            {days !== null && days <= 7 && days > 0 && (
              <Badge variant="destructive" className="text-xs">Urgent</Badge>
            )}
          </div>
          <button
            onClick={() => trackTender(tender.id)}
            className="text-xs text-muted-foreground hover:text-foreground underline mt-1"
          >
            + Track
          </button>
        </div>
      </div>
    </Card>
  );
}