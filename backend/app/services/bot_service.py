from __future__ import annotations

import secrets
from pathlib import PurePosixPath

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException

from app.models.node import Node
from app.schemas.node import NodeOut
from app.services.bot_path import PathNotFoundError, normalize_path
from app.services.node_service import ConflictError, NodeNotFoundError, _check_owner, get_user_root, to_out


class NoImagesError(Exception):
    pass


def _parse_extensions(extensions: str | None) -> set[str]:
    if not extensions or not extensions.strip():
        return set()
    out: set[str] = set()
    for part in extensions.split(","):
        e = part.strip().lower().lstrip(".")
        if e:
            out.add(e)
    return out


def _matches_image(node: Node, mime_prefix: str, extensions: set[str]) -> bool:
    if node.is_folder or not node.blob_id:
        return False
    mime = (node.mime_type or "").lower()
    if mime_prefix and mime.startswith(mime_prefix.lower()):
        return True
    if extensions:
        suffix = PurePosixPath(node.name or "").suffix.lower().lstrip(".")
        if suffix in extensions:
            return True
    return False


async def resolve_folder_by_path(
    session: AsyncSession,
    path: str,
    user_id: str,
) -> tuple[Node, str]:
    segments = normalize_path(path)
    root = await get_user_root(session, user_id)
    if not segments:
        return root, "/"

    current_id = root.id
    resolved_parts: list[str] = []
    for segment in segments:
        res = await session.execute(
            select(Node).where(
                Node.parent_id == current_id,
                Node.name == segment,
                Node.is_folder.is_(True),
                Node.owner_id == user_id,
            )
        )
        matches = list(res.scalars().all())
        if not matches:
            raise PathNotFoundError(segment, "/".join(resolved_parts))
        if len(matches) > 1:
            raise ConflictError(f"路径段「{segment}」存在多个同名文件夹")
        folder = matches[0]
        current_id = folder.id
        resolved_parts.append(segment)

    folder = await session.get(Node, current_id)
    if not folder or not folder.is_folder:
        raise PathNotFoundError(segments[-1], "/".join(resolved_parts[:-1]))
    return folder, "/".join(resolved_parts)


async def pick_random_image_in_folder(
    session: AsyncSession,
    folder_id: str,
    user_id: str,
    *,
    mime_prefix: str = "image/",
    extensions: str | None = None,
) -> NodeOut:
    folder = await session.get(Node, folder_id)
    if not folder or not folder.is_folder:
        raise NodeNotFoundError(folder_id)
    _check_owner(folder, user_id)

    ext_set = _parse_extensions(extensions)
    res = await session.execute(
        select(Node).where(
            Node.parent_id == folder_id,
            Node.is_folder.is_(False),
            Node.owner_id == user_id,
        )
    )
    candidates = [
        to_out(n)
        for n in res.scalars().all()
        if _matches_image(n, mime_prefix, ext_set)
    ]
    if not candidates:
        raise NoImagesError()
    return secrets.choice(candidates)
