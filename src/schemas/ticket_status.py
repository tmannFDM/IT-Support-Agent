import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator

_TICKET_ID_PATTERN = re.compile(r"^TKT-\d+$", re.IGNORECASE)
_UTC_Z_TIMESTAMP_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class TicketStatusRequest(BaseModel):
    ticket_id: str = Field(min_length=1)

    @field_validator("ticket_id", mode="before")
    @classmethod
    def trim_whitespace(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("ticket_id")
    @classmethod
    def normalize_ticket_id(cls, value: str) -> str:
        if not _TICKET_ID_PATTERN.fullmatch(value):
            raise ValueError("ticket_id must match TKT-<digits>")
        return value.upper()


class TicketStatusResponse(BaseModel):
    ticket_id: str = Field(min_length=1)
    status: Literal["open", "in_progress", "resolved", "closed"]
    priority: Literal["low", "medium", "high", "critical"]
    summary: str = Field(min_length=1)
    last_updated: str = Field(min_length=1)

    @field_validator("ticket_id", mode="before")
    @classmethod
    def trim_ticket_id(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("ticket_id")
    @classmethod
    def validate_ticket_id(cls, value: str) -> str:
        if not _TICKET_ID_PATTERN.fullmatch(value):
            raise ValueError("ticket_id must match TKT-<digits>")
        return value.upper()

    @field_validator("summary", "last_updated", mode="before")
    @classmethod
    def trim_string_values(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("last_updated")
    @classmethod
    def validate_last_updated(cls, value: str) -> str:
        if not _UTC_Z_TIMESTAMP_PATTERN.fullmatch(value):
            raise ValueError("last_updated must be UTC ISO 8601 with Z suffix")
        return value
