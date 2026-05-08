"""
╔══════════════════════════════════════════════════════════════════════╗
║     DADI KI BAATEIN — Knowledge Base Builder v3.0                    ║
║     Handles JS-rendered sites + Wikipedia API + Seed Data            ║
╚══════════════════════════════════════════════════════════════════════╝

INSTALL DEPENDENCIES FIRST:
    pip install requests beautifulsoup4 lxml tqdm wikipedia-api selenium

FOR JS SITES (indianculture.gov.in):
    Install ChromeDriver: https://chromedriver.chromium.org/
    OR run in --no-selenium mode which uses Wikipedia + seed data only

USAGE:
    python knowledge_scraper_v2.py              # full mode (needs ChromeDriver)
    python knowledge_scraper_v2.py --no-selenium # Wikipedia + seed only
"""

import requests
import json
import time
import re
import os
import hashlib
import logging
import argparse
import random
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
    import wikipediaapi
    WIKI_OK = True
except ImportError:
    WIKI_OK = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
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

# ─────────────────────────────────────────────
#  DATA MODEL
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
    health_benefits: list = field(default_factory=list)
    ingredients: list = field(default_factory=list)
    remedy_steps: list = field(default_factory=list)
    yoga_poses: list = field(default_factory=list)
    seasonal_relevance: str = ""
    dosha_type: str = ""
    modern_relevance: list = field(default_factory=list)
    keywords: list = field(default_factory=list)
    source_url: str = ""
    source_name: str = ""
    scraped_at: str = ""
    authenticity_score: float = 0.0
    gen_z_hook: str = ""
    language_origin: str = "Sanskrit/Hindi"
    data_source_type: str = ""  # "wikipedia", "selenium", "seed", "static"

# ─────────────────────────────────────────────
#  WIKIPEDIA TOPICS (comprehensive list)
# ─────────────────────────────────────────────
WIKIPEDIA_TOPICS = [
    # Ayurveda systems
    ("Ayurveda",               "Ayurveda",         "Ayurvedic System"),
    ("Dosha",                  "Ayurveda",         "Tridosha Theory"),
    ("Panchakarma",            "Ayurveda",         "Detox Therapies"),
    ("Dinacharya",             "Ayurveda",         "Daily Routine"),
    ("Rasayana (Ayurveda)",    "Ayurveda",         "Rejuvenation"),
    ("Charaka Samhita",        "Ancient Texts",    "Classical Texts"),
    ("Sushruta Samhita",       "Ancient Texts",    "Classical Texts"),
    ("Ashtanga Hridayam",      "Ancient Texts",    "Classical Texts"),

    # Individual herbs and plants
    ("Withania somnifera",     "Ayurveda",         "Ashwagandha"),
    ("Ocimum tenuiflorum",     "Ayurveda",         "Tulsi / Holy Basil"),
    ("Turmeric",               "Ayurveda",         "Haldi"),
    ("Azadirachta indica",     "Ayurveda",         "Neem"),
    ("Triphala",               "Ayurveda",         "Herbal Formulas"),
    ("Phyllanthus emblica",    "Ayurveda",         "Amla"),
    ("Tinospora cordifolia",   "Ayurveda",         "Giloy"),
    ("Bacopa monnieri",        "Ayurveda",         "Brahmi"),
    ("Zingiber officinale",    "Ayurveda",         "Ginger"),
    ("Curcumin",               "Ayurveda",         "Active Compounds"),
    ("Moringa oleifera",       "Ayurveda",         "Drumstick Tree"),
    ("Shatavari",              "Ayurveda",         "Women's Health"),
    ("Nigella sativa",         "Ayurveda",         "Kalonji"),
    ("Centella asiatica",      "Ayurveda",         "Gotu Kola"),

    # Yoga
    ("Yoga",                   "Yoga",             "Overview"),
    ("Pranayama",              "Yoga",             "Breathing Techniques"),
    ("Surya Namaskar",         "Yoga",             "Sequences"),
    ("Hatha yoga",             "Yoga",             "Physical Yoga"),
    ("Kundalini yoga",         "Yoga",             "Energy Yoga"),
    ("Ashtanga vinyasa yoga",  "Yoga",             "Dynamic Yoga"),
    ("Chakra",                 "Yoga",             "Energy Centers"),
    ("Mudra",                  "Yoga",             "Hand Gestures"),
    ("Meditation",             "Yoga",             "Dhyana"),
    ("Vipassanā",              "Yoga",             "Meditation Techniques"),

    # Indian medicine systems
    ("Siddha medicine",        "Siddha",           "Overview"),
    ("Unani medicine",         "Unani",            "Overview"),
    ("Naturopathy",            "Naturopathy",      "Overview"),

    # Food and culture
    ("Indian cuisine",         "Food & Culture",   "Overview"),
    ("Ghee",                   "Food & Culture",   "Sacred Foods"),
    ("Sattvic diet",           "Food & Culture",   "Ayurvedic Diet"),
    ("Fermentation in food",   "Food & Culture",   "Traditional Preservation"),
    ("Spice",                  "Food & Culture",   "Spice Knowledge"),
    ("Fasting",                "Food & Culture",   "Ritualistic Practices"),

    # Farming
    ("Zero Budget Natural Farming",      "Sustainable Farming", "Modern Methods"),
    ("Organic farming",                  "Sustainable Farming", "Overview"),
    ("Biodynamic agriculture",           "Sustainable Farming", "Holistic Farming"),
    ("Crop rotation",                    "Sustainable Farming", "Soil Health"),

    # Astronomy and mathematics
    ("Hindu astrology",        "Ancient Astronomy",    "Jyotisha"),
    ("Indian mathematics",     "Vedic Mathematics",    "Overview"),
    ("Aryabhata",              "Ancient Astronomy",    "Ancient Scholars"),
    ("Brahmagupta",            "Vedic Mathematics",    "Ancient Scholars"),
    ("Vedic Mathematics",      "Vedic Mathematics",    "Modern Vedic Math"),

    # Cultural practices
    ("Panchang",               "Oral History",         "Calendar System"),
    ("Rangoli",                "Arts & Culture",       "Folk Arts"),
    ("Indian classical dance", "Arts & Culture",       "Performing Arts"),
    ("Carnatic music",         "Arts & Culture",       "Music Tradition"),
    ("Oral tradition",         "Oral History",         "Storytelling"),
    ("Folklore of India",      "Oral History",         "Folk Stories"),
]

