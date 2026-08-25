from __future__ import annotations

import os

import httpx

from src.agent.prompts import (
    CLASSIFICATION_PROMPT,
    DIRECT_RESPONSE_SYSTEM_PROMPT,
    LLM_API_KEY_ENV,
    LLM_API_URL_ENV,
    LLM_DEFAULT_API_URL,
    LLM_DEFAULT_MODEL,
    LLM_MODEL_ENV,
    PLACEHOLDER_UNSUPPORTED,
)
from src.agent.state import AgentState, IntentLabel


def classify_intent_label(message: str) -> IntentLabel:
    text = message.lower()

    if any(keyword in text for keyword in ("blocked", "forbidden", "bypass", "hack", "exploit")):
        return "blocked"
    if any(keyword in text for keyword in ("escalate", "human", "agent", "manager")):
        return "escalation"
    if any(keyword in text for keyword in ("policy", "compliance", "allowed", "rule")):
        return "policy_question"
    if any(keyword in text for keyword in ("reset", "create", "open", "change", "request")):
        return "action_request"
    return "direct_response"


async def classify_intent_node(state: AgentState) -> AgentState:
    _ = CLASSIFICATION_PROMPT
    intent = classify_intent_label(state["message"])
    return {**state, "intent": intent}


async def call_llm_direct_response(message: str) -> str:
    api_key = os.getenv(LLM_API_KEY_ENV)
    if not api_key:
        raise RuntimeError("LLM API key is not configured")

    api_url = os.getenv(LLM_API_URL_ENV, LLM_DEFAULT_API_URL)
    model = os.getenv(LLM_MODEL_ENV, LLM_DEFAULT_MODEL)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": DIRECT_RESPONSE_SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        "temperature": 0.2,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError, AttributeError) as exc:
        raise RuntimeError("LLM response was missing expected content") from exc


async def generate_response_node(state: AgentState) -> AgentState:
    intent = state["intent"]

    if intent != "direct_response":
        return {**state, "response": PLACEHOLDER_UNSUPPORTED}

    try:
        response = await call_llm_direct_response(state["message"])
        return {**state, "response": response}
    except Exception as exc:  # noqa: BLE001
        return {**state, "error": str(exc)}
