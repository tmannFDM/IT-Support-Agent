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
    pii_detected: bool
    redacted_email_count: int
    redacted_phone_count: int
    injection_detected: bool
    intent: IntentLabel
    used_context: bool
    cited_sources: list[str]
    retrieved_chunks: list[dict[str, object]]
    response: str
    tool_call: str
    escalation_reason: Literal["vague_reason", "urgency_pressure", "invalid_employee_id"]
    error: str
    error_code: str
