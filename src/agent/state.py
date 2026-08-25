from typing import Literal, TypedDict

IntentLabel = Literal[
    "policy_question",
    "action_request",
    "direct_response",
    "escalation",
    "blocked",
]


class AgentState(TypedDict, total=False):
    user_id: str
    session_id: str
    message: str
    intent: IntentLabel
    used_context: bool
    cited_sources: list[str]
    retrieved_chunks: list[dict[str, object]]
    response: str
    error: str
