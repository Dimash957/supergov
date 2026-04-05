import random
import string
import time
from app.redis_client import redis_client

_MEMORY: dict[str, tuple[str, float]] = {}


def _key(email: str) -> str:
    return f"supergov:otp:{email.lower().strip()}"


def generate_code() -> str:
    return "".join(random.choices(string.digits, k=6))


def save_code(email: str, code: str, ttl_sec: int = 600) -> None:
    try:
        if redis_client.client:
            redis_client.client.setex(_key(email), ttl_sec, code)
        else:
            raise Exception("Redis client is None")
    except Exception as e:
        print(f"WARN OTP Storage: Using in-memory fallback (Redis error: {type(e).__name__})")
        _MEMORY[email.lower().strip()] = (code, time.time() + ttl_sec)


def verify_and_consume(email: str, code: str) -> bool:
    k = email.lower().strip()
    try:
        stored = redis_client.client.get(_key(k))
        if not stored or stored != code:
            return False
        redis_client.client.delete(_key(k))
        return True
    except Exception:
        if k not in _MEMORY:
            return False
        c, exp = _MEMORY[k]
        if time.time() > exp or c != code:
            del _MEMORY[k]
            return False
        del _MEMORY[k]
        return True
