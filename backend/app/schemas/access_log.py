from datetime import datetime

from pydantic import BaseModel, ConfigDict


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
