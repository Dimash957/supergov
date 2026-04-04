from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.database import get_db
from app.agents.guide_agent import guide_agent

router = APIRouter(prefix="/api", tags=["applications"])

@router.get("/applications")
async def get_applications(user: dict = Depends(get_current_user)):
    # Feature 4
    db = get_db()
    res = db.table("applications").select("*").eq("user_id", user["id"]).execute()
    return {"success": True, "data": res.data}

@router.get("/guide/{service_type}")
async def get_guide(service_type: str, user: dict = Depends(get_current_user)):
    # Feature 3
    plan = guide_agent.get_guide(user, service_type)
    return {"success": True, "data": {"steps": plan}}

@router.post("/applications/simulate")
async def simulate_app(req: dict, user: dict = Depends(get_current_user)):
    # Feature 16
    return {
        "success": True, 
        "data": {
            "rejection_risk": "low", 
            "missing_docs": [], 
            "suggestions": ["Form looks perfect!"]
        }
    }
