from __future__ import annotations

import uuid
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.auth import get_current_user
from app.database import get_db
from app.services.ocr_service import OCRService
from app.services.form_filler_ai import form_filler_ai
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.get("/")
async def get_documents(user: dict = Depends(get_current_user)):
    try:
        db = get_db()
        res = db.table("documents").select("*").eq("user_id", user["id"]).execute()
        return {"success": True, "data": res.data}
    except Exception as e:
        if "Invalid API key" in str(e):
            raise HTTPException(503, "Supabase connection failed. Invalid API key.")
        raise HTTPException(503, f"Database error: {type(e).__name__}")

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


# ====== AI ЗАПОЛНЕНИЕ ФОРМ ======

@router.post("/extract-ai")
async def extract_with_ai(
    file: UploadFile = File(...),
    doc_type: Optional[str] = "passport",
    user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Загрузить документ и автоматически извлечь данные используя AI
    Поддерживает: паспорт, удостоверение, свидетельство о рождении, браке
    """
    try:
        content = await file.read()
        
        # Использовать OCR для извлечения текста
        ocr_text = OCRService.extract_text(content)
        
        # Использовать AI для извлечения структурированных данных
        extracted_data = form_filler_ai.extract_from_document(ocr_text, doc_type)
        
        # Валидировать извлеченные данные
        validation = form_filler_ai.validate_extracted_data(extracted_data)
        
        # Сохранить в БД
        db = get_db()
        file_id = str(uuid.uuid4())
        
        doc_record = {
            "user_id": user["id"],
            "doc_type": doc_type,
            "file_name": file.filename,
            "ocr_text": ocr_text,
            "extracted_fields": extracted_data,
            "validation_score": validation.get("confidence", 0),
            "extraction_method": "ai"
        }
        
        res = db.table("documents").insert(doc_record).execute()
        
        logger.info(f"AI извлечение для пользователя {user['id']}: {doc_type}")
        
        return {
            "success": True,
            "file_id": res.data[0]["id"] if res.data else file_id,
            "doc_type": doc_type,
            "extracted_data": extracted_data,
            "validation": validation,
            "message": "Данные успешно извлечены",
            "next_action": "fill-form" if validation["valid"] else "review"
        }
    
    except Exception as e:
        logger.error(f"Ошибка AI извлечения: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка извлечения: {str(e)}")


@router.post("/{doc_id}/fill-form")
async def fill_form(
    doc_id: str,
    service_type: str = "PASSPORT",
    user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Автоматически заполнить форму подачи в ЦОН на основе извлеченных данных
    
    Параметры:
    - service_type: тип услуги (PASSPORT, ID_CARD, DRIVING_LICENSE, BENEFITS)
    """
    try:
        db = get_db()
        
        # Получить документ
        res = db.table("documents").select("*").eq("id", doc_id).eq("user_id", user["id"]).execute()
        
        if not res.data:
            raise HTTPException(status_code=404, detail="Документ не найден")
        
        doc = res.data[0]
        extracted_data = doc.get("extracted_fields", {})
        
        if not extracted_data:
            raise HTTPException(status_code=400, detail="Данные еще не извлечены из документа")
        
        # Заполнить форму используя AI
        filled_form = form_filler_ai.auto_fill_form(service_type, extracted_data)
        
        # Сохранить заполненную форму в БД
        update_data = {
            "filled_form": filled_form,
            "service_type": service_type,
            "filled_at": datetime.now().isoformat()
        }
        
        db.table("documents").update(update_data).eq("id", doc_id).execute()
        
        logger.info(f"Форма заполнена для {user['id']}: {service_type}")
        
        return {
            "success": True,
            "file_id": doc_id,
            "service_type": service_type,
            "form": filled_form,
            "status": "draft",
            "message": "Форма автоматически заполнена. Пожалуйста, проверьте данные перед отправкой."
        }
    
    except Exception as e:
        logger.error(f"Ошибка заполнения формы: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка заполнения формы: {str(e)}")


@router.put("/{doc_id}/form-update")
async def update_form(
    doc_id: str,
    form_updates: Dict[str, Any],
    user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Редактировать заполненную форму перед отправкой
    Пользователь может изменить любые поля
    """
    try:
        db = get_db()
        
        # Получить документ
        res = db.table("documents").select("*").eq("id", doc_id).eq("user_id", user["id"]).execute()
        
        if not res.data:
            raise HTTPException(status_code=404, detail="Документ не найден")
        
        doc = res.data[0]
        filled_form = doc.get("filled_form", {})
        
        if not filled_form:
            raise HTTPException(status_code=400, detail="Форма еще не заполнена")
        
        # Обновить поля в форме
        if "fields" in filled_form:
            filled_form["fields"].update(form_updates.get("fields", {}))
        
        filled_form["last_edited_at"] = datetime.now().isoformat()
        
        # Сохранить обновленную форму
        db.table("documents").update({"filled_form": filled_form}).eq("id", doc_id).execute()
        
        logger.info(f"Форма отредактирована для {user['id']}")
        
        return {
            "success": True,
            "file_id": doc_id,
            "form": filled_form,
            "message": "Форма обновлена"
        }
    
    except Exception as e:
        logger.error(f"Ошибка обновления формы: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления формы: {str(e)}")


@router.post("/{doc_id}/submit-form")
async def submit_form(
    doc_id: str,
    user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Отправить заполненную форму подачи в ЦОН
    """
    try:
        db = get_db()
        
        # Получить документ
        res = db.table("documents").select("*").eq("id", doc_id).eq("user_id", user["id"]).execute()
        
        if not res.data:
            raise HTTPException(status_code=404, detail="Документ не найден")
        
        doc = res.data[0]
        filled_form = doc.get("filled_form", {})
        
        if not filled_form:
            raise HTTPException(status_code=400, detail="Форма еще не заполнена")
        
        # Изменить статус на submitted
        filled_form["status"] = "submitted"
        filled_form["submitted_at"] = datetime.now().isoformat()
        
        # Генерировать номер заявления
        application_number = f"APP-{doc_id[:8].upper()}-{datetime.now().strftime('%Y%m%d')}"
        filled_form["application_number"] = application_number
        
        # Сохранить в БД  
        db.table("documents").update({
            "filled_form": filled_form,
            "status": "submitted",
            "application_number": application_number
        }).eq("id", doc_id).execute()
        
        logger.info(f"Форма отправлена: {application_number}")
        
        return {
            "success": True,
            "file_id": doc_id,
            "application_number": application_number,
            "status": "submitted",
            "message": "Ваша заявка успешно отправлена в ЦОН"
        }
    
    except Exception as e:
        logger.error(f"Ошибка отправки формы: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка отправки формы: {str(e)}")
