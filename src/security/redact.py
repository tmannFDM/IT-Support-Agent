from __future__ import annotations

from dataclasses import dataclass
import re

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    re.IGNORECASE,
)
PHONE_PATTERN = re.compile(
    r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)",
)


@dataclass(frozen=True)
class RedactionResult:
    original_message: str
    redacted_message: str
    redacted_email_count: int
    redacted_phone_count: int

    @property
    def pii_detected(self) -> bool:
        return (self.redacted_email_count + self.redacted_phone_count) > 0


def redact_pii(message: str) -> RedactionResult:
    redacted_emails_message, email_count = EMAIL_PATTERN.subn("[REDACTED_EMAIL]", message)
    redacted_message, phone_count = PHONE_PATTERN.subn("[REDACTED_PHONE]", redacted_emails_message)

    return RedactionResult(
        original_message=message,
        redacted_message=redacted_message,
        redacted_email_count=email_count,
        redacted_phone_count=phone_count,
    )
