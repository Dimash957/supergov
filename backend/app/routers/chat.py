from __future__ import annotations

import json
import time

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.agents.nlp_agent import nlp_agent
from app.auth import get_current_user

router = APIRouter(prefix="/api/chat", tags=["chat"])

CHAT_QUEUE_KEY = "supergov:chat_queue"


def _enqueue_chat_turn(user: dict, session_id: str, message: str) -> None:
    """Сохраняет обращение в Redis-очередь (аудит / последующая обработка). Без Redis — in-memory."""
    try:
        from app.redis_client import redis_client

        payload = json.dumps(
            {
                "ts": int(time.time()),
                "user_id": str(user.get("id", "")),
                "session_id": session_id,
                "preview": (message or "")[:800],
            },
            ensure_ascii=False,
        )
        redis_client.lpush_trim(CHAT_QUEUE_KEY, payload, 499)
    except Exception:
        pass


class ChatMessageBody(BaseModel):
    message: str = Field(..., min_length=1, max_length=32000)
    session_id: str = Field(..., min_length=8, max_length=128)


@router.post("/message")
async def chat_message(
    body: ChatMessageBody,
    user: dict = Depends(get_current_user),
):
    """Потоковый ответ Claude (SSE). Все инструменты исполняются на сервере после tool_use."""
    _enqueue_chat_turn(user, body.session_id, body.message)
    return StreamingResponse(
        nlp_agent.stream_chat(body.message, body.session_id, user),
        media_type="text/event-stream",
    )


@router.get("/stream")
async def chat_stream(
    message: str = Query(...),
    session_id: str = Query(...),
    user: dict = Depends(get_current_user),
):
    """Обратная совместимость: GET + query."""
    _enqueue_chat_turn(user, session_id, message)
    return StreamingResponse(
        nlp_agent.stream_chat(message, session_id, user),
        media_type="text/event-stream",
    )
