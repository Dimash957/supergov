import os
import json
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class RedisClient:
    def __init__(self):
        self.client = redis.from_url(REDIS_URL, decode_responses=True)

    def get_json(self, key: str):
        val = self.client.get(key)
        if val:
            return json.loads(val)
        return None

    def set_json(self, key: str, value: dict, ttl: int = 10800):
        self.client.setex(key, ttl, json.dumps(value))

    def delete(self, key: str):
        self.client.delete(key)

redis_client = RedisClient()
