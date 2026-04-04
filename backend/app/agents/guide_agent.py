from app.agents.base_agent import BaseAgent
import json

class GuideAgent(BaseAgent):
    SYSTEM_PROMPT = """You are a step-by-step guide for Kazakhstan government services.
Create a personalized action plan for the citizen.
Each step must have: title, description, duration_days, required_docs list, agency name, depends_on (step numbers).
Personalize: skip steps the citizen already completed (has EDS, has bank account, etc.)
Citizen profile: {profile}
Service type: {service_type}
Return ONLY a JSON array of step objects."""

    def get_guide(self, profile: dict, service_type: str) -> list:
        system = self.SYSTEM_PROMPT.format(
            profile=json.dumps(profile, ensure_ascii=False),
            service_type=service_type
        )
        
        res = self.call_claude(
            system_prompt=system,
            messages=[{"role": "user", "content": "Generate the personalized plan."}],
            max_tokens=1500
        )
        try:
            return json.loads(res.content[0].text)
        except Exception:
            return []

guide_agent = GuideAgent()
