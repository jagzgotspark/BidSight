export interface Bid {
  id: string;
  user_id: string;
  tender_id: string;
  stage: string;
  match_score: number | null;
  notes: string;
  created_at: string;
  updated_at: string;
  tender_title: string | null;
  tender_authority: string | null;
  tender_deadline: string | null;
  tender_budget_raw: string | null;
  tender_source: string | null;
}

export const STAGES = [
  { id: "new", label: "New", color: "bg-gray-100" },
  { id: "interested", label: "Interested", color: "bg-blue-50" },
  { id: "evaluating", label: "Evaluating", color: "bg-purple-50" },
  { id: "drafting", label: "Drafting", color: "bg-amber-50" },
  { id: "submitted", label: "Submitted", color: "bg-orange-50" },
  { id: "won", label: "Won", color: "bg-green-50" },
  { id: "lost", label: "Lost", color: "bg-red-50" },
] as const;