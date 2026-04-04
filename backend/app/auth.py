import os
import httpx
from typing import Optional
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pathlib import Path

from dotenv import load_dotenv

from app.database import get_db

_env_root = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_env_root)
load_dotenv()

security = HTTPBearer(auto_error=False)
STACK_AUTH_JWKS_URL = os.getenv("STACK_AUTH_JWKS_URL")
SUPERGOV_JWT_SECRET = os.getenv(
    "SUPERGOV_JWT_SECRET",
    "dev-supergov-jwt-change-in-production",
)

_jwks = None


async def get_jwks():
    global _jwks
    if not _jwks:
        async with httpx.AsyncClient() as client:
            resp = await client.get(STACK_AUTH_JWKS_URL)
            if resp.status_code == 200:
                _jwks = resp.json()
    return _jwks


def _user_from_supergov_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token,
            SUPERGOV_JWT_SECRET,
            algorithms=["HS256"],
        )
        if payload.get("typ") != "supergov_otp":
            return None
        uid = payload.get("sub")
        if not uid:
            return None
        db = get_db()
        user_res = db.table("users").select("*").eq("id", uid).execute()
        if user_res.data:
            return user_res.data[0]
    except JWTError:
        return None
    return None


async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)):
    if not STACK_AUTH_JWKS_URL:
        return {
            "id": "mock-user-id",
            "stack_user_id": "mock-stack",
            "full_name": "Демо пользователь",
            "iin": "870412300415",
            "email": "demo@supergov.kz",
            "phone": "+77001234567",
        }

    if not credentials:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = credentials.credentials

    otp_user = _user_from_supergov_token(token)
    if otp_user:
        return otp_user

    try:
        jwks = await get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
        if rsa_key:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=os.getenv("STACK_PROJECT_ID"),
                issuer=f"https://api.stack-auth.com/api/v1/projects/{os.getenv('STACK_PROJECT_ID')}",
            )
            stack_user_id = payload.get("sub")
            db = get_db()
            user_res = db.table("users").select("*").eq("stack_user_id", stack_user_id).execute()
            if not user_res.data:
                raise HTTPException(
                    status_code=404,
                    detail="Профиль не найден в базе — сначала завершите регистрацию на странице «Создать аккаунт».",
                )
            return user_res.data[0]

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    raise HTTPException(status_code=401, detail="Unable to parse authentication token")