# ─────────────────────────────────────────────
#  CURATED SEED KNOWLEDGE BASE
#  Used as fallback or to enrich scraped data
# ─────────────────────────────────────────────
SEED_KNOWLEDGE = [
    {
        "title": "Turmeric Milk (Haldi Doodh) — Golden Milk",
        "domain": "Home Remedies",
        "subdomain": "Immunity & Cold",
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
        "scientific_backing": [
            "Curcumin: Potent anti-inflammatory and antioxidant compound",
            "Piperine: Increases curcumin bioavailability by up to 2000%",
            "Anti-inflammatory: Reduces cytokine activity",
            "Antibacterial: Effective against many strains",
        ],
        "dosha_type": "All doshas (tridoshic)",
        "seasonal_relevance": "Winter",
        "modern_relevance": ["Immunity Boosting", "Anti-aging", "Sleep Wellness"],
        "gen_z_hook": "Golden Milk was trending on TikTok in 2020 — your dadi was making it in 1960 💛",
        "source_name": "Traditional Ayurvedic Knowledge (Seed)",
        "source_url": "https://www.tkdl.res.in",
        "keywords": ["turmeric", "curcumin", "haldi", "golden milk", "immunity", "inflammation"],
    },
    {
        "title": "Tulsi (Holy Basil) — The Queen of Herbs",
        "domain": "Ayurveda",
        "subdomain": "Adaptogenic Herbs",
        "summary": "Ocimum tenuiflorum, known as Tulsi, is considered the most sacred plant in Ayurveda. It is a potent adaptogen that helps the body respond to stress, has antimicrobial properties, and supports respiratory health.",
        "ingredients": ["Tulsi leaves", "Honey", "Ginger", "Black Pepper"],
        "remedy_steps": [
            "Collect 8-10 fresh Tulsi leaves in the morning (best harvested before noon)",
            "Boil in 2 cups of water with 2 slices of ginger for 5 minutes",
            "Strain and add a pinch of black pepper",
            "Sweeten with honey after cooling to below 40°C",
            "Drink twice daily during cold, fever, or stress",
            "For skin: apply fresh Tulsi paste to acne or insect bites"
        ],
        "health_benefits": ["Immunity", "Stress", "Respiratory", "Skin", "Fever", "Anxiety"],
        "scientific_backing": [
            "Adaptogen: Modulates the HPA axis and stress response hormones",
            "Antibacterial: Eugenol and other volatile oils fight bacteria",
            "Antiviral: Active against HSV and other common viruses",
            "Immunomodulatory: Upregulates T-helper cell activity",
        ],
        "dosha_type": "Vata, Kapha",
        "seasonal_relevance": "Monsoon, Winter",
        "modern_relevance": ["Immunity Boosting", "Mental Health", "Gut Health"],
        "gen_z_hook": "Adaptogens are a $14 billion wellness industry. Tulsi did it first, for free, in your courtyard 🌿",
        "source_name": "TKDL Traditional Knowledge (Seed)",
        "source_url": "https://www.tkdl.res.in",
        "keywords": ["tulsi", "holy basil", "adaptogen", "eugenol", "stress", "antiviral"],
    },
    {
        "title": "Ashwagandha — Ancient Adaptogen for Stress & Vitality",
        "domain": "Ayurveda",
        "subdomain": "Rasayana (Rejuvenation)",
        "summary": "Withania somnifera is one of Ayurveda's most prized rasayana herbs. Its name means 'smell of horse' — implying it gives the strength and vitality of a horse. Modern research confirms its powerful cortisol-lowering, muscle-building, and neuroprotective effects.",
        "ingredients": ["Ashwagandha root powder", "Warm Milk", "Honey", "Ghee"],
        "remedy_steps": [
            "Take 1/4 to 1/2 tsp of ashwagandha root powder",
            "Mix into warm milk with a small amount of ghee",
            "Add honey to taste after mixing (do not cook honey)",
            "Consume before bedtime for 3 months minimum (rasayana requires sustained use)",
            "Alternatively: capsule form 300-600mg standardised to withanolides daily",
            "Best taken with food to avoid stomach upset"
        ],
        "health_benefits": ["Stress", "Anxiety", "Memory", "Energy", "Sleep", "Testosterone", "Immunity"],
        "scientific_backing": [
            "Withanolide: Primary bioactive; significant cortisol reduction in RCTs",
            "Adaptogen: Modulates HPA-axis response to chronic stress",
            "Neuroprotective: Promotes dendrite and axon growth in neurons",
            "Immunomodulatory: Increases NK cell activity",
            "Analgesic: COX-2 inhibition similar to NSAIDs",
        ],
        "dosha_type": "Vata, Kapha",
        "seasonal_relevance": "Winter",
        "modern_relevance": ["Mental Health", "Fitness & Yoga", "Immunity Boosting", "Sleep Wellness"],
        "gen_z_hook": "Andrew Huberman's top supplement? Ashwagandha. Your great-great-grandmother's top supplement? Also Ashwagandha. 🐴",
        "source_name": "Ayurvedic Classical Texts (Seed)",
        "source_url": "https://www.tkdl.res.in",
        "keywords": ["ashwagandha", "withania", "withanolide", "adaptogen", "cortisol", "rasayana"],
    },
    {
        "title": "Triphala — Three-Fruit Formula for Complete Wellness",
        "domain": "Ayurveda",
        "subdomain": "Herbal Formulas",
        "summary": "Triphala ('three fruits') is a classical Ayurvedic formulation of Amla (Phyllanthus emblica), Haritaki (Terminalia chebula), and Bibhitaki (Terminalia bellirica). It is considered one of the most important formulas in all of Ayurvedic medicine — balancing all three doshas and supporting digestion, detoxification, and eye health.",
        "ingredients": ["Amla (Indian Gooseberry)", "Haritaki", "Bibhitaki"],
        "remedy_steps": [
            "Mix 1/2 tsp Triphala powder in warm water",
            "Drink at bedtime on an empty stomach for digestive benefits",
            "For eye wash: brew 1 tsp in 2 cups water, cool completely, strain through cloth, use as eyewash",
            "For oral health: mix with sesame oil for oil pulling",
            "Take consistently for 3 months for full digestive reset",
            "Reduce dose if loose stools occur (sign it is working)"
        ],
        "health_benefits": ["Digestion", "Detox", "Immunity", "Eye Health", "Dental", "Weight", "Skin"],
        "scientific_backing": [
            "Antioxidant: Among the highest ORAC values of any plant compound",
            "Antibacterial: Effective against Staph aureus and E. coli",
            "Hepatoprotective: Protects liver cells from oxidative damage",
            "Anti-inflammatory: Inhibits NF-κB pathway",
            "Prebiotic: Increases beneficial Bifidobacterium and Lactobacillus",
        ],
        "dosha_type": "All doshas (tridoshic)",
        "seasonal_relevance": "All seasons",
        "modern_relevance": ["Gut Health", "Detox", "Skincare", "Immunity Boosting"],
        "gen_z_hook": "One formula balancing ALL three body types = the original personalised medicine 🫙",
        "source_name": "Charaka Samhita (Seed)",
        "source_url": "https://www.tkdl.res.in",
        "keywords": ["triphala", "amla", "haritaki", "bibhitaki", "digestion", "detox", "tridoshic"],
    },
    {
        "title": "Kapalbhati Pranayama — Skull-Shining Breath",
        "domain": "Yoga",
        "subdomain": "Pranayama",
        "summary": "Kapalbhati is a powerful breathing technique from Hatha Yoga where the emphasis is on forceful exhalations. 'Kapal' means skull, 'bhati' means shining — regular practice is said to make the face luminous. Modern research confirms benefits for lung function, metabolism, and parasympathetic activation.",
        "ingredients": [],
        "remedy_steps": [
            "Sit in Padmasana or Sukhasana with spine straight",
            "Take a deep inhale to prepare",
            "Exhale sharply through the nose by contracting the abdomen inward",
            "Allow inhalation to happen passively as the abdomen releases",
            "Start with 30 rounds, gradually increase to 120 rounds per minute",
            "Do 3-5 sets with 1 minute rest between sets",
            "Best practised on empty stomach in early morning",
            "AVOID if pregnant, have hypertension, or recent abdominal surgery"
        ],
        "yoga_poses": ["Kapalbhati", "Padmasana", "Sukhasana"],
        "health_benefits": ["Digestion", "Weight", "Metabolism", "Lungs", "Energy", "Stress", "Skin"],
        "scientific_backing": [
            "Improves FEV1 and peak expiratory flow rate in pulmonary studies",
            "Activates parasympathetic nervous system post-practice",
            "Increases core temperature and metabolic rate",
            "Strengthens transversus abdominis (deep core muscle)",
        ],
        "dosha_type": "Kapha (especially beneficial)",
        "seasonal_relevance": "All seasons",
        "modern_relevance": ["Fitness & Yoga", "Gut Health", "Mental Health", "Detox"],
        "gen_z_hook": "Free, equipment-free metabolism hack your ancestors used before Ozempic existed 💨",
        "source_name": "Hatha Yoga Pradipika (Seed)",
        "source_url": "https://www.yogamdniy.nic.in",
        "keywords": ["kapalbhati", "pranayama", "breathing", "metabolism", "kapal", "skull shining"],
    },
    {
        "title": "Anulom Vilom — Alternate Nostril Breathing",
        "domain": "Yoga",
        "subdomain": "Pranayama",
        "summary": "Nadi Shodhana Pranayama (alternate nostril breathing) is one of the most studied yoga breathing techniques. By alternating breath between left (Ida nadi - lunar/parasympathetic) and right (Pingala nadi - solar/sympathetic) nostrils, it balances the two hemispheres of the brain and the autonomic nervous system.",
        "ingredients": [],
        "remedy_steps": [
            "Sit comfortably, use Vishnu mudra (fold index and middle finger of right hand)",
            "Close right nostril with thumb, inhale through left nostril for 4 counts",
            "Close both nostrils, hold for 4 counts (optional — skip if hypertensive)",
            "Release thumb, close left nostril with ring finger, exhale through right for 8 counts",
            "Inhale through right for 4 counts",
            "Close both, hold 4 counts",
            "Exhale through left for 8 counts — this completes one full cycle",
            "Do 10-20 cycles daily. Build over weeks"
        ],
        "yoga_poses": ["Anulom Vilom", "Nadi Shodhana", "Vishnu Mudra", "Padmasana"],
        "health_benefits": ["Stress", "Anxiety", "Blood Pressure", "Sleep", "Memory", "Lungs"],
        "scientific_backing": [
            "Activates parasympathetic nervous system, reducing cortisol",
            "EEG studies show increased alpha wave activity post-practice",
            "Significantly reduces systolic and diastolic blood pressure",
            "Improves spatial memory and reaction time in RCTs",
        ],
        "dosha_type": "All doshas",
        "seasonal_relevance": "All seasons",
        "modern_relevance": ["Mental Health", "Sleep Wellness", "Fitness & Yoga"],
        "gen_z_hook": "Box breathing for Navy SEALs is basically Anulom Vilom. We just named it better. 🫁",
        "source_name": "Yoga Sutras of Patanjali (Seed)",
        "source_url": "https://www.yogamdniy.nic.in",
        "keywords": ["anulom vilom", "nadi shodhana", "alternate nostril", "pranayama", "brain balance"],
    },
    {
        "title": "Neem — Village Pharmacy in a Tree",
        "domain": "Ayurveda",
        "subdomain": "Medicinal Trees",
        "summary": "Azadirachta indica (Neem) has been called the 'village pharmacy' of India. Every part of the tree — leaves, bark, seeds, oil — has documented medicinal uses. It is the world's most researched botanical with over 4000 published studies.",
        "ingredients": ["Neem leaves", "Neem bark", "Neem oil", "Neem powder"],
        "remedy_steps": [
            "For skin infections: grind fresh neem leaves into paste, apply to affected area for 20 min",
            "For dental health: chew neem twig daily as natural toothbrush (antimicrobial)",
            "For blood purification: boil 10 leaves in water, drink on empty stomach (3 weeks max)",
            "For hair: mix neem oil with coconut oil, massage scalp, leave 30 min before washing",
            "For wounds: apply diluted neem leaf paste as natural antiseptic dressing",
            "WARNING: Do NOT consume neem oil internally — only leaves and bark are for internal use"
        ],
        "health_benefits": ["Skin", "Dental", "Hair", "Immunity", "Blood Purification", "Wounds", "Allergy"],
        "scientific_backing": [
            "Nimbin and Nimbidin: Primary antibacterial and antifungal compounds",
            "Azadirachtin: Powerful natural pesticide (safe for humans)",
            "Anti-inflammatory: Inhibits PGE2 synthesis",
            "Antibacterial: Effective against Streptococcus mutans (dental cavities)",
            "Antifungal: Effective against Candida species",
        ],
        "dosha_type": "Pitta, Kapha",
        "seasonal_relevance": "Summer, Monsoon",
        "modern_relevance": ["Skincare", "Haircare", "Immunity Boosting", "Sustainability"],
        "gen_z_hook": "The most researched plant on Earth grows for free in every Indian village. No patent possible. 🌳",
        "source_name": "TKDL + Charaka Samhita (Seed)",
        "source_url": "https://www.tkdl.res.in",
        "keywords": ["neem", "azadirachta", "nimbin", "antibacterial", "dental", "skin", "village pharmacy"],
    },
    {
        "title": "Surya Namaskar — The Complete Body Workout",
        "domain": "Yoga",
        "subdomain": "Sequences",
        "summary": "Surya Namaskar (Sun Salutation) is a 12-step yoga sequence traditionally performed at sunrise. It is a complete cardiovascular, flexibility, and strength workout that activates every major muscle group and organ system. 12 rounds = 288 yoga postures completed in under 15 minutes.",
        "ingredients": [],
        "remedy_steps": [
            "Step 1 - Pranamasana: Stand at mat's edge, join palms at chest, exhale",
            "Step 2 - Hastauttanasana: Raise arms overhead, arch back gently, inhale",
            "Step 3 - Hasta Padasana: Fold forward, hands to floor by feet, exhale",
            "Step 4 - Ashwa Sanchalanasana: Step right foot back, left knee down, inhale",
            "Step 5 - Dandasana: Both feet back, plank position, hold breath",
            "Step 6 - Ashtanga Namaskara: Knees-chest-chin to floor, exhale",
            "Step 7 - Bhujangasana: Slide forward, cobra pose, inhale",
            "Step 8 - Adho Mukha Svanasana: Downward dog, exhale",
            "Steps 9-12: Mirror steps 4-1 back to start, completing the cycle",
            "One full round = left side + right side. Start with 2 rounds, build to 12"
        ],
        "yoga_poses": ["Surya Namaskar", "Pranamasana", "Bhujangasana", "Adho Mukha", "Dandasana", "Balasana"],
        "health_benefits": ["Flexibility", "Strength", "Metabolism", "Stress", "Energy", "Skin", "Digestion"],
        "scientific_backing": [
            "12 rounds burns ~150 calories — equivalent to jogging 1.5km",
            "Increases cortisol morning peak alignment with circadian rhythm",
            "Improves VO2 max with 3-month regular practice (RCT evidence)",
            "Reduces anxiety scores on GAD-7 scale significantly",
        ],
        "dosha_type": "All doshas",
        "seasonal_relevance": "All seasons (sunrise practice)",
        "modern_relevance": ["Fitness & Yoga", "Mental Health", "Metabolism", "Sustainability"],
        "gen_z_hook": "A 5000-year-old HIIT routine that needs no gym membership or equipment. 🌅",
        "source_name": "Traditional Yoga Texts (Seed)",
        "source_url": "https://www.yogamdniy.nic.in",
        "keywords": ["surya namaskar", "sun salutation", "yoga", "full body", "sequence", "morning routine"],
    },
    {
        "title": "Kadha — Immunity Decoction for Colds and Flu",
        "domain": "Home Remedies",
        "subdomain": "Respiratory Health",
        "summary": "Kadha (also Kwath) is a traditional Ayurvedic herbal decoction made by boiling multiple medicinal ingredients in water until reduced. It became famous during COVID-19 when the Ministry of AYUSH officially recommended it as an immunity booster.",
        "ingredients": ["Tulsi", "Ginger", "Black Pepper", "Cinnamon", "Clove", "Turmeric", "Honey"],
        "remedy_steps": [
            "Boil 2 cups water with 4-5 Tulsi leaves",
            "Add 1/2 inch fresh ginger (grated or sliced)",
            "Add 2-3 black peppercorns, 1 small cinnamon stick, 2 cloves",
            "Add 1/4 tsp turmeric powder",
            "Simmer for 8-10 minutes until liquid reduces to 1 cup",
            "Strain, let cool to warm (not hot), add 1 tsp honey",
            "Drink twice daily at the first sign of cold or during flu season",
            "Children's dose: half quantity, ensure it is not too spicy"
        ],
        "health_benefits": ["Immunity", "Cold", "Cough", "Respiratory", "Fever", "Throat", "Digestion"],
        "scientific_backing": [
            "Eugenol (cloves): Antibacterial against respiratory pathogens",
            "Gingerol (ginger): Anti-inflammatory, anti-nausea, antiviral",
            "Cinnamaldehyde: Antifungal and antibacterial",
            "Curcumin (turmeric): Broad-spectrum anti-inflammatory",
            "Piperine (pepper): Bioavailability enhancer for all active compounds",
        ],
        "dosha_type": "Kapha (especially for respiratory Kapha excess)",
        "seasonal_relevance": "Winter, Monsoon",
        "modern_relevance": ["Immunity Boosting", "Gut Health", "Mental Health"],
        "gen_z_hook": "The WHO promoted this in 2020. Your nani was making it in 1970. Zero lag, infinite wisdom. ☕",
        "source_name": "AYUSH Ministry + Traditional Knowledge (Seed)",
        "source_url": "https://main.ayush.gov.in",
        "keywords": ["kadha", "kwath", "decoction", "immunity", "cold", "ayush", "covid remedy"],
    },
    {
        "title": "Chyawanprash — Original Superfood Formula",
        "domain": "Ayurveda",
        "subdomain": "Rasayana (Rejuvenation)",
        "summary": "Chyawanprash is the oldest known health supplement in the world, first described in the Charaka Samhita (~ 600 BCE). It is a jam-like preparation based primarily on Amla (Indian gooseberry) with 35-50 additional herbs. It is named after sage Chyawan who was said to have regained his youth using it.",
        "ingredients": ["Amla", "Ashwagandha", "Shatavari", "Ghee", "Honey", "Sesame Oil", "Long Pepper"],
        "remedy_steps": [
            "Traditional preparation requires 35+ herbs — store-bought versions are fine",
            "Adults: 1-2 tsp with warm milk every morning before breakfast",
            "Children (5-12 years): 1/2 tsp with milk",
            "Elderly: 1 tsp twice daily, morning and evening",
            "Continue for minimum 3 months for rasayana (rejuvenation) effects",
            "Summer: take with cold milk to prevent heat; Winter: take with warm milk"
        ],
        "health_benefits": ["Immunity", "Memory", "Energy", "Lungs", "Skin", "Digestion", "Metabolism"],
        "scientific_backing": [
            "Amla: Highest natural source of Vitamin C (600mg per 100g — 20x orange)",
            "Adaptogenic complex: Multiple adaptogens act synergistically",
            "Antioxidant: Polyphenol density reduces oxidative stress markers",
            "Immunomodulatory: Increases IgG and IgM antibody titers",
        ],
        "dosha_type": "All doshas (tridoshic)",
        "seasonal_relevance": "Winter, Monsoon",
        "modern_relevance": ["Immunity Boosting", "Mental Health", "Skincare", "Energy"],
        "gen_z_hook": "The world's oldest known health supplement is Indian and is 2600 years old. SuperGreens can sit down. 🍃",
        "source_name": "Charaka Samhita + TKDL (Seed)",
        "source_url": "https://www.tkdl.res.in",
        "keywords": ["chyawanprash", "amla", "rasayana", "immunity", "vitamin c", "superfood", "charaka"],
    },
    {
        "title": "Dinacharya — Ayurvedic Daily Routine",
        "domain": "Ayurveda",
        "subdomain": "Lifestyle Medicine",
        "summary": "Dinacharya describes the ideal Ayurvedic daily routine — a 24-hour framework for optimal health. It synchronises human biology with the rhythms of nature and the sun. Modern chronobiology is now confirming many of its practices including wake time, meal timing, and sleep windows.",
        "ingredients": ["Sesame Oil (for oil pulling)", "Neem twig", "Copper tongue scraper"],
        "remedy_steps": [
            "Brahma muhurta wake-up: Rise 90 minutes before sunrise (~4:30-5:30am)",
            "Eliminate naturally and drink 2 cups of warm water (ushapan)",
            "Tongue scraping: 7 strokes with copper scraper from back to tip",
            "Oil pulling (gandusha): 1 tbsp sesame oil, swish 10-20 minutes, spit, do NOT swallow",
            "Abhyanga: Self-massage with warm sesame oil before shower",
            "Exercise/yoga during Kapha time (6-10am)",
            "Main meal at midday (when digestive fire is strongest)",
            "Light dinner before 7pm, no food after",
            "Screen-free wind-down by 9pm, sleep by 10pm (Pitta time begins)"
        ],
        "health_benefits": ["Digestion", "Sleep", "Energy", "Skin", "Dental", "Mental Health", "Immunity"],
        "scientific_backing": [
            "Circadian biology confirms eating in alignment with daylight reduces metabolic syndrome risk",
            "Oil pulling: Saponification destroys bacterial cell membranes (peer-reviewed)",
            "Abhyanga: Reduces cortisol and improves lymphatic drainage",
            "Sleep by 10pm aligns with natural melatonin peak window",
        ],
        "dosha_type": "All doshas",
        "seasonal_relevance": "All seasons (adjustments per season)",
        "modern_relevance": ["Mental Health", "Sleep Wellness", "Gut Health", "Skincare", "Fitness & Yoga"],
        "gen_z_hook": "Biohackers spend $10,000 on devices to optimise what Ayurveda nailed 3000 years ago for free. 🕰️",
        "source_name": "Ashtanga Hridayam (Seed)",
        "source_url": "https://www.tkdl.res.in",
        "keywords": ["dinacharya", "daily routine", "oil pulling", "abhyanga", "circadian", "tongue scraping", "brahma muhurta"],
    },
    {
        "title": "Zero Budget Natural Farming (ZBNF) — Subhash Palekar",
        "domain": "Sustainable Farming",
        "subdomain": "Modern Traditional Methods",
        "summary": "Developed by Padma Shri Subhash Palekar, ZBNF is inspired by ancient Indian Vedic farming traditions. It uses cow dung and urine from indigenous Desi cattle (not hybrid), jaggery, and pulse flour to create 'Jeevamrit' — a fermented microbial inoculant that dramatically boosts soil health.",
        "ingredients": ["Cow dung (desi cow)", "Cow urine", "Jaggery", "Pulse flour (gram)", "Soil"],
        "remedy_steps": [
            "Jeevamrit preparation: Mix 10kg fresh cow dung + 10L cow urine in 200L water",
            "Add 2kg jaggery + 2kg pulse flour (besan/gram flour)",
            "Add one handful of soil from under an old tree (native microbes)",
            "Stir clockwise for 5 minutes, ferment under shade for 48 hours, stirring twice daily",
            "Dilute 10% solution and apply to crops through drip irrigation or spraying",
            "Apply every 15 days as a soil drench",
            "Bijamrit (seed treatment): 500g cow dung + 1L cow urine + 50g lime, coat seeds before planting"
        ],
        "health_benefits": ["Soil Health", "Crop Yield", "Biodiversity", "Water Retention"],
        "scientific_backing": [
            "Increases soil microbial diversity by 10-15x (bioinformatics studies)",
            "Reduces input costs to near zero vs. chemical farming",
            "Maintains yield parity with chemical farming in 3-year transition studies",
            "Humus formation: increases water retention by 20-30%",
        ],
        "seasonal_relevance": "All seasons",
        "modern_relevance": ["Sustainability", "Climate Resilience", "Zero-waste"],
        "gen_z_hook": "Regenerative farming is trending in Silicon Valley. Indian farmers invented it 5000 years ago. 🐄",
        "source_name": "Subhash Palekar ZBNF + Vedic Agricultural Texts (Seed)",
        "source_url": "https://zerobudgetfarming.com",
        "keywords": ["zbnf", "natural farming", "jeevamrit", "subhash palekar", "cow dung", "organic", "regenerative"],
    },
    {
        "title": "Abhyanga — Ayurvedic Self-Massage",
        "domain": "Ayurveda",
        "subdomain": "Daily Practices",
        "summary": "Abhyanga is the daily self-massage with warm oil, a cornerstone of Ayurvedic dinacharya. Charaka states it prevents aging (jaravyapeta), relieves fatigue, and calms Vata dosha. Modern research confirms it reduces cortisol, improves sleep quality, and enhances lymphatic circulation.",
        "ingredients": ["Sesame Oil (Vata)", "Coconut Oil (Pitta)", "Mustard Oil (Kapha)"],
        "remedy_steps": [
            "Choose oil based on dosha: sesame for Vata, coconut for Pitta, mustard for Kapha",
            "Warm the oil gently (test on wrist — should be comfortably warm)",
            "Apply to scalp first with circular movements, then ears",
            "Massage down the neck and shoulders with long strokes",
            "Work chest, abdomen in clockwise circular motion (following digestion direction)",
            "Long strokes on arms and legs, circular at joints",
            "Massage feet thoroughly, including between toes",
            "Leave oil on for 15-20 minutes (longer for dry skin/Vata types)",
            "Shower with warm water using minimal soap to preserve the oil's effect"
        ],
        "health_benefits": ["Skin", "Sleep", "Stress", "Joint Pain", "Immunity", "Energy", "Circulation"],
        "scientific_backing": [
            "Reduces cortisol levels comparable to Swedish massage",
            "Increases oxytocin and serotonin production",
            "Improves lymphatic drainage in perioperative studies",
            "Sesame oil: Lignans (sesamin) have antioxidant and antibacterial properties",
        ],
        "dosha_type": "Vata (primary), all doshas with appropriate oil",
        "seasonal_relevance": "All seasons",
        "modern_relevance": ["Skincare", "Sleep Wellness", "Mental Health", "Fitness & Yoga"],
        "gen_z_hook": "Luxury spas charge ₹5000 for what your dadi called Tuesday morning. 🫒",
        "source_name": "Charaka Samhita + Ashtanga Hridayam (Seed)",
        "source_url": "https://www.tkdl.res.in",
        "keywords": ["abhyanga", "self massage", "sesame oil", "vata", "daily routine", "lymphatic", "skin"],
    },
]

