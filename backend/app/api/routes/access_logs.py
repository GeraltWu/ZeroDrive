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
    share_token: Annotated[str | None, Query()] = None,
    action: Annotated[str | None, Query()] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    sort: Annotated[str, Query(pattern=r"^(asc|desc)$")] = "desc",
) -> dict:
    items, total = await access_log_service.list_for_owner(
        db,
        user.id,
        share_token=share_token,
        action=action,
        offset=offset,
        limit=limit,
        sort_desc=sort == "desc",
    )
    return ok({
        "items": [i.model_dump(mode="json") for i in items],
        "total": total,
    }).model_dump()
