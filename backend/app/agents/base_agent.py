import os
from anthropic import Anthropic, AsyncAnthropic
from app.redis_client import redis_client
from app.database import get_db

class BaseAgent:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.sync_client = Anthropic(api_key=self.api_key) if self.api_key else None
        self.async_client = AsyncAnthropic(api_key=self.api_key) if self.api_key else None
        self.model = os.getenv(
            "ANTHROPIC_MODEL",
            "claude-haiku-4-5-20251001",
        )

    def load_context(self, session_id: str) -> dict:
        return redis_client.get_json(f"session:{session_id}") or {}

    def save_context(self, session_id: str, context: dict):
        redis_client.set_json(f"session:{session_id}", context, ttl=10800)

    def get_user_profile(self, user_id: str) -> dict:
        cache_key = f"profile:{user_id}"
        cached = redis_client.get_json(cache_key)
        if cached:
            return cached
            
        db = get_db()
        res = db.table("users").select("*").eq("id", user_id).execute()
        if res.data:
            profile = res.data[0]
            redis_client.set_json(cache_key, profile, ttl=3600)
            return profile
        return {}

    def call_claude(self, system_prompt: str, messages: list, tools=None, max_tokens=1000):
        if not self.sync_client:
            raise RuntimeError("ANTHROPIC_API_KEY is not configured")
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": messages
        }
        if tools:
            kwargs["tools"] = tools
            
        response = self.sync_client.messages.create(**kwargs)
        return response