# ─────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────
def make_id(url: str, title: str) -> str:
    return hashlib.md5(f"{url}_{title}".encode()).hexdigest()[:12]

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()

STOPWORDS = {
    "their","there","which","about","these","those","would","could","should",
    "other","often","using","being","having","where","while","since","after",
    "before","during","through","between","because","therefore","however",
    "although","within","without","against","across","along","among","around"
}

def extract_keywords(text: str, top_n: int = 20) -> list:
    words = re.findall(r"\b[a-zA-Z]{5,}\b", text.lower())
    freq = {}
    for w in words:
        if w not in STOPWORDS:
            freq[w] = freq.get(w, 0) + 1
    return sorted(freq, key=freq.get, reverse=True)[:top_n]

DADI_INTROS = [
    "Baith mere paas, sunle ek baat... ",
    "Sit down child, let Dadi tell you something important... ",
    "Arey, you think this is just old talk? Listen carefully... ",
    "Beta, our ancestors knew things modern science is only now catching up to... ",
    "Close your phone for a second, this story is worth more than any reel... ",
]
DADI_CLOSINGS = [
    " — You see, they hid science inside daily rituals so we would never forget.",
    " — Every ritual has a reason. Every spice has a purpose. That is the wisdom of our people.",
    " — They did not need labs. They had thousands of years of careful observation and love.",
    " — The secret was always that our ancestors were not superstitious — they were scientists without the vocabulary.",
]

