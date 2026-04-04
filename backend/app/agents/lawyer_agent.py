from app.agents.base_agent import BaseAgent
import json

class LawyerAgent(BaseAgent):
    SYSTEM_PROMPT = """Вы - высококвалифицированный юридический ИИ-помощник для граждан Казахстана.
Ваша задача: Объяснять законы и НПА Республики Казахстан простым, понятным языком (без юридического жаргона).
Каждый ответ должен содержать:
1. Понятное объяснение сути закона
2. Прямые ссылки на статьи НПА (например, "ст. 43 Гражданского кодекса РК")
3. Рекомендацию для гражданина, что делать.
Гражданин задал вопрос: {query}"""

    def consult(self, query: str) -> dict:
        system = self.SYSTEM_PROMPT.format(query=query)
        res = self.call_claude(
            system_prompt=system,
            messages=[{"role": "user", "content": "Пожалуйста, объясни этот правовой нюанс."}],
            max_tokens=1500
        )
        return {
            "answer": res.content[0].text
        }

lawyer_agent = LawyerAgent()
