from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    parent_id: str | None
    name: str
    is_folder: bool
    size: int
    mime_type: str | None = None
    meta_json: dict[str, Any] | None = None
    owner_id: str | None = None
    owner_username: str | None = None
    updated_at: datetime

    @field_validator("updated_at", mode="before")
    @classmethod
    def ensure_timezone(cls, v: datetime) -> datetime:
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v


class BreadcrumbItem(BaseModel):
    id: str
    name: str


class FolderTreeItem(BaseModel):
    id: str
    parent_id: str | None
    name: str


class FolderCreateBody(BaseModel):
    parent_id: str = Field(..., description="Parent folder node id (use root id for top level)")
    name: str = Field(..., min_length=1, max_length=512)


class RenameBody(BaseModel):
    name: str = Field(..., min_length=1, max_length=512)


class MoveBody(BaseModel):
    parent_id: str = Field(..., description="Target folder id")


