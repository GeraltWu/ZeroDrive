from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.db.session import get_db
from app.schemas.response import ok
from app.services import access_log_service

router = APIRouter()
Db = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=dict)
async def list_access_logs(
    user: CurrentUser,
    db: Db,
    limit: Annotated[int, Query(ge=1, le=500)] = 200,
) -> dict:
    items = await access_log_service.list_for_owner(db, user.id, limit=limit)
    return ok([i.model_dump(mode="json") for i in items]).model_dump()
