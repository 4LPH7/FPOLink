"""FPOLink TN — Statewide Platform Foundation Reference Seed (v0.5)

Populates canonical reference data for Tamil Nadu:
1. State (Tamil Nadu) and all 38 Revenue Districts.
2. Taluks for primary pilot hubs (Erode, Coimbatore, Thanjavur).
3. Tier-A commodities (20+ crops) with botanical names, Tamil names, and aliases.
4. Key crop varieties and aliases.
5. Regulated market master registry with district links, coordinates, and aliases.
6. Ingestion Data Sources telemetry master.

Idempotent: safe to run multiple times without duplicating or corrupting data.
"""

import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal
from app.models.crop import Crop
from app.models.crop_alias import CropAlias
from app.models.data_quality import DataSource
from app.models.geography import District, State, Taluk
from app.models.market import Market
from app.models.market_alias import MarketAlias
from app.models.variety import Variety
from app.models.variety_alias import VarietyAlias


# ─────────────────────────────────────────────────────────────────────────────
# 1. TAMIL NADU 38 DISTRICTS
# ─────────────────────────────────────────────────────────────────────────────
TN_DISTRICTS = [
    ("Ariyalur", "ARI"),
    ("Chengalpattu", "CGL"),
    ("Chennai", "CHN"),
    ("Coimbatore", "CBE"),
    ("Cuddalore", "CUD"),
    ("Dharmapuri", "DHP"),
    ("Dindigul", "DGL"),
    ("Erode", "ERD"),
    ("Kallakurichi", "KLK"),
    ("Kanchipuram", "KCH"),
    ("Kanyakumari", "KKI"),
    ("Karur", "KAR"),
    ("Krishnagiri", "KGI"),
    ("Madurai", "MDU"),
    ("Mayiladuthurai", "MYD"),
    ("Nagapattinam", "NGP"),
    ("Namakkal", "NMK"),
    ("Nilgiris", "NLG"),
    ("Perambalur", "PER"),
    ("Pudukkottai", "PDK"),
    ("Ramanathapuram", "RMD"),
    ("Ranipet", "RNP"),
    ("Salem", "SLM"),
    ("Sivaganga", "SVG"),
    ("Tenkasi", "TKS"),
    ("Thanjavur", "TNJ"),
    ("Theni", "THN"),
    ("Thoothukudi", "TTK"),
    ("Tiruchirappalli", "TRY"),
    ("Tirunelveli", "TNV"),
    ("Tirupathur", "TPR"),
    ("Tiruppur", "TUP"),
    ("Tiruvallur", "TLR"),
    ("Tiruvannamalai", "TVM"),
    ("Tiruvarur", "TVR"),
    ("Vellore", "VEL"),
    ("Viluppuram", "VLP"),
    ("Virudhunagar", "VRD"),
]

