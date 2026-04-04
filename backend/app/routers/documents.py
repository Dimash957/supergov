from fastapi import APIRouter, Depends, UploadFile, File
from app.auth import get_current_user
from app.database import get_db
from app.services.ocr_service import OCRService
import uuid

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.get("/")
async def get_documents(user: dict = Depends(get_current_user)):
    db = get_db()
    res = db.table("documents").select("*").eq("user_id", user["id"]).execute()
    return {"success": True, "data": res.data}

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...), 
    user: dict = Depends(get_current_user)
):
    # Feature 12: Vault & OCR
    content = await file.read()
    
    # Supabase Storage 
    db = get_db()
    file_id = str(uuid.uuid4())
    path = f"{user['id']}/{file_id}_{file.filename}"
    
    # db.storage.from_("vault").upload(path, content) # Need mocked or valid supabase client
    
    ocr_text = OCRService.extract_text(content)
    
    # In reality Call DocumentAgent for classification of ocr_text here
    classified = {
        "doc_type": "passport", 
        "fields": {"iin": user.get("iin")}
    }
    
    doc_record = {
        "user_id": user["id"],
        "doc_type": classified["doc_type"],
        "file_name": file.filename,
        "storage_path": path,
        "ocr_text": ocr_text,
        "extracted_fields": classified["fields"]
    }
    
    res = db.table("documents").insert(doc_record).execute()
    
    return {"success": True, "data": res.data}
