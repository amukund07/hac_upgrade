"""
Dadi Ki Baatein — Mega Knowledge Base Scraper v2
=================================================
Sources:
  - Wikipedia API (expanded: 120+ topics)
  - AYUSH Portal (requests + BeautifulSoup)
  - TKDL (Traditional Knowledge Digital Library)
  - PubMed / NCBI Entrez API (scientific abstracts for Ayurvedic herbs)
  - Open Library / Internet Archive (public-domain Ayurvedic texts)
  - Yoga Journal RSS (public yoga content)
  - India.gov.in cultural portals
  - Selenium for JS-rendered sites (indianculture.gov.in etc.)
  - Curated seed data (expanded 50+ entries)
  - Wikidata SPARQL (structured plant/herb data)
  - DBpedia SPARQL (linked data for Indian knowledge systems)

Usage:
  pip install requests beautifulsoup4 lxml tqdm selenium SPARQLWrapper biopython
  python scraper_v2.py --seed-only          # fast test, no network
  python scraper_v2.py --no-selenium        # skip JS sites
  python scraper_v2.py                      # full run (~30 min)
  python scraper_v2.py --pubmed             # also fetch PubMed abstracts
"""

import requests, json, time, re, os, hashlib, logging, argparse, random
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import Optional
from tqdm import tqdm

try:
    from bs4 import BeautifulSoup
    BS4_OK = True
except ImportError:
    BS4_OK = False

try:
    from SPARQLWrapper import SPARQLWrapper, JSON as SPARQL_JSON
    SPARQL_OK = True
except ImportError:
    SPARQL_OK = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    SELENIUM_OK = True
except ImportError:
    SELENIUM_OK = False

# ─────────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()]
)
log = logging.getLogger(__name__)

OUTPUT_DIR = "data/knowledge_base"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "DadiKiBaatein/2.0 Research Project (dadi-ki-baatein-hackathon; contact@example.com)"
}

# ─────────────────────────────────────────────
#  DATA MODEL (expanded)
# ─────────────────────────────────────────────
@dataclass
class KnowledgeEntry:
    id: str = ""
    title: str = ""
    domain: str = ""
    subdomain: str = ""
    dadi_story: str = ""
    summary: str = ""
    raw_content: str = ""
    scientific_backing: list = field(default_factory=list)
    pubmed_abstracts: list = field(default_factory=list)   # NEW: PubMed citations
    health_benefits: list = field(default_factory=list)
    contraindications: list = field(default_factory=list)   # NEW: safety info
    ingredients: list = field(default_factory=list)
    remedy_steps: list = field(default_factory=list)
    yoga_poses: list = field(default_factory=list)
    pranayama_steps: list = field(default_factory=list)     # NEW
    seasonal_relevance: str = ""
    dosha_type: str = ""
    taste_rasa: str = ""                                     # NEW: Ayurvedic taste
    potency_virya: str = ""                                  # NEW: hot/cold potency
    post_digest_vipaka: str = ""                             # NEW: Ayurvedic digestion
    modern_relevance: list = field(default_factory=list)
    keywords: list = field(default_factory=list)
    related_entries: list = field(default_factory=list)     # NEW
    source_url: str = ""
    source_name: str = ""
    language_of_origin: str = "Sanskrit/Hindi"
    regional_names: dict = field(default_factory=dict)      # NEW: Hindi/Tamil/Telugu names
    scraped_at: str = ""
    authenticity_score: float = 0.0
    gen_z_hook: str = ""
    data_source_type: str = ""
    wikidata_qid: str = ""                                   # NEW: Wikidata entity ID
    image_url: str = ""                                      # NEW

# ─────────────────────────────────────────────
#  EXPANDED WIKIPEDIA TOPICS (120+)
# ─────────────────────────────────────────────
WIKIPEDIA_TOPICS = [
    # ── Ayurvedic Systems & Texts ─────────────────────────────────────
    ("Ayurveda",                    "Ayurveda",          "Overview"),
    ("Dosha",                       "Ayurveda",          "Tridosha Theory"),
    ("Panchakarma",                 "Ayurveda",          "Detox Therapies"),
    ("Dinacharya",                  "Ayurveda",          "Daily Routine"),
    ("Rasayana (Ayurveda)",         "Ayurveda",          "Rejuvenation"),
    ("Charaka Samhita",             "Ancient Texts",     "Classical Texts"),
    ("Sushruta Samhita",            "Ancient Texts",     "Classical Texts"),
    ("Ashtanga Hridayam",           "Ancient Texts",     "Classical Texts"),
    ("Ashtanga Hridaya",            "Ancient Texts",     "Classical Texts"),
    ("Dhanvantari",                 "Ancient Texts",     "Deity of Medicine"),
    ("Vagbhata",                    "Ancient Texts",     "Classical Authors"),
    ("Charaka",                     "Ancient Texts",     "Classical Authors"),
    ("Sushruta",                    "Ancient Texts",     "Classical Authors"),
    ("Rtucharya",                   "Ayurveda",          "Seasonal Regimen"),
    ("Sattvavajaya",                "Ayurveda",          "Psychotherapy"),
    ("Panchamahabhuta",             "Ayurveda",          "Five Elements"),
    ("Agni (Ayurveda)",             "Ayurveda",          "Digestive Fire"),
    ("Ama (Ayurveda)",              "Ayurveda",          "Metabolic Toxins"),
    ("Ojas",                        "Ayurveda",          "Vital Essence"),
    ("Prana",                       "Yoga",              "Life Force"),
    ("Dhatu (Ayurveda)",            "Ayurveda",          "Body Tissues"),
    ("Srotas",                      "Ayurveda",          "Bodily Channels"),

    # ── Medicinal Herbs & Plants ──────────────────────────────────────
    ("Withania somnifera",          "Ayurveda",          "Ashwagandha"),
    ("Ocimum tenuiflorum",          "Ayurveda",          "Tulsi"),
    ("Turmeric",                    "Ayurveda",          "Haldi"),
    ("Azadirachta indica",          "Ayurveda",          "Neem"),
    ("Triphala",                    "Ayurveda",          "Herbal Formulas"),
    ("Phyllanthus emblica",         "Ayurveda",          "Amla"),
    ("Tinospora cordifolia",        "Ayurveda",          "Giloy"),
    ("Bacopa monnieri",             "Ayurveda",          "Brahmi"),
    ("Zingiber officinale",         "Ayurveda",          "Ginger"),
    ("Curcumin",                    "Ayurveda",          "Active Compounds"),
    ("Moringa oleifera",            "Ayurveda",          "Drumstick Tree"),
    ("Shatavari",                   "Ayurveda",          "Women's Health"),
    ("Nigella sativa",              "Ayurveda",          "Kalonji"),
    ("Centella asiatica",           "Ayurveda",          "Gotu Kola"),
    ("Terminalia chebula",          "Ayurveda",          "Haritaki"),
    ("Terminalia bellirica",        "Ayurveda",          "Bibhitaki"),
    ("Mucuna pruriens",             "Ayurveda",          "Kaunch Beej"),
    ("Commiphora wightii",          "Ayurveda",          "Guggul"),
    ("Boswellia serrata",           "Ayurveda",          "Shallaki"),
    ("Gymnema sylvestre",           "Ayurveda",          "Gurmar"),
    ("Andrographis paniculata",     "Ayurveda",          "Kalmegh"),
    ("Emblica officinalis",         "Ayurveda",          "Amla"),
    ("Aloe vera",                   "Ayurveda",          "Ghritkumari"),
    ("Fenugreek",                   "Ayurveda",          "Methi"),
    ("Coriander",                   "Ayurveda",          "Dhaniya"),
    ("Cumin",                       "Ayurveda",          "Jeera"),
    ("Cardamom",                    "Ayurveda",          "Elaichi"),
    ("Cinnamon",                    "Ayurveda",          "Dalchini"),
    ("Clove",                       "Ayurveda",          "Laung"),
    ("Piper longum",                "Ayurveda",          "Pippali"),
    ("Black pepper",                "Ayurveda",          "Kali Mirch"),
    ("Garlic",                      "Ayurveda",          "Lahsun"),
    ("Sesame",                      "Ayurveda",          "Til"),
    ("Ashoka tree",                 "Ayurveda",          "Ashoka"),
    ("Senna (plant)",               "Ayurveda",          "Senna"),
    ("Castor oil plant",            "Ayurveda",          "Arandi"),
    ("Calotropis gigantea",         "Ayurveda",          "Ak"),
    ("Acorus calamus",              "Ayurveda",          "Vacha"),
    ("Tribulus terrestris",         "Ayurveda",          "Gokshura"),
    ("Asparagus racemosus",         "Ayurveda",          "Shatavari Herb"),
    ("Stevia",                      "Ayurveda",          "Natural Sweeteners"),
    ("Nardostachys jatamansi",      "Ayurveda",          "Jatamansi"),
    ("Punica granatum",             "Ayurveda",          "Pomegranate"),
    ("Aegle marmelos",              "Ayurveda",          "Bael"),
    ("Solanum nigrum",              "Ayurveda",          "Kakamachi"),
    ("Plumbago zeylanica",          "Ayurveda",          "Chitraka"),

    # ── Yoga & Pranayama ─────────────────────────────────────────────
    ("Yoga",                        "Yoga",              "Overview"),
    ("Pranayama",                   "Yoga",              "Breathing Techniques"),
    ("Surya Namaskar",              "Yoga",              "Sequences"),
    ("Hatha yoga",                  "Yoga",              "Physical Yoga"),
    ("Kundalini yoga",              "Yoga",              "Energy Yoga"),
    ("Ashtanga vinyasa yoga",       "Yoga",              "Dynamic Yoga"),
    ("Iyengar yoga",                "Yoga",              "Alignment Yoga"),
    ("Bikram yoga",                 "Yoga",              "Hot Yoga"),
    ("Yin yoga",                    "Yoga",              "Restorative Yoga"),
    ("Chakra",                      "Yoga",              "Energy Centers"),
    ("Mudra",                       "Yoga",              "Hand Gestures"),
    ("Meditation",                  "Yoga",              "Dhyana"),
    ("Vipassanā",                   "Yoga",              "Meditation"),
    ("Yoga nidra",                  "Yoga",              "Yogic Sleep"),
    ("Bandha (yoga)",               "Yoga",              "Energy Locks"),
    ("Trataka",                     "Yoga",              "Yogic Gazing"),
    ("Neti pot",                    "Yoga",              "Shatkarma"),
    ("Shatkarma",                   "Yoga",              "Six Purifications"),
    ("Yoga Sutras of Patanjali",    "Yoga",              "Classical Texts"),
    ("Bhagavad Gita",               "Ancient Texts",     "Spiritual Texts"),
    ("Samkhya",                     "Ancient Texts",     "Philosophy"),
    ("Ashtanga yoga",               "Yoga",              "Eight Limbs"),
    ("Yamas and Niyamas",           "Yoga",              "Ethical Practices"),
    ("Pratyahara",                  "Yoga",              "Sense Withdrawal"),
    ("Dharana",                     "Yoga",              "Concentration"),
    ("Samadhi in Hinduism",         "Yoga",              "Enlightenment"),

    # ── Indian Medicine Systems ───────────────────────────────────────
    ("Siddha medicine",             "Siddha",            "Overview"),
    ("Unani medicine",              "Unani",             "Overview"),
    ("Naturopathy",                 "Naturopathy",       "Overview"),
    ("Marma (Ayurveda)",            "Ayurveda",          "Vital Points"),
    ("Kalaripayattu",               "Traditional Martial Arts", "Kerala"),

    # ── Food, Spices & Culture ───────────────────────────────────────
    ("Indian cuisine",              "Food & Culture",    "Overview"),
    ("Ghee",                        "Food & Culture",    "Sacred Foods"),
    ("Sattvic diet",                "Food & Culture",    "Ayurvedic Diet"),
    ("Fermentation in food processing","Food & Culture", "Preservation"),
    ("Spice",                       "Food & Culture",    "Spice Knowledge"),
    ("Fasting",                     "Food & Culture",    "Ritualistic Practices"),
    ("Chyawanprash",                "Ayurveda",          "Classical Formulas"),
    ("Kadha (drink)",               "Home Remedies",     "Decoctions"),
    ("Rasam",                       "Food & Culture",    "Traditional Foods"),
    ("Dal (dish)",                  "Food & Culture",    "Traditional Foods"),
    ("Khichdi",                     "Food & Culture",    "Traditional Foods"),
    ("Tamarind",                    "Food & Culture",    "Sour Spices"),
    ("Asafoetida",                  "Food & Culture",    "Hing"),
    ("Amchur",                      "Food & Culture",    "Dried Mango Powder"),
    ("Paneer",                      "Food & Culture",    "Dairy"),
    ("Lassi",                       "Food & Culture",    "Probiotic Drinks"),
    ("Idli",                        "Food & Culture",    "Fermented Foods"),
    ("Dosa",                        "Food & Culture",    "Fermented Foods"),
    ("Chapati",                     "Food & Culture",    "Traditional Breads"),

    # ── Sustainable Farming ──────────────────────────────────────────
    ("Zero Budget Natural Farming", "Sustainable Farming","Modern Methods"),
    ("Organic farming",             "Sustainable Farming","Overview"),
    ("Biodynamic agriculture",      "Sustainable Farming","Holistic Farming"),
    ("Crop rotation",               "Sustainable Farming","Soil Health"),
    ("Agroforestry",                "Sustainable Farming","Traditional Systems"),
    ("Permaculture",                "Sustainable Farming","Design Methods"),
    ("Vermicompost",                "Sustainable Farming","Soil Health"),
    ("Intercropping",               "Sustainable Farming","Traditional Techniques"),
    ("Sacred grove",                "Sustainable Farming","Conservation"),
    ("Water harvesting",            "Sustainable Farming","Water Management"),

    # ── Ancient Astronomy & Mathematics ─────────────────────────────
    ("Hindu astrology",             "Ancient Astronomy", "Jyotisha"),
    ("Indian mathematics",          "Vedic Mathematics", "Overview"),
    ("Aryabhata",                   "Ancient Astronomy", "Ancient Scholars"),
    ("Brahmagupta",                 "Vedic Mathematics", "Ancient Scholars"),
    ("Vedic Mathematics",           "Vedic Mathematics", "Modern Vedic Math"),
    ("Indian astronomy",            "Ancient Astronomy", "Overview"),
    ("Surya Siddhanta",             "Ancient Astronomy", "Classical Texts"),
    ("Aryabhatiya",                 "Ancient Astronomy", "Classical Texts"),
    ("Varahamihira",                "Ancient Astronomy", "Ancient Scholars"),
    ("Bhaskara I",                  "Vedic Mathematics", "Ancient Scholars"),
    ("Madhava of Sangamagrama",     "Vedic Mathematics", "Kerala School"),

    # ── Arts, Culture & Oral History ─────────────────────────────────
    ("Panchang",                    "Oral History",      "Calendar System"),
    ("Rangoli",                     "Arts & Culture",    "Folk Arts"),
    ("Indian classical dance",      "Arts & Culture",    "Performing Arts"),
    ("Carnatic music",              "Arts & Culture",    "Music Tradition"),
    ("Oral tradition",              "Oral History",      "Storytelling"),
    ("Folklore of India",           "Oral History",      "Folk Stories"),
    ("Bharatanatyam",               "Arts & Culture",    "Classical Dance"),
    ("Kathak",                      "Arts & Culture",    "Classical Dance"),
    ("Kuchipudi",                   "Arts & Culture",    "Classical Dance"),
    ("Natyashastra",                "Arts & Culture",    "Classical Texts"),
    ("Ramayana",                    "Oral History",      "Epic Literature"),
    ("Mahabharata",                 "Oral History",      "Epic Literature"),
    ("Panchatantra",                "Oral History",      "Fables"),
    ("Jataka tales",                "Oral History",      "Buddhist Stories"),
    ("Vedas",                       "Ancient Texts",     "Sacred Texts"),
    ("Upanishads",                  "Ancient Texts",     "Philosophy"),
    ("Puranas",                     "Ancient Texts",     "Mythological Texts"),
]

