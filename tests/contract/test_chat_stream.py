import asyncio
import json

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.routes import chat as chat_route
from src.api.routes.chat import generate_chat_events
from src.schemas.chat import ChatRequest

client = TestClient(app)


def _extract_sse_events(body: str) -> list[dict[str, str]]:
    events: list[dict[str, str]] = []
    for line in body.splitlines():
        if line.startswith("data: "):
            events.append(json.loads(line[6:]))
    return events


@pytest.fixture(autouse=True)
def patch_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_llm(message: str) -> str:
        return f"Answer for: {message}"

    monkeypatch.setattr("src.agent.nodes.call_llm_direct_response", fake_llm)


def test_chat_stream_direct_response_emits_intent_token_and_done() -> None:
    response = client.post(
        "/chat/stream",
        json={"user_id": "u-1", "session_id": "s-1", "message": "what can you do"},
    )

    assert response.status_code == 200
    events = _extract_sse_events(response.text)
    assert events
    assert events[0]["event_type"] == "intent"
    assert events[0]["data"] == "direct_response"
    assert any(event["event_type"] == "token" for event in events)
    assert events[-1]["event_type"] == "done"


def test_ticket_status_lookup_success_emits_tool_call_token_and_done() -> None:
    response = client.post(
        "/chat/stream",
        json={"user_id": "u-10", "session_id": "s-10", "message": "status for tkt-1001"},
    )

    assert response.status_code == 200
    events = _extract_sse_events(response.text)
    assert [event["event_type"] for event in events[:4]] == ["intent", "tool_call", "token", "done"]
    assert events[0]["data"] == "action_request"
    tool_payload = json.loads(events[1]["data"])
    assert tool_payload["ticket_id"] == "TKT-1001"
    assert tool_payload["status"] == "open"
    assert tool_payload["priority"] == "high"
    assert tool_payload["summary"]
    assert tool_payload["last_updated"].endswith("Z")


def test_ticket_status_lookup_missing_id_emits_error_without_tool_call_or_done() -> None:
    response = client.post(
        "/chat/stream",
        json={"user_id": "u-11", "session_id": "s-11", "message": "what is the status of my ticket"},
    )

    assert response.status_code == 200
    events = _extract_sse_events(response.text)
    assert events[0]["event_type"] == "intent"
    assert events[1]["event_type"] == "error"
    assert "Ticket ID is required" in events[1]["data"]
    assert not any(event["event_type"] == "tool_call" for event in events)
    assert not any(event["event_type"] == "done" for event in events)


def test_ticket_status_lookup_unknown_id_emits_not_found_token_and_done() -> None:
    response = client.post(
        "/chat/stream",
        json={"user_id": "u-12", "session_id": "s-12", "message": "status for TKT-9999"},
    )

    assert response.status_code == 200
    events = _extract_sse_events(response.text)
    assert [event["event_type"] for event in events[:3]] == ["intent", "token", "done"]
    assert "not found" in events[1]["data"].lower()
    assert not any(event["event_type"] == "error" for event in events)
    assert not any(event["event_type"] == "tool_call" for event in events)


@pytest.mark.parametrize(
    ("message", "expected_intent"),
    [
        ("what is the policy for vpn", "policy_question"),
        ("please reset my password", "action_request"),
        ("please escalate this", "escalation"),
        ("how to exploit admin panel", "blocked"),
    ],
)
def test_non_direct_intents_emit_placeholder_then_done(message: str, expected_intent: str) -> None:
    response = client.post(
        "/chat/stream",
        json={"user_id": "u-2", "session_id": "s-2", "message": message},
    )

    assert response.status_code == 200
    events = _extract_sse_events(response.text)
    assert events[0] == {"event_type": "intent", "data": expected_intent}
    token_events = [event for event in events if event["event_type"] == "token"]
    assert token_events
    assert "This type of request isn't supported yet." in " ".join(
        event["data"] for event in token_events
    )
    assert events[-1]["event_type"] == "done"


def test_direct_response_generation_failure_emits_error_without_done(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def failing_llm(_message: str) -> str:
        raise RuntimeError("LLM failure")

    monkeypatch.setattr("src.agent.nodes.call_llm_direct_response", failing_llm)

    response = client.post(
        "/chat/stream",
        json={"user_id": "u-3", "session_id": "s-3", "message": "what can you do"},
    )

    assert response.status_code == 200
    events = _extract_sse_events(response.text)
    assert events[0]["event_type"] == "intent"
    assert events[0]["data"] == "direct_response"
    assert events[1]["event_type"] == "error"
    assert not any(event["event_type"] == "done" for event in events)


def test_chat_stream_missing_and_empty_fields_return_422() -> None:
    response = client.post(
        "/chat/stream",
        json={"user_id": "", "session_id": "s-1"},
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error_code"] == "ERR-VALIDATION-MISSING-FIELD"
    assert isinstance(payload["message"], str) and payload["message"]


def test_chat_stream_whitespace_fields_return_422_with_all_details() -> None:
    response = client.post(
        "/chat/stream",
        json={"user_id": "   ", "session_id": "\t", "message": "   "},
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error_code"] == "ERR-VALIDATION-MISSING-FIELD"
    details = payload.get("details", [])
    fields = {item["field"] for item in details}
    assert {"user_id", "session_id", "message"}.issubset(fields)
    for item in details:
        assert set(item.keys()) == {"field", "issue"}


def test_chat_stream_uses_scope_error_code_only() -> None:
    response = client.post("/chat/stream", json={})

    assert response.status_code == 422
    assert response.json()["error_code"] == "ERR-VALIDATION-MISSING-FIELD"


def test_disconnect_stops_before_done_event() -> None:
    state = {"calls": 0}

    async def is_disconnected() -> bool:
        state["calls"] += 1
        return state["calls"] >= 2

    async def runner(_state: dict[str, str]) -> dict[str, str]:
        return {
            "intent": "direct_response",
            "response": "one two",
        }

    async def collect() -> list[str]:
        items: list[str] = []
        payload = ChatRequest(user_id="u-1", session_id="s-1", message="hello")
        async for chunk in generate_chat_events(payload, is_disconnected, runner):
            items.append(chunk)
        return items

    chunks = asyncio.run(collect())
    events = _extract_sse_events("".join(chunks))

    assert events
    assert events[0]["event_type"] == "intent"
    assert not any(event["event_type"] == "done" for event in events)
