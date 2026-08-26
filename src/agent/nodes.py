from __future__ import annotations

import json
import os
import re

import httpx

from src.agent.prompts import (
    CLASSIFICATION_PROMPT,
    DIRECT_RESPONSE_SYSTEM_PROMPT,
    LLM_API_URL_ENV,
    LLM_DEFAULT_API_URL,
    LLM_DEFAULT_MODEL,
    LLM_MODEL_ENV,
    POLICY_FALLBACK_TEXT,
    POLICY_GROUNDED_SYSTEM_PROMPT,
    PLACEHOLDER_UNSUPPORTED,
    PROMPT_INJECTION_ERROR_CODE,
    PROMPT_INJECTION_ERROR_MESSAGE,
)
from src.security import detect_prompt_injection, redact_pii
from src.security.injection import normalize_for_matching
from src.rag.retrieve import retrieve_policy_chunks
from src.agent.state import AgentState, IntentLabel
from src.schemas.password_reset import PasswordResetResponse
from src.schemas.ticket_create import TicketCreateResponse
from src.tools.create_ticket import create_ticket
from src.tools.password_reset import TEMP_PASSWORD_NOTE, password_reset
from src.tools.ticket_store import get_ticket

PASSWORD_RESET_INTENT_PHRASES = (
    "reset password",
    "reset my password",
    "password reset",
    "forgot password",
    "forgot my password",
    "locked out",
)

VAGUE_REASON_PHRASES = (
    "reset my password",
    "need password reset",
    "forgot my password",
    "please reset it",
    "password reset",
    "need a reset",
)

URGENCY_PRESSURE_PHRASES = (
    "immediately",
    "right now",
    "asap",
    "as soon as possible",
    "urgent",
    "or i'll be locked out permanently",
)

EMPLOYEE_ID_PATTERN = re.compile(r"\bEMP-\d{4}\b", re.IGNORECASE)
TICKET_ID_PATTERN = re.compile(r"\bTKT-\d{4}\b", re.IGNORECASE)

TICKET_CREATE_INTENT_PHRASES = (
    "create ticket",
    "open ticket",
    "log ticket",
    "file ticket",
    "raise ticket",
    "submit ticket",
    "new ticket",
)

TICKET_CREATE_PATTERN = re.compile(
    r"\b(create|open|log|file|raise|submit|new|make)\b(?:\s+\w+){0,2}?\s+ticket\b"
)

TICKET_CATEGORY_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "Access",
        ("access", "permission", "permissions", "role", "privilege", "privileges", "unauthorized"),
    ),
    (
        "VPN",
        ("vpn", "virtual private network", "remote tunnel", "remote access"),
    ),
    (
        "Password",
        ("password", "passcode", "credential", "credentials", "locked out"),
    ),
    (
        "Hardware",
        ("hardware", "laptop", "monitor", "keyboard", "mouse", "printer", "dock"),
    ),
    (
        "Software",
        ("software", "application", "app", "install", "installation", "update", "crash", "bug"),
    ),
)

PRIORITY_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "critical",
        (
            "critical",
            "sev1",
            "service down",
            "production down",
            "outage",
            "cannot work",
            "can't work",
        ),
    ),
    (
        "high",
        ("urgent", "asap", "immediately", "blocked", "cannot access", "can't access"),
    ),
    ("low", ("minor", "low priority", "not urgent", "whenever")),
)


def is_password_reset_action_request(message: str) -> bool:
    normalized = normalize_for_matching(message)
    return any(phrase in normalized for phrase in PASSWORD_RESET_INTENT_PHRASES)


def _extract_valid_employee_id(message: str) -> str | None:
    match = EMPLOYEE_ID_PATTERN.search(message)
    if not match:
        return None
    return match.group(0).upper()


def _extract_ticket_id(message: str) -> str | None:
    match = TICKET_ID_PATTERN.search(message)
    if not match:
        return None
    return match.group(0).upper()


def is_ticket_status_action_request(message: str) -> bool:
    ticket_id = _extract_ticket_id(message)
    if ticket_id is None:
        return False
    return get_ticket(ticket_id) is not None


def is_ticket_create_action_request(message: str) -> bool:
    normalized = normalize_for_matching(message)
    if "ticket" not in normalized:
        return False
    return bool(TICKET_CREATE_PATTERN.search(normalized))


def _infer_ticket_category(normalized_message: str) -> str | None:
    for category, keywords in TICKET_CATEGORY_KEYWORDS:
        if any(keyword in normalized_message for keyword in keywords):
            return category
    return None


def _infer_ticket_priority(normalized_message: str) -> str:
    for priority, keywords in PRIORITY_KEYWORDS:
        if any(keyword in normalized_message for keyword in keywords):
            return priority
    return "medium"


