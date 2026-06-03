import { Tender } from "@/types/tender";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { formatBudget, daysToDeadline, categoryLabel, sourceLabel } from "@/lib/tenderUtils";
import { ExternalLink, Clock, Building2, MapPin } from "lucide-react";

export default function TenderCard({ tender }: { tender: Tender }) {
  const days = daysToDeadline(tender.deadline);

  return (
    <Card className="p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-2">
          <div className="flex items-start gap-2">
            <h3 className="font-medium text-sm leading-snug">{tender.title}</h3>
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