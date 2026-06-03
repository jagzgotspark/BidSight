export interface Tender {
  id: string;
  tender_id: string;
  source: string;
  title: string;
  description: string;
  authority: string;
  location: string;
  category: string;
  budget_min: number | null;
  budget_max: number | null;
  budget_raw: string;
  published_at: string | null;
  deadline: string | null;
  deadline_raw: string;
  status: string;
  source_url: string;
  ai_summary: string | null;
  ai_risk: string | null;
  ai_eligibility: string | null;
  scraped_at: string | null;
  created_at: string;
}

export interface TenderListResponse {
  items: Tender[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}