def generate_dadi_story(title: str, summary: str, domain: str) -> str:
    intro = random.choice(DADI_INTROS)
    closing = random.choice(DADI_CLOSINGS)
    return f"{intro}{summary[:400]}{closing}"

GEN_Z_HOOKS = {
    "Ayurveda":           "Your ancestors had personalised medicine 5000 years before Goop. 💚",
    "Yoga":               "Ancient biohacking, no subscription required. 🧘",
    "Home Remedies":      "Kitchen pharmacies that actually work — no side effects attached. 🍯",
    "Food & Culture":     "This carries 3000 years of ancestral memory. No cap. 🌶️",
    "Sustainable Farming":"Zero-waste farming, invented before zero-waste was a trend. 🌱",
    "Oral History":       "This survived 40 generations. Hear it before it disappears. 📖",
    "Ancient Astronomy":  "They mapped the cosmos without telescopes. Lowkey insane. ✨",
    "Vedic Mathematics":  "Mental math shortcuts that make calculators look slow. 🧮",
    "Siddha":             "Tamil medicine was practised for 10,000 years before colonisation tried to erase it. 🌺",
    "Unani":              "The world's first universal healthcare system, from Hakim to patient. 🌿",
}

def get_gen_z_hook(domain: str, title: str) -> str:
    return GEN_Z_HOOKS.get(domain, "This wisdom survived centuries. Time to keep it alive. 🙏")

