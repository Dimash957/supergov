"""
18 функций SuperGov для Claude tool_use — исполнение на бэкенде (мок/интеграции).
"""
from __future__ import annotations

import json
from typing import Any

from app.database import get_db
from app.services.halyk_connector import halyk_bank


def _resolve_iin(user_pk: str) -> str | None:
    if not user_pk or user_pk in ("anonymous", "mock-user-id"):
        return "870412300415"
    try:
        db = get_db()
        r = db.table("users").select("iin").eq("id", user_pk).limit(1).execute()
        if r.data:
            return r.data[0].get("iin")
    except Exception:
        pass
    return None


def _ok(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False)


def execute_tool(name: str, tool_input: dict[str, Any], user_id: str | None) -> str:
    uid = user_id or "anonymous"

    handlers = {
        "voice_agent": _voice_agent,
        "predictive_benefits": _predictive_benefits,
        "ai_lawyer": _ai_lawyer,
        "smart_queue_tson": _smart_queue_tson,
        "agency_rating": _agency_rating,
        "digital_storage": _digital_storage,
        "family_profile": _family_profile,
        "gov_analytics": _gov_analytics,
        "offline_mode": _offline_mode,
        "sandbox_application": _sandbox_application,
        "ai_chat_core": _ai_chat_core,
        "form_generation": _form_generation,
        "step_by_step_guide": _step_by_step_guide,
        "status_dashboard": _status_dashboard,
        "autofill_profile": _autofill_profile,
        "refusal_explanation": _refusal_explanation,
        "complaints_map": _complaints_map,
        "unified_life_flow": _unified_life_flow,
        # совместимость со старыми именами
        "check_bank_balance": _check_bank_balance,
        "pay_state_fee": _pay_state_fee,
        "book_tson_appointment": _book_tson_appointment,
    }

    fn = handlers.get(name)
    if not fn:
        return _ok({"ok": False, "error": f"unknown_tool:{name}"})
    try:
        return fn(tool_input, uid)
    except Exception as e:
        return _ok({"ok": False, "error": str(e)})


def _voice_agent(inp: dict, uid: str) -> str:
    return _ok({
        "ok": True,
        "feature": "Голосовой агент",
        "detail": "Полное управление голосом; распознавание через /api/voice/transcribe; ответы — Claude.",
        "user": uid,
        "action": inp.get("action") or "info",
    })


def _predictive_benefits(inp: dict, uid: str) -> str:
    return _ok({
        "ok": True,
        "feature": "Предиктивные льготы",
        "detail": "ИИ подбирает пособия и субсидии по профилю; раздел /benefits.",
        "query": inp.get("query"),
    })


def _ai_lawyer(inp: dict, uid: str) -> str:
    return _ok({
        "ok": True,
        "feature": "AI-юрист",
        "detail": "Объяснение НПА простым языком; ссылки на нормы; API /api/legal.",
        "question": inp.get("question"),
    })


def _smart_queue_tson(inp: dict, uid: str) -> str:
    return _ok({
        "ok": True,
        "feature": "Умная очередь ЦОН",
        "detail": "Запись с прогнозом загрузки; /api/tson.",
        "tson_id": inp.get("tson_id"),
        "slot": inp.get("time_slot"),
    })


def _agency_rating(inp: dict, uid: str) -> str:
    return _ok({
        "ok": True,
        "feature": "Рейтинг ведомств",
        "detail": "Публичный рейтинг по скорости и качеству; страница /rating.",
        "agency": inp.get("agency_name"),
    })


def _digital_storage(inp: dict, uid: str) -> str:
    return _ok({
        "ok": True,
        "feature": "Цифровое хранилище",
        "detail": "Документы в облаке; автоподгрузка в заявках; /documents.",
    })


def _family_profile(inp: dict, uid: str) -> str:
    return _ok({
        "ok": True,
        "feature": "Семейный профиль",
        "detail": "Один аккаунт на семью; доверенности; /family.",
    })


