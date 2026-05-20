from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import CurrentUser
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginBody, LoginOut, RegisterBody
from app.schemas.response import ok
from app.services.node_service import create_user_root

router = APIRouter()
Db = AsyncSession


@router.post("/register")
async def register(body: RegisterBody, db: Db = Depends(get_db)) -> dict:
    q = select(User).where(User.username == body.username.strip())
    exists = (await db.execute(q)).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已存在")
    user = User(
        username=body.username.strip(),
        password_hash=hash_password(body.password),
    )
    db.add(user)
    await db.flush()
    await create_user_root(db, user.id)
    return ok({"username": user.username}).model_dump()


@router.post("/login")
async def login(body: LoginBody, db: Db = Depends(get_db)) -> dict:
    q = select(User).where(User.username == body.username.strip())
    user = (await db.execute(q)).scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")
    token = create_access_token(user.id)
    payload = LoginOut(access_token=token, username=user.username)
    return ok(payload.model_dump()).model_dump()


@router.post("/logout")
async def logout(_: CurrentUser) -> dict:
    return ok(None).model_dump()


@router.get("/me")
async def me(user: CurrentUser) -> dict:
    return ok({"username": user.username}).model_dump()
