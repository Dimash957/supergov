import pytesseract
from PIL import Image
import io

class OCRService:
    @staticmethod
    def extract_text(file_bytes: bytes) -> str:
        try:
            image = Image.open(io.BytesIO(file_bytes))
            # Require both RU and KZ, ENG fallback
            text = pytesseract.image_to_string(image, lang="rus+kaz+eng")
            return text
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""
