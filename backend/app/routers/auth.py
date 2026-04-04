from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from pydantic import BaseModel, Field, model_validator

from app.auth import SUPERGOV_JWT_SECRET, get_current_user
from app.database import get_db
from app.services.notifications import NotificationService
from app.services.otp_store import generate_code, save_code, verify_and_consume

router = APIRouter(prefix="/api/auth", tags=["auth"])

JWT_EXP_DAYS = 7


class RegisterRequest(BaseModel):
    stack_user_id: str
    iin: str = Field(..., min_length=12, max_length=12)
    email: str
    phone: str
    full_name: str = Field(..., min_length=2, max_length=300)

    @model_validator(mode="before")
    @classmethod
    def map_name_to_full_name(cls, data: object):
        if isinstance(data, dict) and not data.get("full_name") and data.get("name"):
            return {**data, "full_name": data["name"]}
        return data


class OtpSendRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=320)


class OtpVerifyRequest(BaseModel):
    email: str
    code: str = Field(..., min_length=6, max_length=6)


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    address: str | None = None
    birth_date: str | None = None
    language: str | None = None


@router.post("/register")
async def register_user(req: RegisterRequest):
    if not req.iin.isdigit():
        raise HTTPException(400, "IIN must be 12 digits")

    db = get_db()
    existing = db.table("users").select("id").eq("iin", req.iin).execute()
    if existing.data:
        raise HTTPException(400, "IIN already registered")

    user_data = {
        "stack_user_id": req.stack_user_id,
        "iin": req.iin,
        "email": req.email,
        "phone": req.phone,
        "full_name": req.full_name,
    }

    res = db.table("users").insert(user_data).execute()
    if not res.data:
        raise HTTPException(500, "Database insertion failed")

    NotificationService.send_email(
        req.email,
        "Добро пожаловать в SuperGov",
        f"<p>Здравствуйте, {req.full_name}!</p><p>Регистрация завершена. Вход по коду на почту доступен на странице входа.</p>",
    )

    return {"success": True, "data": {"user_id": res.data[0]["id"], "message": "OK"}}


@router.post("/otp/send")
async def otp_send(body: OtpSendRequest):
    db = get_db()
    found = db.table("users").select("id,email,full_name").eq("email", body.email.strip()).execute()
    if not found.data:
        raise HTTPException(404, "Пользователь с таким email не найден. Сначала зарегистрируйтесь.")

    code = generate_code()
    save_code(body.email, code)
    ok = NotificationService.send_email(
        body.email.strip(),
        "SuperGov — код входа",
        f"<p>Ваш код для входа: <strong style='font-size:24px'>{code}</strong></p><p>Код действителен 10 минут.</p>",
    )
    if not ok:
        raise HTTPException(503, "Не удалось отправить письмо (проверьте SENDGRID_API_KEY и SENDGRID_FROM_EMAIL)")
    return {"success": True, "data": {"message": "Код отправлен на email"}}


@router.post("/otp/verify")
async def otp_verify(body: OtpVerifyRequest):
    if not verify_and_consume(body.email, body.code.strip()):
        raise HTTPException(400, "Неверный или просроченный код")

    db = get_db()
    user_res = db.table("users").select("*").eq("email", body.email.strip()).execute()
    if not user_res.data:
        raise HTTPException(404, "Пользователь не найден")

    user = user_res.data[0]
    exp = datetime.now(timezone.utc) + timedelta(days=JWT_EXP_DAYS)
    token = jwt.encode(
        {
            "sub": str(user["id"]),
            "typ": "supergov_otp",
            "email": user["email"],
            "exp": int(exp.timestamp()),
        },
        SUPERGOV_JWT_SECRET,
        algorithm="HS256",
    )

    return {
        "success": True,
        "data": {
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": user["id"], "full_name": user.get("full_name"), "email": user["email"]},
        },
    }


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    return {"success": True, "data": user}


@router.patch("/me")
async def patch_me(body: ProfileUpdateRequest, user: dict = Depends(get_current_user)):
    uid = user.get("id")
    if not uid or uid == "mock-user-id":
        return {"success": True, "data": user}

    updates = {k: v for k, v in body.model_dump(exclude_none=True).items()}
    if not updates:
        return {"success": True, "data": user}

    db = get_db()
    res = db.table("users").update(updates).eq("id", uid).execute()
    if not res.data:
        raise HTTPException(500, "Не удалось обновить профиль")
    return {"success": True, "data": res.data[0]}
