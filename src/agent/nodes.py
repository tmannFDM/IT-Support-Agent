from __future__ import annotations

import os

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
)
from src.rag.retrieve import retrieve_policy_chunks
from src.agent.state import AgentState, IntentLabel


def classify_intent_label(message: str) -> IntentLabel:
    text = message.lower()

    if any(keyword in text for keyword in ("blocked", "forbidden", "bypass", "hack", "exploit")):
        return "blocked"
    if any(keyword in text for keyword in ("escalate", "human", "agent", "manager")):
        return "escalation"
    if any(keyword in text for keyword in ("reset", "create", "open", "change", "request")):
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
