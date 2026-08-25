from pydantic import BaseModel


class ValidationErrorDetail(BaseModel):
    field: str
    issue: str


class ValidationErrorResponse(BaseModel):
    error_code: str
    message: str
    details: list[ValidationErrorDetail] | None = None
