"""
Seed the database with realistic sample tenders for development.
Usage: python seed_data.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.tender import Tender

def main():
    db = SessionLocal()

    sample_tenders = [
        {
            "id": "gem_seed_001",
            "tender_id": "GEM/2026/B/4521890",
            "source": "gem",
            "title": "AI-Powered Analytics Platform for Ministry of Finance",
            "description": "Development and deployment of an AI-powered analytics platform for real-time financial data monitoring.",
            "authority": "Ministry of Finance",
            "location": "New Delhi",
            "category": "ai_ml",
            "budget_max": 1_80_00_000.0,
            "budget_raw": "₹1.8 Cr",
            "deadline": datetime.utcnow() + timedelta(days=12),
            "deadline_raw": (datetime.utcnow() + timedelta(days=12)).strftime("%d/%m/%Y"),
            "status": "active",
            "source_url": "https://bidplus.gem.gov.in/viewbid/GEM/2026/B/4521890",
        },
        {
            "id": "gem_seed_002",
            "tender_id": "GEM/2026/B/4498231",
            "source": "gem",
            "title": "Cloud Migration Services for IRCTC Digital Infrastructure",
            "description": "End-to-end cloud migration of IRCTC's on-premise infrastructure to AWS/Azure with 24x7 support.",
            "authority": "Indian Railway Catering and Tourism Corporation",
            "location": "New Delhi",
            "category": "cloud",
            "budget_max": 3_40_00_000.0,
            "budget_raw": "₹3.4 Cr",
            "deadline": datetime.utcnow() + timedelta(days=20),
            "deadline_raw": (datetime.utcnow() + timedelta(days=20)).strftime("%d/%m/%Y"),
            "status": "active",
            "source_url": "https://bidplus.gem.gov.in/viewbid/GEM/2026/B/4498231",
        },
        {
            "id": "cppp_seed_001",
            "tender_id": "CPPP/2026/ET/293847",
            "source": "cppp",
            "title": "Cybersecurity Audit and Compliance Assessment — DRDO",
            "description": "Comprehensive cybersecurity audit, VAPT, and compliance assessment for DRDO's internal systems.",
            "authority": "Defence Research and Development Organisation",
            "location": "Bangalore",
            "category": "cybersecurity",
            "budget_max": 95_00_000.0,
            "budget_raw": "₹95 L",
            "deadline": datetime.utcnow() + timedelta(days=7),
            "deadline_raw": (datetime.utcnow() + timedelta(days=7)).strftime("%d/%m/%Y"),
            "status": "active",
            "source_url": "https://eprocure.gov.in/cppp/viewtender/CPPP/2026/ET/293847",
        },
        {
            "id": "cppp_seed_002",
            "tender_id": "CPPP/2026/ET/301234",
            "source": "cppp",
            "title": "ERP Implementation for State Government of Uttar Pradesh",
            "description": "End-to-end ERP implementation covering HR, Finance, and Supply Chain for UP State Government.",
            "authority": "Government of Uttar Pradesh",
            "location": "Lucknow",
            "category": "it_software",
            "budget_max": 3_20_00_000.0,
            "budget_raw": "₹3.2 Cr",
            "deadline": datetime.utcnow() + timedelta(days=21),
            "deadline_raw": (datetime.utcnow() + timedelta(days=21)).strftime("%d/%m/%Y"),
            "status": "active",
            "source_url": "https://eprocure.gov.in/cppp/viewtender/CPPP/2026/ET/301234",
        },
        {
            "id": "gem_seed_003",
            "tender_id": "GEM/2026/B/4510099",
            "source": "gem",
            "title": "Mobile App Development for PMGSY Rural Roads Portal",
            "description": "Native iOS and Android app for monitoring Pradhan Mantri Gram Sadak Yojana road construction progress.",
            "authority": "National Rural Infrastructure Development Agency",
            "location": "New Delhi",
            "category": "it_software",
            "budget_max": 40_00_000.0,
            "budget_raw": "₹40 L",
            "deadline": datetime.utcnow() + timedelta(days=3),
            "deadline_raw": (datetime.utcnow() + timedelta(days=3)).strftime("%d/%m/%Y"),
            "status": "active",
            "source_url": "https://bidplus.gem.gov.in/viewbid/GEM/2026/B/4510099",
        },
        {
            "id": "cppp_seed_003",
            "tender_id": "CPPP/2026/ET/298765",
            "source": "cppp",
            "title": "IT Consulting Services for Digital India Programme",
            "description": "Strategic IT consulting for planning and executing Digital India initiatives across 5 ministries.",
            "authority": "Ministry of Electronics and Information Technology",
            "location": "New Delhi",
            "category": "consulting",
            "budget_max": 1_10_00_000.0,
            "budget_raw": "₹1.1 Cr",
            "deadline": datetime.utcnow() + timedelta(days=15),
            "deadline_raw": (datetime.utcnow() + timedelta(days=15)).strftime("%d/%m/%Y"),
            "status": "active",
            "source_url": "https://eprocure.gov.in/cppp/viewtender/CPPP/2026/ET/298765",
        },
        {
            "id": "gem_seed_004",
            "tender_id": "GEM/2026/B/4488901",
            "source": "gem",
            "title": "Network Infrastructure Upgrade — AIIMS Delhi",
            "description": "Complete network infrastructure upgrade including switches, routers, and fibre cabling for AIIMS Delhi.",
            "authority": "All India Institute of Medical Sciences",
            "location": "New Delhi",
            "category": "infrastructure",
            "budget_max": 2_50_00_000.0,
            "budget_raw": "₹2.5 Cr",
            "deadline": datetime.utcnow() + timedelta(days=30),
            "deadline_raw": (datetime.utcnow() + timedelta(days=30)).strftime("%d/%m/%Y"),
            "status": "active",
            "source_url": "https://bidplus.gem.gov.in/viewbid/GEM/2026/B/4488901",
        },
        {
            "id": "cppp_seed_004",
            "tender_id": "CPPP/2026/ET/312098",
            "source": "cppp",
            "title": "Machine Learning Model Development for GST Fraud Detection",
            "description": "Build and deploy ML models to detect fraudulent GST filings using transaction pattern analysis.",
            "authority": "Central Board of Indirect Taxes and Customs",
            "location": "Mumbai",
            "category": "ai_ml",
            "budget_max": 85_00_000.0,
            "budget_raw": "₹85 L",
            "deadline": datetime.utcnow() + timedelta(days=2),
            "deadline_raw": (datetime.utcnow() + timedelta(days=2)).strftime("%d/%m/%Y"),
            "status": "active",
            "source_url": "https://eprocure.gov.in/cppp/viewtender/CPPP/2026/ET/312098",
        },
    ]

    created = 0
    skipped = 0
    for data in sample_tenders:
        exists = db.query(Tender).filter(Tender.id == data["id"]).first()
        if exists:
            skipped += 1
            continue
        db.add(Tender(**data))
        created += 1

    db.commit()
    db.close()

    print(f"✓ Seeded {created} tenders ({skipped} already existed)")

if __name__ == "__main__":
    main()