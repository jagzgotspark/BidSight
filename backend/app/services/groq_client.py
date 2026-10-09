from __future__ import annotations

import asyncio
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")


class GroqRateLimited(RuntimeError):
    """Groq kept returning 429 after all retries."""


async def chat_completion(
    body: dict,
    timeout: float = 60,
    max_wait: float = 60,
) -> dict:
    """
    POST a chat completion to Groq, retrying on 429.

    The free tier caps tokens per minute, so a burst of calls (proposal
    sections, background scoring) hits 429 until the window resets. Honour
    Retry-After, and give up once `max_wait` seconds have been spent waiting.
    """
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {"model": GROQ_MODEL, **body}
    waited = 0.0
    attempt = 0

    async with httpx.AsyncClient(timeout=timeout) as client:
        while True:
            response = await client.post(GROQ_URL, headers=headers, json=body)
            if response.status_code != 429:
                response.raise_for_status()
                return response.json()

            wait = float(response.headers.get("retry-after", 2 ** attempt))
            wait = min(wait, 30)
            if waited + wait > max_wait:
                raise GroqRateLimited("Groq rate limit: retries exhausted")
            await asyncio.sleep(wait)
            waited += wait
            attempt += 1
