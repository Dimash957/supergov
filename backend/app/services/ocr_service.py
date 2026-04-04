from __future__ import annotations

import io
import os

from PIL import Image

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

class OCRService:
    @staticmethod
    def extract_text(file_bytes: bytes) -> str:
        try:
            if not PYTESSERACT_AVAILABLE:
                print("Warning: Tesseract OCR not installed. Install it via: apt-get install tesseract-ocr")
                return "(OCR недоступен - установите Tesseract)"
            
            image = Image.open(io.BytesIO(file_bytes))
            # Require both RU and KZ, ENG fallback
            if os.name == "nt":  # Windows
                # On Windows, tesseract path may need to be set manually
                try:
                    text = pytesseract.image_to_string(image, lang="rus+kaz+eng")
                except pytesseract.TesseractNotFoundError:
                    print("Tesseract not found in PATH on Windows")
                    return "(Tesseract не найден в PATH)"
            else:
                text = pytesseract.image_to_string(image, lang="rus+kaz+eng")
            return text
        except Exception as e:
            print(f"OCR Error: {e!s}")
            return f"(OCR ошибка: {type(e).__name__})"
