import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


class ComplaintCreate(BaseModel):
    category: str = Field(..., min_length=1, max_length=120)
    description: str = Field(..., min_length=3, max_length=4000)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


@router.get("/")
async def get_complaints(user: dict = Depends(get_current_user)):
    db = get_db()
    res = db.table("complaints").select("*").order("created_at", desc=True).limit(500).execute()
    return {"success": True, "data": res.data or []}


@router.post("/")
async def create_complaint(body: ComplaintCreate, user: dict = Depends(get_current_user)):
    uid = user.get("id")
    row = {
        "category": body.category,
        "description": body.description,
        "lat": body.lat,
        "lng": body.lng,
        "status": "new",
        "votes": 0,
    }
    if not uid or uid == "mock-user-id":
        return {
            "success": True,
            "data": {
                "id": str(uuid.uuid4()),
                **row,
                "user_id": None,
                "demo": True,
            },
        }
    db = get_db()
    row["user_id"] = uid
    res = db.table("complaints").insert(row).execute()
    return {"success": True, "data": res.data[0] if res.data else row}


@router.post("/{complaint_id}/vote")
async def vote_complaint(complaint_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    cur = db.table("complaints").select("votes").eq("id", complaint_id).execute()
    if not cur.data:
        raise HTTPException(status_code=404, detail="not_found")
    v = (cur.data[0].get("votes") or 0) + 1
    db.table("complaints").update({"votes": v}).eq("id", complaint_id).execute()
    return {"success": True, "data": {"votes": v}}


@router.get("/clusters")
async def get_clusters(user: dict = Depends(get_current_user)):
    return {
        "success": True,
        "data": {
            "insight": "Кластеризация по районам доступна на карте; добавляйте жалобы через форму «Сообщить о проблеме».",
        },
    }
