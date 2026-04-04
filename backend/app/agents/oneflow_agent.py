from app.agents.base_agent import BaseAgent
import json

class OneFlowAgent(BaseAgent):
    SYSTEM_PROMPT = """You are a Master Planner for Kazakhstan Government Services.
Given any unique life event or user input (e.g. "my wife had a baby", "I want to open a cafe with an expat partner"),
you must deduce the exact government services required.
Produce a dependency graph and an estimated days to completion.
Return ONLY JSON data matching:
{
  "services": ["service_code_1", "service_code_2"],
  "dependency_graph": {"service_code_2": ["service_code_1"]},
  "estimated_days": 14
}"""

    def generate_flow(self, life_event: str) -> dict:
        messages = [{"role": "user", "content": f"Life Event: {life_event}"}]
        res = self.call_claude(
            system_prompt=self.SYSTEM_PROMPT,
            messages=messages,
            max_tokens=1500
        )
        try:
            return json.loads(res.content[0].text)
        except Exception:
            return {"error": "Failed to generate dynamic flow"}

oneflow_agent = OneFlowAgent()