def _gov_analytics(inp: dict, uid: str) -> str:
    return _ok({
        "ok": True,
        "feature": "Gov-аналитика",
        "detail": "Дашборд узких мест и трендов для органа; /analytics.",
    })


def _offline_mode(inp: dict, uid: str) -> str:
    return _ok({
        "ok": True,
        "feature": "Офлайн-режим",
        "detail": "Черновики форм в IndexedDB; синхронизация при сети.",
    })


def _sandbox_application(inp: dict, uid: str) -> str:
    return _ok({
        "ok": True,
        "feature": "Песочница заявки",
        "detail": "Симуляция проверки заявки до отправки без риска.",
        "application_type": inp.get("application_type"),
    })


def _ai_chat_core(inp: dict, uid: str) -> str:
    return _ok({
        "ok": True,
        "feature": "AI-помощник MVP",
        "detail": "Чат kk/ru/en; этот диалог — Claude API.",
    })


def _form_generation(inp: dict, uid: str) -> str:
    return _ok({
        "ok": True,
        "feature": "Генерация форм",
        "detail": "Автозаполнение полей из ИИН и профиля; мастер услуг /services.",
        "service": inp.get("service_type"),
    })


def _step_by_step_guide(inp: dict, uid: str) -> str:
    return _ok({
        "ok": True,
        "feature": "Пошаговый гайд",
        "detail": "Визуальный план с прогрессом по выбранной услуге.",
        "step": inp.get("step_name"),
    })


def _status_dashboard(inp: dict, uid: str) -> str:
    return _ok({
        "ok": True,
        "feature": "Дашборд статусов",
        "detail": "Все заявки в одном месте; /applications.",
    })


def _autofill_profile(inp: dict, uid: str) -> str:
    return _ok({
        "ok": True,
        "feature": "Автозаполнение",
        "detail": "Поля формы из профиля гражданина.",
        "field_group": inp.get("field_group"),
    })


def _refusal_explanation(inp: dict, uid: str) -> str:
    return _ok({
        "ok": True,
        "feature": "AI-объяснение отказов",
        "detail": "Перевод юридического текста отказа и план исправления.",
        "refusal_snippet": inp.get("refusal_text", "")[:500],
    })


def _complaints_map(inp: dict, uid: str) -> str:
    return _ok({
        "ok": True,
        "feature": "Карта жалоб",
        "detail": "Карта + кластеризация по районам; /map.",
        "region": inp.get("region"),
    })


def _unified_life_flow(inp: dict, uid: str) -> str:
    return _ok({
        "ok": True,
        "feature": "Единый поток",
        "detail": "Жизненное событие → параллельные услуги в одном сценарии.",
        "event": inp.get("life_event"),
    })


def _check_bank_balance(inp: dict, uid: str) -> str:
    iin = _resolve_iin(uid)
    if not iin:
        return _ok({"ok": False, "error": "Нет ИИН в профиле"})
    try:
        accounts = halyk_bank.get_accounts(iin)
        return _ok({"ok": True, "bank": "Halyk (демо-интеграция)", "iin_tail": iin[-4:], "accounts": accounts})
    except Exception as e:
        return _ok({"ok": False, "error": str(e)})


def _pay_state_fee(inp: dict, uid: str) -> str:
    iin = _resolve_iin(uid)
    if not iin:
        return _ok({"ok": False, "error": "Нет ИИН в профиле"})
    amt = float(inp.get("amount") or 0)
    purpose = str(inp.get("purpose") or "госпошлина")
    try:
        result = halyk_bank.process_payment(iin, amt, purpose)
        return _ok(result)
    except Exception as e:
        return _ok({"ok": False, "error": str(e)})


def _book_tson_appointment(inp: dict, uid: str) -> str:
    return _ok({
        "ok": True,
        "tson_id": inp.get("tson_id"),
        "time_slot": inp.get("time_slot"),
        "confirmation": "MOCK-BOOKING",
    })


