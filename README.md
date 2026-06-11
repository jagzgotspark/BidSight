# BidSight

**See opportunities before everyone else.**

AI-powered government tender discovery platform for the Indian market. BidSight monitors government procurement portals, scores every tender against your company profile using AI, and helps you manage your entire bid lifecycle — from discovery to proposal.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![Next.js](https://img.shields.io/badge/Next.js-15-black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791)
![License](https://img.shields.io/badge/License-MIT-green)

---

## What it does

- **Scrapes real government tenders** from GeM (Government e-Marketplace) using Playwright with stealth mode — intercepting the portal's internal XHR API to bypass bot protection
- **Scores every tender 0–100** against your company profile (services, tech stack, certifications, geography) using Groq Llama 3
- **Bid pipeline CRM** — drag-and-drop Kanban board to track bids across 7 stages (New → Interested → Evaluating → Drafting → Submitted → Won/Lost)
- **AI proposal generator** — produces a 6-section technical proposal draft (executive summary, capability statement, methodology, team structure, timeline, why us) from your company profile + optional PDF upload
- **Analytics dashboard** — tender categories, match score distribution, source breakdown, pipeline funnel, scrape history

## Architecture
```mermaid
flowchart LR
    GEM[GeM Portal<br/>internal XHR API] -->|Playwright stealth<br/>intercepts JSON| SCRAPER[Scraper<br/>Python 3.11]
    SCRAPER -->|dedup via<br/>Redis fingerprints| DB[(PostgreSQL)]
    DB <--> API[FastAPI<br/>REST API]
    API <-->|match scoring<br/>+ proposals| GROQ[Groq<br/>Llama 3.1]
    FRONTEND[Next.js 15<br/>Dashboard] <-->|React Query| API
```

**Stack:** FastAPI · PostgreSQL · Redis · SQLAlchemy + Alembic · Playwright · Groq (Llama 3.1) · Next.js 15 · React Query · Tailwind + shadcn/ui · Recharts · Docker Compose

## Key technical highlights

### 1. Scraping a protected government portal
GeM blocks plain HTTP requests with Cloudflare and session-cookie checks. BidSight solves this by:
- Running a real Chromium browser via Playwright with `playwright-stealth` to pass bot detection
- Intercepting the portal's internal `all-bids-data` XHR endpoint instead of parsing HTML
- Paginating by calling the portal's own `loadBids()` JavaScript function
- Deduplicating tenders with Redis-backed SHA-256 fingerprints

### 2. AI match scoring
Every tender is scored against the user's company profile with structured reasoning:
```json
{
  "score": 83,
  "reasoning": "Strong alignment with cybersecurity services and ISO 27001 certification...",
  "strengths": ["Relevant services", "Certification match"],
  "risks": ["Tight deadline", "Defence sector experience not listed"]
}
```
Validated results: IT/consulting tenders score 60–85%, physical goods correctly score 20–30%.

### 3. Dual Python environments
Python 3.13 (main backend) is incompatible with Playwright's greenlet dependency, so scraping runs in an isolated Python 3.11 venv — a real-world dependency conflict solved with environment separation.

## Project structure

```
BidSight/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + router registration
│   │   ├── config.py            # pydantic-settings configuration
│   │   ├── database.py          # SQLAlchemy session
│   │   ├── models/              # Tender, Bid, CompanyProfile, Proposal, User
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── routers/             # tenders, match, bids, proposals, analytics
│   │   └── services/            # match_service, proposal_service, tender_service
│   ├── scraper/
│   │   ├── models/tender.py     # Scraper-side tender model + fingerprinting
│   │   ├── scrapers/
│   │   │   ├── gem_stealth.py   # Playwright XHR-intercepting scraper
│   │   │   ├── gem.py           # httpx-based scraper (shared parsers)
│   │   │   └── cppp.py          # CPPP scraper
│   │   └── dedup.py             # Redis fingerprint deduplication
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
│   │   └── tenders/[id]/        # Tender detail page
│   ├── components/              # TenderFeed, TenderCard, shadcn/ui
│   └── types/                   # TypeScript interfaces
└── docker-compose.yml           # PostgreSQL (5433) + Redis (6379)
```

## Running locally

### Prerequisites
- Python 3.13 + Python 3.11 (for scraper)
- Node.js 18+
- Docker Desktop
- Free [Groq API key](https://console.groq.com)

### 1. Database
```bash
docker-compose up -d   # PostgreSQL on 5433, Redis on 6379
```

### 2. Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create .env with:
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
```bash
# Option A — seed sample tenders
python seed_data.py

# Option B — scrape real GeM tenders (needs Python 3.11 venv)
python3.11 -m venv .venv-scraper
source .venv-scraper/bin/activate
pip install playwright playwright-stealth httpx beautifulsoup4 lxml pydantic \
            sqlalchemy psycopg2-binary python-dotenv structlog tenacity \
            python-dateutil pydantic-settings
playwright install chromium
python scraper/scrapers/gem_stealth.py
```

### 5. Set up your company profile
```bash
curl -X POST "http://localhost:8000/api/v1/match/profile" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Your Company",
    "services": "software development, cloud migration",
    "tech_stack": "Python, React, AWS",
    "certifications": "ISO 27001",
    "team_size": "small",
    "geography": "Delhi, Mumbai",
    "min_budget": "10",
    "max_budget": "500"
  }'
```

## API overview

| Endpoint | Description |
|---|---|
| `GET /api/v1/tenders/` | List tenders with filters (source, category, search, budget, deadline) |
| `GET /api/v1/tenders/{id}` | Tender detail |
| `POST /api/v1/match/profile` | Create/update company profile |
| `GET /api/v1/match/score` | AI-score tenders against profile |
| `GET/POST/PATCH/DELETE /api/v1/bids/` | Bid pipeline CRUD |
| `POST /api/v1/proposals/generate` | Generate AI proposal (multipart, accepts PDF) |
| `GET /api/v1/analytics/overview` | Dashboard analytics |

Interactive docs at `http://localhost:8000/docs`.

## Roadmap

- [ ] Deadline email alerts (30/14/7/3-day reminders)
- [ ] Real authentication (Clerk)
- [ ] CPPP real scraping
- [ ] Budget extraction from GeM detail pages
- [ ] Scheduled auto-scraping (APScheduler)
- [ ] Deployment (Render/Fly.io + Vercel)

