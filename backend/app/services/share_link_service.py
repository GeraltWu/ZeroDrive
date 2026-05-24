from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password as _hash_password
from app.models.node import Node
from app.models.share_link import ShareLink
from app.schemas.share_link import ShareLinkOut, ShareLinkPublicInfo, ShareLinkWithNode


def _generate_token() -> str:
    return secrets.token_urlsafe(32)


async def create_share_link(
    session: AsyncSession,
    node_id: str,
    owner_id: str,
    password: str | None = None,
    expire_in_hours: int | None = None,
    max_access_count: int | None = None,
) -> ShareLinkOut:
    from app.services.node_service import _check_access

    node = await session.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    await _check_access(session, node, owner_id, min_role="admin")

    # Generate unique token
    token = _generate_token()
    for _ in range(5):
        existing = await session.scalar(
            select(ShareLink.id).where(ShareLink.token == token)
        )
        if not existing:
            break
        token = _generate_token()
    else:
        raise HTTPException(status_code=500, detail="生成分享链接失败，请重试")

    link = ShareLink(
        node_id=node_id,
        owner_id=owner_id,
        token=token,
        password_hash=_hash_password(password) if password else None,
        expire_at=datetime.now(timezone.utc) + timedelta(hours=expire_in_hours)
        if expire_in_hours
        else None,
        max_access_count=max_access_count,
    )
    session.add(link)
    await session.flush()

    return ShareLinkOut(
        id=link.id,
        node_id=link.node_id,
        token=link.token,
        expire_at=link.expire_at,
        max_access_count=link.max_access_count,
        access_count=link.access_count,
        is_active=link.is_active,
        created_at=link.created_at,
        has_password=link.password_hash is not None,
    )


async def list_share_links(
    session: AsyncSession,
    node_id: str,
    user_id: str,
) -> list[ShareLinkOut]:
    rows = await session.execute(
        select(ShareLink)
        .where(ShareLink.node_id == node_id, ShareLink.owner_id == user_id)
        .order_by(ShareLink.created_at.desc())
    )
    links = rows.scalars().all()
    return [
        ShareLinkOut(
            id=link.id,
            node_id=link.node_id,
            token=link.token,
            expire_at=link.expire_at,
            max_access_count=link.max_access_count,
            access_count=link.access_count,
            is_active=link.is_active,
            created_at=link.created_at,
            has_password=link.password_hash is not None,
        )
        for link in links
    ]


async def list_all_share_links(
    session: AsyncSession,
    user_id: str,
) -> list[ShareLinkWithNode]:
    rows = await session.execute(
        select(ShareLink, Node.name, Node.is_folder)
        .join(Node, ShareLink.node_id == Node.id)
        .where(ShareLink.owner_id == user_id)
        .order_by(ShareLink.created_at.desc())
        .limit(200)
    )
    return [
        ShareLinkWithNode(
            id=link.id,
            node_id=link.node_id,
            token=link.token,
            expire_at=link.expire_at,
            max_access_count=link.max_access_count,
            access_count=link.access_count,
            is_active=link.is_active,
            created_at=link.created_at,
            has_password=link.password_hash is not None,
            node_name=node_name or "未命名",
            is_folder=is_folder,
        )
        for link, node_name, is_folder in rows.all()
    ]


async def revoke_share_link(
    session: AsyncSession,
    link_id: str,
    user_id: str,
) -> None:
    link = await session.get(ShareLink, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="分享链接不存在")
    if link.owner_id != user_id:
        raise HTTPException(status_code=403, detail="无权操作此分享链接")
    await session.delete(link)
    await session.flush()


async def get_share_by_token(
    session: AsyncSession,
    token: str,
) -> ShareLink:
    link = await session.scalar(
        select(ShareLink).where(ShareLink.token == token)
    )
    if not link:
        raise HTTPException(status_code=404, detail="分享链接不存在或已被撤销")

    if not link.is_active:
        raise HTTPException(status_code=410, detail="分享链接已被停用")

    if link.expire_at and link.expire_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="分享链接已过期")

    if (
        link.max_access_count is not None
        and link.access_count >= link.max_access_count
    ):
        raise HTTPException(status_code=410, detail="分享链接已达访问上限")

    return link


async def toggle_share_link(
    session: AsyncSession,
    link_id: str,
    user_id: str,
) -> ShareLinkOut:
    link = await session.get(ShareLink, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="分享链接不存在")
    if link.owner_id != user_id:
        raise HTTPException(status_code=403, detail="无权操作此分享链接")
    link.is_active = not link.is_active
    await session.flush()
    return ShareLinkOut(
        id=link.id,
        node_id=link.node_id,
        token=link.token,
        expire_at=link.expire_at,
        max_access_count=link.max_access_count,
        access_count=link.access_count,
        is_active=link.is_active,
        created_at=link.created_at,
        has_password=link.password_hash is not None,
    )


async def verify_share_password(
    session: AsyncSession,
    token: str,
    password: str,
) -> bool:
    from app.core.security import verify_password

    link = await get_share_by_token(session, token)
    if not link.password_hash:
        return True
    if not verify_password(password, link.password_hash):
        raise HTTPException(status_code=403, detail="密码错误")
    return True


async def get_share_node_info(
    session: AsyncSession,
    token: str,
) -> ShareLinkPublicInfo:
    link = await get_share_by_token(session, token)
    node = await session.get(Node, link.node_id)
    if not node:
        raise HTTPException(status_code=404, detail="文件不存在")
    return ShareLinkPublicInfo(
        node_name=node.name or "未命名",
        is_folder=node.is_folder,
        size=node.size,
        mime_type=node.mime_type,
        has_password=link.password_hash is not None,
    )


async def increment_access_count(session: AsyncSession, link: ShareLink) -> None:
    link.access_count += 1
    await session.flush()


async def join_folder_link(
    session: AsyncSession,
    token: str,
    user_id: str,
) -> str:
    """Add the user as a viewer collaborator to the shared folder. Returns node_id."""
    from app.models.collaborator import FolderCollaborator
    from app.models.user import User

    link = await get_share_by_token(session, token)

    node = await session.get(Node, link.node_id)
    if not node or not node.is_folder:
        raise HTTPException(status_code=400, detail="只有文件夹支持此操作")

    if node.owner_id == user_id:
        raise HTTPException(status_code=400, detail="无需加入自己的文件夹")

    existing = await session.scalar(
        select(FolderCollaborator).where(
            FolderCollaborator.folder_id == node.id,
            FolderCollaborator.user_id == user_id,
        )
    )
    if existing:
        return node.id  # already joined

    collab = FolderCollaborator(
        folder_id=node.id,
        user_id=user_id,
        role="viewer",
        invited_by=link.owner_id,
    )
    session.add(collab)
    link.access_count += 1
    await session.flush()
    return node.id
