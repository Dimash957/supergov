from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io

class PdfGenerator:
    @staticmethod
    def generate_form(data: dict) -> bytes:
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=A4)
        c.drawString(100, 800, "SuperGov - Form Generation")
        
        y = 750
        for key, val in data.items():
            if isinstance(val, dict):
                c.drawString(100, y, f"{key}:")
                y -= 20
                for k, v in val.items():
                    c.drawString(120, y, f"{k}: {v}")
                    y -= 20
            else:
                c.drawString(100, y, f"{key}: {val}")
                y -= 20
        c.save()
        packet.seek(0)
        return packet.read()
