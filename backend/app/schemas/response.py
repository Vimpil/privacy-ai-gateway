from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""

    status: str  # "success" or "error"
    data: T | None = None
    error: str | None = None


class ErrorDetail(BaseModel):
    """Error response body."""

    message: str
    code: str | None = None

