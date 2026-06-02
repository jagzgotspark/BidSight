from __future__ import annotations

"""
Deduplication engine for BidSight.

Strategy
--------
Every scraped Tender has a `fingerprint` (SHA-256 of source+id+title).
Before inserting, we check a fast in-memory set (for the current run)
AND a Redis bloom-filter-style set (across runs).

If Redis is unavailable, we fall back to a simple in-memory set —
safe for single-worker setups, not for distributed workers.
"""

import json
import os
import structlog
from typing import Optional

log = structlog.get_logger()

try:
    import redis

    _redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=int(os.getenv("REDIS_DEDUP_DB", 1)),
        decode_responses=True,
        socket_connect_timeout=2,
    )
    _redis_client.ping()
    _REDIS_AVAILABLE = True
    log.info("dedup_redis_connected")
except Exception as exc:
    _REDIS_AVAILABLE = False
    log.warning("dedup_redis_unavailable", error=str(exc), fallback="in_memory")


_DEDUP_KEY_PREFIX = "bidsight:dedup:"
_DEDUP_TTL_SECONDS = 60 * 60 * 24 * 90  # 90 days


class Deduplicator:
    """
    Tracks seen fingerprints to avoid re-inserting the same tender.

    Usage:
        dedup = Deduplicator()
        for tender in scraped_tenders:
            if dedup.is_new(tender):
                await save(tender)
                dedup.mark_seen(tender)
    """

    def __init__(self) -> None:
        self._local_seen: set[str] = set()

    def is_new(self, fingerprint: str) -> bool:
        """Return True if this fingerprint has not been seen before."""
        if fingerprint in self._local_seen:
            return False

        if _REDIS_AVAILABLE:
            key = _DEDUP_KEY_PREFIX + fingerprint
            return not bool(_redis_client.exists(key))

        return True

    def mark_seen(self, fingerprint: str) -> None:
        """Record that this fingerprint has been processed."""
        self._local_seen.add(fingerprint)

        if _REDIS_AVAILABLE:
            key = _DEDUP_KEY_PREFIX + fingerprint
            _redis_client.set(key, "1", ex=_DEDUP_TTL_SECONDS)

    def bulk_check(self, fingerprints: list[str]) -> set[str]:
        """Return the subset of fingerprints that are NEW (not seen before)."""
        if _REDIS_AVAILABLE:
            pipe = _redis_client.pipeline()
            for fp in fingerprints:
                pipe.exists(_DEDUP_KEY_PREFIX + fp)
            results = pipe.execute()
            new_fps: set[str] = set()
            for fp, exists in zip(fingerprints, results):
                if not exists and fp not in self._local_seen:
                    new_fps.add(fp)
            return new_fps

        return {fp for fp in fingerprints if fp not in self._local_seen}