# Taluks for primary pilot hubs
TALUKS_BY_DISTRICT = {
    "Erode": [
        ("Erode", "ERD-ERD"),
        ("Perundurai", "ERD-PRD"),
        ("Bhavani", "ERD-BHV"),
        ("Modakkurichi", "ERD-MDK"),
        ("Kodumudi", "ERD-KDM"),
        ("Gobichettipalayam", "ERD-GBC"),
        ("Sathyamangalam", "ERD-STM"),
        ("Anthiyur", "ERD-ANT"),
        ("Thalavadi", "ERD-TLV"),
    ],
    "Coimbatore": [
        ("Coimbatore North", "CBE-NORTH"),
        ("Coimbatore South", "CBE-SOUTH"),
        ("Pollachi", "CBE-POL"),
        ("Mettupalayam", "CBE-MTP"),
        ("Sulur", "CBE-SLR"),
        ("Annur", "CBE-ANR"),
        ("Kinathukadavu", "CBE-KKD"),
        ("Valparai", "CBE-VLP"),
    ],
    "Thanjavur": [
        ("Thanjavur", "TNJ-TNJ"),
        ("Kumbakonam", "TNJ-KMB"),
        ("Papanasam", "TNJ-PPN"),
        ("Pattukkottai", "TNJ-PKT"),
        ("Orathanadu", "TNJ-ORT"),
        ("Thiruvaiyaru", "TNJ-TVR"),
        ("Budalur", "TNJ-BDL"),
        ("Peravurani", "TNJ-PVR"),
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. TIER-A COMMODITIES & ALIASES
# ─────────────────────────────────────────────────────────────────────────────
TIER_A_CROPS = [
    {
        "name": "turmeric",
        "canonical_name": "turmeric",
        "scientific_name": "Curcuma longa",
        "category": "spice",
        "tamil_name": "மஞ்சள்",
        "unit": "kg",
        "hs_code": "091030",
        "aliases": ["manjal", "haldi", "turmeric", "erode turmeric", "raw turmeric", "dry turmeric"],
        "varieties": [
            ("Salem", ["salem manjal", "salem variety"]),
            ("Erode Local", ["erode local", "chinna manjal"]),
            ("BSR-1", ["bsr 1", "bhavanisagar 1"]),
            ("BSR-2", ["bsr 2"]),
        ],
    },
    {
        "name": "banana",
        "canonical_name": "banana",
        "scientific_name": "Musa acuminata",
        "category": "fruit",
        "tamil_name": "வாழை",
        "unit": "kg",
        "hs_code": "080390",
        "aliases": ["vaazhai", "kela", "banana", "plantain"],
        "varieties": [
            ("Poovan", ["poovan vaazhai", "poovan"]),
            ("Nendran", ["nendran", "kerala banana"]),
            ("Robusta", ["robusta", "green banana"]),
            ("Rasthali", ["rasthali", "silk banana"]),
            ("Red Banana", ["sevvaazhai", "red banana"]),
        ],
    },
    {
        "name": "coconut",
        "canonical_name": "coconut",
        "scientific_name": "Cocos nucifera",
        "category": "plantation",
        "tamil_name": "தேங்காய்",
        "unit": "unit",
        "hs_code": "080112",
        "aliases": ["thengai", "nariyal", "coconut", "copra", "koppari"],
        "varieties": [
            ("West Coast Tall", ["wct", "tall coconut"]),
            ("East Coast Tall", ["ect"]),
            ("TxD Hybrid", ["hybrid coconut"]),
        ],
    },
    {
        "name": "paddy",
        "canonical_name": "paddy",
        "scientific_name": "Oryza sativa",
        "category": "cereal",
        "tamil_name": "நெல்",
        "unit": "kg",
        "hs_code": "100610",
        "aliases": ["nellu", "dhaan", "paddy", "rice", "rough rice"],
        "varieties": [
            ("Ponni", ["ponni", "deluxe ponni"]),
            ("BPT 5204", ["samba masuri", "bpt"]),
            ("ADT 37", ["adt 37"]),
            ("CO 51", ["co 51"]),
            ("CR 1009", ["cr 1009", "savithri"]),
        ],
    },
    {
        "name": "groundnut",
        "canonical_name": "groundnut",
        "scientific_name": "Arachis hypogaea",
        "category": "oilseed",
        "tamil_name": "நிலக்கடலை",
        "unit": "kg",
        "hs_code": "120242",
        "aliases": ["verkadalai", "moongphali", "peanut", "groundnut"],
        "varieties": [
            ("TMV 7", ["tmv 7"]),
            ("JL 24", ["jl 24"]),
            ("VRI 2", ["vri 2"]),
        ],
    },
    {
        "name": "tomato",
        "canonical_name": "tomato",
        "scientific_name": "Solanum lycopersicum",
        "category": "vegetable",
        "tamil_name": "தக்காளி",
        "unit": "kg",
        "hs_code": "070200",
        "aliases": ["thakkali", "tamatar", "tomato", "local tomato"],
        "varieties": [
            ("Country / Naatu", ["naatu thakkali", "desi tomato"]),
            ("Hybrid", ["hybrid tomato", "bangalore tomato"]),
        ],
    },
    {
        "name": "small onion",
        "canonical_name": "small onion",
        "scientific_name": "Allium cepa var. aggregatum",
        "category": "vegetable",
        "tamil_name": "சின்ன வெங்காயம்",
        "unit": "kg",
        "hs_code": "070310",
        "aliases": ["chinna vengayam", "shallots", "sambar onion", "small onion"],
        "varieties": [
            ("Co-5", ["co 5 onion"]),
            ("Local Red", ["naatu chinna vengayam"]),
        ],
    },
    {
        "name": "onion",
        "canonical_name": "onion",
        "scientific_name": "Allium cepa",
        "category": "vegetable",
        "tamil_name": "பெரிய வெங்காயம்",
        "unit": "kg",
        "hs_code": "070310",
        "aliases": ["periya vengayam", "pyaz", "onion", "bellary onion"],
        "varieties": [
            ("Bellary", ["bellary pyaz"]),
            ("Nasik", ["nasik onion"]),
        ],
    },
    {
        "name": "green chilli",
        "canonical_name": "green chilli",
        "scientific_name": "Capsicum annuum",
        "category": "spice",
        "tamil_name": "பச்சை மிளகாய்",
        "unit": "kg",
        "hs_code": "070960",
        "aliases": ["pachai milagai", "hari mirch", "green chilli", "chilli"],
        "varieties": [
            ("Samba", ["samba milagai"]),
            ("Kanthari", ["bird eye chilli"]),
        ],
    },
    {
        "name": "red chilli",
        "canonical_name": "red chilli",
        "scientific_name": "Capsicum annuum",
        "category": "spice",
        "tamil_name": "காய்ந்த மிளகாய்",
        "unit": "kg",
        "hs_code": "090421",
        "aliases": ["vara milagai", "sukhi lal mirch", "dry chilli", "red chilli"],
        "varieties": [
            ("Sannam", ["sannam s4"]),
            ("Ramnad Mundu", ["mundu chilli", "ramnad round"]),
        ],
    },
    {
        "name": "maize",
        "canonical_name": "maize",
        "scientific_name": "Zea mays",
        "category": "cereal",
        "tamil_name": "மக்காச்சோளம்",
        "unit": "kg",
        "hs_code": "100590",
        "aliases": ["makkacholam", "makka", "corn", "maize"],
        "varieties": [
            ("Yellow Maize", ["yellow corn", "feed maize"]),
            ("White Maize", ["white corn"]),
        ],
    },
    {
        "name": "cotton",
        "canonical_name": "cotton",
        "scientific_name": "Gossypium hirsutum",
        "category": "fiber",
        "tamil_name": "பருத்தி",
        "unit": "kg",
        "hs_code": "520100",
        "aliases": ["paruthi", "kapas", "cotton", "raw cotton"],
        "varieties": [
            ("Bt Cotton", ["bt cotton"]),
            ("MCU 5", ["mcu 5"]),
        ],
    },
    {
        "name": "sugarcane",
        "canonical_name": "sugarcane",
        "scientific_name": "Saccharum officinarum",
        "category": "commercial",
        "tamil_name": "கரும்பு",
        "unit": "kg",
        "hs_code": "121293",
        "aliases": ["karumbu", "ganna", "sugarcane"],
        "varieties": [
            ("Co 86032", ["nayana"]),
            ("Co 0212", ["co 0212"]),
        ],
    },
    {
        "name": "black gram",
        "canonical_name": "black gram",
        "scientific_name": "Vigna mungo",
        "category": "pulse",
        "tamil_name": "உளுந்து",
        "unit": "kg",
        "hs_code": "071331",
        "aliases": ["ulundhu", "urad dal", "urad", "black gram"],
        "varieties": [
            ("VBN 4", ["vbn 4"]),
            ("VBN 8", ["vbn 8"]),
        ],
    },
    {
        "name": "green gram",
        "canonical_name": "green gram",
        "scientific_name": "Vigna radiata",
        "category": "pulse",
        "tamil_name": "பாசிப்பயறு",
        "unit": "kg",
        "hs_code": "071331",
        "aliases": ["paasi payaru", "moong dal", "moong", "green gram"],
        "varieties": [
            ("CO 8", ["co 8 moong"]),
            ("VBN 3", ["vbn 3"]),
        ],
    },
    {
        "name": "tapioca",
        "canonical_name": "tapioca",
        "scientific_name": "Manihot esculenta",
        "category": "tuber",
        "tamil_name": "மரவள்ளிக்கிழங்கு",
        "unit": "kg",
        "hs_code": "071410",
        "aliases": ["maravalli kizhangu", "kuchikizhangu", "tapioca", "cassava"],
        "varieties": [
            ("MVD 1", ["mvd 1"]),
            ("H 226", ["h 226"]),
        ],
    },
    {
        "name": "mango",
        "canonical_name": "mango",
        "scientific_name": "Mangifera indica",
        "category": "fruit",
        "tamil_name": "மாம்பழம்",
        "unit": "kg",
        "hs_code": "080450",
        "aliases": ["maambazham", "aam", "mango"],
        "varieties": [
            ("Alphonso", ["alphonso", "gundu mango"]),
            ("Banganapalli", ["banganapalli", "chappathai"]),
            ("Imam Pasand", ["himayat", "imam pasand"]),
            ("Neelam", ["neelam"]),
        ],
    },
    {
        "name": "brinjal",
        "canonical_name": "brinjal",
        "scientific_name": "Solanum melongena",
        "category": "vegetable",
        "tamil_name": "கத்தரிக்காய்",
        "unit": "kg",
        "hs_code": "070930",
        "aliases": ["katharikai", "baingan", "brinjal", "eggplant"],
        "varieties": [
            ("Uthukuli Purple", ["uthukuli katharikai"]),
            ("Green Striped", ["pachai katharikai"]),
        ],
    },
    {
        "name": "ladies finger",
        "canonical_name": "ladies finger",
        "scientific_name": "Abelmoschus esculentus",
        "category": "vegetable",
        "tamil_name": "வெண்டைக்காய்",
        "unit": "kg",
        "hs_code": "070999",
        "aliases": ["vendaikkai", "bhindi", "okra", "ladies finger"],
        "varieties": [
            ("Arka Anamika", ["arka anamika"]),
            ("Pusa Sawani", ["pusa sawani"]),
        ],
    },
    {
        "name": "ginger",
        "canonical_name": "ginger",
        "scientific_name": "Zingiber officinale",
        "category": "spice",
        "tamil_name": "இஞ்சி",
        "unit": "kg",
        "hs_code": "091011",
        "aliases": ["inji", "adrak", "ginger", "green ginger"],
        "varieties": [
            ("Rio de Janeiro", ["rio de janeiro"]),
            ("Maran", ["maran inji"]),
        ],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# 3. REGULATED MARKETS & ALIASES
# ─────────────────────────────────────────────────────────────────────────────
PILOT_MARKETS = [
    {
        "name": "Erode Regulated Market",
        "code": "TN-ERD-01",
        "district": "Erode",
        "lat": 11.3410,
        "lon": 77.7172,
        "aliases": ["erode mandi", "erode", "semmampalayam mandi", "erode regulated market committee"],
    },
    {
        "name": "Perundurai Regulated Market",
        "code": "TN-ERD-02",
        "district": "Erode",
        "lat": 11.2764,
        "lon": 77.5831,
        "aliases": ["perundurai mandi", "perundurai", "perundurai regulated market"],
    },
    {
        "name": "Gobichettipalayam Regulated Market",
        "code": "TN-ERD-03",
        "district": "Erode",
        "lat": 11.4549,
        "lon": 77.4373,
        "aliases": ["gobi mandi", "gobichettipalayam", "gobi regulated market"],
    },
    {
        "name": "Kodumudi Regulated Market",
        "code": "TN-ERD-04",
        "district": "Erode",
        "lat": 11.0805,
        "lon": 77.8860,
        "aliases": ["kodumudi mandi", "kodumudi", "kodumudi regulated market"],
    },
    {
        "name": "Coimbatore Regulated Market",
        "code": "TN-CBE-01",
        "district": "Coimbatore",
        "lat": 11.0168,
        "lon": 76.9558,
        "aliases": ["cbe mandi", "coimbatore mandi", "coimbatore regulated market"],
    },
    {
        "name": "Pollachi Regulated Market",
        "code": "TN-CBE-02",
        "district": "Coimbatore",
        "lat": 10.6609,
        "lon": 77.0048,
        "aliases": ["pollachi mandi", "pollachi", "pollachi regulated market"],
    },
    {
        "name": "Thanjavur Regulated Market",
        "code": "TN-TNJ-01",
        "district": "Thanjavur",
        "lat": 10.7870,
        "lon": 79.1378,
        "aliases": ["thanjavur mandi", "thanjavur", "thanjavur regulated market"],
    },
    {
        "name": "Kumbakonam Regulated Market",
        "code": "TN-TNJ-02",
        "district": "Thanjavur",
        "lat": 10.9602,
        "lon": 79.3845,
        "aliases": ["kumbakonam mandi", "kumbakonam", "kumbakonam regulated market"],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# 4. DATA SOURCES TELEMETRY
# ─────────────────────────────────────────────────────────────────────────────
DATA_SOURCES = [
    {"name": "OGD India Mandi Feed", "code": "ogd", "priority": 1},
    {"name": "Agmarknet Central Portal", "code": "agmarknet", "priority": 2},
    {"name": "CEDA Ashoka Mandi Feed", "code": "ceda", "priority": 3},
    {"name": "TN AgriNet Portal", "code": "tn_agrinet", "priority": 4},
    {"name": "Manual Mandi Entry", "code": "manual", "priority": 5},
]


def seed_statewide():
    """Seed statewide master references idempotently."""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("FPOLink TN — Seeding Statewide Platform Foundation (v0.5)")
        print("=" * 60)

        # ─── 1. State ─────────────────────────────────────
        state = db.query(State).filter(State.code == "TN").first()
        if not state:
            state = State(name="Tamil Nadu", code="TN")
            db.add(state)
            db.commit()
            db.refresh(state)
            print(f"✓ Created State: {state.name} ({state.code})")
        else:
            print(f"· State already exists: {state.name} ({state.code})")

        # ─── 2. 38 Revenue Districts ──────────────────────
        district_map = {}
        districts_created = 0
        for name, code in TN_DISTRICTS:
            district = db.query(District).filter(District.name == name).first()
            if not district:
                district = District(name=name, code=code, state_id=state.id)
                db.add(district)
                districts_created += 1
            else:
                if not district.code:
                    district.code = code
                if not district.state_id:
                    district.state_id = state.id
            district_map[name] = district
        db.commit()
        for name in district_map:
            db.refresh(district_map[name])
        print(f"✓ Tamil Nadu Districts: {len(TN_DISTRICTS)} total ({districts_created} newly created)")

        # ─── 3. Pilot Taluks ──────────────────────────────
        taluks_created = 0
        for dist_name, taluks in TALUKS_BY_DISTRICT.items():
            dist_obj = district_map.get(dist_name)
            if not dist_obj:
                continue
            for t_name, t_code in taluks:
                taluk = (
                    db.query(Taluk)
                    .filter(Taluk.name == t_name, Taluk.district_id == dist_obj.id)
                    .first()
                )
                if not taluk:
                    taluk = Taluk(name=t_name, district_id=dist_obj.id)
                    db.add(taluk)
                    taluks_created += 1
        db.commit()
        print(f"✓ Pilot Taluks: {taluks_created} newly created across Erode, Coimbatore, Thanjavur")

        # ─── 4. Tier-A Crops, Varietals & Aliases ──────────
        crops_created = 0
        aliases_created = 0
        varieties_created = 0
        for cdata in TIER_A_CROPS:
            crop = db.query(Crop).filter(Crop.name == cdata["name"]).first()
            if not crop:
                crop = Crop(
                    name=cdata["name"],
                    canonical_name=cdata["canonical_name"],
                    scientific_name=cdata["scientific_name"],
                    category=cdata["category"],
                    tamil_name=cdata["tamil_name"],
                    unit=cdata["unit"],
                    is_active=True,
                )
                db.add(crop)
                db.commit()
                db.refresh(crop)
                crops_created += 1
            else:
                crop.canonical_name = cdata["canonical_name"]
                crop.scientific_name = cdata["scientific_name"]
                crop.tamil_name = cdata["tamil_name"]
                crop.unit = cdata["unit"]
                crop.is_active = True
                db.commit()

            # Seed crop aliases
            for alias_str in cdata["aliases"]:
                alias_clean = alias_str.strip().lower()
                existing_alias = (
                    db.query(CropAlias)
                    .filter(CropAlias.crop_id == crop.id, CropAlias.alias == alias_clean)
                    .first()
                )
                if not existing_alias:
                    db.add(CropAlias(crop_id=crop.id, alias=alias_clean, source="canonical"))
                    aliases_created += 1

            # Seed varieties & variety aliases
            for v_name, v_aliases in cdata.get("varieties", []):
                var_obj = (
                    db.query(Variety)
                    .filter(Variety.crop_id == crop.id, Variety.name == v_name)
                    .first()
                )
                if not var_obj:
                    var_obj = Variety(crop_id=crop.id, name=v_name, canonical_name=v_name)
                    db.add(var_obj)
                    db.commit()
                    db.refresh(var_obj)
                    varieties_created += 1

                for va_str in v_aliases:
                    va_clean = va_str.strip().lower()
                    existing_va = (
                        db.query(VarietyAlias)
                        .filter(VarietyAlias.variety_id == var_obj.id, VarietyAlias.alias == va_clean)
                        .first()
                    )
                    if not existing_va:
                        db.add(VarietyAlias(variety_id=var_obj.id, alias=va_clean, source="canonical"))
        db.commit()
        print(f"✓ Tier-A Commodities: {len(TIER_A_CROPS)} crops ({crops_created} new), {aliases_created} aliases, {varieties_created} varieties")

        # ─── 5. Regulated Markets & Aliases ───────────────
        markets_created = 0
        market_aliases_created = 0
        for mdata in PILOT_MARKETS:
            dist_obj = district_map.get(mdata["district"])
            dist_id = dist_obj.id if dist_obj else None

            market = db.query(Market).filter(Market.name == mdata["name"]).first()
            if not market:
                market = Market(
                    name=mdata["name"],
                    code=mdata["code"],
                    district=mdata["district"],
                    district_id=dist_id,
                    state="Tamil Nadu",
                    market_type="mandi",
                    latitude=mdata["lat"],
                    longitude=mdata["lon"],
                    is_active=True,
                )
                db.add(market)
                db.commit()
                db.refresh(market)
                markets_created += 1
            else:
                market.code = mdata["code"]
                market.district_id = dist_id
                market.latitude = mdata["lat"]
                market.longitude = mdata["lon"]
                market.is_active = True
                db.commit()

            # Seed market aliases
            for ma_str in mdata["aliases"]:
                ma_clean = ma_str.strip().lower()
                existing_ma = (
                    db.query(MarketAlias)
                    .filter(MarketAlias.market_id == market.id, MarketAlias.alias == ma_clean)
                    .first()
                )
                if not existing_ma:
                    db.add(MarketAlias(market_id=market.id, alias=ma_clean, source="canonical"))
                    market_aliases_created += 1
        db.commit()
        print(f"✓ Regulated Markets: {len(PILOT_MARKETS)} markets ({markets_created} new), {market_aliases_created} aliases")

        # ─── 6. Ingestion Data Sources Telemetry ───────────
        ds_created = 0
        for ds in DATA_SOURCES:
            existing_ds = db.query(DataSource).filter(DataSource.code == ds["code"]).first()
            if not existing_ds:
                db.add(
                    DataSource(
                        name=ds["name"],
                        code=ds["code"],
                        priority=ds["priority"],
                        is_active=True,
                    )
                )
                ds_created += 1
        db.commit()
        print(f"✓ Ingestion Data Sources: {len(DATA_SOURCES)} configured ({ds_created} new)")

        print("=" * 60)
        print("✓ Statewide Foundation Reference Seed successfully applied!")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"✗ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_statewide()
