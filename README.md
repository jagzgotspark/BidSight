# BidSight

**See opportunities before everyone else.**

AI-powered government tender discovery platform for the Indian market. BidSight monitors government procurement portals, scores every tender against your company profile using AI, and manages your entire bid lifecycle — from discovery to proposal.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![Next.js](https://img.shields.io/badge/Next.js-15-black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791)
![License](https://img.shields.io/badge/License-MIT-green)

---

## What it does

- **Scrapes real government tenders** from GeM (Government e-Marketplace) and CPPP (Central Public Procurement Portal) using Playwright with stealth mode
- **Scores every tender 0–100** against your company profile (services, tech stack, certifications, geography) using Groq Llama 3
- **Proactive match alerts** — notifies you when newly scraped tenders cross your score threshold
- **Bid pipeline CRM** — drag-and-drop Kanban board across 7 stages (New → Interested → Evaluating → Drafting → Submitted → Won/Lost)
- **Deadline alerts** — in-app notifications at 30/14/7/3/1-day thresholds, deduped per bid
- **AI proposal generator** — 6-section technical proposal draft from your company profile + optional PDF upload
- **AI document analysis** — upload a tender PDF to extract scope, eligibility, EMD, key dates, and a go/caution/skip recommendation
- **Analytics dashboard** — tender categories, match score distribution, source breakdown, pipeline funnel, scrape history
- **Company profile UI** — configure your profile from the dashboard; no curl required

## Architecture

```mermaid
flowchart LR
    GEM[GeM Portal\ninternal XHR API] -->|Playwright stealth\nintercepts JSON| SCRAPER[Scraper\nPython 3.11]
    CPPP[CPPP Portal\n246 organisations] -->|Playwright stealth\norg drill-down| SCRAPER
    SCRAPER -->|dedup via\nRedis fingerprints| DB[(PostgreSQL)]
    CELERY[Celery Beat\nScheduler] -->|subprocess| SCRAPER
    CELERY -->|in-process| ALERTS[Alert Service]
    DB <--> API[FastAPI\nREST API]
    API <-->|match scoring\nproposals\ndoc analysis| GROQ[Groq\nLlama 3.1]
    FRONTEND[Next.js 15\nDashboard] <-->|React Query| API
```

**Stack:** FastAPI · PostgreSQL · Redis · SQLAlchemy + Alembic · Playwright · Groq (Llama 3.1) · Next.js 15 · React Query · Tailwind + shadcn/ui · Recharts · Celery · Docker Compose

---

## Design decisions and tradeoffs

### 1. Coverage moat vs workflow wedge

The obvious play in this market is coverage — aggregating every government portal into one feed. Competitors like TenderKart win on this axis (100+ portals). BidSight deliberately does not compete there.

Covering 100+ portals is an infrastructure and legal problem: each portal has different session mechanics, CAPTCHA strategies, and terms of service. Maintaining scrapers across all of them is a full-time operation, not a side project. A solo developer cannot match a funded team on this dimension.

BidSight's defensible position is the **bid workspace** — the discover → score → track → draft → alert loop that incumbents treat as an afterthought. Coverage is the moat you build with a team and capital. Workflow quality is the moat you build with product judgment.

### 2. Scraping strategy: XHR interception over HTML parsing

GeM blocks plain HTTP requests with Cloudflare and session-cookie checks. The naive approach — `requests.get()` or even basic Playwright navigation — fails immediately.

The breakthrough was observing that the portal's own frontend calls an internal JSON endpoint (`/all-bids-data`) to populate the tender table. By running a real Chromium browser with `playwright-stealth` and intercepting that XHR response, BidSight gets clean structured JSON directly from the portal's own API — no fragile HTML parsing, no scraping of rendered text. Pagination works by calling the portal's own `loadBids()` JavaScript function.

This is more robust than HTML scraping: the portal's internal API is more stable than its visual layout, and the data arrives pre-structured.

### 3. CPPP: bypassing the CAPTCHA dead-end

CPPP's main search is CAPTCHA-gated — a genuine dead end. The common solution (CAPTCHA-solving services) is expensive, fragile, and legally ambiguous.

The actual solution was finding a different entry point: CPPP's "Tenders by Organisation" page lists ~246 government organisations without any CAPTCHA. Each organisation's drill-down page shows its active tenders — also CAPTCHA-free. A single configurable scraper harvests all 246 organisation links in one browser session and follows each drill-down within the same session (before the session tokens expire). This covers the full portal through a legitimate navigation path that requires no CAPTCHA bypass.

The tradeoff: `sp=` session tokens are bound to the browser session and expire, so all links must be followed within the same run. The scraper is designed around this constraint.

### 4. Dual Python environments

Python 3.13 (the main backend runtime) is incompatible with Playwright's `greenlet` dependency. The options were: downgrade the entire backend to 3.11, or isolate the incompatibility.

BidSight uses two venvs: `.venv` (Python 3.13) for the FastAPI backend, and `.venv-scraper` (Python 3.11) for Playwright scrapers. The Celery worker runs in the backend venv and shells out to the scraper venv via `subprocess` for any task requiring Playwright. The Celery worker itself never imports Playwright.

This adds operational complexity (two venvs to manage) but keeps the backend on a current Python version and makes the dependency boundary explicit. The subprocess interface is a clean seam: the scraper is independently runnable and testable without the backend stack.

### 5. AI scoring: Groq over OpenAI, and known calibration limits

Groq's free tier (Llama 3.1 8b instant) was chosen over OpenAI for cost — this is a portfolio project, not a funded product. The tradeoff is quality: the model clusters scores around 30–40% regardless of actual fit, because it lacks the few-shot calibration examples that would teach it what a 90% match looks like for this domain.

The current scoring is useful for relative ranking (a 70 is a better fit than a 35) but the absolute numbers are not reliable. The right fix is few-shot prompting with labelled examples, or a calibration pass that maps raw scores to outcomes. This is documented as a known limitation rather than papered over with fabricated accuracy stats.

Rate limiting (Groq's 429s) is handled with exponential backoff and `Retry-After` header respect in `match_service.py`. The frontend scores tenders sequentially, not in parallel, to avoid bursting the rate limit.

### 6. No authentication (by choice, for now)

Auth was deferred deliberately. Adding Clerk or any auth system creates a dependency chain: auth → user isolation → plan gating → billing. Building billing without auth is wasted work; building auth without a billing reason is over-engineering for a demo.

Everything is hardcoded to `demo_user`. This is honest about the project's current scope and keeps the codebase focused on the features that demonstrate AI and system design judgment — which is what this portfolio project is actually for.

---

## Key technical highlights

### Scraping a protected government portal

GeM blocks plain HTTP requests with Cloudflare and session-cookie checks. BidSight solves this by:
- Running a real Chromium browser via Playwright with `playwright-stealth` to pass bot detection
- Intercepting the portal's internal `all-bids-data` XHR endpoint instead of parsing HTML
- Paginating by calling the portal's own `loadBids()` JavaScript function
- Deduplicating tenders with Redis-backed SHA-256 fingerprints (`source:tender_id:title`)

### AI match scoring with rate limit handling

Every tender is scored against the user's company profile with structured reasoning:
```json
{
  "score": 83,
  "reasoning": "Strong alignment with cybersecurity services and ISO 27001 certification...",
  "strengths": ["Relevant services", "Certification match"],
  "risks": ["Tight deadline", "Defence sector experience not listed"]
}
```
Scores are persisted on first computation and served from cache on subsequent requests. The scoring queue in the frontend processes tenders sequentially to respect Groq's rate limits, with the backend implementing exponential backoff (4 retries, respects `Retry-After`).

### Scheduled pipeline with subprocess isolation

Celery Beat runs five scheduled tasks:
- GeM scrape every 6 hours
- CPPP full scrape (all 246 orgs) daily at 06:00 IST
- Deadline alert scan daily at 08:00 IST
- Match alert scan every 6 hours

Playwright tasks are executed via `subprocess` into the scraper venv — the Celery worker never imports Playwright directly, keeping the two Python environments cleanly separated.

---

## Project structure

```
BidSight/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + router registration
│   │   ├── config.py            # pydantic-settings configuration
│   │   ├── database.py          # SQLAlchemy session
│   │   ├── models/              # Tender, Bid, CompanyProfile, Proposal, Alert
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── routers/             # tenders, match, bids, proposals, analytics,
│   │   │                        # alerts, analysis
│   │   └── services/            # match_service, proposal_service,
│   │                            # document_analysis_service, alert_service
│   ├── scraper/
│   │   ├── models/tender.py     # Scraper-side tender model + fingerprinting
│   │   ├── scrapers/
│   │   │   ├── gem_stealth.py   # Playwright XHR-intercepting GeM scraper
│   │   │   └── cppp_stealth.py  # Playwright org-drill-down CPPP scraper
│   │   ├── dedup.py             # Redis fingerprint deduplication
│   │   └── tasks/scrape.py      # Celery app + beat schedule
│   ├── alembic/                 # Database migrations
│   ├── seed_data.py             # Sample tender seeder
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Landing page
│   │   ├── dashboard/           # Tender feed
│   │   ├── dashboard/pipeline/  # Kanban CRM
│   │   ├── dashboard/proposals/ # AI proposal generator
│   │   ├── dashboard/analytics/ # Charts dashboard
│   │   ├── dashboard/alerts/    # Deadline + match alerts
│   │   ├── dashboard/analysis/  # AI document analysis
│   │   ├── dashboard/settings/  # Company profile UI
│   │   └── tenders/[id]/        # Tender detail page
│   ├── components/              # TenderFeed, TenderCard, shadcn/ui
│   ├── lib/                     # api.ts (axios), tenderUtils.ts
│   └── types/                   # TypeScript interfaces
└── docker-compose.yml           # PostgreSQL (5433) + Redis (6379)
```

---

## Running locally

### Prerequisites
- Python 3.13 + Python 3.11 (for scraper venv)
- Node.js 18+
- Docker Desktop
- Free [Groq API key](https://console.groq.com)

### 1. Start the database
```bash
docker-compose up -d   # PostgreSQL on 5433, Redis on 6379
```

### 2. Backend
```bash
cd backend
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create .env:
# DATABASE_URL=postgresql://bidsight:bidsight_dev@127.0.0.1:5433/bidsight
# GROQ_API_KEY=gsk_your_key_here

alembic upgrade head
uvicorn app.main:app --reload   # http://localhost:8000
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev   # http://localhost:3000
```

### 4. Get data

**Option A — seed sample tenders:**
```bash
cd backend && python seed_data.py
```

**Option B — scrape real tenders (requires Python 3.11 venv):**
```bash
cd backend
python3.11 -m venv .venv-scraper
source .venv-scraper/bin/activate
pip install playwright playwright-stealth httpx beautifulsoup4 lxml pydantic \
            sqlalchemy psycopg2-binary python-dotenv structlog tenacity \
            python-dateutil pydantic-settings
playwright install chromium

# GeM (real-time XHR interception)
python scraper/scrapers/gem_stealth.py

# CPPP (all 246 organisations, or pass a number to limit)
python scraper/scrapers/cppp_stealth.py 10
```

### 5. Configure your company profile

Visit `http://localhost:3000/dashboard/settings` and fill in the form, or via curl:
```bash
curl -X POST "http://localhost:8000/api/v1/match/profile" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Your Company",
    "services": "software development, cloud migration",
    "tech_stack": "Python, React, AWS",
    "certifications": "ISO 27001",
    "team_size": "45",
    "geography": "Delhi, Mumbai",
    "min_budget": "10",
    "max_budget": "500"
  }'
```

### 6. Optional: run the Celery scheduler
```bash
cd backend && source .venv/bin/activate
pip install "celery[redis]"

# Worker (terminal 1)
celery -A scraper.tasks.scrape worker --loglevel=info --concurrency=1

# Beat scheduler (terminal 2)
celery -A scraper.tasks.scrape beat --loglevel=info
```

---

## API overview

| Endpoint | Description |
|---|---|
| `GET /api/v1/tenders/` | List tenders with filters (source, category, search) |
| `GET /api/v1/tenders/{id}` | Tender detail |
| `POST /api/v1/match/profile` | Create/update company profile |
| `GET /api/v1/match/profile` | Get current company profile |
| `POST /api/v1/match/score/{id}` | Score one tender and persist result |
| `GET/POST/PATCH/DELETE /api/v1/bids/` | Bid pipeline CRUD |
| `POST /api/v1/proposals/generate` | Generate AI proposal (multipart, accepts PDF) |
| `GET /api/v1/analytics/overview` | Dashboard analytics |
| `GET /api/v1/alerts/` | List alerts (deadline + match) |
| `POST /api/v1/alerts/scan` | Trigger deadline alert scan |
| `POST /api/v1/alerts/scan-matches` | Trigger match alert scan |
| `POST /api/v1/analysis/document` | Analyse tender PDF (multipart) |

Interactive docs at `http://localhost:8000/docs`.

---

## Known limitations

- **Match score calibration** — the model clusters scores around 30–40% regardless of fit. Scores are useful for relative ranking but absolute numbers are not reliable. Fix: few-shot prompting with labelled examples.
- **Budget data** — most tenders show N/A. GeM listings don't expose budget in the XHR response; extraction would require drilling into each tender's detail page.
- **No authentication** — everything runs as `demo_user`. Clerk integration is the prerequisite for multi-tenancy and billing.
- **Two venvs** — Python 3.13/3.11 split adds operational overhead. Documented in setup; worth it to keep the backend on a current runtime.

## Roadmap

- [ ] Match score calibration (few-shot prompting)
- [ ] Real authentication (Clerk)
- [ ] Budget extraction from tender detail pages
- [ ] Auto-fetch tender documents for analysis (currently upload-only)
- [ ] Deployment (Fly.io backend + Vercel frontend)
