from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.access_log import AccessLog
from app.models.node import Node
from app.models.user import User
from app.schemas.admin import AdminUserOut


async def list_users(session: AsyncSession) -> list[AdminUserOut]:
    rows = await session.execute(
        select(
            User,
            func.count(Node.id).label("file_count"),
            func.coalesce(func.sum(Node.size), 0).label("storage"),
        )
        .outerjoin(Node, Node.owner_id == User.id)
        .group_by(User.id)
        .order_by(User.created_at.desc())
    )
    return [
        AdminUserOut(
            id=u.id,
            username=u.username,
            is_admin=u.is_admin,
            is_active=u.is_active,
            file_count=fc or 0,
            storage=st or 0,
            created_at=u.created_at,
        )
        for u, fc, st in rows.all()
    ]


async def update_user(
    session: AsyncSession,
    target_id: str,
    *,
    is_admin: bool | None = None,
    is_active: bool | None = None,
) -> AdminUserOut:
    target = await session.get(User, target_id)
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")

    if is_admin is False:
        remaining = await session.scalar(
            select(func.count(User.id)).where(
                User.is_admin == True,
                User.id != target_id,
                User.is_active == True,
            )
        )
        if remaining == 0:
            raise HTTPException(
                status_code=400, detail="不能撤销最后一名活跃管理员的权限"
            )

    if is_admin is not None:
        target.is_admin = is_admin
    if is_active is not None:
        target.is_active = is_active
    await session.flush()

    fc = (await session.execute(select(func.count(Node.id)).where(Node.owner_id == target.id))).scalar() or 0
    st = (await session.execute(select(func.coalesce(func.sum(Node.size), 0)).where(Node.owner_id == target.id))).scalar() or 0

    return AdminUserOut(
        id=target.id,
        username=target.username,
        is_admin=target.is_admin,
        is_active=target.is_active,
        file_count=fc,
        storage=st,
        created_at=target.created_at,
    )


async def delete_user(session: AsyncSession, target_id: str) -> None:
    target = await session.get(User, target_id)
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")
    if target.is_admin:
        remaining = await session.scalar(
            select(func.count(User.id)).where(
                User.is_admin == True,
                User.id != target_id,
                User.is_active == True,
            )
        )
        if remaining == 0:
            raise HTTPException(
                status_code=400, detail="不能删除最后一名活跃管理员"
            )
    await session.delete(target)
    await session.flush()