CHAT_TOOLS = [
    {
        "name": "voice_agent",
        "description": "Голосовой агент: полное управление голосом, доступность для пожилых и регионов.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "start|stop|info"},
            },
        },
    },
    {
        "name": "predictive_benefits",
        "description": "Предиктивные льготы: найти пособия и субсидии по праву гражданина.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
        },
    },
    {
        "name": "ai_lawyer",
        "description": "AI-юрист: объяснить законы простым языком, ссылки на НПА.",
        "input_schema": {
            "type": "object",
            "properties": {"question": {"type": "string"}},
            "required": ["question"],
        },
    },
    {
        "name": "smart_queue_tson",
        "description": "Умная очередь ЦОН: запись с предсказанием загрузки.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tson_id": {"type": "string"},
                "time_slot": {"type": "string"},
            },
        },
    },
    {
        "name": "agency_rating",
        "description": "Рейтинг ведомств: публичный рейтинг по скорости и качеству.",
        "input_schema": {
            "type": "object",
            "properties": {"agency_name": {"type": "string"}},
        },
    },
    {
        "name": "digital_storage",
        "description": "Цифровое хранилище документов в облаке и автоподгрузка в заявки.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "family_profile",
        "description": "Семейный профиль: один аккаунт на семью, доверенности онлайн.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "gov_analytics",
        "description": "Gov-аналитика: узкие места, аномалии, тренды для государства.",
        "input_schema": {
            "type": "object",
            "properties": {"metric": {"type": "string"}},
        },
    },
    {
        "name": "offline_mode",
        "description": "Офлайн-режим: черновики форм без интернета, синхронизация при подключении.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "sandbox_application",
        "description": "Песочница: проверить заявку до отправки без риска.",
        "input_schema": {
            "type": "object",
            "properties": {"application_type": {"type": "string"}},
        },
    },
    {
        "name": "ai_chat_core",
        "description": "AI-помощник MVP: мультиязычный чат (kk, ru, en) и голосовой ввод.",
        "input_schema": {
            "type": "object",
            "properties": {"language": {"type": "string", "description": "kk|ru|en"}},
        },
    },
    {
        "name": "form_generation",
        "description": "Генерация форм MVP: автозаполнение полей из ИИН и профиля.",
        "input_schema": {
            "type": "object",
            "properties": {"service_type": {"type": "string"}},
        },
    },
    {
        "name": "step_by_step_guide",
        "description": "Пошаговый гайд MVP: визуальный план с прогрессом по услуге.",
        "input_schema": {
            "type": "object",
            "properties": {"step_name": {"type": "string"}},
        },
    },
    {
        "name": "status_dashboard",
        "description": "Дашборд статусов MVP: все заявки, статусы в реальном времени.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "autofill_profile",
        "description": "Автозаполнение MVP: профиль гражданина в поля формы.",
        "input_schema": {
            "type": "object",
            "properties": {"field_group": {"type": "string"}},
        },
    },
    {
        "name": "refusal_explanation",
        "description": "AI-объяснение отказов MVP: разбор юридического текста и план исправления.",
        "input_schema": {
            "type": "object",
            "properties": {"refusal_text": {"type": "string"}},
        },
    },
    {
        "name": "complaints_map",
        "description": "Карта жалоб MVP: интерактивная карта и кластеризация по районам.",
        "input_schema": {
            "type": "object",
            "properties": {"region": {"type": "string"}},
        },
    },
    {
        "name": "unified_life_flow",
        "description": "Единый поток MVP: жизненное событие — все связанные услуги параллельно.",
        "input_schema": {
            "type": "object",
            "properties": {"life_event": {"type": "string"}},
        },
    },
    {
        "name": "check_bank_balance",
        "description": "Проверить счета и баланс Halyk Bank по ИИН пользователя (демо-интеграция).",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "pay_state_fee",
        "description": "Оплатить госпошлину с привязанного счёта Halyk (демо).",
        "input_schema": {
            "type": "object",
            "properties": {
                "amount": {"type": "number"},
                "purpose": {"type": "string"},
            },
            "required": ["amount", "purpose"],
        },
    },
]
