from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_validator


def _ensure_timezone(v: datetime | None) -> datetime | None:
    if isinstance(v, datetime) and v.tzinfo is None:
        return v.replace(tzinfo=UTC)
    return v


class CollaboratorOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    folder_id: str
    user_id: str
    username: str
    role: str
    created_at: datetime

    _fix_created = field_validator("created_at", mode="before")(_ensure_timezone)


class CreateCollaboratorBody(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    role: str = Field(default="editor", pattern=r"^(viewer|editor|admin)$")


class UpdateCollaboratorBody(BaseModel):
    role: str = Field(..., pattern=r"^(viewer|editor|admin)$")


class SharedFolderOut(BaseModel):
    folder_id: str
    folder_name: str
    role: str
