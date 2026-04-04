import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import Client, create_client

# При запуске uvicorn из папки backend cwd ≠ корень репозитория — грузим .env из gogo/
_env_root = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_env_root)
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("Warning: Supabase credentials not found. DB operations will fail.")

# Use service key for backend admin operations bypass RLS
supabase: Client = create_client(SUPABASE_URL or "http://localhost", SUPABASE_SERVICE_KEY or "dummy")

def get_db():
    return supabase
