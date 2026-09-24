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

from sqlalchemy import func

from app.database import SessionLocal
from app.models.crop import Crop
from app.models.crop_alias import CropAlias
from app.models.data_quality import DataSource
from app.models.geography import District, State, Taluk
from app.models.market import Market
from app.models.market_alias import MarketAlias
from app.models.source_mapping import (
    CropSourceMapping,
    MarketSourceMapping,
    VarietySourceMapping,
)
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
# 3. REGULATED MARKETS & ALIASES (38 DISTRICTS)
# ─────────────────────────────────────────────────────────────────────────────
PILOT_MARKETS = [
    {
        "name": "Erode Regulated Market",
        "canonical_name": "erode regulated market",
        "tamil_name": "ஈரோடு ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-ERD-01",
        "district": "Erode",
        "lat": 11.3410,
        "lon": 77.7172,
        "aliases": ["erode mandi", "erode", "semmampalayam mandi", "erode regulated market committee"],
    },
    {
        "name": "Perundurai Regulated Market",
        "canonical_name": "perundurai regulated market",
        "tamil_name": "பெருந்துறை ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-ERD-02",
        "district": "Erode",
        "lat": 11.2764,
        "lon": 77.5831,
        "aliases": ["perundurai mandi", "perundurai", "perundurai regulated market"],
    },
    {
        "name": "Gobichettipalayam Regulated Market",
        "canonical_name": "gobichettipalayam regulated market",
        "tamil_name": "கோபிசெட்டிபாளையம் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-ERD-03",
        "district": "Erode",
        "lat": 11.4549,
        "lon": 77.4373,
        "aliases": ["gobi mandi", "gobichettipalayam", "gobi regulated market"],
    },
    {
        "name": "Kodumudi Regulated Market",
        "canonical_name": "kodumudi regulated market",
        "tamil_name": "கொடுமுடி ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-ERD-04",
        "district": "Erode",
        "lat": 11.0805,
        "lon": 77.8860,
        "aliases": ["kodumudi mandi", "kodumudi", "kodumudi regulated market"],
    },
    {
        "name": "Coimbatore Regulated Market",
        "canonical_name": "coimbatore regulated market",
        "tamil_name": "கோயம்புத்தூர் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-CBE-01",
        "district": "Coimbatore",
        "lat": 11.0168,
        "lon": 76.9558,
        "aliases": ["cbe mandi", "coimbatore mandi", "coimbatore regulated market"],
    },
    {
        "name": "Pollachi Regulated Market",
        "canonical_name": "pollachi regulated market",
        "tamil_name": "பொள்ளாச்சி ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-CBE-02",
        "district": "Coimbatore",
        "lat": 10.6609,
        "lon": 77.0048,
        "aliases": ["pollachi mandi", "pollachi", "pollachi regulated market"],
    },
    {
        "name": "Thanjavur Regulated Market",
        "canonical_name": "thanjavur regulated market",
        "tamil_name": "தஞ்சாவூர் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-TNJ-01",
        "district": "Thanjavur",
        "lat": 10.7870,
        "lon": 79.1378,
        "aliases": ["thanjavur mandi", "thanjavur", "thanjavur regulated market"],
    },
    {
        "name": "Kumbakonam Regulated Market",
        "canonical_name": "kumbakonam regulated market",
        "tamil_name": "கும்பகோணம் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-TNJ-02",
        "district": "Thanjavur",
        "lat": 10.9602,
        "lon": 79.3845,
        "aliases": ["kumbakonam mandi", "kumbakonam", "kumbakonam regulated market"],
    },
]

