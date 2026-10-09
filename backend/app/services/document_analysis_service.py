from __future__ import annotations

import json

from app.services.groq_client import chat_completion

MAX_CHARS = 15000

SYSTEM = (
    "You are an expert analyst of Indian government tenders. You read tender "
    "documents and extract the facts a bidder needs to decide whether to bid. "
    "Be precise and never invent details that aren't in the document."
)


async def analyze_document(text: str, tender_title: str = "") -> dict:
    text = (text or "").strip()
    if not text:
        return {"error": "No readable text found in the document."}

    prompt = f"""Analyze this government tender document and return ONLY a JSON object
(no markdown, no preamble) with EXACTLY these keys:
- "summary": 2-3 sentence plain-language overview
- "scope_of_work": array of short strings
- "eligibility_criteria": array of short strings
- "required_documents": array of short strings
- "emd": earnest money deposit amount, or "Not specified"
- "tender_fee": tender/processing fee, or "Not specified"
- "key_dates": array of objects each with "label" and "date"
- "risks": array of short strings (ambiguities, tight timelines, strict criteria)
- "recommendation": object with "verdict" (one of "go", "caution", "skip") and "reason" (one sentence)

Tender title: {tender_title or "Unknown"}

Document text:
{text[:MAX_CHARS]}
"""

    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 2000,
        "response_format": {"type": "json_object"},
    }

    data = await chat_completion(payload)

    content = data["choices"][0]["message"]["content"].strip()
    # Defensive strip in case the model wraps in code fences
    if content.startswith("```"):
        content = content.split("```")[1].lstrip("json").strip()
    return json.loads(content)