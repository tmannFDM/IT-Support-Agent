from typing import Literal

from pydantic import BaseModel, Field


class PasswordResetRequest(BaseModel):
    employee_id: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class PasswordResetResponse(BaseModel):
    employee_id: str
    status: Literal["reset_issued", "escalated"]
    temporary_password_note: str
    escalation_reason: Literal["vague_reason", "urgency_pressure", "invalid_employee_id"] | None = None
