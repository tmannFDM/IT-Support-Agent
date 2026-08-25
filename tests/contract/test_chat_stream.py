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
