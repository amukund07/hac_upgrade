"""
╔══════════════════════════════════════════════════════════════════════════╗
║   DADI KI BAATEIN — MEGA Knowledge Base Builder v4.0                     ║
║   Target: 500+ rich entries across 20+ domains                           ║
║                                                                          ║
║   NEW IN v4:                                                             ║
║   • 400+ curated seed entries (herbs, remedies, yoga, food, stories)     ║
║   • 80+ Wikipedia topics with full-text extraction                       ║
║   • Selenium for JS-rendered govt sites                                  ║
║   • Multi-language support (Sanskrit terms preserved)                    ║
║   • Vector embedding preparation (chunk + embed-ready)                   ║
║   • JSONL export for fine-tuning LLMs                                    ║
║   • CSV export for spreadsheet analysis                                  ║
║   • Markdown export (one file per entry — for Obsidian/Notion)          ║
║   • SQLite database for fast querying                                    ║
║   • Tag taxonomy with 50+ tags                                           ║
║   • Rasa NLU training data export                                        ║
║   • Chatbot persona script generator                                     ║
║   • Conflict/duplication detector                                        ║
║   • Safety flags (contraindications, warnings)                           ║
║                                                                          ║
║   INSTALL:                                                               ║
║     pip install requests beautifulsoup4 lxml tqdm selenium               ║
║   OPTIONAL (for embeddings):                                             ║
║     pip install sentence-transformers                                    ║
║   USAGE:                                                                 ║
║     python dadi_mega.py                  # full run                      ║
║     python dadi_mega.py --seed-only      # instant, no network needed    ║
║     python dadi_mega.py --no-selenium    # skip JS sites                 ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

# ─────────────────────────────────────────────────────────────────────────────
#  IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
import requests, json, time, re, os, hashlib, logging, argparse, random
import csv, sqlite3, textwrap
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import Optional
from pathlib import Path
from tqdm import tqdm

try:
    from bs4 import BeautifulSoup
    BS4_OK = True
except ImportError:
    BS4_OK = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    SELENIUM_OK = True
except ImportError:
    SELENIUM_OK = False

# ─────────────────────────────────────────────────────────────────────────────
#  LOGGING & DIRECTORIES
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("dadi_scraper.log"), logging.StreamHandler()]
)
log = logging.getLogger(__name__)

BASE   = Path("data/dadi_knowledge_base")
DIRS   = ["json", "markdown", "csv", "sqlite", "jsonl",
          "training_data", "domain_files", "embeddings"]
for d in DIRS:
    (BASE / d).mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
#  DATA MODEL  (v4 — extended)
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class KnowledgeEntry:
    # Core identity
    id:                  str  = ""
    title:               str  = ""
    title_sanskrit:      str  = ""   # Sanskrit/Hindi name
    domain:              str  = ""
    subdomain:           str  = ""
    tags:               list  = field(default_factory=list)  # 50-tag taxonomy

    # Content
    dadi_story:          str  = ""   # grandma storytelling voice
    summary:             str  = ""   # 2-3 sentence plain summary
    raw_content:         str  = ""   # full scraped/seed text
    origin_story:        str  = ""   # historical/mythological origin
    how_it_was_forgotten: str = ""   # why modern India forgot this

    # Ayurvedic metadata
    dosha_type:          str  = ""   # Vata / Pitta / Kapha
    body_system:        list  = field(default_factory=list)  # digestive, nervous, ...
    age_group:          list  = field(default_factory=list)  # children, adults, elderly
    gender_notes:        str  = ""   # any gender-specific info
    season_best:         str  = ""
    time_of_day:         str  = ""   # morning / evening / anytime

    # Practical knowledge
    ingredients:        list  = field(default_factory=list)
    ingredient_quantities: dict = field(default_factory=dict)  # ingredient → quantity
    remedy_steps:       list  = field(default_factory=list)
    duration:            str  = ""   # "3 weeks", "daily for 3 months"
    dosage:              str  = ""
    preparation_time:    str  = ""

    # Yoga/Movement
    yoga_poses:         list  = field(default_factory=list)
    breathing_type:      str  = ""
    difficulty_level:    str  = ""   # beginner / intermediate / advanced

    # Safety
    contraindications:  list  = field(default_factory=list)   # NEW — critical
    side_effects:       list  = field(default_factory=list)   # NEW
    drug_interactions:  list  = field(default_factory=list)   # NEW
    warnings:           list  = field(default_factory=list)   # NEW

    # Science & validation
    scientific_backing: list  = field(default_factory=list)
    active_compounds:   list  = field(default_factory=list)   # NEW — curcumin, withanolide etc
    research_status:     str  = ""   # "well-researched" / "preliminary" / "traditional only"
    pubmed_keywords:    list  = field(default_factory=list)   # NEW — for finding studies

    # Benefits
    health_benefits:    list  = field(default_factory=list)
    mental_benefits:    list  = field(default_factory=list)   # NEW
    spiritual_benefits: list  = field(default_factory=list)   # NEW

    # Culture & stories
    regional_variant:    str  = ""   # regional variations
    state_of_origin:     str  = ""   # Tamil Nadu, Rajasthan etc
    language_origin:     str  = "Sanskrit"
    related_festival:    str  = ""   # Diwali, Pongal etc
    oral_story_snippet:  str  = ""   # the actual folk story/legend
    grandmother_quote:   str  = ""   # a memorable one-liner from Dadi

    # Engagement
    modern_relevance:   list  = field(default_factory=list)
    gen_z_hook:          str  = ""
    tiktok_angle:        str  = ""   # NEW — short video angle
    challenge_idea:      str  = ""   # NEW — gamification challenge idea
    daily_habit_tip:     str  = ""   # NEW — how to make it a daily habit
    difficulty_to_adopt: str  = ""   # "easy" / "medium" / "hard"

    # Metadata
    keywords:           list  = field(default_factory=list)
    source_url:          str  = ""
    source_name:         str  = ""
    scraped_at:          str  = ""
    authenticity_score: float = 0.0
    data_source_type:    str  = ""   # seed / wikipedia / selenium
    verified:           bool  = False
    last_updated:        str  = ""

# ─────────────────────────────────────────────────────────────────────────────
#  TAG TAXONOMY  (50+ tags for filtering in chatbot)
# ─────────────────────────────────────────────────────────────────────────────
ALL_TAGS = [
    # Health goals
    "immunity","digestion","sleep","stress","anxiety","memory","skin","hair",
    "weight-loss","detox","energy","pain-relief","diabetes","heart-health",
    "liver-health","kidney-health","eye-health","dental-health","bone-health",
    "respiratory","reproductive-health","menstrual-health","hormonal-balance",
    # Practice type
    "home-remedy","yoga","pranayama","meditation","massage","diet",
    "herbal","ritual","exercise","fasting","oil-pulling",
    # Ayurveda-specific
    "vata","pitta","kapha","rasayana","panchakarma","dinacharya","tridoshic",
    # Accessibility
    "zero-cost","kitchen-ingredients","5-minutes","daily-habit","beginner-friendly",
    # Culture
    "vedic","folk-story","festival","regional","sanskrit","oral-tradition",
    # Audience
    "for-children","for-elderly","for-women","for-men","for-athletes",
    # Evidence
    "science-backed","traditional-only","who-validated","ayush-approved",
]

def auto_tag(e: "KnowledgeEntry") -> list:
    tags = set()
    text = (e.summary + " " + " ".join(e.health_benefits) + " " +
            " ".join(e.scientific_backing) + " " + e.dosha_type).lower()

    tag_map = {
        "immunity":        ["immunity","immune"],
        "digestion":       ["digestion","digestive","gut"],
        "sleep":           ["sleep","insomnia"],
        "stress":          ["stress","cortisol"],
        "anxiety":         ["anxiety","calm"],
        "memory":          ["memory","brain","neuro"],
        "skin":            ["skin","glow","acne"],
        "hair":            ["hair","scalp"],
        "detox":           ["detox","cleanse","toxin"],
        "energy":          ["energy","fatigue","vitality"],
        "vata":            ["vata"],
        "pitta":           ["pitta"],
        "kapha":           ["kapha"],
        "tridoshic":       ["tridoshic","all doshas"],
        "rasayana":        ["rasayana","rejuvenat"],
        "science-backed":  ["curcumin","withanolide","gingerol","eugenol","adaptogen",
                            "antibacterial","anti-inflammatory","antioxidant"],
        "yoga":            ["asana","yoga","surya namaskar"],
        "pranayama":       ["pranayama","breathing","breath"],
        "meditation":      ["meditation","dhyana","mindful"],
        "home-remedy":     ["remedy","remedies","paste","decoction","kadha"],
        "kitchen-ingredients":["turmeric","ginger","honey","garlic","neem","tulsi"],
        "zero-cost":       ["free","no cost","kitchen","garden"],
        "for-women":       ["women","menstrual","pregnancy","shatavari","lactation"],
        "for-children":    ["children","child","kids"],
        "for-elderly":     ["elderly","aging","old age","senior"],
        "festival":        ["diwali","pongal","holi","navratri","festival"],
        "folk-story":      ["story","legend","myth","folklore","grandmother"],
        "ayush-approved":  ["ayush","ministry","government"],
        "who-validated":   ["who","world health organization"],
    }
    for tag, keywords in tag_map.items():
        if any(kw in text for kw in keywords):
            tags.add(tag)

    if e.domain == "Yoga":             tags.add("yoga")
    if e.domain == "Ayurveda":         tags.add("rasayana")
    if e.domain == "Home Remedies":    tags.add("home-remedy")
    if e.domain == "Sustainable Farming": tags.add("zero-cost")
    if e.ingredients and len(e.ingredients) <= 5: tags.add("kitchen-ingredients")
    if e.remedy_steps and len(e.remedy_steps[0]) < 80: tags.add("5-minutes")

    return sorted(tags)

# ─────────────────────────────────────────────────────────────────────────────
#  UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def make_id(url, title):
    return hashlib.md5(f"{url}_{title}".encode()).hexdigest()[:12]

def clean(text):
    text = re.sub(r"\s+", " ", str(text))
    return text.strip()

STOPWORDS = {
    "their","there","which","about","these","those","would","could","should",
    "other","often","using","being","having","where","while","since","after",
    "before","during","through","between","because","therefore","however",
    "although","within","without","against","across","along","among","around",
    "traditional","knowledge","system","india","indian","ancient","practice",
}

def kw(text, n=25):
    words = re.findall(r"\b[a-zA-Z]{5,}\b", text.lower())
    freq = {}
    for w in words:
        if w not in STOPWORDS:
            freq[w] = freq.get(w, 0) + 1
    return sorted(freq, key=freq.get, reverse=True)[:n]

DADI_INTROS = [
    "Aa baith, sunle ek baat jo aaj kal koi nahi sunata... ",
    "Bhai, yeh sun — yeh sirf purani baatein nahi, yeh science hai... ",
    "Sit down child, let Dadi tell you something important... ",
    "Arey, you think this is just superstition? Listen carefully... ",
    "Beta, our ancestors were smarter than we give them credit for... ",
    "Close that phone for one second. This is worth more than any reel... ",
    "You know what your great-great-grandmother used to say every morning?... ",
    "1000 saal pehle, ek vaid ne likha tha — aur woh aaj bhi sach hai... ",
]
DADI_CLOSINGS = [
    " — Yeh sab science hai, bas kapdon mein lipti hui.",
    " — Science was always there, wrapped in stories so children would remember.",
    " — Every ritual has a reason. Every spice has a purpose.",
    " — They didn't need labs. They had 5000 years of careful observation.",
    " — The secret: our ancestors were not superstitious — they were scientists without the vocabulary.",
]

def dadi_story(title, summary, domain):
    return random.choice(DADI_INTROS) + summary[:450] + random.choice(DADI_CLOSINGS)

GEN_Z_HOOKS = {
    "Ayurveda":           "Your ancestors had personalised medicine 5000 years before Goop. 💚",
    "Yoga":               "Ancient biohacking — no subscription, no gym, no equipment. 🧘",
    "Home Remedies":      "Kitchen pharmacy that slaps. Zero side effects. 🍯",
    "Food & Culture":     "This recipe carries 3000 years of ancestral memory. No cap. 🌶️",
    "Sustainable Farming":"Regenerative farming before Silicon Valley made it trendy. 🌱",
    "Oral History":       "This story survived 40 generations. Don't let it die with yours. 📖",
    "Ancient Astronomy":  "They mapped the cosmos without telescopes. Lowkey insane. ✨",
    "Vedic Mathematics":  "Mental math that makes your calculator look slow. 🧮",
    "Siddha":             "Tamil medicine: 10,000 years old and colonisation tried to erase it. 🌺",
    "Unani":              "Greco-Persian medicine adopted and mastered by Indian Hakims for 800 years. 🌿",
    "Naturopathy":        "Healing without pills. Your body knows the way when you help it. 🌊",
    "Tribal Knowledge":   "This knowledge is not in any textbook. Pass it on before it vanishes. 🌾",
}

TIKTOK_ANGLES = {
    "Ayurveda":           "POV: Your grandma knew your 'personalised nutrition plan' 50 years ago",
    "Yoga":               "Things our grandparents did daily that biohackers now charge $200/month for",
    "Home Remedies":      "I tried my dadi's cold remedy. Here's what happened (day 1 vs day 3)",
    "Food & Culture":     "Ancient Indian ingredient that's now in every Whole Foods — and we forgot it first",
    "Sustainable Farming":"This farmer grows 5 crops with zero chemicals and zero bills. How?",
    "Oral History":       "The story my nani told me that I almost let die with her",
}

# ─────────────────────────────────────────────────────────────────────────────
#  CLASSIFIER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
DOMAIN_RULES = {
    "Ayurveda":           ["ayurveda","vata","pitta","kapha","dosha","herb","turmeric",
                           "tulsi","neem","ashwagandha","triphala","ghee","kadha","rasayana",
                           "dinacharya","panchakarma","abhyanga","chyawanprash","amla",
                           "giloy","brahmi","shatavari","haritaki","trikatu"],
    "Yoga":               ["yoga","asana","pranayama","meditation","surya namaskar","chakra",
                           "mudra","dhyana","prana","hatha","kundalini","bandha","samadhi"],
    "Home Remedies":      ["remedy","remedies","cure","paste","decoction","honey","ginger",
                           "garlic","pepper","apply","consume","boil","grind","kadha"],
    "Sustainable Farming":["farming","agriculture","soil","crop","seed","organic","compost",
                           "cow dung","jeevamrit","natural farming","permaculture"],
    "Ancient Astronomy":  ["astronomy","jyotisha","nakshatra","graha","panchang","aryabhata",
                           "vedic astronomy","eclipse","solstice"],
    "Vedic Mathematics":  ["vedic math","sutra","aryabhata","brahmagupta","geometry","sulba"],
    "Food & Culture":     ["food","recipe","cuisine","spice","masala","ferment","pickle",
                           "sattvic","rajasic","fasting","prasad","anna","roti","dal"],
    "Oral History":       ["story","folklore","legend","myth","oral tradition","ritual",
                           "festival","puja","grandmother","nani","dadi","ancestor"],
    "Siddha":             ["siddha","siddhar","tamil medicine","agattiyar","thirumoolar"],
    "Unani":              ["unani","hakeem","tibb","mizaj","ibn sina","avicenna"],
    "Tribal Knowledge":   ["tribal","adivasi","van aushadhi","jungle","forest medicine",
                           "indigenous","folk medicine"],
    "Naturopathy":        ["naturopathy","water cure","mud therapy","sun therapy","fasting cure",
                           "natural healing","hydro"],
    "Arts & Culture":     ["dance","music","art","craft","rangoli","mehndi","kolam",
                           "carnatic","bharatanatyam","kathak","painting","pottery"],
    "Architecture":       ["vastu","temple","architecture","mandala","sacred geometry",
                           "stupa","gopuram","shikhara"],
    "Textile & Craft":    ["weaving","handloom","silk","cotton","khadi","block print",
                           "zari","embroidery","pottery","craft"],
    "Martial Arts":       ["kalaripayattu","silambam","malla","gatka","wrestling","akhara"],
    "Astronomy & Maths":  ["zero","decimal","pi","infinity","binary","fibonacci","pascal"],
}

def classify(text, default="Traditional Knowledge"):
    t = text.lower()
    scores = {d: sum(1 for kw in kws if kw in t) for d, kws in DOMAIN_RULES.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else default

INGREDIENTS_LIST = [
    "turmeric","haldi","ginger","adrak","tulsi","neem","ashwagandha","amla",
    "giloy","brahmi","triphala","honey","ghee","milk","coconut oil","sesame oil",
    "mustard oil","black pepper","cumin","coriander","fenugreek","mustard seeds",
    "cinnamon","cardamom","clove","nutmeg","saffron","aloe vera","moringa",
    "curry leaves","neem leaves","peppercorn","long pepper","dry ginger","garlic",
    "onion","lemon","pomegranate","sandalwood","camphor","rose water","haritaki",
    "bibhitaki","manjistha","shatavari","vidari","guduchi","punarnava","kutki",
    "licorice","mulethi","kalmegh","bhringraj","jatamansi","shankhpushpi",
    "gokshura","shilajit","guggul","trikatu","ajwain","hing","asafoetida",
    "kokum","tamarind","curry powder","jeera","methi","kalonji","nigella",
    "black cumin","bitter gourd","drumstick","neem flower","hibiscus",
    "lotus","marigold","jasmine","rose","chrysanthemum","brahmi leaves",
    "castor oil","neem oil","eucalyptus oil","peppermint oil","lavender",
    "flaxseed","chia","sesame seeds","sunflower seeds","pumpkin seeds",
    "cow urine","cow dung","jaggery","besan","flour","rice","wheat",
]

def get_ingr(text):
    t = text.lower()
    return list({i.title() for i in INGREDIENTS_LIST if i in t})

YOGA_POSES_LIST = [
    "tadasana","vrikshasana","trikonasana","adho mukha svanasana","uttanasana",
    "virabhadrasana i","virabhadrasana ii","virabhadrasana iii","balasana","savasana",
    "padmasana","siddhasana","bhujangasana","dhanurasana","halasana","sarvangasana",
    "sirsasana","sukhasana","vajrasana","kapalbhati","anulom vilom","bhastrika",
    "nadi shodhana","surya namaskar","chandrasana","paschimottanasana","ardha matsyendrasana",
    "gomukhasana","ustrasana","setu bandhasana","chakrasana","mayurasana","bakasana",
    "garudasana","natarajasana","uttita hasta padangusthasana","ardha chandrasana",
    "parivrtta trikonasana","malasana","baddha konasana","upavistha konasana",
    "virasana","supta virasana","matsyasana","janu sirsasana","kurmasana",
]

def get_yoga(text):
    t = text.lower()
    return list({p.title() for p in YOGA_POSES_LIST if p in t})

SCIENCE_TERMS = {
    "antibacterial":    "Fights harmful bacteria",
    "antimicrobial":    "Kills microorganisms broadly",
    "anti-inflammatory":"Reduces inflammation (COX-2 inhibition)",
    "antioxidant":      "Fights free radicals / slows cell aging",
    "antifungal":       "Fights fungal infections",
    "antiviral":        "Helps fight viruses",
    "adaptogen":        "Regulates stress response (HPA axis)",
    "immunomodulatory": "Boosts or regulates immune system",
    "hepatoprotective": "Protects liver cells",
    "neuroprotective":  "Protects and regenerates brain cells",
    "analgesic":        "Reduces pain perception",
    "antipyretic":      "Reduces fever",
    "carminative":      "Reduces gas and bloating",
    "diuretic":         "Increases kidney filtration",
    "emmenagogue":      "Stimulates menstrual flow",
    "galactagogue":     "Promotes breast milk production",
    "rasayana":         "Promotes longevity and rejuvenation",
    "nootropic":        "Enhances cognitive function",
    "curcumin":         "Primary anti-inflammatory in turmeric",
    "gingerol":         "Antinausea and antioxidant compound in ginger",
    "eugenol":          "Antimicrobial compound in cloves and tulsi",
    "withanolide":      "Cortisol-lowering adaptogen in ashwagandha",
    "allicin":          "Antibacterial compound in garlic",
    "quercetin":        "Antiviral and anti-inflammatory flavonoid",
    "piperine":         "Bioavailability enhancer in black pepper",
    "azadirachtin":     "Natural pesticide / antimicrobial in neem",
    "nimbin":           "Anti-inflammatory compound in neem",
    "bacosides":        "Cognitive-enhancing compounds in brahmi",
    "berberine":        "Blood sugar regulating compound in daruharidra",
}

def get_science(text):
    t = text.lower()
    return [f"{k.title()}: {v}" for k, v in SCIENCE_TERMS.items() if k in t]

HEALTH_KW = [
    "immunity","digestion","sleep","stress","anxiety","memory","skin","hair",
    "joint pain","pain","fever","cold","cough","flu","diabetes","blood pressure",
    "cholesterol","weight","metabolism","energy","detox","liver","kidney","heart",
    "lungs","bones","dental","eye","ear","wound","inflammation","allergy",
    "menstrual","fertility","testosterone","hormones","thyroid","depression",
    "focus","concentration","circulation","blood sugar",
]

def get_health(text):
    t = text.lower()
    return [kw.title() for kw in HEALTH_KW if kw in t]

MENTAL_KW = ["anxiety","stress","depression","focus","memory","concentration",
             "clarity","calm","emotional","mood","sleep","mindfulness"]

def get_mental(text):
    t = text.lower()
    return [kw.title() for kw in MENTAL_KW if kw in t]

MODERN_TAGS = {
    "Immunity Boosting":    ["immunity","immune","resistance","viral","covid","flu"],
    "Mental Health":        ["stress","anxiety","depression","mental","mind","cortisol"],
    "Gut Health":           ["digestion","gut","probiotic","microbiome","bowel","ibs"],
    "Skincare":             ["skin","glow","acne","complexion","moistur","wrinkle"],
    "Haircare":             ["hair","scalp","growth","dandruff","follicle","alopecia"],
    "Sustainability":       ["sustainable","eco","natural","organic","zero waste","regenerative"],
    "Sleep Wellness":       ["sleep","insomnia","rest","melatonin","circadian"],
    "Fitness & Yoga":       ["fitness","yoga","asana","flexibility","strength","endurance"],
    "Detox":                ["detox","cleanse","purify","flush","toxin","liver"],
    "Women's Wellness":     ["women","menstrual","pcos","fertility","shatavari","menopause"],
    "Children's Health":    ["children","kids","child","immunity","growth","brain development"],
    "Longevity":            ["aging","anti-aging","longevity","rasayana","rejuvenat"],
    "Mental Performance":   ["memory","focus","brain","nootropic","cognitive","concentration"],
    "Climate Resilience":   ["drought","flood","climate","biodiversity","seed","soil"],
}

def get_modern(text):
    t = text.lower()
    return [tag for tag, terms in MODERN_TAGS.items() if any(term in t for term in terms)]

SEASONAL_MAP = {
    "Winter":  ["winter","shishir","hemant","cold","december","january","february"],
    "Summer":  ["summer","grishma","heat","may","june"],
    "Monsoon": ["monsoon","rainy","varsha","july","august","september"],
    "Spring":  ["spring","vasant","basant","march","april"],
    "Autumn":  ["autumn","sharad","october","november"],
}

def get_season(text):
    t = text.lower()
    for s, kws in SEASONAL_MAP.items():
        if any(kw in t for kw in kws):
            return s
    return "All seasons"

DOSHA_KW = ["vata","pitta","kapha","tridoshic","all doshas"]
def get_dosha(text):
    t = text.lower()
    found = [d.title() for d in DOSHA_KW if d in t]
    return ", ".join(found) if found else ""

CONTRAINDICATION_TRIGGERS = {
    "pregnancy":         ["emmenagogue","during pregnancy","pregnant women should avoid",
                          "abortifacient","uterine stimulant"],
    "hypertension":      ["high blood pressure","hypertension","avoid if hypertensive"],
    "diabetes medication":["blood sugar","hypoglycaemic","metformin","insulin"],
    "anticoagulants":    ["blood thinning","warfarin","clotting","anticoagulant"],
    "children under 5":  ["not for infants","children under 5","avoid in young children"],
    "kidney disease":    ["kidney disease","renal failure","high oxalate","kidney stone"],
    "surgery":           ["before surgery","post-operative","discontinue before"],
    "autoimmune":        ["autoimmune","lupus","rheumatoid","immunosuppressant"],
}

def get_contraindications(text):
    t = text.lower()
    found = []
    for condition, triggers in CONTRAINDICATION_TRIGGERS.items():
        if any(tr in t for tr in triggers):
            found.append(f"Caution: {condition}")
    return found

def score_authenticity(e: KnowledgeEntry) -> float:
    s = 0.0
    if e.ingredients:           s += 0.12
    if e.remedy_steps:          s += 0.18
    if e.scientific_backing:    s += 0.18
    if e.dosha_type:            s += 0.08
    if e.active_compounds:      s += 0.10
    if e.health_benefits:       s += 0.08
    if e.contraindications:     s += 0.08  # safety adds credibility
    if e.origin_story:          s += 0.06
    if len(e.raw_content) > 500: s += 0.07
    if e.seasonal_relevance:    s += 0.05
    return round(min(s, 1.0), 2)

# ─────────────────────────────────────────────────────────────────────────────
#  ░░░  MEGA SEED KNOWLEDGE DATABASE  ░░░
#  400+ entries across: Herbs, Remedies, Yoga, Food, Farming, Stories,
#  Astronomy, Mathematics, Arts, Tribal Knowledge, Siddha, Unani
# ─────────────────────────────────────────────────────────────────────────────
SEED_KNOWLEDGE = [

    # ═══════════════════════════════════════════════════════════════
    #  AYURVEDIC HERBS  (30 entries)
    # ═══════════════════════════════════════════════════════════════
    {
        "title": "Turmeric (Haldi) — The Golden Spice",
        "title_sanskrit": "Haridra (हरिद्रा)",
        "domain": "Ayurveda", "subdomain": "Anti-inflammatory Herbs",
        "summary": "Curcuma longa, known as haldi, is the most studied medicinal plant on Earth with over 12,000 peer-reviewed papers. Its primary compound curcumin is a potent anti-inflammatory, antioxidant, and antimicrobial agent. Ayurveda has used it for 4000+ years for wound healing, digestion, and immunity.",
        "origin_story": "In the Atharva Veda, turmeric is called 'Haridra' — 'the one that heals the body'. It was used in haldi ceremonies before marriage to purify the body and protect from evil spirits — a ritual that doubled as a pre-wedding antimicrobial skin treatment.",
        "how_it_was_forgotten": "Western medicine's focus on single-molecule drugs dismissed turmeric's multi-pathway action. Colonisation brought pharmaceutical culture that devalued kitchen remedies as 'superstition'.",
        "ingredients": ["Turmeric", "Black Pepper", "Milk", "Honey", "Ghee"],
        "ingredient_quantities": {"Turmeric": "1/2 tsp", "Black Pepper": "pinch", "Milk": "1 cup", "Honey": "1 tsp"},
        "remedy_steps": [
            "For golden milk: heat 1 cup milk, add 1/2 tsp turmeric + pinch black pepper, simmer 2 min",
            "Add honey after removing from heat (never cook honey)",
            "For wounds: mix turmeric with coconut oil into paste, apply to cut, cover lightly",
            "For digestion: 1/4 tsp turmeric in warm water 30 min before meals",
            "For joint pain: turmeric + ginger + sesame oil massage on affected joints",
        ],
        "health_benefits": ["Immunity","Inflammation","Wound Healing","Digestion","Skin","Joint Pain","Liver"],
        "mental_benefits": ["Depression (via BDNF pathways)","Anxiety","Brain Fog"],
        "active_compounds": ["Curcumin","Bisdemethoxycurcumin","Turmerones"],
        "scientific_backing": [
            "Curcumin: Inhibits NF-κB, COX-2, and LOX inflammatory pathways",
            "Antioxidant: ORAC value higher than blueberry",
            "Piperine (from black pepper) increases curcumin absorption 2000%",
            "Clinical trials show comparable efficacy to ibuprofen for knee pain (no gastric damage)",
            "Antibacterial: Effective against MRSA and drug-resistant bacteria",
        ],
        "dosha_type": "All doshas (tridoshic)", "season_best": "All seasons",
        "time_of_day": "Morning or bedtime",
        "contraindications": ["High doses may increase gallstone risk","Avoid therapeutic doses before surgery (blood thinning)"],
        "warnings": ["Do not take more than 1-2 tsp daily as supplement","Cooking turmeric is safe in any quantity"],
        "duration": "Ongoing — daily use as food is ideal",
        "modern_relevance": ["Immunity Boosting","Mental Performance","Skincare","Longevity"],
        "gen_z_hook": "12,000 research papers. One spice. Your kitchen has had it all along. 💛",
        "tiktok_angle": "I replaced ibuprofen with turmeric for 30 days. Here's what happened.",
        "challenge_idea": "7-day Haldi Challenge: add turmeric to one meal daily, track how you feel",
        "daily_habit_tip": "Add 1/4 tsp to your morning chai or scrambled eggs — tastes great, zero effort",
        "difficulty_to_adopt": "easy",
        "state_of_origin": "All India (Meghalaya produces world's finest)",
        "source_name": "TKDL + Charaka Samhita", "source_url": "https://www.tkdl.res.in",
        "pubmed_keywords": ["curcumin anti-inflammatory","turmeric clinical trial","curcuma longa"],
    },
    {
        "title": "Ashwagandha — The Horse of Herbs",
        "title_sanskrit": "Ashwagandha (अश्वगंधा) — Withania somnifera",
        "domain": "Ayurveda", "subdomain": "Rasayana — Adaptogens",
        "summary": "Ashwagandha is Ayurveda's premier adaptogenic rasayana. Its name means 'smell of horse' implying it grants equine strength. Clinical research confirms it significantly reduces cortisol, builds muscle, improves sleep, and enhances cognitive function.",
        "origin_story": "In the Charaka Samhita, ashwagandha is listed as one of the most powerful rasayanas for vata disorders. Ancient vaidyas prescribed it to warriors returning from battle for stress recovery, and to elders for rejuvenation.",
        "how_it_was_forgotten": "British colonial medicine dismantled the gurukul system where vaidyas trained. Ashwagandha was classified as folk medicine and excluded from medical education for 150 years.",
        "ingredients": ["Ashwagandha Root Powder", "Warm Milk", "Honey", "Ghee", "Saffron"],
        "ingredient_quantities": {"Ashwagandha Root Powder": "300-500mg or 1/4 tsp", "Warm Milk": "1 cup", "Honey": "1 tsp", "Ghee": "1/4 tsp"},
        "remedy_steps": [
            "Mix 1/4 tsp ashwagandha root powder into warm (not hot) milk",
            "Add a small amount of ghee — it helps fat-soluble withanolides absorb",
            "Sweeten with honey after mixing",
            "Take 1 hour before bedtime for sleep and recovery benefits",
            "For sustained rasayana effect: take consistently for 3 months minimum",
            "Capsule alternative: 300-600mg standardised to 5% withanolides twice daily with food",
        ],
        "health_benefits": ["Stress","Anxiety","Sleep","Energy","Testosterone","Muscle Strength","Immunity","Thyroid"],
        "mental_benefits": ["Cortisol Reduction","Memory","Focus","Depression","Brain BDNF"],
        "active_compounds": ["Withanolide A","Withanolide B","Withaferin A","Sitoindosides"],
        "scientific_backing": [
            "RCT: 300mg twice daily reduced serum cortisol by 27.9% vs placebo",
            "Meta-analysis: Significantly improved VO2 max and muscle recovery in athletes",
            "Neuroprotective: Promotes dendrite and axon growth in brain cells (in vitro)",
            "Thyroid: Significant increase in T3/T4 in subclinical hypothyroid patients",
            "Immunomodulatory: Increases NK cell activity and immunoglobulin levels",
        ],
        "dosha_type": "Vata, Kapha", "season_best": "Winter",
        "time_of_day": "Bedtime",
        "contraindications": ["Avoid in pregnancy (uterine stimulant)","Caution with thyroid medication","Avoid with immunosuppressants (autoimmune disease)"],
        "warnings": ["Do not self-medicate thyroid conditions without a doctor","May cause drowsiness if taken with sedatives"],
        "duration": "3-6 months for full rasayana effect",
        "modern_relevance": ["Mental Health","Fitness & Yoga","Sleep Wellness","Immunity Boosting","Longevity"],
        "gen_z_hook": "Andrew Huberman's #1 supplement? Ashwagandha. Your dadi's? Also Ashwagandha. Since forever. 🐎",
        "tiktok_angle": "I took ashwagandha for 90 days. My cortisol test results will shock you.",
        "challenge_idea": "90-day Ashwagandha Rasayana Challenge — track stress levels weekly",
        "daily_habit_tip": "Warm moon milk before bed: ashwagandha + milk + saffron = best sleep of your life",
        "difficulty_to_adopt": "easy",
        "grandmother_quote": "Beta, yeh doodh peele. Kal fauji ki tarah uthega.",
        "state_of_origin": "Madhya Pradesh, Rajasthan (Manasa region produces finest quality)",
        "source_name": "Charaka Samhita + TKDL", "source_url": "https://www.tkdl.res.in",
        "pubmed_keywords": ["ashwagandha cortisol RCT","withania somnifera adaptogen","withanolide stress"],
    },
    {
        "title": "Tulsi — Queen of Herbs",
        "title_sanskrit": "Tulasi (तुलसी) — Ocimum tenuiflorum",
        "domain": "Ayurveda", "subdomain": "Sacred Medicinal Plants",
        "summary": "Tulsi is both the most sacred plant in Hinduism and one of the most pharmacologically active. It is grown in nearly every Indian home. Modern science confirms it is a potent adaptogen, antimicrobial, immunomodulator, and respiratory healer.",
        "origin_story": "In the Skanda Purana, Tulsi is the earthly form of Goddess Vrinda — Vishnu's devoted follower transformed into a plant so that all who touched her would receive her blessings. The ritual of watering Tulsi at dawn was the world's first 'mindfulness morning routine'.",
        "ingredients": ["Tulsi Leaves", "Ginger", "Black Pepper", "Honey", "Lemon"],
        "ingredient_quantities": {"Tulsi Leaves": "8-10 fresh", "Ginger": "1 inch", "Black Pepper": "2 corns", "Honey": "1 tsp"},
        "remedy_steps": [
            "Boil 8-10 fresh tulsi leaves with 1 inch ginger in 2 cups water for 5 minutes",
            "Add 2-3 black peppercorns and simmer 2 more minutes",
            "Strain into cup, add lemon juice and honey after cooling to warm",
            "Drink twice daily for respiratory issues, once daily for maintenance",
            "For skin: crush fresh leaves into paste, apply to acne or insect bites for 15 min",
            "For stress: simply rubbing tulsi leaves and inhaling the aroma lowers cortisol",
            "For ear drops: warm 2-3 drops tulsi leaf juice, instill in ear for ear pain",
        ],
        "health_benefits": ["Immunity","Respiratory","Stress","Fever","Cold","Cough","Skin","Dental","Ear"],
        "mental_benefits": ["Stress","Anxiety","Cortisol Reduction","Clarity"],
        "active_compounds": ["Eugenol","Rosmarinic Acid","Ursolic Acid","Ocimumosides A & B","Beta-Caryophyllene"],
        "scientific_backing": [
            "Adaptogen: Regulates HPA-axis stress response — comparable to anti-anxiety medication in animal models",
            "Antibacterial: Eugenol active against E. coli, S. aureus, and Pseudomonas",
            "Antiviral: Active against Dengue, H1N1, and Herpes simplex viruses",
            "Immunomodulatory: Increases CD4+ T-lymphocytes and NK cell count",
            "Anti-diabetic: Reduces fasting blood glucose in type 2 diabetics (multiple RCTs)",
        ],
        "dosha_type": "Vata, Kapha", "season_best": "Monsoon, Winter",
        "time_of_day": "Morning (empty stomach), evening",
        "contraindications": ["Avoid concentrated extracts in pregnancy","Avoid with anticoagulants (blood thinning)"],
        "duration": "Daily — preventive use ongoing",
        "modern_relevance": ["Immunity Boosting","Mental Health","Gut Health","Respiratory"],
        "gen_z_hook": "Adaptogens are a $14B industry. Tulsi did it first, for free, in your courtyard. 🌿",
        "tiktok_angle": "I added tulsi to my morning routine for 21 days. Here's what changed.",
        "challenge_idea": "21-day Tulsi Immunity Challenge — one cup tulsi kadha every morning",
        "daily_habit_tip": "Put a Tulsi plant at your window. Water it at dawn (actually meditative) and pluck 5 leaves for tea.",
        "difficulty_to_adopt": "easy",
        "grandmother_quote": "Tulsi ke bina ghar adhura hai. Aur tulsi ke bina shareer bhi.",
        "related_festival": "Tulsi Vivah (Kartik month)",
        "state_of_origin": "All India (originated in northeast India)",
        "source_name": "Charaka Samhita + TKDL", "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Neem — Village Pharmacy in a Tree",
        "title_sanskrit": "Nimba (निम्ब) — Azadirachta indica",
        "domain": "Ayurveda", "subdomain": "Medicinal Trees",
        "summary": "Neem is the world's most researched botanical with 4000+ published studies. Every part — leaves, bark, seeds, oil, roots, flowers — has documented medicinal uses. It is the original 'full-stack' pharmacy, freely available to every Indian village.",
        "origin_story": "In Skanda Purana, neem is called 'Sarva Roga Nivarini' — the curer of all diseases. Temples in Tamil Nadu have neem trees as sacred guardians. The tradition of cleaning teeth with neem twigs dates to Sushruta Samhita — 600 BCE.",
        "ingredients": ["Neem Leaves", "Neem Bark", "Neem Oil", "Neem Powder", "Coconut Oil"],
        "ingredient_quantities": {"Neem Oil": "few drops", "Coconut Oil": "1 tbsp"},
        "remedy_steps": [
            "For skin infections: grind 10 fresh neem leaves into paste, apply to infected area 20 min",
            "For dental health: chew neem twig daily (break end into brush shape) — original toothbrush",
            "For dandruff/scalp: mix neem oil + coconut oil 1:4, massage scalp, leave 1 hour",
            "For blood purification: boil 5-7 leaves in water, drink on empty stomach (max 3 weeks at a time)",
            "For mosquito repellent: burn dried neem leaves (natural, non-toxic)",
            "For wounds: diluted neem leaf extract as antiseptic wash",
            "For acne: neem face pack — neem powder + rose water paste, apply 15 min",
            "WARNING: Never consume neem OIL internally — toxic. Only leaves/bark internally.",
        ],
        "health_benefits": ["Skin","Dental","Hair","Blood Purification","Wounds","Acne","Immunity","Malaria Prevention"],
        "active_compounds": ["Nimbin","Nimbidin","Azadirachtin","Gedunin","Nimbolide","Quercetin"],
        "scientific_backing": [
            "Nimbolide: Significant anticancer activity in breast, prostate, pancreatic cancer (in vitro/vivo)",
            "Antibacterial: Effective against drug-resistant Staphylococcus and Streptococcus",
            "Azadirachtin: EPA-approved natural pesticide — disrupts insect hormone system",
            "Antifungal: 100% inhibition of Candida albicans at 1000μg/ml",
            "Anti-malarial: Gedunin effective against Plasmodium falciparum",
        ],
        "dosha_type": "Pitta, Kapha", "season_best": "Summer, Monsoon",
        "contraindications": ["NEVER consume neem oil internally","Avoid in pregnancy (abortifacient)","Do not give to children under 3"],
        "warnings": ["Neem oil is only for external use","Internal neem leaf use: max 3 weeks at a time"],
        "modern_relevance": ["Skincare","Haircare","Sustainability","Immunity Boosting"],
        "gen_z_hook": "One tree. 4000 studies. Grows for free. No patent possible. That's why Big Pharma hates it. 🌳",
        "grandmother_quote": "Neem kadwa hai to kya? Zindagi bhi kadwi hai — dono tujhe bachate hain.",
        "state_of_origin": "All India (native to Indian subcontinent)",
        "source_name": "TKDL + Sushruta Samhita", "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Amla — Immortal Fruit of Ayurveda",
        "title_sanskrit": "Amalaki (आमलकी) — Phyllanthus emblica",
        "domain": "Ayurveda", "subdomain": "Rasayana Fruits",
        "summary": "Amla (Indian Gooseberry) contains the highest natural Vitamin C of any food — 600-700mg per 100g, nearly 20 times more than oranges. Unlike synthetic Vitamin C, amla's tannins protect the ascorbic acid even during cooking. Considered the most important rasayana fruit in all of Ayurveda.",
        "origin_story": "The Dhanvantari Nighantus describes Amla as 'Divya Phala' — divine fruit. The legend says Brahma created Amla from his tears of compassion that fell to earth. Chyawanprash, the 2600-year-old health supplement, is built on amla as its primary ingredient.",
        "ingredients": ["Amla (Fresh or Dried)", "Honey", "Ginger", "Black Pepper", "Sesame Seeds"],
        "remedy_steps": [
            "Fresh amla juice: blend 2-3 amla with 1/4 cup water, strain, drink with honey",
            "Amla powder: 1 tsp in warm water every morning (preserves all nutrients)",
            "Amla murabba: candied amla in jaggery — traditional Rajasthani preservation method",
            "For hair: boil dried amla in coconut oil until charred, cool, massage scalp — reverses greying",
            "For eye health: amla juice + honey 1:1 ratio, 1/4 tsp taken daily",
            "For diabetes: amla juice + bitter gourd juice (50:50), 30ml morning empty stomach",
        ],
        "health_benefits": ["Immunity","Hair","Eye Health","Digestion","Diabetes","Liver","Skin","Cholesterol"],
        "active_compounds": ["Vitamin C (600-700mg/100g)","Tannins (Emblicanin A & B)","Gallic Acid","Ellagic Acid","Quercetin"],
        "scientific_backing": [
            "Tannins protect Vitamin C from heat degradation — unlike synthetic ascorbic acid",
            "Lowers LDL cholesterol comparable to simvastatin in 3-month RCT",
            "Hepatoprotective: Reduces liver enzyme AST/ALT in alcoholic liver disease",
            "Anti-diabetic: Reduces fasting blood glucose and HbA1c",
            "Anti-aging: Increases telomere length and reduces oxidative DNA damage",
        ],
        "dosha_type": "All doshas (tridoshic)", "season_best": "Winter (fresh season)",
        "modern_relevance": ["Immunity Boosting","Skincare","Haircare","Longevity","Mental Performance"],
        "gen_z_hook": "Vitamin C supplements didn't exist in 1000 BCE. Amla did. 20x more than an orange. 🍏",
        "grandmother_quote": "Roz ek amla khao. Doctor ki zaroorat kabhi nahi padegi.",
        "state_of_origin": "All India (Pratapgarh, UP produces most)",
        "source_name": "Charaka Samhita + TKDL", "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Giloy (Guduchi) — The Root of Immortality",
        "title_sanskrit": "Guduchi (गुडूची) — Tinospora cordifolia",
        "domain": "Ayurveda", "subdomain": "Immunomodulatory Herbs",
        "summary": "Giloy is called 'Amrita' — the nectar of immortality in Sanskrit — because it is one of only three plants mentioned in the Charaka Samhita as 'Rasayanas for all disorders'. It is Ayurveda's most powerful immunomodulator, confirmed by multiple clinical trials.",
        "origin_story": "In the Ramayana, when Rama's army of monkeys was killed in battle, the celestial being Indra sprinkled nectar over the battlefield. Where this nectar fell on the dead, the Giloy creeper sprouted — giving it the name 'Amrita' — immortality.",
        "ingredients": ["Giloy Stem","Tulsi","Black Pepper","Honey"],
        "remedy_steps": [
            "Giloy kadha: boil 2-inch fresh giloy stem in 2 cups water, reduce to 1 cup, strain",
            "Add tulsi and black pepper for enhanced respiratory benefit",
            "Giloy juice: blend fresh stem + water, strain, drink 20ml on empty stomach",
            "For dengue/chikungunya: giloy juice 20ml twice daily increases platelet count",
            "Giloy churna: 1/4 tsp powder with honey twice daily for immunity maintenance",
            "For arthritis: giloy + ginger decoction, reduces joint inflammation significantly",
        ],
        "health_benefits": ["Immunity","Fever","Dengue","Arthritis","Diabetes","Liver","Digestion","Allergies"],
        "active_compounds": ["Berberine","Tinocordiside","Giloin","Giloinin","Syringin","Palmatine"],
        "scientific_backing": [
            "Immunomodulatory: Increases macrophage activity, T-cell and B-cell proliferation",
            "Anti-diabetic: Inhibits alpha-glucosidase enzyme (same mechanism as acarbose)",
            "Anti-arthritic: Reduces joint swelling comparable to diclofenac in rat models",
            "Hepatoprotective: Significant reduction in liver enzymes in hepatotoxic studies",
            "COVID-19: AYUSH Protocol recommended for immune support during pandemic",
        ],
        "dosha_type": "All doshas (tridoshic)", "season_best": "Monsoon",
        "contraindications": ["Avoid with immunosuppressants","Caution in autoimmune disease","May lower blood sugar — caution with diabetes medication"],
        "modern_relevance": ["Immunity Boosting","Gut Health","Longevity","Ayush-Approved"],
        "gen_z_hook": "This herb literally means 'immortality nectar' in Sanskrit. It survived 5000 years of Indian medicine for a reason. ⚡",
        "grandmother_quote": "Giloy ka kadha pee le — koi bimaari paas nahi aayegi.",
        "state_of_origin": "All India (abundant in Himalayan foothills)",
        "source_name": "Charaka Samhita + AYUSH Protocol", "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Brahmi — Brain Tonic of the Gods",
        "title_sanskrit": "Brahmi (ब्राह्मी) — Bacopa monnieri",
        "domain": "Ayurveda", "subdomain": "Nootropic Herbs (Brain Herbs)",
        "summary": "Brahmi is Ayurveda's foremost brain herb, used for thousands of years to enhance memory, learning, and concentration. Children in gurukuls were given Brahmi before lessons. Modern neuroscience confirms it grows dendrites, reduces anxiety, and protects against Alzheimer's through multiple mechanisms.",
        "origin_story": "Brahmi is named after Brahma, the god of knowledge and creation. Ancient texts say sages consumed Brahmi to memorise the Vedas — texts running to hundreds of thousands of verses committed entirely to memory.",
        "ingredients": ["Brahmi Powder", "Warm Milk", "Honey", "Ghee", "Almonds"],
        "remedy_steps": [
            "Brahmi milk: 1/4 tsp brahmi powder in warm milk with honey, take before bed",
            "Brahmi ghee (Brahmi Ghrita): traditional classical preparation — brahmi cooked in ghee",
            "Brahmi hair oil: boil brahmi leaves in coconut oil, cool, massage scalp weekly",
            "For children's memory: 1/4 tsp brahmi + 1/4 tsp ashwagandha in warm milk daily",
            "Brahmi tea: boil 5-6 fresh leaves, drink with honey for clarity before study/work",
        ],
        "health_benefits": ["Memory","Focus","Anxiety","ADHD","Epilepsy","Hair","Alzheimer's Prevention"],
        "mental_benefits": ["Memory Consolidation","Anxiety","Focus","Learning","Stress","Depression"],
        "active_compounds": ["Bacosides A & B","Bacopasaponins","Alkaloids (brahmine, herpestine)","Flavonoids"],
        "scientific_backing": [
            "Meta-analysis (9 RCTs): Significant improvement in free recall memory vs placebo",
            "Reduces cortisol equivalent to 300mg ashwagandha in direct comparison",
            "Inhibits acetylcholinesterase — same mechanism as Alzheimer's drugs (donepezil)",
            "Promotes dendrite branching and synaptogenesis in hippocampus",
            "ADHD: Significant reduction in ADHD scores in children (double-blind RCT)",
        ],
        "dosha_type": "Pitta, Vata", "season_best": "All seasons",
        "time_of_day": "Morning for focus, bedtime for memory consolidation",
        "contraindications": ["May slow processing speed initially — give 4-6 weeks for full effect","Caution with thyroid medication"],
        "modern_relevance": ["Mental Performance","Sleep Wellness","Children's Health","Longevity"],
        "gen_z_hook": "Ancient monks memorised 100,000-verse texts using this herb. You need to remember a 10-page essay. 🧠",
        "grandmother_quote": "Brahmi tel se maalish kar sakte the Vedanta. Aaj tum padhai yaddasht bhool jaate ho.",
        "state_of_origin": "All India (wetlands and water bodies)",
        "source_name": "Charaka Samhita + TKDL", "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Triphala — Three-Fruit Master Formula",
        "title_sanskrit": "Triphala (त्रिफला) — Amalaki + Haritaki + Bibhitaki",
        "domain": "Ayurveda", "subdomain": "Classical Formulations",
        "summary": "Triphala is Ayurveda's most celebrated formula — a precise blend of three fruits that balance all three doshas, support complete digestion, act as a prebiotic, and have more antioxidant activity than most single superfoods. It is the most referenced formulation in the Charaka Samhita.",
        "origin_story": "The ancient text Ashtanga Hridayam says: 'One who takes Triphala regularly for a year will live 100 years free of disease and old age.' The three fruits represent the sun (Haritaki), moon (Amalaki), and fire (Bibhitaki) — the three cosmic energies balancing the body.",
        "ingredients": ["Amla (Amalaki)", "Haritaki (Chebulic Myrobalan)", "Bibhitaki (Baheda)"],
        "ingredient_quantities": {"Amla": "1 part", "Haritaki": "1 part", "Bibhitaki": "1 part"},
        "remedy_steps": [
            "Standard dose: 1/2 to 1 tsp Triphala powder in warm water before bedtime",
            "For eye wash: brew 1 tsp in 2 cups water, cool completely, strain through fine cloth, use as eyewash twice daily",
            "For oral health: mix with sesame oil for oil pulling, or gargle with diluted solution",
            "For constipation: 1 tsp in hot water before bed (laxative action)",
            "For weight management: 1/2 tsp in warm water 30 min before meals",
            "Triphala ghrita: classical preparation with ghee for eye and brain health",
            "Reduce dose if stools become too loose — it is working",
        ],
        "health_benefits": ["Digestion","Detox","Eye Health","Dental","Weight","Immunity","Skin","Cholesterol"],
        "active_compounds": ["Chebulinic Acid","Chebulagic Acid","Emblicanin A","Ellagic Acid","Gallic Acid","Tannins"],
        "scientific_backing": [
            "Prebiotic: Increases Bifidobacterium and Lactobacillus populations in gut by 30%",
            "Anticancer: Triphala extract induces apoptosis in cancer cells while protecting normal cells",
            "Antioxidant: Higher ORAC value than Vitamin C, E, or blueberry extract",
            "Lowers LDL and total cholesterol in type 2 diabetics (3-month RCT)",
            "Anti-obesity: Reduces BMI and waist circumference in overweight adults (RCT)",
        ],
        "dosha_type": "All doshas (tridoshic)", "season_best": "All seasons",
        "time_of_day": "Bedtime (laxative action), or morning for eye wash",
        "modern_relevance": ["Gut Health","Detox","Skincare","Immunity Boosting","Longevity"],
        "gen_z_hook": "Three fruits. One formula. Balances all three body types. 2500 years before personalised medicine. 🫙",
        "grandmother_quote": "Triphala le le — aankhein, pet, aur dil — teeno theek ho jayenge.",
        "state_of_origin": "Classical formulation from multiple regions",
        "source_name": "Charaka Samhita + Ashtanga Hridayam", "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Shatavari — The Herb of 100 Roots",
        "title_sanskrit": "Shatavari (शतावरी) — Asparagus racemosus",
        "domain": "Ayurveda", "subdomain": "Women's Health / Rasayana",
        "summary": "Shatavari means 'she who possesses a hundred husbands' — reflecting its role as the primary Ayurvedic herb for women's reproductive health across all life stages. It is a powerful phytoestrogen, galactagogue (increases breast milk), and adaptogen that supports hormonal balance.",
        "ingredients": ["Shatavari Powder", "Warm Milk", "Honey", "Ghee"],
        "remedy_steps": [
            "Shatavari milk: 1/2 tsp powder in warm milk with honey, take daily",
            "For menopausal symptoms: 500mg capsule twice daily for 3 months",
            "For milk production: 1/2 tsp shatavari + 1/4 tsp vidarikanda in warm milk twice daily",
            "For menstrual irregularity: shatavari + ashoka + lodhra combination (consult vaidya)",
            "For fertility: shatavari + ashwagandha in equal parts, 1/4 tsp each in milk",
        ],
        "health_benefits": ["Menstrual Health","Fertility","Menopause","Breast Milk","Hormonal Balance","Immunity","Digestion"],
        "active_compounds": ["Steroidal Saponins (Shatavarins I-IX)","Isoflavones","Alkaloids","Mucilage"],
        "scientific_backing": [
            "Galactagogue: Significantly increases prolactin and milk volume in lactating mothers",
            "Phytoestrogenic: Shatavarin I binds estrogen receptors — manages menopausal symptoms",
            "Adaptogen: Comparable to ashwagandha in HPA-axis modulation",
            "Anti-ulcerogenic: Comparable to ranitidine in gastric ulcer protection",
        ],
        "dosha_type": "Pitta, Vata", "season_best": "All seasons",
        "contraindications": ["Caution with estrogen-sensitive conditions (breast cancer history)","May interact with diuretics","Avoid with kidney disease"],
        "modern_relevance": ["Women's Wellness","Mental Health","Immunity Boosting","Gut Health"],
        "gen_z_hook": "PCOS, menopause, postpartum — Ayurveda had one herb for all of it. 5000 years before gynecology. 🌺",
        "grandmother_quote": "Shatavari khao, har umra mein aurat takat se rahegi.",
        "state_of_origin": "All India (Himachal Pradesh, Bihar)",
        "source_name": "Charaka Samhita + TKDL", "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Shilajit — Exudate of the Mountains",
        "title_sanskrit": "Shilajit (शिलाजीत) — Mineral Pitch",
        "domain": "Ayurveda", "subdomain": "Mineral Medicines (Khanjara)",
        "summary": "Shilajit is a sticky resinous substance exuded from Himalayan rocks formed over millennia from compressed plant matter. It contains 85+ minerals in ionic form, fulvic acid, and humic acid. Ayurveda calls it 'Yoga Vahi' — the carrier that amplifies the benefits of every herb taken with it.",
        "ingredients": ["Shilajit (resin or powder)", "Warm Water or Milk", "Honey"],
        "remedy_steps": [
            "Dissolve pea-sized amount of pure shilajit resin in warm water or milk",
            "Add honey to taste, drink in morning on empty stomach",
            "Start with small amount and increase gradually over 2 weeks",
            "For maximum absorption: take with fat (milk with ghee)",
            "Powder form: 300-500mg capsule with warm milk twice daily",
            "Cycle: use for 6-8 weeks, then 2 weeks off for best results",
            "WARNING: Only use lab-tested, pure shilajit — heavy metal contamination is a real risk in adulterated products",
        ],
        "health_benefits": ["Energy","Testosterone","Fertility","Altitude Sickness","Immunity","Cognitive","Bone Health","Anti-aging"],
        "active_compounds": ["Fulvic Acid","Humic Acid","DBPs (Dibenzo-alpha-pyrones)","85+ Ionic Minerals","Selenium","Zinc"],
        "scientific_backing": [
            "Increases total testosterone by 23.5% in healthy men (3-month RCT, Journal of Ethnopharmacology)",
            "Increases ATP production in mitochondria — explains energy enhancement",
            "Fulvic acid: Prevents aggregation of tau proteins (Alzheimer's mechanism)",
            "Reduces altitude sickness symptoms significantly (used by Himalayan trekkers)",
            "Anti-osteoporotic: Increases bone mineral density in ovariectomised rat models",
        ],
        "dosha_type": "Vata, Kapha", "season_best": "Winter",
        "contraindications": ["Caution with gout (high uric acid levels)","Never use unprocessed/raw shilajit","Avoid counterfeit products (heavy metal risk)"],
        "modern_relevance": ["Fitness & Yoga","Longevity","Mental Performance","Energy"],
        "gen_z_hook": "Himalayan mountains literally sweat out medicine. And it's been in Ayurveda for 3000 years. ⛰️",
        "state_of_origin": "Himalayan region (Himachal Pradesh, Uttarakhand, Ladakh)",
        "source_name": "Charaka Samhita + TKDL", "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Moringa — The Miracle Tree",
        "title_sanskrit": "Shigru (शिग्रु) — Moringa oleifera",
        "domain": "Ayurveda", "subdomain": "Nutritive Herbs",
        "summary": "Moringa oleifera is called 'Shigru' in Ayurveda and is considered a powerhouse of nutrition. It contains 7x Vitamin C of oranges, 4x Vitamin A of carrots, 4x calcium of milk, 3x potassium of bananas, and 2x protein of yogurt — making it one of the most nutrient-dense plants on Earth.",
        "ingredients": ["Moringa Leaves (fresh or dried)", "Moringa Powder", "Moringa Seeds"],
        "remedy_steps": [
            "Add 1 tsp moringa powder to smoothie, dal, or rice daily",
            "Fresh moringa leaves: sauté with garlic and cumin as saag",
            "Moringa tea: steep 1 tsp dried leaves in hot water 5 min, strain, drink",
            "For bone health: moringa powder + sesame seeds + jaggery laddoo",
            "For breast milk: moringa leaves cooked in dal daily for nursing mothers",
            "Moringa seed oil: apply directly to skin as anti-aging oil",
        ],
        "health_benefits": ["Nutrition","Immunity","Diabetes","Cholesterol","Inflammation","Breast Milk","Skin","Bone Health"],
        "active_compounds": ["Isothiocyanates","Quercetin","Chlorogenic Acid","Kaempferol","Glucosinolates"],
        "scientific_backing": [
            "Reduces fasting blood glucose by 28% in 3-month RCT",
            "Reduces LDL cholesterol by 14.3% in postmenopausal women",
            "Isothiocyanates: anti-cancer activity in colon, pancreatic, and liver cancer cells",
            "Antioxidant: Inhibits lipid peroxidation equivalent to BHT food preservative",
        ],
        "dosha_type": "Vata, Kapha", "season_best": "All seasons",
        "modern_relevance": ["Immunity Boosting","Women's Wellness","Sustainability","Children's Health"],
        "gen_z_hook": "7x Vitamin C. 4x Vitamin A. 4x Calcium. Grows in 3 months from seed. UN calls it the tree that fights malnutrition. 🌿",
        "state_of_origin": "All India (native to sub-Himalayan region)",
        "source_name": "Sushruta Samhita + TKDL", "source_url": "https://www.tkdl.res.in",
    },

    # ═══════════════════════════════════════════════════════════════
    #  HOME REMEDIES  (25 entries)
    # ═══════════════════════════════════════════════════════════════
    {
        "title": "Kadha — Immunity Decoction",
        "title_sanskrit": "Kasaya (काषाय)",
        "domain": "Home Remedies", "subdomain": "Respiratory & Immunity",
        "summary": "Kadha is a traditional herbal decoction — a water extract of multiple medicinal spices boiled together. It became world-famous during COVID-19 when AYUSH Ministry officially endorsed it. There are hundreds of regional variants — every grandmother has her own formula.",
        "origin_story": "Kadha is the primary form of Ayurvedic medicine described in the Charaka Samhita. Of the 5 major preparations (Kasaya, Churna, Avaleha, Ghrita, Taila), Kasaya (decoction) is described as most effective for respiratory conditions.",
        "ingredients": ["Tulsi", "Ginger", "Black Pepper", "Cinnamon", "Clove", "Turmeric", "Honey"],
        "ingredient_quantities": {"Tulsi": "5 leaves", "Ginger": "1/2 inch", "Black Pepper": "3 corns", "Cinnamon": "1 small stick", "Clove": "2", "Turmeric": "1/4 tsp", "Water": "2 cups"},
        "remedy_steps": [
            "Bring 2 cups water to boil",
            "Add all ingredients except honey",
            "Simmer covered for 10 minutes until reduced to 1 cup",
            "Strain through fine mesh",
            "Allow to cool to warm (under 40°C), then add 1 tsp honey",
            "Drink twice daily at first sign of cold or flu",
            "Children's dose: half quantity, reduce spice",
            "Add lemon juice for Vitamin C boost",
        ],
        "health_benefits": ["Immunity","Cold","Cough","Sore Throat","Respiratory","Fever","Digestion"],
        "active_compounds": ["Eugenol","Gingerol","Cinnamaldehyde","Curcumin","Piperine","Rosmarinic Acid"],
        "scientific_backing": [
            "All 6 primary ingredients independently show antiviral and antimicrobial activity",
            "Piperine enhances bioavailability of all other active compounds",
            "WHO acknowledged traditional medicine role in COVID-19 symptom management",
            "AYUSH Ministry officially endorsed as preventive during COVID-19 pandemic",
        ],
        "dosha_type": "Kapha (especially)", "season_best": "Winter, Monsoon",
        "time_of_day": "Morning and evening",
        "modern_relevance": ["Immunity Boosting","Respiratory","Gut Health"],
        "gen_z_hook": "AYUSH made it official in 2020. Dadi was making it in 1970. Same recipe. ☕",
        "challenge_idea": "Morning Kadha Challenge: replace morning chai with kadha for 7 days",
        "state_of_origin": "All India (varies by region)",
        "source_name": "AYUSH Ministry + Charaka Samhita", "source_url": "https://main.ayush.gov.in",
    },
    {
        "title": "Chyawanprash — World's Oldest Health Supplement",
        "title_sanskrit": "Chyavanprasha (च्यवनप्राश)",
        "domain": "Ayurveda", "subdomain": "Rasayana Formulations",
        "summary": "Chyawanprash is the oldest known health supplement in the world, first described around 900 BCE in the Charaka Samhita. It is a jam-like preparation built on Amla as the primary base with 35-50 additional herbs, ghee, honey, and sesame oil. It is named after the sage Chyawan who reportedly regained his youth using it.",
        "origin_story": "The sage Chyawan, in extreme old age, was given Chyawanprash by the divine physician twins (Ashwini Kumars) who were helping him regain his youth before his marriage to Princess Sukanya. The original formula in Charaka Samhita remains essentially unchanged for 2500 years.",
        "ingredients": ["Amla","Ashwagandha","Shatavari","Ghee","Honey","Sesame Oil","Long Pepper","Cardamom","Cinnamon","Clove"],
        "remedy_steps": [
            "Adults: 1-2 tsp with warm milk every morning before breakfast",
            "Children (5+): 1/2 tsp with warm milk daily",
            "Elderly: 1 tsp twice daily, morning and evening",
            "In summer: take with cold milk (cooling); in winter: with warm milk (heating)",
            "Do not cook honey — add separately to warm milk after mixing chyawanprash",
            "Minimum 3 months for full rasayana effect",
        ],
        "health_benefits": ["Immunity","Memory","Energy","Respiratory","Skin","Digestion","Metabolism","Longevity"],
        "active_compounds": ["Emblicanins A&B (Amla)","Withanolides (Ashwagandha)","Steroidal Saponins (Shatavari)","Piperine"],
        "scientific_backing": [
            "Amla: Highest natural Vitamin C — 600mg per 100g (20x orange)",
            "RCT: Significant improvement in respiratory function in asthmatic children",
            "Immunomodulatory: Increases IgG and IgM antibody titres significantly",
            "Antioxidant: Reduces oxidative stress markers in healthy adults over 12 weeks",
        ],
        "dosha_type": "All doshas (tridoshic)", "season_best": "Winter, Monsoon",
        "time_of_day": "Morning",
        "modern_relevance": ["Immunity Boosting","Children's Health","Longevity","Skincare"],
        "gen_z_hook": "Oldest health supplement on Earth. Indian. 2500 years old. AG1 Athletic Greens takes notes. 🍃",
        "grandmother_quote": "Subah ek chamach chyawanprash le le — sardi-bukhar wala doctor kabhi nahi milega.",
        "state_of_origin": "All India (classical formulation)",
        "source_name": "Charaka Samhita + TKDL", "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Oil Pulling (Gandusha) — Ancient Oral Detox",
        "title_sanskrit": "Gandusha/Kavala (गण्डूष)",
        "domain": "Ayurveda", "subdomain": "Dinacharya (Daily Practices)",
        "summary": "Oil pulling — swishing sesame or coconut oil in the mouth for 10-20 minutes — is described in the Charaka Samhita as Gandusha. It is one of the most extensively scientifically validated Ayurvedic practices, with peer-reviewed evidence for dental health benefits comparable to chlorhexidine mouthwash.",
        "ingredients": ["Sesame Oil (traditional)", "Coconut Oil (alternative)"],
        "ingredient_quantities": {"Sesame/Coconut Oil": "1 tablespoon"},
        "remedy_steps": [
            "On waking (before eating, drinking, or brushing), take 1 tbsp sesame or coconut oil",
            "Swish vigorously in mouth for 15-20 minutes — pulling between teeth",
            "The oil will turn white and thin as it emulsifies saliva and pulls bacteria",
            "Spit into trash bin — NOT the sink (can clog pipes)",
            "Rinse mouth with warm salt water",
            "Brush teeth as normal afterward",
            "Do this daily for 30 days and notice the difference in oral freshness, gum health, teeth whitening",
        ],
        "health_benefits": ["Dental","Gum Health","Tooth Whitening","Bad Breath","Headache","Detox","Skin"],
        "active_compounds": ["Sesamin (sesame oil)","Lauric Acid (coconut oil)","Vitamin E"],
        "scientific_backing": [
            "Comparable to 0.2% chlorhexidine mouthwash in reducing Streptococcus mutans count",
            "Saponification: Oil emulsifies bacterial cell membranes — physical removal mechanism",
            "Reduces plaque index and gingival scores comparable to chlorhexidine (RCT)",
            "Lauric acid (coconut): Potent antimicrobial against oral pathogens",
        ],
        "dosha_type": "Vata (especially)", "season_best": "All seasons",
        "time_of_day": "Morning, before eating",
        "duration": "20 minutes daily",
        "modern_relevance": ["Dental Health","Detox","Skincare"],
        "gen_z_hook": "Charcoal toothpaste: ₹500. Chlorhexidine mouthwash: ₹300. Sesame oil pull: ₹20. Same results. 🫧",
        "challenge_idea": "30-day Oil Pull Challenge — photograph teeth before/after",
        "state_of_origin": "All India (South India especially — sesame belt)",
        "source_name": "Charaka Samhita + Ashtanga Hridayam", "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Nasya — Nasal Oiling",
        "title_sanskrit": "Nasya (नस्य)",
        "domain": "Ayurveda", "subdomain": "Dinacharya (Daily Practices)",
        "summary": "Nasya is the practice of administering medicated oil or ghee into the nostrils. The nose is considered the 'gateway to the brain' in Ayurveda. Modern understanding of the nose-brain connection through the olfactory nerve and nasal mucosa validates many of its claimed benefits.",
        "ingredients": ["Sesame Oil", "Ghee (cow ghee)", "Anu Taila (classical formulation)"],
        "remedy_steps": [
            "Warm 2-3 drops of sesame oil or ghee",
            "Lie back with head tilted slightly backward",
            "Instill 2-3 drops in each nostril",
            "Sniff gently to draw oil upward",
            "Stay lying for 1-2 minutes",
            "Best done in morning after brushing and before eating",
            "Do NOT do during fever, after oil massage, or immediately after food",
        ],
        "health_benefits": ["Headache","Migraine","Nasal Congestion","Sinus","Dry Nasal Passages","Memory","Insomnia"],
        "scientific_backing": [
            "Olfactory nerve is a direct pathway to limbic system — nasal administration bypasses blood-brain barrier",
            "Reduces nasal dryness and is protective against airborne pathogens during cold season",
            "Sesame oil: Forms protective layer in nasal mucosa, reducing pathogen adhesion",
        ],
        "dosha_type": "Vata (especially)", "season_best": "Winter, Autumn",
        "time_of_day": "Morning",
        "modern_relevance": ["Mental Health","Sleep Wellness","Immunity Boosting"],
        "gen_z_hook": "Nasal drug delivery bypasses the blood-brain barrier. Ayurveda used this route 3000 years ago. 👃",
        "state_of_origin": "All India (classical Ayurvedic practice)",
        "source_name": "Ashtanga Hridayam + Charaka Samhita", "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Haldi Milk for Wounds — Kitchen First Aid",
        "title_sanskrit": "Haridra Kshira",
        "domain": "Home Remedies", "subdomain": "Wound Healing",
        "summary": "Applying turmeric paste to wounds is one of the oldest first-aid practices in India. Modern research confirms turmeric promotes collagen synthesis, has anti-inflammatory and antibacterial effects, and accelerates wound healing — properties now being exploited by the pharmaceutical industry in wound dressings.",
        "ingredients": ["Turmeric Powder", "Coconut Oil", "Honey", "Ghee"],
        "remedy_steps": [
            "For minor cuts: mix 1 tsp turmeric in 1 tsp coconut oil to form thick paste",
            "Apply generously to wound, cover with clean bandage",
            "For burns (minor): apply turmeric + aloe vera gel immediately",
            "For infections: turmeric + neem paste combination",
            "Change dressing twice daily, rinse gently each time",
            "For internal wounds (ulcers): turmeric + honey + warm water drink",
        ],
        "health_benefits": ["Wounds","Cuts","Burns","Skin Infections","Ulcers","Bruises"],
        "scientific_backing": [
            "Curcumin accelerates wound healing by increasing TGF-β and VEGF (growth factors)",
            "Reduces wound inflammation significantly vs. petroleum jelly control",
            "Antibacterial: Effective against wound pathogens including MRSA",
            "Collagen synthesis: Increases collagen type I production in fibroblasts",
        ],
        "dosha_type": "Pitta (anti-inflammatory)", "season_best": "All seasons",
        "modern_relevance": ["Skincare","Sustainability","Zero-cost"],
        "gen_z_hook": "Johnson & Johnson now makes turmeric wound dressings. Your kitchen was the original. 🩹",
        "state_of_origin": "All India",
        "source_name": "TKDL + Sushruta Samhita", "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Ginger Honey for Sore Throat and Nausea",
        "title_sanskrit": "Ardraka (आर्द्रक) + Madhu (मधु)",
        "domain": "Home Remedies", "subdomain": "Digestive & Respiratory",
        "summary": "Fresh ginger with raw honey is one of the most scientifically validated simple home remedies. Ginger contains gingerols and shogaols — potent anti-nausea and anti-inflammatory compounds. Raw honey adds antimicrobial H2O2 and propolis. Together, they form a powerful combination for sore throats, nausea, cold, and digestion.",
        "ingredients": ["Fresh Ginger Root", "Raw Honey", "Lemon", "Black Pepper"],
        "remedy_steps": [
            "Slice 1-inch fresh ginger thinly, add to 2 cups boiling water",
            "Simmer 5 minutes, strain",
            "Add juice of half lemon and 1-2 tsp raw honey when warm",
            "For nausea: 1/4 tsp fresh ginger juice directly, or ginger tea",
            "For sore throat: honey + ginger + black pepper paste, 1/4 tsp every 2 hours",
            "Ginger chew: suck on thin slice of fresh ginger for motion sickness",
        ],
        "health_benefits": ["Nausea","Sore Throat","Cold","Digestion","Anti-inflammatory","Menstrual Pain"],
        "active_compounds": ["Gingerol (6-gingerol)","Shogaol","Zingerone","Paradol"],
        "scientific_backing": [
            "Meta-analysis: 1g ginger daily significantly reduces nausea/vomiting in pregnancy",
            "5-HT3 antagonist activity (same mechanism as anti-nausea drug ondansetron)",
            "Honey: H2O2 production kills Staphylococcus pyogenes — sore throat pathogen",
            "Anti-inflammatory: Comparable to NSAIDs for menstrual pain in RCT",
        ],
        "dosha_type": "Vata, Kapha", "season_best": "Winter, Monsoon",
        "contraindications": ["Do not give honey to children under 1 year (botulism risk)","Avoid large ginger doses with anticoagulants"],
        "modern_relevance": ["Immunity Boosting","Gut Health","Women's Wellness"],
        "gen_z_hook": "Morning sickness drug sales: billions. 1g of ginger: same efficacy, zero money. 🫚",
        "state_of_origin": "All India (ginger from Kerala and NE India)",
        "source_name": "Charaka Samhita + TKDL", "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Mustard Oil Massage — Cold and Chest Rub",
        "title_sanskrit": "Sarshapa Taila (सर्षप तैल)",
        "domain": "Home Remedies", "subdomain": "Respiratory",
        "summary": "Mustard oil heated with garlic and applied to chest, back, and feet is one of the most common cold remedies across North India. Its erucic acid and allyl isothiocyanate have warming, antibacterial, and decongestant properties. Applied to the feet with garlic at night, it was the original 'vapour rub'.",
        "ingredients": ["Mustard Oil", "Garlic", "Ajwain (Carom Seeds)", "Camphor"],
        "remedy_steps": [
            "Heat 2 tbsp mustard oil with 3-4 crushed garlic cloves until garlic turns golden",
            "Add 1/2 tsp ajwain seeds, heat 30 more seconds",
            "Cool to warm (test on wrist), apply to chest and back while warm",
            "For congestion: add 1 small camphor piece to oil, apply to chest only",
            "For feet: rub warm garlic-mustard oil on soles and toes before bed, wear socks",
            "For babies: use warm (not hot) mustard oil massage daily in winter for warmth",
        ],
        "health_benefits": ["Cold","Congestion","Cough","Chest Tightness","Muscle Aches","Warming"],
        "scientific_backing": [
            "Allyl isothiocyanate: Creates heat through TRPV1 receptor activation (similar to capsaicin)",
            "Selenium in mustard oil: Antioxidant and antifungal",
            "Garlic allicin: Antimicrobial against respiratory pathogens",
            "Counter-irritant effect: Increases local blood flow and reduces deep congestion",
        ],
        "dosha_type": "Vata, Kapha", "season_best": "Winter",
        "contraindications": ["Do not apply near eyes or on broken skin","Allergy to mustard (rare)"],
        "modern_relevance": ["Immunity Boosting","Respiratory","Children's Health"],
        "gen_z_hook": "Vicks VapoRub was invented in 1894. The garlic-mustard oil trick: 3000 BCE. Your dadi was right. 👃",
        "state_of_origin": "North India (Punjabi/Rajasthani tradition especially)",
        "source_name": "Traditional Knowledge (Seed)", "source_url": "https://www.tkdl.res.in",
    },

    # ═══════════════════════════════════════════════════════════════
    #  YOGA  (20 entries)
    # ═══════════════════════════════════════════════════════════════
    {
        "title": "Surya Namaskar — Complete Body Workout",
        "title_sanskrit": "Surya Namaskar (सूर्य नमस्कार)",
        "domain": "Yoga", "subdomain": "Sequences",
        "summary": "Surya Namaskar (Sun Salutation) is a 12-step yoga sequence performed at sunrise that activates every major muscle group, joint, and organ system. 12 rounds = 288 postures in ~15 minutes. It combines strength, flexibility, cardiovascular fitness, and breathwork in one complete practice.",
        "origin_story": "The Rig Veda describes Surya (the Sun) as 'the soul of all that moves and all that is still'. Sun salutations as a movement practice are mentioned in the Aditya Hridayam (a hymn from the Ramayana). The modern 12-step form was systematised by Balasaheb Pratinidhi of Aundh in the 1920s.",
        "remedy_steps": [
            "Step 1 Pranamasana: Stand at mat edge, join palms at chest, exhale completely",
            "Step 2 Hastauttanasana: Inhale, raise arms overhead, gentle backbend",
            "Step 3 Hasta Padasana: Exhale, fold forward, palms to floor beside feet",
            "Step 4 Ashwa Sanchalanasana: Inhale, step right foot back, left knee over ankle",
            "Step 5 Dandasana: Hold breath, step left foot back, straight plank",
            "Step 6 Ashtanga Namaskara: Exhale, lower knees-chest-chin to floor (8 points touching)",
            "Step 7 Bhujangasana: Inhale, slide forward into cobra — shoulders down, look up",
            "Step 8 Adho Mukha Svanasana: Exhale, push back into downward-facing dog",
            "Steps 9-12: Mirror steps 4-1 in reverse (right side) to complete 1/2 round",
            "Left side repeats steps 4-8 with opposite foot — completes 1 full round",
            "Start with 2 rounds, build to 12 over 6 weeks",
        ],
        "yoga_poses": ["Pranamasana","Hastauttanasana","Hasta Padasana","Ashwa Sanchalanasana","Dandasana","Bhujangasana","Adho Mukha Svanasana","Ashtanga Namaskara"],
        "health_benefits": ["Flexibility","Strength","Cardiovascular","Metabolism","Posture","Digestion","Stress","Skin"],
        "mental_benefits": ["Stress","Anxiety","Mood","Focus","Energy"],
        "scientific_backing": [
            "12 rounds = ~150 calories burned — equivalent to jogging 1.5km",
            "Improves VO2 max with 3-month practice (RCT evidence)",
            "Reduces anxiety scores on GAD-7 significantly",
            "Improves spinal flexibility by 34% over 12 weeks",
        ],
        "dosha_type": "All doshas", "season_best": "All seasons", "time_of_day": "Sunrise",
        "difficulty_level": "Beginner to Intermediate",
        "duration": "15-30 minutes for 12 rounds",
        "breathing_type": "Synchronised inhale/exhale with each step",
        "contraindications": ["Avoid in advanced pregnancy","Avoid with hernia","Caution with high blood pressure — skip backbends"],
        "modern_relevance": ["Fitness & Yoga","Mental Health","Sustainability","Longevity"],
        "gen_z_hook": "Free HIIT + flexibility + meditation in 15 minutes. No gym required. Ancient. 🌅",
        "tiktok_angle": "I did 12 rounds of Surya Namaskar every day for 30 days. These were my results.",
        "challenge_idea": "30-day Surya Namaskar Challenge: start with 4 rounds, add 1 each week",
        "grandmother_quote": "Suraj niklte hi uthke namaskar karo — yeh duniya ki sabse purani dua hai.",
        "state_of_origin": "All India",
        "source_name": "Hatha Yoga Pradipika + Traditional Texts", "source_url": "https://www.yogamdniy.nic.in",
    },
    {
        "title": "Kapalbhati Pranayama — Skull Shining Breath",
        "title_sanskrit": "Kapalbhati (कपालभाति)",
        "domain": "Yoga", "subdomain": "Pranayama (Breath Practices)",
        "summary": "Kapalbhati is a powerful active exhalation practice from Hatha Yoga. 'Kapal' means skull, 'bhati' means shining — regular practice makes the face luminous. Modern research confirms it activates core muscles, increases metabolic rate, clears airways, and stimulates the digestive organs through abdominal pressure changes.",
        "remedy_steps": [
            "Sit in Padmasana or Sukhasana with spine erect",
            "Take a deep preparatory inhale",
            "Exhale sharply through the nose by contracting abdomen inward and upward",
            "Inhale passively as the abdomen naturally expands — no effort needed",
            "Begin with 30 pumps in 30 seconds, rest 1 minute",
            "Gradually build to 120 pumps per minute over 4 weeks",
            "3-5 sets per session",
            "BEST: early morning on empty stomach",
            "AVOID: pregnancy, hypertension, recent abdominal surgery, hernia",
        ],
        "yoga_poses": ["Kapalbhati","Padmasana","Sukhasana"],
        "health_benefits": ["Digestion","Weight","Metabolism","Respiratory","Energy","Skin","Sinuses"],
        "mental_benefits": ["Clarity","Energy","Stress","Depression"],
        "scientific_backing": [
            "Increases FEV1 (forced expiratory volume) by 14% after 6 weeks",
            "Activates transversus abdominis and rectus abdominis — deep core strengthening",
            "Increases basal metabolic rate during and after practice",
            "Parasympathetic activation post-practice: lowers cortisol by 23%",
        ],
        "dosha_type": "Kapha (especially beneficial)", "season_best": "All seasons",
        "time_of_day": "Morning (empty stomach)",
        "difficulty_level": "Beginner",
        "breathing_type": "Active exhalation, passive inhalation",
        "contraindications": ["Absolute: pregnancy","High blood pressure (above 160/100)","Recent abdominal surgery or hernia","Epilepsy","Heart disease (consult doctor)"],
        "modern_relevance": ["Fitness & Yoga","Gut Health","Mental Health","Detox"],
        "gen_z_hook": "Free metabolism hack. No Ozempic needed. Just breathe wrong. Wait, breathe RIGHT. 💨",
        "tiktok_angle": "Day 1 vs Day 30 of Kapalbhati — the change in my belly (and my anxiety) shocked me",
        "challenge_idea": "60-day Kapalbhati Challenge: 5 min daily, track energy and digestion weekly",
        "grandmother_quote": "Kapalbhati kar le — koi dawaai nahi chahiye phir.",
        "source_name": "Hatha Yoga Pradipika + Gheranda Samhita", "source_url": "https://www.yogamdniy.nic.in",
    },
    {
        "title": "Anulom Vilom — Alternate Nostril Breathing",
        "title_sanskrit": "Nadi Shodhana Pranayama (नाड़ी शोधन)",
        "domain": "Yoga", "subdomain": "Pranayama (Breath Practices)",
        "summary": "Alternate nostril breathing (Nadi Shodhana) balances the left (Ida — lunar) and right (Pingala — solar) nadis, corresponding to the parasympathetic and sympathetic nervous systems. It is the most studied yoga breathing technique with robust evidence for blood pressure reduction, anxiety relief, and cognitive enhancement.",
        "remedy_steps": [
            "Sit comfortably, form Vishnu mudra: fold index and middle fingers, use thumb for right nostril, ring finger for left",
            "Exhale completely",
            "Close right nostril with thumb, inhale through left for 4 counts",
            "Close both nostrils, retain breath for 4-8 counts (optional for beginners: skip retention)",
            "Release thumb, close left nostril with ring finger, exhale through right for 8 counts",
            "Inhale through right for 4 counts",
            "Close both, retain 4-8 counts",
            "Exhale through left for 8 counts = 1 complete cycle",
            "Do 10-20 cycles. Build time over weeks. Ratio: inhale 1 : retain 2-4 : exhale 2",
        ],
        "yoga_poses": ["Anulom Vilom","Nadi Shodhana","Vishnu Mudra","Padmasana"],
        "health_benefits": ["Blood Pressure","Stress","Anxiety","Sleep","Asthma","Respiratory","Heart"],
        "mental_benefits": ["Anxiety","Stress","Memory","Focus","Brain Balance","Calm"],
        "scientific_backing": [
            "Significantly reduces systolic and diastolic blood pressure in hypertensive patients (RCT)",
            "EEG shows synchronised alpha wave activity across both hemispheres post-practice",
            "Right nostril breathing activates left brain (logic); left nostril activates right brain (creativity)",
            "Improves spatial memory and reaction time vs control group",
            "Reduces anxiety comparable to lorazepam in dental patients (RCT)",
        ],
        "dosha_type": "All doshas", "season_best": "All seasons",
        "time_of_day": "Morning, evening, or before sleep",
        "difficulty_level": "Beginner",
        "breathing_type": "Alternate nostril, controlled",
        "contraindications": ["Avoid breath retention if hypertensive","Avoid with severe nasal congestion (use decongestant first)"],
        "modern_relevance": ["Mental Health","Sleep Wellness","Fitness & Yoga","Blood Pressure"],
        "gen_z_hook": "Box breathing for Navy SEALs costs $2000 in training. This is the same thing. Free. For 3000 years. 🫁",
        "state_of_origin": "All India (Yoga tradition)",
        "source_name": "Yoga Sutras + Hatha Yoga Pradipika", "source_url": "https://www.yogamdniy.nic.in",
    },
    {
        "title": "Dinacharya — Ayurvedic Daily Routine",
        "title_sanskrit": "Dinacharya (दिनचर्या)",
        "domain": "Ayurveda", "subdomain": "Lifestyle Medicine",
        "summary": "Dinacharya is the complete Ayurvedic framework for an optimal daily routine. It syncs human biology with the sun's rhythms across three dosha periods: Kapha (6-10), Pitta (10-2), Vata (2-6) both AM and PM. Modern chronobiology is now confirming what Ayurveda described 3000 years ago about circadian rhythm and health.",
        "origin_story": "Charaka wrote: 'One who follows the daily regimen with care will live for 100 years without disease.' Brahma Muhurta (1.5 hours before sunrise) is said to be the time when the universe is most sattvic — modern sleep science calls this the light REM stage most aligned with memory consolidation.",
        "ingredients": ["Sesame Oil", "Neem Twig", "Copper Tongue Scraper", "Warm Water"],
        "remedy_steps": [
            "Brahma Muhurta wake-up: Rise 90 min before sunrise (~4:30-5:30 AM)",
            "Ushapan: Drink 2-3 cups warm water (copper vessel preferred) immediately on rising",
            "Natural elimination: allow 15 minutes for natural bowel movement",
            "Tongue scraping: 7-10 backward strokes with copper scraper (removes ama/toxins from tongue)",
            "Oil pulling (Gandusha): 1 tbsp sesame oil, swish 15-20 min, spit in bin",
            "Abhyanga: Warm oil self-massage head to toe before shower (15-20 min)",
            "Vyayama (Exercise/Yoga): Surya Namaskar + pranayama during Kapha time (6-10 AM)",
            "Breakfast: light, warm, after exercise — not immediately on waking",
            "Main meal (Dinacharya): at noon (Pitta peak — strongest digestive fire)",
            "Nap: 20-30 min post-lunch in summer (Nidra — not in winter)",
            "Evening walk at sunset — Sandhyavandana time",
            "Dinner: light, before 7 PM — do NOT eat after 8 PM",
            "Wind-down: screen-free by 9 PM, sleep by 10 PM (Pitta time begins — avoid sleep at Pitta time)",
        ],
        "health_benefits": ["Digestion","Sleep","Energy","Skin","Dental","Mental Health","Immunity","Weight"],
        "scientific_backing": [
            "Circadian biology: Eating aligned with daylight reduces metabolic syndrome risk by 36%",
            "Time-restricted eating (TRE) research confirms Ayurvedic meal timing for metabolic health",
            "Tongue scraping: Removes bacteria that cause halitosis and contribute to gut dysbiosis",
            "Abhyanga massage: Reduces cortisol and improves lymphatic drainage (validated in RCTs)",
            "Brahma Muhurta waking: Aligns with natural cortisol awakening response peak (5-8 AM)",
        ],
        "dosha_type": "All doshas", "season_best": "All seasons (adjusted per season)",
        "difficulty_level": "Intermediate (full practice)",
        "modern_relevance": ["Mental Health","Sleep Wellness","Gut Health","Skincare","Fitness & Yoga","Longevity"],
        "gen_z_hook": "Huberman Lab protocol 2024 = Charaka Samhita 600 BCE. We just forgot it for 200 years. 🕰️",
        "tiktok_angle": "I followed Ayurvedic dinacharya for 30 days. Morning routine results week 1 vs week 4.",
        "challenge_idea": "7-day Dinacharya Challenge: add 1 new practice per day for a week",
        "grandmother_quote": "Brahma muhurta mein utho. Duniya ki jo bhi problems hain — woh is ek aadat se aadhi kam ho jaayengi.",
        "state_of_origin": "All India (classical Ayurvedic practice)",
        "source_name": "Ashtanga Hridayam + Charaka Samhita", "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Yoga Nidra — Sleep of the Yogis",
        "title_sanskrit": "Yoga Nidra (योग निद्रा)",
        "domain": "Yoga", "subdomain": "Meditation & Deep Relaxation",
        "summary": "Yoga Nidra is a state of conscious sleep — aware but completely relaxed, suspended between waking and sleeping. One hour of Yoga Nidra is said to equal 4 hours of deep sleep. It is the only practice proven to produce delta brain waves while the practitioner remains conscious.",
        "remedy_steps": [
            "Lie in Savasana (flat on back, arms slightly away, palms up)",
            "Close eyes, take 3 deep sighing breaths",
            "Follow a guided voice rotating awareness through 61 body parts (Brahmananda Saraswati method)",
            "Maintain awareness while allowing the body to enter deep relaxation (not sleep)",
            "Visualize opposites: hot/cold, heavy/light, pain/pleasure (activates right brain)",
            "Receive a Sankalpa (intention) — plant it in the fertile ground of the hypnagogic state",
            "Minimum 30 minutes for full cycle",
            "Guided recordings available on YouTube (look for Swami Satyananda tradition)",
        ],
        "yoga_poses": ["Savasana"],
        "health_benefits": ["Sleep","Anxiety","PTSD","Chronic Pain","Insomnia","Fatigue","Hypertension"],
        "mental_benefits": ["Stress","Anxiety","PTSD","Depression","Trauma Healing","Memory Consolidation"],
        "scientific_backing": [
            "EEG: Produces theta (4-8 Hz) and delta (0.5-4 Hz) waves while maintaining consciousness",
            "US military using Yoga Nidra (as iRest) for PTSD — equivalent to CBT in trials",
            "Dopamine release increased by 65% during Yoga Nidra (PET scan study)",
            "Reduces chronic pain symptoms in cancer patients comparable to medication",
        ],
        "dosha_type": "Vata, Pitta", "season_best": "All seasons",
        "time_of_day": "Midday, evening, or before sleep",
        "difficulty_level": "Beginner",
        "breathing_type": "Natural, diaphragmatic",
        "modern_relevance": ["Mental Health","Sleep Wellness","Trauma Healing"],
        "gen_z_hook": "The US Army uses this for PTSD. The yoga masters invented it 4000 years ago. 😴",
        "state_of_origin": "All India (Swami Satyananda Saraswati modernised, Bihar School of Yoga)",
        "source_name": "Mandukya Upanishad + Bihar School of Yoga", "source_url": "https://www.yogamdniy.nic.in",
    },
    {
        "title": "Bhramari Pranayama — Humming Bee Breath",
        "title_sanskrit": "Bhramari (भ्रामरी) — Humming Breath",
        "domain": "Yoga", "subdomain": "Pranayama (Breath Practices)",
        "summary": "Bhramari involves exhaling with a humming sound (like a bee) while plugging ears and eyes with fingers. The vibration activates the vagus nerve, instantly calming the nervous system. It is the fastest-acting pranayama for acute anxiety and panic.",
        "remedy_steps": [
            "Sit comfortably with spine straight",
            "Use Shanmukhi mudra: thumbs plug ears, index fingers gently cover closed eyelids, middle fingers on nostrils (gently), ring fingers above lips, little fingers below lips",
            "Take a deep inhale through the nose",
            "On the exhale, make a continuous humming sound (mmmmm) like a bee",
            "Feel the vibration in the skull, forehead, and chest",
            "Exhale completely before next inhale",
            "5-10 rounds for acute anxiety; 15-20 min for meditation",
        ],
        "yoga_poses": ["Bhramari","Shanmukhi Mudra","Padmasana"],
        "health_benefits": ["Anxiety","Blood Pressure","Migraine","Insomnia","Thyroid"],
        "mental_benefits": ["Anxiety","Panic Attacks","Stress","Anger","Racing Thoughts"],
        "scientific_backing": [
            "Vagal nerve stimulation via cranial vibration — same mechanism as medical VNS devices",
            "Increases nitric oxide production in nasal sinuses — antimicrobial and vasodilatory",
            "Lowers heart rate and blood pressure within 5 minutes",
            "Binaural beat effect from bilateral ear plugging — induces alpha/theta brain states",
        ],
        "dosha_type": "Pitta, Vata", "season_best": "All seasons",
        "time_of_day": "Anytime, especially during acute stress",
        "difficulty_level": "Beginner",
        "modern_relevance": ["Mental Health","Sleep Wellness","Fitness & Yoga"],
        "gen_z_hook": "Having a panic attack? 3 rounds of Bhramari. It works in under 2 minutes. Ancient neuroscience. 🐝",
        "tiktok_angle": "I replaced Xanax with Bhramari pranayama. Here's my honest 90-day report.",
        "state_of_origin": "All India",
        "source_name": "Hatha Yoga Pradipika + Gheranda Samhita", "source_url": "https://www.yogamdniy.nic.in",
    },

    # ═══════════════════════════════════════════════════════════════
    #  FOOD & CULTURE  (20 entries)
    # ═══════════════════════════════════════════════════════════════
    {
        "title": "Sattvic Diet — Yogic Eating System",
        "title_sanskrit": "Sattvic Aahar (सात्त्विक आहार)",
        "domain": "Food & Culture", "subdomain": "Ayurvedic Diet",
        "summary": "Ayurveda classifies food into three categories based on their effect on mind and body: Sattvic (pure, light, promotes clarity), Rajasic (stimulating, activating), and Tamasic (heavy, dulling, promoting inertia). This 5000-year-old food classification system remarkably aligns with modern nutritional science on gut-brain connection and neuroinflammation.",
        "ingredients": ["Fruits","Vegetables","Whole Grains","Legumes","Dairy","Nuts","Seeds","Honey","Jaggery"],
        "remedy_steps": [
            "Sattvic foods: fresh fruits, vegetables, dairy, whole grains, legumes, nuts, honey",
            "Eat freshly cooked food within 4 hours of cooking (prana is highest)",
            "Avoid reheated, stale, or processed food (tamasic)",
            "Eat in calm environment, with gratitude, without screens or arguments (emotional sattvic)",
            "Avoid overeating — fill stomach: 50% food, 25% water, 25% empty (air space)",
            "Rajasic to limit: excess spice, caffeine, onion, garlic (stimulating — fine in moderation)",
            "Tamasic to avoid: meat, alcohol, heavily processed foods, stale food",
        ],
        "health_benefits": ["Mental Clarity","Digestion","Energy","Mood","Sleep","Skin","Immunity"],
        "mental_benefits": ["Clarity","Focus","Calm","Creativity","Emotional Balance"],
        "scientific_backing": [
            "Gut-brain axis: Diet directly modulates neurotransmitter production (90% of serotonin in gut)",
            "Inflammatory foods (high-fat, processed) increase neuroinflammation — aligns with 'tamasic' category",
            "Mediterranean/plant-rich diet (similar to sattvic) reduces depression risk by 33% (meta-analysis)",
            "Mindful eating reduces cortisol and improves digestive enzyme production",
        ],
        "dosha_type": "All doshas (promotes sattva in all)", "season_best": "All seasons",
        "modern_relevance": ["Mental Health","Gut Health","Immunity Boosting","Longevity"],
        "gen_z_hook": "The gut-brain axis paper won a Nobel. Ayurveda wrote about Sattvic food 5000 years ago. 🥗",
        "grandmother_quote": "Taaza khana khao. Taza soch aayegi. Taaza jeevan milega.",
        "state_of_origin": "All India (Vedic tradition)",
        "source_name": "Bhagavad Gita Ch 17 + Charaka Samhita", "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Fermented Foods of India — Probiotic Heritage",
        "title_sanskrit": "Khameer/Kanjika (खमीर)",
        "domain": "Food & Culture", "subdomain": "Traditional Preservation & Gut Health",
        "summary": "India has one of the world's richest traditions of fermented foods — idli, dosa, dhokla, kanji, lassi, chaas, pickle, koozh, ambali, and dozens more regional variants. These 5000-year-old fermentation techniques naturally produce probiotics, increase nutrient bioavailability, and support gut microbiome diversity.",
        "ingredients": ["Rice","Urad Dal","Mustard","Fenugreek","Beetroot","Carrots","Yogurt","Buttermilk"],
        "remedy_steps": [
            "Idli-Dosa batter: soak rice + urad dal separately 6 hours, grind, ferment overnight (8-12 hours)",
            "Kanji (Probiotic Drink): grate carrots/beetroot, soak in mustard water 2-3 days at room temperature",
            "Lassi: blend yogurt + water + spices — naturally probiotic, digestive, cooling",
            "Chaas (Buttermilk): diluted yogurt with rock salt + roasted cumin — post-meal digestive",
            "Pickle: seasonal vegetables in oil + mustard seed + fenugreek — traditional lacto-fermentation",
            "Koozh (Tamil Nadu): fermented millet porridge — overnight soak, morning meal",
        ],
        "health_benefits": ["Gut Health","Immunity","Digestion","Nutrition","Mental Health","Diabetes","Cholesterol"],
        "scientific_backing": [
            "Fermentation increases B-vitamin content by 200-300% (especially B12 in yogurt-based)",
            "Phytic acid reduction: 60-90% reduction in antinutrients during idli/dosa fermentation",
            "Gut diversity: Daily fermented food consumption increases microbiome diversity by 20% (Stanford RCT)",
            "Lactobacillus plantarum from Indian pickles: Clinically proven probiotic strain",
        ],
        "dosha_type": "Pitta, Kapha (balanced in moderation)", "season_best": "Summer, Monsoon",
        "modern_relevance": ["Gut Health","Immunity Boosting","Mental Health","Sustainability"],
        "gen_z_hook": "You're paying ₹400 for Yakult. Your dadi was making kanji at home since birth. 🫙",
        "grandmother_quote": "Roz chaas peeyo. Pet saaf, mann saaf.",
        "state_of_origin": "All India (each region has unique fermented foods)",
        "source_name": "Charaka Samhita + Regional Food Traditions", "source_url": "https://www.indianculture.gov.in",
    },
    {
        "title": "Haldi Ceremony (Ubtan) — Pre-Wedding Skin Ritual",
        "title_sanskrit": "Pithi / Ubtan (उबटन)",
        "domain": "Food & Culture", "subdomain": "Beauty & Skin Rituals",
        "summary": "The Haldi ceremony involves applying a paste of turmeric, sandalwood, rose water, and chickpea flour to the bride (and groom) before the wedding. This ancient ritual was simultaneously a spiritual purification, skin brightening treatment, antimicrobial protection, and stress relief ceremony before the biggest day of life.",
        "ingredients": ["Turmeric","Sandalwood Powder","Rose Water","Chickpea Flour (Besan)","Milk","Honey","Saffron","Neem"],
        "remedy_steps": [
            "Mix 2 tbsp besan + 1 tsp turmeric + 1 tsp sandalwood + rose water into smooth paste",
            "Optional: add saffron strands soaked in 2 tbsp milk + 1 tsp honey",
            "Apply to face and body in circular motions",
            "Allow to dry 15-20 minutes",
            "Exfoliate gently with hands under water — removes dead skin while tightening pores",
            "Use daily for 1 week before a special occasion for visible brightening",
            "For daily face care: besan + turmeric + yogurt paste, rinse after 10 min",
        ],
        "health_benefits": ["Skin Brightening","Acne","Tan Removal","Exfoliation","Anti-aging"],
        "scientific_backing": [
            "Turmeric curcumin: Inhibits melanin synthesis (same target as hydroquinone — without side effects)",
            "Besan (exfoliant): Removes dead skin cells through enzymatic and physical action",
            "Sandalwood: Inhibits 5-alpha-reductase — anti-acne mechanism",
            "Rose water: Tannins reduce pore size and inflammation",
        ],
        "dosha_type": "Pitta", "season_best": "All seasons",
        "modern_relevance": ["Skincare","Sustainability","Zero-cost","Women's Wellness"],
        "gen_z_hook": "₹2000 brightening serum vs. ₹50 haldi ubtan. Both inhibit melanin. One has a 5000-year track record. ✨",
        "related_festival": "Haldi Ceremony (pre-wedding)",
        "state_of_origin": "All India (especially North India, Punjab, Rajasthan)",
        "source_name": "Traditional Beauty Texts + Ayurvedic Recipes", "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Jal Neti — Nasal Irrigation",
        "title_sanskrit": "Jala Neti (जल नेति)",
        "domain": "Yoga", "subdomain": "Shatkarma (Cleansing Practices)",
        "summary": "Jal Neti involves pouring warm salt water through one nostril and letting it flow out the other using a Neti pot. It is one of the six Shatkarmas (purification practices) of Hatha Yoga. The FDA in the USA has officially recommended nasal irrigation for sinus congestion as a drug-free alternative.",
        "ingredients": ["Warm Water","Non-Iodised Salt","Neti Pot"],
        "ingredient_quantities": {"Warm Water": "500ml (body temperature)","Non-Iodised Salt": "1/4 to 1/2 tsp"},
        "remedy_steps": [
            "Mix 1/4 tsp non-iodised salt per 250ml warm water (saline solution — same as blood)",
            "Fill neti pot with warm saline",
            "Stand over sink, tilt head 45 degrees to right",
            "Insert spout into right nostril, pour slowly — water flows out left nostril",
            "Breathe through the mouth continuously",
            "Repeat on left side",
            "After neti: blow nose gently 3-4 times each side to remove remaining water",
            "Practice kapal bhati 2-3 minutes to dry nasal passages",
            "Do NOT use tap water — must be sterile or boiled-cooled",
        ],
        "health_benefits": ["Sinusitis","Allergies","Congestion","Cold Prevention","Snoring","Headache","Asthma"],
        "scientific_backing": [
            "Cochrane review: Saline nasal irrigation significantly reduces symptoms in chronic sinusitis",
            "FDA officially recommends nasal irrigation as first-line treatment for sinusitis",
            "Reduces need for antibiotics in acute bacterial sinusitis by 70% (RCT)",
            "Clears pollen, dust, and pollution particles from nasal mucosa",
        ],
        "dosha_type": "Kapha", "season_best": "Monsoon, Autumn (allergy season)",
        "time_of_day": "Morning",
        "difficulty_level": "Beginner",
        "contraindications": ["Never use tap water (amoebic infection risk)","Avoid with active ear infection","Avoid immediately before lying down"],
        "modern_relevance": ["Immunity Boosting","Respiratory","Sustainability"],
        "gen_z_hook": "FDA-approved nasal irrigation. Hatha Yoga Pradipika: 5000 BCE. They agree. 💧",
        "state_of_origin": "All India (Yoga tradition)",
        "source_name": "Hatha Yoga Pradipika + Gheranda Samhita", "source_url": "https://www.yogamdniy.nic.in",
    },

    # ═══════════════════════════════════════════════════════════════
    #  ORAL HISTORY & STORIES  (15 entries)
    # ═══════════════════════════════════════════════════════════════
    {
        "title": "The Legend of Dhanvantari — God of Medicine",
        "title_sanskrit": "Dhanvantari (धन्वन्तरी)",
        "domain": "Oral History", "subdomain": "Origin Stories",
        "summary": "Dhanvantari is the Hindu god of medicine who emerged from the churning of the cosmic ocean (Samudra Manthan) holding the pot of Amrita (immortality nectar). He is the divine founder of Ayurveda. The Dhanvantari Trayodashi festival (Dhanteras) celebrates his birthday — the day before Diwali.",
        "oral_story_snippet": "Long ago, the gods and demons churned the cosmic ocean to obtain Amrita, the nectar of immortality. After many divine gifts emerged from the churning, at the very end, Dhanvantari arose — wearing white robes, carrying a conch and a Sudarshana Chakra, holding in one hand the sacred pot of Amrita. It was he who transmitted the knowledge of Ayurveda to the sages, and through them, to all of humanity.",
        "origin_story": "Dhanvantari is mentioned in the Bhagavata Purana as the twelfth avatar of Vishnu, who descended to end the suffering of disease and death. The Charaka Samhita and Sushruta Samhita both trace their lineage through him.",
        "how_it_was_forgotten": "Colonialism systematically discredited indigenous medical knowledge as superstition. Dhanvantari temples were seen as religious, not scientific — the knowledge was separated from its cultural container.",
        "health_benefits": ["Cultural Heritage","Meaning-Making","Connection to Ancestry"],
        "modern_relevance": ["Mental Health","Oral Tradition","Cultural Identity"],
        "gen_z_hook": "The 5000-year-old origin story of an entire medical system. Told by word of mouth. Never patented. 🌊",
        "grandmother_quote": "Dhanvantari ne diya tha yeh gyaan. Hum sirf bhool gaye the.",
        "related_festival": "Dhanteras (two days before Diwali)",
        "state_of_origin": "All India (Vedic tradition)",
        "source_name": "Bhagavata Purana + Charaka Samhita", "source_url": "https://www.indianculture.gov.in",
    },
    {
        "title": "The Panchatantra — Original Management Philosophy",
        "title_sanskrit": "Panchatantra (पञ्चतन्त्र)",
        "domain": "Oral History", "subdomain": "Ancient Wisdom Literature",
        "summary": "The Panchatantra, composed around 300 BCE by the scholar Vishnu Sharma, is the world's most widely translated non-religious text — translated into 50+ languages. It uses animal fables to teach five tantra (principles): friends and allies, enemies, war and peace, loss of gains, and rash action.",
        "oral_story_snippet": "Once, the crow, deer, mouse, turtle and crow were friends who lived by a lake. One day, a hunter came. The deer was caught in a trap. The mouse quickly chewed through the net. The crow distracted the hunter. The turtle lured the hunter away. Each used their unique gift. This is the first lesson of the Panchatantra: Mitra-bheda — only those who know how to build allies can survive.",
        "origin_story": "King Amarasakti of Mahilaropya had three 'incorrigible' princes who refused to learn. He gave them to the scholar Vishnu Sharma, who promised to make them wise in 6 months using only stories. The Panchatantra is that curriculum — the world's first 'gamified' teaching method.",
        "how_it_was_forgotten": "Reduced to 'children's stories'. The deep political philosophy of niti (statecraft) was stripped out by Victorian translators who published only the moral tales, losing the strategic wisdom.",
        "modern_relevance": ["Mental Health","Oral Tradition","Cultural Identity","Mental Performance"],
        "gen_z_hook": "Harvard Business School case studies: 1908. Panchatantra: 300 BCE. Same lessons. The deer, the net, the allies.",
        "grandmother_quote": "Ek akele hiran ka kya hoga? Panchatantra padha hota to jaanta — dost banao pehle.",
        "related_festival": "Told during Diwali nights traditionally",
        "state_of_origin": "Kashmir/Central India (Amarasakti's kingdom)",
        "source_name": "Panchatantra (Vishnu Sharma)", "source_url": "https://www.indianculture.gov.in",
    },
    {
        "title": "Kolam — Tamil Living Geometry",
        "title_sanskrit": "Kolam (கோலம்) / Rangoli",
        "domain": "Arts & Culture", "subdomain": "Sacred Geometry & Daily Art",
        "summary": "Kolam is a Tamil tradition of drawing geometric patterns at the threshold of homes each morning using rice flour. It is simultaneously spiritual practice, spatial reasoning exercise, mathematical exploration, and daily meditation. Computer scientists have studied Kolam patterns as equivalent to Lindenmayer systems (L-systems) — formal grammars used in computational biology.",
        "origin_story": "In the Silappadikaram (Tamil epic, 2nd century CE), Kolam is mentioned as a daily practice of Tamil women. The rice flour feeds ants and insects — a daily act of feeding all living beings before feeding the family.",
        "oral_story_snippet": "Every morning, before the sun rose, Thangam would wash the threshold and bend to draw. Her mother's mother had drawn the same pattern. And her mother's mother before that. Nobody had written it down. The pattern lived in her hands.",
        "how_it_was_forgotten": "Urbanisation replaced thresholds with apartment doors. Vinyl sticker kolams replaced hand-drawn art. The daily practice became a weekend decoration, losing its meditative and mathematical dimension.",
        "modern_relevance": ["Mental Health","Arts & Culture","Sustainability","Mental Performance","Children's Health"],
        "gen_z_hook": "CS researchers found that Kolam patterns contain the same mathematical structure as computer fractals. Tamil women were doing computational geometry every morning. 🌺",
        "challenge_idea": "7-day Kolam Challenge: draw one pattern each morning for a week. Share it.",
        "state_of_origin": "Tamil Nadu, Kerala, Karnataka, Andhra Pradesh",
        "source_name": "Silappadikaram + IGNCA", "source_url": "https://www.indianculture.gov.in",
    },

    # ═══════════════════════════════════════════════════════════════
    #  SUSTAINABLE FARMING  (10 entries)
    # ═══════════════════════════════════════════════════════════════
    {
        "title": "Jeevamrit — Living Elixir for Soil",
        "title_sanskrit": "Jeevamrit (जीवामृत)",
        "domain": "Sustainable Farming", "subdomain": "Zero Budget Natural Farming",
        "summary": "Jeevamrit is the cornerstone of Subhash Palekar's Zero Budget Natural Farming (ZBNF). It is a fermented microbial inoculant made from desi cow dung, cow urine, jaggery, pulse flour, and native soil. Applied every 15 days, it dramatically increases soil microbial biomass, making nutrients bioavailable without chemical inputs.",
        "ingredients": ["Desi Cow Dung (fresh)", "Desi Cow Urine", "Jaggery (raw)", "Pulse Flour (Besan)", "Native Soil", "Water"],
        "ingredient_quantities": {"Cow Dung": "10kg", "Cow Urine": "10L", "Jaggery": "2kg", "Pulse Flour": "2kg", "Soil": "1 handful", "Water": "200L"},
        "remedy_steps": [
            "Fill 200L barrel with 180L water",
            "Add 10kg fresh cow dung + 10L cow urine",
            "Add 2kg jaggery (jaggery feeds the microbes during fermentation)",
            "Add 2kg pulse/grain flour (provides nitrogen for microbial growth)",
            "Add one handful of undisturbed native soil from under a 10+ year old tree",
            "Stir vigorously clockwise for 5 minutes",
            "Cover loosely (allow air) and ferment in shade for exactly 48 hours",
            "Stir twice daily during fermentation (morning and evening)",
            "Dilute 10% in irrigation water OR apply directly as foliar spray",
            "Apply every 15 days throughout the growing season",
        ],
        "health_benefits": ["Soil Microbial Diversity","Crop Yield","Water Retention","Nutrient Availability"],
        "scientific_backing": [
            "Increases soil microbial diversity by 10-15 times vs. chemical farming plots",
            "Increases total microbial biomass carbon from 150 to 1200 mg/kg soil in 3 years",
            "Maintains yield parity with chemical farming in 3-year transition studies (ICAR)",
            "Humus formation increases field water retention by 20-30%",
            "Reduces input cost to near-zero — $0 vs $200-500/acre for chemical farming",
        ],
        "season_best": "Apply year-round, every 15 days",
        "modern_relevance": ["Sustainability","Climate Resilience","Zero-cost","Food Security"],
        "gen_z_hook": "Silicon Valley spends billions on soil health tech. This costs ₹100 per acre and you need a cow. 🐄",
        "state_of_origin": "Vidarbha region (Subhash Palekar's origin), now nationwide ZBNF movement",
        "source_name": "Subhash Palekar ZBNF Training Materials", "source_url": "https://zerobudgetfarming.com",
    },
    {
        "title": "Bijamrit — Seed Treatment for Disease Resistance",
        "title_sanskrit": "Bijamrit (बीजामृत)",
        "domain": "Sustainable Farming", "subdomain": "Zero Budget Natural Farming",
        "summary": "Bijamrit is the companion to Jeevamrit — a seed treatment that coats seeds before planting with a protective microbial layer. It dramatically reduces seed-borne disease while activating beneficial soil microbes from the first moment of germination.",
        "ingredients": ["Desi Cow Dung (fresh)", "Desi Cow Urine", "Water", "Lime", "Native Soil"],
        "ingredient_quantities": {"Cow Dung": "500g", "Cow Urine": "1L", "Water": "5L", "Lime": "50g"},
        "remedy_steps": [
            "Dissolve 50g lime in 5L water overnight",
            "Add 500g fresh cow dung + 1L cow urine",
            "Add handful of native soil",
            "Mix and allow to ferment for 24 hours",
            "Filter through cloth",
            "Pour over seeds on a clean surface, coat thoroughly",
            "Shade-dry for 30 minutes",
            "Plant immediately — do not store Bijamrit-treated seeds",
        ],
        "health_benefits": ["Seed Germination","Disease Resistance","Seedling Vigour","Root Development"],
        "scientific_backing": [
            "Reduces damping-off disease (fungal) by 60-80% vs untreated seeds",
            "Improves germination percentage by 15-20% in field trials",
            "Lime creates pH barrier against soil-borne pathogens",
        ],
        "modern_relevance": ["Sustainability","Climate Resilience","Food Security"],
        "gen_z_hook": "Monsanto sells seed treatment coatings for $400/kg. This costs ₹5. Same function. 🌱",
        "state_of_origin": "Vidarbha, Maharashtra",
        "source_name": "Subhash Palekar ZBNF", "source_url": "https://zerobudgetfarming.com",
    },

    # ═══════════════════════════════════════════════════════════════
    #  ANCIENT ASTRONOMY & MATHEMATICS  (10 entries)
    # ═══════════════════════════════════════════════════════════════
    {
        "title": "Aryabhata and the Invention of Zero",
        "title_sanskrit": "Shunya (शून्य) — The Void that Changed Mathematics",
        "domain": "Vedic Mathematics", "subdomain": "Number Theory",
        "summary": "The concept of zero as a number (not just a placeholder) was invented in India. Brahmagupta (7th century CE) first formalised the arithmetic of zero in Brahmasphutasiddhanta. Without zero, modern computing, cryptography, calculus, and physics would be impossible. This is arguably India's greatest intellectual gift to humanity.",
        "origin_story": "The word 'zero' derives from Sanskrit 'Shunya' (the void) via Arabic 'sifr'. When Arab traders carried Indian numerals back to Baghdad in the 9th century, the concept of zero transformed Islamic mathematics — and through them, European mathematics. Without this transmission, the Renaissance may never have happened.",
        "how_it_was_forgotten": "Eurocentrism in education attributed modern mathematics to Greek and Roman traditions. Indian mathematical contributions were systematically overlooked in colonial-era curricula that are still largely unchanged today.",
        "modern_relevance": ["Mental Performance","Cultural Identity","Children's Health"],
        "gen_z_hook": "No zero = no computers. No zero = no internet. No zero = you're reading this on paper. Thank India. 0️⃣",
        "grandmother_quote": "Shunya ne sab kuch diya. Khaali haath se hi duniya bani.",
        "state_of_origin": "India (Aryabhata from Patliputra, Bihar)",
        "source_name": "Aryabhatiya + Brahmasphutasiddhanta", "source_url": "https://www.indianculture.gov.in",
    },
    {
        "title": "Vedic Maths Sutras — Speed Computation",
        "title_sanskrit": "Vedic Ganita (वैदिक गणित)",
        "domain": "Vedic Mathematics", "subdomain": "Computational Shortcuts",
        "summary": "Vedic Mathematics consists of 16 sutras (formulas) and 13 sub-sutras extracted from the Vedas by Swami Bharati Krishna Tirthaji in the early 20th century. These sutras provide remarkably efficient mental calculation methods — allowing multiplication of large numbers in 5 seconds, square roots mentally, and complex division without long division.",
        "oral_story_snippet": "A Vedic maths student was asked to multiply 97 × 98. In 3 seconds, she answered 9506. 'How?' the teacher asked. '97 is 3 short of 100. 98 is 2 short. Add the deficiencies: 3+2=5. Subtract from 100: 95. Multiply the deficiencies: 3×2=06. Answer: 9506.' This is the Nikhilam Navatashcaramam Dashatah sutra. It works for any numbers near a base.",
        "remedy_steps": [
            "Multiplication near base 10: e.g., 9×8: both are 1 and 2 below 10. Cross-subtract: 9-2=7 OR 8-1=7. Multiply shortfalls: 1×2=2. Answer: 72.",
            "Multiplication near base 100: e.g., 97×98: shortfalls 3 and 2. 97-2=95. 3×2=06. Answer: 9506.",
            "Multiplication by 11: 25×11 = 2_5 → insert sum of digits in middle: 2+5=7 → 275.",
            "Squaring numbers ending in 5: 75² = (7×8) followed by 25 = 5625.",
            "Divisibility tests: any number's digits sum to 9 = divisible by 9.",
        ],
        "modern_relevance": ["Mental Performance","Children's Health","Cultural Identity"],
        "gen_z_hook": "No calculator. No paper. Large number multiplication in under 5 seconds. Ancient India did it. 🧮",
        "challenge_idea": "30-day Vedic Maths Daily Challenge: one sutra per week, 5 problems daily",
        "grandmother_quote": "Beta, yeh sutras se calculator se bhi tez calculate karte the hum log.",
        "state_of_origin": "All India",
        "source_name": "Vedic Mathematics (Swami Bharati Krishna Tirthaji)", "source_url": "https://www.indianculture.gov.in",
    },
    {
        "title": "Jantar Mantar — Ancient Astronomical Observatory",
        "title_sanskrit": "Yantra Mantra (यन्त्र मन्त्र) — Instrument Formula",
        "domain": "Ancient Astronomy", "subdomain": "Observational Astronomy",
        "summary": "Jantar Mantar, built by Maharaja Jai Singh II in Jaipur (1734), is the world's largest stone astronomical observatory. Its 19 architectural instruments can measure time to within 2 seconds accuracy, predict eclipses, track star constellations, and determine the sun's distance — using no electronics, no computers, and no modern technology.",
        "origin_story": "Maharaja Jai Singh II, a scholar-king, studied Ptolemy, Ulugh Beg, and Brahmagupta. Frustrated by the inaccuracy of brass instruments, he built five observatories across India — all in stone, to eliminate thermal expansion errors. The Samrat Yantra (sundial) at Jaipur, 27 meters tall, is accurate to 2 seconds.",
        "how_it_was_forgotten": "Colonial education prioritised European scientific achievements. Indian scientific infrastructure — observatories, manuscripts, mathematical texts — was systematically ignored or destroyed.",
        "modern_relevance": ["Cultural Identity","Mental Performance","Ancient Astronomy"],
        "gen_z_hook": "No satellites. No computers. Stone architecture that tells time to within 2 seconds. India, 1734. 🌌",
        "state_of_origin": "Rajasthan (Jaipur) — also Delhi, Varanasi, Ujjain, Mathura",
        "source_name": "IGNCA + Archaeological Survey of India", "source_url": "https://www.indianculture.gov.in",
    },

    # ═══════════════════════════════════════════════════════════════
    #  SIDDHA MEDICINE  (8 entries)
    # ═══════════════════════════════════════════════════════════════
    {
        "title": "Siddha Medicine — Tamil Heritage of Healing",
        "title_sanskrit": "Siddha Vaidyam (சித்த வைத்தியம்)",
        "domain": "Siddha", "subdomain": "Overview",
        "summary": "Siddha is one of the oldest medical systems in the world, practiced in Tamil Nadu for over 10,000 years according to traditional reckoning. It was developed by the 18 Siddhars — enlightened Tamil saints who combined medicine with yoga, alchemy, and astrology. Unlike Ayurveda which focuses on doshas, Siddha classifies the body through Muppini (three humours) — Vatam, Pittam, and Kapam.",
        "origin_story": "The primordial Siddhar Agattiyar (Agastya) received Siddha knowledge from Lord Shiva at Mount Meru and transmitted it to the 18 Siddhars. The most celebrated — Thirumoolar, Patanjali, Boghar — developed alchemical preparations using metals, minerals, and rare herbs found in South Indian forests.",
        "how_it_was_forgotten": "British colonial medicine classified Siddha as 'primitive' medicine. Medical licensure favored Western medicine exclusively. The written tradition in Tamil manuscripts was systematically undervalued.",
        "modern_relevance": ["Immunity Boosting","Mental Health","Oral Tradition","Cultural Identity"],
        "gen_z_hook": "Tamil medicine is 10,000 years old. It used mercury, sulfur, and minerals 5000 years before Paracelsus. 🌺",
        "state_of_origin": "Tamil Nadu (primarily)",
        "source_name": "AYUSH Ministry + TKDL Siddha Database", "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Kabasura Kudineer — Siddha Respiratory Formula",
        "title_sanskrit": "Kabasura Kudineer (கபசுர குடிநீர்)",
        "domain": "Siddha", "subdomain": "Respiratory Formulations",
        "summary": "Kabasura Kudineer is a classical Siddha decoction using 15 herbs, first described in the 'Siddha Maruthuvam' text. The Tamil Nadu government distributed it during COVID-19 to 30 million people as an approved prophylactic. Clinical trials showed significant reduction in viral load and symptom severity.",
        "ingredients": ["Nilavembu (Kalmegh)", "Seenthil Kodi (Giloy)", "Neem", "Ginger", "Black Pepper", "Dry Ginger", "Long Pepper", "Coriander", "Omam (Ajwain)", "Kottam", "Kostam", "Vattiveru", "Chukku", "Karpooravalli", "Pippili"],
        "remedy_steps": [
            "Boil 5g Kabasura Kudineer churna (powder) in 200ml water",
            "Reduce to 100ml (half) by continuous boiling",
            "Strain and drink warm",
            "Take twice daily before meals",
            "Treatment course: 7-14 days for active infection",
            "Prophylactic: 30ml once daily during peak season",
        ],
        "health_benefits": ["Respiratory","Fever","Immunity","Viral Infections","Inflammation"],
        "scientific_backing": [
            "Clinical trial (2020): Significantly reduced COVID-19 symptoms and duration",
            "Government of Tamil Nadu distributed to 30+ million as official prophylactic",
            "All 15 herbs independently show antiviral, antibacterial, or immunomodulatory activity",
            "AYUSH Ministry included in clinical trial protocols",
        ],
        "dosha_type": "Kapam (Kapha) imbalance", "season_best": "Monsoon, Winter",
        "state_of_origin": "Tamil Nadu",
        "source_name": "Siddha Maruthuvam + Tamil Nadu AYUSH", "source_url": "https://www.tkdl.res.in",
        "modern_relevance": ["Immunity Boosting","Respiratory","Ayush-Approved"],
    },

    # ═══════════════════════════════════════════════════════════════
    #  TRIBAL / INDIGENOUS KNOWLEDGE  (8 entries)
    # ═══════════════════════════════════════════════════════════════
    {
        "title": "Adivasi Forest Medicine — Chhattisgarh",
        "domain": "Tribal Knowledge", "subdomain": "Forest Healing Traditions",
        "summary": "The Adivasi communities of Chhattisgarh have documented over 1200 medicinal plants in their oral tradition. The Baiga, Gond, and Saura tribes use plants unavailable in mainstream pharmacopeias. Their knowledge of forest ecologies and plant combinations represents a unique pharmaceutical resource threatened by deforestation and cultural loss.",
        "oral_story_snippet": "The Baiga vaidya would walk for 3 days into the forest, collecting 40 different plants that only bloom together in August during the monsoon rains. He knew each one by touch, smell, and the way it tasted. This knowledge was not in any book — it was in his hands, his tongue, and the relationship with the forest that had taken 50 years to build.",
        "how_it_was_forgotten": "Forest Rights Act implementation failures have displaced Adivasi communities. Urbanisation of younger generations breaks the knowledge transmission. Mining and deforestation destroy the plants themselves.",
        "modern_relevance": ["Sustainability","Climate Resilience","Cultural Identity","Oral Tradition"],
        "gen_z_hook": "1200 medicinal plants. Zero textbooks. All in human memory. Being lost right now. 🌿",
        "grandmother_quote": "Jungle ki har patti ka naam yaad tha. Ab jungle hi nahi raha.",
        "state_of_origin": "Chhattisgarh, Jharkhand, Odisha (Adivasi belt)",
        "source_name": "IGNCA Tribal Documentation Project", "source_url": "https://www.indianculture.gov.in",
    },
    {
        "title": "Kalari Marma Therapy — Points of Life",
        "title_sanskrit": "Marma Chikitsa (मर्म चिकित्सा)",
        "domain": "Martial Arts", "subdomain": "Kalaripayattu Healing",
        "summary": "Kalaripayattu (Kerala's ancient martial art) has an associated healing system called Kalari Chikitsa which includes Marma therapy — the stimulation of 107 vital energy points on the body. These Marma points (described in Sushruta Samhita) are the predecessors of acupuncture points, predating Chinese acupuncture by centuries.",
        "origin_story": "The Dhanur Veda (Science of Archery and Combat) describes 107 Marma points — strike them in combat to incapacitate or kill; stimulate them in therapy to heal. The Kerala tradition of Kalaripayattu preserves both applications — the combat system and its healing counterpart.",
        "how_it_was_forgotten": "The British banned Kalaripayattu in 1804 as a public safety threat. The prohibition lasted until Independence. 150 years of suppression nearly eliminated both the martial art and its healing tradition.",
        "modern_relevance": ["Mental Health","Fitness & Yoga","Cultural Identity","Pain Relief"],
        "gen_z_hook": "Acupuncture: China, 100 BCE. Marma therapy: India, 600 BCE. The original acupuncture was Indian. 📍",
        "state_of_origin": "Kerala, Tamil Nadu",
        "source_name": "Sushruta Samhita + Dhanur Veda", "source_url": "https://www.tkdl.res.in",
    },

    # ═══════════════════════════════════════════════════════════════
    #  UNANI MEDICINE  (5 entries)
    # ═══════════════════════════════════════════════════════════════
    {
        "title": "Unani — Greco-Persian Medicine in India",
        "domain": "Unani", "subdomain": "Overview",
        "summary": "Unani medicine (Tibb-e-Unani, or 'Greek medicine') was transmitted from Greece through Persia and the Arab world, adopted and dramatically expanded by Indian Hakims over 800 years. The Indian Unani tradition produced unique formulations blending Greco-Arabic concepts with Indian medicinal plants, creating a distinct healing system practiced by 45,000+ practitioners in India today.",
        "origin_story": "Ibn Sina's Canon of Medicine (1025 CE) is the foundational Unani text. When Mughal emperors brought Persian physicians to Delhi, they encountered Indian medicinal plants, developed new combinations, and created a unique Indo-Unani tradition. Hakim Ajmal Khan (1868-1927) documented thousands of Unani formulas and founded the Unani Medical College in Delhi.",
        "how_it_was_forgotten": "Both Hindu nationalism (which favored Ayurveda) and British colonialism (which favored Western medicine) sidelined Unani as 'foreign' — despite it being uniquely Indian for 800 years.",
        "modern_relevance": ["Cultural Identity","Oral Tradition","Immunity Boosting"],
        "gen_z_hook": "Unani has been Indian for 800 years. Mughal emperors, Indian herbs, ancient Greek theory. The most multicultural medicine system. 🏛️",
        "state_of_origin": "Delhi, Uttar Pradesh, Andhra Pradesh (major centres)",
        "source_name": "AYUSH Ministry + Canon of Medicine", "source_url": "https://main.ayush.gov.in",
    },

    # ═══════════════════════════════════════════════════════════════
    #  ARTS & CULTURE  (10 entries)
    # ═══════════════════════════════════════════════════════════════
    {
        "title": "Kalaripayattu — Mother of Martial Arts",
        "domain": "Martial Arts", "subdomain": "Ancient Combat Arts",
        "summary": "Kalaripayattu from Kerala is widely considered the world's oldest martial art, predating kung fu and karate by centuries. Its techniques include high kicks, low sweeps, jumps, weapons training, and the therapeutic Marma system. Bodhidharma, an Indian monk trained in Kalaripayattu, is credited with transmitting the combat forms that became the foundation of Shaolin Kung Fu.",
        "origin_story": "In the Ramayana, the demon king Ravana was himself a master of Kalaripayattu. Parashurama, the sixth avatar of Vishnu, is said to have created the art to protect the newly created land of Kerala. The first written references date to the Sangam literature (~300 BCE).",
        "how_it_was_forgotten": "British colonial ban in 1804 nearly eliminated the art. Only a handful of gurukkal (masters) preserved the tradition in remote Kerala villages. Revival began post-Independence through the efforts of masters like C.V. Narayanan Nair.",
        "modern_relevance": ["Fitness & Yoga","Cultural Identity","Mental Health"],
        "gen_z_hook": "The movie 'Enthiran' and countless Bollywood action sequences trace their fight choreography to Kalaripayattu. The original Indian martial art. 🥋",
        "state_of_origin": "Kerala (Northern and Southern styles), Tamil Nadu",
        "source_name": "IGNCA + Cultural Survival Documentation", "source_url": "https://www.indianculture.gov.in",
    },
    {
        "title": "Bharatanatyam — The Dance of Truth",
        "title_sanskrit": "Bharatanatyam (भरतनाट्यम्)",
        "domain": "Arts & Culture", "subdomain": "Classical Dance",
        "summary": "Bharatanatyam is one of the oldest classical dance forms in the world, originating in Tamil Nadu's temples. 'Bharata' refers to the Natya Shastra of Sage Bharata (200 BCE), 'Na' is natya (dance), 'tya' is gita (music), 'tyam' is vadya (rhythm). Every movement is a medicine for body and mind — recent research shows Bharatanatyam practitioners have higher bone density, flexibility, and lower cortisol levels.",
        "origin_story": "Lord Nataraja (Shiva as the cosmic dancer) is the deity of Bharatanatyam. The Natya Shastra describes 108 karanas (movement units) of Nataraja's cosmic dance — each is a complete yoga posture and expression combined. Devadasis (temple dancers) preserved this art form for millennia in Tamil Nadu temples.",
        "how_it_was_forgotten": "British colonial legislation (Devadasi Abolition Act, 1947) was created to combat exploitation but effectively banned temple dancing, nearly eliminating Bharatanatyam. Rukmini Devi Arundale revived it as a concert dance form in the 1930s.",
        "modern_relevance": ["Fitness & Yoga","Mental Health","Cultural Identity","Arts & Culture"],
        "gen_z_hook": "108 dance postures that are simultaneously yoga, storytelling, and physical therapy. 2000-year-old performance art from temple walls. 💃",
        "state_of_origin": "Tamil Nadu (originally)",
        "source_name": "Natya Shastra + IGNCA", "source_url": "https://www.ignca.gov.in",
    },
    {
        "title": "Ayurvedic Seasonal Routine — Ritucharya",
        "title_sanskrit": "Ritucharya (ऋतुचर्या)",
        "domain": "Ayurveda", "subdomain": "Seasonal Medicine",
        "summary": "Ritucharya is the Ayurvedic seasonal routine — a complete framework for adapting diet, lifestyle, exercise, and herbal support across India's six classical seasons (Ritu). Just as Dinacharya syncs the body with the day, Ritucharya syncs the body with the year. Failure to adapt to seasonal transitions is considered a primary cause of disease in Ayurveda.",
        "origin_story": "The Ashtanga Hridayam dedicates an entire chapter to Ritucharya, describing in detail how each organ system is stressed differently in each season, and how food, herbs, and routines should shift to maintain balance.",
        "remedy_steps": [
            "Shishira (Jan-Feb, late winter): Warming foods — til, ghee, wheat, new jaggery. Vigorous exercise. Hot water bathing.",
            "Vasanta (Mar-Apr, spring): Detox season — light foods, bitter greens, Triphala, avoid oily heavy foods. Vaman (emesis therapy) classically recommended.",
            "Grishma (May-Jun, summer): Cooling foods — coconut water, buttermilk, cucumber, rice, avoid chilli. Reduce exercise intensity. Cold water bathing.",
            "Varsha (Jul-Aug, monsoon): Digestive fire lowest — light soups, moong dal, ginger. Avoid raw vegetables and leafy greens. Consume garlic, rock salt.",
            "Sharad (Sep-Oct, autumn): Purification season — Virechan (purgation). Light, dry, bitter, astringent foods. Moon-charged water (leave water in silver vessel overnight).",
            "Hemanta (Nov-Dec, early winter): Nourishing season — dairy, sesame, warm oils. Abhyanga daily. Rasayana herbs — ashwagandha, chyawanprash.",
        ],
        "health_benefits": ["Seasonal Immunity","Digestion","Energy","Prevention","Balance"],
        "scientific_backing": [
            "Chronobiology confirms seasonal shifts in metabolism, immune function, and hormones",
            "Vitamin D synthesis lowest in winter (Shishira) — Ayurvedic warming protocols address deficiency consequences",
            "Monsoon season pathogen increase confirmed — Ayurvedic digestive support is evidence-aligned",
        ],
        "dosha_type": "All doshas (seasonal adjustments)", "season_best": "Applied across all seasons",
        "modern_relevance": ["Immunity Boosting","Mental Health","Gut Health","Longevity"],
        "gen_z_hook": "Your body is not the same in summer and winter. Ayurveda built a complete protocol for this 3000 years ago. 📅",
        "state_of_origin": "All India",
        "source_name": "Ashtanga Hridayam + Charaka Samhita", "source_url": "https://www.tkdl.res.in",
    },
    {
        "title": "Abhyanga — Sacred Self-Massage",
        "title_sanskrit": "Abhyanga (अभ्यंग)",
        "domain": "Ayurveda", "subdomain": "Dinacharya (Daily Practices)",
        "summary": "Abhyanga is the daily self-massage with warm oil, a cornerstone of Ayurvedic dinacharya. Charaka writes: 'Abhyanga prevents aging, relieves fatigue, improves eyesight, nourishes the skin, and calms Vata.' Modern research confirms it reduces cortisol by 31%, improves lymphatic flow, and increases oxytocin and serotonin.",
        "ingredients": ["Sesame Oil (Vata)", "Coconut Oil (Pitta)", "Mustard Oil (Kapha)"],
        "remedy_steps": [
            "Choose oil based on dosha: sesame for Vata, coconut for Pitta, mustard for Kapha",
            "Warm oil to comfortable temperature (test on inner wrist)",
            "Begin at scalp — circular motions, fingertips pressing gently",
            "Move to ears, neck, shoulders with gentle circular strokes",
            "Chest and abdomen: clockwise circles (following direction of digestion)",
            "Arms and legs: long strokes from joint to joint, circles at joints (wrists, elbows, knees, ankles)",
            "Feet: thorough massage including soles and between toes",
            "Rest for 15-20 minutes allowing oil to absorb",
            "Shower with warm water, minimal soap to preserve oil benefits",
        ],
        "health_benefits": ["Skin","Sleep","Stress","Joint Pain","Immunity","Circulation","Anti-aging"],
        "mental_benefits": ["Stress","Anxiety","Depression","Oxytocin Release"],
        "scientific_backing": [
            "Reduces salivary cortisol by 31% comparable to Swedish massage",
            "Increases oxytocin (bonding hormone) by 45% in self-massage studies",
            "Sesame oil lignans (sesamin, sesamolin): Antioxidant and anti-inflammatory",
            "Lymphatic drainage: Manual pressure increases lymph flow rate by 10-20x",
        ],
        "dosha_type": "Vata (primary), all doshas with appropriate oil", "season_best": "All seasons",
        "time_of_day": "Morning before shower",
        "duration": "15-30 minutes",
        "modern_relevance": ["Skincare","Sleep Wellness","Mental Health","Fitness & Yoga","Longevity"],
        "gen_z_hook": "Luxury spa Abhyanga massage: ₹5000/hour. DIY at home with ₹30 of sesame oil: same science. 🫒",
        "challenge_idea": "30-day Abhyanga Challenge: 10 min self-massage before shower every day",
        "grandmother_quote": "Tel malish karo. Aaj mein taqat hai agar roz malish ho.",
        "state_of_origin": "All India (especially South India — sesame oil tradition)",
        "source_name": "Charaka Samhita + Ashtanga Hridayam", "source_url": "https://www.tkdl.res.in",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
#  WIKIPEDIA TOPICS  (80+ for bulk data collection)
# ─────────────────────────────────────────────────────────────────────────────
WIKIPEDIA_TOPICS = [
    # Herbs
    ("Ayurveda",                     "Ayurveda",           "Overview"),
    ("Dosha",                        "Ayurveda",           "Tridosha"),
    ("Withania somnifera",           "Ayurveda",           "Ashwagandha"),
    ("Ocimum tenuiflorum",           "Ayurveda",           "Tulsi"),
    ("Turmeric",                     "Ayurveda",           "Haldi"),
    ("Azadirachta indica",           "Ayurveda",           "Neem"),
    ("Triphala",                     "Ayurveda",           "Classical Formula"),
    ("Phyllanthus emblica",          "Ayurveda",           "Amla"),
    ("Tinospora cordifolia",         "Ayurveda",           "Giloy"),
    ("Bacopa monnieri",              "Ayurveda",           "Brahmi"),
    ("Zingiber officinale",          "Home Remedies",      "Ginger"),
    ("Curcumin",                     "Ayurveda",           "Active Compounds"),
    ("Moringa oleifera",             "Ayurveda",           "Moringa"),
    ("Asparagus racemosus",          "Ayurveda",           "Shatavari"),
    ("Shilajit",                     "Ayurveda",           "Mineral Medicine"),
    ("Centella asiatica",            "Ayurveda",           "Gotu Kola"),
    ("Nigella sativa",               "Home Remedies",      "Black Seed"),
    ("Aloe vera",                    "Home Remedies",      "Aloe"),
    ("Glycyrrhiza glabra",           "Ayurveda",           "Licorice / Mulethi"),
    ("Andrographis paniculata",      "Ayurveda",           "Kalmegh"),
    ("Terminalia chebula",           "Ayurveda",           "Haritaki"),
    ("Emblica officinalis",          "Ayurveda",           "Amla (alt)"),
    ("Commiphora mukul",             "Ayurveda",           "Guggul"),
    ("Tribulus terrestris",          "Ayurveda",           "Gokshura"),
    ("Mucuna pruriens",              "Ayurveda",           "Kapikachhu"),
    ("Boswellia serrata",            "Ayurveda",           "Shallaki"),
    ("Cinnamomum verum",             "Home Remedies",      "Cinnamon"),
    ("Elettaria cardamomum",         "Food & Culture",     "Cardamom"),
    ("Syzygium aromaticum",          "Home Remedies",      "Clove"),
    ("Piper nigrum",                 "Home Remedies",      "Black Pepper"),
    # Yoga
    ("Yoga",                         "Yoga",               "Overview"),
    ("Pranayama",                    "Yoga",               "Breathing Techniques"),
    ("Surya Namaskar",               "Yoga",               "Sequences"),
    ("Hatha yoga",                   "Yoga",               "Physical Yoga"),
    ("Kundalini yoga",               "Yoga",               "Energy Yoga"),
    ("Ashtanga vinyasa yoga",        "Yoga",               "Dynamic Yoga"),
    ("Chakra",                       "Yoga",               "Energy Centers"),
    ("Mudra",                        "Yoga",               "Hand Gestures"),
    ("Meditation",                   "Yoga",               "Dhyana"),
    ("Vipassanā",                    "Yoga",               "Meditation Techniques"),
    ("Yoga Nidra",                   "Yoga",               "Yogic Sleep"),
    ("Panchakarma",                  "Ayurveda",           "Detox Therapies"),
    ("Dinacharya",                   "Ayurveda",           "Daily Routine"),
    ("Rasayana (Ayurveda)",          "Ayurveda",           "Rejuvenation"),
    # Systems
    ("Charaka Samhita",              "Ancient Texts",      "Classical Text"),
    ("Sushruta Samhita",             "Ancient Texts",      "Classical Text"),
    ("Ashtanga Hridayam",            "Ancient Texts",      "Classical Text"),
    ("Siddha medicine",              "Siddha",             "Overview"),
    ("Unani medicine",               "Unani",              "Overview"),
    ("Naturopathy",                  "Naturopathy",        "Overview"),
    # Food
    ("Indian cuisine",               "Food & Culture",     "Overview"),
    ("Ghee",                         "Food & Culture",     "Sacred Foods"),
    ("Sattvic diet",                 "Food & Culture",     "Ayurvedic Diet"),
    ("Fermentation in food processing", "Food & Culture", "Fermentation"),
    ("Spice",                        "Food & Culture",     "Spice Knowledge"),
    ("Fasting",                      "Food & Culture",     "Ritualistic Practices"),
    ("Khichdi",                      "Food & Culture",     "Healing Food"),
    ("Kadha (herbal drink)",         "Home Remedies",      "Decoction"),
    ("Chyawanprash",                 "Ayurveda",           "Classical Formula"),
    # Farming
    ("Zero Budget Natural Farming",  "Sustainable Farming","Modern Methods"),
    ("Organic farming",              "Sustainable Farming","Overview"),
    ("Biodynamic agriculture",       "Sustainable Farming","Holistic Farming"),
    ("Crop rotation",                "Sustainable Farming","Soil Health"),
    ("Permaculture",                 "Sustainable Farming","Design Principles"),
    # Science / Maths
    ("Indian mathematics",           "Vedic Mathematics",  "Overview"),
    ("Aryabhata",                    "Ancient Astronomy",  "Aryabhata"),
    ("Brahmagupta",                  "Vedic Mathematics",  "Brahmagupta"),
    ("0 (number)",                   "Vedic Mathematics",  "Zero"),
    ("Vedic Mathematics",            "Vedic Mathematics",  "Sutras"),
    ("Hindu astrology",              "Ancient Astronomy",  "Jyotisha"),
    ("Indian astronomy",             "Ancient Astronomy",  "Overview"),
    # Culture
    ("Folklore of India",            "Oral History",       "Folk Stories"),
    ("Oral tradition",               "Oral History",       "Storytelling"),
    ("Bharatanatyam",                "Arts & Culture",     "Classical Dance"),
    ("Kalaripayattu",                "Martial Arts",       "Ancient Combat"),
    ("Rangoli",                      "Arts & Culture",     "Folk Arts"),
    ("Carnatic music",               "Arts & Culture",     "Music Tradition"),
    ("Kolam",                        "Arts & Culture",     "Living Geometry"),
    ("Panchang",                     "Oral History",       "Calendar System"),
    ("Vastu shastra",                "Architecture",       "Sacred Architecture"),
    ("Panchatantra",                 "Oral History",       "Wisdom Literature"),
    ("Indian folk art",              "Arts & Culture",     "Visual Traditions"),
    ("Warli painting",               "Arts & Culture",     "Tribal Art"),
    ("Madhubani painting",           "Arts & Culture",     "Folk Painting"),
    ("Pashmina",                     "Textile & Craft",    "Textile Heritage"),
]

# ─────────────────────────────────────────────────────────────────────────────
#  SCRAPERS
# ─────────────────────────────────────────────────────────────────────────────
def scrape_wikipedia(page_title, domain, subdomain):
    api = "https://en.wikipedia.org/w/api.php"
    params = {"action": "query", "format": "json", "titles": page_title,
              "prop": "extracts", "explaintext": True, "exsectionformat": "plain"}
    headers = {"User-Agent": "DadiKiBaatein/2.0 Hackathon (https://github.com) bot@example.com"}
    try:
        r = requests.get(api, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        for pid, page in pages.items():
            if pid == "-1":
                return None
            content = clean(page.get("extract", ""))
            if len(content) < 200:
                return None
            return build_entry(
                title=page.get("title", page_title),
                content=content, source_url=f"https://en.wikipedia.org/wiki/{page_title.replace(' ','_')}",
                source_name=f"Wikipedia — {page_title}",
                default_domain=domain, subdomain=subdomain, src_type="wikipedia")
    except Exception as e:
        log.warning(f"Wiki fail: {page_title} — {e}")
    return None

JS_SITES = [
    {"name": "Indian Cultural Portal - Ayurveda",   "url": "https://www.indianculture.gov.in/ayurveda",   "domain": "Ayurveda"},
    {"name": "Indian Cultural Portal - Yoga",        "url": "https://www.indianculture.gov.in/yoga",        "domain": "Yoga"},
    {"name": "Indian Cultural Portal - KS",          "url": "https://www.indianculture.gov.in/indian-knowledge-systems", "domain": "Traditional Knowledge"},
    {"name": "Indian Cultural Portal - Manuscripts", "url": "https://www.indianculture.gov.in/manuscripts", "domain": "Ancient Texts"},
    {"name": "AYUSH Ministry - Ayurveda",            "url": "https://main.ayush.gov.in/ayurveda",           "domain": "Ayurveda"},
    {"name": "AYUSH Ministry - Yoga",                "url": "https://main.ayush.gov.in/yoga-naturopathy",   "domain": "Yoga"},
    {"name": "AYUSH Ministry - Siddha",              "url": "https://main.ayush.gov.in/siddha",             "domain": "Siddha"},
    {"name": "AYUSH Ministry - Unani",               "url": "https://main.ayush.gov.in/unani",              "domain": "Unani"},
    {"name": "Yoga Institute Mumbai",                "url": "https://theyogainstitute.org/yoga-benefits/",  "domain": "Yoga"},
    {"name": "Morarji Desai Yoga",                   "url": "https://www.yogamdniy.nic.in/",                "domain": "Yoga"},
]

def get_driver():
    if not SELENIUM_OK: return None
    try:
        opts = Options()
        opts.add_argument("--headless"); opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage"); opts.add_argument("--disable-gpu")
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        return webdriver.Chrome(options=opts)
    except Exception as e:
        log.error(f"ChromeDriver not available: {e}")
        return None

def scrape_selenium(driver, site):
    try:
        driver.get(site["url"]); time.sleep(4)
        soup = BeautifulSoup(driver.page_source, "lxml") if BS4_OK else None
        if not soup: return None
        for sel in ["article","main",".field-items",".node__content",".view-content","#content"]:
            el = soup.select_one(sel)
            if el:
                paras = el.find_all(["p","li","h2","h3","h4"])
                content = " ".join(clean(p.get_text()) for p in paras if len(p.get_text())>30)
                if len(content) > 200:
                    h1 = soup.select_one("h1,h2,.page-title")
                    title = clean(h1.get_text()) if h1 else site["name"]
                    return build_entry(title=title, content=content, source_url=site["url"],
                                       source_name=site["name"], default_domain=site["domain"],
                                       subdomain="", src_type="selenium")
    except Exception as e:
        log.error(f"Selenium error {site['url']}: {e}")
    return None

# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY BUILDER
# ─────────────────────────────────────────────────────────────────────────────
def build_entry(title, content, source_url, source_name,
                default_domain, subdomain, src_type) -> KnowledgeEntry:
    domain = classify(content, default_domain)
    sents  = re.split(r"(?<=[.!?])\s+", content)
    summary = " ".join(s for s in sents if len(s)>40)[:600]
    e = KnowledgeEntry(
        id=make_id(source_url, title),
        title=title, domain=domain, subdomain=subdomain,
        dadi_story=dadi_story(title, summary, domain),
        summary=summary, raw_content=content[:4000],
        scientific_backing=get_science(content),
        health_benefits=get_health(content),
        mental_benefits=get_mental(content),
        ingredients=get_ingr(content),
        remedy_steps=[],
        yoga_poses=get_yoga(content),
        seasonal_relevance=get_season(content),
        dosha_type=get_dosha(content),
        modern_relevance=get_modern(content),
        keywords=kw(content),
        contraindications=get_contraindications(content),
        source_url=source_url, source_name=source_name,
        scraped_at=datetime.now().isoformat(),
        gen_z_hook=GEN_Z_HOOKS.get(domain,"Ancient wisdom for modern lives. 🙏"),
        tiktok_angle=TIKTOK_ANGLES.get(domain,""),
        data_source_type=src_type,
    )
    e.tags = auto_tag(e)
    e.authenticity_score = score_authenticity(e)
    return e

def build_from_seed(item) -> KnowledgeEntry:
    content = " ".join([
        item.get("summary",""),
        " ".join(item.get("remedy_steps",[])),
        " ".join(item.get("scientific_backing",[])),
    ])
    e = KnowledgeEntry(
        id=make_id(item.get("source_url","seed"), item["title"]),
        title=item["title"],
        title_sanskrit=item.get("title_sanskrit",""),
        domain=item["domain"],
        subdomain=item.get("subdomain",""),
        dadi_story=dadi_story(item["title"], item.get("summary",""), item["domain"]),
        summary=item.get("summary",""),
        raw_content=content,
        origin_story=item.get("origin_story",""),
        how_it_was_forgotten=item.get("how_it_was_forgotten",""),
        dosha_type=item.get("dosha_type",""),
        season_best=item.get("season_best",""),
        time_of_day=item.get("time_of_day",""),
        body_system=item.get("body_system",[]),
        age_group=item.get("age_group",[]),
        gender_notes=item.get("gender_notes",""),
        ingredients=item.get("ingredients",[]),
        ingredient_quantities=item.get("ingredient_quantities",{}),
        remedy_steps=item.get("remedy_steps",[]),
        duration=item.get("duration",""),
        dosage=item.get("dosage",""),
        preparation_time=item.get("preparation_time",""),
        yoga_poses=item.get("yoga_poses",[]),
        breathing_type=item.get("breathing_type",""),
        difficulty_level=item.get("difficulty_level",""),
        contraindications=item.get("contraindications",[]),
        side_effects=item.get("side_effects",[]),
        drug_interactions=item.get("drug_interactions",[]),
        warnings=item.get("warnings",[]),
        scientific_backing=item.get("scientific_backing",[]),
        active_compounds=item.get("active_compounds",[]),
        research_status=item.get("research_status",""),
        pubmed_keywords=item.get("pubmed_keywords",[]),
        health_benefits=item.get("health_benefits",[]),
        mental_benefits=item.get("mental_benefits",[]),
        spiritual_benefits=item.get("spiritual_benefits",[]),
        regional_variant=item.get("regional_variant",""),
        state_of_origin=item.get("state_of_origin",""),
        language_origin=item.get("language_origin","Sanskrit"),
        related_festival=item.get("related_festival",""),
        oral_story_snippet=item.get("oral_story_snippet",""),
        grandmother_quote=item.get("grandmother_quote",""),
        modern_relevance=item.get("modern_relevance",[]),
        gen_z_hook=item.get("gen_z_hook",GEN_Z_HOOKS.get(item["domain"],"")),
        tiktok_angle=item.get("tiktok_angle",TIKTOK_ANGLES.get(item["domain"],"")),
        challenge_idea=item.get("challenge_idea",""),
        daily_habit_tip=item.get("daily_habit_tip",""),
        difficulty_to_adopt=item.get("difficulty_to_adopt",""),
        keywords=item.get("keywords", kw(content)),
        source_url=item.get("source_url",""),
        source_name=item.get("source_name",""),
        scraped_at=datetime.now().isoformat(),
        data_source_type="seed",
        verified=True,
        last_updated=datetime.now().isoformat(),
    )
    e.tags = auto_tag(e)
    e.seasonal_relevance = e.season_best
    e.authenticity_score = score_authenticity(e)
    return e

# ─────────────────────────────────────────────────────────────────────────────
#  EXPORT FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def save_json_full(entries, filename="knowledge_base_full.json"):
    path = BASE/"json"/filename
    with open(path,"w",encoding="utf-8") as f:
        json.dump([asdict(e) for e in entries], f, indent=2, ensure_ascii=False)
    log.info(f"  JSON full → {path} ({len(entries)} entries)")

def save_chatbot_rag(entries):
    records = [{
        "id": e.id, "title": e.title, "title_sanskrit": e.title_sanskrit,
        "domain": e.domain, "subdomain": e.subdomain, "tags": e.tags,
        "dadi_story": e.dadi_story, "summary": e.summary,
        "origin_story": e.origin_story,
        "health_benefits": e.health_benefits, "mental_benefits": e.mental_benefits,
        "ingredients": e.ingredients, "ingredient_quantities": e.ingredient_quantities,
        "remedy_steps": e.remedy_steps, "yoga_poses": e.yoga_poses,
        "active_compounds": e.active_compounds,
        "scientific_backing": e.scientific_backing,
        "contraindications": e.contraindications, "warnings": e.warnings,
        "modern_relevance": e.modern_relevance,
        "gen_z_hook": e.gen_z_hook, "tiktok_angle": e.tiktok_angle,
        "challenge_idea": e.challenge_idea, "daily_habit_tip": e.daily_habit_tip,
        "grandmother_quote": e.grandmother_quote,
        "dosha_type": e.dosha_type, "seasonal_relevance": e.seasonal_relevance,
        "state_of_origin": e.state_of_origin, "related_festival": e.related_festival,
        "keywords": e.keywords, "authenticity_score": e.authenticity_score,
        "source": e.source_url, "data_source_type": e.data_source_type,
    } for e in entries]
    path = BASE/"json"/"chatbot_knowledge_base.json"
    with open(path,"w",encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    log.info(f"  Chatbot RAG JSON → {path}")

def save_domain_files(entries):
    dm = {}
    for e in entries:
        dm.setdefault(e.domain, []).append(asdict(e))
    for d, items in dm.items():
        safe = re.sub(r"[^\w]","_",d).lower()
        path = BASE/"domain_files"/f"{safe}.json"
        with open(path,"w",encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
    log.info(f"  Domain files → {BASE}/domain_files/ ({len(dm)} domains)")

def save_csv(entries):
    path = BASE/"csv"/"knowledge_base.csv"
    flat_fields = ["id","title","title_sanskrit","domain","subdomain","summary","dosha_type",
                   "seasonal_relevance","state_of_origin","gen_z_hook","authenticity_score","source_url"]
    with open(path,"w",newline="",encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=flat_fields + ["tags","health_benefits","ingredients","keywords"])
        w.writeheader()
        for e in entries:
            row = {field: getattr(e, field, "") for field in flat_fields}
            row["tags"] = "|".join(e.tags)
            row["health_benefits"] = "|".join(e.health_benefits)
            row["ingredients"] = "|".join(e.ingredients)
            row["keywords"] = "|".join(e.keywords[:10])
            w.writerow(row)
    log.info(f"  CSV → {path}")

def save_sqlite(entries):
    path = BASE/"sqlite"/"knowledge_base.db"
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS knowledge (
        id TEXT PRIMARY KEY, title TEXT, title_sanskrit TEXT,
        domain TEXT, subdomain TEXT, tags TEXT, summary TEXT,
        dadi_story TEXT, origin_story TEXT, gen_z_hook TEXT,
        dosha_type TEXT, season TEXT, state TEXT,
        health_benefits TEXT, ingredients TEXT, active_compounds TEXT,
        scientific_backing TEXT, contraindications TEXT,
        authenticity_score REAL, source_url TEXT,
        data_source_type TEXT, scraped_at TEXT
    )""")
    for e in entries:
        c.execute("""INSERT OR REPLACE INTO knowledge VALUES
            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
            e.id, e.title, e.title_sanskrit,
            e.domain, e.subdomain, "|".join(e.tags), e.summary,
            e.dadi_story, e.origin_story, e.gen_z_hook,
            e.dosha_type, e.seasonal_relevance, e.state_of_origin,
            "|".join(e.health_benefits), "|".join(e.ingredients),
            "|".join(e.active_compounds), "|".join(e.scientific_backing),
            "|".join(e.contraindications), e.authenticity_score,
            e.source_url, e.data_source_type, e.scraped_at,
        ))
    conn.commit(); conn.close()
    log.info(f"  SQLite DB → {path}")

def save_jsonl_finetune(entries):
    """JSONL for LLM fine-tuning — one conversation per entry."""
    path = BASE/"jsonl"/"finetune_conversations.jsonl"
    with open(path,"w",encoding="utf-8") as f:
        for e in entries:
            if not e.summary: continue
            # Q&A pairs for fine-tuning Dadi persona
            pairs = []
            if e.summary:
                pairs.append({
                    "messages": [
                        {"role": "user", "content": f"Tell me about {e.title}"},
                        {"role": "assistant", "content": e.dadi_story}
                    ]
                })
            if e.remedy_steps:
                steps_text = "\n".join(f"{i+1}. {s}" for i,s in enumerate(e.remedy_steps))
                pairs.append({
                    "messages": [
                        {"role": "user", "content": f"How do I use {e.title}? What are the steps?"},
                        {"role": "assistant", "content": f"Aa, sun baith ke. Yeh hai {e.title} ka sahi tarika:\n\n{steps_text}\n\nYaad rakh — {e.gen_z_hook}"}
                    ]
                })
            if e.health_benefits:
                pairs.append({
                    "messages": [
                        {"role": "user", "content": f"What are the health benefits of {e.title}?"},
                        {"role": "assistant", "content": f"Beta, {e.title} ke faayde suno: {', '.join(e.health_benefits[:5])}. Aur science bhi kehti hai — {e.scientific_backing[0] if e.scientific_backing else 'hazaaron saal ka anubhav hai'}."}
                    ]
                })
            if e.contraindications:
                pairs.append({
                    "messages": [
                        {"role": "user", "content": f"Is {e.title} safe? Any warnings?"},
                        {"role": "assistant", "content": f"Suno dhyan se — {e.title} zyaadatar log ke liye safe hai. Lekin yeh baat yaad raho: {'. '.join(e.contraindications)}"}
                    ]
                })
            for p in pairs:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")
    log.info(f"  JSONL fine-tune → {path}")

def save_rasa_training(entries):
    """Generate Rasa NLU training data for intent classification."""
    path = BASE/"training_data"/"rasa_nlu.yml"
    domain_intents = {}
    for e in entries:
        intent = re.sub(r"[^\w]","_",e.domain).lower()
        domain_intents.setdefault(intent, [])
        if e.title: domain_intents[intent].append(f"tell me about {e.title.lower()}")
        if e.keywords: domain_intents[intent].extend([f"what is {k}" for k in e.keywords[:3]])
    lines = ["version: '3.1'", "nlu:"]
    for intent, examples in domain_intents.items():
        lines.append(f"- intent: ask_{intent}")
        lines.append("  examples: |")
        for ex in list(set(examples))[:15]:
            lines.append(f"    - {ex}")
    with open(path,"w",encoding="utf-8") as f:
        f.write("\n".join(lines))
    log.info(f"  Rasa NLU training data → {path}")

def save_markdown_cards(entries):
    """One Markdown file per entry — for Obsidian/Notion import."""
    md_dir = BASE/"markdown"
    for e in entries:
        safe_title = re.sub(r"[^\w\s-]","", e.title)[:50].strip().replace(" ","_")
        path = md_dir/f"{safe_title}.md"
        lines = [
            f"# {e.title}", "",
            f"**Sanskrit/Hindi Name:** {e.title_sanskrit}" if e.title_sanskrit else "",
            f"**Domain:** {e.domain} > {e.subdomain}",
            f"**Tags:** {', '.join(['#'+t for t in e.tags])}",
            f"**Dosha:** {e.dosha_type}" if e.dosha_type else "",
            f"**Season:** {e.seasonal_relevance}" if e.seasonal_relevance else "",
            f"**State of Origin:** {e.state_of_origin}" if e.state_of_origin else "",
            "", "---", "", "## 🧓 Dadi's Story", "",
            e.dadi_story, "",
        ]
        if e.summary:
            lines += ["## 📖 Summary", "", e.summary, ""]
        if e.origin_story:
            lines += ["## 🌺 Origin Story", "", e.origin_story, ""]
        if e.ingredients:
            lines += ["## 🌿 Ingredients", ""]
            for ing, qty in (e.ingredient_quantities or {}).items():
                lines.append(f"- {ing}: {qty}")
            remaining = [i for i in e.ingredients if i not in (e.ingredient_quantities or {})]
            for r in remaining: lines.append(f"- {r}")
            lines.append("")
        if e.remedy_steps:
            lines += ["## 📋 How to Use", ""]
            for i, step in enumerate(e.remedy_steps, 1):
                lines.append(f"{i}. {step}")
            lines.append("")
        if e.health_benefits:
            lines += ["## 💚 Health Benefits", "", ", ".join(e.health_benefits), ""]
        if e.active_compounds:
            lines += ["## 🔬 Active Compounds", ""]
            for a in e.active_compounds: lines.append(f"- {a}")
            lines.append("")
        if e.scientific_backing:
            lines += ["## 🧬 Scientific Backing", ""]
            for s in e.scientific_backing: lines.append(f"- {s}")
            lines.append("")
        if e.contraindications:
            lines += ["## ⚠️ Contraindications & Safety", ""]
            for c in e.contraindications: lines.append(f"- ⚠️ {c}")
            lines.append("")
        if e.gen_z_hook:
            lines += ["## 🔥 Gen-Z Hook", "", f"> {e.gen_z_hook}", ""]
        if e.grandmother_quote:
            lines += ["## 💬 Dadi's Words", "", f"> *\"{e.grandmother_quote}\"*", ""]
        if e.challenge_idea:
            lines += ["## 🎮 Gamification Challenge", "", e.challenge_idea, ""]
        lines += ["---", f"**Source:** [{e.source_name}]({e.source_url})",
                  f"**Authenticity Score:** {e.authenticity_score}/1.0",
                  f"**Data Source:** {e.data_source_type}",
                  f"**Scraped:** {e.scraped_at}"]
        with open(path,"w",encoding="utf-8") as f:
            f.write("\n".join(l for l in lines if l is not None))
    log.info(f"  Markdown cards → {md_dir}/ ({len(entries)} files)")

def save_prompt_ready(entries):
    """Plain text format for direct RAG context injection."""
    path = BASE/"chatbot_system_prompt_seed.txt"
    blocks = []
    for e in entries:
        parts = [f"ENTRY_ID: {e.id}",
                 f"TITLE: {e.title}{' (' + e.title_sanskrit + ')' if e.title_sanskrit else ''}",
                 f"DOMAIN: {e.domain} | SUBDOMAIN: {e.subdomain}",
                 f"TAGS: {', '.join(e.tags)}"]
        if e.summary:      parts.append(f"SUMMARY: {e.summary}")
        if e.origin_story: parts.append(f"ORIGIN: {e.origin_story[:300]}")
        if e.ingredients:
            qtys = e.ingredient_quantities or {}
            ing_str = ", ".join(f"{i}({qtys[i]})" if i in qtys else i for i in e.ingredients)
            parts.append(f"INGREDIENTS: {ing_str}")
        if e.remedy_steps:
            parts.append("STEPS:\n" + "\n".join(f"  {i+1}. {s}" for i,s in enumerate(e.remedy_steps)))
        if e.health_benefits:    parts.append(f"HEALTH: {', '.join(e.health_benefits)}")
        if e.active_compounds:   parts.append(f"COMPOUNDS: {', '.join(e.active_compounds)}")
        if e.scientific_backing: parts.append(f"SCIENCE: {'; '.join(e.scientific_backing[:3])}")
        if e.contraindications:  parts.append(f"CAUTION: {'; '.join(e.contraindications)}")
        if e.dosha_type:         parts.append(f"DOSHA: {e.dosha_type}")
        if e.gen_z_hook:         parts.append(f"GEN_Z: {e.gen_z_hook}")
        if e.grandmother_quote:  parts.append(f"DADI_QUOTE: {e.grandmother_quote}")
        parts.append(f"AUTHENTICITY: {e.authenticity_score}")
        blocks.append("\n".join(parts))
    with open(path,"w",encoding="utf-8") as f:
        f.write("\n\n─────────────────────\n\n".join(blocks))
    log.info(f"  Prompt-ready text → {path}")

def save_embeddings_prep(entries):
    """JSON optimised for embedding into vector DB (ChromaDB/Pinecone)."""
    records = []
    for e in entries:
        # Create one text document per entry for embedding
        doc_text = " ".join(filter(None, [
            e.title, e.title_sanskrit, e.summary,
            " ".join(e.health_benefits), " ".join(e.ingredients),
            " ".join(e.tags), e.dosha_type, e.gen_z_hook,
        ]))
        records.append({
            "id": e.id,
            "document": doc_text,
            "metadata": {
                "title": e.title,
                "domain": e.domain,
                "subdomain": e.subdomain,
                "tags": e.tags,
                "dosha": e.dosha_type,
                "season": e.seasonal_relevance,
                "state": e.state_of_origin,
                "verified": e.verified,
                "score": e.authenticity_score,
                "source_type": e.data_source_type,
            }
        })
    path = BASE/"embeddings"/"chromadb_ready.json"
    with open(path,"w",encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    log.info(f"  ChromaDB-ready → {path}")

# ─────────────────────────────────────────────────────────────────────────────
#  STATS REPORTER
# ─────────────────────────────────────────────────────────────────────────────
def stats(entries):
    print("\n" + "═"*65)
    print("  📚  DADI KI BAATEIN — MEGA Knowledge Base Stats")
    print("═"*65)
    print(f"  Total entries          : {len(entries)}")

    dm = {}
    for e in entries: dm[e.domain] = dm.get(e.domain, 0) + 1
    print("\n  By Domain:")
    for d,c in sorted(dm.items(), key=lambda x:-x[1]):
        print(f"    {d:<35} {c:>3}  {'█'*c}")

    sm = {}
    for e in entries: sm[e.data_source_type] = sm.get(e.data_source_type, 0) + 1
    print("\n  By Source Type:")
    for t,c in sorted(sm.items(), key=lambda x:-x[1]):
        print(f"    {t:<20} {c:>3}")

    avg = sum(e.authenticity_score for e in entries) / max(len(entries),1)
    print(f"\n  Avg authenticity score : {avg:.2f} / 1.00")
    print(f"  With remedy steps      : {sum(1 for e in entries if e.remedy_steps)}")
    print(f"  With ingredients       : {sum(1 for e in entries if e.ingredients)}")
    print(f"  With science backing   : {sum(1 for e in entries if e.scientific_backing)}")
    print(f"  With active compounds  : {sum(1 for e in entries if e.active_compounds)}")
    print(f"  With contraindications : {sum(1 for e in entries if e.contraindications)}")
    print(f"  With yoga poses        : {sum(1 for e in entries if e.yoga_poses)}")
    print(f"  With origin stories    : {sum(1 for e in entries if e.origin_story)}")
    print(f"  With gen-Z hooks       : {sum(1 for e in entries if e.gen_z_hook)}")
    print(f"  With challenges        : {sum(1 for e in entries if e.challenge_idea)}")
    print(f"  Total tags used        : {len(set(t for e in entries for t in e.tags))}")
    print("═"*65 + "\n")

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Dadi Ki Baatein MEGA Scraper")
    ap.add_argument("--seed-only",    action="store_true")
    ap.add_argument("--no-selenium",  action="store_true")
    ap.add_argument("--no-wikipedia", action="store_true")
    args = ap.parse_args()

    all_entries = []
    seen = set()

    def add(e):
        if e and e.id not in seen:
            seen.add(e.id); all_entries.append(e)

    # ── Phase 1: Curated Seed Data ──────────────────────────────────
    print("\n🌿  Phase 1: Loading Curated Seed Knowledge Base")
    seeds = [build_from_seed(s) for s in SEED_KNOWLEDGE]
    for e in seeds: add(e)
    print(f"  ✅  {len(seeds)} seed entries loaded")

    if args.seed_only:
        pass
    else:
        # ── Phase 2: Wikipedia API ────────────────────────────────────
        if not args.no_wikipedia:
            print(f"\n🌿  Phase 2: Wikipedia API ({len(WIKIPEDIA_TOPICS)} topics)")
            for title, domain, sub in tqdm(WIKIPEDIA_TOPICS, desc="Wikipedia"):
                add(scrape_wikipedia(title, domain, sub))
                time.sleep(0.6)
            print(f"  ✅  Wikipedia phase done. Total: {len(all_entries)} entries")

        # ── Phase 3: Selenium for JS Sites ───────────────────────────
        if not args.no_selenium:
            if not SELENIUM_OK:
                print("  ⚠️  selenium not installed (pip install selenium)")
            elif not BS4_OK:
                print("  ⚠️  beautifulsoup4 not installed (pip install beautifulsoup4 lxml)")
            else:
                print(f"\n🌿  Phase 3: JS-Rendered Government Sites ({len(JS_SITES)} sites)")
                driver = get_driver()
                if driver:
                    try:
                        for site in tqdm(JS_SITES, desc="JS Sites"):
                            add(scrape_selenium(driver, site))
                            time.sleep(2)
                    finally:
                        driver.quit()
                    print(f"  ✅  Selenium phase done. Total: {len(all_entries)} entries")
                else:
                    print("  ⚠️  ChromeDriver not found. Get it: https://chromedriver.chromium.org")

    # ── Save All Outputs ─────────────────────────────────────────────
    print("\n💾  Saving all output files...\n")
    save_json_full(all_entries)
    save_chatbot_rag(all_entries)
    save_domain_files(all_entries)
    save_csv(all_entries)
    save_sqlite(all_entries)
    save_jsonl_finetune(all_entries)
    save_rasa_training(all_entries)
    save_markdown_cards(all_entries)
    save_prompt_ready(all_entries)
    save_embeddings_prep(all_entries)

    stats(all_entries)

    print("✅  ALL FILES SAVED")
    print(f"   📁 {BASE}/")
    print(f"      json/knowledge_base_full.json        ← complete database")
    print(f"      json/chatbot_knowledge_base.json     ← RAG chatbot format")
    print(f"      domain_files/*.json                  ← one per domain")
    print(f"      csv/knowledge_base.csv               ← spreadsheet format")
    print(f"      sqlite/knowledge_base.db             ← queryable database")
    print(f"      jsonl/finetune_conversations.jsonl   ← LLM fine-tuning")
    print(f"      training_data/rasa_nlu.yml           ← Rasa NLU training")
    print(f"      markdown/*.md                        ← Obsidian/Notion cards")
    print(f"      embeddings/chromadb_ready.json       ← vector DB ready")
    print(f"      chatbot_system_prompt_seed.txt       ← paste into chatbot prompt\n")

if __name__ == "__main__":
    main()