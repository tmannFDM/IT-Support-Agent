from __future__ import annotations

import json
import os
import re

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
from src.tools.ticket_status_tool import ticket_status_lookup

_TICKET_ID_PATTERN = re.compile(r"\b(TKT-\d+)\b", re.IGNORECASE)


def extract_ticket_id(message: str) -> str | None:
    match = _TICKET_ID_PATTERN.search(message)
    if match is None:
        return None
    return match.group(1).upper()


def is_ticket_status_request(message: str) -> bool:
    text = message.lower()
    has_status_word = "status" in text
    has_ticket_context = "ticket" in text or _TICKET_ID_PATTERN.search(message) is not None
    return has_status_word and has_ticket_context


def classify_intent_label(message: str) -> IntentLabel:
    text = message.lower()

    if any(keyword in text for keyword in ("blocked", "forbidden", "bypass", "hack", "exploit")):
        return "blocked"
    if any(keyword in text for keyword in ("escalate", "human", "agent", "manager")):
        return "escalation"
    if any(keyword in text for keyword in ("policy", "compliance", "allowed", "rule")):
        return "policy_question"
    if is_ticket_status_request(message):
        return "action_request"
    if any(keyword in text for keyword in ("reset", "create", "open", "change", "request")):
        return "action_request"
    return "direct_response"


async def classify_intent_node(state: AgentState) -> AgentState:
    _ = CLASSIFICATION_PROMPT
    intent = classify_intent_label(state["message"])
    return {**state, "intent": intent}


async def check_ticket_status_node(state: AgentState) -> AgentState:
    if state["intent"] != "action_request" or not is_ticket_status_request(state["message"]):
        return state

    ticket_id = extract_ticket_id(state["message"])
    if ticket_id is None:
        return {
            **state,
            "error": "Ticket ID is required for status lookup. Provide an ID like TKT-1001.",
        }

    tool_result = ticket_status_lookup(ticket_id)
    if tool_result is None:
        return {
            **state,
            "ticket_id": ticket_id,
            "response": f"Ticket {ticket_id} was not found.",
            "single_token_response": True,
        }

    summary = (
        f"Ticket {tool_result['ticket_id']} is {tool_result['status']} "
        f"with {tool_result['priority']} priority: {tool_result['summary']}"
    )

    return {
        **state,
        "ticket_id": tool_result["ticket_id"],
        "tool_name": "ticket_status_lookup",
        "tool_payload_json": json.dumps(tool_result),
        "response": summary,
        "single_token_response": True,
    }


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
    if "response" in state or "error" in state:
        return state

    intent = state["intent"]

    if intent != "direct_response":
        return {**state, "response": PLACEHOLDER_UNSUPPORTED}

    try:
        response = await call_llm_direct_response(state["message"])
        return {**state, "response": response}
    except Exception as exc:  # noqa: BLE001
        return {**state, "error": str(exc)}
