from __future__ import annotations

import asyncio
import os
import tempfile
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import AsyncSessionLocal
from app.models.node import Node
from app.models.storage import Blob, StorageBackend
from app.schemas.node import BreadcrumbItem, FolderTreeItem, NodeOut
from app.services.media_meta import extract_media_meta
from app.services.storage_drivers import get_driver
from app.services.storage_drivers.s3 import S3StorageDriver

META_MAX_S3_BYTES = 50 * 1024 * 1024


class NodeNotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


class NodeValidationError(Exception):
    pass


def _check_owner(node: Node, user_id: str) -> None:
    """所有权校验 — 后续扩展共享时在此加 shares 表查询。"""
    if node.owner_id is None:
        return
    if node.owner_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问")


async def create_user_root(session: AsyncSession, user_id: str) -> Node:
    node = Node(
        id=str(uuid.uuid4()),
        parent_id=None,
        name="",
        is_folder=True,
        size=0,
        blob_id=None,
        owner_id=user_id,
        updated_at=datetime.now(timezone.utc),
    )
    session.add(node)
    await session.flush()
    return node


async def get_user_root(session: AsyncSession, user_id: str) -> Node:
    res = await session.execute(
        select(Node).where(Node.parent_id.is_(None), Node.owner_id == user_id)
    )
    root = res.scalar_one_or_none()
    if not root:
        raise NodeNotFoundError("根节点不存在")
    return root


async def _get_or_404(session: AsyncSession, node_id: str, user_id: str) -> Node:
    n = await session.get(Node, node_id)
    if not n:
        raise NodeNotFoundError(node_id)
    _check_owner(n, user_id)
    return n


async def get_node(session: AsyncSession, node_id: str, user_id: str) -> Node:
    return await _get_or_404(session, node_id, user_id)


async def _same_name_exists(
    session: AsyncSession,
    parent_id: str | None,
    name: str,
    owner_id: str,
    exclude_id: str | None = None,
) -> bool:
    q = select(Node).where(
        Node.parent_id == parent_id,
        Node.name == name,
        Node.owner_id == owner_id,
    )
    if exclude_id:
        q = q.where(Node.id != exclude_id)
    res = await session.execute(q)
    return res.scalar_one_or_none() is not None


def to_out(n: Node) -> NodeOut:
    return NodeOut.model_validate(n)


async def list_all_folders(session: AsyncSession, user_id: str) -> list[FolderTreeItem]:
    res = await session.execute(
        select(Node.id, Node.parent_id, Node.name)
        .where(Node.is_folder.is_(True), Node.owner_id == user_id)
        .order_by(Node.name.asc())
    )
    return [
        FolderTreeItem(id=r[0], parent_id=r[1], name=r[2] or "")
        for r in res.all()
    ]


async def list_children(session: AsyncSession, parent_id: str, user_id: str) -> list[NodeOut]:
    parent = await _get_or_404(session, parent_id, user_id)
    if not parent.is_folder:
        raise NodeValidationError("parent must be a folder")
    res = await session.execute(
        select(Node)
        .where(Node.parent_id == parent_id, Node.owner_id == user_id)
        .order_by(Node.is_folder.desc(), Node.name.asc())
    )
    return [to_out(n) for n in res.scalars().all()]


async def ancestors(
    session: AsyncSession,
    node_id: str,
    user_id: str,
) -> list[BreadcrumbItem]:
    await _get_or_404(session, node_id, user_id)
    chain: list[BreadcrumbItem] = []
    cur: str | None = node_id
    while cur:
        n = await session.get(Node, cur)
        if not n:
            break
        display = n.name if n.name else "根"
        chain.append(BreadcrumbItem(id=n.id, name=display))
        cur = n.parent_id
    chain.reverse()
    return chain


async def create_folder(session: AsyncSession, parent_id: str, name: str, user_id: str) -> NodeOut:
    parent = await _get_or_404(session, parent_id, user_id)
    if not parent.is_folder:
        raise NodeValidationError("parent must be a folder")
    if await _same_name_exists(session, parent_id, name, user_id):
        raise ConflictError("name already exists")
    node = Node(
        id=str(uuid.uuid4()),
        parent_id=parent_id,
        name=name.strip(),
        is_folder=True,
        size=0,
        blob_id=None,
        owner_id=user_id,
        updated_at=datetime.now(timezone.utc),
    )
    session.add(node)
    await session.flush()
    return to_out(node)