# ─────────────────────────────────────────────
#  PUBMED QUERIES (Ayurvedic research)
# ─────────────────────────────────────────────
PUBMED_QUERIES = [
    "Ashwagandha withania somnifera clinical trial",
    "Turmeric curcumin anti-inflammatory randomized",
    "Brahmi Bacopa monnieri memory cognition",
    "Tulsi ocimum tenuiflorum adaptogen",
    "Triphala antioxidant clinical study",
    "Giloy tinospora cordifolia immunity",
    "Neem azadirachta antibacterial skin",
    "Shatavari asparagus racemosus women health",
    "Ayurvedic medicine systematic review",
    "Yoga pranayama blood pressure randomized",
    "Meditation anxiety depression clinical trial",
    "Kapalbhati breathing exercise metabolic",
    "Surya namaskar cardiovascular exercise",
    "Indian traditional medicine cancer",
    "Amla Phyllanthus emblica vitamin C",
    "Guggul Commiphora cholesterol",
    "Boswellia serrata arthritis inflammation",
    "Ginger zingiber nausea inflammation",
    "Black pepper piperine bioavailability",
    "Moringa oleifera nutrition review",
]

# ─────────────────────────────────────────────
#  AYUSH PORTAL URLS
# ─────────────────────────────────────────────
AYUSH_URLS = [
    {"url": "https://main.ayush.gov.in/ayurveda",          "domain": "Ayurveda",  "name": "AYUSH Ayurveda"},
    {"url": "https://main.ayush.gov.in/yoga-naturopathy",  "domain": "Yoga",      "name": "AYUSH Yoga"},
    {"url": "https://main.ayush.gov.in/unani",             "domain": "Unani",     "name": "AYUSH Unani"},
    {"url": "https://main.ayush.gov.in/siddha",            "domain": "Siddha",    "name": "AYUSH Siddha"},
    {"url": "https://main.ayush.gov.in/homeopathy",        "domain": "Homeopathy","name": "AYUSH Homeopathy"},
]

# ─────────────────────────────────────────────
#  STATIC SCRAPEABLE SITES (requests + BS4)
# ─────────────────────────────────────────────
STATIC_SITES = [
    {
        "name": "NLM Ayurveda Overview",
        "url":  "https://www.ncbi.nlm.nih.gov/books/NBK92764/",
        "domain": "Ayurveda",
        "selectors": ["div.content", "article", "section"],
    },
    {
        "name": "NLM Yoga Overview",
        "url":  "https://www.ncbi.nlm.nih.gov/books/NBK92754/",
        "domain": "Yoga",
        "selectors": ["div.content", "article", "section"],
    },
    {
        "name": "NCCIH Ayurvedic Medicine",
        "url":  "https://www.nccih.nih.gov/health/ayurvedic-medicine-in-depth",
        "domain": "Ayurveda",
        "selectors": ["main", "article", "#content"],
    },
    {
        "name": "NCCIH Yoga",
        "url":  "https://www.nccih.nih.gov/health/yoga-what-you-need-to-know",
        "domain": "Yoga",
        "selectors": ["main", "article", "#content"],
    },
    {
        "name": "NCCIH Meditation",
        "url":  "https://www.nccih.nih.gov/health/meditation-in-depth",
        "domain": "Yoga",
        "selectors": ["main", "article", "#content"],
    },
    {
        "name": "Yoga Journal — Pranayama",
        "url":  "https://www.yogajournal.com/practice/pranayama/",
        "domain": "Yoga",
        "selectors": ["article", "main", ".entry-content"],
    },
    {
        "name": "Yoga Journal — Poses",
        "url":  "https://www.yogajournal.com/poses/",
        "domain": "Yoga",
        "selectors": ["article", "main", ".entry-content"],
    },
    {
        "name": "Healthline Ayurveda",
        "url":  "https://www.healthline.com/nutrition/ayurveda",
        "domain": "Ayurveda",
        "selectors": ["article", ".article-body", "main"],
    },
    {
        "name": "Healthline Ashwagandha",
        "url":  "https://www.healthline.com/nutrition/ashwagandha",
        "domain": "Ayurveda",
        "selectors": ["article", ".article-body", "main"],
    },
    {
        "name": "Healthline Turmeric",
        "url":  "https://www.healthline.com/nutrition/top-10-evidence-based-health-benefits-of-turmeric",
        "domain": "Ayurveda",
        "selectors": ["article", ".article-body", "main"],
    },
    {
        "name": "Healthline Brahmi",
        "url":  "https://www.healthline.com/health/bacopa-monnieri",
        "domain": "Ayurveda",
        "selectors": ["article", ".article-body", "main"],
    },
    {
        "name": "Healthline Neem",
        "url":  "https://www.healthline.com/health/neem-oil",
        "domain": "Ayurveda",
        "selectors": ["article", ".article-body", "main"],
    },
    {
        "name": "Healthline Moringa",
        "url":  "https://www.healthline.com/nutrition/6-benefits-of-moringa-oleifera",
        "domain": "Ayurveda",
        "selectors": ["article", ".article-body", "main"],
    },
    {
        "name": "Healthline Amla",
        "url":  "https://www.healthline.com/nutrition/amla-benefits",
        "domain": "Ayurveda",
        "selectors": ["article", ".article-body", "main"],
    },
    {
        "name": "Healthline Tulsi",
        "url":  "https://www.healthline.com/health/food-nutrition/basil",
        "domain": "Ayurveda",
        "selectors": ["article", ".article-body", "main"],
    },
    {
        "name": "Healthline Triphala",
        "url":  "https://www.healthline.com/health/triphala",
        "domain": "Ayurveda",
        "selectors": ["article", ".article-body", "main"],
    },
    {
        "name": "Healthline Ghee",
        "url":  "https://www.healthline.com/nutrition/ghee",
        "domain": "Food & Culture",
        "selectors": ["article", ".article-body", "main"],
    },
    {
        "name": "WebMD Ayurveda",
        "url":  "https://www.webmd.com/balance/guide/ayurvedic-treatments",
        "domain": "Ayurveda",
        "selectors": ["article", ".article-body", "main", "#main-content"],
    },
    {
        "name": "WebMD Meditation",
        "url":  "https://www.webmd.com/balance/video/meditation-benefits",
        "domain": "Yoga",
        "selectors": ["article", ".article-body", "main", "#main-content"],
    },
    {
        "name": "Wikipedia Chyawanprash",
        "url":  "https://en.wikipedia.org/wiki/Chyawanprash",
        "domain": "Ayurveda",
        "selectors": ["#mw-content-text"],
    },
    {
        "name": "Wikipedia Panchakarma",
        "url":  "https://en.wikipedia.org/wiki/Panchakarma",
        "domain": "Ayurveda",
        "selectors": ["#mw-content-text"],
    },
]

# ─────────────────────────────────────────────
#  JS-RENDERED SITES (Selenium)
# ─────────────────────────────────────────────
JS_SITES = [
    {"name": "Indian Cultural Portal — Ayurveda",
     "url":  "https://www.indianculture.gov.in/ayurveda",
     "domain": "Ayurveda"},
    {"name": "Indian Cultural Portal — Yoga",
     "url":  "https://www.indianculture.gov.in/yoga",
     "domain": "Yoga"},
    {"name": "Indian Cultural Portal — Knowledge Systems",
     "url":  "https://www.indianculture.gov.in/indian-knowledge-systems",
     "domain": "Traditional Knowledge"},
    {"name": "Indian Cultural Portal — Performing Arts",
     "url":  "https://www.indianculture.gov.in/performing-arts",
     "domain": "Arts & Culture"},
    {"name": "Indian Cultural Portal — Manuscripts",
     "url":  "https://www.indianculture.gov.in/manuscripts",
     "domain": "Ancient Texts"},
    {"name": "AYUSH Ayurveda",
     "url":  "https://main.ayush.gov.in/ayurveda",
     "domain": "Ayurveda"},
    {"name": "AYUSH Yoga & Naturopathy",
     "url":  "https://main.ayush.gov.in/yoga-naturopathy",
     "domain": "Yoga"},
    {"name": "TKDL Traditional Knowledge",
     "url":  "https://www.tkdl.res.in/tkdl/langdefault/common/Home.asp?GL=Eng",
     "domain": "Traditional Knowledge"},
    {"name": "Yoga MDNIY",
     "url":  "https://www.yogamdniy.nic.in/",
     "domain": "Yoga"},
    {"name": "National Digital Library",
     "url":  "https://ndl.iitkgp.ac.in/",
     "domain": "Ancient Texts"},
    {"name": "Indira Gandhi National Centre for Arts",
     "url":  "https://www.ignca.gov.in/",
     "domain": "Arts & Culture"},
    {"name": "India — Cultural Heritage",
     "url":  "https://www.india.gov.in/topics/culture-tourism",
     "domain": "Arts & Culture"},
    {"name": "Archaeological Survey of India",
     "url":  "https://asi.nic.in/",
     "domain": "Ancient Texts"},
]

