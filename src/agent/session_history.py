from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Sequence
from typing import TypedDict

SESSION_HISTORY_WINDOW_SIZE = 5


class SessionExchange(TypedDict):
    user_message_redacted: str
    assistant_response_redacted: str


# In-memory, process-local, session-scoped short-term history.
_SESSION_HISTORY_BY_SESSION: dict[str, deque[SessionExchange]] = defaultdict(
    lambda: deque(maxlen=SESSION_HISTORY_WINDOW_SIZE)
)


def reset_session_history_store() -> None:
    _SESSION_HISTORY_BY_SESSION.clear()


def append_completed_exchange(
    session_id: str,
    user_message_redacted: str,
    assistant_response_redacted: str,
) -> None:
    if not session_id:
        return

    exchange: SessionExchange = {
        "user_message_redacted": user_message_redacted,
        "assistant_response_redacted": assistant_response_redacted,
    }
    _SESSION_HISTORY_BY_SESSION[session_id].append(exchange)


def get_session_history(session_id: str) -> list[SessionExchange]:
    if not session_id:
        return []
    history = _SESSION_HISTORY_BY_SESSION.get(session_id)
    if history is None:
        return []
    return [dict(item) for item in history]


def build_prior_turn_messages(history: Sequence[SessionExchange]) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    for exchange in history:
        messages.append({"role": "user", "content": exchange["user_message_redacted"]})
        messages.append({"role": "assistant", "content": exchange["assistant_response_redacted"]})
    return messages