async def _extract_meta_after_upload(
    driver: object,
    backend: StorageBackend,
    bucket: str,
    object_key: str,
    mime_type: str | None,
    size: int,
) -> dict | None:
    if not mime_type or not (
        mime_type.startswith("audio/") or mime_type.startswith("video/")
    ):
        return None
    if driver.is_filesystem():
        path = driver.filesystem_path(object_key)
        if not path.is_file():
            return None
        return extract_media_meta(path, mime_type=mime_type)
    if not isinstance(driver, S3StorageDriver):
        return None
    if size > META_MAX_S3_BYTES:
        return None

    def _probe() -> dict | None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".probe") as tmp:
            tmp_path = tmp.name
        try:
            driver.download_object_to_path(bucket, object_key, tmp_path)
            meta = extract_media_meta(Path(tmp_path), mime_type=mime_type)
            return meta
        finally:
            if os.path.isfile(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

    return await asyncio.to_thread(_probe)


async def save_upload(
    session: AsyncSession,
    parent_id: str,
    upload: UploadFile,
    user_id: str,
) -> NodeOut:
    parent = await _get_or_404(session, parent_id, user_id)
    if not parent.is_folder:
        raise NodeValidationError("parent must be a folder")
    raw_name = upload.filename or "unnamed"
    name = os.path.basename(raw_name).strip() or "unnamed"
    if await _same_name_exists(session, parent_id, name, user_id):
        raise ConflictError("name already exists")

    backend = (
        await session.execute(
            select(StorageBackend).where(StorageBackend.is_default.is_(True)).limit(1)
        )
    ).scalar_one_or_none()
    if backend is None:
        raise NodeValidationError("未配置默认存储后端（storage_backends）")

    settings = get_settings()
    driver = get_driver(backend, settings)
    object_key = str(uuid.uuid4())
    bucket = (backend.default_bucket or "").strip()
    size, etag = await driver.put_upload_file(bucket, object_key, upload)
    mime_type = (upload.content_type or "").strip() or None

    blob = Blob(
        id=str(uuid.uuid4()),
        storage_backend_id=backend.id,
        bucket=bucket,
        object_key=object_key,
        size=size,
        etag=etag,
        refcount=1,
    )
    session.add(blob)
    await session.flush()

    meta_json = await _extract_meta_after_upload(
        driver, backend, bucket, object_key, mime_type, size
    )

    node = Node(
        id=str(uuid.uuid4()),
        parent_id=parent_id,
        name=name,
        is_folder=False,
        size=size,
        blob_id=blob.id,
        mime_type=mime_type,
        meta_json=meta_json,
        owner_id=user_id,
        updated_at=datetime.now(timezone.utc),
    )
    session.add(node)
    await session.flush()
    return to_out(node)


async def reparse_meta(session: AsyncSession, node_id: str, user_id: str) -> NodeOut:
    node = await _get_or_404(session, node_id, user_id)
    if node.is_folder:
        raise NodeValidationError("folder has no media metadata")

    mime_type = node.mime_type
    if node.blob_id:
        blob = await session.get(Blob, node.blob_id)
        if not blob:
            raise NodeValidationError("file content is missing")
        backend = await session.get(StorageBackend, blob.storage_backend_id)
        if not backend:
            raise NodeValidationError("file content is missing")
        settings = get_settings()
        driver = get_driver(backend, settings)
        if driver.is_filesystem():
            path = driver.filesystem_path(blob.object_key)
            if not path.is_file():
                raise NodeValidationError("file content is missing")
            node.meta_json = extract_media_meta(path, mime_type=mime_type)
        elif isinstance(driver, S3StorageDriver):

            def _probe() -> dict | None:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".probe") as tmp:
                    tmp_path = tmp.name
                try:
                    driver.download_object_to_path(blob.bucket, blob.object_key, tmp_path)
                    return extract_media_meta(Path(tmp_path), mime_type=mime_type)
                finally:
                    if os.path.isfile(tmp_path):
                        try:
                            os.unlink(tmp_path)
                        except OSError:
                            pass

            node.meta_json = await asyncio.to_thread(_probe)
        else:
            raise NodeValidationError("unsupported storage driver for reparse")
    else:
        raise NodeValidationError("file content is missing")

    node.updated_at = datetime.now(timezone.utc)
    await session.flush()
    return to_out(node)


