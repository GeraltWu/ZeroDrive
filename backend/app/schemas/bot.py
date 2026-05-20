from pydantic import BaseModel, Field


class BotFolderRef(BaseModel):
    id: str
    resolved_path: str


class BotResolvePathOut(BaseModel):
    id: str
    name: str
    parent_id: str | None
    resolved_path: str


class BotRandomImageOut(BaseModel):
    node_id: str
    name: str
    mime_type: str | None = None
    size: int
    folder: BotFolderRef
    download_url: str