# ─────────────────────────────────────────────
#  MASSIVELY EXPANDED SEED KNOWLEDGE BASE (50+)
# ─────────────────────────────────────────────
SEED_KNOWLEDGE = [
    # ── HOME REMEDIES ─────────────────────────────────────────────────
    {
        "title": "Turmeric Milk (Haldi Doodh) — Golden Milk",
        "domain": "Home Remedies", "subdomain": "Immunity & Cold",
        "summary": "A warm drink made with turmeric, milk, black pepper, and honey. Used for centuries to boost immunity, reduce inflammation, and aid sleep. The piperine in black pepper increases curcumin absorption by 2000%.",
        "ingredients": ["Turmeric", "Milk", "Black Pepper", "Honey", "Ginger"],
        "remedy_steps": [
            "Heat 1 cup of milk (dairy or plant-based) until warm but not boiling",
            "Add 1/2 tsp turmeric powder and a pinch of black pepper",
            "Add a small piece of fresh ginger or 1/4 tsp ginger powder",
            "Stir well and simmer for 2 minutes",
            "Remove from heat, add 1 tsp honey after cooling slightly",
            "Drink warm before bedtime for best results"
        ],
        "health_benefits": ["Immunity", "Inflammation", "Sleep", "Joint Pain", "Digestion"],
        "contraindications": ["Avoid excess during pregnancy", "May interact with blood thinners in high doses"],
        "scientific_backing": [
            "Curcumin: Potent anti-inflammatory and antioxidant (Aggarwal et al., 2007)",
            "Piperine increases curcumin bioavailability by up to 2000% (Shoba et al., 1998)",
        ],
        "dosha_type": "All doshas (tridoshic)",
        "taste_rasa": "Bitter, Pungent",
        "potency_virya": "Heating",
        "seasonal_relevance": "Winter",
        "modern_relevance": ["Immunity Boosting", "Anti-aging", "Sleep Wellness"],
        "regional_names": {"Hindi": "Haldi Doodh", "Tamil": "Manjal Paal", "Telugu": "Pasupu Palu"},
        "gen_z_hook": "Golden Milk trended on TikTok in 2020. Your dadi made it in 1960. Zero lag. 🌟",
        "keywords": ["turmeric", "curcumin", "haldi", "golden milk", "immunity", "inflammation"],
        "source_name": "TKDL / Traditional Ayurvedic Knowledge",
        "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Ginger Honey Lemon Tea — Cold & Flu First Aid",
        "domain": "Home Remedies", "subdomain": "Respiratory Health",
        "summary": "A trio that combines gingerol's anti-inflammatory power, honey's antibacterial properties, and lemon's vitamin C. Used as first-line treatment for colds, sore throats, and digestive distress across India for millennia.",
        "ingredients": ["Fresh Ginger", "Honey", "Lemon", "Water", "Tulsi (optional)"],
        "remedy_steps": [
            "Boil 2 cups water with 1-inch grated fresh ginger for 5 minutes",
            "Add juice of half a lemon",
            "Strain into a cup",
            "Let cool to warm temperature (below 40°C)",
            "Add 1 tsp raw honey (never add honey to boiling water)",
            "Drink 2-3 times daily at first sign of cold"
        ],
        "health_benefits": ["Cold", "Sore Throat", "Digestion", "Nausea", "Immunity"],
        "scientific_backing": [
            "Gingerol: Antiviral and anti-inflammatory (Chang et al., 2013)",
            "Honey: Antibacterial via hydrogen peroxide and bee defensin-1",
            "Vitamin C (lemon): Supports neutrophil function and immune response",
        ],
        "dosha_type": "Kapha, Vata",
        "seasonal_relevance": "Winter, Monsoon",
        "modern_relevance": ["Immunity Boosting", "Gut Health"],
        "regional_names": {"Hindi": "Adrak Shahad Nimbu Chai", "Tamil": "Inji Theneer"},
        "gen_z_hook": "3 ingredients, costs ₹5, destroys cold symptoms. No prescription needed. 💪",
        "keywords": ["ginger", "honey", "lemon", "cold", "flu", "sore throat", "gingerol"],
        "source_name": "Traditional Knowledge",
        "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Jeera Water (Cumin Water) — Digestive Miracle",
        "domain": "Home Remedies", "subdomain": "Digestive Health",
        "summary": "Jeera (cumin) water is one of the most common Ayurvedic morning rituals for digestive health. It stimulates digestive enzymes, reduces bloating, and is a potent iron source. Recommended in Charaka Samhita for enhancing Agni (digestive fire).",
        "ingredients": ["Cumin Seeds", "Water"],
        "remedy_steps": [
            "Soak 1 tsp cumin seeds in 1 glass of water overnight",
            "In the morning, boil the soaked seeds for 5 minutes",
            "Strain and drink warm on empty stomach",
            "Alternative: Dry roast cumin, crush, mix in warm water with pinch of salt",
            "For weight loss: add 1/4 tsp turmeric and pinch of black pepper",
            "Drink consistently for 3-4 weeks to see digestive benefits"
        ],
        "health_benefits": ["Digestion", "Bloating", "IBS", "Iron Deficiency", "Weight", "Acidity"],
        "scientific_backing": [
            "Thymoquinone and cuminaldehyde: Stimulate digestive enzyme secretion",
            "High iron content: ~66mg per 100g, highest in common spices",
            "Antiflatulent: Reduces abdominal gas by inhibiting fermentation bacteria",
        ],
        "dosha_type": "Vata, Kapha",
        "taste_rasa": "Pungent, Bitter",
        "potency_virya": "Heating",
        "seasonal_relevance": "All seasons",
        "modern_relevance": ["Gut Health", "Weight Management", "Detox"],
        "regional_names": {"Hindi": "Jeera Paani", "Tamil": "Jeeragam Tanneer"},
        "gen_z_hook": "Your gut microbiome will thank you. Free probiotic ritual since 3000 BCE. 🌿",
        "keywords": ["jeera", "cumin", "digestion", "bloating", "agni", "ayurveda", "morning ritual"],
        "source_name": "Charaka Samhita",
        "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Neem Datun — Natural Toothbrush",
        "domain": "Home Remedies", "subdomain": "Oral Health",
        "summary": "Chewing neem twigs as a toothbrush is documented across Ayurvedic texts and is still used in rural India. Nimbin, nimbidin, and eugenol in neem are more effective against Streptococcus mutans (the cavity bacterium) than commercial fluoride toothpastes in several studies.",
        "ingredients": ["Fresh Neem Twig (pencil-thin)"],
        "remedy_steps": [
            "Select a fresh neem twig about the width of a pencil and 15cm long",
            "Wash thoroughly and chew one end for 2-3 minutes until fibres fray like bristles",
            "Use frayed end to brush teeth and gums with gentle circular motions",
            "Chew the twig as you brush — the sap is the active ingredient",
            "Use daily in the morning for 10-15 minutes",
            "Discard after use — each twig is single-use"
        ],
        "health_benefits": ["Dental", "Gum Disease", "Cavity Prevention", "Oral Bacteria", "Bad Breath"],
        "scientific_backing": [
            "Nimbidin: Antibacterial against S. mutans and S. sanguis (Pai et al., 2004)",
            "Eugenol: Anti-inflammatory for gum tissue",
            "WHO recommends neem twigs in countries where toothbrushes are unavailable",
        ],
        "dosha_type": "Pitta, Kapha",
        "seasonal_relevance": "All seasons",
        "modern_relevance": ["Oral Health", "Sustainability", "Zero Waste"],
        "regional_names": {"Hindi": "Neem Datun", "Tamil": "Veppilai Toothu Kuchi"},
        "gen_z_hook": "WHO literally recommends this. Colgate should be nervous. 🌳",
        "keywords": ["neem", "datun", "dental", "oral health", "cavity", "natural toothbrush"],
        "source_name": "WHO + Ayurvedic Texts",
        "source_url": "https://www.who.int/oral_health/",
    },
    {
        "title": "Mustard Oil Massage for Infants (Sarson Tel Malish)",
        "domain": "Home Remedies", "subdomain": "Infant Care",
        "summary": "The tradition of daily warm mustard oil massage for newborns and infants is deeply embedded in Indian culture. Modern research confirms it improves weight gain, reduces pain responses, and promotes neurological development through touch stimulation.",
        "ingredients": ["Cold-Pressed Mustard Oil", "Garlic (optional, 2 cloves infused)"],
        "remedy_steps": [
            "Warm cold-pressed mustard oil gently (test on wrist)",
            "For infants: 15 minutes daily massage, covering the full body",
            "Use gentle pressure with fingertips — not palms — for newborns",
            "Massage in direction of hair growth",
            "Allow 20 minutes before bathing",
            "For adults: weekly deep muscle massage, especially in winter"
        ],
        "health_benefits": ["Weight Gain (Infants)", "Bone Strength", "Circulation", "Skin", "Joint Pain"],
        "scientific_backing": [
            "RCT showed 30% better weight gain in mustard oil vs. mineral oil massage (Field et al.)",
            "Erucic acid in mustard oil: transdermal penetration aids deep tissue warming",
            "Allyl isothiocyanate: antimicrobial protection on infant skin",
        ],
        "dosha_type": "Vata",
        "seasonal_relevance": "Winter",
        "modern_relevance": ["Infant Care", "Skincare"],
        "regional_names": {"Hindi": "Sarson Tel Malish", "Punjabi": "Sarsoun Da Tel"},
        "gen_z_hook": "Clinical trials confirmed what dadi knew. Touch therapy for babies = neurological gold. 👶",
        "keywords": ["mustard oil", "infant massage", "malish", "newborn", "weight gain", "ayurveda"],
        "source_name": "Traditional Knowledge + Pediatric Studies",
        "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Clove Oil for Toothache — Emergency Dentistry",
        "domain": "Home Remedies", "subdomain": "Pain Relief",
        "summary": "Clove oil (Syzygium aromaticum) is the original dental anaesthetic. Eugenol, its primary compound, is still used by dentists as a topical anaesthetic and in zinc oxide eugenol cement. Ayurvedic practitioners have used it for toothache relief for over 2000 years.",
        "ingredients": ["Clove Oil", "Cotton Ball", "Coconut Oil (carrier)"],
        "remedy_steps": [
            "Dilute 1 drop of clove oil in 1/4 tsp coconut oil (never apply neat)",
            "Dip a small cotton ball in the diluted mixture",
            "Apply directly to the affected tooth and surrounding gum",
            "Hold in place for 5-10 minutes",
            "Repeat up to 4 times daily as needed",
            "Do NOT swallow — spit out after use",
            "Seek dental care — this is temporary relief only"
        ],
        "health_benefits": ["Toothache", "Dental Pain", "Gum Inflammation", "Oral Bacteria"],
        "contraindications": ["Never apply neat — can burn mucous membranes", "Avoid during pregnancy", "Dilute for children"],
        "scientific_backing": [
            "Eugenol: Local anaesthetic (reversible Na+ channel blockade)",
            "Active ingredient in ZOE cement used in modern dentistry",
            "Antibacterial against E. faecalis in root canals",
        ],
        "dosha_type": "Kapha, Vata",
        "modern_relevance": ["Oral Health", "Pain Relief"],
        "regional_names": {"Hindi": "Laung Tel", "Tamil": "Kirambu Ennai"},
        "gen_z_hook": "The same molecule your dentist uses in a ₹5 clove. Big Pharma hates this. 🦷",
        "keywords": ["clove", "eugenol", "toothache", "dental", "pain", "laung", "oil"],
        "source_name": "Charaka Samhita + Modern Dentistry",
        "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Aloe Vera (Ghritkumari) — Skin & Gut Healer",
        "domain": "Home Remedies", "subdomain": "Skin Health",
        "summary": "Aloe vera is called Ghritkumari in Sanskrit ('the plant that is oily like ghee and has properties of a young girl'). Its gel contains over 75 bioactive compounds including vitamins A, C, E, B12, folic acid, and choline. Used topically for burns, wounds, and acne, and internally for constipation and gut health.",
        "ingredients": ["Fresh Aloe Vera Leaf", "Water (for internal use)", "Honey (optional)"],
        "remedy_steps": [
            "Cut a mature aloe leaf close to the stem",
            "Wash and let yellow latex (aloin) drain out for 10 minutes — this is laxative and can cause cramps",
            "Cut leaf open and scoop clear gel",
            "For burns/wounds: apply gel directly to affected area, leave uncovered",
            "For skin: mix gel with rose water 1:1, apply as face mask",
            "For internal use: 1-2 tbsp fresh gel in 1 cup water with honey daily",
            "For constipation: aloe juice (with latex) — use cautiously, max 7 days"
        ],
        "health_benefits": ["Burns", "Wounds", "Acne", "Constipation", "Gut Health", "Skin Hydration"],
        "contraindications": ["Yellow latex (aloin) causes diarrhoea — drain before use", "Avoid internal use in pregnancy"],
        "scientific_backing": [
            "Acemannan: Immunostimulant polysaccharide, promotes wound healing",
            "Anthraquinones: Laxative effect via colon stimulation (for constipation)",
            "Anti-inflammatory: Inhibits COX-2 and TNF-alpha",
        ],
        "dosha_type": "Pitta, Vata",
        "taste_rasa": "Bitter, Astringent",
        "seasonal_relevance": "Summer",
        "modern_relevance": ["Skincare", "Gut Health", "Beauty"],
        "regional_names": {"Hindi": "Ghritkumari", "Tamil": "Katralai", "Telugu": "Kalabanda"},
        "gen_z_hook": "The ₹30 plant in your balcony outperforms ₹3000 burn creams. No cap. 🌵",
        "keywords": ["aloe vera", "ghritkumari", "gel", "burns", "skin", "acemannan", "wounds"],
        "source_name": "Ayurvedic Nighantus + Modern Dermatology",
        "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Triphala Eye Wash — Ancient Ophthalmology",
        "domain": "Home Remedies", "subdomain": "Eye Health",
        "summary": "Triphala as an eye wash is documented in Sushruta Samhita — the world's oldest surgical text. It is used for reducing eye strain, conjunctivitis, and improving vision. Modern research shows its antioxidant compounds protect the retina from oxidative damage.",
        "ingredients": ["Triphala Powder", "Distilled Water or Boiled Cooled Water"],
        "remedy_steps": [
            "Boil 1 cup water and let cool completely to room temperature",
            "Add 1/4 tsp Triphala powder and stir well",
            "Let settle for 10 minutes, then strain through very fine cloth or coffee filter — NO particles",
            "Wash eyes with the clear liquid using an eye cup twice daily",
            "Alternatively use as an eyedrop: 2-3 drops per eye",
            "Use fresh preparation daily — do not store for more than 24 hours"
        ],
        "health_benefits": ["Eye Strain", "Conjunctivitis", "Vision", "Eye Dryness", "Digital Eye Fatigue"],
        "contraindications": ["Must be particle-free before use", "Stop if irritation increases", "Not for contact lens wearers"],
        "scientific_backing": [
            "Ellagic acid in Amla: Protects retinal cells from oxidative stress",
            "Anti-inflammatory: Reduces conjunctival inflammation markers",
            "Antibacterial: Effective against Staphylococcus epidermidis",
        ],
        "dosha_type": "Pitta (especially for eye issues)",
        "seasonal_relevance": "All seasons (especially for screen fatigue)",
        "modern_relevance": ["Digital Eye Strain", "Eye Health", "Screen Wellness"],
        "gen_z_hook": "You've been staring at a screen for 8 hours. Your ancestors had a fix for that. 👁️",
        "keywords": ["triphala", "eye wash", "conjunctivitis", "vision", "eye strain", "sushruta"],
        "source_name": "Sushruta Samhita",
        "source_url": "https://www.tkdl.res.in",
    },
    # ── YOGA ──────────────────────────────────────────────────────────
    {
        "title": "Kapalbhati Pranayama — Skull-Shining Breath",
        "domain": "Yoga", "subdomain": "Pranayama",
        "summary": "Kapalbhati is a powerful Hatha Yoga breathing technique where emphasis is on forceful exhalations. 'Kapal' means skull, 'bhati' means shining. Regular practice boosts metabolism, strengthens the core, and activates the parasympathetic nervous system.",
        "ingredients": [],
        "remedy_steps": [
            "Sit in Padmasana or Sukhasana with spine erect",
            "Take a deep inhale to prepare",
            "Exhale sharply through the nose by sharply contracting the abdomen inward",
            "Allow inhalation to happen passively as abdomen releases",
            "Start with 30 rounds, build gradually to 120 rounds per minute",
            "Do 3-5 sets with 1 minute rest between each set",
            "Best practised on empty stomach early morning",
            "AVOID if pregnant, hypertensive, have recent abdominal surgery, or hernias"
        ],
        "yoga_poses": ["Kapalbhati", "Padmasana", "Sukhasana"],
        "health_benefits": ["Digestion", "Weight", "Metabolism", "Lungs", "Energy", "Stress", "Skin"],
        "contraindications": ["Pregnancy", "Hypertension", "Recent abdominal surgery", "Hernia", "Epilepsy"],
        "scientific_backing": [
            "Improves FEV1 and peak expiratory flow rate (pulmonary studies)",
            "Activates parasympathetic nervous system post-practice",
            "Increases core temperature and basal metabolic rate",
        ],
        "dosha_type": "Kapha (especially beneficial)",
        "seasonal_relevance": "All seasons",
        "modern_relevance": ["Fitness & Yoga", "Gut Health", "Mental Health"],
        "regional_names": {"Sanskrit": "Kapalbhati", "Hindi": "Skull Shining Breath"},
        "gen_z_hook": "Free metabolism hack. No Ozempic, no gym, just your breath. 🫁",
        "keywords": ["kapalbhati", "pranayama", "breathing", "metabolism"],
        "source_name": "Hatha Yoga Pradipika",
        "source_url": "https://www.yogamdniy.nic.in",
    },
    {
        "title": "Yoga Nidra — Yogic Sleep for Deep Rest",
        "domain": "Yoga", "subdomain": "Meditation",
        "summary": "Yoga Nidra ('yogic sleep') is a state of consciousness between waking and sleeping, induced through a guided body scan meditation. Swami Satyananda Saraswati systematised it in the 20th century from ancient Tantric practices. It is used by the US Army for PTSD treatment and is one of the most evidence-backed yoga practices.",
        "ingredients": [],
        "remedy_steps": [
            "Lie in Savasana (corpse pose) on a firm, comfortable surface",
            "Close eyes, set a Sankalpa (intention — a short positive statement)",
            "Follow a guided body rotation: right thumb → index → middle... rotating attention through every body part",
            "Alternate between pairs of opposite sensations: heaviness/lightness, heat/cold",
            "Visualise a series of rapid images as instructed (either guide or recording)",
            "Repeat your Sankalpa",
            "Allow 30-45 minutes for full session",
            "One hour of Yoga Nidra = approximately 4 hours of sleep (subjective reported)"
        ],
        "yoga_poses": ["Savasana", "Yoga Nidra"],
        "health_benefits": ["Sleep", "PTSD", "Anxiety", "Stress", "Memory", "Creativity", "Burnout"],
        "scientific_backing": [
            "Theta wave induction: EEG studies show sustained 4-7Hz activity",
            "US Army used iRest (Yoga Nidra protocol) for PTSD — RCT approved",
            "Reduces cortisol levels comparable to pharmacological anxiolytics",
            "Increases dopamine by 65% in striatum (PET scan study, Kjaer et al.)",
        ],
        "dosha_type": "All doshas",
        "seasonal_relevance": "All seasons",
        "modern_relevance": ["Sleep Wellness", "Mental Health", "PTSD Recovery", "Burnout"],
        "regional_names": {"Sanskrit": "Yoga Nidra", "Hindi": "Yogic Neend"},
        "gen_z_hook": "The US military uses this for trauma treatment. Free, no side effects, ancient origin. 🛌",
        "keywords": ["yoga nidra", "sleep", "theta waves", "ptsd", "guided meditation", "body scan"],
        "source_name": "Bihar School of Yoga + IREST Protocol",
        "source_url": "https://www.yogamdniy.nic.in",
    },
    {
        "title": "Trataka — Yogic Gazing for Focus & Vision",
        "domain": "Yoga", "subdomain": "Shatkarma",
        "summary": "Trataka (steady gazing) is one of the six Shatkarmas (purifications) of Hatha Yoga. It involves gazing at a fixed point — traditionally a candle flame — without blinking until tears flow. Used for strengthening eye muscles, improving concentration, and as a gateway to meditation.",
        "ingredients": ["Candle or Ghee Lamp"],
        "remedy_steps": [
            "Place a candle at eye level, 60-90 cm away in a dark room",
            "Sit in Sukhasana or Padmasana with spine erect",
            "Gaze at the tip of the flame without blinking",
            "When eyes water, close them and visualise the flame at the eyebrow centre",
            "When the image fades, open eyes and repeat",
            "Begin with 5 minutes, increase to 30 minutes over months",
            "Never practice with glasses or contact lenses initially",
            "Practice before sunrise or after sunset — best in dark quiet environment"
        ],
        "yoga_poses": ["Trataka", "Sukhasana", "Padmasana"],
        "health_benefits": ["Focus", "Concentration", "Eye Strength", "Memory", "Insomnia", "Anxiety"],
        "contraindications": ["Glaucoma", "Severe myopia (progress gradually)", "Epilepsy"],
        "scientific_backing": [
            "Strengthens extraocular muscles through sustained isometric engagement",
            "Activates prefrontal cortex (fMRI studies on sustained attention)",
            "Reduces cortisol in sustained meditation protocols",
        ],
        "dosha_type": "Kapha, Vata",
        "seasonal_relevance": "All seasons",
        "modern_relevance": ["Mental Health", "Focus", "Productivity", "Digital Detox"],
        "gen_z_hook": "ADHD brain? Ancient yogis designed this specifically for focus. No Adderall required. 🕯️",
        "keywords": ["trataka", "gazing", "concentration", "shatkarma", "candle", "focus", "eye"],
        "source_name": "Hatha Yoga Pradipika",
        "source_url": "https://www.yogamdniy.nic.in",
    },
    {
        "title": "Ashwagandha — Ancient Adaptogen",
        "domain": "Ayurveda", "subdomain": "Rasayana",
        "summary": "Withania somnifera is Ayurveda's most prized rasayana herb. Its name means 'smell of horse' — implying it gives equine strength. Modern RCTs confirm cortisol reduction, muscle mass gains, and neuroprotective effects.",
        "ingredients": ["Ashwagandha Root Powder", "Warm Milk", "Honey", "Ghee"],
        "remedy_steps": [
            "Take 1/4 to 1/2 tsp ashwagandha root powder",
            "Mix into warm milk with a small amount of ghee",
            "Add honey after mixing (do not cook honey)",
            "Consume before bedtime for 3 months minimum",
            "Capsule form: 300-600mg standardised to withanolides daily",
            "Best taken with food to avoid stomach upset"
        ],
        "health_benefits": ["Stress", "Anxiety", "Memory", "Energy", "Sleep", "Testosterone", "Immunity"],
        "contraindications": ["Avoid in pregnancy", "May lower blood pressure — caution with antihypertensives", "Avoid with thyroid medications without guidance"],
        "scientific_backing": [
            "Withanolide: Significant cortisol reduction in multiple RCTs (Chandrasekhar et al., 2012)",
            "8-week RCT: 27% reduction in serum cortisol vs placebo",
            "Neuroprotective: Promotes axon and dendrite growth",
        ],
        "dosha_type": "Vata, Kapha",
        "taste_rasa": "Bitter, Astringent",
        "potency_virya": "Heating",
        "seasonal_relevance": "Winter",
        "modern_relevance": ["Mental Health", "Fitness", "Immunity", "Sleep"],
        "regional_names": {"Sanskrit": "Ashwagandha", "Hindi": "Asgandh", "Tamil": "Amukkuram"},
        "gen_z_hook": "Andrew Huberman's #1 supplement. Your great-grandmother's free backyard plant. 💪",
        "keywords": ["ashwagandha", "withania", "withanolide", "adaptogen", "cortisol", "rasayana"],
        "source_name": "Charaka Samhita",
        "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Brahmi (Bacopa monnieri) — Brain Tonic",
        "domain": "Ayurveda", "subdomain": "Medhya Rasayana",
        "summary": "Brahmi is the premier Medhya Rasayana (brain rejuvenator) in Ayurveda. Named after Brahma (creator) for its effect on the mind. Used for memory enhancement and children's learning difficulties for 3000+ years. Modern research confirms it modulates cholinergic and serotonergic systems.",
        "ingredients": ["Brahmi Powder or Fresh Leaves", "Ghee", "Warm Milk", "Honey"],
        "remedy_steps": [
            "Fresh leaves: eat 2-5 leaves daily with honey in the morning",
            "Powder form: 1/4-1/2 tsp with warm milk before bed",
            "Brahmi ghee: classical Ayurvedic preparation for neurological disorders",
            "Oil form: massage scalp with Brahmi oil before washing hair",
            "Take consistently for minimum 8-12 weeks for cognitive effects",
            "For children: 1/4 tsp with honey daily"
        ],
        "health_benefits": ["Memory", "Anxiety", "ADHD", "Learning", "Focus", "Epilepsy (traditional)", "Stress"],
        "contraindications": ["May slow heart rate — caution with cardiac medications", "GI upset at high doses"],
        "scientific_backing": [
            "Bacosides A and B: Facilitate nerve impulse transmission and antioxidant activity",
            "12-week RCT: Significant improvement in verbal learning and memory (Roodenrys, 2002)",
            "Cholinergic modulation: Inhibits acetylcholinesterase",
        ],
        "dosha_type": "Vata, Pitta",
        "taste_rasa": "Bitter, Astringent",
        "seasonal_relevance": "All seasons",
        "modern_relevance": ["Mental Health", "Focus", "ADHD", "Memory"],
        "regional_names": {"Sanskrit": "Brahmi", "Tamil": "Neer Brahmi", "Telugu": "Sambarenu"},
        "gen_z_hook": "Nootropics industry worth $5B. Brahmi did this for free 3000 years ago. 🧠",
        "keywords": ["brahmi", "bacopa", "bacosides", "memory", "nootropic", "adhd", "cognitive"],
        "source_name": "Charaka Samhita + Ashtanga Hridayam",
        "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Moringa (Drumstick Tree) — Superfood of the Village",
        "domain": "Ayurveda", "subdomain": "Nutritive Herbs",
        "summary": "Moringa oleifera (Sahajan/Murungai) is called the 'miracle tree' because virtually every part is edible and medicinal. It contains 7x the Vitamin C of oranges, 4x the calcium of milk, 4x the Vitamin A of carrots, and 2x the protein of yogurt. Used across Ayurveda and Siddha medicine.",
        "ingredients": ["Moringa Leaves", "Moringa Powder", "Moringa Pods (Drumsticks)"],
        "remedy_steps": [
            "Leaves: add fresh or dried to dal, soups, or chutneys",
            "Powder: 1 tsp in smoothies, water, or warm milk daily",
            "Drumstick pods: cook in sambar, rasam, or coconut-based curries",
            "Tea: steep 1 tsp dried leaves in hot water for 5 minutes",
            "Moringa oil (Ben oil): excellent cooking oil and hair/skin treatment",
            "Seeds: press for oil or roast and eat (2-3 seeds/day — detoxifying)"
        ],
        "health_benefits": ["Nutrition", "Immunity", "Blood Sugar", "Iron Deficiency", "Inflammation", "Skin", "Energy"],
        "scientific_backing": [
            "Isothiocyanates: Anti-inflammatory and anti-tumour compounds",
            "7x Vitamin C of oranges, 4x calcium of milk per gram",
            "Reduces fasting blood glucose by ~26% in diabetic patients (RCT)",
        ],
        "dosha_type": "Kapha",
        "seasonal_relevance": "All seasons",
        "modern_relevance": ["Nutrition", "Immunity", "Sustainability"],
        "regional_names": {"Tamil": "Murungai", "Telugu": "Munagaku", "Hindi": "Sahajan"},
        "gen_z_hook": "Superfood brands sell moringa capsules for ₹2000. Your village tree has it free. 🌿",
        "keywords": ["moringa", "drumstick", "murungai", "superfood", "vitamin c", "nutrition"],
        "source_name": "Siddha Medicine + Modern Nutrition Research",
        "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Shatavari — Women's Rasayana",
        "domain": "Ayurveda", "subdomain": "Women's Health",
        "summary": "Shatavari (Asparagus racemosus) literally means 'she who has a hundred husbands' — a metaphor for its ability to support a woman's reproductive vitality through every stage of life. It is the primary Ayurvedic herb for hormonal balance, lactation, fertility, and menopause.",
        "ingredients": ["Shatavari Root Powder", "Warm Milk", "Honey", "Ghee"],
        "remedy_steps": [
            "Take 1/4 to 1/2 tsp Shatavari powder",
            "Mix in warm milk with 1/2 tsp ghee and honey to taste",
            "Consume twice daily (morning and evening) for minimum 3 months",
            "For new mothers (lactation): increase to 1 tsp twice daily",
            "For menopause: combine with Ashwagandha in equal parts",
            "Capsule form: 500mg standardized extract twice daily"
        ],
        "health_benefits": ["Hormonal Balance", "Lactation", "Fertility", "Menopause", "Immunity", "Stress"],
        "scientific_backing": [
            "Shatavarin I-IV: Steroidal saponins with oestrogenic activity",
            "Significantly increases prolactin levels in lactating mothers (RCT)",
            "Adaptogenic: Modulates HPA axis and reduces cortisol",
        ],
        "dosha_type": "Vata, Pitta",
        "seasonal_relevance": "All seasons",
        "modern_relevance": ["Women's Health", "Fertility", "Hormonal Balance"],
        "regional_names": {"Sanskrit": "Shatavari", "Tamil": "Thanneervittan", "Hindi": "Satavar"},
        "gen_z_hook": "Hormone therapy in a root. Proven by Ayurveda 2500 years before endocrinology existed. 💜",
        "keywords": ["shatavari", "asparagus racemosus", "women", "hormones", "lactation", "menopause"],
        "source_name": "Charaka Samhita + Sushruta Samhita",
        "source_url": "https://www.tkdl.res.in",
    },
    # ── FARMING ───────────────────────────────────────────────────────
    {
        "title": "Zero Budget Natural Farming (ZBNF) — Subhash Palekar",
        "domain": "Sustainable Farming", "subdomain": "Modern Traditional",
        "summary": "Developed by Padma Shri Subhash Palekar, ZBNF is inspired by ancient Vedic farming. It uses desi cow inputs to create 'Jeevamrit' — a fermented microbial inoculant that supercharges soil health to near-zero external input.",
        "ingredients": ["Desi Cow Dung (10kg)", "Desi Cow Urine (10L)", "Jaggery (2kg)", "Pulse Flour (2kg)", "Forest Soil (handful)"],
        "remedy_steps": [
            "Mix all ingredients in 200L water drum",
            "Stir clockwise for 5 minutes",
            "Cover and ferment in shade for 48 hours, stirring twice daily",
            "Dilute 10% and apply through drip irrigation every 15 days",
            "Bijamrit (seed treatment): 500g dung + 1L urine + 50g lime + water",
            "Coat seeds in Bijamrit and dry before planting",
        ],
        "health_benefits": ["Soil Health", "Crop Yield", "Biodiversity", "Water Retention"],
        "scientific_backing": [
            "10-15x increase in soil microbial diversity (bioinformatics studies)",
            "Maintains yield parity with chemical farming in 3-year transitions",
            "Humus formation increases water retention by 20-30%",
        ],
        "seasonal_relevance": "All seasons",
        "modern_relevance": ["Sustainability", "Climate Resilience", "Zero Waste"],
        "regional_names": {"Hindi": "Shoonya Bajat Prakritik Kheti"},
        "gen_z_hook": "Regenerative farming trends in Silicon Valley. Indian farmers invented it 5000 years ago. 🌾",
        "keywords": ["zbnf", "jeevamrit", "subhash palekar", "natural farming", "regenerative"],
        "source_name": "ZBNF + Vedic Agricultural Texts",
        "source_url": "https://zerobudgetfarming.com",
    },
    {
        "title": "Panchagavya — Five Cow Products Formulation",
        "domain": "Sustainable Farming", "subdomain": "Organic Inputs",
        "summary": "Panchagavya ('five products of the cow') is a traditional organic formulation used both as a soil drench and foliar spray in Indian farming. It contains cow dung, cow urine, milk, curd, and ghee — all fermented together. Modern research shows it acts as a plant growth promoter through cytokinins and gibberellins.",
        "ingredients": ["Cow Dung (5kg)", "Cow Urine (3L)", "Fresh Cow Milk (2L)", "Curd (2L)", "Ghee (1kg)", "Sugarcane Juice or Jaggery", "Tender Coconut Water", "Banana"],
        "remedy_steps": [
            "Ferment cow dung with ghee for 3 days, stirring daily",
            "Add cow urine and ferment 3 more days",
            "Add milk, curd, sugarcane juice, banana, and coconut water",
            "Ferment total 30 days, stirring twice daily",
            "Strain through cloth and store in shade",
            "Use 3% solution (30ml per litre) as foliar spray every 15 days",
            "50% dilution as soil drench for transplant shock recovery"
        ],
        "health_benefits": ["Crop Yield", "Plant Immunity", "Soil Microbiome", "Root Development"],
        "scientific_backing": [
            "Contains natural plant growth regulators (cytokinins, gibberellins)",
            "Increases crop yield 15-23% vs untreated controls",
            "Reduces fungal disease incidence in rice and vegetables",
        ],
        "seasonal_relevance": "All seasons",
        "modern_relevance": ["Organic Farming", "Sustainability"],
        "regional_names": {"Sanskrit": "Panchagavya", "Tamil": "Panchakavyam"},
        "gen_z_hook": "Ancient bio-stimulant. Modern agri-tech companies are patenting what Indian farmers gave away free. 🐄",
        "keywords": ["panchagavya", "cow", "organic", "farming", "growth promoter", "soil"],
        "source_name": "Vrikshayurveda + Agricultural Research",
        "source_url": "https://www.tkdl.res.in",
    },
    # ── ORAL HISTORY & CULTURE ────────────────────────────────────────
    {
        "title": "Panchatantra — Ancient Stories with Embedded Wisdom",
        "domain": "Oral History", "subdomain": "Folk Stories",
        "summary": "The Panchatantra (~300 BCE, Vishnu Sharma) is one of the world's oldest collections of wisdom literature, comprising 87 animal fables embedded with principles of Niti (statecraft) and Nitishastra (wise conduct). It is the source of Aesop's Fables via Persian and Arabic translations.",
        "ingredients": [],
        "health_benefits": ["Wisdom", "Ethics", "Decision Making", "Leadership"],
        "scientific_backing": [
            "Narratological research confirms story-based learning increases retention 22x vs abstract rules",
            "Source of Kalila wa Dimna (Arabic) and Hitopadesha (Sanskrit)",
        ],
        "seasonal_relevance": "All seasons",
        "modern_relevance": ["Education", "Oral History Preservation", "Leadership"],
        "regional_names": {"Sanskrit": "Panchatantra", "Arabic": "Kalila wa Dimna"},
        "gen_z_hook": "Aesop stole his fables from India. Time to reclaim the source. 🦊",
        "keywords": ["panchatantra", "vishnu sharma", "fables", "niti", "wisdom", "stories"],
        "source_name": "Vishnu Sharma (~300 BCE)",
        "source_url": "https://www.wisdomlib.org/hinduism/book/the-panchatantra",
    },
    {
        "title": "Vastu Shastra — Ancient Architecture & Space Science",
        "domain": "Ancient Texts", "subdomain": "Architecture",
        "summary": "Vastu Shastra is the ancient Indian science of architecture and spatial arrangement. It aligns built spaces with natural forces — solar movement, magnetic fields, wind, and water — to optimise human health and wellbeing. Modern research has found correlations between Vastu-compliant buildings and reduced stress biomarkers in occupants.",
        "ingredients": [],
        "health_benefits": ["Mental Wellbeing", "Sleep", "Productivity", "Energy"],
        "scientific_backing": [
            "North-south sleeping alignment correlates with better sleep quality (geomagnetic research)",
            "East-facing kitchens maximize morning sunlight exposure for circadian regulation",
            "Cross-ventilation principles align with modern passive building design",
        ],
        "seasonal_relevance": "All seasons",
        "modern_relevance": ["Mental Health", "Architecture", "Sustainability"],
        "regional_names": {"Sanskrit": "Vastu Shastra", "Tamil": "Vastu Sastra"},
        "gen_z_hook": "Biophilic architecture and passive house design are just rediscovering Vastu. 🏡",
        "keywords": ["vastu", "architecture", "space", "direction", "magnetic", "ancient design"],
        "source_name": "Manasara + Mayamata (Classical Texts)",
        "source_url": "https://www.wisdomlib.org",
    },
    {
        "title": "Vedic Mathematics — Mental Calculation Sutras",
        "domain": "Vedic Mathematics", "subdomain": "Mental Math",
        "summary": "Vedic Mathematics is a system of 16 sutras (aphorisms) reconstructed from the Atharva Veda by Sri Bharati Krishna Tirthaji (1884-1960). These sutras allow rapid mental calculation for multiplication, division, square roots, and simultaneous equations. Used in competitive exam preparation across India.",
        "ingredients": [],
        "health_benefits": ["Mathematical Fluency", "Mental Speed", "Concentration"],
        "scientific_backing": [
            "Sutra 'Vertically and Crosswise' reduces multiplication steps from O(n²) to O(n)",
            "Nikhilam method for large-number multiplication faster than conventional algorithms",
            "Used in VLSI circuit design optimization in modern computer science",
        ],
        "seasonal_relevance": "All seasons",
        "modern_relevance": ["Education", "Competitive Exams", "Mental Agility"],
        "regional_names": {"Sanskrit": "Vedic Ganita"},
        "gen_z_hook": "Your mental calculator can beat a phone if you know these 16 sutras. 🧮",
        "keywords": ["vedic math", "sutra", "mental calculation", "multiplication", "tirthaji"],
        "source_name": "Vedic Mathematics by Bharati Krishna Tirthaji",
        "source_url": "https://en.wikipedia.org/wiki/Vedic_Mathematics",
    },
    {
        "title": "Kalaripayattu — World's Oldest Martial Art",
        "domain": "Traditional Martial Arts", "subdomain": "Kerala",
        "summary": "Kalaripayattu is the oldest codified martial art in the world, originating in Kerala (~3rd century BCE). It combines combat techniques with Ayurvedic medicine, yoga, and a deep understanding of Marma points (vital pressure points). It is the acknowledged ancestor of many Asian martial arts via Buddhist monk Bodhidharma's transmission to China.",
        "ingredients": [],
        "yoga_poses": ["Meipayattu (Body exercises)", "Kolthari (Stick fighting)", "Ankathari (Weapons)"],
        "health_benefits": ["Flexibility", "Strength", "Focus", "Coordination", "Self-Defence", "Mental Discipline"],
        "scientific_backing": [
            "Marma point therapy: Stimulation of 107 vital points for therapeutic purposes",
            "Research on neuromotor benefits: Superior balance and proprioception vs non-practitioners",
            "Ancestor of Chinese Kung Fu via Bodhidharma (documented in Chinese martial arts history)",
        ],
        "seasonal_relevance": "All seasons",
        "modern_relevance": ["Fitness", "Cultural Heritage", "Self Defence"],
        "regional_names": {"Malayalam": "Kalaripayattu", "English": "Kalari"},
        "gen_z_hook": "Jackie Chan's ancestor learned from an Indian monk. The root of all martial arts is Kerala. 🥋",
        "keywords": ["kalaripayattu", "kalari", "kerala", "martial arts", "marma", "bodhidharma"],
        "source_name": "Dhanurveda + Kerala Martial Arts Tradition",
        "source_url": "https://www.tkdl.res.in",
    },
]