async def rename_node(session: AsyncSession, node_id: str, new_name: str, user_id: str) -> NodeOut:
    node = await _get_or_404(session, node_id, user_id)
    if node.parent_id is None:
        raise NodeValidationError("cannot rename root")
    name = new_name.strip()
    if await _same_name_exists(session, node.parent_id, name, user_id, exclude_id=node_id):
        raise ConflictError("name already exists")
    node.name = name
    node.updated_at = datetime.now(timezone.utc)
    await session.flush()
    return to_out(node)


async def is_under(session: AsyncSession, ancestor_id: str, node_id: str) -> bool:
    cur: str | None = node_id
    while cur:
        if cur == ancestor_id:
            return True
        n = await session.get(Node, cur)
        if not n:
            break
        cur = n.parent_id
    return False


async def move_node(session: AsyncSession, node_id: str, new_parent_id: str, user_id: str) -> NodeOut:
    node = await _get_or_404(session, node_id, user_id)
    if node.parent_id is None:
        raise NodeValidationError("cannot move root")
    target = await _get_or_404(session, new_parent_id, user_id)
    if not target.is_folder:
        raise NodeValidationError("target must be a folder")
    if new_parent_id == node_id:
        raise NodeValidationError("cannot move into self")
    if await is_under(session, node_id, new_parent_id):
        raise NodeValidationError("cannot move into own descendant")
    if await _same_name_exists(session, new_parent_id, node.name, user_id, exclude_id=node_id):
        raise ConflictError("name already exists in target folder")
    node.parent_id = new_parent_id
    node.updated_at = datetime.now(timezone.utc)
    await session.flush()
    return to_out(node)


async def _collect_subtree_post_order(session: AsyncSession, nid: str) -> list[str]:
    res = await session.execute(select(Node).where(Node.parent_id == nid))
    children = list(res.scalars().all())
    out: list[str] = []
    for ch in children:
        out.extend(await _collect_subtree_post_order(session, ch.id))
    out.append(nid)
    return out


async def delete_cascade(session: AsyncSession, node_id: str, user_id: str) -> list[tuple[str, str, str]]:
    """
    删除子树；返回待删存储对象列表 (backend_id, bucket, object_key)。
    须在事务 commit 成功后再执行物理删除。
    """
    node = await _get_or_404(session, node_id, user_id)
    if node.parent_id is None:
        raise NodeValidationError("cannot delete root")
    ordered_ids = await _collect_subtree_post_order(session, node_id)
    blob_dec: defaultdict[str, int] = defaultdict(int)
    for nid in ordered_ids:
        n = await session.get(Node, nid)
        if not n or n.is_folder:
            continue
        if n.blob_id:
            blob_dec[n.blob_id] += 1

    for nid in ordered_ids:
        n = await session.get(Node, nid)
        if n:
            await session.delete(n)
            await session.flush()

    to_purge: list[tuple[str, str, str]] = []
    for bid, dec in blob_dec.items():
        blob = await session.get(Blob, bid)
        if not blob:
            continue
        blob.refcount -= dec
        if blob.refcount <= 0:
            to_purge.append((blob.storage_backend_id, blob.bucket, blob.object_key))
            await session.delete(blob)
        await session.flush()

    return to_purge


async def purge_storage_after_delete(purged: list[tuple[str, str, str]]) -> None:
    settings = get_settings()
    async with AsyncSessionLocal() as session:
        for backend_id, bucket, object_key in purged:
            backend = await session.get(StorageBackend, backend_id)
            if not backend:
                continue
            driver = get_driver(backend, settings)

            def _run_delete() -> None:
                driver.delete_object(bucket, object_key)

            await asyncio.to_thread(_run_delete)
