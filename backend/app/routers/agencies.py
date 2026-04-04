from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/api/agencies", tags=["agencies"])

@router.get("/rating")
async def get_agency_rating(user: dict = Depends(get_current_user)):
    # Feature 13
    db = get_db()
    res = db.table("agencies").select("*").order("composite_score", desc=True).execute()
    return {"success": True, "data": res.data}
