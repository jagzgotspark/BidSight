"use client";
import Link from "next/link";

export default function Home() {
  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

        * { box-sizing: border-box; margin: 0; padding: 0; }
        :root {
          --bs-ink: #0D1117;
          --bs-ink2: #3A4250;
          --bs-ink3: #7A8394;
          --bs-surface: #F5F4F0;
          --bs-white: #FFFFFF;
          --bs-accent: #1D9E75;
          --bs-accent-light: #E1F5EE;
          --bs-accent-mid: #0F6E56;
          --bs-amber: #BA7517;
          --bs-amber-light: #FAEEDA;
          --bs-line: rgba(13,17,23,0.1);
        }
        .bs { font-family: 'DM Sans', sans-serif; color: var(--bs-ink); background: var(--bs-white); min-height: 100vh; }
        .bs-nav { display: flex; align-items: center; justify-content: space-between; padding: 1.25rem 2rem; border-bottom: 0.5px solid var(--bs-line); }
        .bs-logo { display: flex; align-items: center; gap: 8px; }
        .bs-logo-mark { width: 28px; height: 28px; background: var(--bs-ink); border-radius: 6px; display: flex; align-items: center; justify-content: center; }
        .bs-logo-name { font-size: 16px; font-weight: 500; letter-spacing: -0.3px; }
        .bs-nav-links { display: flex; gap: 1.5rem; font-size: 13px; color: var(--bs-ink2); }
        .bs-nav-cta { font-size: 13px; font-weight: 500; background: var(--bs-ink); color: #fff; padding: 6px 16px; border-radius: 6px; border: none; cursor: pointer; text-decoration: none; }
        .bs-ticker { background: var(--bs-surface); padding: 0.75rem 2rem; border-bottom: 0.5px solid var(--bs-line); overflow: hidden; }
        .bs-ticker-inner { display: flex; gap: 2rem; font-size: 12px; color: var(--bs-ink2); white-space: nowrap; animation: ticker 18s linear infinite; }
        .bs-ticker-item { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
        .bs-ticker-badge { background: var(--bs-accent-light); color: var(--bs-accent-mid); padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 500; }
        .bs-ticker-badge.amber { background: var(--bs-amber-light); color: var(--bs-amber); }
        @keyframes ticker { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
        .bs-hero { padding: 4rem 2rem 3rem; border-bottom: 0.5px solid var(--bs-line); max-width: 900px; margin: 0 auto; }
        .bs-eyebrow { display: inline-flex; align-items: center; gap: 6px; background: var(--bs-accent-light); color: var(--bs-accent-mid); font-size: 12px; font-weight: 500; padding: 4px 12px; border-radius: 20px; margin-bottom: 1.5rem; }
        .bs-eyebrow-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--bs-accent); }
        .bs-hero h1 { font-family: 'DM Serif Display', serif; font-size: 52px; line-height: 1.05; letter-spacing: -1px; margin-bottom: 1.25rem; max-width: 560px; }
        .bs-hero h1 em { font-style: italic; color: var(--bs-accent); }
        .bs-hero-sub { font-size: 16px; color: var(--bs-ink2); line-height: 1.65; max-width: 480px; margin-bottom: 2rem; font-weight: 300; }
        .bs-hero-ctas { display: flex; gap: 12px; align-items: center; }
        .bs-btn-primary { background: var(--bs-ink); color: #fff; font-size: 14px; font-weight: 500; padding: 10px 22px; border-radius: 7px; border: none; cursor: pointer; font-family: inherit; text-decoration: none; }
        .bs-btn-secondary { background: transparent; color: var(--bs-ink); font-size: 14px; padding: 10px 22px; border-radius: 7px; border: 0.5px solid var(--bs-ink); cursor: pointer; font-family: inherit; text-decoration: none; }
        .bs-hero-proof { margin-top: 2.5rem; display: flex; align-items: center; gap: 1.5rem; padding-top: 2rem; border-top: 0.5px solid var(--bs-line); }
        .bs-proof-num { font-family: 'DM Serif Display', serif; font-size: 28px; }
        .bs-proof-label { font-size: 12px; color: var(--bs-ink3); margin-top: 2px; }
        .bs-proof-divider { width: 0.5px; height: 36px; background: var(--bs-line); }
        .bs-section { padding: 2.5rem 2rem; border-bottom: 0.5px solid var(--bs-line); max-width: 900px; margin: 0 auto; }
        .bs-section-label { font-size: 11px; font-weight: 500; letter-spacing: 1.5px; text-transform: uppercase; color: var(--bs-ink3); margin-bottom: 1rem; }
        .bs-section h2 { font-family: 'DM Serif Display', serif; font-size: 32px; letter-spacing: -0.5px; margin-bottom: 0.5rem; line-height: 1.15; }
        .bs-section-sub { font-size: 14px; color: var(--bs-ink2); font-weight: 300; margin-bottom: 2rem; max-width: 440px; line-height: 1.6; }
        .bs-features-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1px; background: var(--bs-line); border: 0.5px solid var(--bs-line); border-radius: 12px; overflow: hidden; }
        .bs-feat { background: var(--bs-white); padding: 1.25rem; display: flex; flex-direction: column; gap: 8px; }
        .bs-feat-icon { width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-bottom: 4px; font-size: 18px; }
        .bs-feat-icon.green { background: var(--bs-accent-light); color: var(--bs-accent); }
        .bs-feat-icon.amber { background: var(--bs-amber-light); color: var(--bs-amber); }
        .bs-feat-icon.gray { background: var(--bs-surface); color: var(--bs-ink2); }
        .bs-feat-title { font-size: 14px; font-weight: 500; }
        .bs-feat-desc { font-size: 12px; color: var(--bs-ink2); line-height: 1.55; font-weight: 300; }
        .bs-match-demo { border: 0.5px solid var(--bs-line); border-radius: 12px; overflow: hidden; margin-top: 1.5rem; }
        .bs-match-header { background: var(--bs-surface); padding: 0.75rem 1.25rem; font-size: 12px; font-weight: 500; color: var(--bs-ink2); display: flex; justify-content: space-between; border-bottom: 0.5px solid var(--bs-line); }
        .bs-match-row { padding: 1rem 1.25rem; border-bottom: 0.5px solid var(--bs-line); display: flex; align-items: center; gap: 1rem; }
        .bs-match-row:last-child { border-bottom: none; }
        .bs-match-info { flex: 1; }
        .bs-match-title { font-size: 13px; font-weight: 500; margin-bottom: 4px; }
        .bs-match-meta { display: flex; gap: 8px; }
        .bs-match-pill { background: var(--bs-surface); padding: 2px 8px; border-radius: 10px; font-size: 10px; color: var(--bs-ink2); }
        .bs-score { font-family: 'DM Serif Display', serif; font-size: 20px; color: var(--bs-accent); }
        .bs-score-bar-bg { width: 80px; height: 4px; background: var(--bs-accent-light); border-radius: 2px; margin-top: 4px; }
        .bs-score-bar { height: 4px; background: var(--bs-accent); border-radius: 2px; }
        .bs-score-label { font-size: 10px; color: var(--bs-ink3); margin-top: 2px; }
        .bs-pipeline { display: flex; margin-top: 1.5rem; border-radius: 10px; border: 0.5px solid var(--bs-line); overflow: hidden; }
        .bs-stage { flex: 1; padding: 0.75rem 0.5rem; background: var(--bs-white); border-right: 0.5px solid var(--bs-line); text-align: center; }
        .bs-stage:last-child { border-right: none; }
        .bs-stage-name { font-size: 10px; color: var(--bs-ink3); font-weight: 500; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 6px; }
        .bs-stage-count { font-family: 'DM Serif Display', serif; font-size: 22px; }
        .bs-stage.active { background: var(--bs-surface); }
        .bs-stage.active .bs-stage-count { color: var(--bs-accent); }
        .bs-pricing-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-top: 1.5rem; }
        .bs-plan { border: 0.5px solid var(--bs-line); border-radius: 12px; padding: 1.25rem; position: relative; }
        .bs-plan.featured { border: 1.5px solid var(--bs-accent); }
        .bs-plan-badge { position: absolute; top: -10px; left: 50%; transform: translateX(-50%); background: var(--bs-accent); color: #fff; font-size: 10px; font-weight: 500; padding: 3px 12px; border-radius: 10px; white-space: nowrap; }
        .bs-plan-name { font-size: 13px; font-weight: 500; margin-bottom: 4px; }
        .bs-plan-price { font-family: 'DM Serif Display', serif; font-size: 28px; margin-bottom: 2px; }
        .bs-plan-price span { font-size: 12px; font-family: 'DM Sans', sans-serif; font-weight: 300; color: var(--bs-ink3); }
        .bs-plan-desc { font-size: 11px; color: var(--bs-ink3); margin-bottom: 1rem; font-weight: 300; }
        .bs-plan-features { list-style: none; display: flex; flex-direction: column; gap: 6px; }
        .bs-plan-features li { font-size: 11px; color: var(--bs-ink2); display: flex; align-items: flex-start; gap: 6px; line-height: 1.45; }
        .bs-plan-features li::before { content: "✓"; color: var(--bs-accent); flex-shrink: 0; }
        .bs-plan-btn { width: 100%; margin-top: 1.25rem; padding: 8px; border-radius: 7px; font-size: 12px; font-weight: 500; font-family: inherit; cursor: pointer; border: 0.5px solid var(--bs-ink); background: transparent; color: var(--bs-ink); }
        .bs-plan.featured .bs-plan-btn { background: var(--bs-ink); color: #fff; }
        .bs-footer { padding: 1.5rem 2rem; display: flex; align-items: center; justify-content: space-between; font-size: 12px; color: var(--bs-ink3); max-width: 900px; margin: 0 auto; }
      `}</style>

      <div className="bs">
        {/* Nav */}
        <nav className="bs-nav">
          <div className="bs-logo">
            <div className="bs-logo-mark">
              <svg viewBox="0 0 16 16" width="16" height="16" fill="none">
                <circle cx="7" cy="7" r="4.5" stroke="white" strokeWidth="1.5"/>
                <path d="M10.5 10.5L13.5 13.5" stroke="white" strokeWidth="1.5" strokeLinecap="round"/>
                <circle cx="7" cy="7" r="1.5" fill="white"/>
              </svg>
            </div>
            <span className="bs-logo-name">BidSight</span>
          </div>
          <div className="bs-nav-links">
            <span>Features</span>
            <span>Pricing</span>
            <span>About</span>
          </div>
          <Link href="/dashboard" className="bs-nav-cta">Get early access</Link>
        </nav>

        {/* Ticker */}
        <div className="bs-ticker">
          <div className="bs-ticker-inner">
            {[...Array(2)].map((_, i) => (
              <span key={i} style={{display:"contents"}}>
                <div className="bs-ticker-item"><span className="bs-ticker-badge">NEW</span> Cloud Infrastructure Tender — ₹2.4 Cr · GeM Portal · Closes in 6 days</div>
                <div className="bs-ticker-item"><span className="bs-ticker-badge amber">CLOSING</span> AI/ML Consulting RFP — ₹85 L · NIC · 2 days left</div>
                <div className="bs-ticker-item"><span className="bs-ticker-badge">NEW</span> Cybersecurity Audit — ₹1.1 Cr · DRDO · 14 days</div>
                <div className="bs-ticker-item"><span className="bs-ticker-badge">NEW</span> ERP Implementation — ₹3.2 Cr · CPPP · 21 days</div>
                <div className="bs-ticker-item"><span className="bs-ticker-badge amber">CLOSING</span> Mobile App Dev — ₹40 L · State Portal · 1 day left</div>
              </span>
            ))}
          </div>
        </div>

        {/* Hero */}
        <div className="bs-hero">
          <div className="bs-eyebrow"><div className="bs-eyebrow-dot"></div>AI-Powered Tender Intelligence</div>
          <h1>See opportunities<br/><em>before everyone else.</em></h1>
          <p className="bs-hero-sub">BidSight monitors GeM, CPPP, and 40+ procurement portals daily. AI scores every tender against your profile and drafts your proposal — so you bid smarter, not harder.</p>
          <div className="bs-hero-ctas">
            <Link href="/dashboard" className="bs-btn-primary">Start free trial</Link>
            <a href="#features" className="bs-btn-secondary">Watch 2-min demo</a>
          </div>
          <div className="bs-hero-proof">
            <div><div className="bs-proof-num">40+</div><div className="bs-proof-label">Portals monitored daily</div></div>
            <div className="bs-proof-divider"></div>
            <div><div className="bs-proof-num">92%</div><div className="bs-proof-label">Match accuracy</div></div>
            <div className="bs-proof-divider"></div>
            <div><div className="bs-proof-num">4 hrs</div><div className="bs-proof-label">Saved per tender review</div></div>
            <div className="bs-proof-divider"></div>
            <div><div className="bs-proof-num">Minutes</div><div className="bs-proof-label">To first proposal draft</div></div>
          </div>
        </div>

        {/* Features */}
        <div className="bs-section" id="features">
          <div className="bs-section-label">Platform</div>
          <h2>Everything your bid team needs</h2>
          <p className="bs-section-sub">From discovery to submission — one platform replaces your spreadsheets, portal tabs, and email reminders.</p>
          <div className="bs-features-grid">
            {[
              { icon: "🔍", cls: "green", title: "Opportunity discovery", desc: "Crawls GeM, CPPP, state portals, and PSU sites. New tenders appear in your feed within hours of posting." },
              { icon: "🧠", cls: "green", title: "AI match scoring", desc: "Every tender gets a 0–100 match score against your services, certifications, geography, and budget range." },
              { icon: "📄", cls: "amber", title: "Proposal assistant", desc: "Upload your company profile and past proposals. Generate a full technical proposal draft in minutes." },
              { icon: "🏆", cls: "amber", title: "Competitor intelligence", desc: "See who's winning similar tenders, their bid patterns, and typical contract sizes." },
              { icon: "🔔", cls: "gray", title: "Deadline monitoring", desc: "30-, 14-, 7-, 3-day and 24-hour reminders via email, Slack, or Teams. Never miss a closing date." },
              { icon: "📊", cls: "gray", title: "Bid analytics", desc: "Track win rate, submission rate, and revenue pipeline. Identify which categories you win most." },
            ].map((f) => (
              <div key={f.title} className="bs-feat">
                <div className={`bs-feat-icon ${f.cls}`}>{f.icon}</div>
                <div className="bs-feat-title">{f.title}</div>
                <div className="bs-feat-desc">{f.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Match demo */}
        <div className="bs-section">
          <div className="bs-section-label">Smart matching</div>
          <h2>Your feed, scored for you</h2>
          <p className="bs-section-sub">No more scanning irrelevant tenders. BidSight ranks every opportunity by how well it fits your firm.</p>
          <div className="bs-match-demo">
            <div className="bs-match-header"><span>Recommended opportunities</span><span style={{fontWeight:400,color:"var(--bs-ink3)"}}>Sorted by match · Today</span></div>
            {[
              { title: "AI-Powered Analytics Platform — Ministry of Finance", budget: "₹1.8 Cr", src: "GeM", days: "12 days", score: 96 },
              { title: "Cloud Migration Services — IRCTC", budget: "₹3.4 Cr", src: "CPPP", days: "20 days", score: 87 },
              { title: "Cybersecurity Audit & Compliance — DRDO", budget: "₹95 L", src: "Direct", days: "7 days", score: 74 },
            ].map((r) => (
              <div key={r.title} className="bs-match-row">
                <div className="bs-match-info">
                  <div className="bs-match-title">{r.title}</div>
                  <div className="bs-match-meta">
                    <span className="bs-match-pill">{r.budget}</span>
                    <span className="bs-match-pill">{r.src}</span>
                    <span className="bs-match-pill">Closes in {r.days}</span>
                  </div>
                </div>
                <div style={{display:"flex",flexDirection:"column",alignItems:"flex-end",gap:4}}>
                  <div className="bs-score">{r.score}%</div>
                  <div className="bs-score-bar-bg"><div className="bs-score-bar" style={{width:`${r.score}%`}}></div></div>
                  <div className="bs-score-label">Match score</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Pipeline */}
        <div className="bs-section">
          <div className="bs-section-label">Bid CRM</div>
          <h2>Your pipeline, at a glance</h2>
          <p className="bs-section-sub">Track every bid from discovery to award in one place.</p>
          <div className="bs-pipeline">
            {[
              { name: "New", count: 24, active: false },
              { name: "Evaluating", count: 9, active: false },
              { name: "Drafting", count: 3, active: true },
              { name: "Submitted", count: 11, active: false },
              { name: "Won", count: 5, active: false },
              { name: "Lost", count: 6, active: false },
            ].map((s) => (
              <div key={s.name} className={`bs-stage${s.active ? " active" : ""}`}>
                <div className="bs-stage-name">{s.name}</div>
                <div className="bs-stage-count">{s.count}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Pricing */}
        <div className="bs-section">
          <div className="bs-section-label">Pricing</div>
          <h2>Simple, transparent plans</h2>
          <p className="bs-section-sub">Start free for 14 days. No credit card required.</p>
          <div className="bs-pricing-grid">
            <div className="bs-plan">
              <div className="bs-plan-name">Starter</div>
              <div className="bs-plan-price">₹999<span>/mo</span></div>
              <div className="bs-plan-desc">For solo consultants</div>
              <ul className="bs-plan-features">
                <li>Opportunity feed</li><li>AI summaries</li><li>Basic tracking</li><li>Email alerts</li>
              </ul>
              <button className="bs-plan-btn">Get started</button>
            </div>
            <div className="bs-plan featured">
              <div className="bs-plan-badge">Most popular</div>
              <div className="bs-plan-name">Professional</div>
              <div className="bs-plan-price">₹2,999<span>/mo</span></div>
              <div className="bs-plan-desc">For growing agencies</div>
              <ul className="bs-plan-features">
                <li>Smart match scoring</li><li>Proposal generation</li><li>Analytics dashboard</li><li>Slack & Teams alerts</li><li>Competitor intelligence</li>
              </ul>
              <button className="bs-plan-btn">Start free trial</button>
            </div>
            <div className="bs-plan">
              <div className="bs-plan-name">Enterprise</div>
              <div className="bs-plan-price" style={{fontSize:22}}>Custom</div>
              <div className="bs-plan-desc">For large teams</div>
              <ul className="bs-plan-features">
                <li>Team collaboration</li><li>API access</li><li>Custom integrations</li><li>Dedicated support</li>
              </ul>
              <button className="bs-plan-btn">Contact sales</button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bs-footer">
          <span>© 2026 BidSight · See opportunities before everyone else.</span>
          <span style={{display:"flex",gap:"1rem"}}>
            <span>Privacy</span><span>Terms</span><span>Contact</span>
          </span>
        </div>
      </div>
    </>
  );
}