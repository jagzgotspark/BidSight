import { Tender } from "@/types/tender";

export function hasBudget(tender: Tender): boolean {
  return Boolean(tender.budget_max) || Boolean(tender.budget_raw && tender.budget_raw !== "NA");
}

export function formatBudget(tender: Tender): string {
  if (tender.budget_max) {
    const cr = tender.budget_max / 1_00_00_000;
    if (cr >= 1) return `₹${cr.toFixed(1)} Cr`;
    const lakh = tender.budget_max / 1_00_000;
    return `₹${lakh.toFixed(0)}L`;
  }
  // Portals only publish a value when the buyer discloses it; scrapers store "NA" otherwise
  if (!tender.budget_raw || tender.budget_raw === "NA") return "Value not disclosed";
  return tender.budget_raw;
}

export function daysToDeadline(deadline: string | null): number | null {
  if (!deadline) return null;
  const diff = new Date(deadline).getTime() - Date.now();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

// Must match TenderCategory in backend/scraper/models/tender.py
export const CATEGORIES: { value: string; label: string }[] = [
  { value: "construction", label: "Construction & Civil Works" },
  { value: "roads_highways", label: "Roads & Highways" },
  { value: "electrical", label: "Electrical & HVAC" },
  { value: "water_sanitation", label: "Water & Sanitation" },
  { value: "maintenance_amc", label: "Maintenance / AMC" },
  { value: "medical", label: "Medical" },
  { value: "lab_scientific", label: "Lab & Scientific" },
  { value: "it_software", label: "IT / Software" },
  { value: "cloud", label: "Cloud" },
  { value: "ai_ml", label: "AI / ML" },
  { value: "cybersecurity", label: "Cybersecurity" },
  { value: "infrastructure", label: "Network & Telecom" },
  { value: "hardware", label: "IT Hardware" },
  { value: "consulting", label: "Consulting & Surveys" },
  { value: "manpower", label: "Manpower & Outsourcing" },
  { value: "security_services", label: "Security & Surveillance" },
  { value: "horticulture", label: "Horticulture & Agriculture" },
  { value: "industrial_parts", label: "Industrial Parts" },
  { value: "equipment_machinery", label: "Equipment & Machinery" },
  { value: "chemicals_gases", label: "Chemicals, Fuels & Gases" },
  { value: "vehicles", label: "Vehicles & Transport" },
  { value: "food_catering", label: "Food & Catering" },
  { value: "furniture", label: "Furniture" },
  { value: "textiles_apparel", label: "Textiles & Apparel" },
  { value: "office_supplies", label: "Printing & Stationery" },
  { value: "library_publishing", label: "Library & Publishing" },
  { value: "sports", label: "Sports" },
  { value: "defense_marine", label: "Defence & Marine" },
  { value: "other", label: "Other" },
];

const CATEGORY_LABELS: Record<string, string> = Object.fromEntries(
  CATEGORIES.map((c) => [c.value, c.label])
);

export function categoryLabel(category: string): string {
  return CATEGORY_LABELS[category] || category;
}

export function sourceLabel(source: string): string {
  return source === "gem" ? "GeM" : "CPPP";
}

export function tenderSourceUrl(tender: Tender): string {
  // Portal deep-links are session-bound and expire, so we send users to the
  // portal's stable search page where they can look the tender up by ID.
  if (tender.source === "cppp") {
    return "https://eprocure.gov.in/eprocure/app?page=FrontEndTendersByOrganisation&service=page";
  }
  if (tender.source === "gem") {
    return "https://bidplus.gem.gov.in/all-bids";
  }
  return tender.source_url || "https://eprocure.gov.in";
}