from typing import Literal

from pydantic import BaseModel, ConfigDict


class UserMemoryFacts(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preferred_device_type: Literal["laptop", "desktop"] | None = None
    office_region: Literal["APAC", "EMEA", "AMER"] | None = None
    timezone: Literal["AEST", "PST", "EST", "CET", "GMT"] | None = None
