from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collaborator import FolderCollaborator
from app.models.node import Node
from app.models.user import User
from app.schemas.collaborator import CollaboratorOut, SharedFolderOut
from app.services.node_service import _get_or_404

ROLE_LEVEL = {"viewer": 0, "editor": 1, "admin": 2}


def _require_min_role(role: str, min_role: str) -> None:
    if ROLE_LEVEL.get(role, -1) < ROLE_LEVEL.get(min_role, 0):
        raise HTTPException(status_code=403, detail="权限不足")


async def _require_admin_or_owner(
    session: AsyncSession, folder_id: str, user_id: str
) -> Node:
    folder = await session.get(Node, folder_id)
    if not folder or not folder.is_folder:
        raise HTTPException(status_code=404, detail="文件夹不存在")
    if folder.owner_id == user_id:
        return folder

    cur_id: str | None = folder_id
    while cur_id:
        n = await session.get(Node, cur_id)
        if not n:
            break
        if n.is_folder and n.owner_id == user_id:
            return folder
        collab = await session.scalar(
            select(FolderCollaborator).where(
                FolderCollaborator.folder_id == cur_id,
                FolderCollaborator.user_id == user_id,
            )
        )
        if collab:
            if collab.role != "admin":
                raise HTTPException(status_code=403, detail="需要文件夹管理员权限")
            return folder
        cur_id = n.parent_id

    raise HTTPException(status_code=403, detail="需要文件夹管理员权限")


async def list_collaborators(
    session: AsyncSession, folder_id: str, user_id: str
) -> list[CollaboratorOut]:
    folder = await _require_admin_or_owner(session, folder_id, user_id)
    rows = await session.execute(
        select(FolderCollaborator, User.username)
        .join(User, FolderCollaborator.user_id == User.id)
        .where(FolderCollaborator.folder_id == folder_id)
    )
    return [
        CollaboratorOut(
            id=row.FolderCollaborator.id,
            folder_id=row.FolderCollaborator.folder_id,
            user_id=row.FolderCollaborator.user_id,
            username=row.username,
            role=row.FolderCollaborator.role,
            created_at=row.FolderCollaborator.created_at,
        )
        for row in rows.all()
    ]


async def add_collaborator(
    session: AsyncSession,
    folder_id: str,
    username: str,
    role: str,
    invited_by_id: str,
) -> CollaboratorOut:
    folder = await _require_admin_or_owner(session, folder_id, invited_by_id)
    target = await session.scalar(
        select(User).where(User.username == username)
    )
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")
    if target.id == folder.owner_id:
        raise HTTPException(status_code=400, detail="文件夹所有者无需添加为协作者")
    existing = await session.scalar(
        select(FolderCollaborator).where(
            FolderCollaborator.folder_id == folder_id,
            FolderCollaborator.user_id == target.id,
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="该用户已是协作者")
    collab = FolderCollaborator(
        folder_id=folder_id,
        user_id=target.id,
        role=role,
        invited_by=invited_by_id,
    )
    session.add(collab)
    await session.flush()
    return CollaboratorOut(
        id=collab.id,
        folder_id=collab.folder_id,
        user_id=collab.user_id,
        username=target.username,
        role=collab.role,
        created_at=collab.created_at,
    )


async def update_collaborator(
    session: AsyncSession,
    folder_id: str,
    target_user_id: str,
    role: str,
    requested_by_id: str,
) -> CollaboratorOut:
    await _require_admin_or_owner(session, folder_id, requested_by_id)
    collab = await session.scalar(
        select(FolderCollaborator).where(
            FolderCollaborator.folder_id == folder_id,
            FolderCollaborator.user_id == target_user_id,
        )
    )
    if not collab:
        raise HTTPException(status_code=404, detail="协作者不存在")
    collab.role = role
    await session.flush()
    user = await session.get(User, target_user_id)
    return CollaboratorOut(
        id=collab.id,
        folder_id=collab.folder_id,
        user_id=collab.user_id,
        username=user.username if user else "",
        role=collab.role,
        created_at=collab.created_at,
    )


async def remove_collaborator(
    session: AsyncSession,
    folder_id: str,
    target_user_id: str,
    requested_by_id: str,
) -> None:
    await _require_admin_or_owner(session, folder_id, requested_by_id)
    collab = await session.scalar(
        select(FolderCollaborator).where(
            FolderCollaborator.folder_id == folder_id,
            FolderCollaborator.user_id == target_user_id,
        )
    )
    if not collab:
        raise HTTPException(status_code=404, detail="协作者不存在")
    await session.delete(collab)
    await session.flush()


async def leave_collaboration(
    session: AsyncSession,
    folder_id: str,
    user_id: str,
) -> None:
    collab = await session.scalar(
        select(FolderCollaborator).where(
            FolderCollaborator.folder_id == folder_id,
            FolderCollaborator.user_id == user_id,
        )
    )
    if not collab:
        raise HTTPException(status_code=404, detail="不在此协作中")

    # Prevent leave if user has access via an ancestor folder
    node = await session.get(Node, folder_id)
    cur_id = node.parent_id if node else None
    while cur_id:
        ancestor = await session.get(Node, cur_id)
        if not ancestor:
            break
        if ancestor.owner_id == user_id:
            raise HTTPException(
                status_code=400,
                detail="你是上级文件夹的所有者，无法单独退出此子文件夹的协作",
            )
        anc_collab = await session.scalar(
            select(FolderCollaborator).where(
                FolderCollaborator.folder_id == cur_id,
                FolderCollaborator.user_id == user_id,
            )
        )
        if anc_collab:
            raise HTTPException(
                status_code=400,
                detail="此文件夹的权限由上级文件夹继承，无法单独退出。请从父文件夹「退出共享」",
            )
        cur_id = ancestor.parent_id
    if collab.role == "admin":
        other_admin = await session.scalar(
            select(FolderCollaborator.id).where(
                FolderCollaborator.folder_id == folder_id,
                FolderCollaborator.role == "admin",
                FolderCollaborator.user_id != user_id,
            )
        )
        if not other_admin:
            raise HTTPException(
                status_code=400,
                detail="作为唯一的管理员，请先将管理员权限转让给其他成员后再退出",
            )
    await session.delete(collab)
    await session.flush()


async def list_shared_with_me(
    session: AsyncSession, user_id: str
) -> list[SharedFolderOut]:
    rows = await session.execute(
        select(FolderCollaborator, Node.name)
        .join(Node, FolderCollaborator.folder_id == Node.id)
        .where(FolderCollaborator.user_id == user_id)
    )
    return [
        SharedFolderOut(
            folder_id=row.FolderCollaborator.folder_id,
            folder_name=row.name or "文件夹",
            role=row.FolderCollaborator.role,
        )
        for row in rows.all()
    ]
