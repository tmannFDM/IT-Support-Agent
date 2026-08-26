from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TicketCreateRequest(BaseModel):
    category: Literal["VPN", "Password", "Hardware", "Software", "Access"]
    priority: Literal["low", "medium", "high", "critical"]
    summary: str = Field(min_length=1)

    @field_validator("summary", mode="before")
    @classmethod
    def trim_summary(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class TicketCreateResponse(BaseModel):
    ticket_id: str = Field(pattern=r"^TKT-\d{4}$")
    category: Literal["VPN", "Password", "Hardware", "Software", "Access"]
    priority: Literal["low", "medium", "high", "critical"]
    status: Literal["open"]
    summary: str
