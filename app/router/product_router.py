from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schema.product import Product as ProductSchema
from app.schema.product import ProductCreate
from app.service import product_service

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/")
async def get_all_products(db: Annotated[AsyncSession, Depends(get_db)]) -> JSONResponse:
    result = await product_service.get_all_product(db)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[ProductSchema.model_validate(p).model_dump() for p in result],
    )


@router.get("/{product_id}")
async def get_product_by_id(db: Annotated[AsyncSession, Depends(get_db)], product_id: int) -> JSONResponse:
    result = await product_service.get_product_by_id(db, product_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ProductSchema.model_validate(result).model_dump(),
    )


@router.post("/")
async def add_product(
    product: ProductCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[User, Depends(require_admin)],
) -> JSONResponse:
    result = await product_service.add_product(db, product, admin.email)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ProductSchema.model_validate(result).model_dump(),
    )


@router.put("/{product_id}")
async def update_product(
    db: Annotated[AsyncSession, Depends(get_db)],
    product_id: int,
    product: ProductCreate,
    admin: Annotated[User, Depends(require_admin)],
) -> JSONResponse:
    result = await product_service.update_product(db, product_id, product, admin.email)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ProductSchema.model_validate(result).model_dump(),
    )


@router.delete("/{product_id}")
async def delete_product(
    db: Annotated[AsyncSession, Depends(get_db)],
    product_id: int,
    admin: Annotated[User, Depends(require_admin)],
) -> JSONResponse:
    result = await product_service.delete_product(db, product_id, admin.email)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
