from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/api/family", tags=["family"])

@router.get("/")
async def get_family(user: dict = Depends(get_current_user)):
    # Feature 15
    # From eGov mock or user relations DB table
    return {"success": True, "data": []}

@router.post("/")
async def add_family_member(req: dict, user: dict = Depends(get_current_user)):
    return {"success": True, "data": {"message": "Pending validation"}}

@router.post("/verify/iin")
async def verify_iin(req: dict, user: dict = Depends(get_current_user)):
    # Feature 17
    iin = req.get("iin", "")
    if len(iin) != 12 or not iin.isdigit():
        return {"success": True, "data": {"valid": False}}
        
    weights1 = [1,2,3,4,5,6,7,8,9,10,11]
    weights2 = [3,4,5,6,7,8,9,10,11,1,2]
    sum1 = sum(int(iin[i]) * weights1[i] for i in range(11)) % 11
    
    if sum1 == 10:
        control = sum(int(iin[i]) * weights2[i] for i in range(11)) % 11
    else:
        control = sum1
        
    valid = control == int(iin[11])
    return {
        "success": True, 
        "data": {"valid": valid, "birth_date": "20" + iin[0:2] + "-" + iin[2:4] + "-" + iin[4:6]}
    }
