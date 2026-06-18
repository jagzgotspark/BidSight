"""
One-time backfill: re-classify all existing tenders using the expanded
category taxonomy. Safe to re-run — it's idempotent (just re-derives category
from title/description each time).

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

# ── Same keyword table as scraper/scrapers/gem.py — keep in sync ──
_CATEGORY_KEYWORDS = {
    "it_software": ["software", "erp", "mobile app", "web", "portal", "application", "crm"],
    "cloud": ["cloud", "aws", "azure", "saas", "hosting", "data center service"],
    "ai_ml": ["artificial intelligence", "machine learning", " ai ", "ml model", "data science", "analytics platform"],
    "cybersecurity": ["cyber security", "vapt", "penetration test", "firewall", "soc service"],
    "consulting": ["consulting", "advisory", "consultancy", "assessment study"],
    "infrastructure": ["network", "cabling", "datacenter", "data centre", "it storage"],
    "hardware": ["laptop", "desktop", "computer", "printer", "server hardware", "ups", "projector"],
    "medical": ["medical", "hospital", "surgical", "pharma", "drug", "tab.", "syringe", "catheter", "diagnostic", "x-ray", "ventilator", "ambulance", "laryngoscope", "endoscop", "laparoscop", "airway scope", "nerve monitoring", "elispot", "antibiotic", "biochemistry", "microbiology", "mr imaging", "gamma knife", "aiims", "clinical", "operative", "patient", "icu", "dialysis", "oxygen concentrator", "defibrillator"],
    "construction": ["construction", "civil work", "building work", "renovation", "road work", "infrastructure work", "tender for construction"],
    "equipment_machinery": ["earth moving", "excavator", "dumper", "tractor", "crane", "generator", "compressor", "machine", "machinery", "equipment hire"],
    "vehicles": ["vehicle", "bus", "car", "ambulance", "two wheeler", "motor cycle", "tipper"],
    "furniture": ["furniture", "chair", "table", "almirah", "cabinet", "desk", "sofa"],
    "electrical": ["electrical", "wiring", "transformer", "switchgear", "cable", "led light", "solar panel"],
    "textiles_apparel": ["uniform", "textile", "fabric", "garment", "apparel", "shoes", "footwear"],
    "food_catering": ["catering", "food supply", "ration", "canteen", "meal"],
    "office_supplies": ["stationery", "paper", "printing service", "office supply"],
    "security_services": ["security guard", "security service", "manpower security", "watchman"],
    "maintenance_amc": ["amc", "annual maintenance", "cmc", "housekeeping", "facility management", "repair and overhauling", "repair, maintenance", "overhaul"],
    "industrial_parts": ["bearing", "valve", "gasket", "shelving rack", "ballast block", "union 1/2", "spare part", "industrial component", "vacuum cleaner", "cylinder", "skid steer"],
    "defense_marine": ["submarine", "naval", "marine unit", "battery type", "tps", "ugssn", "kpcl", "defence", "armed forces"],
    "library_publishing": ["database subscription", "library", "journal", "publication", "signage"],
}


def classify(title: str, description: str = "") -> str:
    text = (title + " " + (description or "")).lower()
    for category, keywords in _CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return category
    return "other"


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