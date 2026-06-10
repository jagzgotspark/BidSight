from __future__ import annotations

import json
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"


async def _call_groq(prompt: str, max_tokens: int = 1000) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.4,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(GROQ_URL, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
    return data["choices"][0]["message"]["content"].strip()


async def generate_proposal(
    tender_title: str,
    tender_authority: str,
    tender_description: str,
    tender_budget: str,
    tender_deadline: str,
    company_name: str,
    company_services: str,
    company_tech_stack: str,
    company_certifications: str,
    company_team_size: str,
    past_projects: str,
    additional_notes: str,
    company_profile_text: str = "",
) -> dict:
    """Generate all proposal sections using Groq."""

    context = f"""
TENDER DETAILS:
Title: {tender_title}
Authority: {tender_authority}
Description: {tender_description}
Budget: {tender_budget}
Deadline: {tender_deadline}

COMPANY DETAILS:
Company: {company_name}
Services: {company_services}
Tech Stack: {company_tech_stack}
Certifications: {company_certifications}
Team Size: {company_team_size}
Past Projects: {past_projects}
Additional Notes: {additional_notes}
{f'Company Profile Document: {company_profile_text[:2000]}' if company_profile_text else ''}
"""

    import asyncio

    async def gen_section(section_name: str, instruction: str, tokens: int = 600) -> str:
        prompt = f"""You are a professional bid writer helping an Indian IT company respond to a government tender.

{context}

Write the {section_name} section for this proposal.
{instruction}

Be specific, professional, and tailored to this exact tender.
Write in formal business English. 3-5 paragraphs. No headers, just the content."""
        try:
            result = await _call_groq(prompt, max_tokens=tokens)
            await asyncio.sleep(1)  # avoid rate limit
            return result
        except Exception as e:
            return f"[Generation failed: {e}]"

    # Generate all sections
    executive_summary = await gen_section(
        "Executive Summary",
        "Summarize why this company is the perfect fit for this tender. Mention key capabilities and commitment to delivery.",
        500
    )

    capability_statement = await gen_section(
        "Company Capability Statement",
        "Detail the company's relevant experience, technical capabilities, certifications, and past government project experience.",
        600
    )

    methodology = await gen_section(
        "Technical Methodology",
        "Describe the step-by-step approach the company will take to deliver this project. Include phases, tools, and quality assurance.",
        700
    )

    team_structure = await gen_section(
        "Team Structure",
        "Describe the proposed team for this project — roles, responsibilities, and how the team size matches project needs.",
        400
    )

    timeline = await gen_section(
        "Project Timeline",
        "Propose a realistic phased timeline for delivering this project. Reference the tender deadline. Include milestones.",
        400
    )

    why_us = await gen_section(
        "Why Choose Us",
        "Make a compelling case for why this company should win the bid. Reference specific tender requirements and company strengths.",
        400
    )

    return {
        "executive_summary": executive_summary,
        "capability_statement": capability_statement,
        "methodology": methodology,
        "team_structure": team_structure,
        "timeline": timeline,
        "why_us": why_us,
    }


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from uploaded PDF."""
    try:
        import io
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text[:5000]  # limit to 5000 chars
        except ImportError:
            pass

        # Fallback: try pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text[:5000]
        except ImportError:
            pass

        return ""
    except Exception:
        return ""