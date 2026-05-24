from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.db.session import get_db
from app.schemas.collaborator import (
    CollaboratorOut,
    CreateCollaboratorBody,
    SharedFolderOut,
    UpdateCollaboratorBody,
)
from app.schemas.response import ok
from app.services import collaborator_service

router = APIRouter()
Db = Annotated[AsyncSession, Depends(get_db)]


@router.get("/{folder_id}", response_model=dict)
async def list_collaborators(
    folder_id: str,
    user: CurrentUser,
    db: Db,
) -> dict:
    items = await collaborator_service.list_collaborators(db, folder_id, user.id)
    return ok([i.model_dump(mode="json") for i in items]).model_dump()


@router.post("/{folder_id}", response_model=dict)
async def add_collaborator(
    folder_id: str,
    body: CreateCollaboratorBody,
    user: CurrentUser,
    db: Db,
) -> dict:
    created = await collaborator_service.add_collaborator(
        db, folder_id, body.username, body.role, user.id
    )
    return ok(created.model_dump(mode="json")).model_dump()


@router.put("/{folder_id}/{target_user_id}", response_model=dict)
async def update_collaborator(
    folder_id: str,
    target_user_id: str,
    body: UpdateCollaboratorBody,
    user: CurrentUser,
    db: Db,
) -> dict:
    updated = await collaborator_service.update_collaborator(
        db, folder_id, target_user_id, body.role, user.id
    )
    return ok(updated.model_dump(mode="json")).model_dump()


@router.delete("/{folder_id}/leave", response_model=dict)
async def leave_folder(folder_id: str, user: CurrentUser, db: Db) -> dict:
    await collaborator_service.leave_collaboration(db, folder_id, user.id)
    return ok(None).model_dump()


@router.delete("/{folder_id}/{target_user_id}", response_model=dict)
async def remove_collaborator(
    folder_id: str,
    target_user_id: str,
    user: CurrentUser,
    db: Db,
) -> dict:
    await collaborator_service.remove_collaborator(db, folder_id, target_user_id, user.id)
    return ok(None).model_dump()


@router.get("/with-me/list", response_model=dict)
async def shared_with_me(
    user: CurrentUser,
    db: Db,
) -> dict:
    items = await collaborator_service.list_shared_with_me(db, user.id)
    return ok([i.model_dump(mode="json") for i in items]).model_dump()
