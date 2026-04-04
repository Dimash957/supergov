from app.agents.base_agent import BaseAgent
import json

class QueueAgent(BaseAgent):
    SYSTEM_PROMPT = """You are an AI analyzing TsON (Public Service Center) loads.
Given a TsON region code and time context, realistically predict the crowd load using your internal model of crowd behavior.
Return ONLY JSON:
{
  "tson_id": "...",
  "current_load_percent": 85,
  "estimated_wait_minutes": 45,
  "recommendation": "Come after 4 PM",
  "available_slots": ["16:00", "16:30"]
}"""

    def predict_queue(self, tson_id: str) -> dict:
        messages = [{"role": "user", "content": f"Predict load for TsON: {tson_id}"}]
        res = self.call_claude(
            system_prompt=self.SYSTEM_PROMPT,
            messages=messages,
            max_tokens=800
        )
        try:
            return json.loads(res.content[0].text)
        except Exception:
            return {"error": "Failed to predict queue"}

queue_agent = QueueAgent()
