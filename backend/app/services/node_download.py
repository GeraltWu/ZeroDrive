from __future__ import annotations

import asyncio
from urllib.parse import quote

from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool
from starlette.responses import FileResponse, StreamingResponse

from app.core.config import get_settings
from app.models.storage import Blob, StorageBackend
from app.models.node import Node
from app.services.storage_drivers import get_driver


async def build_node_download_response(
    session: AsyncSession,
    node_id: str,
    request: Request,
    *,
    filename: str | None = None,
) -> FileResponse | StreamingResponse:
    settings = get_settings()
    node = await session.get(Node, node_id)
    if node is None:
        raise HTTPException(status_code=404, detail="文件不存在")
    if node.is_folder:
        raise HTTPException(status_code=400, detail="不能下载文件夹")
    display_name = filename or node.name or "download"

    if not node.blob_id:
        raise HTTPException(status_code=404, detail="无文件内容")
    blob = await session.get(Blob, node.blob_id)
    if not blob:
        raise HTTPException(status_code=404, detail="无文件内容")
    backend = await session.get(StorageBackend, blob.storage_backend_id)
    if not backend:
        raise HTTPException(status_code=404, detail="无文件内容")
    driver = get_driver(backend, settings)
    media_type = (node.mime_type or "").strip() or "application/octet-stream"

    if driver.is_filesystem():
        path = driver.filesystem_path(blob.object_key)
        if not path.is_file():
            raise HTTPException(status_code=404, detail="无文件内容")
        return FileResponse(
            path=str(path),
            filename=display_name,
            media_type=media_type,
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
                chunk = await run_in_threadpool(body_stream.read, 1024 * 1024)
                if not chunk:
                    break
                yield chunk
        finally:
            close_fn = getattr(body_stream, "close", None)
            if callable(close_fn):
                await run_in_threadpool(close_fn)

    headers: dict[str, str] = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{quote(display_name)}",
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
        media_type=media_type,
        headers=headers,
    )
