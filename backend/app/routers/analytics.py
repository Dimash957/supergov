from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/agencies")
async def get_analytics(user: dict = Depends(get_current_user)):
    # Feature 14
    # Real world: ensure user role is admin
    return {
        "success": True, 
        "data": {"insight": "Rejection rate anomaly in Mgd."}
    }

from app.agents.oneflow_agent import oneflow_agent

@router.get("/oneflow/{life_event}")
async def get_oneflow(life_event: str, user: dict = Depends(get_current_user)):
    # Feature 8 - Pure Claude API Generation
    flow_data = oneflow_agent.generate_flow(life_event)
    return {
        "success": True,
        "data": flow_data
    }
