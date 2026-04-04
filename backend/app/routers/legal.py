from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.auth import get_current_user
from app.agents.lawyer_agent import lawyer_agent

router = APIRouter(prefix="/api/legal", tags=["legal"])

class ConsultReq(BaseModel):
    query: str

@router.post("/consult")
async def legal_consultation(req: ConsultReq, user: dict = Depends(get_current_user)):
    # AI Юрист
    consultation = lawyer_agent.consult(req.query)
    return {"success": True, "data": consultation}
