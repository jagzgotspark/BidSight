"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getProfile, saveProfile } from "../../../lib/api";
import type { CompanyProfileCreate } from "../../../types/profile";

const EMPTY_FORM: CompanyProfileCreate = {
  company_name: "",
  services: "",
  tech_stack: "",
  certifications: "",
  team_size: null,
  geography: "",
  min_budget: "",
  max_budget: "",
};

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState<CompanyProfileCreate>(EMPTY_FORM);
  const [savedOnce, setSavedOnce] = useState(false);

  // Pre-fill form when profile loads
  const { isLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: getProfile,
    onSuccess: (data) => {
      if (data) {
        setForm({
          company_name: data.company_name ?? "",
          services: data.services ?? "",
          tech_stack: data.tech_stack ?? "",
          certifications: data.certifications ?? "",
          team_size: data.team_size ?? null,
          geography: data.geography ?? "",
          min_budget: data.min_budget ?? "",
          max_budget: data.max_budget ?? "",
        });
      }
    },
  });

  const mutation = useMutation({
    mutationFn: saveProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile"] });
      setSavedOnce(true);
    },
  });

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: name === "team_size" ? (value === "" ? null : Number(value)) : value,
    }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSavedOnce(false);
    mutation.mutate(form);
  }

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#0a0a0a", color: "#e5e5e5" }}>
      {/* Nav */}
      <header style={{ borderBottom: "1px solid #1f1f1f", padding: "0 2rem" }}>
        <nav style={{ display: "flex", gap: "2rem", alignItems: "center", height: "56px", maxWidth: "1200px", margin: "0 auto" }}>
          <a href="/dashboard" style={{ color: "#a3a3a3", textDecoration: "none", fontSize: "0.875rem" }} className="hover:text-foreground">Tenders</a>
          <a href="/dashboard/pipeline" style={{ color: "#a3a3a3", textDecoration: "none", fontSize: "0.875rem" }} className="hover:text-foreground">Pipeline</a>
          <a href="/dashboard/proposals" style={{ color: "#a3a3a3", textDecoration: "none", fontSize: "0.875rem" }} className="hover:text-foreground">Proposals</a>
          <a href="/dashboard/analytics" style={{ color: "#a3a3a3", textDecoration: "none", fontSize: "0.875rem" }} className="hover:text-foreground">Analytics</a>
          <a href="/dashboard/alerts" style={{ color: "#a3a3a3", textDecoration: "none", fontSize: "0.875rem" }} className="hover:text-foreground">Alerts</a>
          <a href="/dashboard/analysis" style={{ color: "#a3a3a3", textDecoration: "none", fontSize: "0.875rem" }} className="hover:text-foreground">Analyze</a>
          <span style={{ color: "#e5e5e5", fontSize: "0.875rem", fontWeight: 500 }}>Settings</span>
        </nav>
      </header>

      {/* Page body */}
      <main style={{ maxWidth: "680px", margin: "0 auto", padding: "3rem 2rem" }}>
        <div style={{ marginBottom: "2.5rem" }}>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 600, marginBottom: "0.5rem" }}>Company profile</h1>
          <p style={{ color: "#737373", fontSize: "0.875rem", lineHeight: 1.6 }}>
            BidSight scores every tender against this profile. Fill it in accurately — the match quality depends entirely on it.
          </p>
        </div>

        {isLoading ? (
          <p style={{ color: "#737373", fontSize: "0.875rem" }}>Loading your profile…</p>
        ) : (
          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.75rem" }}>

            {/* Company name */}
            <Field label="Company name" hint="The legal or trading name you bid under.">
              <input
                name="company_name"
                value={form.company_name}
                onChange={handleChange}
                placeholder="e.g. TechCorp India Pvt Ltd"
                required
              />
            </Field>

            {/* Services */}
            <Field label="Services / sectors" hint="What your company does. Used to match tender categories.">
              <textarea
                name="services"
                value={form.services}
                onChange={handleChange}
                placeholder="e.g. Cloud infrastructure, software development, AI/ML consulting"
                rows={3}
              />
            </Field>

            {/* Tech stack */}
            <Field label="Tech stack" hint="Technologies you can deliver on.">
              <input
                name="tech_stack"
                value={form.tech_stack}
                onChange={handleChange}
                placeholder="e.g. Python, FastAPI, React, AWS, PostgreSQL"
              />
            </Field>

            {/* Certifications */}
            <Field label="Certifications" hint="ISO, CMMI, empanelments, or other credentials relevant to bids.">
              <input
                name="certifications"
                value={form.certifications}
                onChange={handleChange}
                placeholder="e.g. ISO 27001, CMMI Level 3, NIC empanelled"
              />
            </Field>

            {/* Team size */}
            <Field label="Team size" hint="Approximate number of full-time employees.">
              <input
                name="team_size"
                type="number"
                min={1}
                value={form.team_size ?? ""}
                onChange={handleChange}
                placeholder="e.g. 45"
              />
            </Field>

            {/* Geography */}
            <Field label="Operating geography" hint="States or cities where you can deliver. Affects location-based scoring.">
              <input
                name="geography"
                value={form.geography}
                onChange={handleChange}
                placeholder="e.g. Delhi, Mumbai, Bangalore, Uttar Pradesh"
              />
            </Field>

            {/* Budget range */}
            <div>
              <label style={{ display: "block", fontSize: "0.8125rem", fontWeight: 500, color: "#a3a3a3", marginBottom: "0.375rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Budget range (₹ lakhs)
              </label>
              <p style={{ fontSize: "0.8125rem", color: "#525252", marginBottom: "0.75rem" }}>
                Tenders outside this range score lower for fit.
              </p>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                <div>
                  <label style={{ fontSize: "0.75rem", color: "#525252", display: "block", marginBottom: "0.25rem" }}>Minimum</label>
                  <input
                    name="min_budget"
                    value={form.min_budget}
                    onChange={handleChange}
                    placeholder="e.g. 10"
                    style={{ width: "100%" }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: "0.75rem", color: "#525252", display: "block", marginBottom: "0.25rem" }}>Maximum</label>
                  <input
                    name="max_budget"
                    value={form.max_budget}
                    onChange={handleChange}
                    placeholder="e.g. 500"
                    style={{ width: "100%" }}
                  />
                </div>
              </div>
            </div>

            {/* Save button + feedback */}
            <div style={{ display: "flex", alignItems: "center", gap: "1rem", paddingTop: "0.5rem" }}>
              <button
                type="submit"
                disabled={mutation.isPending}
                style={{
                  backgroundColor: mutation.isPending ? "#1f1f1f" : "#e5e5e5",
                  color: "#0a0a0a",
                  border: "none",
                  borderRadius: "6px",
                  padding: "0.625rem 1.5rem",
                  fontSize: "0.875rem",
                  fontWeight: 600,
                  cursor: mutation.isPending ? "not-allowed" : "pointer",
                  transition: "background-color 0.15s",
                }}
              >
                {mutation.isPending ? "Saving…" : "Save changes"}
              </button>

              {savedOnce && !mutation.isPending && !mutation.isError && (
                <span style={{ fontSize: "0.875rem", color: "#4ade80" }}>✓ Profile saved</span>
              )}

              {mutation.isError && (
                <span style={{ fontSize: "0.875rem", color: "#f87171" }}>
                  Save failed — check the backend is running.
                </span>
              )}
            </div>

          </form>
        )}
      </main>

      <style>{inputStyles}</style>
    </div>
  );
}

// ── Reusable field wrapper ────────────────────────────────────
function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label style={{ display: "block", fontSize: "0.8125rem", fontWeight: 500, color: "#a3a3a3", marginBottom: "0.375rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>
        {label}
      </label>
      {hint && (
        <p style={{ fontSize: "0.8125rem", color: "#525252", marginBottom: "0.75rem" }}>
          {hint}
        </p>
      )}
      {children}
    </div>
  );
}

// ── Shared input/textarea styles injected once ────────────────
const inputStyles = `
  input:not([type="submit"]):not([type="button"]):not([type="number"]),
  input[type="number"],
  textarea {
    width: 100%;
    background: #111111;
    border: 1px solid #2a2a2a;
    border-radius: 6px;
    color: #e5e5e5;
    font-size: 0.875rem;
    padding: 0.625rem 0.75rem;
    outline: none;
    box-sizing: border-box;
    font-family: inherit;
    transition: border-color 0.15s;
  }
  input:not([type="submit"]):not([type="button"]):focus,
  input[type="number"]:focus,
  textarea:focus {
    border-color: #525252;
  }
  input::placeholder,
  textarea::placeholder {
    color: #3a3a3a;
  }
  textarea {
    resize: vertical;
  }
`;