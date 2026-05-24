from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateShareLinkBody(BaseModel):
    password: str | None = Field(None, min_length=1, max_length=128)
    expire_in_hours: int | None = Field(None, ge=1)
    max_access_count: int | None = Field(None, ge=1)


class ShareLinkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    node_id: str
    token: str
    expire_at: datetime | None = None
    max_access_count: int | None = None
    access_count: int
    is_active: bool = True
    created_at: datetime
    has_password: bool = False


class ShareLinkWithNode(ShareLinkOut):
    node_name: str
    is_folder: bool


class ShareLinkPublicInfo(BaseModel):
    node_name: str
    is_folder: bool
    size: int
    mime_type: str | None = None
    has_password: bool = False


class VerifyPasswordBody(BaseModel):
    password: str = Field(..., min_length=1)
