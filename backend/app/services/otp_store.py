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
        redis_client.client.setex(_key(email), ttl_sec, code)
    except Exception:
        _MEMORY[email.lower().strip()] = (code, time.time() + ttl_sec)


def verify_and_consume(email: str, code: str) -> bool:
    k = email.lower().strip()
    try:
        stored = redis_client.client.get(_key(email))
        if not stored or stored != code:
            return False
        redis_client.client.delete(_key(email))
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
