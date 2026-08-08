import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("DATA_DIR", BASE_DIR / "data"))
DB_PATH = DATA_DIR / "opinion.db"
MANIFESTO_DIR = DATA_DIR / "manifestos"
INDEX_DIR = DATA_DIR / "index"

DATA_DIR.mkdir(parents=True, exist_ok=True)
MANIFESTO_DIR.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

REDDIT_USER_AGENT = os.environ.get(
    "REDDIT_USER_AGENT", "python:public-opinion-aggregator:v1.0 (by /u/dev21382)"
)
REDDIT_SUBREDDITS = "india+IndianPolitics+IndiaSpeaks+worldnews"

INGESTION_INTERVAL_MINUTES = int(os.environ.get("INGESTION_INTERVAL_MINUTES", "60"))
FORECAST_RETRAIN_INTERVAL_HOURS = int(os.environ.get("FORECAST_RETRAIN_INTERVAL_HOURS", "24"))
