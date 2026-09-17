from __future__ import annotations

import json
import asyncio
import os
import httpx
from dotenv import load_dotenv
from app.models.tender import Tender
from app.models.company_profile import CompanyProfile

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"


async def score_tender(tender: Tender, profile: CompanyProfile) -> dict:
    """
    Score a tender against a company profile using Groq (Llama 3).
    Returns: { score: int, reasoning: str, strengths: list, risks: list }
    """

    prompt = f"""You are a procurement expert. Score how well a government tender matches a company's profile.

Score from 0 to 100 where:
- 90-100: Perfect fit, should definitely bid
- 70-89: Strong fit, worth serious consideration
- 50-69: Moderate fit, some gaps but possible
- 30-49: Weak fit, significant gaps
- 0-29: Poor fit, not recommended

Use the FULL range. Do not default to the 20-40 band out of caution — a company
that clearly does this kind of work, in this location, at this budget, should
score 70+ even if the tender description is thin. Judge on the concrete
overlaps below, not on how much detail the tender text happens to contain.

Here are calibration examples showing how to score:

EXAMPLE 1 (strong fit → 88):
TENDER: Title: Development of Municipal Water Billing Software | Authority: Pune Municipal Corporation | Category: IT Services | Location: Maharashtra | Budget: ₹45L | Description: Design and deploy a web-based billing system for water supply.
COMPANY: Services offered: Web application development, government SaaS | Tech stack: React, Node.js, PostgreSQL | Certifications: ISO 27001 | Team size: 25 | Geography focus: Maharashtra, Gujarat | Budget range: ₹20L - ₹80L
{{"score": 88, "reasoning": "Direct match on service type, tech stack, and geography, with budget comfortably inside the company's range.", "strengths": ["Core competency is web app development for government clients", "Operates in Maharashtra"], "risks": ["No stated experience with utility billing specifically"]}}

EXAMPLE 2 (moderate fit → 55):
TENDER: Title: Supply and Installation of CCTV Surveillance System | Authority: Delhi Police | Category: Security Hardware | Location: Delhi | Budget: ₹1.2Cr | Description: Procurement and installation of 500 CCTV cameras with monitoring software.
COMPANY: Services offered: Software development, IT consulting | Tech stack: Python, AWS | Certifications: None listed | Team size: 12 | Geography focus: North India | Budget range: ₹10L - ₹50L
{{"score": 55, "reasoning": "Geography matches and the monitoring-software component overlaps with software capability, but the hardware procurement/installation core is outside expertise, and the budget far exceeds the company's stated range.", "strengths": ["Location match", "Some overlap via monitoring software"], "risks": ["No hardware installation capability", "Budget more than 2x the company's max"]}}

EXAMPLE 3 (poor fit → 12):
TENDER: Title: Construction of Rural Road Network | Authority: PWD Rajasthan | Category: Civil Works | Location: Rajasthan | Budget: ₹8Cr | Description: Construction of 40km of rural roads including drainage.
COMPANY: Services offered: Mobile app development | Tech stack: Flutter, Firebase | Certifications: None | Team size: 8 | Geography focus: South India | Budget range: ₹5L - ₹30L
{{"score": 12, "reasoning": "No overlap in service type (civil construction vs. software), no geographic presence in Rajasthan, and budget is orders of magnitude beyond capacity.", "strengths": [], "risks": ["Entirely different industry", "No geographic presence", "Budget mismatch by 25x+"]}}

Now score this tender:

TENDER:
Title: {tender.title}
Authority: {tender.authority}
Category: {tender.category}
Location: {tender.location}
Budget: {tender.budget_raw or "Not specified"}
Description: {tender.description[:400] if tender.description else "Not provided"}

COMPANY PROFILE:
Company: {profile.company_name}
Services offered: {profile.services}
Tech stack: {profile.tech_stack}
Certifications: {profile.certifications}
Team size: {profile.team_size}
Geography focus: {profile.geography}
Budget range: ₹{profile.min_budget}L - ₹{profile.max_budget}L

Respond ONLY with valid JSON, no markdown, no extra text, matching the exact format of the examples above:
{{"score": <integer 0-100>, "reasoning": "<2 sentences>", "strengths": ["<strength 1>", "<strength 2>"], "risks": ["<risk 1>", "<risk 2>"]}}"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 400,
        "temperature": 0.2,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        for attempt in range(4):
            response = await client.post(GROQ_URL, headers=headers, json=body)
            if response.status_code == 429:
                # Respect Retry-After if present, else exponential backoff
                wait = float(response.headers.get("retry-after", 2 ** attempt))
                await asyncio.sleep(min(wait, 15))
                continue
            response.raise_for_status()
            data = response.json()
            break
        else:
            raise RuntimeError("Groq rate limit: retries exhausted")

    text = data["choices"][0]["message"]["content"].strip()

    # Strip markdown fences if present
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    result = json.loads(text)
    return {
        "score": int(result.get("score", 0)),
        "reasoning": result.get("reasoning", ""),
        "strengths": result.get("strengths", []),
        "risks": result.get("risks", []),
    }


async def score_all_tenders(
    tenders: list[Tender],
    profile: CompanyProfile,
    limit: int = 20,
) -> list[dict]:
    """Score multiple tenders against a profile. Returns sorted by score."""
    results = []
    for tender in tenders[:limit]:
        try:
            score_data = await score_tender(tender, profile)
            results.append({
                "tender_id": tender.id,
                "tender_title": tender.title,
                **score_data,
            })
        except Exception as exc:
            results.append({
                "tender_id": tender.id,
                "tender_title": tender.title,
                "score": 0,
                "reasoning": f"Scoring unavailable: {exc}",
                "strengths": [],
                "risks": [],
            })
        await asyncio.sleep(0.5) 

    return sorted(results, key=lambda x: x["score"], reverse=True)