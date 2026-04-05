from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.auth import get_current_user
from app.database import get_db
from app.services.form_filler_ai import form_filler_ai
from app.services.ocr_service import OCRService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/documents", tags=["documents"])


def success_response(data: Any = None, message: str = "Success", **kwargs) -> Dict[str, Any]:
    return {
        "success": True,
        "message": message,
        "data": data,
        **kwargs,
    }


@router.get("/")
async def get_documents(user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    try:
        db = get_db()
        res = db.table("documents").select("*").eq("user_id", user["id"]).execute()
        return success_response(data=res.data or [], message="Documents loaded")
    except Exception as e:
        logger.error("get_documents error: %s", e)
        raise HTTPException(status_code=500, detail="Failed to load documents")


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")

        ocr_text = OCRService.extract_text(content)
        db = get_db()
        file_id = str(uuid.uuid4())

        doc_record = {
            "id": file_id,
            "user_id": user["id"],
            "doc_type": "passport",
            "file_name": file.filename,
            "ocr_text": ocr_text,
            "extracted_fields": {"iin": user.get("iin", "")},
            "status": "uploaded",
            "created_at": datetime.now().isoformat(),
        }
        res = db.table("documents").insert(doc_record).execute()
        row = res.data[0] if res.data else doc_record

        return success_response(
            data=row,
            file_id=row.get("id", file_id),
            message="Document uploaded",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("upload_document error: %s", e)
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")


@router.post("/extract-ai")
async def extract_with_ai(
    file: UploadFile = File(...),
    doc_type: Optional[str] = "passport",
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")

        ocr_text = OCRService.extract_text(content)
        if not ocr_text or ocr_text.startswith("("):
            ocr_text = ""

        extracted_data = form_filler_ai.extract_from_document(ocr_text, doc_type or "passport") if ocr_text else {}
        validation = form_filler_ai.validate_extracted_data(extracted_data)

        db = get_db()
        file_id = str(uuid.uuid4())
        doc_record = {
            "id": file_id,
            "user_id": user["id"],
            "doc_type": doc_type,
            "file_name": file.filename,
            "ocr_text": ocr_text,
            "extracted_fields": extracted_data,
            "validation_score": validation.get("confidence", 0),
            "extraction_method": "ai",
            "status": "extracted",
            "created_at": datetime.now().isoformat(),
        }

        try:
            res = db.table("documents").insert(doc_record).execute()
            saved_file_id = res.data[0]["id"] if res.data else file_id
        except Exception as db_error:
            logger.warning("extract_with_ai db fallback: %s", db_error)
            saved_file_id = file_id

        payload = {
            "file_id": saved_file_id,
            "doc_type": doc_type,
            "extracted_data": extracted_data,
            "validation": validation,
        }
        return success_response(
            data=payload,
            file_id=saved_file_id,
            doc_type=doc_type,
            extracted_data=extracted_data,
            validation=validation,
            message="Data extracted",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("extract_with_ai error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}")


@router.post("/{doc_id}/fill-form")
async def fill_form(
    doc_id: str,
    service_type: str = "PASSPORT",
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        db = get_db()
        res = db.table("documents").select("*").eq("id", doc_id).eq("user_id", user["id"]).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Document not found")

        doc = res.data[0]
        extracted_data = doc.get("extracted_fields", {})
        if not extracted_data:
            raise HTTPException(status_code=400, detail="No extracted data")

        filled_form = form_filler_ai.auto_fill_form(service_type, extracted_data)
        db.table("documents").update(
            {
                "filled_form": filled_form,
                "service_type": service_type,
                "filled_at": datetime.now().isoformat(),
                "status": "filled",
            }
        ).eq("id", doc_id).execute()

        payload = {
            "file_id": doc_id,
            "service_type": service_type,
            "form": filled_form,
            "status": "draft",
        }
        return success_response(
            data=payload,
            file_id=doc_id,
            service_type=service_type,
            form=filled_form,
            status="draft",
            message="Form filled",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("fill_form error: %s", e)
        raise HTTPException(status_code=500, detail=f"Fill form failed: {e}")


@router.put("/{doc_id}/form-update")
async def update_form(
    doc_id: str,
    form_updates: Dict[str, Any],
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        db = get_db()
        res = db.table("documents").select("*").eq("id", doc_id).eq("user_id", user["id"]).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Document not found")

        doc = res.data[0]
        filled_form = doc.get("filled_form") or {}
        if not filled_form:
            raise HTTPException(status_code=400, detail="Form is not filled")

        if isinstance(filled_form.get("fields"), dict):
            updates = form_updates.get("fields", {}) if isinstance(form_updates.get("fields", {}), dict) else {}
            filled_form["fields"].update(updates)
        else:
            filled_form.update(form_updates)

        filled_form["last_edited_at"] = datetime.now().isoformat()
        db.table("documents").update({"filled_form": filled_form}).eq("id", doc_id).execute()

        return success_response(
            data={"file_id": doc_id, "form": filled_form},
            file_id=doc_id,
            form=filled_form,
            message="Form updated",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_form error: %s", e)
        raise HTTPException(status_code=500, detail=f"Update form failed: {e}")


@router.post("/{doc_id}/submit-form")
async def submit_form(
    doc_id: str,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        db = get_db()
        res = db.table("documents").select("*").eq("id", doc_id).eq("user_id", user["id"]).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Document not found")

        doc = res.data[0]
        filled_form = doc.get("filled_form") or {}
        if not filled_form:
            raise HTTPException(status_code=400, detail="Form is not filled")

        application_number = f"APP-{doc_id[:8].upper()}-{datetime.now().strftime('%Y%m%d')}"
        db.table("documents").update(
            {
                "status": "submitted",
                "submitted_at": datetime.now().isoformat(),
                "application_number": application_number,
                "filled_form": {
                    **filled_form,
                    "status": "submitted",
                    "submitted_at": datetime.now().isoformat(),
                    "application_number": application_number,
                },
            }
        ).eq("id", doc_id).execute()

        payload = {
            "file_id": doc_id,
            "application_number": application_number,
            "status": "submitted",
        }
        return success_response(
            data=payload,
            file_id=doc_id,
            application_number=application_number,
            status="submitted",
            message="Application submitted",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("submit_form error: %s", e)
        raise HTTPException(status_code=500, detail=f"Submit form failed: {e}")
