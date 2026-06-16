"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";

interface KeyDate { label: string; date: string; }
interface Analysis {
  summary: string;
  scope_of_work: string[];
  eligibility_criteria: string[];
  required_documents: string[];
  emd: string;
  tender_fee: string;
  key_dates: KeyDate[];
  risks: string[];
  recommendation: { verdict: string; reason: string };
}

const VERDICT = {
  go: { bg: "#E1F5EE", fg: "#0F6E56", label: "Go" },
  caution: { bg: "#FAEEDA", fg: "#854F0B", label: "Caution" },
  skip: { bg: "#FCEBEB", fg: "#A32D2D", label: "Skip" },
} as const;

export default function AnalysisPage() {
  const [file, setFile] = useState<File | null>(null);
  const [tenderId, setTenderId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<Analysis | null>(null);

  const { data: tenders } = useQuery({
    queryKey: ["tenders-for-analysis"],
    queryFn: async () => (await api.get("/tenders/?per_page=100")).data.items,
  });

  async function runAnalysis() {
    if (!file) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      if (tenderId) fd.append("tender_id", tenderId);
      const res = await api.post("/analysis/document", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(res.data);
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Analysis failed. Try another PDF.");
    } finally {
      setLoading(false);
    }
  }

  const verdict = result
    ? VERDICT[(result.recommendation?.verdict as keyof typeof VERDICT)] || VERDICT.caution
    : null;

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="max-w-3xl mx-auto px-6 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold">Tender Document Analysis</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Upload a tender PDF — AI extracts scope, eligibility, key dates, and risks
          </p>
        </div>

        <div className="space-y-4 mb-8">
          <div>
            <label className="text-sm font-medium block mb-1">Tender PDF *</label>
            <input
              type="file"
              accept="application/pdf"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="text-sm"
            />
          </div>

          <div>
            <label className="text-sm font-medium block mb-1">
              Attach to tender (optional — saves the analysis to it)
            </label>
            <select
              value={tenderId}
              onChange={(e) => setTenderId(e.target.value)}
              className="w-full border rounded-md px-3 py-2 text-sm"
            >
              <option value="">Don&apos;t attach — analyze only</option>
              {tenders?.map((t: any) => (
                <option key={t.id} value={t.id}>
                  {t.title.slice(0, 80)}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={runAnalysis}
            disabled={!file || loading}
            className="w-full bg-foreground text-background rounded-md py-2.5 text-sm font-medium disabled:opacity-50"
          >
            {loading ? "Analyzing..." : "Analyze Document"}
          </button>

          {error && <p className="text-sm text-red-600">{error}</p>}
        </div>

        {result && (
          <div className="space-y-5">
            {verdict && (
              <div className="flex items-center gap-3">
                <span
                  className="text-sm font-medium px-3 py-1 rounded-full"
                  style={{ background: verdict.bg, color: verdict.fg }}
                >
                  {verdict.label}
                </span>
                <span className="text-sm text-muted-foreground">
                  {result.recommendation?.reason}
                </span>
              </div>
            )}

            <Section title="Summary">
              <p className="text-sm leading-relaxed">{result.summary}</p>
            </Section>

            <ListSection title="Scope of Work" items={result.scope_of_work} />
            <ListSection title="Eligibility Criteria" items={result.eligibility_criteria} />
            <ListSection title="Required Documents" items={result.required_documents} />

            <div className="grid grid-cols-2 gap-4">
              <Section title="EMD"><p className="text-sm">{result.emd}</p></Section>
              <Section title="Tender Fee"><p className="text-sm">{result.tender_fee}</p></Section>
            </div>

            {result.key_dates?.length > 0 && (
              <Section title="Key Dates">
                <div className="space-y-1">
                  {result.key_dates.map((d, i) => (
                    <div key={i} className="flex justify-between text-sm border-b py-1">
                      <span className="text-muted-foreground">{d.label}</span>
                      <span className="font-medium">{d.date}</span>
                    </div>
                  ))}
                </div>
              </Section>
            )}

            <ListSection title="Risks" items={result.risks} danger />
          </div>
        )}
      </main>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h2 className="text-sm font-semibold mb-2">{title}</h2>
      {children}
    </div>
  );
}

function ListSection({ title, items, danger }: { title: string; items: string[]; danger?: boolean }) {
  if (!items || items.length === 0) return null;
  return (
    <Section title={title}>
      <ul className="space-y-1">
        {items.map((it, i) => (
          <li key={i} className={`text-sm flex gap-2 ${danger ? "text-red-700" : ""}`}>
            <span className="text-muted-foreground flex-shrink-0">•</span>
            <span>{it.replace(/^[\s*•\-]+/, "")}</span>
          </li>
        ))}
      </ul>
    </Section>
  );
}

function Header() {
  return (
    <header className="border-b px-6 py-4 flex items-center justify-between">
      <span className="text-xl font-semibold tracking-tight">BidSight</span>
      <nav className="flex gap-3 text-sm text-muted-foreground overflow-x-auto">
        <a href="/dashboard" className="hover:text-foreground">Tenders</a>
        <a href="/dashboard/pipeline" className="hover:text-foreground">Pipeline</a>
        <a href="/dashboard/proposals" className="hover:text-foreground">Proposals</a>
        <a href="/dashboard/analytics" className="hover:text-foreground">Analytics</a>
        <a href="/dashboard/alerts" className="hover:text-foreground">Alerts</a>
        <a href="/dashboard/settings" style={{ color: "#a3a3a3", textDecoration: "none", fontSize: "0.875rem" }} className="hover:text-foreground">Settings</a>
        <span className="text-foreground font-medium">Analyze</span>
      </nav>
    </header>
  );
}