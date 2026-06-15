export interface Alert {
  id: string;
  bid_id: string;
  tender_id: string | null;
  tender_title: string;
  deadline: string | null;
  days_left: number | null;
  threshold: number;
  message: string;
  is_read: boolean;
  created_at: string;
  kind: string;
  score: number | null;
}