import os
import httpx
import logging
from typing import Optional
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

from app.database import get_db

_env_gogo = Path(__file__).resolve().parents[2] / ".env"
_env_backend = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(_env_gogo)
load_dotenv(_env_backend)
load_dotenv()

security = HTTPBearer(auto_error=False)
STACK_AUTH_JWKS_URL = (os.getenv("STACK_AUTH_JWKS_URL") or "").strip() or None
# Пробел после = в .env даёт ведущий пробел в UUID → audience JWT не совпадает
STACK_PROJECT_ID = (os.getenv("STACK_PROJECT_ID") or "").strip()
SUPERGOV_JWT_SECRET = os.getenv(
    "SUPERGOV_JWT_SECRET",
    "dev-supergov-jwt-change-in-production",
)

_jwks = None


async def get_jwks(force_refresh: bool = False):
    """JWKS Stack; force_refresh — сброс кэша (смена ключа подписи)."""
    global _jwks
    if not STACK_AUTH_JWKS_URL:
        return None
    if force_refresh:
        _jwks = None
    if not _jwks:
        async with httpx.AsyncClient() as client:
            resp = await client.get(STACK_AUTH_JWKS_URL, timeout=15.0)
            if resp.status_code != 200:
                return None
            _jwks = resp.json()
    if not _jwks or not isinstance(_jwks.get("keys"), list):
        return None
    return _jwks