ADDITIONAL_STATEWIDE_MARKETS = [
    {
        "name": "Ariyalur Regulated Market",
        "canonical_name": "ariyalur regulated market",
        "tamil_name": "அரியலூர் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-AYR-01",
        "district": "Ariyalur",
        "lat": 11.1401,
        "lon": 79.0786,
        "aliases": ["ariyalur mandi", "ariyalur", "ariyalur market"],
    },
    {
        "name": "Madurantakam Regulated Market",
        "canonical_name": "madurantakam regulated market",
        "tamil_name": "மதுராந்தகம் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-CGP-01",
        "district": "Chengalpattu",
        "lat": 12.5113,
        "lon": 79.8841,
        "aliases": ["madurantakam mandi", "madurantakam", "chengalpattu mandi"],
    },
    {
        "name": "Koyambedu Wholesale Market",
        "canonical_name": "koyambedu wholesale market",
        "tamil_name": "கோயம்பேடு மொத்த விற்பனை வளாகம்",
        "code": "TN-CHN-01",
        "district": "Chennai",
        "lat": 13.0694,
        "lon": 80.1948,
        "aliases": ["koyambedu mandi", "koyambedu", "chennai mandi", "koyambedu market"],
    },
    {
        "name": "Cuddalore Regulated Market",
        "canonical_name": "cuddalore regulated market",
        "tamil_name": "கடலூர் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-CDL-01",
        "district": "Cuddalore",
        "lat": 11.7480,
        "lon": 79.7714,
        "aliases": ["cuddalore mandi", "cuddalore", "cuddalore market"],
    },
    {
        "name": "Dharmapuri Regulated Market",
        "canonical_name": "dharmapuri regulated market",
        "tamil_name": "தருமபுரி ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-DPI-01",
        "district": "Dharmapuri",
        "lat": 12.1211,
        "lon": 78.1582,
        "aliases": ["dharmapuri mandi", "dharmapuri", "dharmapuri market"],
    },
    {
        "name": "Dindigul Regulated Market",
        "canonical_name": "dindigul regulated market",
        "tamil_name": "திண்டுக்கல் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-DGL-01",
        "district": "Dindigul",
        "lat": 10.3673,
        "lon": 77.9803,
        "aliases": ["dindigul mandi", "dindigul", "dindigul market"],
    },
    {
        "name": "Kallakurichi Regulated Market",
        "canonical_name": "kallakurichi regulated market",
        "tamil_name": "கள்ளக்குறிச்சி ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-KLK-01",
        "district": "Kallakurichi",
        "lat": 11.7384,
        "lon": 78.9639,
        "aliases": ["kallakurichi mandi", "kallakurichi", "kallakurichi market"],
    },
    {
        "name": "Kanchipuram Regulated Market",
        "canonical_name": "kanchipuram regulated market",
        "tamil_name": "காஞ்சிபுரம் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-KCP-01",
        "district": "Kanchipuram",
        "lat": 12.8342,
        "lon": 79.7036,
        "aliases": ["kanchipuram mandi", "kanchipuram", "kanchipuram market"],
    },
    {
        "name": "Nagercoil Regulated Market",
        "canonical_name": "nagercoil regulated market",
        "tamil_name": "நாகர்கோவில் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-KKM-01",
        "district": "Kanyakumari",
        "lat": 8.1833,
        "lon": 77.4119,
        "aliases": ["nagercoil mandi", "nagercoil", "kanyakumari mandi"],
    },
    {
        "name": "Karur Regulated Market",
        "canonical_name": "karur regulated market",
        "tamil_name": "கரூர் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-KRR-01",
        "district": "Karur",
        "lat": 10.9601,
        "lon": 78.0766,
        "aliases": ["karur mandi", "karur", "karur market"],
    },
    {
        "name": "Krishnagiri Regulated Market",
        "canonical_name": "krishnagiri regulated market",
        "tamil_name": "கிருஷ்ணகிரி ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-KGI-01",
        "district": "Krishnagiri",
        "lat": 12.5186,
        "lon": 78.2137,
        "aliases": ["krishnagiri mandi", "krishnagiri", "krishnagiri market"],
    },
    {
        "name": "Madurai Regulated Market",
        "canonical_name": "madurai regulated market",
        "tamil_name": "மதுரை ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-MDU-01",
        "district": "Madurai",
        "lat": 9.9252,
        "lon": 78.1198,
        "aliases": ["madurai mandi", "madurai", "mattuthavani mandi", "madurai market"],
    },
    {
        "name": "Mayiladuthurai Regulated Market",
        "canonical_name": "mayiladuthurai regulated market",
        "tamil_name": "மயிலாடுதுறை ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-MYD-01",
        "district": "Mayiladuthurai",
        "lat": 11.1075,
        "lon": 79.6524,
        "aliases": ["mayiladuthurai mandi", "mayiladuthurai", "mayiladuthurai market"],
    },
    {
        "name": "Nagapattinam Regulated Market",
        "canonical_name": "nagapattinam regulated market",
        "tamil_name": "நாகப்பட்டினம் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-NGP-01",
        "district": "Nagapattinam",
        "lat": 10.7654,
        "lon": 79.8424,
        "aliases": ["nagapattinam mandi", "nagapattinam", "nagapattinam market"],
    },
    {
        "name": "Namakkal Regulated Market",
        "canonical_name": "namakkal regulated market",
        "tamil_name": "நாமக்கல் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-NMK-01",
        "district": "Namakkal",
        "lat": 11.2189,
        "lon": 78.1674,
        "aliases": ["namakkal mandi", "namakkal", "namakkal market"],
    },
    {
        "name": "Udhagamandalam Regulated Market",
        "canonical_name": "udhagamandalam regulated market",
        "tamil_name": "உதகமண்டலம் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-NLG-01",
        "district": "Nilgiris",
        "lat": 11.4102,
        "lon": 76.6950,
        "aliases": ["ooty mandi", "ooty", "udhagamandalam", "nilgiris mandi"],
    },
    {
        "name": "Perambalur Regulated Market",
        "canonical_name": "perambalur regulated market",
        "tamil_name": "பெரம்பலூர் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-PBL-01",
        "district": "Perambalur",
        "lat": 11.2342,
        "lon": 78.8820,
        "aliases": ["perambalur mandi", "perambalur", "perambalur market"],
    },
    {
        "name": "Pudukkottai Regulated Market",
        "canonical_name": "pudukkottai regulated market",
        "tamil_name": "புதுக்கோட்டை ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-PDK-01",
        "district": "Pudukkottai",
        "lat": 10.3797,
        "lon": 78.8208,
        "aliases": ["pudukkottai mandi", "pudukkottai", "pudukkottai market"],
    },
    {
        "name": "Ramanathapuram Regulated Market",
        "canonical_name": "ramanathapuram regulated market",
        "tamil_name": "இராமநாதபுரம் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-RPM-01",
        "district": "Ramanathapuram",
        "lat": 9.3639,
        "lon": 78.8395,
        "aliases": ["ramanathapuram mandi", "ramanathapuram", "ramnad mandi"],
    },
    {
        "name": "Ranipet Regulated Market",
        "canonical_name": "ranipet regulated market",
        "tamil_name": "இராணிப்பேட்டை ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-RPT-01",
        "district": "Ranipet",
        "lat": 12.9298,
        "lon": 79.3326,
        "aliases": ["ranipet mandi", "ranipet", "ranipet market"],
    },
    {
        "name": "Salem Regulated Market",
        "canonical_name": "salem regulated market",
        "tamil_name": "சேலம் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-SLM-01",
        "district": "Salem",
        "lat": 11.6643,
        "lon": 78.1460,
        "aliases": ["salem mandi", "salem", "shevapet mandi", "salem market"],
    },
    {
        "name": "Sivaganga Regulated Market",
        "canonical_name": "sivaganga regulated market",
        "tamil_name": "சிவகங்கை ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-SVG-01",
        "district": "Sivaganga",
        "lat": 9.8433,
        "lon": 78.4809,
        "aliases": ["sivaganga mandi", "sivaganga", "sivaganga market"],
    },
    {
        "name": "Tenkasi Regulated Market",
        "canonical_name": "tenkasi regulated market",
        "tamil_name": "தென்காசி ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-TSI-01",
        "district": "Tenkasi",
        "lat": 8.9594,
        "lon": 77.3150,
        "aliases": ["tenkasi mandi", "tenkasi", "tenkasi market"],
    },
    {
        "name": "Theni Regulated Market",
        "canonical_name": "theni regulated market",
        "tamil_name": "தேனி ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-THN-01",
        "district": "Theni",
        "lat": 10.0104,
        "lon": 77.4768,
        "aliases": ["theni mandi", "theni", "theni market"],
    },
    {
        "name": "Kovilpatti Regulated Market",
        "canonical_name": "kovilpatti regulated market",
        "tamil_name": "கோவில்பட்டி ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-TKD-01",
        "district": "Thoothukudi",
        "lat": 9.1738,
        "lon": 77.8687,
        "aliases": ["kovilpatti mandi", "kovilpatti", "thoothukudi mandi"],
    },
    {
        "name": "Tiruchirappalli Regulated Market",
        "canonical_name": "tiruchirappalli regulated market",
        "tamil_name": "திருச்சிராப்பள்ளி ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-TRY-01",
        "district": "Tiruchirappalli",
        "lat": 10.7905,
        "lon": 78.7047,
        "aliases": ["trichy mandi", "tiruchirappalli", "gandhi market trichy", "trichy market"],
    },
    {
        "name": "Tirunelveli Regulated Market",
        "canonical_name": "tirunelveli regulated market",
        "tamil_name": "திருநெல்வேலி ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-TNL-01",
        "district": "Tirunelveli",
        "lat": 8.7139,
        "lon": 77.7567,
        "aliases": ["tirunelveli mandi", "tirunelveli", "nellai mandi"],
    },
    {
        "name": "Tirupathur Regulated Market",
        "canonical_name": "tirupathur regulated market",
        "tamil_name": "திருப்பத்தூர் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-TPR-01",
        "district": "Tirupathur",
        "lat": 12.4958,
        "lon": 78.5678,
        "aliases": ["tirupathur mandi", "tirupathur", "tirupathur market"],
    },
    {
        "name": "Tiruppur Regulated Market",
        "canonical_name": "tiruppur regulated market",
        "tamil_name": "திருப்பூர் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-TPU-01",
        "district": "Tiruppur",
        "lat": 11.1085,
        "lon": 77.3411,
        "aliases": ["tiruppur mandi", "tiruppur", "tiruppur market"],
    },
    {
        "name": "Tiruvallur Regulated Market",
        "canonical_name": "tiruvallur regulated market",
        "tamil_name": "திருவள்ளூர் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-TLR-01",
        "district": "Tiruvallur",
        "lat": 13.1437,
        "lon": 79.9083,
        "aliases": ["tiruvallur mandi", "tiruvallur", "tiruvallur market"],
    },
    {
        "name": "Tiruvannamalai Regulated Market",
        "canonical_name": "tiruvannamalai regulated market",
        "tamil_name": "திருவண்ணாமலை ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-TVM-01",
        "district": "Tiruvannamalai",
        "lat": 12.2253,
        "lon": 79.0747,
        "aliases": ["tiruvannamalai mandi", "tiruvannamalai", "tiruvannamalai market"],
    },
    {
        "name": "Tiruvarur Regulated Market",
        "canonical_name": "tiruvarur regulated market",
        "tamil_name": "திருவாரூர் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-TVR-01",
        "district": "Tiruvarur",
        "lat": 10.7725,
        "lon": 79.6365,
        "aliases": ["tiruvarur mandi", "tiruvarur", "tiruvarur market"],
    },
    {
        "name": "Vellore Regulated Market",
        "canonical_name": "vellore regulated market",
        "tamil_name": "வேலூர் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-VEL-01",
        "district": "Vellore",
        "lat": 12.9165,
        "lon": 79.1325,
        "aliases": ["vellore mandi", "vellore", "vellore market"],
    },
    {
        "name": "Viluppuram Regulated Market",
        "canonical_name": "viluppuram regulated market",
        "tamil_name": "விழுப்புரம் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-VPM-01",
        "district": "Viluppuram",
        "lat": 11.9401,
        "lon": 79.4861,
        "aliases": ["viluppuram mandi", "viluppuram", "viluppuram market"],
    },
    {
        "name": "Virudhunagar Regulated Market",
        "canonical_name": "virudhunagar regulated market",
        "tamil_name": "விருதுநகர் ஒழுங்குமுறை விற்பனைக்கூடம்",
        "code": "TN-VNR-01",
        "district": "Virudhunagar",
        "lat": 9.5872,
        "lon": 77.9515,
        "aliases": ["virudhunagar mandi", "virudhunagar", "virudhunagar market"],
    },
]

