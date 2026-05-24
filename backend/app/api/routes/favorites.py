from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.db.session import get_db
from app.models.favorite import Favorite
from app.models.node import Node
from app.schemas.node import NodeOut
from app.schemas.response import ok
from app.services.node_service import NodeNotFoundError, _check_access, _bulk_usernames, to_out

router = APIRouter()
Db = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=dict)
async def list_favorites(user: CurrentUser, db: Db) -> dict:
    rows = await db.execute(
        select(Node)
        .select_from(Favorite)
        .join(Node, Favorite.node_id == Node.id)
        .where(Favorite.user_id == user.id)
        .order_by(Node.is_folder.desc(), Node.name.asc())
    )
    nodes = list(rows.scalars().all())
    usernames = {}
    user_ids = {n.owner_id for n in nodes if n.owner_id}
    if user_ids:
        from app.models.user import User
        user_rows = await db.execute(
            select(User.id, User.username).where(User.id.in_(user_ids))
        )
        usernames = {r.id: r.username for r in user_rows.all()}
    items = [to_out(n, usernames.get(n.owner_id or "")) for n in nodes]
    return ok([i.model_dump(mode="json") for i in items]).model_dump()


@router.post("/{node_id}", response_model=dict)
async def add_favorite(node_id: str, user: CurrentUser, db: Db) -> dict:
    node = await db.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")
    await _check_access(db, node, user.id)
    existing = await db.scalar(
        select(Favorite).where(
            Favorite.user_id == user.id, Favorite.node_id == node_id
        )
    )
    if not existing:
        fav = Favorite(user_id=user.id, node_id=node_id)
        db.add(fav)
        await db.flush()
    return ok(None).model_dump()


@router.delete("/{node_id}", response_model=dict)
async def remove_favorite(node_id: str, user: CurrentUser, db: Db) -> dict:
    fav = await db.scalar(
        select(Favorite).where(
            Favorite.user_id == user.id, Favorite.node_id == node_id
        )
    )
    if fav:
        await db.delete(fav)
        await db.flush()
    return ok(None).model_dump()
