from app.agents.base_agent import BaseAgent
import json

class BenefitsAgent(BaseAgent):
    SYSTEM_PROMPT = """You are a benefits specialist for Kazakhstan.
You evaluate if a citizen matches specific benefit rules.
Citizen profile: {profile}
Benefit details & rules: {benefit}
1. Analyze ALL criteria strictly against the user profile.
2. If the user does NOT meet the criteria, set `is_eligible` to false.
3. If they DO meet the criteria, set `is_eligible` to true and generate an encouraging explanation in {language}.
Return ONLY JSON:
{
  "is_eligible": true,
  "explanation": "..."
}"""

    def evaluate_benefit(self, profile: dict, benefit: dict, language: str = 'ru') -> dict:
        system = self.SYSTEM_PROMPT.format(
            profile=json.dumps(profile, ensure_ascii=False),
            benefit=json.dumps(benefit, ensure_ascii=False),
            language=language
        )
        res = self.call_claude(
            system_prompt=system,
            messages=[{"role": "user", "content": "Generate explanation for my benefits."}],
            max_tokens=500
        )
        try:
            return json.loads(res.content[0].text)
        except Exception:
            return {"is_eligible": False, "explanation": ""}

benefits_agent = BenefitsAgent()
