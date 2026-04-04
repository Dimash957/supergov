from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.auth import get_current_user
from app.agents.queue_agent import queue_agent

router = APIRouter(prefix="/api/tson", tags=["tson"])

@router.get("/queue/{tson_id}")
async def get_queue_load(tson_id: str, user: dict = Depends(get_current_user)):
    # Умная очередь: предсказание от AI
    prediction = queue_agent.predict_queue(tson_id)
    return {
        "success": True, 
        "data": prediction
    }

class BookSlotReq(BaseModel):
    tson_id: str
    time: str

@router.post("/book")
async def book_slot(req: BookSlotReq, user: dict = Depends(get_current_user)):
    return {
        "success": True,
        "data": {"ticket_number": f"T-{random.randint(100, 999)}", "time": req.time}
    }
