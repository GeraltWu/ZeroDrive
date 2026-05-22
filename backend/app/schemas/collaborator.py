from datetime import datetime

from pydantic import BaseModel, Field


class CollaboratorOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    folder_id: str
    user_id: str
    username: str
    role: str
    created_at: datetime


class CreateCollaboratorBody(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    role: str = Field(default="editor", pattern=r"^(viewer|editor|admin)$")


class UpdateCollaboratorBody(BaseModel):
    role: str = Field(..., pattern=r"^(viewer|editor|admin)$")


class SharedFolderOut(BaseModel):
    folder_id: str
    folder_name: str
    role: str
