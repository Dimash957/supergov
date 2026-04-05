import json
import os
from pathlib import Path

from dotenv import load_dotenv

_env_root = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_env_root)
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# In-process fallback, если Redis не запущен (dev / Windows без Docker)
_memory_kv: dict[str, str] = {}
_memory_lists: dict[str, list[str]] = {}


class RedisClient:
    """Redis при наличии; иначе in-memory (сессии Claude и очередь не переживут рестарт процесса)."""

    def __init__(self):
        self._redis = None
        try:
            import redis

            r = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
            r.ping()
            self._redis = r
            print("OK: Redis подключен успешно")
        except Exception as e:
            print(
                f"WARN: Redis недоступен ({type(e).__name__}). "
                "Используется память процесса; установите Redis для продакшена."
            )

    @property
    def client(self):
        """Сырой redis-клиент или None — для otp_store и совместимости."""
        return self._redis

    def get_json(self, key: str):
        if self._redis is not None:
            try:
                val = self._redis.get(key)
                if val:
                    return json.loads(val)
            except Exception:
                pass
        raw = _memory_kv.get(key)
        if raw:
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return None
        return None

    def set_json(self, key: str, value: dict, ttl: int = 10800):
        s = json.dumps(value, ensure_ascii=False)
        if self._redis is not None:
            try:
                self._redis.setex(key, ttl, s)
                return
            except Exception:
                pass
        _memory_kv[key] = s

    def delete(self, key: str):
        if self._redis is not None:
            try:
                self._redis.delete(key)
            except Exception:
                pass
        _memory_kv.pop(key, None)

    def lpush_trim(self, list_key: str, payload: str, max_keep: int) -> None:
        if self._redis is not None:
            try:
                self._redis.lpush(list_key, payload)
                self._redis.ltrim(list_key, 0, max_keep)
                return
            except Exception:
                pass
        lst = _memory_lists.setdefault(list_key, [])
        lst.insert(0, payload)
        del lst[max_keep + 1 :]


redis_client = RedisClient()
