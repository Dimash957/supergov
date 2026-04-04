from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.auth import get_current_user
from app.agents.document_agent import document_agent
from app.services.egov_mock import egov_mock
from app.agents.refusal_agent import refusal_agent

router = APIRouter(prefix="/api/forms", tags=["forms"])

class GenerateFormReq(BaseModel):
    service_type: str
    session_id: str

@router.post("/generate")
async def generate_form(req: GenerateFormReq, user: dict = Depends(get_current_user)):
    # Feature 2
    # Mocking vault
    vault = [{"doc_type": "passport", "file_name": "pass.pdf"}]
    form_data = document_agent.generate_form(req.service_type, user, vault)
    return {"success": True, "data": form_data}

class AutoFillReq(BaseModel):
    service_type: str

@router.post("/autofill")
async def autofill_form(req: AutoFillReq, user: dict = Depends(get_current_user)):
    # Feature 5
    profile = egov_mock.get_citizen_by_iin(user.get("iin", ""))
    if not profile:
        profile = user
    return {"success": True, "data": {"pre_filled": profile, "sources": {"iin": "ГБД ФЛ"}}}

class RefusalReq(BaseModel):
    text: str

@router.post("/refusal/analyze")
async def analyze_refusal(req: RefusalReq, user: dict = Depends(get_current_user)):
    # Feature 6
    analysis = refusal_agent.analyze_refusal(req.text, user.get("language", "ru"))
    return {"success": True, "data": analysis}
