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
    response: str
    error: str