STATEWIDE_MARKETS = PILOT_MARKETS + ADDITIONAL_STATEWIDE_MARKETS

# ─────────────────────────────────────────────────────────────────────────────
# 4. DETERMINISTIC SOURCE MAPPINGS (OGD & AGMARKNET)
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_CROP_SOURCE_MAPPINGS = [
    {"crop": "turmeric", "source": "ogd", "code": "TURMERIC", "name": "Turmeric"},
    {"crop": "turmeric", "source": "agmarknet", "code": "AGM_TURM", "name": "Turmeric"},
    {"crop": "banana", "source": "ogd", "code": "BANANA", "name": "Banana"},
    {"crop": "banana", "source": "agmarknet", "code": "AGM_BAN", "name": "Banana"},
    {"crop": "coconut", "source": "ogd", "code": "COCONUT", "name": "Coconut"},
    {"crop": "coconut", "source": "agmarknet", "code": "AGM_COC", "name": "Coconut"},
    {"crop": "paddy", "source": "ogd", "code": "PADDY_DHAN", "name": "Paddy(Dhan)(Common)"},
    {"crop": "paddy", "source": "agmarknet", "code": "AGM_PAD", "name": "Paddy(Dhan)"},
    {"crop": "groundnut", "source": "ogd", "code": "GROUNDNUT", "name": "Groundnut"},
    {"crop": "groundnut", "source": "agmarknet", "code": "AGM_GNT", "name": "Groundnut"},
    {"crop": "tomato", "source": "ogd", "code": "TOMATO", "name": "Tomato"},
    {"crop": "tomato", "source": "agmarknet", "code": "AGM_TOM", "name": "Tomato"},
    {"crop": "small onion", "source": "ogd", "code": "SMALL_ONION", "name": "Small Onion"},
    {"crop": "small onion", "source": "agmarknet", "code": "AGM_SON", "name": "Shallot (Small Onion)"},
    {"crop": "onion", "source": "ogd", "code": "ONION", "name": "Onion"},
    {"crop": "onion", "source": "agmarknet", "code": "AGM_ONI", "name": "Onion"},
    {"crop": "green chilli", "source": "ogd", "code": "GREEN_CHILLI", "name": "Green Chilli"},
    {"crop": "green chilli", "source": "agmarknet", "code": "AGM_GCH", "name": "Green Chilli"},
    {"crop": "red chilli", "source": "ogd", "code": "CHILLI_RED", "name": "Chilli Red"},
    {"crop": "red chilli", "source": "agmarknet", "code": "AGM_RCH", "name": "Red Chilli"},
    {"crop": "maize", "source": "ogd", "code": "MAIZE", "name": "Maize"},
    {"crop": "maize", "source": "agmarknet", "code": "AGM_MAI", "name": "Maize"},
    {"crop": "cotton", "source": "ogd", "code": "COTTON", "name": "Cotton"},
    {"crop": "cotton", "source": "agmarknet", "code": "AGM_COT", "name": "Cotton"},
    {"crop": "sugarcane", "source": "ogd", "code": "SUGARCANE", "name": "Sugarcane"},
    {"crop": "sugarcane", "source": "agmarknet", "code": "AGM_SUG", "name": "Sugarcane"},
    {"crop": "black gram", "source": "ogd", "code": "BLACK_GRAM", "name": "Black Gram (Urd Crop)"},
    {"crop": "black gram", "source": "agmarknet", "code": "AGM_BGR", "name": "Black Gram"},
    {"crop": "green gram", "source": "ogd", "code": "GREEN_GRAM", "name": "Green Gram (Moong)"},
    {"crop": "green gram", "source": "agmarknet", "code": "AGM_GGR", "name": "Green Gram"},
    {"crop": "tapioca", "source": "ogd", "code": "TAPIOCA", "name": "Tapioca"},
    {"crop": "tapioca", "source": "agmarknet", "code": "AGM_TAP", "name": "Tapioca"},
    {"crop": "mango", "source": "ogd", "code": "MANGO", "name": "Mango"},
    {"crop": "mango", "source": "agmarknet", "code": "AGM_MNG", "name": "Mango"},
    {"crop": "brinjal", "source": "ogd", "code": "BRINJAL", "name": "Brinjal"},
    {"crop": "brinjal", "source": "agmarknet", "code": "AGM_BRN", "name": "Brinjal"},
    {"crop": "ladies finger", "source": "ogd", "code": "BHINDI", "name": "Bhindi(Ladies Finger)"},
    {"crop": "ladies finger", "source": "agmarknet", "code": "AGM_BHN", "name": "Bhindi"},
    {"crop": "ginger", "source": "ogd", "code": "GINGER", "name": "Ginger(Green)"},
    {"crop": "ginger", "source": "agmarknet", "code": "AGM_GIN", "name": "Ginger"},
]

