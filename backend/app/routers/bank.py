from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.auth import get_current_user
from app.services.halyk_connector import halyk_bank

router = APIRouter(prefix="/api/bank", tags=["bank"])

@router.get("/accounts")
async def get_accounts(user: dict = Depends(get_current_user)):
    iin = user.get("iin")
    if not iin:
        return {"success": False, "error": "User has no IIN configured"}
    accounts = halyk_bank.get_accounts(iin)
    return {"success": True, "data": accounts}

class PaymentReq(BaseModel):
    amount: float
    purpose: str

@router.post("/pay")
async def process_payment(req: PaymentReq, user: dict = Depends(get_current_user)):
    iin = user.get("iin")
    result = halyk_bank.process_payment(iin, req.amount, req.purpose)
    if not result["success"]:
        return {"success": False, "error": result["error"]}
    return {"success": True, "data": result}
