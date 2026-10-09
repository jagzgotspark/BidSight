import pytest

from scraper.classify import classify
from scraper.models.tender import TenderCategory as C


@pytest.mark.parametrize("title, expected", [
    # Substring false positives the old classifier had
    ("Registration and administration of business events", C.OTHER),
    ("Construction of hospital block at AIIMS", C.CONSTRUCTION),
    ("Repair/maint of B and R assets for ORs at COB Kotlein of 19 Assam Rifles", C.CONSTRUCTION),
    ("Continuous Monitoring of slew bearing of antenna", C.INDUSTRIAL_PARTS),
    # Categories that used to fall through to "other"
    ("Providing Man power services to National Highway Circle, Bengaluru", C.MANPOWER),
    ("Short Term Maintenance of Rigid Pavement of NH 347C from Km 0/000 to Km 49.985", C.ROADS_HIGHWAYS),
    ("Purchase of Liquid Chromatography-Mass Spectrometer (LCMS)", C.LAB_SCIENTIFIC),
    ("Installation of submersible pump and laying of water supply line", C.WATER_SANITATION),
    ("M/o completed scheme under NA-II, Hort. Zone.", C.HORTICULTURE),
    ("Supply of Technical Grade Urea", C.CHEMICALS_GASES),
    ("Procurement of HOYT Make Archery Equipment", C.SPORTS),
    ("M/o Various colonies under South Zone.", C.CONSTRUCTION),
    ("Inj. Belinostat 500mg", C.MEDICAL),
    ("SUPLLY OF MUTTON CHICKEN FISH EGGS ITEMS", C.FOOD_CATERING),
    ("Provision of CCTV at DRDO Residential Complex", C.SECURITY_SERVICES),
    ("Customized AMC/CMC for Pre-owned Products", C.MAINTENANCE_AMC),
    ("Desktop with monitor", C.HARDWARE),
    # Bare reference numbers carry no signal
    ("28006/Engr/MW-11/2026-27/11", C.OTHER),
])
def test_classify(title, expected):
    assert classify(title) == expected
