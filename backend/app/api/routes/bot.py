from __future__ import annotations

import time
from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse, StreamingResponse

from app.api.deps import CurrentUser, OptionalCurrentUser
from app.core.config import get_settings
from app.core.security import create_download_signature, verify_download_signature
from app.db.session import get_db
from app.models.node import Node
from app.schemas.bot import BotFolderRef, BotRandomImageOut, BotResolvePathOut
from app.schemas.response import ok
from app.services import bot_service
from app.services.bot_path import PathNotFoundError, PathValidationError
from app.services.bot_service import NoImagesError
from app.services.node_download import build_node_download_response
from app.services.node_service import _check_owner

router = APIRouter()

Db = Annotated[AsyncSession, Depends(get_db)]


def _build_download_url(request: Request, node_id: str) -> str:
    settings = get_settings()
    exp = int(time.time()) + max(60, settings.bot_download_expire_seconds)
    sig = create_download_signature(node_id, exp)
    query = urlencode({"sig": sig, "exp": str(exp)})
    base = str(request.base_url).rstrip("/")
    return f"{base}/api/bot/files/{node_id}/content?{query}"


@router.get("/resolve-path")
async def resolve_path(
    db: Db,
    user: CurrentUser,
    path: str = Query(..., min_length=1, description="文件夹绝对路径，/ 为根目录，/图片/奶龙"),
) -> dict:
    folder, resolved = await bot_service.resolve_folder_by_path(db, path, user.id)
    payload = BotResolvePathOut(
        id=folder.id,
        name=folder.name,
        parent_id=folder.parent_id,
        resolved_path=resolved,
    )
    return ok(payload.model_dump(mode="json")).model_dump()


@router.get("/random-image")
async def random_image(
    request: Request,
    db: Db,
    user: CurrentUser,
    path: str = Query(..., min_length=1, description="文件夹绝对路径，/ 为根目录，/图片/奶龙"),
    mime_prefix: str = Query("image/", description="mime_type 前缀匹配"),
    extensions: str | None = Query(None, description="扩展名白名单，逗号分隔，如 jpg,png,gif"),
) -> dict:
    folder, resolved = await bot_service.resolve_folder_by_path(db, path, user.id)
    picked = await bot_service.pick_random_image_in_folder(
        db,
        folder.id,
        user.id,
        mime_prefix=mime_prefix,
        extensions=extensions,
    )
    payload = BotRandomImageOut(
        node_id=picked.id,
        name=picked.name,
        mime_type=picked.mime_type,
        size=picked.size,
        folder=BotFolderRef(id=folder.id, resolved_path=resolved),
        download_url=_build_download_url(request, picked.id),
    )
    return ok(payload.model_dump(mode="json")).model_dump()


@router.get("/files/{node_id}/content", response_model=None)
async def download_file_content(
    node_id: str,
    request: Request,
    db: Db,
    sig: str | None = Query(None),
    exp: int | None = Query(None),
    user: OptionalCurrentUser = None,
) -> FileResponse | StreamingResponse:
    if user is not None:
        node = await db.get(Node, node_id)
        if node:
            _check_owner(node, user.id)
    elif sig and exp is not None:
        if not verify_download_signature(node_id, exp, sig):
            raise HTTPException(status_code=403, detail="下载链接无效或已过期")
    else:
        raise HTTPException(status_code=401, detail="未授权")

    return await build_node_download_response(db, node_id, request)
