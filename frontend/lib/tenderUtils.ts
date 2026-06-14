import { Tender } from "@/types/tender";

export function formatBudget(tender: Tender): string {
  if (tender.budget_max) {
    const cr = tender.budget_max / 1_00_00_000;
    if (cr >= 1) return `₹${cr.toFixed(1)} Cr`;
    const lakh = tender.budget_max / 1_00_000;
    return `₹${lakh.toFixed(0)}L`;
  }
  return tender.budget_raw || "N/A";
}

export function daysToDeadline(deadline: string | null): number | null {
  if (!deadline) return null;
  const diff = new Date(deadline).getTime() - Date.now();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

export function categoryLabel(category: string): string {
  const map: Record<string, string> = {
    it_software: "IT / Software",
    cloud: "Cloud",
    ai_ml: "AI / ML",
    cybersecurity: "Cybersecurity",
    consulting: "Consulting",
    infrastructure: "Infrastructure",
    hardware: "Hardware",
    other: "Other",
  };
  return map[category] || category;
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