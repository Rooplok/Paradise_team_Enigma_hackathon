"""
MVP AI service: заглушка.
Позже подключите Transformers/LLM.
Сейчас: простые эвристики + шаблон.
"""

import re
from typing import Any

def analyze_message(subject: str, text: str) -> dict[str, Any]:
    low = (subject + "\n" + text).lower()

    # category (very naive)
    if "оплат" in low or "платеж" in low or "billing" in low:
        category = "billing"
    elif "не могу войти" in low or "login" in low or "парол" in low:
        category = "login"
    elif "ошибк" in low or "error" in low or "exception" in low:
        category = "bug"
    else:
        category = "general"

    # priority
    priority = "medium"
    if any(x in low for x in ["срочно", "urgent", "не работает", "down", "прод", "production"]):
        priority = "high"
    if any(x in low for x in ["вопрос", "как сделать", "how to"]):
        priority = "low"

    # entities
    error_codes = re.findall(r"\b(?:0x[0-9a-fA-F]+|E\d{3,6}|\d{3,5})\b", text)
    version = re.findall(r"\bv?\d+\.\d+(?:\.\d+)?\b", text)
    os_hint = ""
    if "windows" in low:
        os_hint = "Windows"
    elif "mac" in low or "os x" in low:
        os_hint = "macOS"
    elif "linux" in low:
        os_hint = "Linux"

    summary = text.strip().split("\n")[0][:220]
    if not summary:
        summary = subject[:220]

    missing = []
    if category == "bug" and not error_codes:
        missing.append("Пожалуйста, пришлите текст ошибки/код ошибки (если есть).")
    if category in ("bug", "login") and not os_hint:
        missing.append("Укажите, пожалуйста, ОС и версию приложения.")
    if not missing:
        missing.append("Если возможно, приложите скриншот или логи — поможет ускорить решение.")

    draft = (
        "Здравствуйте!\n\n"
        "Спасибо за обращение. Мы приняли ваш запрос в работу.\n"
        "Чтобы быстрее помочь, уточните, пожалуйста:\n"
        + "\n".join(f"- {q}" for q in missing)
        + "\n\nС уважением,\nТехподдержка"
    )

    suggested_actions = {"next_step": "request_info" if missing else "reply"}

    confidence = 55
    if category in ("billing", "login", "bug"):
        confidence = 70

    return {
        "category": category,
        "priority": priority,
        "product": "",
        "summary": summary,
        "entities": {
            "error_codes": error_codes[:10],
            "versions": version[:5],
            "os": os_hint,
        },
        "missing_info": missing,
        "draft_reply": draft,
        "suggested_actions": suggested_actions,
        "confidence": confidence,
        "model_versions": {"mvp": "heuristics-v1"},
    }