def _token_alg(token: str) -> Optional[str]:
    try:
        return jwt.get_unverified_header(token).get("alg")
    except Exception:
        return None


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
    logger.info("🔐=== get_current_user() CALLED ===")
    
    if not STACK_AUTH_JWKS_URL:
        logger.info("⚠️  STACK_AUTH_JWKS_URL not set, returning MOCK user")
        return {
            "id": "mock-user-id",
            "stack_user_id": "mock-stack",
            "full_name": "Демо пользователь",
            "iin": "870412300415",
            "email": "demo@supergov.kz",
            "phone": "+77001234567",
        }

    if not credentials:
        logger.error("❌ Missing authorization header")
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = credentials.credentials
    logger.debug(f"📌 Token received, first 50 chars: {token[:50]}...")

    otp_user = _user_from_supergov_token(token)
    if otp_user:
        logger.info(f"✅ OTP token verified for user: {otp_user.get('email')}")
        return otp_user

    alg = _token_alg(token)
    logger.debug(f"🔍 Token algorithm: {alg}")
    # Токен входа по коду (HS256) не совместим с проверкой Stack — иначе «Unable to parse»
    if alg == "HS256":
        raise HTTPException(
            status_code=401,
            detail=(
                "Сессия по коду из письма недействительна (истекла, другой SUPERGOV_JWT_SECRET в .env, "
                "или пользователь не найден в базе). Запросите новый код на странице входа или войдите по паролю Stack."
            ),
        )
    if alg is None:
        raise HTTPException(status_code=401, detail="Повреждённый токен авторизации. Выйдите и войдите снова.")
    if alg not in ("RS256", "ES256"):
        raise HTTPException(
            status_code=401,
            detail=f"Неподдерживаемый алгоритм токена ({alg}). Выйдите и войдите снова.",
        )

    try:
        jwks = await get_jwks()
        if not jwks:
            raise HTTPException(
                status_code=503,
                detail="Не удалось загрузить ключи Stack (JWKS). Проверьте STACK_AUTH_JWKS_URL и сеть.",
            )
        unverified_header = jwt.get_unverified_header(token)
        token_kid = unverified_header.get("kid")
        claims = jwt.get_unverified_claims(token)
        expected_iss = claims.get("iss") or (
            f"https://api.stack-auth.com/api/v1/projects/{STACK_PROJECT_ID}"
        )

        def _pick_key(jwks_doc: dict) -> dict:
            key_data: dict = {}
            for key in jwks_doc.get("keys") or []:
                if key.get("kid") != token_kid:
                    continue
                key_type = key.get("kty")
                key_data = {
                    "kty": key_type,
                    "kid": key.get("kid"),
                    "use": key.get("use", "sig"),
                }
                if key_type == "RSA":
                    key_data["n"] = key.get("n")
                    key_data["e"] = key.get("e")
                elif key_type == "EC":
                    key_data["x"] = key.get("x")
                    key_data["y"] = key.get("y")
                    key_data["crv"] = key.get("crv")
                break
            return key_data

        key_data = _pick_key(jwks)
        is_valid_key = False
        if key_data.get("kty") == "RSA":
            is_valid_key = key_data.get("n") and key_data.get("e")
        elif key_data.get("kty") == "EC":
            is_valid_key = key_data.get("x") and key_data.get("y") and key_data.get("crv")
        
        if not is_valid_key:
            jwks = await get_jwks(force_refresh=True)
            if jwks:
                key_data = _pick_key(jwks)
                if key_data.get("kty") == "RSA":
                    is_valid_key = key_data.get("n") and key_data.get("e")
                elif key_data.get("kty") == "EC":
                    is_valid_key = key_data.get("x") and key_data.get("y") and key_data.get("crv")

        if not is_valid_key:
            raise HTTPException(
                status_code=401,
                detail=(
                    f"Ключ подписи Stack (kid={token_kid!r}) не найден в JWKS. "
                    "Обновите страницу или выйдите и войдите снова."
                ),
            )

        aud_claim = claims.get("aud")
        try:
            payload = jwt.decode(
                token,
                key_data,
                algorithms=["RS256", "ES256"],
                audience=STACK_PROJECT_ID,
                issuer=expected_iss,
            )
        except JWTError:
            try:
                payload = jwt.decode(
                    token,
                    key_data,
                    algorithms=["RS256", "ES256"],
                    audience=aud_claim,
                    issuer=expected_iss,
                )
            except JWTError as je_aud:
                raise HTTPException(
                    status_code=401,
                    detail=f"Токен Stack: проверка audience/issuer не прошла ({je_aud!s}). Проверьте STACK_PROJECT_ID в .env.",
                ) from je_aud
        stack_user_id = payload.get("sub")
        logger.info(f"🔑 Stack user_id from token: {stack_user_id}")
        logger.debug(f"   Payload fields: {list(payload.keys())}")
        logger.debug(f"   Email: {payload.get('primary_email') or payload.get('email')}")
        logger.debug(f"   Name: {payload.get('display_name')}")
        
        db = get_db()
        logger.debug("📊 Querying database for existing user...")
        user_res = db.table("users").select("*").eq("stack_user_id", stack_user_id).execute()
        
        if user_res.data:
            logger.info(f"✅ Found existing user: {stack_user_id} (DB ID: {user_res.data[0].get('id')})")
            return user_res.data[0]
        
        # NEW USER - AUTO-CREATE PROFILE
        logger.info(f"👤 New user detected: {stack_user_id}. Creating profile...")
        try:
            email = payload.get("primary_email") or payload.get("email") or f"{stack_user_id}@supergov.kz"
            full_name = payload.get("display_name") or stack_user_id
            
            logger.debug(f"   📧 Email: {email}")
            logger.debug(f"   👌 Full name: {full_name}")
            
            new_user_data = {
                "stack_user_id": stack_user_id,
                "email": email.strip().lower(),
                "full_name": full_name,
                "phone": "",
                "iin": "",
            }
            
            logger.info(f"📝 Inserting user to database...")
            logger.debug(f"   Data: {new_user_data}")
            
            insert_res = db.table("users").insert(new_user_data).execute()
            logger.debug(f"   Response data: {insert_res.data}")
            logger.debug(f"   Response count: {insert_res.count}")
            
            if insert_res.data:
                user_id = insert_res.data[0].get('id')
                logger.info(f"✅ User created successfully (DB ID: {user_id})")
                logger.info(f"   Email: {insert_res.data[0].get('email')}")
                logger.info(f"   Name: {insert_res.data[0].get('full_name')}")
                return insert_res.data[0]
            else:
                logger.warning(f"⚠️  Insert returned empty response, retrying query...")
                # Retry if insert succeeded but returned empty
                retry_res = db.table("users").select("*").eq("stack_user_id", stack_user_id).execute()
                if retry_res.data:
                    logger.info(f"✅ Found created user on retry (DB ID: {retry_res.data[0].get('id')})")
                    return retry_res.data[0]
                else:
                    logger.error(f"❌ Retry query also returned empty")
        except Exception as e:
            logger.error(f"❌ Failed to create user: {type(e).__name__}")
            logger.error(f"   Error: {str(e)}")
            logger.exception(e)
        
        logger.error(f"❌ Could not create profile for {stack_user_id}")
        raise HTTPException(
            status_code=404,
            detail="Профиль не найден. Пожалуйста, обновите страницу или попробуйте позже.",
        )

    except JWTError as je:
        logger.error(f"❌ JWT validation failed: {type(je).__name__}")
        logger.error(f"   Details: {str(je)}")
        raise HTTPException(
            status_code=401,
            detail=f"Токен Stack недействителен или устарел: {je!s}. Выйдите и войдите снова.",
        ) from je
    
    finally:
        logger.info("🔐=== get_current_user() FINISHED ===")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
