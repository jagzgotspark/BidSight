from __future__ import annotations

import json
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

    prompt = f"""You are a procurement expert. Score how well this government tender matches a company's profile.

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

Score this match from 0 to 100 where:
- 90-100: Perfect fit, should definitely bid
- 70-89: Strong fit, worth serious consideration
- 50-69: Moderate fit, some gaps but possible
- 30-49: Weak fit, significant gaps
- 0-29: Poor fit, not recommended

Respond ONLY with valid JSON, no markdown, no extra text:
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
        response = await client.post(GROQ_URL, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()

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