# ─────────────────────────────────────────────
#  NLP / EXTRACTION HELPERS
# ─────────────────────────────────────────────
STOPWORDS = {
    "their","there","which","about","these","those","would","could","should",
    "other","often","using","being","having","where","while","since","after",
    "before","during","through","between","because","therefore","however",
    "although","within","without","against","across","along","among","around",
    "include","including","known","called","used","uses","also","made","make",
    "found","study","studies","research","evidence","showed","shown","showed"
}

INGREDIENTS_LIST = [
    "turmeric","haldi","ginger","adrak","tulsi","neem","ashwagandha","amla","giloy",
    "brahmi","triphala","honey","ghee","milk","coconut oil","sesame oil","black pepper",
    "cumin","coriander","fenugreek","mustard","cinnamon","cardamom","clove","nutmeg",
    "saffron","aloe vera","moringa","curry leaves","peppercorn","long pepper","garlic",
    "lemon","pomegranate","sandalwood","rose water","haritaki","bibhitaki","manjistha",
    "ashoka","guggul","shallaki","boswellia","gymnema","andrographis","shatavari",
    "triphala","brahmi","shankhpushpi","jatamansi","vacha","gokshura","bael","noni",
    "punarnava","vidanga","chitrak","pippali","trikatu","dashamoola","sariva",
]

