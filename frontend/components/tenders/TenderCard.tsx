import Link from "next/link";
import { Tender } from "@/types/tender";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { formatBudget, daysToDeadline, categoryLabel, sourceLabel } from "@/lib/tenderUtils";
import { ExternalLink, Clock, Building2, MapPin } from "lucide-react";

function MatchScoreBar({ score }: { score: number }) {
  const color = score >= 70 ? "bg-green-500" : score >= 50 ? "bg-amber-400" : "bg-gray-300";
  const label = score >= 70 ? "text-green-700" : score >= 50 ? "text-amber-600" : "text-gray-500";
  return (
    <div className="flex items-center gap-2 mt-2">
      <div className="flex-1 h-1.5 rounded-full bg-gray-100 overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${score}%` }} />
      </div>
      <span className={`text-xs font-medium tabular-nums ${label}`}>{score}% match</span>
    </div>
  );
}

export default function TenderCard({ tender }: { tender: Tender }) {
  const days = daysToDeadline(tender.deadline);

  return (
    <Card className="p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-2">
          <div className="flex items-start gap-2">
            <Link href={`/tenders/${tender.id}`} className="font-medium text-sm leading-snug hover:underline">
              {tender.title}
            </Link>
            {tender.source_url && (
              <a href={tender.source_url} target="_blank" rel="noopener noreferrer"
                className="text-muted-foreground hover:text-foreground mt-0.5 flex-shrink-0">
                <ExternalLink size={13} />
              </a>
            )}
          </div>
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
          {tender.ai_summary && (
            <p className="text-xs text-muted-foreground line-clamp-2">{tender.ai_summary}</p>
          )}
          {tender.match_score !== null && tender.match_score !== undefined && (
            <MatchScoreBar score={tender.match_score} />
          )}
        </div>
        <div className="flex flex-col items-end gap-2 flex-shrink-0">
          <span className="text-sm font-semibold">{formatBudget(tender)}</span>
          <div className="flex gap-1.5 flex-wrap justify-end">
            <Badge variant="outline" className="text-xs">{sourceLabel(tender.source)}</Badge>
            <Badge variant="secondary" className="text-xs">{categoryLabel(tender.category)}</Badge>
            {days !== null && days <= 7 && days > 0 && (
              <Badge variant="destructive" className="text-xs">Urgent</Badge>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}