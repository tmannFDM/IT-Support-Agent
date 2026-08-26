from __future__ import annotations

from src.schemas.password_reset import PasswordResetRequest, PasswordResetResponse

TEMP_PASSWORD_NOTE = (
    "A temporary password has been issued and will be required to be changed on next login."
)

# In-memory mock record for this slice only.
PASSWORD_RESET_AUDIT_LOG: list[dict[str, str]] = []


async def password_reset(employee_id: str, reason: str) -> PasswordResetResponse:
    request = PasswordResetRequest(employee_id=employee_id, reason=reason)
    PASSWORD_RESET_AUDIT_LOG.append(
        {
            "employee_id": request.employee_id,
            "reason": request.reason,
        }
    )
    return PasswordResetResponse(
        employee_id=request.employee_id,
        status="reset_issued",
        temporary_password_note=TEMP_PASSWORD_NOTE,
        escalation_reason=None,
    )