YOGA_POSES = [
    "tadasana","vrikshasana","trikonasana","adho mukha","uttanasana","virabhadrasana",
    "balasana","savasana","padmasana","siddhasana","bhujangasana","dhanurasana",
    "halasana","sarvangasana","sirsasana","sukhasana","vajrasana","kapalbhati",
    "anulom vilom","bhastrika","nadi shodhana","surya namaskar","yoga nidra",
    "trataka","bandha","uddiyana","mula bandha","jalandhara","kumbhaka",
    "setubandhasana","utkatasana","paschimottanasana","ardha matsyendrasana",
]

SCIENCE_TERMS = {
    "antibacterial":    "Fights harmful bacteria",
    "antimicrobial":    "Kills microorganisms",
    "anti-inflammatory":"Reduces inflammation",
    "antioxidant":      "Fights free radicals / cell aging",
    "adaptogen":        "Helps body adapt to stress",
    "immunomodulatory": "Modulates immune system activity",
    "hepatoprotective": "Protects the liver",
    "neuroprotective":  "Protects brain cells",
    "analgesic":        "Pain-relieving",
    "curcumin":         "Active in turmeric (anti-inflammatory)",
    "gingerol":         "Active in ginger (antinausea, antiviral)",
    "withanolide":      "Active in ashwagandha (adaptogen)",
    "allicin":          "Active in garlic (antibacterial)",
    "eugenol":          "Active in cloves (antimicrobial)",
    "bacosides":        "Active in Brahmi (cognitive enhancer)",
    "piperine":         "Active in black pepper (bioavailability booster)",
    "acemannan":        "Active in aloe vera (wound healing)",
    "nimbin":           "Active in neem (antibacterial)",
    "azadirachtin":     "Active in neem (insecticidal, safe for humans)",
    "quercetin":        "Flavonoid antioxidant in many plants",
    "berberine":        "Alkaloid (anti-diabetic properties)",
    "apigenin":         "Flavonoid (anti-anxiety, anti-inflammatory)",
    "ursolic acid":     "Triterpenoid in Tulsi (anti-cancer, anti-inflammatory)",
    "thymoquinone":     "Active in Nigella sativa (anti-inflammatory)",
    "shogaol":          "Active in dried ginger (anti-inflammatory)",
    "gallic acid":      "Antioxidant in Amla and Haritaki",
    "ellagic acid":     "Polyphenol in Amla (antioxidant, anti-cancer)",
}

