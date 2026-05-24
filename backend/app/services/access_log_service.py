from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.access_log import AccessLog
from app.models.node import Node
from app.models.share_link import ShareLink
from app.models.user import User
from app.schemas.access_log import AccessLogOut


async def record(
    session: AsyncSession,
    node_id: str,
    owner_id: str,
    *,
    action: str,
    visitor_id: str | None = None,
    share_link_id: str | None = None,
    size: int | None = None,
) -> None:
    log = AccessLog(
        node_id=node_id,
        owner_id=owner_id,
        visitor_id=visitor_id,
        share_link_id=share_link_id,
        action=action,
        size=size,
    )
    session.add(log)
    await session.flush()


async def list_for_owner(
    session: AsyncSession,
    owner_id: str,
    limit: int = 200,
) -> list[AccessLogOut]:
    rows = await session.execute(
        select(AccessLog, Node.name, Node.is_folder, User.username, ShareLink.token)
        .outerjoin(Node, AccessLog.node_id == Node.id)
        .outerjoin(User, AccessLog.visitor_id == User.id)
        .outerjoin(ShareLink, AccessLog.share_link_id == ShareLink.id)
        .where(AccessLog.owner_id == owner_id)
        .order_by(AccessLog.created_at.desc())
        .limit(limit)
    )
    return [
        AccessLogOut(
            id=log.id,
            node_id=log.node_id,
            node_name=node_name or "(已删除)",
            is_folder=is_folder or False,
            action=log.action,
            visitor_name=username or "",
            share_token=token or "",
            size=log.size,
            created_at=log.created_at,
        )
        for log, node_name, is_folder, username, token in rows.all()
    ]
