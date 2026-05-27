from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, field_validator


def _ensure_timezone(v: datetime | None) -> datetime | None:
    if isinstance(v, datetime) and v.tzinfo is None:
        return v.replace(tzinfo=UTC)
    return v


class AccessLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    node_id: str
    node_name: str = ""
    is_folder: bool = False
    action: str
    visitor_name: str = ""
    share_token: str = ""
    size: int | None = None
    created_at: datetime

    _fix_created = field_validator("created_at", mode="before")(_ensure_timezone)