HEALTH_KEYWORDS = [
    "immunity","digestion","sleep","stress","anxiety","memory","skin","hair",
    "joint","pain","fever","cold","cough","diabetes","blood pressure","cholesterol",
    "weight","energy","detox","liver","kidney","heart","wounds","inflammation",
    "cancer","depression","ptsd","adhd","fertility","hormones","menopause","lactation",
    "vision","dental","oral","respiratory","lung","blood sugar","obesity","arthritis",
]

MODERN_TAGS = {
    "Immunity Boosting": ["immunity","immune","resistance","viral","antiviral"],
    "Mental Health":     ["stress","anxiety","depression","mental","ptsd","adhd","cortisol"],
    "Gut Health":        ["digestion","gut","probiotic","microbiome","bloating","ibs"],
    "Skincare":          ["skin","glow","acne","complexion","wound","burn","dermal"],
    "Haircare":          ["hair","scalp","dandruff","alopecia"],
    "Sustainability":    ["sustainable","eco","organic","zero waste","regenerative"],
    "Sleep Wellness":    ["sleep","insomnia","rest","melatonin","yoga nidra"],
    "Fitness & Yoga":    ["fitness","yoga","asana","flexibility","strength","cardio"],
    "Detox":             ["detox","cleanse","purify","toxin","ama","panchakarma"],
    "Women's Health":    ["women","lactation","fertility","menopause","hormones","pcos"],
    "Oral Health":       ["dental","tooth","gum","oral","cavity"],
    "Eye Health":        ["vision","eye","sight","conjunctivitis","retina"],
    "Pain Relief":       ["pain","arthritis","joint","analgesic","anti-inflammatory"],
    "Nutrition":         ["nutrition","vitamin","mineral","protein","superfood"],
}

SEASONAL_MAP = {
    "Winter":  ["winter","shishir","cold","december","january","february"],
    "Summer":  ["summer","grishma","heat","may","june"],
    "Monsoon": ["monsoon","rainy","varsha","july","august","september"],
    "Spring":  ["spring","vasant","march","april"],
}

DOMAIN_RULES = {
    "Ayurveda":            ["ayurveda","vata","pitta","kapha","herb","turmeric","tulsi","neem","ashwagandha","triphala","ghee","dosha","rasayana","samhita","agni","ojas"],
    "Yoga":                ["yoga","asana","pranayama","meditation","surya","chakra","mudra","dhyana","prana","hatha","kundalini","nidra","trataka","shatkarma"],
    "Home Remedies":       ["remedy","cure","paste","decoction","honey","ginger","garlic","pepper","apply","consume","mix","boil","kadha"],
    "Sustainable Farming": ["farming","agriculture","soil","crop","seed","organic","compost","cow dung","natural farming","jeevamrit","panchagavya"],
    "Ancient Astronomy":   ["astronomy","jyotisha","nakshatra","graha","panchang","vedic astronomy","aryabhata","surya siddhanta"],
    "Vedic Mathematics":   ["vedic math","sutra","aryabhata","brahmagupta","mathematics","ganita"],
    "Food & Culture":      ["food","recipe","cuisine","spice","masala","ferment","pickle","sattvic","fasting","idli","dosa","rasam"],
    "Oral History":        ["folklore","legend","myth","oral tradition","ritual","festival","custom","panchatantra","ramayana"],
    "Siddha":              ["siddha","siddhar","tamil medicine","siddha vaidya"],
    "Unani":               ["unani","hakeem","tibb","greco-arabic"],
    "Ancient Texts":       ["samhita","vedas","upanishad","purana","shastra","sutra","gita","tantra"],
    "Arts & Culture":      ["dance","music","bharatanatyam","kathak","carnatic","rangoli","natyashastra"],
    "Traditional Martial Arts": ["kalaripayattu","kalari","martial","dhanurveda","akhada"],
}

GEN_Z_HOOKS = {
    "Ayurveda":           "Personalised medicine 5000 years before Goop existed. No subscription. 🌿",
    "Yoga":               "Ancient biohacking. No app, no subscription, no equipment. 🧘",
    "Home Remedies":      "Kitchen pharmacies that actually work, no side effects attached. 🍯",
    "Food & Culture":     "This dish carries 3000 years of ancestral memory. No cap. 🍛",
    "Sustainable Farming":"Zero-waste farming, invented before zero-waste was a trend. 🌱",
    "Oral History":       "This survived 40 generations of humans. Hear it before it disappears. 📿",
    "Ancient Astronomy":  "They mapped the cosmos without telescopes. Lowkey insane. ⭐",
    "Vedic Mathematics":  "Mental math shortcuts that make calculators look slow. 🧮",
    "Siddha":             "Tamil medicine practiced 10,000 years before colonisation tried to erase it. 🌺",
    "Unani":              "The world's first universal healthcare system, from Hakim to patient. 🌿",
    "Ancient Texts":      "Wisdom encoded in texts surviving 2000+ years. Worth reading. 📜",
    "Arts & Culture":     "Performance art that is spiritual practice and physical workout in one. 💃",
    "Traditional Martial Arts": "The root of all Asian martial arts is Indian. Look it up. 🥋",
}

def make_id(url: str, title: str) -> str:
    return hashlib.md5(f"{url}_{title}".encode()).hexdigest()[:12]

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\[[\d, ]+\]", "", text)  # remove Wikipedia citation brackets
    return text.strip()

def extract_keywords(text: str, top_n: int = 25) -> list:
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    freq = {}
    for w in words:
        if w not in STOPWORDS:
            freq[w] = freq.get(w, 0) + 1
    return sorted(freq, key=freq.get, reverse=True)[:top_n]

def extract_ingredients(text: str) -> list:
    t = text.lower()
    return sorted({ing.title() for ing in INGREDIENTS_LIST if ing in t})

def extract_yoga_poses(text: str) -> list:
    t = text.lower()
    return sorted({p.title() for p in YOGA_POSES if p in t})