def _normalize_reason_candidate(message: str) -> str:
    normalized = normalize_for_matching(message)
    without_employee_id = re.sub(r"\bemp-\d{4}\b", " ", normalized, flags=re.IGNORECASE)
    collapsed = re.sub(r"[^a-z0-9' ]", " ", without_employee_id)
    reduced = re.sub(r"\s+", " ", collapsed).strip()

    # Reduce polite wrappers before fixed-phrase matching.
    wrapper_pattern = re.compile(
        r"^(please|kindly|can you|could you|would you|i need|need|help me|hey|hi)\s+"
    )
    changed = True
    while changed and reduced:
        reduced_after = wrapper_pattern.sub("", reduced).strip()
        changed = reduced_after != reduced
        reduced = reduced_after

    if reduced.endswith(" please"):
        reduced = reduced[: -len(" please")].strip()

    return reduced


def _is_vague_reason(normalized_reason: str) -> bool:
    if not normalized_reason:
        return True
    return normalized_reason in VAGUE_REASON_PHRASES


def _has_urgency_pressure(normalized_message: str) -> bool:
    return any(phrase in normalized_message for phrase in URGENCY_PRESSURE_PHRASES)


def _select_escalation_reason(
    invalid_employee_id: bool,
    urgency_pressure: bool,
    vague_reason: bool,
) -> str | None:
    if invalid_employee_id:
        return "invalid_employee_id"
    if urgency_pressure:
        return "urgency_pressure"
    if vague_reason:
        return "vague_reason"
    return None


async def guardrail_check_node(state: AgentState) -> AgentState:
    injection_result = detect_prompt_injection(state["message"])
    if injection_result.injection_detected:
        payload = {
            "error_code": PROMPT_INJECTION_ERROR_CODE,
            "message": PROMPT_INJECTION_ERROR_MESSAGE,
        }
        return {
            **state,
            "injection_detected": True,
            "pii_detected": False,
            "error_code": PROMPT_INJECTION_ERROR_CODE,
            "error": json.dumps(payload),
        }

    redaction_result = redact_pii(state["message"])
    return {
        **state,
        "message": redaction_result.redacted_message,
        "injection_detected": False,
        "pii_detected": redaction_result.pii_detected,
        "redacted_email_count": redaction_result.redacted_email_count,
        "redacted_phone_count": redaction_result.redacted_phone_count,
    }


def classify_intent_label(message: str) -> IntentLabel:
    text = message.lower()

    if is_ticket_status_action_request(message):
        return "action_request"

    if is_ticket_create_action_request(message):
        return "action_request"

    if is_password_reset_action_request(message):
        return "action_request"

    if any(keyword in text for keyword in ("blocked", "forbidden", "bypass", "hack", "exploit")):
        return "blocked"
    if any(keyword in text for keyword in ("escalate", "human", "agent", "manager")):
        return "escalation"
    if any(
        keyword in text
        for keyword in ("reset", "create", "open", "change", "request", "forgot", "locked out")
    ):
        return "action_request"
    if any(
        keyword in text
        for keyword in (
            "policy",
            "compliance",
            "allowed",
            "rule",
            "vpn",
            "password",
            "mfa",
            "access",
            "software",
            "hardware",
        )
    ):
        return "policy_question"
    return "direct_response"


async def classify_intent_node(state: AgentState) -> AgentState:
    _ = CLASSIFICATION_PROMPT
    intent = classify_intent_label(state["message"])
    return {**state, "intent": intent}


async def check_password_reset_node(state: AgentState) -> AgentState:
    normalized_message = normalize_for_matching(state["message"])
    employee_id = _extract_valid_employee_id(state["message"])
    normalized_reason = _normalize_reason_candidate(state["message"])

    invalid_employee_id = employee_id is None
    urgency_pressure = _has_urgency_pressure(normalized_message)
    print(f"[DEBUG] normalized_reason={normalized_reason!r}")
    vague_reason = _is_vague_reason(normalized_reason)
    escalation_reason = _select_escalation_reason(
        invalid_employee_id=invalid_employee_id,
        urgency_pressure=urgency_pressure,
        vague_reason=vague_reason,
    )

    if escalation_reason is not None:
        escalation_payload = PasswordResetResponse(
            employee_id=employee_id or "UNKNOWN",
            status="escalated",
            temporary_password_note=TEMP_PASSWORD_NOTE,
            escalation_reason=escalation_reason,
        )
        return {
            **state,
            "escalation_reason": escalation_reason,
            "tool_call": escalation_payload.model_dump_json(),
            "response": (
                "Your password reset request has been escalated to a human agent for identity "
                "verification."
            ),
        }

    try:
        tool_result = await password_reset(employee_id=employee_id, reason=normalized_reason)
    except Exception as exc:  # noqa: BLE001
        return {**state, "error": str(exc)}

    return {
        **state,
        "tool_call": tool_result.model_dump_json(),
        "response": (
            "Password reset has been initiated. "
            "A temporary password has been issued and must be changed on next login."
        ),
    }


