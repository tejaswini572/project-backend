import jwt
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schema.auth import ChangePasswordRequest, ForgotPasswordRequest, UserLogin, UserRegister
from app.service.auth_service import (
    ALGORITHM,
    SECRET_KEY,
    change_password,
    create_access_token,
    forgot_password,
    login,
    register,
)

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register")
async def register_user(
    data: UserRegister,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    return await register(db, data.email, data.password)


@router.post("/login")
async def login_user(
    response: Response,
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str | bool]:
    result = await login(db, data.email, data.password)
    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=False,
        samesite="lax"
    )
    return {"access_token": result.access_token, "token_type": "bearer", "is_admin": result.is_admin}  # nosec B105


@router.post("/forgot-password")
async def forgot_password_user(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    return await forgot_password(db, data.email)


@router.post("/change-password")
async def change_password_user(
    data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    return await change_password(db, data.old_password, data.new_password, data.email)


@router.post("/refresh-token")
async def refresh_token_user(
    refresh_token: str = Cookie(None)
) -> dict[str, str]:
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token is found")

    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    email = payload.get("sub")
    if not email or not isinstance(email, str):
        raise HTTPException(status_code=401, detail="Invalid token")

    new_access_token = create_access_token({"sub": email})
    return {"access_token": new_access_token, "token_type": "bearer"}  # nosec B105
