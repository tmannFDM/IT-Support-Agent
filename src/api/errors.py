from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.schemas.errors import ValidationErrorDetail, ValidationErrorResponse

REQUIRED_FIELDS = {"user_id", "session_id", "message"}
ERROR_CODE_MISSING_FIELD = "ERR-VALIDATION-MISSING-FIELD"


def _field_name_from_error_location(location: tuple[object, ...]) -> str | None:
    if len(location) < 2:
        return None
    if location[0] != "body":
        return None
    field_name = location[1]
    if isinstance(field_name, str) and field_name in REQUIRED_FIELDS:
        return field_name
    return None


def _build_validation_error_response(exc: RequestValidationError) -> ValidationErrorResponse:
    details_map: dict[str, ValidationErrorDetail] = {}

    for error in exc.errors():
        field_name = _field_name_from_error_location(tuple(error.get("loc", ())))
        if not field_name:
            continue

        details_map[field_name] = ValidationErrorDetail(
            field=field_name,
            issue="Field required or empty after trim",
        )

    details = list(details_map.values()) or None
    return ValidationErrorResponse(
        error_code=ERROR_CODE_MISSING_FIELD,
        message="Validation failed for required fields.",
        details=details,
    )


async def request_validation_exception_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    payload = _build_validation_error_response(exc)
    return JSONResponse(status_code=422, content=payload.model_dump(exclude_none=True))


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
