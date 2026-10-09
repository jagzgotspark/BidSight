"""
Backfill: re-classify all existing tenders with scraper/classify.py.
Re-run it whenever the keyword table changes. Safe to re-run — it's
idempotent (just re-derives category from title/description each time).

Run from backend/ with the backend venv active:
    python backfill_categories.py
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in .env")
    sys.exit(1)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scraper.classify import classify as _classify  # noqa: E402


def classify(title: str, description: str = "") -> str:
    return _classify(title, description or "").value


def main():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()

    rows = db.execute(
        __import__("sqlalchemy").text("SELECT id, title, description, category FROM tenders")
    ).fetchall()

    print(f"Found {len(rows)} tenders. Re-classifying...")

    changes = {}
    updated = 0

    for row in rows:
        tender_id, title, description, old_category = row
        new_category = classify(title or "", description or "")
        if new_category != old_category:
            db.execute(
                __import__("sqlalchemy").text(
                    "UPDATE tenders SET category = :cat WHERE id = :id"
                ),
                {"cat": new_category, "id": tender_id},
            )
            updated += 1
            changes[new_category] = changes.get(new_category, 0) + 1

    db.commit()

    print(f"\n✓ Updated {updated} of {len(rows)} tenders\n")
    print("New category breakdown of changed rows:")
    for cat, count in sorted(changes.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    db.close()


if __name__ == "__main__":
    main()