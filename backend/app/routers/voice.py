from fastapi import APIRouter, Depends, UploadFile, File
from app.auth import get_current_user

router = APIRouter(prefix="/api/voice", tags=["voice"])

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """Заглушка: в браузере используйте встроенное распознавание (кнопка микрофона в чате). Здесь — мок для демо."""
    await file.read()
    return {
        "success": True,
        "data": {
            "transcript": "Запишитесь в ЦОН на завтра",
            "language_detected": "ru",
            "confidence": 0.85,
            "note": "Для живого голоса в Chrome/Edge включите микрофон в чате — текст пойдёт в Claude без этой загрузки файла.",
        },
    }
