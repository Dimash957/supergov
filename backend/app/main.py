import json
import os
from urllib.error import URLError
from urllib.request import Request, urlopen

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    family,
    forms,
    legal,
    tson,
    voice,
)

app = FastAPI(title="SuperGov API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In prod, restrict to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(forms.router)
app.include_router(applications.router)
app.include_router(benefits.router)
app.include_router(complaints.router)
app.include_router(documents.router)
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
