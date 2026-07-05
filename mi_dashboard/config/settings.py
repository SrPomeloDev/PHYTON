import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
EXCEL_PATH = BASE_DIR.parent / "bbdd_prueba.xlsx"

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

STREAMLIT_CONFIG = {
    "page_title": "Dashboard Comercial — Andina S.A.",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

RANGO_VENTA_BINS = [0, 50, 100, 200, 500, 1000, float("inf")]
RANGO_VENTA_LABELS = ["0-50", "51-100", "101-200", "201-500", "501-1000", "1000+"]