DEFAULT_MARKET_SOURCE_MAPPINGS = [
    {"market": "Erode Regulated Market", "source": "ogd", "code": "OGD_ERD", "name": "Erode"},
    {"market": "Erode Regulated Market", "source": "agmarknet", "code": "AGM_ERD", "name": "Erode"},
    {"market": "Perundurai Regulated Market", "source": "ogd", "code": "OGD_PRD", "name": "Perundurai"},
    {"market": "Perundurai Regulated Market", "source": "agmarknet", "code": "AGM_PRD", "name": "Perundurai"},
    {"market": "Gobichettipalayam Regulated Market", "source": "ogd", "code": "OGD_GOBI", "name": "Gopichettipalayam"},
    {"market": "Gobichettipalayam Regulated Market", "source": "agmarknet", "code": "AGM_GOBI", "name": "Gobichettipalayam"},
    {"market": "Kodumudi Regulated Market", "source": "ogd", "code": "OGD_KOD", "name": "Kodumudi"},
    {"market": "Kodumudi Regulated Market", "source": "agmarknet", "code": "AGM_KOD", "name": "Kodumudi"},
    {"market": "Coimbatore Regulated Market", "source": "ogd", "code": "OGD_CBE", "name": "Coimbatore"},
    {"market": "Coimbatore Regulated Market", "source": "agmarknet", "code": "AGM_CBE", "name": "Coimbatore"},
    {"market": "Pollachi Regulated Market", "source": "ogd", "code": "OGD_POL", "name": "Pollachi"},
    {"market": "Pollachi Regulated Market", "source": "agmarknet", "code": "AGM_POL", "name": "Pollachi"},
    {"market": "Madurai Regulated Market", "source": "ogd", "code": "OGD_MDU", "name": "Madurai"},
    {"market": "Madurai Regulated Market", "source": "agmarknet", "code": "AGM_MDU", "name": "Madurai"},
    {"market": "Salem Regulated Market", "source": "ogd", "code": "OGD_SLM", "name": "Salem"},
    {"market": "Salem Regulated Market", "source": "agmarknet", "code": "AGM_SLM", "name": "Salem"},
    {"market": "Tiruchirappalli Regulated Market", "source": "ogd", "code": "OGD_TRY", "name": "Tiruchirappalli"},
    {"market": "Tiruchirappalli Regulated Market", "source": "agmarknet", "code": "AGM_TRY", "name": "Tiruchirappalli"},
    {"market": "Thanjavur Regulated Market", "source": "ogd", "code": "OGD_TNJ", "name": "Thanjavur"},
    {"market": "Thanjavur Regulated Market", "source": "agmarknet", "code": "AGM_TNJ", "name": "Thanjavur"},
    {"market": "Kumbakonam Regulated Market", "source": "ogd", "code": "OGD_KMB", "name": "Kumbakonam"},
    {"market": "Kumbakonam Regulated Market", "source": "agmarknet", "code": "AGM_KMB", "name": "Kumbakonam"},
    {"market": "Dindigul Regulated Market", "source": "ogd", "code": "OGD_DGL", "name": "Dindigul"},
    {"market": "Dindigul Regulated Market", "source": "agmarknet", "code": "AGM_DGL", "name": "Dindigul"},
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
        for mdata in STATEWIDE_MARKETS:
            dist_obj = district_map.get(mdata["district"])
            dist_id = dist_obj.id if dist_obj else None
            canonical = mdata.get("canonical_name", mdata["name"].lower())
            tamil_name = mdata.get("tamil_name")

            market = db.query(Market).filter(Market.name == mdata["name"]).first()
            if not market:
                market = Market(
                    name=mdata["name"],
                    canonical_name=canonical,
                    tamil_name=tamil_name,
                    code=mdata["code"],
                    district=mdata["district"],
                    district_id=dist_id,
                    state="Tamil Nadu",
                    market_type=mdata.get("market_type", "regulated_market"),
                    is_regulated=True,
                    e_nam=mdata.get("e_nam", False),
                    operating_status="active",
                    latitude=mdata["lat"],
                    longitude=mdata["lon"],
                    is_active=True,
                )
                db.add(market)
                db.commit()
                db.refresh(market)
                markets_created += 1
            else:
                market.canonical_name = canonical
                market.tamil_name = tamil_name
                market.code = mdata["code"]
                market.district_id = dist_id
                market.latitude = mdata["lat"]
                market.longitude = mdata["lon"]
                market.is_regulated = True
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
        print(f"✓ Regulated Markets: {len(STATEWIDE_MARKETS)} markets ({markets_created} new), {market_aliases_created} aliases across 38 districts")

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
        print(f"✓ Data Sources: {len(DATA_SOURCES)} configured ({ds_created} new)")

        # ─── 7. Deterministic Source Mappings ──────────────
        c_mappings_created = 0
        for c_map in DEFAULT_CROP_SOURCE_MAPPINGS:
            crop_obj = db.query(Crop).filter(Crop.name == c_map["crop"]).first()
            ds_obj = db.query(DataSource).filter(DataSource.code == c_map["source"]).first()
            if crop_obj and ds_obj:
                existing_cm = (
                    db.query(CropSourceMapping)
                    .filter(
                        CropSourceMapping.source_code == c_map["source"],
                        CropSourceMapping.external_code == c_map["code"],
                    )
                    .first()
                )
                if not existing_cm:
                    db.add(
                        CropSourceMapping(
                            crop_id=crop_obj.id,
                            source_id=ds_obj.id,
                            source_code=c_map["source"],
                            external_code=c_map["code"],
                            external_name=c_map["name"],
                            confidence=1.0,
                        )
                    )
                    c_mappings_created += 1

        m_mappings_created = 0
        for m_map in DEFAULT_MARKET_SOURCE_MAPPINGS:
            mkt_obj = db.query(Market).filter(Market.name == m_map["market"]).first()
            ds_obj = db.query(DataSource).filter(DataSource.code == m_map["source"]).first()
            if mkt_obj and ds_obj:
                existing_mm = (
                    db.query(MarketSourceMapping)
                    .filter(
                        MarketSourceMapping.source_code == m_map["source"],
                        MarketSourceMapping.external_code == m_map["code"],
                    )
                    .first()
                )
                if not existing_mm:
                    db.add(
                        MarketSourceMapping(
                            market_id=mkt_obj.id,
                            source_id=ds_obj.id,
                            source_code=m_map["source"],
                            external_code=m_map["code"],
                            external_name=m_map["name"],
                            confidence=1.0,
                        )
                    )
                    m_mappings_created += 1
        db.commit()
        print(f"✓ Source Mappings: {c_mappings_created} crop mappings, {m_mappings_created} market mappings")

        # ─── 8. Verification Assertions ──────────────────
        assert len(TN_DISTRICTS) == 38, f"Configured districts: {len(TN_DISTRICTS)}, expected 38"
        assert len(TIER_A_CROPS) == 20, f"Configured crops: {len(TIER_A_CROPS)}, expected 20"
        total_taluks = sum(len(t) for t in TALUKS_BY_DISTRICT.values())
        assert total_taluks == 25, f"Configured taluks: {total_taluks}, expected 25"
        assert len(PILOT_MARKETS) == 8, f"Configured pilot markets: {len(PILOT_MARKETS)}, expected 8"
        assert len(STATEWIDE_MARKETS) >= 38, f"Configured statewide markets: {len(STATEWIDE_MARKETS)}, expected >= 38"
        assert len(DATA_SOURCES) == 5, f"Configured sources: {len(DATA_SOURCES)}, expected 5"

        db_districts = db.query(District).count()
        db_crops = db.query(Crop).filter(Crop.is_active.is_(True)).count()
        db_taluks = db.query(Taluk).count()
        db_markets = db.query(Market).count()
        db_sources = db.query(DataSource).count()
        distinct_market_districts = db.query(func.count(func.distinct(Market.district_id))).scalar()

        assert db_districts == 38, f"DB districts count {db_districts} != 38"
        assert db_crops >= 20, f"DB active crops count {db_crops} < 20"
        assert db_taluks >= 25, f"DB taluks count {db_taluks} < 25"
        assert db_markets >= 38, f"DB markets count {db_markets} < 38"
        assert db_sources >= 5, f"DB sources count {db_sources} < 5"
        assert distinct_market_districts == 38, f"DB markets must cover all 38 districts, got {distinct_market_districts}"

        print("✓ Verified all reference counts: 38 Districts, 20 Tier-A Crops, 25 Taluks, 43 Markets covering all 38 Districts, 5 Data Sources")
        print("=" * 60)
        print("✓ Statewide Foundation Reference Seed successfully applied & verified!")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"✗ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_statewide()
