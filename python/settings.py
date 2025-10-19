import os
from dotenv import load_dotenv
load_dotenv()

DGIS_API_KEY = os.getenv("DGIS_API_KEY", "")
REGION_NAME = os.getenv("REGION_NAME", "Алматы")
CITY_SLUG   = os.getenv("CITY_SLUG", "almaty")
SEARCH_TERMS = [s.strip() for s in os.getenv("SEARCH_TERMS","глэмпинг,юрта,кемпинг,база отдыха").split(",")]

INSTA_USERNAME = os.getenv("INSTA_USERNAME","")
INSTA_PASSWORD = os.getenv("INSTA_PASSWORD","")
INSTA_MAX_POSTS = int(os.getenv("INSTA_MAX_POSTS","2"))

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL","llama3.1:8b-instruct")
DESC_MAX_WORDS = int(os.getenv("DESC_MAX_WORDS","220"))

ALLOW_RENT = os.getenv("ALLOW_RENT","true").lower() == "true"

DATA_RAW = "data/raw"
DATA_OUT = "data/out"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Accept-Language": "ru,en;q=0.8"
}

os.makedirs(DATA_RAW, exist_ok=True)
os.makedirs(DATA_OUT, exist_ok=True)
