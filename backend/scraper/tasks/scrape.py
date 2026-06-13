from __future__ import annotations

"""
Celery tasks for BidSight's scraping pipeline.

The Playwright stealth scrapers run in a separate Python 3.11 venv
(.venv-scraper) because Playwright won't build on 3.13. Each task shells out
to that interpreter rather than importing Playwright into the worker. The
scrapers handle their own dedup + DB save; these tasks orchestrate, time-box,
and log.

Beat schedule (Asia/Kolkata):
  - GeM:  every 6 hours
  - CPPP: daily at 06:00 IST (all organisations)
"""

import os
import subprocess

from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger

log = get_task_logger(__name__)

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCRAPER_PYTHON = os.path.join(BACKEND_DIR, ".venv-scraper", "bin", "python")
GEM_SCRIPT = os.path.join(BACKEND_DIR, "scraper", "scrapers", "gem_stealth.py")
CPPP_SCRIPT = os.path.join(BACKEND_DIR, "scraper", "scrapers", "cppp_stealth.py")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery("bidsight", broker=REDIS_URL, backend=REDIS_URL)
app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=86400,
)


def _run_scraper(script: str, args: list[str], timeout: int) -> dict:
    """Run a stealth scraper in the scraper venv as a subprocess."""
    if not os.path.exists(SCRAPER_PYTHON):
        raise RuntimeError(f"Scraper venv python not found at {SCRAPER_PYTHON}")

    env = {**os.environ, "SCRAPER_HEADLESS": "1"}
    cmd = [SCRAPER_PYTHON, script, *args]
    log.info("running: %s", " ".join(cmd))

    proc = subprocess.run(
        cmd, cwd=BACKEND_DIR, env=env,
        capture_output=True, text=True, timeout=timeout,
    )

    for line in proc.stdout.splitlines():
        log.info("scraper | %s", line)
    if proc.returncode != 0:
        log.error("scraper failed code=%s stderr=%s", proc.returncode, proc.stderr[-2000:])
        raise RuntimeError(f"Scraper exited with code {proc.returncode}")

    return {"returncode": proc.returncode, "tail": proc.stdout.splitlines()[-3:]}


@app.task(bind=True, name="scraper.tasks.scrape_gem_portal",
          max_retries=2, default_retry_delay=300)
def scrape_gem_portal(self) -> dict:
    """Scrape GeM via the stealth scraper."""
    try:
        return _run_scraper(GEM_SCRIPT, [], timeout=900)
    except Exception as exc:
        log.error("gem task error: %s", exc)
        raise self.retry(exc=exc)


@app.task(bind=True, name="scraper.tasks.scrape_cppp_portal",
          max_retries=2, default_retry_delay=600,
          time_limit=2400, soft_time_limit=2100)
def scrape_cppp_portal(self, max_orgs: int = 246) -> dict:
    """Scrape CPPP across organisations via the stealth scraper."""
    try:
        return _run_scraper(CPPP_SCRIPT, [str(max_orgs)], timeout=2300)
    except Exception as exc:
        log.error("cppp task error: %s", exc)
        raise self.retry(exc=exc)

@app.task(name="alerts.tasks.check_deadline_alerts")
def check_deadline_alerts() -> dict:
    """Scan tracked bids and create deadline alerts (runs in the backend venv)."""
    from app.database import SessionLocal
    from app.services.alert_service import scan_and_create_alerts
    db = SessionLocal()
    try:
        result = scan_and_create_alerts(db)
        log.info("deadline_alerts: %s", result)
        return result
    finally:
        db.close()

app.conf.beat_schedule = {
    "scrape-gem-every-6h": {
        "task": "scraper.tasks.scrape_gem_portal",
        "schedule": crontab(hour="*/6", minute=0),
    },
    "scrape-cppp-daily": {
        "task": "scraper.tasks.scrape_cppp_portal",
        "schedule": crontab(hour=0, minute=30),  # 06:00 IST
        "kwargs": {"max_orgs": 246},
    },
    "deadline-alerts-daily": {
        "task": "alerts.tasks.check_deadline_alerts",
        "schedule": crontab(hour=2, minute=30),  # 08:00 IST
    },
}