from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AdminUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    is_admin: bool
    is_active: bool
    file_count: int
    storage: int
    created_at: datetime


class UpdateUserBody(BaseModel):
    is_admin: bool | None = None
    is_active: bool | None = None
