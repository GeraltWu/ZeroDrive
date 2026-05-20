from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    msg: str = "ok"
    data: T | None = None


class ValidationErrorDetail(BaseModel):
    loc: list[str | int]
    msg: str


def ok(data: T | None = None, msg: str = "ok") -> ApiResponse[T]:
    return ApiResponse(code=0, msg=msg, data=data)


def err(code: int, msg: str, data: Any = None) -> ApiResponse[Any]:
    return ApiResponse(code=code, msg=msg, data=data)