async def check_ticket_status_node(state: AgentState) -> AgentState:
    ticket_id = _extract_ticket_id(state["message"])
    if ticket_id is None:
        return {**state, "response": PLACEHOLDER_UNSUPPORTED}

    ticket = get_ticket(ticket_id)
    if ticket is None:
        return {**state, "response": f"No ticket was found for {ticket_id}."}

    return {
        **state,
        "ticket_id": ticket["ticket_id"],
        "response": (
            f"Ticket {ticket['ticket_id']} is {ticket['status']} with {ticket['priority']} priority "
            f"in {ticket['category']}. Summary: {ticket['summary']}"
        ),
    }


async def create_ticket_node(state: AgentState) -> AgentState:
    normalized_message = normalize_for_matching(state["message"])
    category = _infer_ticket_category(normalized_message)
    if category is None:
        return {
            **state,
            "error": (
                "Please provide more detail so I can categorize your ticket "
                "(VPN, Password, Hardware, Software, or Access)."
            ),
        }

    priority = _infer_ticket_priority(normalized_message)

    try:
        tool_result = await create_ticket(
            category=category,
            priority=priority,
            summary=state["message"].strip(),
        )
    except Exception as exc:  # noqa: BLE001
        return {**state, "error": str(exc)}

    response_payload = TicketCreateResponse(
        ticket_id=tool_result.ticket_id,
        category=tool_result.category,
        priority=tool_result.priority,
        status=tool_result.status,
        summary=tool_result.summary,
    )

    return {
        **state,
        "ticket_id": response_payload.ticket_id,
        "ticket_category": response_payload.category,
        "ticket_priority": response_payload.priority,
        "tool_call": response_payload.model_dump_json(),
        "response": (
            f"Ticket {response_payload.ticket_id} has been created with "
            f"{response_payload.priority} priority."
        ),
    }


async def call_llm_direct_response(message: str) -> str:
    api_url = os.getenv(LLM_API_URL_ENV, LLM_DEFAULT_API_URL)
    model = os.getenv(LLM_MODEL_ENV, LLM_DEFAULT_MODEL)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": DIRECT_RESPONSE_SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(api_url, json=payload)
        response.raise_for_status()
        data = response.json()

    try:
        return data["message"]["content"].strip()
    except (KeyError, IndexError, TypeError, AttributeError) as exc:
        raise RuntimeError("LLM response was missing expected content") from exc


async def call_llm_policy_response(question: str, context: str) -> str:
    api_url = os.getenv(LLM_API_URL_ENV, LLM_DEFAULT_API_URL)
    model = os.getenv(LLM_MODEL_ENV, LLM_DEFAULT_MODEL)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": POLICY_GROUNDED_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Question: {question}\n\nContext:\n{context}",
            },
        ],
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(api_url, json=payload)
        response.raise_for_status()
        data = response.json()

    try:
        return data["message"]["content"].strip()
    except (KeyError, IndexError, TypeError, AttributeError) as exc:
        raise RuntimeError("Policy LLM response was missing expected content") from exc


def _append_policy_citations(answer: str, sources: list[str]) -> str:
    unique_sources = sorted({source for source in sources if source})
    if not unique_sources:
        return answer.strip()

    citations = "Sources: " + ", ".join(unique_sources)
    cleaned_answer = answer.strip()
    if not cleaned_answer:
        return citations
    return f"{cleaned_answer}\n\n{citations}"


async def answer_policy_question_node(state: AgentState) -> AgentState:
    retrieval = retrieve_policy_chunks(state["message"], top_k=3, threshold=0.35)
    if not retrieval.above_threshold_items:
        return {
            **state,
            "used_context": False,
            "retrieved_chunks": [],
            "cited_sources": [],
            "response": POLICY_FALLBACK_TEXT,
        }

    sources = [item.source_document for item in retrieval.above_threshold_items]
    context = "\n\n".join(
        [
            f"Source: {item.source_document}\n"
            f"Category: {item.policy_category}\n"
            f"{item.text}"
            for item in retrieval.above_threshold_items
        ]
    )

    try:
        answer = await call_llm_policy_response(state["message"], context)
    except Exception as exc:  # noqa: BLE001
        return {**state, "error": str(exc)}

    return {
        **state,
        "used_context": True,
        "retrieved_chunks": [
            {
                "chunk_id": item.chunk_id,
                "score": item.score,
                "policy_category": item.policy_category,
                "source_document": item.source_document,
            }
            for item in retrieval.above_threshold_items
        ],
        "cited_sources": sorted({source for source in sources if source}),
        "response": _append_policy_citations(answer, sources),
    }


async def generate_response_node(state: AgentState) -> AgentState:
    intent = state["intent"]

    if intent != "direct_response":
        return {**state, "response": PLACEHOLDER_UNSUPPORTED}

    try:
        response = await call_llm_direct_response(state["message"])
        return {**state, "response": response}
    except Exception as exc:  # noqa: BLE001
        return {**state, "error": str(exc)}