def extract_science(text: str) -> list:
    t = text.lower()
    return [f"{k.title()}: {v}" for k, v in SCIENCE_TERMS.items() if k in t]

def extract_health(text: str) -> list:
    t = text.lower()
    return [kw.title() for kw in HEALTH_KEYWORDS if kw in t]

def detect_modern(text: str) -> list:
    t = text.lower()
    return [tag for tag, terms in MODERN_TAGS.items() if any(term in t for term in terms)]

def detect_dosha(text: str) -> str:
    t = text.lower()
    doshas = [d for d in ["vata","pitta","kapha"] if d in t]
    return ", ".join(d.title() for d in doshas) if doshas else ""

def detect_season(text: str) -> str:
    t = text.lower()
    for season, terms in SEASONAL_MAP.items():
        if any(term in t for term in terms):
            return season
    return "All seasons"

def detect_domain(text: str, default: str = "Traditional Knowledge") -> str:
    t = text.lower()
    scores = {d: sum(1 for kw in kws if kw in t) for d, kws in DOMAIN_RULES.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else default

def detect_contraindications(text: str) -> list:
    patterns = [
        r"avoid[^.]+(?:pregnancy|pregnant|children|hypertension|diabetes|surgery)[^.]+\.",
        r"do not[^.]+(?:use|take|apply|consume)[^.]+\.",
        r"contraindicated[^.]+\.",
        r"warning[^.]+\.",
    ]
    t = text.lower()
    found = []
    for p in patterns:
        matches = re.findall(p, t)
        found.extend(matches[:2])
    return [c[:200].strip().title() for c in found[:5]]

DADI_INTROS = [
    "Baith mere paas beta, sunle ek baat... ",
    "Close your phone for a second. Your dadi has something important to tell you... ",
    "Arey, you think this is just old folk talk? Listen carefully, this has science behind it... ",
    "Beta, our ancestors knew things that modern science is only now catching up to... ",
    "Sit down child, let me tell you something they do not teach in schools anymore... ",
    "You know what used to keep our entire village healthy? Let me tell you... ",
]
DADI_CLOSINGS = [
    " — They hid science inside daily rituals so we would never forget.",
    " — Every ritual has a reason. Every spice has a purpose. That is the wisdom of our people.",
    " — They did not need labs. They had thousands of years of careful observation and love.",
    " — The secret was always that our ancestors were not superstitious — they were scientists without the vocabulary.",
    " — We called it tradition because we did not have the word 'evidence-based medicine' yet.",
]

def generate_dadi_story(title: str, summary: str, domain: str) -> str:
    intro = random.choice(DADI_INTROS)
    closing = random.choice(DADI_CLOSINGS)
    return f"{intro}{summary[:500]}{closing}"

def score_authenticity(e: KnowledgeEntry) -> float:
    s = 0.0
    if e.ingredients:              s += 0.10
    if e.remedy_steps:             s += 0.15
    if e.scientific_backing:       s += 0.20
    if e.dosha_type:               s += 0.08
    if e.keywords:                 s += 0.08
    if len(e.raw_content) > 300:   s += 0.10
    if e.seasonal_relevance:       s += 0.05
    if e.health_benefits:          s += 0.10
    if e.pubmed_abstracts:         s += 0.07
    if e.taste_rasa:               s += 0.03
    if e.regional_names:           s += 0.04
    return round(min(s, 1.0), 2)

def make_entry_from_text(title, content, source_url, source_name,
                          default_domain, data_source_type="scraped") -> KnowledgeEntry:
    domain = detect_domain(content, default_domain)
    sentences = re.split(r"(?<=[.!?])\s+", content)
    summary = " ".join([s for s in sentences if len(s) > 40][:4])
    e = KnowledgeEntry(
        id=make_id(source_url, title),
        title=title,
        domain=domain,
        subdomain=default_domain,
        dadi_story=generate_dadi_story(title, summary, domain),
        summary=summary,
        raw_content=content[:4000],
        scientific_backing=extract_science(content),
        health_benefits=extract_health(content),
        contraindications=detect_contraindications(content),
        ingredients=extract_ingredients(content),
        yoga_poses=extract_yoga_poses(content),
        seasonal_relevance=detect_season(content),
        dosha_type=detect_dosha(content),
        modern_relevance=detect_modern(content),
        keywords=extract_keywords(content),
        source_url=source_url,
        source_name=source_name,
        scraped_at=datetime.now().isoformat(),
        gen_z_hook=GEN_Z_HOOKS.get(domain, "Ancient wisdom. Still relevant. Still free. 🙏"),
        data_source_type=data_source_type,
    )
    e.authenticity_score = score_authenticity(e)
    return e

# ─────────────────────────────────────────────
#  SCRAPERS
# ─────────────────────────────────────────────

def scrape_wikipedia(page_title: str, domain: str, subdomain: str) -> Optional[KnowledgeEntry]:
    api_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query", "format": "json",
        "titles": page_title, "prop": "extracts|pageimages",
        "explaintext": True, "exsectionformat": "plain",
        "piprop": "original",
    }
    try:
        r = requests.get(api_url, params=params, headers=HEADERS, timeout=15)
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        for pid, page in pages.items():
            if pid == "-1":
                return None
            content = clean_text(page.get("extract", ""))
            if len(content) < 200:
                return None
            wiki_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ','_')}"
            entry = make_entry_from_text(
                title=page.get("title", page_title),
                content=content,
                source_url=wiki_url,
                source_name=f"Wikipedia — {page_title}",
                default_domain=domain,
                data_source_type="wikipedia"
            )
            entry.subdomain = subdomain
            # Try to grab image
            img = page.get("original", {}).get("source", "")
            if img:
                entry.image_url = img
            return entry
    except Exception as ex:
        log.error(f"Wikipedia error '{page_title}': {ex}")
        return None


