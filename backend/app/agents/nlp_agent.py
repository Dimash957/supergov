from app.agents.base_agent import BaseAgent
from app.agents.chat_tools import CHAT_TOOLS, execute_tool
import json

class NLPAgent(BaseAgent):
    SYSTEM_PROMPT = """You are SuperGov AI for Kazakhstan public services (eGov). You answer via the Claude API.

You can answer general questions (science, culture, everyday life) accurately and briefly, not only government topics.

When the user needs platform data or actions (benefits, ЦОН, ratings, complaints map, family, documents, analytics, bank, fees, forms, voice agent, lawyer, queue, sandbox, offline, unified flow, etc.), call the matching tool from your tool list (voice_agent, predictive_benefits, ai_lawyer, smart_queue_tson, agency_rating, digital_storage, family_profile, gov_analytics, offline_mode, sandbox_application, form_generation, step_by_step_guide, status_dashboard, autofill_profile, refusal_explanation, complaints_map, unified_life_flow, …) instead of guessing.

Languages: Kazakh (қазақша), Russian, English — reply in the user's language.

Address the citizen by their preferred name when greeting or when it feels natural: {display_name}

When a tool returns JSON, summarize clearly for a non-technical citizen. Never claim a payment or booking succeeded unless the tool result says ok.

Citizen profile (may be empty): {profile}
"""

    async def stream_chat(
        self,
        message: str,
        session_id: str,
        user: dict | None = None,
    ):
        user_id = (user or {}).get("id")

        display_name = ""
        if user:
            display_name = (
                (user.get("full_name") or "").strip()
                or (user.get("displayName") or "").strip()
                or (user.get("email") or "").split("@")[0]
            )

        context = self.load_context(session_id)
        api_messages: list = context.get("api_messages") or []

        if user and user.get("id") == "mock-user-id":
            profile = {k: v for k, v in user.items() if v is not None}
        elif user_id:
            profile = self.get_user_profile(user_id)
        else:
            profile = {}
        system_prompt = self.SYSTEM_PROMPT.format(
            profile=json.dumps(profile, ensure_ascii=False),
            display_name=display_name or "(не указано — поздоровайтесь нейтрально)",
        )

        api_messages.append({"role": "user", "content": message})

        if not self.api_key or not self.async_client:
            api_messages.pop()
            err = "Сервер: не задан ANTHROPIC_API_KEY."
            yield f'data: {json.dumps({"token": err, "done": True, "error": True})}\n\n'
            return

        final_text = ""
        try:
            final_text = await self._run_tool_loop(
                system_prompt, api_messages, user_id
            )
        except Exception as e:
            if api_messages and api_messages[-1].get("role") == "user":
                api_messages.pop()
            err = f"Ошибка AI: {e!s}"
            yield f'data: {json.dumps({"token": err, "done": True, "error": True})}\n\n'
            return

        # сохраняем историю для следующего сообщения (ограничение размера)
        context["api_messages"] = api_messages[-48:]
        self.save_context(session_id, context)

        # потоковая отдача текста клиенту
        chunk = 48
        for i in range(0, len(final_text), chunk):
            part = final_text[i : i + chunk]
            yield f'data: {json.dumps({"token": part, "done": False})}\n\n'

        yield f'data: {json.dumps({"token": "", "done": True, "intent": "chat"})}\n\n'

    async def _run_tool_loop(
        self, system_prompt: str, messages: list, user_id: str | None
    ) -> str:
        max_turns = 10
        for _ in range(max_turns):
            resp = await self.async_client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=messages,
                tools=CHAT_TOOLS,
            )

            assistant_blocks = []
            for block in resp.content:
                if block.type == "text":
                    assistant_blocks.append({"type": "text", "text": block.text})
                elif block.type == "tool_use":
                    assistant_blocks.append(
                        {
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input,
                        }
                    )

            messages.append({"role": "assistant", "content": assistant_blocks})

            if resp.stop_reason == "end_turn":
                return "".join(
                    b.text for b in resp.content if b.type == "text"
                )

            if resp.stop_reason == "tool_use":
                tool_results = []
                for block in resp.content:
                    if block.type != "tool_use":
                        continue
                    out = execute_tool(block.name, dict(block.input or {}), user_id)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": out,
                        }
                    )
                if not tool_results:
                    return "Не удалось выполнить инструменты."
                messages.append({"role": "user", "content": tool_results})
                continue

            return "Запрос прерван (лимит токенов или другая причина). Повторите вопрос."

        return "Слишком много шагов. Упростите запрос."

nlp_agent = NLPAgent()
