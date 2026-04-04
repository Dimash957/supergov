from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.database import get_db
from app.agents.benefits_agent import benefits_agent

router = APIRouter(prefix="/api/benefits", tags=["benefits"])

@router.get("/")
async def get_benefits(user: dict = Depends(get_current_user)):
    # Feature 10
    db = get_db()
    all_benefits = db.table("benefits").select("*").execute().data
    
    matches = []
    total_min = 0
    total_max = 0
    
    for b in all_benefits:
        # PURE API: Claude evaluates eligibility entirely based on intelligence and given rules
        evaluation = benefits_agent.evaluate_benefit(user, b, user.get("language", "ru"))
        if evaluation.get("is_eligible", False):
            matches.append({
                "benefit": b,
                "explanation": evaluation.get("explanation", "")
            })
            total_min += b.get("amount_min", 0)
            total_max += b.get("amount_max", 0)
            
    return {
        "success": True,
        "data": {
            "benefits": matches,
            "total_amount_min": total_min,
            "total_amount_max": total_max,
            "count": len(matches)
        }
    }