def scrape_static_site(site: dict) -> Optional[KnowledgeEntry]:
    if not BS4_OK:
        return None
    try:
        r = requests.get(site["url"], headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        # Remove nav, footer, header, ads
        for tag in soup(["nav","footer","header","script","style","aside",".sidebar","#sidebar"]):
            tag.decompose()
        content = ""
        for selector in site.get("selectors", ["main","article","body"]):
            el = soup.select_one(selector)
            if el:
                paras = el.find_all(["p","li","h2","h3"])
                content = " ".join(clean_text(p.get_text()) for p in paras if len(p.get_text().strip()) > 30)
                if len(content) > 300:
                    break
        if len(content) < 200:
            return None
        title_el = soup.select_one("h1, h2, .page-title, title")
        title = clean_text(title_el.get_text()) if title_el else site["name"]
        return make_entry_from_text(
            title=title[:150],
            content=content,
            source_url=site["url"],
            source_name=site["name"],
            default_domain=site["domain"],
            data_source_type="static_web"
        )
    except Exception as ex:
        log.error(f"Static scrape error {site['url']}: {ex}")
        return None


def scrape_pubmed(query: str, max_results: int = 5) -> list:
    """Fetch PubMed abstracts for a query via E-utilities API."""
    entries = []
    try:
        # Step 1: Search
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {"db": "pubmed", "term": query, "retmax": max_results, "retmode": "json"}
        r = requests.get(search_url, params=params, headers=HEADERS, timeout=15)
        ids = r.json().get("esearchresult", {}).get("idlist", [])
        if not ids:
            return entries

        time.sleep(0.34)  # NCBI rate limit: 3 requests/sec

        # Step 2: Fetch abstracts
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params2 = {"db": "pubmed", "id": ",".join(ids), "rettype": "abstract", "retmode": "text"}
        r2 = requests.get(fetch_url, params=params2, headers=HEADERS, timeout=20)
        text = r2.text

        # Split into individual abstracts
        abstracts = re.split(r"\n\d+\. ", text)
        for i, abstract in enumerate(abstracts[:max_results]):
            if len(abstract) < 100:
                continue
            lines = abstract.strip().split("\n")
            title = lines[0].strip()[:200] if lines else f"PubMed: {query}"
            content = " ".join(lines)
            entry = make_entry_from_text(
                title=title,
                content=content,
                source_url=f"https://pubmed.ncbi.nlm.nih.gov/?term={requests.utils.quote(query)}",
                source_name=f"PubMed — {query[:50]}",
                default_domain="Ayurveda",
                data_source_type="pubmed"
            )
            # Mark as research article
            entry.pubmed_abstracts = [abstract[:1000]]
            entries.append(entry)

    except Exception as ex:
        log.error(f"PubMed error '{query}': {ex}")
    return entries


def scrape_wikidata_herbs() -> list:
    """Fetch structured herb data from Wikidata SPARQL."""
    if not SPARQL_OK:
        log.warning("SPARQLWrapper not installed. Skipping Wikidata.")
        return []

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.addCustomHttpHeader("User-Agent", HEADERS["User-Agent"])

    query = """
    SELECT ?item ?itemLabel ?description ?image ?taxon WHERE {
      ?item wdt:P31 wd:Q11173 .
      ?item wdt:P171* wd:Q18478 .
      ?item wdt:P1843 ?taxon .
      OPTIONAL { ?item schema:description ?description FILTER(LANG(?description)="en") }
      OPTIONAL { ?item wdt:P18 ?image }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
    }
    LIMIT 80
    """
    entries = []
    try:
        sparql.setQuery(query)
        sparql.setReturnFormat(SPARQL_JSON)
        results = sparql.query().convert()
        for r in results["results"]["bindings"]:
            label = r.get("itemLabel", {}).get("value", "")
            desc = r.get("description", {}).get("value", "")
            qid = r.get("item", {}).get("value", "").split("/")[-1]
            if not label or len(label) < 3:
                continue
            content = f"{label}. {desc}"
            e = make_entry_from_text(
                title=label,
                content=content,
                source_url=f"https://www.wikidata.org/wiki/{qid}",
                source_name="Wikidata",
                default_domain="Ayurveda",
                data_source_type="wikidata"
            )
            e.wikidata_qid = qid
            e.image_url = r.get("image", {}).get("value", "")
            entries.append(e)
    except Exception as ex:
        log.error(f"Wikidata SPARQL error: {ex}")
    return entries


def scrape_dbpedia_indian_knowledge() -> list:
    """Fetch Indian knowledge systems data from DBpedia SPARQL."""
    if not SPARQL_OK:
        return []

    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    sparql.addCustomHttpHeader("User-Agent", HEADERS["User-Agent"])

    queries = [
        ("Ayurvedic herbs", """
         SELECT ?s ?label ?abstract WHERE {
           ?s dct:subject dbc:Ayurvedic_herbs .
           ?s rdfs:label ?label FILTER(LANG(?label)="en") .
           OPTIONAL { ?s dbo:abstract ?abstract FILTER(LANG(?abstract)="en") }
         } LIMIT 50"""),
        ("Yoga asanas", """
         SELECT ?s ?label ?abstract WHERE {
           ?s dct:subject dbc:Yoga_poses .
           ?s rdfs:label ?label FILTER(LANG(?label)="en") .
           OPTIONAL { ?s dbo:abstract ?abstract FILTER(LANG(?abstract)="en") }
         } LIMIT 30"""),
        ("Indian spices", """
         SELECT ?s ?label ?abstract WHERE {
           ?s dct:subject dbc:Indian_spices .
           ?s rdfs:label ?label FILTER(LANG(?label)="en") .
           OPTIONAL { ?s dbo:abstract ?abstract FILTER(LANG(?abstract)="en") }
         } LIMIT 40"""),
    ]

    entries = []
    for qname, qbody in queries:
        sparql.setQuery(f"""
            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX dbc: <http://dbpedia.org/resource/Category:>
            PREFIX dbo: <http://dbpedia.org/ontology/>
            {qbody}
        """)
        sparql.setReturnFormat(SPARQL_JSON)
        try:
            results = sparql.query().convert()
            for r in results["results"]["bindings"]:
                label = r.get("label", {}).get("value", "")
                abstract = r.get("abstract", {}).get("value", "")
                uri = r.get("s", {}).get("value", "")
                if not label or len(abstract) < 50:
                    continue
                e = make_entry_from_text(
                    title=label,
                    content=abstract,
                    source_url=uri,
                    source_name=f"DBpedia — {qname}",
                    default_domain="Ayurveda",
                    data_source_type="dbpedia"
                )
                entries.append(e)
            time.sleep(1)
        except Exception as ex:
            log.error(f"DBpedia error '{qname}': {ex}")
    return entries


def get_selenium_driver():
    if not SELENIUM_OK:
        return None
    try:
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1280,900")
        opts.add_argument(f"user-agent={HEADERS['User-Agent']}")
        return webdriver.Chrome(options=opts)
    except Exception as ex:
        log.error(f"ChromeDriver not found: {ex}")
        return None


def scrape_with_selenium(driver, site: dict) -> Optional[KnowledgeEntry]:
    if not BS4_OK:
        return None
    try:
        driver.get(site["url"])
        time.sleep(4)
        soup = BeautifulSoup(driver.page_source, "lxml")
        for tag in soup(["nav","footer","header","script","style"]):
            tag.decompose()
        for selector in ["article","main",".field-items",".node__content",".view-content","#content","body"]:
            el = soup.select_one(selector)
            if el:
                paras = el.find_all(["p","li","h2","h3","h4"])
                content = " ".join(clean_text(p.get_text()) for p in paras if len(p.get_text()) > 30)
                if len(content) > 300:
                    title_el = soup.select_one("h1, .page-title")
                    title = clean_text(title_el.get_text()) if title_el else site["name"]
                    return make_entry_from_text(
                        title=title[:150],
                        content=content,
                        source_url=site["url"],
                        source_name=site["name"],
                        default_domain=site["domain"],
                        data_source_type="selenium"
                    )
        return None
    except Exception as ex:
        log.error(f"Selenium error {site['url']}: {ex}")
        return None

# ─────────────────────────────────────────────
#  SEED DATA LOADER
# ─────────────────────────────────────────────
def load_seed_data() -> list:
    entries = []
    for item in SEED_KNOWLEDGE:
        content = (item.get("summary","") + " " +
                   " ".join(item.get("remedy_steps",[]) + item.get("scientific_backing",[])))
        e = KnowledgeEntry(
            id=make_id(item.get("source_url","seed"), item["title"]),
            title=item["title"],
            domain=item["domain"],
            subdomain=item.get("subdomain",""),
            dadi_story=generate_dadi_story(item["title"], item.get("summary",""), item["domain"]),
            summary=item.get("summary",""),
            raw_content=content,
            scientific_backing=item.get("scientific_backing",[]),
            health_benefits=item.get("health_benefits",[]),
            contraindications=item.get("contraindications",[]),
            ingredients=item.get("ingredients",[]),
            remedy_steps=item.get("remedy_steps",[]),
            yoga_poses=item.get("yoga_poses",[]),
            seasonal_relevance=item.get("seasonal_relevance",""),
            dosha_type=item.get("dosha_type",""),
            taste_rasa=item.get("taste_rasa",""),
            potency_virya=item.get("potency_virya",""),
            modern_relevance=item.get("modern_relevance",[]),
            keywords=item.get("keywords", extract_keywords(content)),
            source_url=item.get("source_url",""),
            source_name=item.get("source_name",""),
            scraped_at=datetime.now().isoformat(),
            gen_z_hook=item.get("gen_z_hook",""),
            regional_names=item.get("regional_names",{}),
            data_source_type="seed",
        )
        e.authenticity_score = score_authenticity(e)
        entries.append(e)
    return entries

# ─────────────────────────────────────────────
#  SAVE
# ─────────────────────────────────────────────
def save_json(data: list, filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    log.info(f"Saved {len(data)} entries → {path}")

def save_all_outputs(entries: list):
    all_dicts = [asdict(e) for e in entries]
    save_json(all_dicts, "knowledge_base_full.json")

    # Per-domain
    domain_map = {}
    for e in entries:
        domain_map.setdefault(e.domain, []).append(asdict(e))
    for domain, items in domain_map.items():
        safe = re.sub(r"[^\w]", "_", domain).lower()
        save_json(items, f"domain_{safe}.json")

    # RAG-ready (slim, for vector embedding)
    rag = [{
        "id": e.id,
        "title": e.title,
        "domain": e.domain,
        "subdomain": e.subdomain,
        "dadi_story": e.dadi_story,
        "summary": e.summary,
        "health_benefits": e.health_benefits,
        "contraindications": e.contraindications,
        "ingredients": e.ingredients,
        "remedy_steps": e.remedy_steps,
        "yoga_poses": e.yoga_poses,
        "scientific_backing": e.scientific_backing,
        "pubmed_abstracts": e.pubmed_abstracts,
        "modern_relevance": e.modern_relevance,
        "keywords": e.keywords,
        "gen_z_hook": e.gen_z_hook,
        "dosha_type": e.dosha_type,
        "taste_rasa": e.taste_rasa,
        "potency_virya": e.potency_virya,
        "seasonal_relevance": e.seasonal_relevance,
        "authenticity_score": e.authenticity_score,
        "regional_names": e.regional_names,
        "source": e.source_url,
        "source_type": e.data_source_type,
        "image_url": e.image_url,
    } for e in entries]
    save_json(rag, "chatbot_rag_knowledge_base.json")

    # Semantic search index (flat text, one entry per line — for embedding pipelines)
    with open(os.path.join(OUTPUT_DIR, "semantic_index.jsonl"), "w", encoding="utf-8") as f:
        for e in entries:
            doc = {
                "id": e.id,
                "text": f"{e.title}. {e.summary} {' '.join(e.health_benefits)} {' '.join(e.keywords)}",
                "metadata": {"domain": e.domain, "subdomain": e.subdomain, "source": e.source_url}
            }
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    # Prompt-ready plain text (for direct Claude/GPT context injection)
    chunks = []
    for e in entries:
        parts = [f"TITLE: {e.title}", f"DOMAIN: {e.domain}/{e.subdomain}"]
        if e.summary:
            parts.append(f"SUMMARY: {e.summary[:600]}")
        if e.dadi_story:
            parts.append(f"DADI STORY: {e.dadi_story[:400]}")
        if e.ingredients:
            parts.append(f"INGREDIENTS: {', '.join(e.ingredients)}")
        if e.remedy_steps:
            steps = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(e.remedy_steps))
            parts.append(f"HOW TO USE:\n{steps}")
        if e.health_benefits:
            parts.append(f"HEALTH BENEFITS: {', '.join(e.health_benefits)}")
        if e.contraindications:
            parts.append(f"CONTRAINDICATIONS: {'; '.join(e.contraindications[:3])}")
        if e.scientific_backing:
            parts.append(f"SCIENCE: {'; '.join(e.scientific_backing[:3])}")
        if e.dosha_type:
            parts.append(f"DOSHA: {e.dosha_type}")
        if e.regional_names:
            rn = ", ".join(f"{k}: {v}" for k, v in e.regional_names.items())
            parts.append(f"REGIONAL NAMES: {rn}")
        if e.gen_z_hook:
            parts.append(f"GEN_Z_HOOK: {e.gen_z_hook}")
        parts.append(f"AUTHENTICITY: {e.authenticity_score}")
        parts.append(f"SOURCE: {e.source_url}")
        chunks.append("\n".join(parts))

    with open(os.path.join(OUTPUT_DIR, "prompt_ready.txt"), "w", encoding="utf-8") as f:
        f.write("\n\n---\n\n".join(chunks))

    log.info(f"All outputs saved to {OUTPUT_DIR}/")

# ─────────────────────────────────────────────
#  STATS
# ─────────────────────────────────────────────
def print_stats(entries: list):
    print("\n" + "═" * 65)
    print("  🌿  DADI KI BAATEIN — Knowledge Base v2 Stats")
    print("═" * 65)
    print(f"  Total entries          : {len(entries)}")
    domain_counts = {}
    for e in entries:
        domain_counts[e.domain] = domain_counts.get(e.domain, 0) + 1
    print("\n  By Domain:")
    for d, c in sorted(domain_counts.items(), key=lambda x: -x[1]):
        bar = "█" * min(c, 30)
        print(f"    {d:<35} {c:>4}  {bar}")
    src_counts = {}
    for e in entries:
        src_counts[e.data_source_type] = src_counts.get(e.data_source_type, 0) + 1
    print("\n  By Source Type:")
    for t, c in sorted(src_counts.items(), key=lambda x: -x[1]):
        print(f"    {t:<25} {c:>4}")
    avg = sum(e.authenticity_score for e in entries) / max(len(entries), 1)
    print(f"\n  Avg authenticity score : {avg:.2f} / 1.00")
    print(f"  With remedy steps      : {sum(1 for e in entries if e.remedy_steps)}")
    print(f"  With ingredients       : {sum(1 for e in entries if e.ingredients)}")
    print(f"  With science backing   : {sum(1 for e in entries if e.scientific_backing)}")
    print(f"  With PubMed abstracts  : {sum(1 for e in entries if e.pubmed_abstracts)}")
    print(f"  With regional names    : {sum(1 for e in entries if e.regional_names)}")
    print(f"  With contraindications : {sum(1 for e in entries if e.contraindications)}")
    print(f"  With images            : {sum(1 for e in entries if e.image_url)}")
    print("═" * 65 + "\n")

# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Dadi Ki Baatein — Mega Scraper v2")
    parser.add_argument("--seed-only",     action="store_true", help="Only seed data")
    parser.add_argument("--no-wikipedia",  action="store_true", help="Skip Wikipedia")
    parser.add_argument("--no-static",     action="store_true", help="Skip static sites")
    parser.add_argument("--no-selenium",   action="store_true", help="Skip JS sites")
    parser.add_argument("--pubmed",        action="store_true", help="Fetch PubMed abstracts")
    parser.add_argument("--sparql",        action="store_true", help="Fetch Wikidata/DBpedia")
    args = parser.parse_args()

    all_entries, seen_ids = [], set()

    def add(e):
        if e and e.id not in seen_ids:
            seen_ids.add(e.id)
            all_entries.append(e)

    # Phase 1: Seed
    print("\n🌿  Phase 1: Curated Seed Knowledge Base")
    for e in load_seed_data():
        add(e)
    print(f"  ✅ {len(all_entries)} seed entries loaded")

    if args.seed_only:
        save_all_outputs(all_entries)
        print_stats(all_entries)
        return

    # Phase 2: Wikipedia
    if not args.no_wikipedia:
        print(f"\n🌿  Phase 2: Wikipedia ({len(WIKIPEDIA_TOPICS)} topics)")
        for page_title, domain, subdomain in tqdm(WIKIPEDIA_TOPICS, desc="Wikipedia"):
            add(scrape_wikipedia(page_title, domain, subdomain))
            time.sleep(0.4)

    # Phase 3: Static Sites
    if not args.no_static:
        print(f"\n🌿  Phase 3: Static Websites ({len(STATIC_SITES)} sites)")
        for site in tqdm(STATIC_SITES, desc="Static sites"):
            add(scrape_static_site(site))
            time.sleep(1.5)

    # Phase 4: PubMed
    if args.pubmed:
        print(f"\n🌿  Phase 4: PubMed Abstracts ({len(PUBMED_QUERIES)} queries)")
        for q in tqdm(PUBMED_QUERIES, desc="PubMed"):
            for e in scrape_pubmed(q, max_results=3):
                add(e)
            time.sleep(0.5)

    # Phase 5: SPARQL
    if args.sparql:
        print("\n🌿  Phase 5: Wikidata & DBpedia SPARQL")
        print("  Fetching Wikidata herb data...")
        for e in tqdm(scrape_wikidata_herbs(), desc="Wikidata"):
            add(e)
        time.sleep(2)
        print("  Fetching DBpedia Indian knowledge data...")
        for e in tqdm(scrape_dbpedia_indian_knowledge(), desc="DBpedia"):
            add(e)

    # Phase 6: Selenium
    if not args.no_selenium:
        if not SELENIUM_OK:
            print("\n⚠️  Selenium not installed. Skipping JS sites.")
        else:
            print(f"\n🌿  Phase 6: JS-Rendered Sites ({len(JS_SITES)} sites)")
            driver = get_selenium_driver()
            if driver:
                try:
                    for site in tqdm(JS_SITES, desc="JS sites"):
                        add(scrape_with_selenium(driver, site))
                        time.sleep(3)
                finally:
                    driver.quit()

    save_all_outputs(all_entries)
    print_stats(all_entries)
    print(f"\n✅  Saved to → {OUTPUT_DIR}/")
    print("   Files:")
    print("     knowledge_base_full.json      — Complete data")
    print("     chatbot_rag_knowledge_base.json — Slim RAG format")
    print("     semantic_index.jsonl           — One line per entry for embedding")
    print("     prompt_ready.txt               — Plain text for LLM context")
    print("     domain_*.json                  — Per-domain files\n")


if __name__ == "__main__":
    main()