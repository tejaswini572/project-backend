import os
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_log import ActivityAction
from app.models.user import User
from app.schema.auth import TokenResponse
from app.service.activity_log_service import log_activity

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return password_hash.verify(plain, hashed)


SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is not set")
ALGORITHM = "HS256"


def create_access_token(data: dict[str, str]) -> str:
    payload: dict[str, str | datetime] = dict(data)
    payload["exp"] = datetime.now(UTC) + timedelta(minutes=15)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict[str, str]) -> str:
    payload: dict[str, str | datetime] = dict(data)
    payload["exp"] = datetime.now(UTC) + timedelta(days=7)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def register(db: AsyncSession, email: str, password: str) -> dict[str, str]:
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(password)

    new_user = User(email=email, password=hashed, username=email, slug=email, first_name="", last_name="")
    db.add(new_user)
    await db.commit()
    return {"message": "Registration Successful"}


async def login(db: AsyncSession, email: str, password: str) -> TokenResponse:

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=400, detail="Email not valid")

    if not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Email not verified")

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})
    is_admin = user.is_admin
    user.auth_token = refresh_token
    log_activity(db, user.email, ActivityAction.LOGIN)

    await db.commit()
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        is_admin=is_admin
    )


async def forgot_password(db: AsyncSession, email: str) -> dict[str, str]:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Email Not found")
    return {"message": "Email verified,proceed to reset password"}


async def change_password(db: AsyncSession, password: str, new_password: str, email: str) -> dict[str, str]:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    if not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    user.password = hash_password(new_password)
    await db.commit()
    return {"message": "Password changed successfully"}
