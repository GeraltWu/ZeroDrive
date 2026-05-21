from typing import Annotated

import asyncio
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse, StreamingResponse

from app.api.deps import CurrentUser
from app.core.config import get_settings
from app.db.session import AsyncSessionLocal, get_db
from app.models.node import Node
from app.models.storage import Blob, StorageBackend
from app.schemas.node import FolderCreateBody, MoveBody, RenameBody
from app.schemas.response import ok
from app.services import node_service
from app.services.storage_drivers import get_driver

router = APIRouter()

Db = Annotated[AsyncSession, Depends(get_db)]


@router.get("/root")
async def get_root(user: CurrentUser, db: Db) -> dict:
    root = await node_service.get_user_root(db, user.id)
    return ok({"id": root.id}).model_dump()


@router.get("/folders/tree")
async def folder_tree(user: CurrentUser, db: Db) -> dict:
    items = await node_service.list_all_folders(db, user.id)
    return ok([i.model_dump(mode="json") for i in items]).model_dump()


@router.get("")
async def list_children(
    parent_id: str,
    user: CurrentUser,
    db: Db,
) -> dict:
    items = await node_service.list_children(db, parent_id, user.id)
    return ok([r.model_dump(mode="json") for r in items]).model_dump()


@router.get("/{node_id}/breadcrumb")
async def breadcrumb(
    node_id: str,
    user: CurrentUser,
    db: Db,
) -> dict:
    items = await node_service.ancestors(db, node_id, user.id)
    return ok([b.model_dump(mode="json") for b in items]).model_dump()


@router.post("/folder")
async def create_folder(
    body: FolderCreateBody,
    user: CurrentUser,
    db: Db,
) -> dict:
    created = await node_service.create_folder(db, body.parent_id, body.name, user.id)
    return ok(created.model_dump(mode="json")).model_dump()


@router.post("/upload")
async def upload(
    user: CurrentUser,
    db: Db,
    parent_id: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
) -> dict:
    created = await node_service.save_upload(db, parent_id, file, user.id)
    return ok(created.model_dump(mode="json")).model_dump()


@router.get("/{node_id}/download")
async def download(node_id: str, request: Request):
    settings = get_settings()
    async with AsyncSessionLocal() as session:
        node = await session.get(Node, node_id)
        if not node:
            raise HTTPException(status_code=404, detail="节点不存在")
        if node.is_folder:
            raise HTTPException(status_code=400, detail="不能下载文件夹")
        name = node.name or "download"

        if not node.blob_id:
            raise HTTPException(status_code=404, detail="无文件内容")
        blob = await session.get(Blob, node.blob_id)
        if not blob:
            raise HTTPException(status_code=404, detail="无文件内容")
        backend = await session.get(StorageBackend, blob.storage_backend_id)
        if not backend:
            raise HTTPException(status_code=404, detail="无文件内容")
        driver = get_driver(backend, settings)
        if driver.is_filesystem():
            path = driver.filesystem_path(blob.object_key)
            if not path.is_file():
                raise HTTPException(status_code=404, detail="无文件内容")
            return FileResponse(
                path=str(path),
                filename=name,
                media_type="application/octet-stream",
                content_disposition_type="attachment",
            )
        range_header = request.headers.get("range")
        body_stream, meta = await asyncio.to_thread(
            driver.get_object_stream,
            blob.bucket,
            blob.object_key,
            range_header,
        )

        async def s3_iter():
            try:
                while True:
                    chunk = await asyncio.to_thread(body_stream.read, 1024 * 1024)
                    if not chunk:
                        break
                    yield chunk
            finally:
                close_fn = getattr(body_stream, "close", None)
                if callable(close_fn):
                    await asyncio.to_thread(close_fn)

        headers: dict[str, str] = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{quote(name)}",
            "Accept-Ranges": "bytes",
        }
        if meta.get("ContentLength") is not None:
            headers["Content-Length"] = str(meta["ContentLength"])
        if meta.get("ContentRange"):
            headers["Content-Range"] = meta["ContentRange"]
        etag = meta.get("ETag")
        if etag:
            headers["ETag"] = etag if str(etag).startswith('"') else f'"{etag}"'
        return StreamingResponse(
            s3_iter(),
            status_code=int(meta.get("Status", 200)),
            media_type="application/octet-stream",
            headers=headers,
        )


@router.get("/{node_id}/thumbnail")
async def thumbnail(node_id: str, size: int = 200):
    size = max(40, min(800, size))
    from starlette.responses import Response

    from app.services.thumbnail import thumbnail_from_bytes, thumbnail_from_path

    settings = get_settings()
    async with AsyncSessionLocal() as session:
        node = await session.get(Node, node_id)
        if not node or node.is_folder or not node.blob_id:
            raise HTTPException(status_code=404, detail="无法生成缩略图")
        blob = await session.get(Blob, node.blob_id)
        if not blob:
            raise HTTPException(status_code=404, detail="无法生成缩略图")
        backend = await session.get(StorageBackend, blob.storage_backend_id)
        if not backend:
            raise HTTPException(status_code=404, detail="无法生成缩略图")
        driver = get_driver(backend, settings)

        try:
            if driver.is_filesystem():
                path = driver.filesystem_path(blob.object_key)
                thumb_bytes = await thumbnail_from_path(path, size)
            else:
                body_stream, _ = await asyncio.to_thread(
                    driver.get_object_stream, blob.bucket, blob.object_key, None
                )
                try:
                    data = body_stream.read()
                finally:
                    close_fn = getattr(body_stream, 'close', None)
                    if callable(close_fn):
                        await asyncio.to_thread(close_fn)
                thumb_bytes = await thumbnail_from_bytes(data, size)
        except Exception:
            raise HTTPException(status_code=415, detail="不支持生成该文件的缩略图")

    return Response(content=thumb_bytes, media_type="image/jpeg")


@router.patch("/{node_id}/rename")
async def rename(
    node_id: str,
    body: RenameBody,
    user: CurrentUser,
    db: Db,
) -> dict:
    updated = await node_service.rename_node(db, node_id, body.name, user.id)
    return ok(updated.model_dump(mode="json")).model_dump()


@router.post("/{node_id}/reparse-meta")
async def reparse_meta(
    node_id: str,
    user: CurrentUser,
    db: Db,
) -> dict:
    updated = await node_service.reparse_meta(db, node_id, user.id)
    return ok(updated.model_dump(mode="json")).model_dump()


@router.post("/{node_id}/move")
async def move(
    node_id: str,
    body: MoveBody,
    user: CurrentUser,
    db: Db,
) -> dict:
    updated = await node_service.move_node(db, node_id, body.parent_id, user.id)
    return ok(updated.model_dump(mode="json")).model_dump()


@router.delete("/{node_id}")
async def delete_node(node_id: str, user: CurrentUser) -> dict:
    async with AsyncSessionLocal() as session:
        try:
            purged = await node_service.delete_cascade(session, node_id, user.id)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
    await node_service.purge_storage_after_delete(purged)
    return ok(None).model_dump()
