from __future__ import annotations

"""
Keyword classifier for tender titles.

Each category has a list of keywords. Matching is on whole words/phrases, so
"bus" doesn't fire on "business" and "ration" doesn't fire on "administration".

Keyword syntax:
  "pump"       whole word or phrase
  "spectro*"   prefix: matches spectrometer, spectroscopy, ...
  "~hospital"  weak context word (counts 0.3 instead of 1). Use for words that
               say *where* the work happens rather than *what* it is, so
               "Construction of hospital block" lands in construction.

The category with the highest score wins; ties go to whichever is listed first.
"""

import re
from functools import lru_cache

from scraper.models.tender import TenderCategory as C

WEAK_WEIGHT = 0.3

CATEGORY_KEYWORDS: dict[C, list[str]] = {
    # Service contracts first: their titles also name the site ("manpower for
    # National Highway Circle"), so they need to win ties.
    C.MANPOWER: [
        "manpower", "man power", "man-power", "contract labour*", "labour supply",
        "outsourc*", "deployment of manpower", "staffing", "data entry operator*", "skilled",
        "unskilled", "semi-skilled", "multi tasking staff", "mts", "office assistant*",
        "hiring of personnel", "workforce", "job work*", "job worker*",
    ],
    C.SECURITY_SERVICES: [
        "security guard*", "security service*", "security agency", "manpower security",
        "watchman", "watch and ward", "cctv", "surveillance", "access control",
        "baggage scanner*", "x-ray baggage", "metal detector*", "dfmd", "hhmd",
        "boom barrier*", "concertina", "barbed wire", "cbrn*",
    ],
    # ── IT ────────────────────────────────────────────────────────────────
    C.AI_ML: [
        "artificial intelligence", "machine learning", "ai", "ai enabled", "ai based",
        "ml model", "data science", "analytics platform", "gpu workstation", "gpu server",
        "computer vision", "chatbot", "deep learning",
    ],
    C.CYBERSECURITY: [
        "cyber security", "cybersecurity", "vapt", "penetration test*", "firewall",
        "soc", "siem", "endpoint security", "antivirus", "information security audit",
        "security audit", "ddos",
    ],
    C.CLOUD: [
        "cloud", "aws", "azure", "saas", "paas", "iaas", "hosting", "data center service*",
        "colocation",
    ],
    C.IT_SOFTWARE: [
        "software", "erp", "mobile app", "website", "web portal", "web application", "portal",
        "application development", "crm", "online platform", "online assessment",
        "e-office", "digital transformation", "digitization", "digitisation",
        "it solution*", "it services", "it system*", "management system", "mis",
        "licence*", "license*", "subscription of software",
    ],
    C.INFRASTRUCTURE: [
        "network*", "lan", "wan", "wi-fi", "wifi", "leased line", "internet", "bandwidth",
        "structured cabling", "cabling", "datacenter", "data centre", "data center",
        "it storage", "storage system", "nas", "san storage", "router*", "network switch*", "poe switch*", "l2 switch*", "l3 switch*",
        "mpls", "sdh", "optical fibre", "optical fiber", "ofc", "telecom*", "tower",
        "epabx", "video conferenc*", "audio visual", "av system",
    ],
    C.HARDWARE: [
        "laptop*", "desktop*", "computer*", "printer*", "server", "servers", "rack server*", "ups", "projector*",
        "workstation*", "monitor", "monitors", "ssd", "hard disk", "tablet pc", "nuc", "all in one",
        "scanner*", "toner*", "cartridge*", "it hardware", "computer peripheral*",
        "led display", "video wall", "interactive panel", "smart board",
    ],
    # ── Medical ───────────────────────────────────────────────────────────
    C.MEDICAL: [
        "medical", "surgical*", "surgery", "breast pump*", "pharma*", "drug*", "medicine*", "tab", "tab.",
        "tablet*", "inj", "inj.", "injection*", "capsule*", "syrup", "vaccine*",
        "syringe*", "catheter*", "diagnostic*", "x-ray", "xray", "ct scan*", "ct simulator",
        "mri", "ultrasound", "ventilator*", "laryngoscop*", "endoscop*", "laparoscop*",
        "arthroscop*", "ureteroscop*", "ureterorenoscop*", "bronchoscop*", "airway scope",
        "nerve monitoring", "elispot", "antibiotic*", "biochemistry", "microbiology",
        "mr imaging", "gamma knife", "clinical", "operation theatre", "modular ot", "ot table",
        "icu", "nicu", "picu", "dialysis", "oxygen concentrator*", "defibrillator*",
        "reagent*", "kit", "kits", "test kit*", "nephelometer", "microplate", "chemiluminescence",
        "immunoassay", "pcr", "absorptiometry", "dexa", "coagulation", "gamma globulin",
        "thromboelast*", "cytology", "hematology", "haematology", "transfusion", "blood bag*",
        "blood bank", "pulmonary", "dental", "orthopaedic*", "orthopedic*", "implant*",
        "stent*", "suture*", "gauze", "bandage*", "cotton roll*", "glove*", "ppe",
        "patient monitor*", "infusion pump*", "anaesthesia", "anesthesia", "cardiac",
        "cardiology", "neurology", "oncology", "radiology", "radiotherapy", "linac",
        "urology", "gynaec*", "ophthalm*", "ent", "physiotherapy", "pathology", "histopath*",
        "hospital bed*", "operating table*", "ot light*", "stretcher*", "wheel chair*", "wheelchair*", "autoclave*",
        "sterilizer*", "steriliser*", "medical gas*", "hearing aid*", "prosthe*", "ayush",
        "analyzer*", "analyser*", "blood*", "urine", "cranial", "tld",
        "~hospital", "~aiims", "~patient*", "~esic", "~health", "~dispensary",
    ],
    # ── Lab & scientific instruments (IITs, BARC, DRDO, CSIR labs) ────────
    C.LAB_SCIENTIFIC: [
        "spectro*", "spectrophotometer", "chromatograph*", "hplc", "uhplc", "lcms", "lc-ms",
        "gcms", "gc-ms", "mass spectrometer", "microscope*", "microscopy", "centrifuge*",
        "furnace*", "potentiostat*", "porosimeter*", "rheometer*", "calorimeter*",
        "diffractometer*", "xrd", "nmr", "fume hood*", "glove box*", "incubator*",
        "~laboratory", "~lab", "lab equipment", "reactor*", "microtome", "ultramicrotome", "lab instrument*", "laboratory equipment",
        "test setup", "test rig*", "testing machine", "universal testing", "oscilloscope*",
        "signal generator*", "spectrum analy*", "network analy*", "probe station",
        "sodar", "lidar", "thermal analy*", "particle size", "sputter*", "deposition system",
        "vacuum system", "cryo*", "liquid nitrogen", "chipshover", "laser*", "nd yag",
        "interferometer*", "anaerobic", "bioreactor*", "fermenter*", "pcr machine",
        "thermocycler", "flow cytometer", "simulator*", "telemetry", "piezometer*",
        "flow meter*", "data logger*", "sensor*", "instrumentation",
        "scientific", "research equipment", "analytical balance", "weighing balance",
        "seismic", "~iit", "~iisc", "~iiser", "~tifr", "~barc", "~drdo", "~csir", "~nit",
    ],
    # ── Works ─────────────────────────────────────────────────────────────
    C.ROADS_HIGHWAYS: [
        "road*", "highway*", "nh", "nh-*", "km", "bituminous", "dbm", "bc", "macadam*",
        "pavement*", "paved shoulder*", "carriageway", "flyover", "rob", "rub",
        "bridge*", "culvert*", "service lane*", "kerb*", "road marking", "road stud*",
        "footpath*", "foot path*", "pathway*", "tunnel*", "nhidcl", "nhai",
        "morth", "railway siding", "track", "pothole*", "parking",
    ],
    C.HORTICULTURE: [
        "horticulture", "hort", "garden*", "lawn*", "landscap*", "plantation",
        "tree*", "nursery", "plant saplings", "grass", "hedge*", "park", "parks", "greenery",
        "golf course*", "agricultur*", "seed*", "fertili*", "cow unit*", "dairy",
        "livestock", "poultry", "fisheries", "coconut",
    ],
    C.WATER_SANITATION: [
        "water supply", "water line", "water pipe*", "pipe line*", "pipeline*",
        "plumbing", "sanitary", "sewer*", "sewage", "stp", "etp", "drain*", "septic tank*",
        "soak pit*", "manhole*", "tube well*", "borewell*", "bore well*", "water drilling",
        "submersible pump*", "pump*", "pump house", "overhead tank*", "water tank*",
        "ro plant*", "water treatment", "ultra-pure water", "water purifier*", "water cooler*",
        "water bodies", "waterbodies", "water body", "pond*", "lake*", "canal*", "water proofing",
        "rain water", "rainwater", "drinking water", "river training", "flood protection",
        "anti-erosion", "anti erosion", "toilet*", "urinal*", "conservancy", "garbage", "solid waste",
        "waste management", "desilting", "de-silting",
    ],
    C.CONSTRUCTION: [
        "construction", "c/o", "civil", "civil work*", "building work*", "renovation",
        "infrastructure work*", "patch repair*", "extension of", "building*", "bldg",
        "boundary wall*", "compound wall*", "retaining wall*", "wall*", "fencing", "fence",
        "gate*", "plaster*", "painting", "paint*", "white washing", "whitewash*",
        "distemper*", "waterproofing", "water proofing treatment", "flooring", "floor*",
        "tiling", "tiles", "false ceiling", "ceiling", "roof*", "rcc", "brick*", "masonry",
        "grill*", "shed*", "barrack*", "quarters", "qtr*", "accommodation", "accn",
        "hostel*", "residential", "housing", "colony", "colonies", "m/o", "a/r",
        "a/r and m/o", "special repair*", "sr work*", "mc and ew", "mc ew", "mcew", "cdw",
        "conservation of", "conservation work*", "monument*", "excavated", "stupa",
        "fort", "fortification", "temple", "mosque", "heritage", "tumuli", "rampart",
        "structural", "structure*", "epc", "upgradation of", "public amenities",
        "modernization of", "modernisation of", "retrofitting", "demolition", "dismantling",
        "interior*", "furnishing", "finishing work*", "modification of", "room*",
        "restructuring", "railing*", "partition*", "door*", "window*", "staircase*",
        "kitchen*", "dining hall", "jetty", "pontoon*", "dam", "spillway", "embankment*",
        "anti termite", "repair of", "repairs to", "repair work*", "repair and maint*",
        "repair maint*", "repair/ maint*", "repair/maint*",
        "b and r", "b&r", "bnr", "minor work*", "petty work*", "day to day repair*",
        "day-to-day maintenance", "arm of", "~campus", "~bsf", "~itbp", "~cpwd",
    ],
    C.ELECTRICAL: [
        "electrical", "electrification", "e and m", "e&m", "e m", "wiring", "rewiring",
        "transformer*", "switchgear", "substation*", "sub station*", "panel*", "apfc",
        "power factor", "cable*", "led light*", "led", "lighting", "street light*",
        "high mast", "solar*", "dg set*", "diesel generator*", "kva", "kv", "ht line",
        "lt line", "earthing", "lightning arrester*", "ups system", "inverter*",
        "batter*", "hvac", "air condition*", "precision air condition*", "ac", "a.c.", "split ac", "chiller*",
        "ahu", "fcu*", "vrf", "vrv", "lift*", "elevator*", "escalator*", "fire alarm*",
        "fire fighting", "fire detection", "fire hydrant*", "sprinkler*", "geyser*",
        "fan*", "electric*", "power station", "power supply", "energy meter*",
    ],
    # ── Goods & services ─────────────────────────────────────────────────
    C.MAINTENANCE_AMC: [
        "amc", "camc", "annual maintenance", "cmc", "comprehensive maintenance", "maintenance contract",
        "term contract", "operation and maintenance", "o&m", "o & m", "housekeeping",
        "house keeping", "facility management", "facilities management", "cleaning",
        "sweeping", "pest control", "fumigation", "repair and overhauling",
        "repair, maintenance", "overhaul*", "servicing", "periodical service*",
        "maintenance", "maint", "upkeep", "refilling", "calibration",
    ],
    C.CONSULTING: [
        "consulting", "consultant*", "consultancy", "advisory", "advisor*",
        "assessment study", "study", "feasibility", "survey*", "dpr",
        "detailed project report", "project management consultan*", "pmc", "audit", "audits",
        "valuation", "third party inspection", "tpi", "evaluation agency",
        "implementing agency", "selection of agency", "empanelment", "photogrammetr*",
        "morphological", "hydrological", "geotechnical", "design and drawing",
        "architect*", "training", "capacity building", "research study",
    ],
    C.CHEMICALS_GASES: [
        "chemical*", "acid*", "solvent*", "toluene", "benzene", "methanol", "ethanol",
        "urea", "alum", "alumino*", "ferric", "chlorine", "caustic", "sulphur*", "sulfur*",
        "charcoal", "activated carbon", "resin*", "catalyst*", "lubricant*", "oil*",
        "grease", "diesel", "petrol", "~fuel*", "fuel oil", "furnace oil", "lpg", "cng", "nitrogen", "oxygen",
        "argon", "helium", "hydrogen", "co2", "gas cylinder*", "industrial gas*",
        "corrosion", "polymer*", "xylene", "xylol", "paraffin", "wax", "alcohol",
        "emulsifier*", "dispersing", "reagent grade", "~coating*", "adhesive*", "fly ash", "coal",
    ],
    C.SPORTS: [
        "sport*", "archery", "gym*", "fitness", "athletic*", "stadium", "badminton",
        "basketball", "volleyball", "football", "cricket", "hockey", "tennis",
        "swimming pool", "playground", "play equipment", "synthetic track",
        "acrylic sports", "powerlifting", "weightlifting", "gymnastic*", "table tennis", "yoga",
    ],
    C.FOOD_CATERING: [
        "catering", "caterer*", "food*", "ration*", "canteen*", "meal*", "mess",
        "cafeteria", "refreshment*", "pantry", "kitchen items", "grocery", "groceries",
        "vegetable*", "fruit*", "milk", "mutton", "chicken", "fish", "egg*", "rice",
        "wheat", "atta", "dal", "pulses", "edible oil", "tea", "coffee", "snacks",
        "bread", "packaged water",
    ],
    C.VEHICLES: [
        "vehicle*", "bus", "buses", "car", "cars", "ambulance*", "two wheeler*",
        "motor cycle*", "motorcycle*", "scooter*", "tipper*", "truck*", "jeep*", "suv",
        "taxi", "cab", "cabs", "van", "hiring of vehicle*", "car hire", "transportation",
        "transport", "logistics", "freight", "courier", "shifting of", "tyre*", "tire*",
    ],
    C.EQUIPMENT_MACHINERY: [
        "earth moving", "excavator*", "dumper*", "tractor*", "crane*", "jcb",
        "generator*", "compressor*", "machine*", "machinery", "equipment hire",
        "forklift*", "loader*", "drilling", "boom", "hoist*", "winch*", "workshop equipment",
        "lathe", "welding", "cnc", "press", "engine*", "conveyor*", "boiler*", "turbine*",
        "skid steer", "equipment",
    ],
    C.INDUSTRIAL_PARTS: [
        "bearing*", "valve*", "gasket*", "shelving rack*", "ballast block*", "spare*",
        "spare part*", "industrial component*", "vacuum cleaner*", "cylinder*", "pipe*",
        "fitting*", "flange*", "weldolet*", "elbow*", "tee", "nipple*", "coupling*",
        "nut*", "bolt*", "fastener*", "screw*", "seal*", "o ring*", "o-ring*", "hose*",
        "filter*", "gear*", "shaft*", "impeller*", "motor*", "belt*", "chain*", "wire rope*",
        "sheet*", "plate*", "steel", "ms", "ss", "gi", "aluminium", "aluminum", "copper",
        "brass", "rod*", "tool*", "tool kit*", "abrasive*", "buffing", "grinding wheel*",
        "flap wheel*", "hardware items", "consumable*", "insulator*", "bushing*",
        "contact assembly", "instrument*", "gauge*", "thermocouple*", "thermowell*",
        "steam trap*", "insulation", "rubber lining", "weight*", "stirrup*",
    ],
    C.FURNITURE: [
        "furniture", "chair*", "table*", "almirah*", "cabinet*", "desk*", "sofa*",
        "bench", "benches", "bed", "beds", "mattress*", "cot", "cots", "locker*", "rack*",
        "workstation furniture", "modular furniture", "podium", "stool*", "cupboard*",
    ],
    C.TEXTILES_APPAREL: [
        "uniform*", "textile*", "fabric*", "garment*", "apparel", "shoe*", "footwear",
        "boots", "cloth*", "blanket*", "bedsheet*", "bed sheet*", "linen", "curtain*",
        "towel*", "jacket*", "tent", "tents", "tarpaulin*", "carpet*", "rug", "rugs", "jersey*",
    ],
    C.OFFICE_SUPPLIES: [
        "stationery", "stationary", "paper*", "printing", "printing service*",
        "office supply", "office supplies", "envelope*", "file cover*", "register", "registers",
        "diary", "diaries", "calendar*", "manuals", "workbook*", "book", "books", "booklet*",
        "brochure*", "pamphlet*", "banner*", "flex", "flex banner*", "photocopy*", "xerox", "binding",
        "branding", "visiting card*", "id card*",
    ],
    C.LIBRARY_PUBLISHING: [
        "database subscription", "library", "journal*", "e-journal*", "publication*",
        "publishing", "signage*", "book festival", "magazine*", "newspaper*",
        "subscription", "e-books", "e-resource*",
    ],
    C.DEFENSE_MARINE: [
        "submarine*", "naval", "navy", "marine", "ship*", "boat*", "port",
        "battery type", "ugssn", "defence", "defense", "armed forces", "ordnance",
        "ammunition", "fuze*", "7.62", "5.56", "weapon*", "bomb", "firing range", "parachute*",
        "~army", "~assam rifles", "~coast guard",
    ],
}

_BOUNDARY = r"[a-z0-9]"


def _compile(keyword: str) -> tuple[re.Pattern, float]:
    weight = 1.0
    if keyword.startswith("~"):
        weight = WEAK_WEIGHT
        keyword = keyword[1:]
    prefix = keyword.endswith("*")
    keyword = keyword.rstrip("*")
    pattern = rf"(?<!{_BOUNDARY}){re.escape(keyword)}"
    if not prefix:
        pattern += rf"(?!{_BOUNDARY})"
    return re.compile(pattern), weight


@lru_cache(maxsize=1)
def _compiled() -> list[tuple[C, list[tuple[re.Pattern, float]]]]:
    return [(cat, [_compile(kw) for kw in kws]) for cat, kws in CATEGORY_KEYWORDS.items()]


def classify(title: str, description: str = "") -> C:
    text = f"{title} {description or ''}".lower()
    best, best_score = C.OTHER, 0.0
    for category, patterns in _compiled():
        score = sum(weight for pattern, weight in patterns if pattern.search(text))
        if score > best_score:
            best, best_score = category, score
    # A lone weak context word ("hospital", "IIT") isn't enough to classify
    return best if best_score >= 1 else C.OTHER
