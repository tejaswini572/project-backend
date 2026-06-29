from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schema.customer import Customer as CustomerSchema
from app.schema.customer import CustomerCreate
from app.service import user_service

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/")
async def get_all_users(db: Annotated[AsyncSession, Depends(get_db)]) -> JSONResponse:
    result = await user_service.get_all_users(db)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[CustomerSchema.model_validate(u).model_dump() for u in result],
    )


@router.get("/{customer_id}", responses={404: {"description": "User not found"}})
async def get_user_by_id(customer_id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> JSONResponse:
    result = await user_service.get_user_by_id(db, customer_id)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=CustomerSchema.model_validate(result).model_dump(),
    )


@router.post("/")
async def add_user(customer: CustomerCreate, db: Annotated[AsyncSession, Depends(get_db)]) -> JSONResponse:
    result = await user_service.add_user(db, customer)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=CustomerSchema.model_validate(result).model_dump(),
    )


@router.put("/{customer_id}")
async def update_user(
    customer_id: int,
    customer: CustomerCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JSONResponse:
    result = await user_service.update_user(db, customer_id, customer)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=CustomerSchema.model_validate(result).model_dump(),
    )


@router.delete("/{customer_id}")
async def delete_user(customer_id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> JSONResponse:
    result = await user_service.delete_user(db, customer_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
