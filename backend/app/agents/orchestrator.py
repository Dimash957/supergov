import json
from app.agents.base_agent import BaseAgent

class OrchestratorAgent(BaseAgent):
    SYSTEM_PROMPT = """You are the orchestrator of SuperGov, a Kazakhstan government services platform. 
Classify the user's intent into one of: [register_ip, child_benefit, passport, property_registration, 
car_registration, no_criminal, housing_subsidy, utility_subsidy, education_grant, pension, 
medical_policy, business_license, land_registration, marriage_cert, divorce_cert, 
death_cert, disability_benefit, general_question].
Extract key entities. Detect language (kk/ru/en).
Return JSON only: {"intent": "...", "entities": {}, "language": "ru", "confidence": 0.9}"""

    def classify(self, message: str, session_id: str) -> dict:
        context = self.load_context(session_id)
        
        messages = [{"role": "user", "content": message}]
        
        # Tool forcing JSON could be used, but instruction prompting works for Claude
        response = self.call_claude(
            system_prompt=self.SYSTEM_PROMPT,
            messages=messages,
            max_tokens=500
        )
        
        try:
            return json.loads(response.content[0].text)
        except:
            return {"intent": "general_question", "entities": {}, "language": "ru", "confidence": 0.0}

orchestrator = OrchestratorAgent()