def score_authenticity(e: KnowledgeEntry) -> float:
    score = 0.0
    if e.ingredients:               score += 0.15
    if e.remedy_steps:              score += 0.20
    if e.scientific_backing:        score += 0.20
    if e.dosha_type:                score += 0.10
    if e.keywords:                  score += 0.10
    if len(e.raw_content) > 300:    score += 0.10
    if e.seasonal_relevance:        score += 0.05
    if e.health_benefits:           score += 0.10
    return round(min(score, 1.0), 2)

# ─────────────────────────────────────────────
#  WIKIPEDIA SCRAPER  (Action API)
# ─────────────────────────────────────────────
DOMAIN_RULES = {
    "Ayurveda":           ["ayurveda","vata","pitta","kapha","herb","turmeric","tulsi","neem","ashwagandha","triphala","ghee","kadha","dosha","rasayana"],
    "Yoga":               ["yoga","asana","pranayama","meditation","surya","chakra","mudra","dhyana","prana","hatha","kundalini"],
    "Home Remedies":      ["remedy","cure","paste","decoction","honey","ginger","garlic","pepper","apply","consume","mix","boil"],
    "Sustainable Farming":["farming","agriculture","soil","crop","seed","organic","compost","cow dung","natural farming"],
    "Ancient Astronomy":  ["astronomy","jyotisha","nakshatra","graha","panchang","vedic astronomy","aryabhata"],
    "Vedic Mathematics":  ["vedic math","sutra","aryabhata","brahmagupta","mathematics"],
    "Food & Culture":     ["food","recipe","cuisine","spice","masala","ferment","pickle","sattvic","fasting"],
    "Oral History":       ["folklore","legend","myth","oral tradition","ritual","festival","custom"],
    "Siddha":             ["siddha","siddhar","tamil medicine"],
    "Unani":              ["unani","hakeem","tibb","greco"],
}

