export interface CompanyProfile {
  id: string;
  user_id: string;
  company_name: string;
  services: string;       // comma-separated or free text
  tech_stack: string;
  certifications: string;
  team_size: number | null;
  geography: string;
  min_budget: string;
  max_budget: string;
}

export interface CompanyProfileCreate {
  company_name: string;
  services: string;
  tech_stack: string;
  certifications: string;
  team_size: number | null;
  geography: string;
  min_budget: string;
  max_budget: string;
}