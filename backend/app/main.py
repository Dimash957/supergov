import json
import os
import sys
from urllib.error import URLError
from urllib.request import Request, urlopen

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Avoid Windows console encoding crashes (cp1251/cp866) on unicode logs.
for _stream in (sys.stdout, sys.stderr):
    try:
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(errors="replace")
    except Exception:
        pass

from app.routers import (
    agencies,
    analytics,
    applications,
    auth,
    bank,
    benefits,
    chat,
    complaints,
    documents,
    egov,
    family,
    forms,
    legal,
    tson,
    voice,
    profile_fix,
)

app = FastAPI(title="SuperGov API")

# allow_origins=["*"] + allow_credentials=True в браузерах некорректно; явные origin для Vite и типичных портов
def _normalize_origin(value: str) -> str:
    origin = value.strip().rstrip("/")
    if not origin:
        return ""
    if origin.startswith("http://") or origin.startswith("https://"):
        return origin
    return f"https://{origin}"


_cors_raw = os.getenv("CORS_ORIGINS", "").strip()
_cors_origins = {
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
}

if _cors_raw:
    for origin in _cors_raw.split(","):
        normalized = _normalize_origin(origin)
        if normalized:
            _cors_origins.add(normalized)

for extra_origin in (
    os.getenv("FRONTEND_URL", ""),
    os.getenv("PUBLIC_FRONTEND_URL", ""),
    os.getenv("APP_FRONTEND_URL", ""),
    os.getenv("VERCEL_URL", ""),
):
    normalized = _normalize_origin(extra_origin)
    if normalized:
        _cors_origins.add(normalized)

_cors_origin_regex = os.getenv(
    "CORS_ORIGIN_REGEX",
    r"https://.*\.vercel\.app$|https://.*\.railway\.app$",
).strip() or None

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(_cors_origins),
    allow_origin_regex=_cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(forms.router)
app.include_router(applications.router)
app.include_router(benefits.router)
app.include_router(complaints.router)
app.include_router(documents.router)
app.include_router(egov.router)
app.include_router(profile_fix.router)
app.include_router(agencies.router)
app.include_router(voice.router)
app.include_router(analytics.router)
app.include_router(family.router)
app.include_router(bank.router)
app.include_router(tson.router)
app.include_router(legal.router)

@app.get("/health")
def health_check():
    return {
        "status": "ok", 
        "version": "1.0", 
        "agents": [
            "OrchestratorAgent", 
            "NLPAgent", 
            "DocumentAgent",
            "GuideAgent",
            "RefusalAgent",
            "BenefitsAgent",
            "LawyerAgent"
        ]
    }


@app.get("/health/integrations")
def health_integrations():
    """Локальная сводка: какие переменные заданы и отвечают ли внешние URL (без секретов)."""
    stack_jwks_url = os.getenv("STACK_AUTH_JWKS_URL")
    stack_jwks_ok = False
    if stack_jwks_url:
        try:
            req = Request(stack_jwks_url, headers={"User-Agent": "SuperGov-health/1"})
            with urlopen(req, timeout=8.0) as resp:
                body = json.loads(resp.read().decode())
            stack_jwks_ok = bool(body.get("keys"))
        except (URLError, TimeoutError, OSError, ValueError, TypeError):
            stack_jwks_ok = False

    supabase_rest = "skipped"
    if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_KEY"):
        try:
            from app.database import get_db

            db = get_db()
            db.table("users").select("id").limit(1).execute()
            supabase_rest = "ok"
        except Exception as e:
            supabase_rest = f"error:{type(e).__name__}"

    sendgrid_ready = bool(os.getenv("SENDGRID_API_KEY") and os.getenv("SENDGRID_FROM_EMAIL"))
    twilio_ready = bool(
        os.getenv("TWILIO_ACCOUNT_SID")
        and os.getenv("TWILIO_AUTH_TOKEN")
        and os.getenv("TWILIO_FROM_NUMBER")
    )

    return {
        "supabase": {
            "env_url": bool(os.getenv("SUPABASE_URL")),
            "env_service_key": bool(os.getenv("SUPABASE_SERVICE_KEY")),
            "rest_probe": supabase_rest,
        },
        "stack_auth": {
            "env_project_id": bool(os.getenv("STACK_PROJECT_ID")),
            "env_jwks_url": bool(stack_jwks_url),
            "jwks_reachable": stack_jwks_ok,
        },
        "sendgrid": {
            "env_api_key": bool(os.getenv("SENDGRID_API_KEY")),
            "env_from_email": bool(os.getenv("SENDGRID_FROM_EMAIL")),
            "otp_email_ready": sendgrid_ready,
        },
        "telegram": {
            "env_bot_token": bool(os.getenv("TELEGRAM_BOT_TOKEN")),
            "note": "Call NotificationService.send_telegram(chat_id, message) from your code; no route uses it yet.",
        },
        "twilio": {
            "env_account_sid": bool(os.getenv("TWILIO_ACCOUNT_SID")),
            "env_auth_token": bool(os.getenv("TWILIO_AUTH_TOKEN")),
            "env_from_number": bool(os.getenv("TWILIO_FROM_NUMBER")),
            "sms_ready": twilio_ready,
        },
    }
