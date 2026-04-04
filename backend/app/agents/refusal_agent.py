from app.agents.base_agent import BaseAgent
import json

class RefusalAgent(BaseAgent):
    SYSTEM_PROMPT = """You are a legal interpreter for Kazakhstan government services.
A citizen received an official rejection. Parse it and:
1. Find the exact reason for rejection
2. Translate to plain human language (in citizen's language)
3. List specific corrective actions with exact documents needed
4. Reference the specific law/regulation
Return JSON only: {"reason_raw": "...", "reason_plain": "...", "actions": [{"step": 1, "description": "...", "required_doc": "..."}], "legal_reference": "..."}"""

    def analyze_refusal(self, ocr_text: str, language: str = "ru") -> dict:
        messages = [{"role": "user", "content": f"Language preference: {language}\n\nRefusal Document Text:\n{ocr_text}"}]
        res = self.call_claude(
            system_prompt=self.SYSTEM_PROMPT,
            messages=messages,
            max_tokens=2000
        )
        try:
            return json.loads(res.content[0].text)
        except Exception:
            return {"error": "Failed to parse API response"}

refusal_agent = RefusalAgent()
