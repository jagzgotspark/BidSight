from __future__ import annotations
import os
import structlog

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
except Exception:
    _REDIS_AVAILABLE = False

_DEDUP_KEY_PREFIX = "bidsight:dedup:"
_DEDUP_TTL_SECONDS = 60 * 60 * 24 * 90


class Deduplicator:
    def __init__(self) -> None:
        self._local_seen: set[str] = set()

    def is_new(self, fingerprint: str) -> bool:
        if fingerprint in self._local_seen:
            return False
        if _REDIS_AVAILABLE:
            return not bool(_redis_client.exists(_DEDUP_KEY_PREFIX + fingerprint))
        return True

    def mark_seen(self, fingerprint: str) -> None:
        self._local_seen.add(fingerprint)
        if _REDIS_AVAILABLE:
            _redis_client.set(_DEDUP_KEY_PREFIX + fingerprint, "1", ex=_DEDUP_TTL_SECONDS)

    def bulk_check(self, fingerprints: list[str]) -> set[str]:
        if _REDIS_AVAILABLE:
            pipe = _redis_client.pipeline()
            for fp in fingerprints:
                pipe.exists(_DEDUP_KEY_PREFIX + fp)
            results = pipe.execute()
            return {fp for fp, exists in zip(fingerprints, results) if not exists and fp not in self._local_seen}
        return {fp for fp in fingerprints if fp not in self._local_seen}