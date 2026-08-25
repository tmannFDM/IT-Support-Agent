from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1, max_length=4000)

    @field_validator("user_id", "session_id", "message", mode="before")
    @classmethod
    def trim_whitespace(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class ChatStreamEvent(BaseModel):
    event_type: Literal["token", "tool_call", "error", "done", "intent"]
    data: str
