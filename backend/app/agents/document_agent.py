from app.agents.base_agent import BaseAgent
import json

class DocumentAgent(BaseAgent):
    SYSTEM_PROMPT = """You are a document specialist for Kazakhstan government services.
Given a service type and citizen profile, you must:
1. Identify the correct government form
2. Map profile fields to form fields 
3. List which fields can be auto-filled vs need manual input
4. Generate the filled form data as JSON
5. Validate all required fields are present
Citizen profile: {profile}
Available documents in vault: {documents}
Service type: {service_type}
Return JSON only: {"form_name": "...", "auto_filled": {}, "needs_input": [{"field": "...", "label": "...", "reason": "..."}], "validation_errors": []}"""

    def generate_form(self, service_type: str, profile: dict, documents: list) -> dict:
        system = self.SYSTEM_PROMPT.format(
            profile=json.dumps(profile, ensure_ascii=False),
            documents=json.dumps(documents, ensure_ascii=False),
            service_type=service_type
        )
        
        res = self.call_claude(
            system_prompt=system,
            messages=[{"role": "user", "content": f"Generate form for {service_type}"}],
            max_tokens=2000
        )
        return json.loads(res.content[0].text)

document_agent = DocumentAgent()