def detect_domain(text: str, default: str = "Traditional Knowledge") -> str:
    t = text.lower()
    scores = {d: sum(1 for kw in kws if kw in t) for d, kws in DOMAIN_RULES.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else default

INGREDIENTS_LIST = [
    "turmeric","haldi","ginger","adrak","tulsi","neem","ashwagandha","amla","giloy",
    "brahmi","triphala","honey","ghee","milk","coconut oil","sesame oil","black pepper",
    "cumin","coriander","fenugreek","mustard","cinnamon","cardamom","clove","nutmeg",
    "saffron","aloe vera","moringa","curry leaves","peppercorn","long pepper","garlic",
    "lemon","pomegranate","sandalwood","rose water","haritaki","bibhitaki","manjistha",
]

def extract_ingredients(text: str) -> list:
    t = text.lower()
    return list({ing.title() for ing in INGREDIENTS_LIST if ing in t})

YOGA_POSES = [
    "tadasana","vrikshasana","trikonasana","adho mukha","uttanasana","virabhadrasana",
    "balasana","savasana","padmasana","siddhasana","bhujangasana","dhanurasana",
    "halasana","sarvangasana","sirsasana","sukhasana","vajrasana","kapalbhati",
    "anulom vilom","bhastrika","nadi shodhana","surya namaskar",
]

def extract_yoga_poses(text: str) -> list:
    t = text.lower()
    return list({p.title() for p in YOGA_POSES if p in t})

SCIENCE_TERMS = {
    "antibacterial":"Fights harmful bacteria",
    "antimicrobial":"Kills microorganisms",
    "anti-inflammatory":"Reduces inflammation",
    "antioxidant":"Fights free radicals / cell aging",
    "adaptogen":"Helps body adapt to stress",
    "immunomodulatory":"Boosts immune system",
    "hepatoprotective":"Protects the liver",
    "neuroprotective":"Protects brain cells",
    "analgesic":"Pain-relieving",
    "curcumin":"Active in turmeric (anti-inflammatory)",
    "gingerol":"Active in ginger (antinausea)",
    "withanolide":"Active in ashwagandha (adaptogen)",
    "allicin":"Active in garlic (antibacterial)",
    "eugenol":"Active in cloves (antimicrobial)",
}

def extract_science(text: str) -> list:
    t = text.lower()
    return [f"{k.title()}: {v}" for k, v in SCIENCE_TERMS.items() if k in t]

HEALTH_KEYWORDS = [
    "immunity","digestion","sleep","stress","anxiety","memory","skin","hair",
    "joint","pain","fever","cold","cough","diabetes","blood pressure","cholesterol",
    "weight","energy","detox","liver","kidney","heart","wounds","inflammation",
]

def extract_health(text: str) -> list:
    t = text.lower()
    return [kw.title() for kw in HEALTH_KEYWORDS if kw in t]

MODERN_TAGS = {
    "Immunity Boosting":["immunity","immune","resistance","viral"],
    "Mental Health":    ["stress","anxiety","depression","mental"],
    "Gut Health":       ["digestion","gut","probiotic","microbiome"],
    "Skincare":         ["skin","glow","acne","complexion"],
    "Haircare":         ["hair","scalp","dandruff"],
    "Sustainability":   ["sustainable","eco","organic","zero waste"],
    "Sleep Wellness":   ["sleep","insomnia","rest","melatonin"],
    "Fitness & Yoga":   ["fitness","yoga","asana","flexibility"],
    "Detox":            ["detox","cleanse","purify","toxin"],
}

def detect_modern(text: str) -> list:
    t = text.lower()
    return [tag for tag, terms in MODERN_TAGS.items() if any(term in t for term in terms)]

def detect_dosha(text: str) -> str:
    t = text.lower()
    doshas = [d for d in ["vata","pitta","kapha"] if d in t]
    return ", ".join(d.title() for d in doshas)

SEASONAL_MAP = {
    "Winter":  ["winter","shishir","cold","december","january","february"],
    "Summer":  ["summer","grishma","heat","may","june"],
    "Monsoon": ["monsoon","rainy","varsha","july","august","september"],
    "Spring":  ["spring","vasant","march","april"],
}

def detect_season(text: str) -> str:
    t = text.lower()
    for season, terms in SEASONAL_MAP.items():
        if any(term in t for term in terms):
            return season
    return "All seasons"

def make_entry_from_text(title, content, source_url, source_name,
                          default_domain, data_source_type="wikipedia") -> KnowledgeEntry:
    domain = detect_domain(content, default_domain)
    summary_sentences = re.split(r"(?<=[.!?])\s+", content)
    summary = " ".join([s for s in summary_sentences if len(s) > 40][:3])

    e = KnowledgeEntry(
        id=make_id(source_url, title),
        title=title,
        domain=domain,
        subdomain=default_domain,
        dadi_story=generate_dadi_story(title, summary, domain),
        summary=summary,
        raw_content=content[:3000],
        scientific_backing=extract_science(content),
        health_benefits=extract_health(content),
        ingredients=extract_ingredients(content),
        remedy_steps=[],  # Wikipedia does not have structured steps
        yoga_poses=extract_yoga_poses(content),
        seasonal_relevance=detect_season(content),
        dosha_type=detect_dosha(content),
        modern_relevance=detect_modern(content),
        keywords=extract_keywords(content),
        source_url=source_url,
        source_name=source_name,
        scraped_at=datetime.now().isoformat(),
        gen_z_hook=get_gen_z_hook(domain, title),
        data_source_type=data_source_type,
    )
    e.authenticity_score = score_authenticity(e)
    return e

# ─────────────────────────────────────────────
#  WIKIPEDIA SCRAPER
# ─────────────────────────────────────────────
def scrape_wikipedia(page_title: str, domain: str, subdomain: str) -> Optional[KnowledgeEntry]:
    """Fetch a Wikipedia article via the Action API (no scraping needed)."""
    api_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": page_title,
        "prop": "extracts",
        "explaintext": True,
        "exsectionformat": "plain",
    }
    headers = {
        "User-Agent": "DadiKiBaatein/1.0 Hackathon Project (https://github.com/your-repo) contact@example.com"
    }
    try:
        r = requests.get(api_url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        pages = data.get("query", {}).get("pages", {})
        for pid, page in pages.items():
            if pid == "-1":
                log.warning(f"Wikipedia: page not found — {page_title}")
                return None
            content = clean_text(page.get("extract", ""))
            if len(content) < 200:
                log.warning(f"Wikipedia: too short — {page_title}")
                return None
            wiki_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
            return make_entry_from_text(
                title=page.get("title", page_title),
                content=content,
                source_url=wiki_url,
                source_name=f"Wikipedia — {page_title}",
                default_domain=domain,
                data_source_type="wikipedia"
            )
    except Exception as e:
        log.error(f"Wikipedia API error for '{page_title}': {e}")
        return None

# ─────────────────────────────────────────────
#  SELENIUM SCRAPER (for JS-rendered sites)
# ─────────────────────────────────────────────
JS_SITES = [
    {"name": "Indian Cultural Portal - Ayurveda",
     "url":  "https://www.indianculture.gov.in/ayurveda",
     "domain": "Ayurveda",
     "wait_selector": "div.field-items, article, main, .content"},
    {"name": "Indian Cultural Portal - Yoga",
     "url":  "https://www.indianculture.gov.in/yoga",
     "domain": "Yoga",
     "wait_selector": "div.field-items, article, main, .content"},
    {"name": "Indian Cultural Portal - Indian Knowledge Systems",
     "url":  "https://www.indianculture.gov.in/indian-knowledge-systems",
     "domain": "Indian Knowledge Systems",
     "wait_selector": "div.field-items, article, main, .content"},
    {"name": "Indian Cultural Portal - Manuscripts",
     "url":  "https://www.indianculture.gov.in/manuscripts",
     "domain": "Ancient Texts",
     "wait_selector": "div.field-items, article, main, .content"},
    {"name": "TKDL - Traditional Knowledge",
     "url":  "https://www.tkdl.res.in/tkdl/langdefault/common/Home.asp?GL=Eng",
     "domain": "Traditional Knowledge",
     "wait_selector": "table, div, p"},
    {"name": "AYUSH - Ayurveda",
     "url":  "https://main.ayush.gov.in/ayurveda",
     "domain": "Ayurveda",
     "wait_selector": "article, main, .field-body, .view-content"},
    {"name": "AYUSH - Yoga",
     "url":  "https://main.ayush.gov.in/yoga-naturopathy",
     "domain": "Yoga",
     "wait_selector": "article, main, .field-body, .view-content"},
    {"name": "Morarji Desai Yoga Institute",
     "url":  "https://www.yogamdniy.nic.in/",
     "domain": "Yoga",
     "wait_selector": "article, main, div.content, #content"},
]

def get_selenium_driver() -> Optional["webdriver.Chrome"]:
    if not SELENIUM_OK:
        return None
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280,800")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        log.error(f"Selenium ChromeDriver not found: {e}")
        log.info("Install ChromeDriver: https://chromedriver.chromium.org/downloads")
        return None

def scrape_with_selenium(driver, site: dict) -> Optional[KnowledgeEntry]:
    try:
        driver.get(site["url"])
        time.sleep(3)  # wait for JS to render

        # Try to extract text from best content areas
        soup = BeautifulSoup(driver.page_source, "lxml")

        # Try multiple selectors in order of specificity
        for selector in ["article", "main", ".field-items", ".node__content",
                          ".view-content", "#content", "body"]:
            el = soup.select_one(selector)
            if el:
                paras = el.find_all(["p", "li", "h2", "h3", "h4"])
                content = " ".join(clean_text(p.get_text()) for p in paras if len(p.get_text()) > 30)
                if len(content) > 200:
                    title_el = soup.select_one("h1, h2, .page-title")
                    title = clean_text(title_el.get_text()) if title_el else site["name"]
                    return make_entry_from_text(
                        title=title,
                        content=content,
                        source_url=site["url"],
                        source_name=site["name"],
                        default_domain=site["domain"],
                        data_source_type="selenium"
                    )

        log.warning(f"Selenium: too little content at {site['url']}")
        return None
    except Exception as e:
        log.error(f"Selenium error for {site['url']}: {e}")
        return None

# ─────────────────────────────────────────────
#  SEED DATA LOADER
# ─────────────────────────────────────────────
def load_seed_data() -> list:
    entries = []
    for item in SEED_KNOWLEDGE:
        content = item.get("summary", "") + " " + " ".join(item.get("remedy_steps", []))
        e = KnowledgeEntry(
            id=make_id(item.get("source_url", "seed"), item["title"]),
            title=item["title"],
            domain=item["domain"],
            subdomain=item.get("subdomain", ""),
            dadi_story=generate_dadi_story(item["title"], item.get("summary", ""), item["domain"]),
            summary=item.get("summary", ""),
            raw_content=content,
            scientific_backing=item.get("scientific_backing", []),
            health_benefits=item.get("health_benefits", []),
            ingredients=item.get("ingredients", []),
            remedy_steps=item.get("remedy_steps", []),
            yoga_poses=item.get("yoga_poses", []),
            seasonal_relevance=item.get("seasonal_relevance", ""),
            dosha_type=item.get("dosha_type", ""),
            modern_relevance=item.get("modern_relevance", []),
            keywords=item.get("keywords", extract_keywords(content)),
            source_url=item.get("source_url", ""),
            source_name=item.get("source_name", ""),
            scraped_at=datetime.now().isoformat(),
            gen_z_hook=item.get("gen_z_hook", get_gen_z_hook(item["domain"], item["title"])),
            data_source_type="seed",
        )
        e.authenticity_score = score_authenticity(e)
        entries.append(e)
    return entries

# ─────────────────────────────────────────────
#  SAVE FUNCTIONS
# ─────────────────────────────────────────────
def save_json(data: list, filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    log.info(f"Saved {len(data)} entries → {path}")

def save_all_outputs(entries: list):
    all_dicts = [asdict(e) for e in entries]

    # Full database
    save_json(all_dicts, "knowledge_base_full.json")

    # Per-domain files
    domain_map = {}
    for e in entries:
        domain_map.setdefault(e.domain, []).append(asdict(e))
    for domain, items in domain_map.items():
        safe = re.sub(r"[^\w]", "_", domain).lower()
        save_json(items, f"domain_{safe}.json")

    # Chatbot-ready (slim RAG format)
    rag_records = [{
        "id": e.id,
        "title": e.title,
        "domain": e.domain,
        "subdomain": e.subdomain,
        "dadi_story": e.dadi_story,
        "summary": e.summary,
        "health_benefits": e.health_benefits,
        "ingredients": e.ingredients,
        "remedy_steps": e.remedy_steps,
        "yoga_poses": e.yoga_poses,
        "scientific_backing": e.scientific_backing,
        "modern_relevance": e.modern_relevance,
        "keywords": e.keywords,
        "gen_z_hook": e.gen_z_hook,
        "dosha_type": e.dosha_type,
        "seasonal_relevance": e.seasonal_relevance,
        "authenticity_score": e.authenticity_score,
        "source": e.source_url,
        "data_source_type": e.data_source_type,
    } for e in entries]
    save_json(rag_records, "chatbot_knowledge_base.json")

    # Prompt-ready text format for direct LLM use
    prompt_texts = []
    for e in entries:
        parts = [f"TITLE: {e.title}", f"DOMAIN: {e.domain}"]
        if e.summary:
            parts.append(f"SUMMARY: {e.summary}")
        if e.ingredients:
            parts.append(f"INGREDIENTS: {', '.join(e.ingredients)}")
        if e.remedy_steps:
            steps_str = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(e.remedy_steps))
            parts.append(f"HOW TO USE:\n{steps_str}")
        if e.health_benefits:
            parts.append(f"HEALTH BENEFITS: {', '.join(e.health_benefits)}")
        if e.scientific_backing:
            parts.append(f"SCIENCE: {'; '.join(e.scientific_backing)}")
        if e.dosha_type:
            parts.append(f"DOSHA: {e.dosha_type}")
        if e.gen_z_hook:
            parts.append(f"GEN_Z_HOOK: {e.gen_z_hook}")
        parts.append(f"SOURCE: {e.source_url}")
        prompt_texts.append("\n".join(parts))

    with open(os.path.join(OUTPUT_DIR, "prompt_ready.txt"), "w", encoding="utf-8") as f:
        f.write("\n\n---\n\n".join(prompt_texts))
    log.info(f"Saved prompt_ready.txt → {OUTPUT_DIR}/")

# ─────────────────────────────────────────────
#  STATS REPORTER
# ─────────────────────────────────────────────
def print_stats(entries: list):
    print("\n" + "═" * 60)
    print("  📚  DADI KI BAATEIN — Knowledge Base Stats")
    print("═" * 60)
    print(f"  Total entries          : {len(entries)}")

    domain_counts = {}
    for e in entries:
        domain_counts[e.domain] = domain_counts.get(e.domain, 0) + 1
    print("\n  By Domain:")
    for d, c in sorted(domain_counts.items(), key=lambda x: -x[1]):
        bar = "█" * c
        print(f"    {d:<30} {c:>3}  {bar}")

    source_types = {}
    for e in entries:
        source_types[e.data_source_type] = source_types.get(e.data_source_type, 0) + 1
    print("\n  By Source Type:")
    for t, c in sorted(source_types.items(), key=lambda x: -x[1]):
        print(f"    {t:<20} {c:>3}")

    avg = sum(e.authenticity_score for e in entries) / max(len(entries), 1)
    print(f"\n  Avg authenticity score : {avg:.2f} / 1.00")
    print(f"  With remedy steps      : {sum(1 for e in entries if e.remedy_steps)}")
    print(f"  With ingredients       : {sum(1 for e in entries if e.ingredients)}")
    print(f"  With science backing   : {sum(1 for e in entries if e.scientific_backing)}")
    print(f"  With yoga poses        : {sum(1 for e in entries if e.yoga_poses)}")
    print(f"  With dosha type        : {sum(1 for e in entries if e.dosha_type)}")
    print("═" * 60 + "\n")

# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Dadi Ki Baatein Knowledge Scraper")
    parser.add_argument("--no-selenium", action="store_true",
                        help="Skip JS-rendered sites (no ChromeDriver needed)")
    parser.add_argument("--no-wikipedia", action="store_true",
                        help="Skip Wikipedia scraping")
    parser.add_argument("--seed-only", action="store_true",
                        help="Only load the built-in seed knowledge base")
    args = parser.parse_args()

    all_entries = []
    seen_ids = set()

    def add_entry(e):
        if e and e.id not in seen_ids:
            seen_ids.add(e.id)
            all_entries.append(e)

    # ── Phase 1: Seed Data (always runs) ────────────────────────────
    print("\n🌿  Phase 1: Loading Curated Seed Knowledge Base\n")
    seed_entries = load_seed_data()
    for e in seed_entries:
        add_entry(e)
    print(f"  ✅ Loaded {len(seed_entries)} seed entries")

    if args.seed_only:
        save_all_outputs(all_entries)
        print_stats(all_entries)
        return

    # ── Phase 2: Wikipedia API ───────────────────────────────────────
    if not args.no_wikipedia:
        print("\n🌿  Phase 2: Wikipedia API Scraping\n")
        for page_title, domain, subdomain in tqdm(WIKIPEDIA_TOPICS, desc="Wikipedia"):
            e = scrape_wikipedia(page_title, domain, subdomain)
            if e:
                add_entry(e)
            time.sleep(0.5)  # be polite to Wikipedia API

    # ── Phase 3: Selenium for JS sites ──────────────────────────────
    if not args.no_selenium:
        if not SELENIUM_OK:
            print("\n⚠️  Selenium not installed. Run: pip install selenium")
            print("   Also install ChromeDriver: https://chromedriver.chromium.org/")
        else:
            print("\n🌿  Phase 3: JS-Rendered Sites (Selenium)\n")
            driver = get_selenium_driver()
            if driver:
                try:
                    for site in tqdm(JS_SITES, desc="JS Sites"):
                        e = scrape_with_selenium(driver, site)
                        if e:
                            add_entry(e)
                        time.sleep(2)
                finally:
                    driver.quit()
            else:
                print("  ⚠️  ChromeDriver not found. Skipping JS sites.")
                print("  Install from: https://chromedriver.chromium.org/downloads")

    # ── Save & Report ────────────────────────────────────────────────
    save_all_outputs(all_entries)
    print_stats(all_entries)
    print(f"✅  Saved to → {OUTPUT_DIR}/")
    print("   Files: knowledge_base_full.json | chatbot_knowledge_base.json | prompt_ready.txt\n")


if __name__ == "__main__":
    main()