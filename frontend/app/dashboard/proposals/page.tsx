"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { TenderListResponse } from "@/types/tender";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";

export default function ProposalsPage() {
  const [selectedTenderId, setSelectedTenderId] = useState<string | null>(null);
  const [pastProjects, setPastProjects] = useState("");
  const [additionalNotes, setAdditionalNotes] = useState("");
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [generating, setGenerating] = useState(false);
  const [proposal, setProposal] = useState<any | null>(null);
  const [error, setError] = useState("");

  const { data: tenders } = useQuery<TenderListResponse>({
    queryKey: ["tenders-for-proposal"],
    queryFn: async () => {
      const res = await api.get("/tenders/", { params: { per_page: 50 } });
      return res.data;
    },
  });

  const handleGenerate = async () => {
    if (!selectedTenderId) {
      setError("Please select a tender first.");
      return;
    }
    setError("");
    setGenerating(true);
    setProposal(null);

    try {
      const formData = new FormData();
      formData.append("tender_id", selectedTenderId);
      formData.append("past_projects", pastProjects);
      formData.append("additional_notes", additionalNotes);
      if (pdfFile) {
        formData.append("company_profile_pdf", pdfFile);
      }

      const res = await fetch("http://localhost:8000/api/v1/proposals/generate", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Generation failed");
      }

      const data = await res.json();
      setProposal(data);
    } catch (e: any) {
      setError(e.message || "Something went wrong.");
    } finally {
      setGenerating(false);
    }
  };

  const handleCopy = () => {
    if (!proposal) return;
    const text = `
EXECUTIVE SUMMARY
${proposal.executive_summary}

COMPANY CAPABILITY STATEMENT
${proposal.capability_statement}

TECHNICAL METHODOLOGY
${proposal.methodology}

TEAM STRUCTURE
${proposal.team_structure}

PROJECT TIMELINE
${proposal.timeline}

WHY CHOOSE US
${proposal.why_us}
    `.trim();
    navigator.clipboard.writeText(text);
    alert("Proposal copied to clipboard!");
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b px-6 py-4 flex items-center justify-between">
        <span className="text-xl font-semibold tracking-tight">BidSight</span>
        <nav className="flex gap-4 text-sm text-muted-foreground">
          <a href="/dashboard" className="hover:text-foreground">Tenders</a>
          <a href="/dashboard/pipeline" className="hover:text-foreground">Pipeline</a>
          <span className="text-foreground font-medium">Proposals</span>
        </nav>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold">Proposal Assistant</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Generate a full technical proposal draft in minutes
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left — inputs */}
          <div className="space-y-4">
            {/* Tender selector */}
            <div>
              <label className="text-sm font-medium mb-1.5 block">
                Select Tender *
              </label>
              <select
                className="w-full border rounded-md px-3 py-2 text-sm bg-background"
                value={selectedTenderId || ""}
                onChange={(e) => setSelectedTenderId(e.target.value || null)}
              >
                <option value="">Choose a tender...</option>
                {tenders?.items.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.title.slice(0, 60)}{t.title.length > 60 ? "..." : ""}
                  </option>
                ))}
              </select>
            </div>

            {/* Past projects */}
            <div>
              <label className="text-sm font-medium mb-1.5 block">
                Past Relevant Projects
              </label>
              <textarea
                className="w-full border rounded-md px-3 py-2 text-sm bg-background min-h-28 resize-none"
                placeholder="e.g. Built cloud migration system for BHEL (₹2Cr, 2023), Developed ERP for state govt of MP..."
                value={pastProjects}
                onChange={(e) => setPastProjects(e.target.value)}
              />
            </div>

            {/* Additional notes */}
            <div>
              <label className="text-sm font-medium mb-1.5 block">
                Additional Notes
              </label>
              <textarea
                className="w-full border rounded-md px-3 py-2 text-sm bg-background min-h-20 resize-none"
                placeholder="Any specific points to highlight, pricing strategy, unique differentiators..."
                value={additionalNotes}
                onChange={(e) => setAdditionalNotes(e.target.value)}
              />
            </div>

            {/* PDF upload */}
            <div>
              <label className="text-sm font-medium mb-1.5 block">
                Upload Company Profile PDF
                <span className="text-muted-foreground font-normal ml-1">(optional)</span>
              </label>
              <input
                type="file"
                accept=".pdf"
                className="w-full text-sm text-muted-foreground file:mr-3 file:py-1.5 file:px-3 file:rounded file:border file:border-input file:text-xs file:font-medium file:bg-background hover:file:bg-muted cursor-pointer"
                onChange={(e) => setPdfFile(e.target.files?.[0] || null)}
              />
              {pdfFile && (
                <p className="text-xs text-muted-foreground mt-1">
                  ✓ {pdfFile.name}
                </p>
              )}
            </div>

            {error && (
              <p className="text-sm text-destructive">{error}</p>
            )}

            <button
              onClick={handleGenerate}
              disabled={generating}
              className="w-full bg-foreground text-background py-2.5 rounded-md text-sm font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
            >
              {generating ? "Generating proposal... (~30 seconds)" : "Generate Proposal"}
            </button>

            {generating && (
              <p className="text-xs text-muted-foreground text-center">
                AI is writing 6 sections. This takes about 30 seconds...
              </p>
            )}
          </div>

          {/* Right — output */}
          <div>
            {!proposal && !generating && (
              <div className="border-2 border-dashed rounded-lg h-full min-h-96 flex items-center justify-center">
                <p className="text-sm text-muted-foreground text-center px-8">
                  Fill in the details and click Generate Proposal.<br />
                  Your draft will appear here.
                </p>
              </div>
            )}

            {generating && (
              <div className="border-2 border-dashed rounded-lg h-full min-h-96 flex items-center justify-center">
                <div className="text-center space-y-3">
                  <div className="animate-spin w-8 h-8 border-2 border-foreground border-t-transparent rounded-full mx-auto" />
                  <p className="text-sm text-muted-foreground">Writing your proposal...</p>
                </div>
              </div>
            )}

            {proposal && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="font-medium text-sm">{proposal.tender_title?.slice(0, 50)}</h2>
                    <p className="text-xs text-muted-foreground">{proposal.tender_authority}</p>
                  </div>
                  <button
                    onClick={handleCopy}
                    className="text-xs border rounded px-3 py-1.5 hover:bg-muted transition-colors"
                  >
                    Copy all
                  </button>
                </div>

                {[
                  { key: "executive_summary", label: "Executive Summary" },
                  { key: "capability_statement", label: "Capability Statement" },
                  { key: "methodology", label: "Methodology" },
                  { key: "team_structure", label: "Team Structure" },
                  { key: "timeline", label: "Timeline" },
                  { key: "why_us", label: "Why Choose Us" },
                ].map((section) => (
                  <Card key={section.key} className="p-4">
                    <h3 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">
                      {section.label}
                    </h3>
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">
                      {proposal[section.key]}
                    </p>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}